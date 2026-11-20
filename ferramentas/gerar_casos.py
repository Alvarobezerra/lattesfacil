"""Fase 4 da metodologia: gera a matriz de casos de teste de valores a partir do spec e da captura do Lattes.

Uso:  python ferramentas/gerar_casos.py projeto
Saída: ferramentas/saida/casos_<item>.js  (window.__casos = { <variante_slug>: [caso, ...] }), carregado no Lattes pelo
executor (ferramentas/executor_preenchimento.js), que roda o autofill real e lê cada campo de volta (fase 5).

Casos por tipo de campo:
  texto/área : típico · exatamente maxlength · maxlength+5 (deve cortar) · acentos e pontuação
  ano/número : válido · acima do limite · letras
  seleção    : cada opção (catálogos grandes: 3 primeiras e a última)
  radio      : cada opção
  grupo      : cada opção sozinha · todas
  condicional: aciona o gatilho antes e volta ao estado inicial depois
  lupa       : instituição e órgão (lentos)
"""
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PREFIXO = "ZZ-TESTE-LATTESFACIL"
APOIO = re.compile(r"^(f_nome|f_nme_inst|f_sigla|f_pais_inst|f_uf|nomeautor.*|nometitular.*|f_tipo_privacidade|f_instituicoes)$", re.I)
LUPAS = {"f_inst", "f_orgao", "f_curso", "f_nme_agencia"}


def slug(t):
    s = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def campo_payload(c, valor, codigo="", codigos=None):
    return {"name": c["name"], "rotulo": c.get("rotulo", c["name"]), "tipo": c.get("tipo", "text"), "valor": valor, "codigo": codigo, "codigos": codigos or [], "auto": False}


def gatilho_payload(sv, mq):
    g = next((x for x in sv["campos"] if x["name"].lower() == mq["name"].lower()), None)
    if not g:
        return None
    cod = (g.get("opcoes") or {}).get(mq["valor"], "")
    if g.get("tipo") == "checkbox":
        return campo_payload(g, mq["valor"], codigos=[cod] if cod else [])
    return campo_payload(g, mq["valor"], codigo=cod)


def casos_da_variante(sv):
    casos = []
    for c in sv["campos"]:
        n = c["name"]
        if APOIO.match(n) or (c.get("oculto") and not c.get("mostrar_quando")) or c.get("bloqueado_no_lattes"):
            continue  # bloqueados no Lattes entram pelo endereço de abertura (casos "abertura"), não pelo preenchimento
        tipo = c.get("tipo", "text")
        pre = []
        if c.get("mostrar_quando"):
            gp = gatilho_payload(sv, c["mostrar_quando"])
            if gp:
                pre.append(gp)
        if c.get("exige_antes"):  # o Lattes só aceita o valor depois de outro campo ser escolhido: escolhe o primeiro valor liberador antes
            gp = gatilho_payload(sv, {"name": c["exige_antes"]["name"], "valor": c["exige_antes"]["valores"][0]})
            if gp:
                pre.append(gp)

        def add(sufixo, alvo, esperado, lento=False):
            casos.append({"id": f"{n}#{sufixo}", "campo": n, "tipo": tipo, "rotulo": c.get("rotulo", n), "pre": pre, "alvo": alvo, "esperado": esperado, "lento": lento,
                          "gatilho": c.get("mostrar_quando", {}).get("name", "")})

        if n.lower() in LUPAS:
            nome, contem = {"f_inst": ("Universidade Federal do Maranhão", "maranh"), "f_orgao": ("Centro de Ciências de Imperatriz (CCIm)", "imperatriz"),
                            "f_curso": ("Farmácia", "farm"), "f_nme_agencia": ("CNPq", "conselho nacional")}[n.lower()]
            add("lupa", campo_payload(c, nome), {"modo": "lupa", "contem": contem}, lento=True)
            continue
        ops = c.get("opcoes") or {}
        if tipo == "select":
            itens = [(k, v) for k, v in ops.items() if v not in ("", "Selecione")]
            if len(itens) > 250:  # espelho completo: todas as opções oferecidas pelo Lattes (só catálogos enormes são amostrados)
                itens = itens[:3] + itens[-1:]
            for k, v in itens:
                add("opcao_" + slug(v or k), campo_payload(c, k, codigo=v), {"modo": "valor", "valor": v})
        elif tipo == "radio":
            for k, v in ops.items():
                add("opcao_" + slug(v), campo_payload(c, k, codigo=v), {"modo": "valor", "valor": v})
        elif tipo == "checkbox" and len(ops) > 1:
            for k, v in ops.items():
                add("so_" + slug(v), campo_payload(c, k, codigos=[v]), {"modo": "conjunto", "valores": [v]})
            add("todas", campo_payload(c, "; ".join(ops), codigos=list(ops.values())), {"modo": "conjunto", "valores": list(ops.values())})
        elif tipo in ("text", "textarea"):
            ml = c.get("maxlength")
            numerico = bool(re.match(r"^(f_?ano|f_nro|nro_)|ANO_|NRO_", n, re.I)) and (ml or 0) <= 4
            if numerico:
                add("valido", campo_payload(c, "2025" if "ANO" in n.upper() else "12"[: ml or 2]), {"modo": "texto", "valor": "2025" if "ANO" in n.upper() else "12"[: ml or 2]})
                add("acima_do_limite", campo_payload(c, "9" * ((ml or 2) + 3)), {"modo": "texto", "valor": "9" * (ml or 2)})
                add("letras", campo_payload(c, "ab"), {"modo": "texto", "valor": "ab", "registrar_apenas": True})
            else:
                tipico = f"{PREFIXO} texto típico" if n == "f_titulo" else "Texto de teste típico"
                add("tipico", campo_payload(c, tipico), {"modo": "texto", "valor": tipico[: ml] if ml else tipico})
                if ml:
                    add("maximo", campo_payload(c, "X" * ml), {"modo": "texto", "valor": "X" * ml})
                    add("acima_do_limite", campo_payload(c, "Y" * (ml + 5)), {"modo": "texto", "valor": "Y" * ml})
                esp = "Ação çãõ ÉÍÓ ñ — “aspas” (a; b) & c"
                add("acentos", campo_payload(c, esp[: ml] if ml else esp), {"modo": "texto", "valor": esp[: ml] if ml else esp})
    return casos


def main(item):
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    saida = {}
    for v in spec["variantes"]:
        saida[slug(v["variante"])] = casos_da_variante(v)
    destino = RAIZ / "ferramentas" / "saida"
    destino.mkdir(exist_ok=True)
    (destino / f"casos_{item}.js").write_text("window.__casos = " + json.dumps(saida, ensure_ascii=False) + ";\n", encoding="utf-8")
    for k, v in saida.items():
        print(f"{k}: {len(v)} casos")


if __name__ == "__main__":
    main(sys.argv[1])
