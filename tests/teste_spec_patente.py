"""Regressão do formulário de patente (conferido no Lattes real em 21/11/2026): spec por captura, opções reais, campos que entram pelo endereço de abertura,
paridade e robô (sugestão de pessoas pelo nome inteiro)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


spec = json.loads((RAIZ / "itens" / "especificacao" / "patente.json").read_text(encoding="utf-8"))
v = spec["variantes"][0]
c = {x["name"].lower(): x for x in v["campos"]}
checa("variante com nome do Lattes", v["variante"] == "Patente", v["variante"])
checa("potencial de inovação: Sim=S, Não=N (a captura desloca os textos)", list(c["f_sta_inovacao"]["opcoes"].items()) == [("Sim", "S"), ("Não", "N")], c["f_sta_inovacao"]["opcoes"])
checa("tipo: invenção (PI) e modelo de utilidade (MU)", sorted(c["f_tipo"]["opcoes"].values()) == ["MU", "PI"])
checa("instituição e nº do registro entram pelo endereço de abertura", c["f_inst"].get("entra_pela_abertura") and c["f_cod_reg"].get("entra_pela_abertura"))
checa("grades: situação, titulares (pessoas e instituições), inventores", {g["chave"] for g in v["grades"]} >= {"situacoes", "titulares_pessoa", "titulares_inst", "autores", "palavras_chave", "areas"})

from ferramentas.valida_paridade import carregar_excecoes, comparar  # noqa: E402

ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "patente" / "patente.json").read_text(encoding="utf-8"))
just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes("patente").get(ref["variante_slug"], [])}
pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
checa("paridade com a captura real: 0 pendentes (2 justificadas: textos do potencial de inovação)", not pend, pend)

app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
checa("robô: sugestão de pessoas aceita 'Nome (CITAÇÃO)' e tenta o nome curto", "tentativas" in app and "contém o nome inteiro" in app)
checa("robô: instituição de patente (lista fechada do endereço) não vai pela lupa", "escolhe_inst" in app)
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
