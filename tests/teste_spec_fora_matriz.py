"""Regressão dos itens fora da matriz: paridade do spec com a captura real (0 pendentes, descontadas as exceções justificadas).
Formação acadêmica fica de fora até as lupas das instituições do doutorado sanduíche (f_inst_dout*) serem tratadas (pendência bloqueante no STATUS)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from ferramentas.valida_paridade import carregar_excecoes, comparar, slug  # noqa: E402

ITENS = ["artigo_aceito", "atuacao_profissional", "citacao_google_scholar", "citacao_outra_base", "citacao_scielo", "citacao_scopus", "citacao_web_of_science",
         "comite_assessoramento", "corpo_editorial", "endereco", "formacao_complementar", "identificacao", "idioma", "licenca", "outras_informacoes",
         "revisor_periodico", "revisor_projeto_fomento", "texto_inicial", "pos_doutorado"]
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


for item in ITENS:
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    for v in spec["variantes"]:
        refs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "docs" / "campos-lattes" / "ref" / item).glob("*.json")) if p.name != "excecoes.json"]
        ref = next((r for r in refs if r.get("variante_slug") in ((slug(v["variante"]),) if len(spec["variantes"]) > 1 else (item, slug(v["variante"])))), None)
        checa(f"{item} / {v['variante']}: captura real arquivada", ref is not None)
        if ref is None:
            continue
        just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes(item).get(ref["variante_slug"], [])}
        pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
        checa(f"{item} / {v['variante']}: paridade com a captura real, 0 pendentes", not pend, pend)
end = json.loads((RAIZ / "itens" / "especificacao" / "endereco.json").read_text(encoding="utf-8"))["variantes"][0]
corr = [c for c in end["campos"] if c["name"].lower() == "f_end_corr"]
checa("endereço: um único grupo 'para correspondência' com R e I", len(corr) == 1 and sorted(corr[0]["opcoes"].values()) == ["I", "R"])
at = json.loads((RAIZ / "itens" / "especificacao" / "atuacao_profissional.json").read_text(encoding="utf-8"))["variantes"][0]
checa("atuação: ano/mês de fim só com situação 'Anterior'", all(c.get("mostrar_quando", {}).get("valor", "").startswith("Anterior") for c in at["campos"] if c["name"] in ("f_ano_fim", "f_mes_fim")))
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
