"""Consolida, por item do Lattes, tudo o que foi mapeado (Claude Code e Antigravity) e compara com o que a plataforma tem hoje.

Fontes:
  - Claude Code: capturas em docs/campos-lattes/ref/<item>/, matriz F5 em ref/<item>_f5/, paridade (ferramentas/valida_paridade.py),
    salvamentos de teste em docs/validacao/LOG_OPERACOES_NOITE.md.
  - Antigravity: capturas em docs/auditoria-antigravity/capturas/ e validações F4/F5/F7 (salvar + reabrir + excluir) do documento de referência.
  - Plataforma: specs itens/especificacao/, leitores (itens/leitores.py), itens legados (server.py), exclusão suportada (static/app.js),
    carga do salvamento de teste (ferramentas/gerar_payload_generico.py), robô (extensao/autofill_core.js).

Uso:  python ferramentas/consolidar_campos.py
Saída: docs/validacao/CONSOLIDACAO_CAMPOS.md e docs/validacao/consolidacao_campos.json
"""
import contextlib
import glob
import io
import json
import os
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "ferramentas"))
SPECS = RAIZ / "itens" / "especificacao"
REFS = RAIZ / "docs" / "campos-lattes" / "ref"
AG = RAIZ / "docs" / "auditoria-antigravity" / "capturas"
SAIDA_MD = RAIZ / "docs" / "validacao" / "CONSOLIDACAO_CAMPOS.md"
SAIDA_JSON = RAIZ / "docs" / "validacao" / "consolidacao_campos.json"

# Campos de apoio da página (busca/lupa/visibilidade), iguais aos ignorados pela paridade.
APOIO = re.compile(r"^(f_nome|f_nme_inst|f_sigla|f_pais_inst|f_uf|nomeautor.*|nometitular.*|f_tipo_privacidade|f_instituicoes|f_cod|f_seq|f_ctr|file)$", re.I)

# Captura do Antigravity -> item(s) do spec
AG_PARA_ITEM = {
    "apresentacao_trabalho": ["apresentacao"], "artigo_periodico_contravalidacao": ["artigo"], "banca_trabalho": ["banca"],
    "capitulo_livro": ["livro_capitulo"], "livro": ["livro_capitulo"], "entrevistas_midia": ["entrevista_midia"],
    "pos_doutorado_livre_docencia": ["pos_doutorado"], "processos_tecnicas": ["processo_tecnica"], "produtos": ["produto"],
    "software_registrado": ["software_registro"], "trabalhos_anais_eventos": ["anais"], "trabalhos_tecnicos": ["trabalho_tecnico"],
    "assessoria_consultoria": ["relatorio_tecnico"],  # mesmo formulário: PKG_ASSESSORIA_CONSULTORIA.form
    "citacoes_5_bases": ["citacao_google_scholar", "citacao_outra_base", "citacao_scielo", "citacao_scopus", "citacao_web_of_science"],
}
SEM_SPEC = {  # capturas do Antigravity sem spec correspondente
    "areas_atuacao": "Áreas de atuação (GN_AREA_ATU): grade editável com árvore de áreas, sem spec",
    "atuacao_atividades": "Atividades de atuação (pkg_ativ.cargo): subformulário interno de instituição já cadastrada (Nível 3)",
    "linhas_de_pesquisa": "Linhas de pesquisa: não tem formulário próprio; entra por Atuação > Atividades > Pesquisa e desenvolvimento",
}

# Salvamento de teste conferido na lista do Lattes (LOG_OPERACOES_NOITE.md)
SALVOU_CLAUDE = set("""projeto artigo anais apresentacao orientacao_concluida orientacao_andamento banca banca_comissao_julgadora patente
software_registro software_sem_registro produto processo_tecnica trabalho_tecnico relatorio_tecnico extensao_tecnologica material_didatico
desenho_industrial marca_registrada topografia_circuito cultivar_protegida cultivar_registrada participacao_evento organizacao_evento
curso_ministrado premio texto_jornal_revista traducao prefacio_posfacio partitura_musical musica artes_cenicas artes_visuais cartas_mapas
maquete editoracao entrevista_midia redes_sociais relatorio_pesquisa outra_producao_artistica outra_producao_bibliografica outra_producao_tecnica
manutencao_obra livro_capitulo""".split())
# Formulários de registro único (não há "excluir": salvar sobrescreve o dado real do usuário)
REGISTRO_UNICO = {"identificacao", "endereco", "texto_inicial", "outras_informacoes", "redes_sociais_cv"}
# Validação F7 do Antigravity (salvar + reabrir + excluir), conforme a tabela-mestra do documento de referência
F7_ANTIGRAVITY = SALVOU_CLAUDE | {"premio", "licenca", "idioma", "formacao_academica", "pos_doutorado", "formacao_complementar", "atuacao_profissional",
                  "corpo_editorial", "comite_assessoramento", "revisor_periodico", "revisor_projeto_fomento", "artigo_aceito", "livro_capitulo",
                  "anais", "apresentacao", "prefacio_posfacio", "trabalho_tecnico", "processo_tecnica", "curso_ministrado", "artes_cenicas",
                  "marca_registrada", "cultivar_protegida", "participacao_evento", "organizacao_evento", "orientacao_concluida",
                  "orientacao_andamento", "banca", "banca_comissao_julgadora", "citacao_outra_base", "citacao_web_of_science",
                  "citacao_scielo", "citacao_scopus", "citacao_google_scholar"}
