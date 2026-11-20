"""Gera ferramentas/saida/payload_orientacao.js: cargas de salvamento das orientações (concluída e em andamento), como o app monta (genColetar).
Uso: python ferramentas/gerar_payload_orientacao.py"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402
from itens.leitores import ler  # noqa: E402

USUARIO = "Álvaro Antônio Bezerra dos Santos"
TEXTOS = {
    "orientacao_concluida": f"Declaramos que {USUARIO} orientou como orientador principal o trabalho de conclusão de curso de ZZ Orientando de Teste, do curso de Farmácia, "
                            "da Universidade Federal do Maranhão, intitulado \"ZZ-TESTE-LATTESFACIL Orientação concluída de teste (validação automática)\", defendido e aprovado em 2023.",
    "orientacao_andamento": f"Declaramos que {USUARIO} orienta atualmente o aluno ZZ Orientando de Teste, do curso de Farmácia da Universidade Federal do Maranhão, no trabalho "
                            "intitulado \"ZZ-TESTE-LATTESFACIL Orientação em andamento de teste (validação automática)\", em andamento, com início em 2025.",
}


def carga(item):
    r = ler(item, TEXTOS[item], USUARIO)
    spec = especificacao(item)
    var = spec["variantes"][0]
    v = dict(r["valores"])
    v["f_inst"] = "Universidade Federal do Maranhão"
    v["f_curso"] = "Farmácia"
    if item == "orientacao_andamento":
        v["f_ano"] = "2025"
    if not v.get("F_COD_PROD"):
        opcoes = next(c for c in var["campos"] if c["name"] == "F_COD_PROD")["opcoes"]
        v["F_COD_PROD"] = next(k for k in opcoes if k.startswith("Trabalho"))
    campos = []
    for c in var["campos"]:
        if c.get("oculto") or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    grades = {k.split(":", 1)[1]: x for k, x in v.items() if k.startswith("grade:")}
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": item, "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "campos": campos, "faltam": r["faltam_obrigatorios"], "grades": grades}}


if __name__ == "__main__":
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    casos = {i: carga(i) for i in TEXTOS}
    (saida / "payload_orientacao.js").write_text("window.__payloadOrientacao = " + json.dumps(casos, ensure_ascii=False) + ";\n", encoding="utf-8")
    for k, x in casos.items():
        print(k, [(c["name"], c["valor"][:22]) for c in x["__generico"]["campos"] if c["valor"]], x["__generico"]["faltam"])
