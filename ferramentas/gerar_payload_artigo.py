"""Gera ferramentas/saida/payload_artigo.js: duas cargas (abertura manual por periódico e abertura por DOI) montadas como o app monta
(genColetar/genUrlDaVariante), para o teste de preenchimento real do artigo no Lattes (fase 5).
Uso: python ferramentas/gerar_payload_artigo.py
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402
from itens.leitores import ler  # noqa: E402

TEXTO_MANUAL = ("ZZ-TESTE-LATTESFACIL Artigo de teste (validação automática)\n"
                "Revista de Saude Publica, Volume 12, Issue 3, pp. 101-110, 2025. ISSN 0034-8910.\n"
                "Keywords: probiotics; babassu; beverages.")


def carga(texto, url_fn):
    r = ler("artigo", texto, "")
    spec = especificacao("artigo")
    var = spec["variantes"][0]
    v = r["valores"]
    campos = []
    for c in var["campos"]:
        if c.get("oculto"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor,
                       "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    grades = {k.split(":", 1)[1]: x for k, x in v.items() if k.startswith("grade:")}
    return {"tipo_producao": "generico", "__usuario": "", "__origem": "", "__autoSalvar": False,
            "__generico": {"id": "artigo", "item": spec["item"], "como_abrir": spec["como_abrir"], "url": url_fn(v),
                           "campos": campos, "faltam": r["faltam_obrigatorios"], "grades": grades}}


def url_manual(v):
    from urllib.parse import quote
    return ("PKG_ARTIGO.form?f_sta_divulgacao_cientifica=&F_ORIGEM_WS=F&F_TITULO_PERIODICO=" + quote(v["f_titulo_periodico"]) +
            "&F_ISSN=" + v["f_issn"].replace("-", "") + "&F_VOLUME=" + v["f_volume"] + "&F_SERIE=" + v.get("f_serie", "") +
            "&F_PAG_INI=" + v["f_pag_ini"] + "&F_CTR=FIV&F_COD=<codigo_do_cv>")


def url_doi(v):
    from urllib.parse import quote
    return "PKG_ARTIGO.form?f_sta_divulgacao_cientifica=&F_COD_DOI=" + quote(v["f_cod_doi"], safe="") + "&F_CTR=D&F_COD=<codigo_do_cv>"


if __name__ == "__main__":
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    casos = {"manual": carga(TEXTO_MANUAL, url_manual), "doi": carga("10.1371/journal.pmed.0020124", url_doi)}
    casos["manual"]["__generico"]["grades"]["autores"] = [{"nome": "ZZ Autor de Teste", "citacao": "TESTE, Z. A."}, {"nome": "Segundo Autor Teste", "citacao": "TESTE, S. A."}]
    casos["salvar"] = json.loads(json.dumps(casos["manual"]))
    casos["salvar"]["__usuario"] = "Álvaro Antônio Bezerra dos Santos"
    casos["salvar"]["__semAlerta"] = True
    casos["salvar"]["__autoSalvar"] = True
    casos["salvar"]["__generico"]["grades"]["autores"] = [{"nome": "Álvaro Antônio Bezerra dos Santos", "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}]
    (saida / "payload_artigo.js").write_text("window.__payloadArtigo = " + json.dumps(casos, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", {k: (len(x["__generico"]["campos"]), list(x["__generico"]["grades"])) for k, x in casos.items()})
