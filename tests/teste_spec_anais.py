"""Regressão do formulário de trabalho em anais (conferido no Lattes real em 21/11/2026): spec por captura, opções reais de país e idioma,
leitor (ISBN só com dígitos, título e nome do evento a partir de "Anais do ...") e marcas do robô na extensão."""
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


spec = json.loads((RAIZ / "itens" / "especificacao" / "anais.json").read_text(encoding="utf-8"))
v = spec["variantes"][0]
c = {x["name"].lower(): x for x in v["campos"]}
checa("variante com nome do Lattes", v["variante"] == "Trabalho publicado em anais de evento", v["variante"])
checa("natureza: Completo/Resumo/Resumo Expandido (121/122/123)", c["f_cod_prod"]["opcoes"] == {"Completo": "121", "Resumo": "122", "Resumo Expandido": "123"} and c["f_cod_prod"]["rotulo"] == "Natureza", c["f_cod_prod"])
checa("classificação do evento: Internacional/Nacional/Regional/Local", c["f_tipo_evento"]["opcoes"] == {"Internacional": "I", "Nacional": "N", "Regional": "R", "Local": "L"} and c["f_tipo_evento"]["rotulo"] == "Classificação do evento")
checa("país: 80 opções reais (não as 244 do catálogo)", len(c["f_pais"].get("opcoes", {})) == 80 and "Brasil" in c["f_pais"]["opcoes"], len(c["f_pais"].get("opcoes", {})))
checa("idioma: 80 opções reais (não as 152 do catálogo)", len(c["f_idioma"].get("opcoes", {})) == 80)
checa("grades: autores, palavras-chave, áreas, setores", {g["chave"] for g in v["grades"]} >= {"autores", "palavras_chave", "areas", "setores"})

from ferramentas.valida_paridade import comparar  # noqa: E402

ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "anais" / "anais_evento.json").read_text(encoding="utf-8"))
div = comparar(v, ref)
checa("paridade com a captura real: 0 divergências", not div, div)
rot = {x["name"]: [o["texto"] for o in x["opcoes"]] for x in ref["campos"] if x["tipo"] == "radio"}
checa("captura: radios lidos pelo texto mais próximo do botão", rot["F_COD_PROD"] == ["Completo", "Resumo", "Resumo Expandido"] and rot["f_tipo_evento"][0] == "Internacional", rot)

from itens.leitores import ler  # noqa: E402

texto = ("Efeito do extrato de babaçu na viabilidade celular\nMaria Souza\nAnais do Simpósio Exemplar de Iniciação Científica, 2024.\n"
         "Palavras-chave: babaçu; viabilidade celular.\nISBN 978-0-306-40615-7")
r = ler("anais", texto, "")
val = r["valores"]
checa("leitor: ISBN com hífens vira só dígitos (limite de 13 do Lattes)", val.get("f_isbn") == "9780306406157", val.get("f_isbn"))
checa("leitor: título dos anais e nome do evento", val.get("f_titulo_pub", "").startswith("Anais do Simpósio Exemplar") and val.get("f_evento", "").startswith("Simpósio Exemplar"), (val.get("f_titulo_pub"), val.get("f_evento")))
checa("leitor: não cobra obrigatório que o documento traz", not r["faltam_obrigatorios"], r["faltam_obrigatorios"])
checa("leitor: ano do evento não vira palavra-chave", "2024" not in (val.get("grade:palavras_chave") or []), val.get("grade:palavras_chave"))

ext = (RAIZ / "extensao" / "autofill_core.js").read_text(encoding="utf-8")
for marca, porque in (("pkg_trabalho.lista", "carrega a lista antes do formulário de anais"), ("Operação realizada com sucesso", "reconhece o sucesso do Lattes ao salvar"),
                      ("N[ãa]o foi poss", "lê os pop-ups de erro do Lattes ao salvar")):
    checa(f"extensão: {porque}", marca in ext)

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
