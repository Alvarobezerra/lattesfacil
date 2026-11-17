"""Testes de lote, XML do Lattes, auditor e EditalScore (sem servidor; PDFs gerados na hora).

Uso: python tests/teste_novos_modulos.py
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymupdf  # noqa: E402

import edital  # noqa: E402
from auditor import auditar, isbn_valido, issn_valido  # noqa: E402
from lattes_xml import ler_curriculo, procurar_duplicata  # noqa: E402
from lote import expandir, gerar_zip_organizado, processar_lote  # noqa: E402

XML = """<?xml version="1.0" encoding="ISO-8859-1"?>
<CURRICULO-VITAE NUMERO-IDENTIFICADOR="1234567890123456" DATA-ATUALIZACAO="01012026">
 <DADOS-GERAIS NOME-COMPLETO="João da Silva" NOME-EM-CITACOES-BIBLIOGRAFICAS="SILVA, J.">
  <ATUACOES-PROFISSIONAIS>
   <ATUACAO-PROFISSIONAL NOME-INSTITUICAO="Universidade X"><VINCULOS ANO-INICIO="2005" ANO-FIM=""/></ATUACAO-PROFISSIONAL>
  </ATUACOES-PROFISSIONAIS>
 </DADOS-GERAIS>
 <PRODUCAO-BIBLIOGRAFICA>
  <ARTIGOS-PUBLICADOS>
   <ARTIGO-PUBLICADO>
    <DADOS-BASICOS-DO-ARTIGO TITULO-DO-ARTIGO="Probiotic beverages from babassu" ANO-DO-ARTIGO="2022" DOI="10.1016/j.jff.2022.001"/>
    <DETALHAMENTO-DO-ARTIGO TITULO-DO-PERIODICO-OU-REVISTA="J Funct Foods" ISSN="17564646"/>
    <AUTORES NOME-COMPLETO-DO-AUTOR="João da Silva"/>
   </ARTIGO-PUBLICADO>
   <ARTIGO-PUBLICADO>
    <DADOS-BASICOS-DO-ARTIGO TITULO-DO-ARTIGO="Probiotic Beverages from Babassu." ANO-DO-ARTIGO="2022" DOI="https://doi.org/10.1016/j.jff.2022.001"/>
    <DETALHAMENTO-DO-ARTIGO TITULO-DO-PERIODICO-OU-REVISTA="J Funct Foods" ISSN="12345678"/>
    <AUTORES NOME-COMPLETO-DO-AUTOR="Joao da Silva"/>
   </ARTIGO-PUBLICADO>
   <ARTIGO-PUBLICADO>
    <DADOS-BASICOS-DO-ARTIGO TITULO-DO-ARTIGO="Artigo do futuro" ANO-DO-ARTIGO="2099" DOI=""/>
    <DETALHAMENTO-DO-ARTIGO TITULO-DO-PERIODICO-OU-REVISTA="Rev X" ISSN=""/>
   </ARTIGO-PUBLICADO>
  </ARTIGOS-PUBLICADOS>
  <LIVROS-E-CAPITULOS>
   <LIVROS-PUBLICADOS-OU-ORGANIZADOS>
    <LIVRO-PUBLICADO-OU-ORGANIZADO>
     <DADOS-BASICOS-DO-LIVRO TITULO-DO-LIVRO="Livro de testes" ANO="2020"/>
     <DETALHAMENTO-DO-LIVRO ISBN="9781234567890"/>
    </LIVRO-PUBLICADO-OU-ORGANIZADO>
   </LIVROS-PUBLICADOS-OU-ORGANIZADOS>
  </LIVROS-E-CAPITULOS>
 </PRODUCAO-BIBLIOGRAFICA>
 <DADOS-COMPLEMENTARES>
  <FORMACAO-COMPLEMENTAR>
   <CURSO-DE-CURTA-DURACAO><NOME-CURSO-DUMMY/></CURSO-DE-CURTA-DURACAO>
  </FORMACAO-COMPLEMENTAR>
 </DADOS-COMPLEMENTARES>
