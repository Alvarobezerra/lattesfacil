"""Fase 2 da metodologia: compara o spec (itens/especificacao/<item>.json) com a captura do Lattes real
(docs/campos-lattes/ref/<item>/<variante>.json) e imprime o relatório de divergências por categoria.

Uso:  python ferramentas/valida_paridade.py projeto            (todas as variantes capturadas)
      python ferramentas/valida_paridade.py projeto extensao   (uma variante)
Saída: código 0 se não houver divergência não justificada; 1 caso contrário.
Exceções justificadas ficam em docs/campos-lattes/ref/<item>/excecoes.json:
      {"<variante_slug>": [{"categoria": "...", "campo": "...", "motivo": "..."}]}
"""
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SPECS = RAIZ / "itens" / "especificacao"
REFS = RAIZ / "docs" / "campos-lattes" / "ref"

# Campos que só existem como apoio da própria página do Lattes (busca/lupa/visibilidade) e não são do item.
APOIO = re.compile(r"^(f_nome|f_nme_inst|f_sigla|f_pais_inst|f_uf|nomeautor.*|nometitular.*|f_tipo_privacidade|f_instituicoes)$", re.I)


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", str(t)) if unicodedata.category(c) != "Mn")


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", sem_acento(t).lower())).strip()


def slug(t):
    return re.sub(r"[^a-z0-9]+", "_", sem_acento(t).lower()).strip("_")


def tipo_spec(c):
    t = c.get("tipo", "text")
    if t == "checkbox":
        return "grupo_marcacao" if len(c.get("opcoes", {})) > 1 else "marcacao"
    return t


def comparar(spec_var, ref):
    """Devolve lista de divergências: dicts com categoria, campo, detalhe."""
    div = []
    sc = {c["name"].lower(): c for c in spec_var["campos"]}
    rc = {c["name"].lower(): c for c in ref["campos"]}

    for n, r in rc.items():
        if n not in sc:
            if not APOIO.match(n):
                div.append({"categoria": "ausente_no_spec", "campo": r["name"], "detalhe": f"tipo {r['tipo']}, rótulo '{r.get('rotulo') or r.get('pergunta', '')}'"})
    for n, s in sc.items():
        if n not in rc and not APOIO.match(n):
            div.append({"categoria": "sobrando_no_spec", "campo": s["name"], "detalhe": f"tipo {s.get('tipo')}"})

    for n in sorted(set(sc) & set(rc)):
        s, r = sc[n], rc[n]
        nome = s["name"]
        ts, tr = tipo_spec(s), r["tipo"]
        if ts != tr and not (ts in ("text", "date") and tr in ("text", "date")):
            div.append({"categoria": "tipo_diferente", "campo": nome, "detalhe": f"spec={ts} lattes={tr}"})
        if s.get("maxlength") != r.get("maxlength") and (s.get("maxlength") or r.get("maxlength")):
            div.append({"categoria": "maxlength_diferente", "campo": nome, "detalhe": f"spec={s.get('maxlength')} lattes={r.get('maxlength')}"})
        # opções: pares texto/valor
        if r["tipo"] in ("select", "radio", "grupo_marcacao", "marcacao") and r.get("opcoes"):
            ro = {(norm(o.get("texto", "")) if r["tipo"] == "select" or o.get("texto") else norm(o["valor"]), o["valor"]) for o in r["opcoes"] if o.get("valor") not in ("", "DUMMY", "Selecione")}
            so = {(norm(k), v) for k, v in (s.get("opcoes") or {}).items() if v not in ("", "Selecione")}
            if r["tipo"] == "select" and s.get("catalogo") and not s.get("opcoes"):
                if APOIO.match(n):
                    continue
                # seleção por catálogo: o Lattes oferece só parte do catálogo em alguns formulários (ex.: 80 de 152 idiomas no artigo)
                cat = json.loads((RAIZ / "docs" / "campos-lattes" / s["catalogo"]).read_text(encoding="utf-8"))
                vc = {v["valor"] for v in cat.get("valores", []) if v.get("valor") not in ("", "Selecione")}
                vr = {v for _, v in ro}
                if vr != vc:
                    div.append({"categoria": "opcoes_diferentes", "campo": nome, "detalhe": f"catálogo {s['catalogo']} tem {len(vc)} valores e o Lattes oferece {len(vr)}; só no catálogo={len(vc - vr)} só no lattes={sorted(vr - vc)[:5]}"})
            elif r["tipo"] == "select" and r.get("total_opcoes", 0) > 80:
                pass  # catálogo grande sem catálogo mapeado: comparado à parte
            else:
                vr = {v for _, v in ro}
                vs = {v for _, v in so}
                if vr != vs:
                    div.append({"categoria": "opcoes_diferentes", "campo": nome, "detalhe": f"valores só no spec={sorted(vs - vr)} só no lattes={sorted(vr - vs)}"})
                else:
                    tr_ = {v: t for t, v in ro}
                    ts_ = {v: t for t, v in so}
                    dif_txt = [f"{v}: spec='{ts_[v]}' lattes='{tr_[v]}'" for v in sorted(vr) if tr_[v] and ts_[v] != tr_[v]]
                    if dif_txt and r["tipo"] in ("select", "radio"):
                        div.append({"categoria": "opcoes_diferentes", "campo": nome, "detalhe": "; ".join(dif_txt[:4])})
        # rótulo
        rot_l = r.get("rotulo") or r.get("pergunta") or ""
        rot_s = s.get("rotulo") or ""
        oculto_no_lattes = r["tipo"] in ("radio", "grupo_marcacao", "marcacao") and not r["visivel_inicial"]  # sem texto visível para comparar
        if rot_l and not oculto_no_lattes and norm(rot_s) != norm(rot_l) and not (norm(rot_l).startswith(norm(rot_s)) and len(norm(rot_s)) > 8):
            div.append({"categoria": "rotulo_diferente", "campo": nome, "detalhe": f"spec='{rot_s}' lattes='{rot_l}'"})
        # visibilidade inicial x oculto
        oculto_s = bool(s.get("oculto")) or bool(s.get("mostrar_quando"))  # condicional = oculto até o gatilho
        if r["visivel_inicial"] == oculto_s:
            div.append({"categoria": "visibilidade_diferente", "campo": nome, "detalhe": f"lattes visível={r['visivel_inicial']} spec oculto/condicional={oculto_s}"})
        if r.get("desabilitado") and not s.get("bloqueado_no_lattes") and not s.get("oculto") and not (s.get("tipo") in ("text",) and nome.lower() in ("f_inst", "f_orgao", "f_curso")) and ts == "text" and nome.lower() not in ("f_inst", "f_orgao", "f_curso"):
            div.append({"categoria": "desabilitado_nao_tratado", "campo": nome, "detalhe": "campo desabilitado no Lattes (lupa/automático)"})

    # estados (condicionais): cada campo que aparece por um gatilho deve ter mostrar_quando ou oculto no spec
    for e in ref.get("estados", []):
        for alvo in e["aparecem"]:
            if APOIO.match(alvo):
                continue
            s = sc.get(alvo.lower())
            if s is None:
                continue
            mq = s.get("mostrar_quando") or {}
            if mq.get("name", "").lower() != e["gatilho"].lower():
                div.append({"categoria": "condicional_ausente", "campo": alvo, "detalhe": f"aparece com {e['gatilho']}={e['valor']} ({e.get('texto', '')}); spec mostrar_quando={mq or 'nenhum'}"})

    # listas
    rlistas = {l["id"].lower(): l for l in ref.get("listas", [])}
    for n in ("autores", "instituicoes_envolvidas", "financiamentos"):
        pass
    spec_grades = {g["chave"] for g in spec_var.get("grades", [])}
    ha_pesquisadores = any(l.get("visivel") and ("autorholder" == i or "tabelaautor" == i) for i, l in rlistas.items())
    if ha_pesquisadores and "autores" not in spec_grades:
        div.append({"categoria": "lista_ausente", "campo": "autores", "detalhe": "lista de pesquisadores/autores existe no Lattes e não no spec"})
    botoes = [b["antes"] for b in ref.get("botoes_incluir", [])]
    if botoes and not any(g.get("colunas") for g in spec_var.get("grades", [])) and not spec_var.get("abas_informativas"):
        div.append({"categoria": "lista_ausente", "campo": "botao Incluir novo item", "detalhe": f"{len(botoes)} lista(s) com 'Incluir novo item' no Lattes sem equivalente no spec: {botoes}"})
    return div


