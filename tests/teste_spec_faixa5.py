"""Regressão da faixa 5 (produção técnica e registros): spec de cada item existe, tem variante e campos, e confere com a captura real do Lattes
(paridade com 0 pendentes, descontadas as exceções justificadas)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from ferramentas.valida_paridade import carregar_excecoes, comparar  # noqa: E402

ITENS = ["software_registro", "software_sem_registro", "produto", "processo_tecnica", "trabalho_tecnico", "relatorio_tecnico", "extensao_tecnologica",
         "material_didatico", "desenho_industrial", "marca_registrada", "topografia_circuito", "cultivar_protegida", "cultivar_registrada"]
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


for item in ITENS:
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    checa(f"{item}: spec com variante e campos", bool(spec["variantes"]) and bool(spec["variantes"][0]["campos"]))
    v = spec["variantes"][0]
    nomes = [c["name"].lower() for c in v["campos"]]
    checa(f"{item}: campos sem nome duplicado", len(nomes) == len(set(nomes)), [n for n in nomes if nomes.count(n) > 1])
    refp = RAIZ / "docs" / "campos-lattes" / "ref" / item / f"{item}.json"
    ref = json.loads(refp.read_text(encoding="utf-8"))
    just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes(item).get(ref["variante_slug"], [])}
    pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
    checa(f"{item}: paridade com a captura real, 0 pendentes", not pend, pend)

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
