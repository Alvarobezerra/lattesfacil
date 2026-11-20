"""Regressão da faixa 7 (eventos e cursos): spec de cada item confere com a captura real do Lattes (paridade, 0 pendentes) e o tipo da
participação em eventos depende da forma (Convidado/Participante exigem; Ouvinte não tem lista)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from ferramentas.valida_paridade import carregar_excecoes, comparar  # noqa: E402

ITENS = ["participacao_evento", "organizacao_evento", "curso_ministrado"]
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


for item in ITENS:
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    v = spec["variantes"][0]
    nomes = [c["name"].lower() for c in v["campos"]]
    checa(f"{item}: spec com campos, sem nome duplicado", bool(nomes) and len(nomes) == len(set(nomes)))
    ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / item / f"{item}.json").read_text(encoding="utf-8"))
    just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes(item).get(ref["variante_slug"], [])}
    pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
    checa(f"{item}: paridade com a captura real, 0 pendentes", not pend, pend)

v = json.loads((RAIZ / "itens" / "especificacao" / "participacao_evento.json").read_text(encoding="utf-8"))["variantes"][0]
tpo = next(c for c in v["campos"] if c["name"] == "F_TPO")
checa("participação: tipo exigido só para Convidado e Participante", tpo["obrigatorio_quando"]["valor"] == ["Convidado", "Participante"] and not tpo["obrigatorio"])
checa("participação: tipos por forma conferidos no Lattes (5 / 3 / nenhum)", [len(x) for x in tpo["opcoes_por"]["valores"].values()] == [5, 3, 0])
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