def carregar_excecoes(item):
    p = REFS / item / "excecoes.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    item = argv[0]
    alvo = argv[1] if len(argv) > 1 else None
    spec = json.loads((SPECS / f"{item}.json").read_text(encoding="utf-8"))
    excecoes = carregar_excecoes(item)
    total_nj = 0
    refs = sorted((REFS / item).glob("*.json")) if (REFS / item).exists() else []
    refs = [p for p in refs if p.name != "excecoes.json" and (alvo is None or p.stem == alvo)]
    if not refs:
        print(f"Nenhuma captura em {REFS / item}")
        return 2
    for p in refs:
        ref = json.loads(p.read_text(encoding="utf-8"))
        sv = next((v for v in spec["variantes"] if slug(v["variante"]) == ref.get("variante_slug") or norm(v["variante"]) == norm(ref["variante"])), None)
        print(f"\n=== {item} / {ref['variante']} (captura de {ref.get('capturado_em')}) ===")
        if sv is None:
            print("  variante não encontrada no spec")
            total_nj += 1
            continue
        div = comparar(sv, ref)
        just = {(x["categoria"], x["campo"].lower()) for x in excecoes.get(ref["variante_slug"], [])}
        nj = [d for d in div if (d["categoria"], d["campo"].lower()) not in just]
        por_cat = {}
        for d in div:
            por_cat.setdefault(d["categoria"], []).append(d)
        print(f"  campos Lattes={len(ref['campos'])} spec={len(sv['campos'])} estados={len(ref.get('estados', []))} listas={len(ref.get('listas', []))}")
        print(f"  divergências={len(div)} justificadas={len(div) - len(nj)} PENDENTES={len(nj)}")
        for cat, itens in por_cat.items():
            print(f"  - {cat}: {len(itens)}")
            for d in itens:
                marca = "  (justificada)" if (d["categoria"], d["campo"].lower()) in just else ""
                print(f"      * {d['campo']}: {d['detalhe']}{marca}")
        total_nj += len(nj)
    print(f"\nTOTAL PENDENTE: {total_nj}")
    return 0 if total_nj == 0 else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main(sys.argv[1:]))