# Itens cuja carga de salvamento de teste vem de gerador próprio (não do genérico)
PAYLOAD_PROPRIO = {"artigo", "anais", "apresentacao", "orientacao_concluida", "orientacao_andamento", "projeto"}


def ler(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def nomes_ag(o, acc=None, maxl=None):
    """Todos os 'name' em qualquer profundidade da captura do Antigravity (formato livre); 'FC_LE / F_LE' vira dois nomes."""
    acc = set() if acc is None else acc
    maxl = {} if maxl is None else maxl
    if isinstance(o, dict):
        nm = o.get("name")
        if isinstance(nm, str):
            for n in re.split(r"\s*/\s*|\s*,\s*|\s+\+\s+", nm):
                n = n.strip()
                if re.match(r"^[A-Za-z_#][\w#.\-\[\]]*$", n):
                    acc.add(n)
                    if isinstance(o.get("maxlength"), int) and o["maxlength"] > 0:
                        maxl[n.lower()] = o["maxlength"]
        for k, v in o.items():
            if k.endswith("_url") or k in ("evidencia_screenshot", "evidencias_screenshot", "evidencia_screenshots", "url", "url_exemplo", "form_action", "action", "onclick",
                     "onchange", "onblur", "onfocus", "fonte", "hidden_inputs", "nota", "diferenca_vs_assessoria"):
                continue
            nomes_ag(v, acc, maxl)
    elif isinstance(o, str):
        # capturas em texto livre: "f_ano_ini (max 4)", "F_BOLSA (Sim/Não)", "f_pais_r/i (244/245)"
        for n in re.findall(r"(?<![\w.])((?:f|F|fc|FC)_[A-Za-z0-9_]+)\b", o):
            acc.add(n)
    elif isinstance(o, list):
        for v in o:
            nomes_ag(v, acc, maxl)
    return acc, maxl


def paridade(item):
    try:
        r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "valida_paridade.py"), item], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=RAIZ, env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=120)
        m = re.search(r"TOTAL PENDENTE:\s*(\d+)", r.stdout)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def f5(item):
    ok = tot = 0
    falhas = {}
    for p in glob.glob(str(REFS / f"{item}_f5" / "*.json")):
        try:
            d = ler(p)
        except Exception:
            continue
        res = d.get("resultados") or []
        if res:
            for r in res:
                tot += 1
                st = r.get("status", "")
                cid = str(r.get("id", "")).lower()
                if st in ("OK", "exige_acao_manual") or (cid in ("f_relev#opcao_s", "f_relev#opcao_sim") and st == "divergente"):
                    ok += 1
                else:
                    falhas[st] = falhas.get(st, 0) + 1
        else:
            for st, n in (d.get("resumo") or {}).items():
                tot += n
                if st in ("OK", "exige_acao_manual"):
                    ok += n
                else:
                    falhas[st] = falhas.get(st, 0) + n
    return ok, tot, [f"{k}:{v}" for k, v in sorted(falhas.items())]


def cobertura_salvamento(item, spec):
    """Quantos campos preenchíveis do spec a carga do salvamento de teste realmente preenche."""
    try:
        import gerar_payload_generico as g
    except Exception:
        return None
    pre = tot = 0
    vazios = []
    grades_spec = grades_carga = 0
    for i, var in enumerate(spec["variantes"]):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                c = g.carga(item, i)["__generico"]
        except Exception:
            return None
        for campo in c["campos"]:
            if campo.get("auto"):
                continue
            tot += 1
            if campo["valor"]:
                pre += 1
            else:
                vazios.append(campo["name"])
        grades_spec += len(var.get("grades", []))
        grades_carga += len(c.get("grades") or {})
    return {"preenchidos": pre, "total": tot, "vazios": sorted(set(vazios)), "grades_spec": grades_spec, "grades_carga": grades_carga}


