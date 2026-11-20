"""Gera ferramentas/saida/payload_projeto.js: uma carga de salvamento por variante de projeto (fase 7), montada como o app monta (genColetar),
com o leitor real (ler_projeto) sobre uma resolução de teste. Uso: python ferramentas/gerar_payload_projeto.py"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402
from itens.leitores import ler  # noqa: E402

USUARIO = "Álvaro Antônio Bezerra dos Santos"
TIPOS = {"Projetos de pesquisa": "Projeto de Pesquisa", "Projeto de extensão": "Projeto de Extensão", "Projeto de ensino": "Projeto de Ensino",
         "Projeto de desenvolvimento tecnológico": "Projeto de Desenvolvimento Tecnológico", "Outros tipos de projetos": "Projeto Especial"}


def carga(variante, rotulo):
    texto = (f"Art. 1º Homologar o {rotulo} intitulado ZZ-TESTE-LATTESFACIL {variante} (validação automática), coordenado pelo Professor {USUARIO}, "
             "da Coordenação do Curso de Medicina, vinculada ao Centro de Ciências de Imperatriz (CCIm), da Universidade Federal do Maranhão. São Luís, 28 de janeiro de 2025.")
    r = ler("projeto", texto, USUARIO)
    spec = especificacao("projeto")
    var = next(x for x in spec["variantes"] if x["variante"] == r["variante"]) if r["variante"] == variante else next(x for x in spec["variantes"] if x["variante"] == variante)
    v = dict(r["valores"])
    v["f_titulo"] = f"ZZ-TESTE-LATTESFACIL {variante} (validação automática)"
    v["f_orgao"] = "Centro de Ciências Sociais, Saúde e Tecnologia (CCSST) - Imperatriz- MA"  # nome exato do cadastro do Lattes (sem escolha aproximada)
    campos = []
    for c in var["campos"]:
        if c.get("oculto") and not c.get("mostrar_quando"):
            continue
        valor = str(v.get(c["name"], c.get("padrao", "")) or "")
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    grades = {"autores": [{"nome": USUARIO, "citacao": "SANTOS, A. A. B.", "coordenador": True}]}
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": "projeto", "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "campos": campos,
                           "faltam": [], "grades": grades}}


if __name__ == "__main__":
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    casos = {v: carga(v, TIPOS[v]) for v in TIPOS}
    (saida / "payload_projeto.js").write_text("window.__payloadProjeto = " + json.dumps(casos, ensure_ascii=False) + ";\n", encoding="utf-8")
    print({k: (x["__generico"]["url"][-30:], len(x["__generico"]["campos"])) for k, x in casos.items()})
