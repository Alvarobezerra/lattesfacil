"""Regressão da ponte entre registros no formato antigo (caderno de resumos, histórico) e o formulário gerado pelo spec (anais e artigo),
e do enriquecimento (Crossref/OpenAlex) sobre o formulário novo. Sem rede: a busca externa é simulada."""
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


from itens import leitores  # noqa: E402

reg_anais = {"tipo_producao": "anais", "natureza": "Resumo", "titulo": "Efeito do extrato", "ano": "2024", "nome_evento": "Simpósio Exemplar",
             "classificacao_evento": "Nacional", "cidade_evento": "São Luís - MA", "titulo_anais": "Anais do Simpósio Exemplar", "isbn_issn": "978-0-306-40615-7",
             "autores": [{"nome": "Maria Souza", "citacao": "SOUZA, M."}], "palavras_chave": ["babaçu", "2024"], "area_conhecimento": "Farmacognosia"}
g = leitores.de_registro_antigo("anais", reg_anais)
v = g["valores"]
checa("anais: registro antigo vira valores do formulário do spec", v["f_titulo"] == "Efeito do extrato" and v["f_evento"] == "Simpósio Exemplar" and v["F_COD_PROD"] == "Resumo" and v["f_tipo_evento"] == "Nacional", v)
checa("anais: autores, palavras-chave (sem o ano) e áreas viram listas", v["grade:autores"][0]["nome"] == "Maria Souza" and v["grade:palavras_chave"] == ["babaçu"] and v["grade:areas"] == ["Farmacognosia"], v)
checa("anais: ISBN com hífens vira só dígitos", v["f_isbn"] == "9780306406157", v["f_isbn"])
checa("anais: variante e obrigatórios calculados como na leitura de documento", g["variante"] == "Trabalho publicado em anais de evento" and isinstance(g["faltam_obrigatorios"], list), g)

reg_artigo = {"tipo_producao": "artigo", "titulo": "Artigo X", "ano": "2025", "periodico": "Revista Y", "isbn_issn": "0034-8910", "volume": "12", "pagina_inicial": "101",
              "autores": [{"nome": "Ana Lima", "citacao": "LIMA, A."}]}
ga = leitores.de_registro_antigo("artigo", reg_artigo)
va = ga["valores"]
checa("artigo: registro antigo vira valores do spec", va["f_titulo_periodico"] == "Revista Y" and va["f_issn"] == "0034-8910" and va["f_volume"] == "12" and va["f_pag_ini"] == "101", va)
checa("item sem ponte devolve None (segue no formulário antigo)", leitores.de_registro_antigo("livro_capitulo", {}) is None)

# volta: formulário do spec -> registro antigo (alimenta o enriquecimento)
rec = leitores.para_registro_antigo("artigo", {"f_cod_doi": "10.1/x", "f_titulo": "T", "f_titulo_periodico": "", "f_ano": ""})
checa("volta ao registro antigo ignora campos vazios", rec == {"doi": "10.1/x", "titulo": "T", "tipo_producao": "artigo"}, rec)

# enriquecimento simulado (sem rede)
import extractor  # noqa: E402

original = extractor.enrich_missing_fields
extractor.enrich_missing_fields = lambda r: {"suggestions": {"ano": "2005", "titulo_anais": "PLoS Medicine", "isbn_issn": "1549-1676", "pagina_inicial": "e124"}, "sources": ["Crossref API"]}
try:
    e = leitores.enriquecer("artigo", {"f_cod_doi": "10.1371/x", "f_titulo": "T"})
    checa("enriquecimento: completa só campos vazios, no formato do spec", e["valores"].get("f_ano") == "2005" and e["valores"].get("f_titulo_periodico") == "PLoS Medicine"
          and e["valores"].get("f_issn") == "1549-1676" and "f_titulo" not in e["valores"], e)
    e2 = leitores.enriquecer("artigo", {"f_cod_doi": "10.1371/x", "f_titulo": "T", "f_ano": "1999"})
    checa("enriquecimento: não sobrescreve o que já está preenchido", "f_ano" not in e2["valores"], e2)
    checa("enriquecimento: fonte informada", e["fontes"] == ["Crossref API"])
finally:
    extractor.enrich_missing_fields = original

# rotas e cliente
srv = (RAIZ / "server.py").read_text(encoding="utf-8")
app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
checa("servidor: rotas da ponte", "/api/itens/abrir-registro" in srv and "/api/itens/enriquecer" in srv)
checa("app: caderno e histórico abrem no formulário do spec", "abrirRegistroAntigo(r.record)" in app and "abrirRegistroAntigo(rec.data)" in app)
checa("app: botão de buscar dados faltantes no formulário do spec", "btnGenEnriquecer" in app)

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
