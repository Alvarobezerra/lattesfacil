"""Gera ferramentas/saida/payload_anais.js: carga do trabalho em anais montada como o app monta (genColetar), para o teste de
preenchimento real (fase 5) e o salvamento de teste (fase 7). Uso: python ferramentas/gerar_payload_anais.py"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402
from itens.leitores import ler  # noqa: E402

TEXTO = ("ZZ-TESTE-LATTESFACIL Trabalho de teste em anais (validação automática)\n"
         "Resumo: texto de teste.\nPalavras-chave: teste; validação; anais.\n"
         "Anais do Simpósio Exemplar de Iniciação Científica, 2024.\nISBN 978-0-306-40615-7")


def carga(titular=False):
    r = ler("anais", TEXTO, "")
    spec = especificacao("anais")
    var = spec["variantes"][0]
    v = dict(r["valores"])
    v.update({"f_titulo": "ZZ-TESTE-LATTESFACIL Trabalho de teste em anais (validação automática)", "f_evento": "Simpósio Exemplar de Iniciação Científica",
              "f_titulo_pub": "Anais do Simpósio Exemplar de Iniciação Científica", "f_cidade_evento": "São Luís - MA", "f_tipo_evento": "Nacional",
              "F_COD_PROD": "Resumo", "f_pag_ini": "10", "f_pag_fim": "11", "f_editora": "Editora Exemplar", "f_cidade_ed": "São Luís"})
    campos = []
    for c in var["campos"]:
        if c.get("oculto") or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    autores = [{"nome": "ZZ Autor de Teste", "citacao": "TESTE, Z. A."}]
    if titular:
        autores = [{"nome": "Álvaro Antônio Bezerra dos Santos", "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}]
    grades = {"autores": autores, "palavras_chave": ["teste", "validação", "anais"], "areas": ["Microbiologia"]}
    p = {"tipo_producao": "generico", "__usuario": "Álvaro Antônio Bezerra dos Santos" if titular else "", "__origem": "", "__autoSalvar": titular, "__semAlerta": True,
         "__generico": {"id": "anais", "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "campos": campos, "faltam": [], "grades": grades}}
    return p


if __name__ == "__main__":
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    casos = {"preencher": carga(False), "salvar": carga(True)}
    (saida / "payload_anais.js").write_text("window.__payloadAnais = " + json.dumps(casos, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", {k: len(x["__generico"]["campos"]) for k, x in casos.items()})
