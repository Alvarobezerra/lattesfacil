"""Regressão do formulário de participação em bancas de trabalhos de conclusão (conferido no Lattes real em 21/11/2026): spec por captura,
natureza, dependências da lupa (natureza antes de instituição/curso), opções reais e leitor de documento."""
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


spec = json.loads((RAIZ / "itens" / "especificacao" / "banca.json").read_text(encoding="utf-8"))
v = spec["variantes"][0]
c = {x["name"].lower(): x for x in v["campos"]}
checa("variante com nome do Lattes", v["variante"] == "Participação em bancas de trabalhos de conclusão", v["variante"])
checa("natureza: 6 opções do Lattes (A11..A16)", sorted(c["f_cod_prod"]["opcoes"].values()) == ["A11", "A12", "A13", "A14", "A15", "A16"] and c["f_cod_prod"]["rotulo"] == "Natureza", c["f_cod_prod"])
checa("tipo do mestrado: valores reais do Lattes (com espaço no fim)", list(c["f_sub_prod"]["opcoes"].values()) == ["34 ", "35 "], c["f_sub_prod"]["opcoes"])
checa("tipo do mestrado só com natureza Mestrado", c["f_sub_prod"].get("exige_antes", {}).get("valores") == ["Mestrado"], c["f_sub_prod"].get("exige_antes"))
checa("instituição e curso exigem a natureza antes (Lattes: 'Informe a natureza')", all(c[n].get("exige_antes", {}).get("name") == "F_COD_PROD" for n in ("f_inst", "f_curso")))
checa("grades: participantes, palavras-chave, áreas, setores", {g["chave"] for g in v["grades"]} >= {"autores", "palavras_chave", "areas", "setores"})

from ferramentas.valida_paridade import comparar  # noqa: E402

ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "banca" / "banca_trabalhos_conclusao.json").read_text(encoding="utf-8"))
checa("paridade com a captura real: 0 divergências", not comparar(v, ref), comparar(v, ref))

from itens.leitores import ler  # noqa: E402

r = ler("banca", "Declaramos que Fulano de Tal participou como Presidente da banca examinadora da dissertação de mestrado da mestranda Maria da Silva, do curso de "
        "Farmácia, intitulada \"Efeito do extrato sobre células\", em sessão realizada em 10 de maio de 2024, na Universidade Federal do Maranhão.", "Fulano de Tal")
val = (r or {}).get("valores", {})
checa("leitor: tipo Mestrado e subtipo Acadêmico", val.get("F_COD_PROD") == "Mestrado" and val.get("f_sub_prod") == "Acadêmico", val)
# --- Bancas de comissões julgadoras (mesma família) ---
spec2 = json.loads((RAIZ / "itens" / "especificacao" / "banca_comissao_julgadora.json").read_text(encoding="utf-8"))
v2 = spec2["variantes"][0]
c2 = {x["name"].lower(): x for x in v2["campos"]}
checa("comissão: variante com nome do Lattes", v2["variante"] == "Participação em bancas de comissões julgadoras", v2["variante"])
checa("comissão: natureza com 5 opções (A21..A24, A29)", sorted(c2["f_cod_prod"]["opcoes"].values()) == ["A21", "A22", "A23", "A24", "A29"] and c2["f_cod_prod"]["rotulo"] == "Natureza", c2["f_cod_prod"])
checa("comissão: instituição obrigatória (asterisco) e exige a natureza antes", c2["f_inst"].get("obrigatorio") is True and c2["f_inst"].get("exige_antes", {}).get("name") == "F_COD_PROD", c2["f_inst"])
ref2 = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "banca_comissao_julgadora" / "banca_comissao_julgadora.json").read_text(encoding="utf-8"))
from ferramentas.valida_paridade import carregar_excecoes  # noqa: E402

just2 = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes("banca_comissao_julgadora").get(ref2["variante_slug"], [])}
pend2 = [d for d in comparar(v2, ref2) if (d["categoria"], d["campo"].lower()) not in just2]
checa("comissão: paridade com a captura real: 0 divergências (1 justificada: rótulo '*')", not pend2 and len(just2) == 1, pend2)
app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
checa("robô: campo marcado como lupa (input-lupa) vai pela janela de seleção mesmo habilitado", "input-lupa" in app)
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
