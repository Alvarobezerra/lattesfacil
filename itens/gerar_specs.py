"""Gera itens/especificacao/<id>.json a partir do mapeamento real dos formulários (docs/campos-lattes).

Cada especificação descreve, para um item do Lattes: como abrir o formulário, e todos os campos (nome técnico,
tipo, opções, limite, obrigatório, aba). É a fonte única para: formulário na tela, preenchimento no Lattes e testes.
Rode de novo se o mapeamento mudar:  python itens/gerar_specs.py
Curadoria manual (origem dos campos, regras de extração) fica em itens/curadoria.json e é mesclada aqui.
"""
import json, re, unicodedata, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MAPA = RAIZ / "docs" / "campos-lattes"
SAIDA = pathlib.Path(__file__).resolve().parent / "especificacao"

# id do classificador -> arquivos do mapeamento (e o nome de cada variante de formulário, quando há várias)
ITENS = {
    "participacao_evento": ["eventos/participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json"],
    "organizacao_evento": ["eventos/organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json"],
    "artigo_aceito": ["producoes/artigos-aceitos-para-publicacao.json"],
    "livro_capitulo": ["producoes/livros-e-capitulos.json"],
    "banca": ["bancas/participacao-em-bancas-de-trabalhos-de-conclusao.json"],
    "curso_ministrado": ["producoes/curso-de-curta-duracao-ministrado.json"],
    "formacao_complementar": ["formacao/formacao-complementar.json"],
    "formacao_academica": ["formacao/formacao-academica-titulacao.json"],
    "atuacao_profissional": ["atuacao/atuacao-profissional.json"],
    "revisor_periodico": ["atuacao/revisor-de-periodico.json"],
    "corpo_editorial": ["atuacao/membro-de-corpo-editorial.json"],
    "patente": ["patentes-e-registros/patente.json"],
    "software_registro": ["patentes-e-registros/programa-de-computador-registrado.json"],
    "premio": ["dados-gerais/premios-e-titulos.json"],
    "projeto": ["projetos/projetos-de-pesquisa.json", "projetos/projeto-de-extensao.json", "projetos/projeto-de-ensino.json",
                "projetos/projeto-de-desenvolvimento-tecnologico.json", "projetos/outros-tipos-de-projetos.json"],
    "idioma": ["dados-gerais/idiomas.json"],
    "licenca": ["dados-gerais/licenca-maternidade-paternidade-e-adocao.json"],
    "relatorio_tecnico": ["producoes/assessoria-e-consultoria.json"],
}


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode()


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", sem_acento(t).lower()).strip()


def opcoes_dict(op):
    """Normaliza opções: dict rótulo->valor, ou lista 'valor=rótulo' (a '=' vazia é o 'selecione')."""
    if isinstance(op, dict):
        return {str(k): str(v) for k, v in op.items()}
    out = {}
    for o in op or []:
        if "=" in str(o):
            v, _, r = str(o).partition("=")
            if r.strip():
                out[r.strip()] = v.strip()
    return out


def campos_do_formulario(f):
    obrig = [norm(x) for x in f.get("campos_obrigatorios_segundo_mensagens", [])]
    campos = []
    for aba in f.get("abas", []):
        for c in aba.get("campos", []):
            c = dict(c)
            c.setdefault("name", c.get("id", ""))
            if not c["name"]:
                continue
            rot = c.get("rotulo_provavel") or c.get("rotulo") or ""
            item = {
                "chave": re.sub(r"^f_", "", c["name"].lower()),
                "name": c["name"],
                "rotulo": rot or c["name"],
                "aba": aba.get("aba", ""),
                "tipo": c.get("tipo", "text"),
            }
            if c.get("maxlength"):
                item["maxlength"] = c["maxlength"]
            ops = opcoes_dict(c.get("opcoes"))
            if ops:
                item["opcoes"] = ops
            if c.get("catalogo"):
                item["catalogo"] = c["catalogo"]
            if c.get("oculto_inicialmente"):
                item["oculto"] = True
            r = norm(rot)
            item["obrigatorio"] = bool(r) and any(r == o or (len(r) > 3 and (r in o or o in r)) for o in obrig)
            campos.append(item)
    return campos


def gerar():
    SAIDA.mkdir(exist_ok=True)
    cur_p = pathlib.Path(__file__).resolve().parent / "curadoria.json"
    curadoria = json.loads(cur_p.read_text(encoding="utf-8")) if cur_p.exists() else {}
    resumo = []
    for item_id, arquivos in ITENS.items():
        variantes = []
        for rel in arquivos:
            d = json.loads((MAPA / rel).read_text(encoding="utf-8"))
            inicio = len(variantes)
            for i, f in enumerate(d.get("formularios", [])):
                variantes.append({
                    "variante": f.get("nome") or f.get("formulario") or (d["item"] if len(arquivos) > 1 else (f"Formulário {i + 1}" if len(d.get("formularios", [])) > 1 else "único")),
                    "url": f.get("url", ""),
                    "abertura": d.get("abertura", {}),
                    "janelas_auxiliares": f.get("janelas_auxiliares", []),
                    "campos": campos_do_formulario(f),
                    "obrigatorios_mensagens": f.get("campos_obrigatorios_segundo_mensagens", []),
                })
            primeiro = d
            over = curadoria.get(item_id, {}).get("campos", {})
            for var_ in variantes[inicio:]:
                for c in var_["campos"]:
                    c.update(over.get(c["name"], {}))
        spec = {
            "id": item_id,
            "secao": primeiro.get("secao", ""),
            "item": primeiro.get("item", ""),
            "como_abrir": primeiro.get("como_abrir", ""),
            "salvar": "O LattesFácil nunca clica em Salvar sozinho; o usuário confere e salva.",
            "variantes": variantes,
            "curadoria": curadoria.get(item_id, {}),
        }
        (SAIDA / f"{item_id}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        resumo.append((item_id, len(variantes), sum(len(v["campos"]) for v in variantes), sum(c["obrigatorio"] for v in variantes for c in v["campos"])))
    return resumo


if __name__ == "__main__":
    for r in gerar():
        print("%-22s variantes=%d campos=%d obrigatorios=%d" % r)
