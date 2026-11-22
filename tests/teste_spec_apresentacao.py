"""Regressão do formulário de apresentação de trabalho e palestra (conferido no Lattes real em 21/11/2026): spec por captura, natureza, opções reais
de país e idioma, leitor de certificado e abertura de registros antigos."""
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


spec = json.loads((RAIZ / "itens" / "especificacao" / "apresentacao.json").read_text(encoding="utf-8"))
v = spec["variantes"][0]
c = {x["name"].lower(): x for x in v["campos"]}
checa("variante com nome do Lattes", v["variante"] == "Apresentação de trabalho e palestra", v["variante"])
checa("natureza: 6 opções do Lattes (2J1..2J9)", list(c["f_cod_prod"]["opcoes"].values()) == ["2J1", "2J2", "2J3", "2J4", "2J5", "2J9"] and c["f_cod_prod"]["rotulo"] == "Natureza", c["f_cod_prod"])
checa("país e idioma: 244 países e 152 idiomas do catálogo completo", len(c["f_pais"].get("opcoes", {})) == 244 and len(c["f_idioma"].get("opcoes", {})) == 152, (len(c["f_pais"].get("opcoes", {})), len(c["f_idioma"].get("opcoes", {}))))
checa("grades: autores, palavras-chave, áreas, setores", {g["chave"] for g in v["grades"]} >= {"autores", "palavras_chave", "areas", "setores"})

from ferramentas.valida_paridade import comparar  # noqa: E402

ref = json.loads((RAIZ / "docs" / "campos-lattes" / "ref" / "apresentacao" / "apresentacao_trabalho.json").read_text(encoding="utf-8"))
checa("paridade com a captura real: 0 divergências", not comparar(v, ref), comparar(v, ref))

from itens.leitores import de_registro_antigo, ler  # noqa: E402

r = ler("apresentacao", "Certificamos que o trabalho intitulado Efeito do extrato foi apresentado no XII Congresso Brasileiro de Ciências (CBC), realizado pela Sociedade X, "
        "no período de 10 a 12 de maio de 2024, em São Luís - MA.", "")
val = r["valores"]
checa("leitor: título, evento, promotora, cidade e ano", (val.get("f_titulo"), val.get("f_nme_evento"), val.get("f_inst"), val.get("f_cidade"), val.get("f_ano")) ==
      ("Efeito do extrato", "XII Congresso Brasileiro de Ciências (CBC)", "Sociedade X", "São Luís - MA", "2024"), val)
checa("leitor: natureza pelo tipo de evento (Congresso)", val.get("F_COD_PROD") == "Congresso", val.get("F_COD_PROD"))
g = de_registro_antigo("apresentacao", {"tipo_producao": "apresentacao", "natureza": "Seminário", "titulo": "Registro antigo", "ano": "2023", "nome_evento": "Seminário X"})
checa("registro antigo abre no formulário do spec", g["valores"]["f_titulo"] == "Registro antigo" and g["valores"]["f_nme_evento"] == "Seminário X" and g["valores"]["F_COD_PROD"] == "Seminário", g["valores"])

srv = (RAIZ / "server.py").read_text(encoding="utf-8")
app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
checa("servidor: apresentação sai do caminho antigo", 'item_id == "apresentacao":\n        extracted = parse_certificado' not in srv)
checa("app: apresentação sem formulário antigo no 'em branco'", 'apresentacao: "apresentacao", orientacao_concluida' not in app)
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
