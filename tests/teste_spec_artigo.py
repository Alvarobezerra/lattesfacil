"""Regressão do formulário de artigo em periódico (conferido no Lattes real em 20-21/11/2026): spec por captura, idiomas, campos bloqueados,
leitor de citação do PDF, palavras-chave em inglês e presença das proteções do robô de preenchimento na extensão."""
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


spec = json.loads((RAIZ / "itens" / "especificacao" / "artigo.json").read_text(encoding="utf-8"))
v = spec["variantes"][0]
c = {x["name"].lower(): x for x in v["campos"]}
checa("variante com nome do Lattes", v["variante"] == "Artigo completo publicado em periódico", v["variante"])
checa("idioma: só as 80 opções do formulário real (não o catálogo de 152)", len(c["f_idioma"].get("opcoes", {})) == 80 and "Português" in c["f_idioma"]["opcoes"], len(c["f_idioma"].get("opcoes", {})))
checa("idioma sem o catálogo completo como fonte", not c["f_idioma"].get("catalogo"))
for n in ("f_titulo_periodico", "f_issn", "f_volume", "f_serie", "f_pag_ini", "f_jcr"):
    checa(f"{n} bloqueado no Lattes", c[n].get("bloqueado_no_lattes") is True)
checa("radios Sim/Não com rótulo do Lattes", c["f_relev"]["opcoes"] == {"Sim": "S", "Não": "N"} and c["f_relev"]["rotulo"].startswith("É um dos 10"))
checa("grades: autores, palavras-chave, áreas, setores", {g["chave"] for g in v["grades"]} >= {"autores", "palavras_chave", "areas", "setores"}, [g["chave"] for g in v["grades"]])

# paridade com a captura real
from ferramentas.valida_paridade import comparar  # noqa: E402

ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "artigo" / "artigo_periodico.json").read_text(encoding="utf-8"))
div = comparar(v, ref)
checa("paridade com a captura real: 0 divergências", not div, div)
checa("captura com os radios Sim/Não lidos certo", [o["texto"].lower()[:1] for o in next(x for x in ref["campos"] if x["name"] == "F_RELEV")["opcoes"]] == ["s", "n"])

# leitor: citação do PDF (sem DOI resolvido)
from itens.leitores import ler  # noqa: E402

texto = ("Autora Exemplo, Outro Autor\nJournal of Exemplary Food Science, Volume 12, Issue 3, pp. 101-110, 2025. ISSN 0000-0000. "
         "DOI 10.9999/jefs.2025.0123\nKeywords: probióticos; babaçu; bebidas.")
r = ler("artigo", texto, "")
val = r["valores"]
checa("leitor: periódico, volume, edição, páginas e ISSN da citação", (val.get("f_titulo_periodico"), val.get("f_volume"), val.get("f_serie"), val.get("f_pag_ini"), val.get("f_pag_fim"), val.get("f_issn")) ==
      ("Journal of Exemplary Food Science", "12", "3", "101", "110", "0000-0000"), val)
checa("leitor: palavras-chave do PDF valem mais que a sugestão do título", val.get("grade:palavras_chave") == ["probióticos", "babaçu", "bebidas"], val.get("grade:palavras_chave"))
checa("leitor: radios com o rótulo do spec (Não)", val.get("F_RELEV") == "Não" and val.get("F_STA_DIVULGACAO_CIENTIFICA") == "Não", (val.get("F_RELEV"), val.get("F_STA_DIVULGACAO_CIENTIFICA")))

# palavras-chave: títulos em inglês não geram lixo
from itens.sugestoes import palavras_chave  # noqa: E402

checa("palavras-chave: 'Why Most Published Research Findings Are False' não gera lixo", palavras_chave("Why Most Published Research Findings Are False") == [])
checa("palavras-chave: frase nominal em inglês", "Intestinal mucositis" in palavras_chave("Moringa oleifera attenuates intestinal mucositis"))

# a extensão precisa conter as proteções do robô (alertas, validações do Lattes, lista antes do formulário, idempotência)
ext = (RAIZ / "extensao" / "autofill_core.js").read_text(encoding="utf-8")
for marca, porque in (("__lfRestaurarAlertas", "silencia alertas do Lattes"), ("prc_valida_issn", "valida o ISSN como o Lattes"),
                      ("valida_nome_issn_periodico", "valida nome x ISSN"), ("find_periodico", "busca o periódico por nome"),
                      ("pkg_artigo.lista", "carrega a lista antes do formulário"), ("já está na lista", "não repete itens das listas"),
                      ("__semAlerta", "modo sem diálogos para automação")):
    checa(f"extensão: {porque}", marca in ext)

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