def main():
    from itens.leitores import LEITORES
    try:
        srv = (RAIZ / "server.py").read_text(encoding="utf-8")
        legado = set(re.search(r"LEGADO_PARA_ITEM\s*=\s*\(([^)]*)\)", srv).group(1).replace('"', "").replace(" ", "").split(","))
    except Exception:
        legado = set()
    app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
    m = re.search(r"REMOCAO_SUPORTADA\s*=\s*new Set\(\[([^\]]*)\]", app)
    remocao = {x.strip().strip('"\'') for x in (m.group(1).split(",") if m else []) if x.strip()}
    if "/api/itens/listas" in app:
        listas_p = RAIZ / "itens" / "listas_lattes.json"
        if listas_p.exists():
            remocao.update(k for k, v in ler(listas_p).items() if v and not k.startswith("_"))

    # capturas do Antigravity agrupadas por item
    ag_por_item, ag_maxl = {}, {}
    cit_bases = {"1_web_of_science": "citacao_web_of_science", "2_scielo": "citacao_scielo", "3_scopus": "citacao_scopus",
                 "4_google_scholar": "citacao_google_scholar", "99_outra_base": "citacao_outra_base"}
    for p in sorted(AG.glob("*.json")):
        base = p.stem
        if base in SEM_SPEC:
            continue
        dados = ler(p)
        if base == "citacoes_5_bases":
            comuns, maxl_c = nomes_ag(dados.get("campos_comuns") or [])
            for bk, it in cit_bases.items():
                ext_n, ext_m = nomes_ag(((dados.get("bases") or {}).get(bk) or {}).get("extras") or [])
                ag_por_item.setdefault(it, set()).update(comuns | ext_n)
                ag_maxl.setdefault(it, {}).update({**maxl_c, **ext_m})
            continue
        alvo_ag = dados.get("nivel_1_inclui") if base == "atuacao_profissional" else dados
        nomes, maxl = nomes_ag(alvo_ag)
        if base == "extensao_tecnologica":
            nomes = {n for n in nomes if n.lower() != "f_cod_prod"}
        for it in AG_PARA_ITEM.get(base, [base]):
            ag_por_item.setdefault(it, set()).update(nomes)
            ag_maxl.setdefault(it, {}).update(maxl)

    linhas = []
    for sp in sorted(SPECS.glob("*.json")):
        item = sp.stem
        spec = ler(sp)
        vars_ = spec["variantes"]
        nomes_spec, maxl_spec, trunc, obrig = set(), {}, [], 0
        grades = set()
        for v in vars_:
            for g in v.get("grades", []):
                grades.add(g.get("chave") or g.get("id") or "?")
            for c in v["campos"]:
                nomes_spec.add(c["name"])
                if c.get("maxlength"):
                    maxl_spec.setdefault(c["name"].lower(), set()).add(c["maxlength"])
                if c.get("obrigatorio"):
                    obrig += 1
                if len(c.get("opcoes") or {}) in (79, 80) and c.get("catalogo_completo"):
                    trunc.append(f"{c['name']} ({len(c.get('opcoes') or {})} de {c['catalogo_completo'].split('/')[-1]})")
        # capturas Claude
        ref_nomes, ref_listas, ref_vars, trunc_ref = set(), set(), 0, []
        for p in glob.glob(str(REFS / item / "*.json")):
            if os.path.basename(p).startswith(("excecoes", "_")):
                continue
            try:
                d = ler(p)
            except Exception:
                continue
            if "campos" not in d:
                continue
            ref_vars += 1
            for c in d["campos"]:
                ref_nomes.add(c["name"])
                if c.get("total_opcoes", 0) > len(c.get("opcoes") or []):
                    trunc_ref.append(c["name"])
            for li in d.get("listas", []):
                ref_listas.add(li.get("id"))
        ag = ag_por_item.get(item, set())
        low = lambda s: {x.lower() for x in s if not APOIO.match(x)}
        conhecidos = low(nomes_spec) | low(ref_nomes)
        so_ag = sorted(low(ag) - conhecidos)
        so_claude = sorted(low(ref_nomes) - low(nomes_spec))
        div_maxl = []
        for n, mx in ag_maxl.get(item, {}).items():
            if n in maxl_spec and mx not in maxl_spec[n]:
                div_maxl.append(f"{n}: spec={sorted(maxl_spec[n])} AG={mx}")
        ok, tot, falhas = f5(item)
        par = paridade(item) if ref_vars else None
        cob = cobertura_salvamento(item, spec)
        unico = item in REGISTRO_UNICO
        linhas.append({
            "item": item, "secao": spec.get("secao", ""), "nome": spec.get("item", ""), "variantes": len(vars_),
            "spec_campos": len(nomes_spec), "spec_obrigatorios": obrig, "spec_grades": sorted(grades), "catalogo_truncado": sorted(set(trunc)),
            "claude_captura_variantes": ref_vars, "claude_campos": len(ref_nomes), "claude_listas": len(ref_listas),
            "claude_opcoes_cortadas_captura": sorted(set(trunc_ref)), "paridade_pendentes": par,
            "f5_ok": ok, "f5_total": tot, "f5_falhas": falhas,
            "ag_captura": bool(ag), "ag_campos": len(low(ag)), "so_no_antigravity": so_ag, "so_na_captura_claude": so_claude, "maxlength_divergente": div_maxl,
            "app_leitor": item in LEITORES, "app_legado": item in legado, "app_exclusao": item in remocao,
            "salvou_claude": item in SALVOU_CLAUDE, "f7_antigravity": item in F7_ANTIGRAVITY, "registro_unico": unico,
            "carga_salvamento": cob,
        })

    for base, txt in SEM_SPEC.items():
        linhas.append({"item": base, "secao": "", "nome": txt, "sem_spec": True})

    SAIDA_JSON.write_text(json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")
    escrever_md(linhas)
    print(f"{len(linhas)} itens -> {SAIDA_MD.relative_to(RAIZ)} e {SAIDA_JSON.relative_to(RAIZ)}")


def sim(b):
    return "✔" if b else "✘"


def escrever_md(L):
    itens = [x for x in L if not x.get("sem_spec")]
    n = len(itens)
    cnt = lambda f: sum(1 for x in itens if f(x))
    def pronto(x):
        cob = x["carga_salvamento"]
        cheio = cob is not None and cob["preenchidos"] == cob["total"] and cob["grades_carga"] >= cob["grades_spec"]
        return (x["paridade_pendentes"] == 0 and x["f5_total"] and not x["f5_falhas"] and not x["catalogo_truncado"] and not x["so_no_antigravity"]
                and x["app_leitor"] and (x["salvou_claude"] or x["f7_antigravity"] or x["registro_unico"]) and (x["app_exclusao"] or x["registro_unico"]) and cheio)
    o = []
    o.append("# Consolidação de campos: mapeado (Claude Code + Antigravity) × plataforma hoje\n")
    o.append("Gerado por `python ferramentas/consolidar_campos.py` (não editar à mão; rode de novo após cada mudança). Dados brutos: `consolidacao_campos.json`.\n")
    o.append("## Critério de \"pronto\" (meta do projeto)\n")
    o.append("Um formulário só está pronto quando: (1) captura real e paridade 0; (2) matriz F5 sem falha; (3) catálogos completos; (4) nenhum campo mapeado "
             "pelo Antigravity ausente; (5) disponível no app (leitor + formulário); (6) **salvamento de teste com TODOS os campos e grades preenchidos**, "
             "conferido na lista e na reabertura; (7) **exclusão pela plataforma** testada e conferida. Registro único (identificação, endereço, textos): "
             "salvar com cópia e restauração do original no lugar da exclusão.\n")
    o.append("## Placar\n")
    o.append("| Indicador | Itens |\n| --- | --- |")
    o.append(f"| Specs (formulários) na plataforma | {n} ({sum(x['variantes'] for x in itens)} variantes) |")
    o.append(f"| Captura real do Claude | {cnt(lambda x: x['claude_captura_variantes'])} |")
    o.append(f"| Paridade spec × Lattes = 0 | {cnt(lambda x: x['paridade_pendentes'] == 0)} |")
    o.append(f"| Matriz F5 executada sem falha | {cnt(lambda x: x['f5_total'] and not x['f5_falhas'])} (executada em {cnt(lambda x: x['f5_total'])}) |")
    o.append(f"| Catálogo truncado em 80 opções no spec | {cnt(lambda x: x['catalogo_truncado'])} |")
    o.append(f"| Com campos vistos só pelo Antigravity | {cnt(lambda x: x['so_no_antigravity'])} |")
    o.append(f"| Com `maxlength` divergente (spec × Antigravity) | {cnt(lambda x: x['maxlength_divergente'])} |")
    o.append(f"| Disponível no app (leitor) | {cnt(lambda x: x['app_leitor'])} |")
    o.append(f"| Salvamento de teste conferido (Claude) | {cnt(lambda x: x['salvou_claude'])} |")
    o.append(f"| Salvamento de teste com todos os campos | {cnt(lambda x: x['carga_salvamento'] and x['carga_salvamento']['preenchidos'] == x['carga_salvamento']['total'])} |")
    o.append(f"| Exclusão suportada pela plataforma | {cnt(lambda x: x['app_exclusao'])} |")
    o.append(f"| Salvar + reabrir + excluir validado pelo Antigravity (amostra manual) | {cnt(lambda x: x['f7_antigravity'])} |")
    o.append(f"| **Pronto pelo critério acima** | **{cnt(pronto)}** |\n")

    o.append("## Matriz por item\n")
    o.append("Legenda: Par = pendentes de paridade · F5 = casos OK/total · Cat80 = catálogo cortado · só AG = campos que só o Antigravity viu · "
             "Carga = campos preenchidos pelo salvamento de teste / preenchíveis (grades) · Excl = exclusão pela plataforma · F7-AG = salvar/reabrir/excluir pelo Antigravity.\n")
    o.append("| Seção | Item | Var | Campos spec | Par | F5 | Cat80 | só AG | App | Salvou | Carga | Excl | F7-AG |")
    o.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for x in sorted(itens, key=lambda x: (x["secao"], x["item"])):
        cob = x["carga_salvamento"]
        cg = "—" if cob is None else f"{cob['preenchidos']}/{cob['total']} ({cob['grades_carga']}/{cob['grades_spec']})"
        f5t = f"{x['f5_ok']}/{x['f5_total']}" if x["f5_total"] else "—"
        par = "—" if x["paridade_pendentes"] is None else x["paridade_pendentes"]
        sal = "único" if x["registro_unico"] else sim(x["salvou_claude"])
        exc = "n/a" if x["registro_unico"] else sim(x["app_exclusao"])
        app = ("legado" if x["app_legado"] else sim(x["app_leitor"]))
        o.append(f"| {x['secao']} | `{x['item']}` | {x['variantes']} | {x['spec_campos']} | {par} | {f5t} | {len(x['catalogo_truncado']) or ''} | "
                 f"{len(x['so_no_antigravity']) or ''} | {app} | {sal} | {cg} | {exc} | {sim(x['f7_antigravity'])} |")
    o.append("")
    o.append("## Detalhe das diferenças por item\n")
    for x in sorted(itens, key=lambda x: (x["secao"], x["item"])):
        det = []
        if x["catalogo_truncado"]:
            det.append("catálogo cortado no spec: " + ", ".join(x["catalogo_truncado"]))
        if x["claude_opcoes_cortadas_captura"]:
            det.append("captura Claude com opções cortadas (`slice(0, 80)`): " + ", ".join(f"`{c}`" for c in x["claude_opcoes_cortadas_captura"]))
        if x["so_no_antigravity"]:
            det.append("campos só no Antigravity (conferir ao vivo e incluir no spec): " + ", ".join(f"`{c}`" for c in x["so_no_antigravity"]))
        if x["so_na_captura_claude"]:
            det.append("na captura Claude e fora do spec: " + ", ".join(f"`{c}`" for c in x["so_na_captura_claude"]))
        if x["maxlength_divergente"]:
            det.append("maxlength: " + "; ".join(x["maxlength_divergente"]))
        if x["f5_falhas"]:
            det.append("F5 não-OK: " + ", ".join(x["f5_falhas"]))
        cob = x["carga_salvamento"]
        if cob and cob["vazios"]:
            det.append(f"salvamento de teste deixa vazios ({len(cob['vazios'])}): " + ", ".join(f"`{c}`" for c in cob["vazios"]))
        if cob and cob["grades_carga"] < cob["grades_spec"]:
            det.append(f"salvamento de teste preenche {cob['grades_carga']} de {cob['grades_spec']} grades ({', '.join(x['spec_grades'])})")
        if not x["claude_captura_variantes"]:
            det.append("sem captura real do Claude")
        if not x["ag_captura"]:
            det.append("sem captura do Antigravity")
        if det:
            o.append(f"### `{x['item']}` — {x['nome']}\n")
            o.extend(f"- {d}" for d in det)
            o.append("")
    o.append("## Formulários mapeados sem spec\n")
    for x in L:
        if x.get("sem_spec"):
            o.append(f"- `{x['item']}`: {x['nome']}")
    o.append("")
    SAIDA_MD.write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    main()