</CURRICULO-VITAE>
""".replace("<NOME-CURSO-DUMMY/>", "").replace("<CURSO-DE-CURTA-DURACAO>", '<CURSO-DE-CURTA-DURACAO NOME-CURSO="Bioestatística" ANO-DE-CONCLUSAO="2021">')

BAREMA = """EDITAL 12/2026 - PROVA DE TÍTULOS
PRODUÇÃO CIENTÍFICA (máximo 40 pontos)
Artigo publicado em periódico: 10 pontos por artigo, máximo 30 pontos
Livro publicado com ISBN: 8 pontos por livro
Curso de capacitação concluído - 2 pontos por curso (nos últimos 5 anos)
Artigo em periódico Qualis A1 - 15 pontos por artigo
Pontuação máxima total: 50 pontos
"""


def pdf(texto: str) -> bytes:
    d = pymupdf.open()
    d.new_page().insert_text((72, 100), texto, fontsize=11)
    return d.tobytes()


ok = falhas = 0


def checa(nome: str, cond: bool, detalhe: str = "") -> None:
    global ok, falhas
    print(("OK     " if cond else "FALHA  ") + nome + ("" if cond else f"  | {detalhe}"))
    ok += cond
    falhas += not cond


def main() -> int:
    # --- XML
    cur = ler_curriculo(XML.encode("iso-8859-1"))
    cats = [i["categoria"] for i in cur["itens"]]
    checa("XML: nome e itens", cur["nome"] == "João da Silva" and cats.count("artigo") == 3 and "livro" in cats
          and "formacao_complementar" in cats and "atuacao_profissional" in cats, str(cats))
    checa("XML: ZIP com XML dentro", ler_curriculo(_zip({"curriculo.xml": XML.encode("iso-8859-1")}))["nome"] == "João da Silva")
    try:
        ler_curriculo(b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><CURRICULO-VITAE/>')
        checa("XML: recusa DTD/entidades", False)
    except ValueError:
        checa("XML: recusa DTD/entidades", True)
    try:
        ler_curriculo(b"<outro/>")
        checa("XML: recusa outro formato", False)
    except ValueError:
        checa("XML: recusa outro formato", True)

    # --- duplicatas
    d = procurar_duplicata(cur, {"titulo": "Probiotic beverages from babassu", "ano": "2022"})
    checa("Duplicata por título", bool(d) and d[0]["similaridade"] >= 0.88, str(d))
    d = procurar_duplicata(cur, {"titulo": "Outro assunto", "doi": "10.1016/J.JFF.2022.001"})
    checa("Duplicata por DOI (com prefixo/caixa)", bool(d) and d[0]["motivo"] == "mesmo DOI")
    checa("Sem falso positivo", not procurar_duplicata(cur, {"titulo": "Efeito do exercício em idosos", "ano": "2022"}))

    # --- auditor
    checa("ISSN válido/ inválido", issn_valido("1756-4646") and not issn_valido("1234-5678") and issn_valido("0378-5955"))
    checa("ISBN válido/ inválido", isbn_valido("978-0-306-40615-7") and not isbn_valido("9781234567890"))
    import datetime
    a = auditar(cur, datetime.date(2026, 11, 16))
    codigos = {p["codigo"] for p in a["pendencias"]}
    esperados = {"duplicado", "ano_futuro", "issn_invalido", "isbn_invalido", "doi_formato", "sem_doi", "vinculo_sem_fim", "nome_inconsistente"}
    checa("Auditor: pendências esperadas", esperados <= codigos, f"faltam {esperados - codigos}")
    checa("Auditor: ordenado por risco", [p["risco"] for p in a["pendencias"]] == sorted((p["risco"] for p in a["pendencias"]),
          key=("Gravíssimo", "Grave", "Leve").index))

    # --- barema e pontuação
    b = edital.ler_barema(BAREMA, "Edital 12/2026")
    itens = [i for bl in b["blocos"] for i in bl["itens"]]
    checa("Barema: blocos/itens/teto global", len(itens) == 4 and b["teto_global"] == 50 and b["blocos"][0]["teto"] == 40, str(b)[:300])
    art = next(i for i in itens if i["descricao"].lower().startswith("artigo publicado"))
    checa("Barema: teto do item e categoria", art["teto"] == 30 and art["categorias"] == ["artigo"] and art["pontos_unitarios"] == 10)
    curso = next(i for i in itens if "curso" in i["descricao"].lower())
    checa("Barema: janela de anos", curso["janela_anos"] == 5)
    r = edital.calcular(b, [i for i in cur["itens"] if i["ano"] != "2099"], 2026)
    # 2 artigos (2022) = 20 + livro 8 + curso de 2021 fora da janela = 28; Qualis sem base = pendência
    checa("Cálculo: total e pendência Qualis", r["total"] == 28 and any(i["status"] == "pendente_qualis" for bl in r["blocos"] for i in bl["itens"]), str(r["total"]))
    r2 = edital.calcular(b, cur["itens"], 2026, evidencias={"artigo": 1, "livro": 1})
    checa("Cálculo: comprovantes", r2["total_sem_comprovante"] > r2["total"], f"{r2['total_sem_comprovante']} x {r2['total']}")
    s = edital.simular(b, [i for i in cur["itens"] if i["ano"] != "2099"], [{"categoria": "artigo"}], 2026)
    checa("Simulação: +1 artigo = +10 (teto do item 30 ainda não atingido)", s["diferenca"] == 10.0, str(s))
    s2 = edital.simular(b, [i for i in cur["itens"] if i["ano"] != "2099"], [{"categoria": "artigo"}] * 5, 2026)
    checa("Simulação: respeita teto do item", s2["diferenca"] == 10.0, str(s2))  # 2 existentes+5 = 7 -> teto 30 (antes 20)
    checa("Lacunas apontam teto", any(l["situacao"] == "teto atingido" for l in edital.lacunas(edital.calcular(b, cur["itens"] * 3, 2026))))

    # --- dossiê
    raw = edital.gerar_dossie("João da Silva", "Edital 12/2026", [
        {"item": "1.1", "descricao": "Artigo A", "nome": "a.pdf", "dados": pdf("Artigo A")},
        {"item": "1.2", "descricao": "Livro", "nome": "b.pdf", "dados": pdf("Livro") },
        {"item": "2", "descricao": "Quebrado", "nome": "c.pdf", "dados": b"nao e pdf"}])
    doc = pymupdf.open(stream=raw, filetype="pdf")
    txt = doc[2].get_text()
    checa("Dossiê: capa+sumário+2 PDFs e cabeçalho", len(doc) == 4 and "[Item 1.1]" in txt and "Página 3 de 4" in txt, f"{len(doc)} {txt[:80]!r}")

    # --- lote
    arqs = [("cert.pdf", pdf("CERTIFICADO Certificamos que Maria participou do I Congresso Brasileiro de Saude (COBRAS), realizado em Sao Luis - MA, "
                              "no período de 10 a 12 de março de 2024. Carga horária 20 horas.")),
            ("lixo.xyz", b"x"), ("../../etc/passwd.txt", b"nada de util aqui para classificar, apenas um texto qualquer curto")]
    zbytes = _zip({"pasta/dentro.pdf": pdf("Declaração de licença-maternidade de 01 de março de 2024 a 28 de agosto de 2024 concedida a servidora"), ".oculto.pdf": b"x"})
    arqs.append(("lote.zip", zbytes))
    aceitos, ign = expandir(arqs)
    nomes = [n for n, _ in aceitos]
    checa("Lote: expande ZIP, ignora tipo/ocultos e neutraliza caminho", "dentro.pdf" in nomes and "passwd.txt" in nomes
          and ".oculto.pdf" not in nomes and any(i["arquivo"] == "lixo.xyz" for i in ign), f"{nomes} {ign}")
    from server import process_extract
    res = processar_lote(arqs, "Maria Souza", process_extract)
    por = {l["arquivo"]: l for l in res["arquivos"]}
    checa("Lote: classifica certificado e licença", por["cert.pdf"].get("item") == "participacao_evento" and por["dentro.pdf"].get("item") == "licenca",
          str({k: v.get("item") for k, v in por.items()}))
    zout = zipfile.ZipFile(io.BytesIO(gerar_zip_organizado(arqs, res)))
    checa("Lote: ZIP organizado (pastas e LEIAME)", "LEIAME.txt" in zout.namelist() and any(n.startswith("2024/") or n.startswith("revisar/") for n in zout.namelist()),
          str(zout.namelist()))
    bomba = _zip({"a.txt": b"0" * (50 * 1024 * 1024)})
    _, ign2 = expandir([("bomba.zip", bomba)])
    checa("Lote: barra taxa de compressão suspeita", any("compress" in i["motivo"] for i in ign2), str(ign2))

    print(f"\nAcertos: {ok}/{ok + falhas}")
    return 1 if falhas else 0


def _zip(arquivos: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n, d in arquivos.items():
            z.writestr(n, d)
    return buf.getvalue()


if __name__ == "__main__":
    sys.exit(main())
