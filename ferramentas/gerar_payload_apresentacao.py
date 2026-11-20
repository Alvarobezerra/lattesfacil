"""Gera ferramentas/saida/payload_apresentacao.js (carga de salvamento da apresentação de trabalho, fase 7) como o app monta (genColetar).
Uso: python ferramentas/gerar_payload_apresentacao.py"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402
from itens.leitores import ler  # noqa: E402

USUARIO = "Álvaro Antônio Bezerra dos Santos"
TEXTO = ("Certificamos que o trabalho intitulado ZZ-TESTE-LATTESFACIL Apresentação de teste (validação automática) foi apresentado no 5º Encontro Regional de "
         "Química Exemplar (ERQE), realizado pela Universidade Federal do Maranhão, no período de 19 a 21 de agosto de 2024, em São Luís - MA, apresentado por "
         f"{USUARIO} e coautoria de ZZ Coautor de Teste no formato pôster.")


def carga():
    r = ler("apresentacao", TEXTO, USUARIO)
    spec = especificacao("apresentacao")
    var = spec["variantes"][0]
    v = dict(r["valores"])
    v["f_titulo"] = "ZZ-TESTE-LATTESFACIL Apresentação de teste (validação automática)"
    campos = []
    for c in var["campos"]:
        if c.get("oculto") or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    grades = {"autores": [{"nome": USUARIO, "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}],
              "palavras_chave": ["teste", "validação"], "areas": ["Microbiologia"]}
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": "apresentacao", "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "campos": campos, "faltam": r["faltam_obrigatorios"], "grades": grades}}


if __name__ == "__main__":
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    (saida / "payload_apresentacao.js").write_text("window.__payloadApresentacao = " + json.dumps(carga(), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", [(c["name"], c["valor"][:25]) for c in carga()["__generico"]["campos"] if c["valor"]])
