"""Regressão da faixa 8 (livros, prêmios e demais produções): cada formulário do spec confere com a captura real do Lattes
(paridade com 0 pendentes) e regras achadas na captura (valores reais com espaço no fim, natureza do livro bloqueada, autores nas mídias)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from ferramentas.valida_paridade import carregar_excecoes, comparar, slug  # noqa: E402

ITENS = ["livro_capitulo", "premio", "texto_jornal_revista", "traducao", "prefacio_posfacio", "partitura_musical", "musica", "artes_cenicas",
         "artes_visuais", "cartas_mapas", "maquete", "editoracao", "entrevista_midia", "redes_sociais", "relatorio_pesquisa", "outra_producao_artistica",
         "outra_producao_bibliografica", "outra_producao_tecnica", "manutencao_obra"]
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


def spec_de(item):
    return json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))


for item in ITENS:
    spec = spec_de(item)
    for v in spec["variantes"]:
        nomes = [c["name"].lower() for c in v["campos"]]
        checa(f"{item} / {v['variante']}: campos sem nome duplicado", bool(nomes) and len(nomes) == len(set(nomes)))
        refs = sorted(p for p in (RAIZ / "docs" / "campos-lattes" / "ref" / item).glob("*.json") if p.name != "excecoes.json")
        ref = next((json.loads(p.read_text(encoding="utf-8")) for p in refs if json.loads(p.read_text(encoding="utf-8")).get("variante_slug") in (slug(v["variante"]), item) and (len(spec["variantes"]) == 1 or json.loads(p.read_text(encoding="utf-8")).get("variante_slug") == slug(v["variante"]))), None)
        checa(f"{item} / {v['variante']}: captura real arquivada", ref is not None)
        if ref is None:
            continue
        just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes(item).get(ref["variante_slug"], [])}
        pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
        checa(f"{item} / {v['variante']}: paridade com a captura real, 0 pendentes", not pend, pend)

pf = spec_de("prefacio_posfacio")["variantes"][0]
sub = next(c for c in pf["campos"] if c["name"] == "f_sub_tipo")
checa("prefácio: valores reais da natureza (com espaço no fim, como no Lattes)", sorted(sub["opcoes"].values()) == ["31 ", "32 ", "33 "], sub["opcoes"])
lv = spec_de("livro_capitulo")["variantes"][0]
checa("livro: natureza bloqueada (o Lattes a preenche a partir do tipo)", next(c for c in lv["campos"] if c["name"].lower() == "f_sub_prod").get("bloqueado_no_lattes"))
for item in ("entrevista_midia", "redes_sociais"):
    checa(f"{item}: lista de autores", "autores" in {g["chave"] for g in spec_de(item)["variantes"][0]["grades"]})
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
