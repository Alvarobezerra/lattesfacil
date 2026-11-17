"""Leitor de XML conferido com a DTD oficial do Lattes (LMPLCurriculo.DTD): nomes de tags e de atributos de título/ano.
Os nomes abaixo vêm da DTD; o conteúdo é fictício. Uso: python tests/teste_lattes_xml_dtd.py"""
import pathlib
import sys

raiz = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))
from lattes_xml import ler_curriculo  # noqa: E402

falhas = []


def ok(cond, msg):
    print(("OK     " if cond else "FALHA  ") + msg)
    if not cond:
        falhas.append(msg)


XML = """<?xml version="1.0" encoding="ISO-8859-1"?>
<CURRICULO-VITAE SISTEMA-ORIGEM-XML="TESTE" NUMERO-IDENTIFICADOR="1" DATA-ATUALIZACAO="01012026" HORA-ATUALIZACAO="120000">
 <DADOS-GERAIS NOME-COMPLETO="Fulano de Tal">
  <FORMACAO-ACADEMICA-TITULACAO>
   <ENSINO-MEDIO-SEGUNDO-GRAU NOME-INSTITUICAO="Colegio Exemplo" ANO-DE-CONCLUSAO="2003"/>
   <CURSO-TECNICO-PROFISSIONALIZANTE NOME-CURSO="Tecnico em Quimica" ANO-DE-CONCLUSAO="2005"/>
  </FORMACAO-ACADEMICA-TITULACAO>
  <ATUACOES-PROFISSIONAIS>
   <ATUACAO-PROFISSIONAL NOME-INSTITUICAO="Universidade Exemplo">
    <VINCULOS ANO-INICIO="2010" ANO-FIM="2012"/>
    <ATIVIDADES-DE-ENSINO><ENSINO NOME-CURSO="Curso que nao deve virar o titulo" ANO-INICIO="2011"/></ATIVIDADES-DE-ENSINO>
   </ATUACAO-PROFISSIONAL>
  </ATUACOES-PROFISSIONAIS>
  <PREMIOS-TITULOS><PREMIO-TITULO NOME-DO-PREMIO-OU-TITULO="Premio Exemplo" ANO-DA-PREMIACAO="2019"/></PREMIOS-TITULOS>
 </DADOS-GERAIS>
 <PRODUCAO-BIBLIOGRAFICA>
  <TEXTOS-EM-JORNAIS-OU-REVISTAS>
   <TEXTO-EM-JORNAL-OU-REVISTA SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DO-TEXTO TITULO-DO-TEXTO="Texto de jornal" ANO-DO-TEXTO="2018"/></TEXTO-EM-JORNAL-OU-REVISTA>
  </TEXTOS-EM-JORNAIS-OU-REVISTAS>
 </PRODUCAO-BIBLIOGRAFICA>
 <PRODUCAO-TECNICA>
  <SOFTWARE SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DO-SOFTWARE TITULO-DO-SOFTWARE="Software Exemplo" ANO="2020"/></SOFTWARE>
  <PATENTE SEQUENCIA-PRODUCAO="2"><DADOS-BASICOS-DA-PATENTE TITULO="Patente Exemplo" ANO-DESENVOLVIMENTO="2015"/></PATENTE>
  <MARCA SEQUENCIA-PRODUCAO="3"><DADOS-BASICOS-DA-MARCA TITULO="Marca Exemplo" ANO-DESENVOLVIMENTO="2016"/></MARCA>
  <CULTIVAR-PROTEGIDA SEQUENCIA-PRODUCAO="4"><DADOS-BASICOS-DA-CULTIVAR DENOMINACAO="Cultivar Exemplo" ANO-SOLICITACAO="2014"/></CULTIVAR-PROTEGIDA>
  <PROCESSOS-OU-TECNICAS SEQUENCIA-PRODUCAO="5"><DADOS-BASICOS-DO-PROCESSOS-OU-TECNICAS TITULO-DO-PROCESSO="Processo Exemplo" ANO="2017"/></PROCESSOS-OU-TECNICAS>
  <TRABALHO-TECNICO SEQUENCIA-PRODUCAO="6"><DADOS-BASICOS-DO-TRABALHO-TECNICO TITULO-DO-TRABALHO-TECNICO="Trabalho Tecnico Exemplo" ANO="2019"/></TRABALHO-TECNICO>
  <DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
   <OUTRA-PRODUCAO-TECNICA SEQUENCIA-PRODUCAO="7">
    <DADOS-BASICOS-DE-OUTRA-PRODUCAO-TECNICA TITULO="Outra producao tecnica" ANO="2021"/>
    <REGISTRO-OU-PATENTE TITULO-PATENTE="Patente aninhada" DATA-PEDIDO-DE-DEPOSITO="15032022"/>
   </OUTRA-PRODUCAO-TECNICA>
   <MIDIA-SOCIAL-WEBSITE-BLOG SEQUENCIA-PRODUCAO="8"><DADOS-BASICOS-DE-MIDIA-SOCIAL-WEBSITE-BLOG TITULO="Blog Exemplo" ANO="2022"/></MIDIA-SOCIAL-WEBSITE-BLOG>
  </DEMAIS-TIPOS-DE-PRODUCAO-TECNICA>
 </PRODUCAO-TECNICA>
 <OUTRA-PRODUCAO>
  <PRODUCAO-ARTISTICA-CULTURAL>
   <COMPOSICAO-MUSICAL SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DA-COMPOSICAO-MUSICAL TITULO="Composicao Exemplo" ANO="2012"/></COMPOSICAO-MUSICAL>
   <CURSO-DE-CURTA-DURACAO SEQUENCIA-PRODUCAO="2"><DADOS-BASICOS-DO-CURSO-DE-CURTA-DURACAO TITULO="Oficina de arte" ANO="2013"/></CURSO-DE-CURTA-DURACAO>
  </PRODUCAO-ARTISTICA-CULTURAL>
  <DEMAIS-TRABALHOS SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DE-DEMAIS-TRABALHOS TITULO="Demais trabalhos exemplo" ANO="2011"/></DEMAIS-TRABALHOS>
 </OUTRA-PRODUCAO>
 <DADOS-COMPLEMENTARES>
  <FORMACAO-COMPLEMENTAR>
   <MBA NOME-CURSO="MBA Exemplo" ANO-DE-CONCLUSAO="2018"/>
  </FORMACAO-COMPLEMENTAR>
  <PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO>
   <PARTICIPACAO-EM-BANCA-DE-MESTRADO SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-MESTRADO TITULO="Banca de mestrado" ANO="2019"/></PARTICIPACAO-EM-BANCA-DE-MESTRADO>
   <OUTRAS-PARTICIPACOES-EM-BANCA SEQUENCIA-PRODUCAO="2"><DADOS-BASICOS-DE-OUTRAS-PARTICIPACOES-EM-BANCA TITULO="Outra banca" ANO="2020"/></OUTRAS-PARTICIPACOES-EM-BANCA>
  </PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO>
  <PARTICIPACAO-EM-BANCA-JULGADORA>
   <BANCA-JULGADORA-PARA-CONCURSO-PUBLICO SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DA-BANCA-JULGADORA-PARA-CONCURSO-PUBLICO TITULO="Concurso exemplo" ANO="2017"/></BANCA-JULGADORA-PARA-CONCURSO-PUBLICO>
   <OUTRAS-BANCAS-JULGADORAS SEQUENCIA-PRODUCAO="2"><DADOS-BASICOS-DE-OUTRAS-BANCAS-JULGADORAS TITULO="Outra julgadora" ANO="2018"/></OUTRAS-BANCAS-JULGADORAS>
  </PARTICIPACAO-EM-BANCA-JULGADORA>
  <ORIENTACOES-EM-ANDAMENTO>
   <OUTRAS-ORIENTACOES-EM-ANDAMENTO NOME-DO-ORIENTANDO="Orientando Exemplo" NOME-CURSO="Curso do orientando" ANO="2024"/>
  </ORIENTACOES-EM-ANDAMENTO>
 </DADOS-COMPLEMENTARES>
</CURRICULO-VITAE>"""

cur = ler_curriculo(XML.encode("iso-8859-1"))
por = {}
for i in cur["itens"]:
    por.setdefault(i["categoria"], []).append(i)
titulos = lambda c: sorted(i["titulo"] for i in por.get(c, []))  # noqa: E731

ok(titulos("banca") == ["Banca de mestrado", "Concurso exemplo", "Outra banca", "Outra julgadora"],
   f"bancas: o contêiner PARTICIPACAO-EM-BANCA-JULGADORA não engole as 2 bancas julgadoras ({titulos('banca')})")
ok(titulos("patente") == ["Patente Exemplo", "Patente aninhada"] and [i["ano"] for i in por["patente"] if i["titulo"] == "Patente aninhada"] == ["2022"],
   f"patente comum e patente aninhada em OUTRA-PRODUCAO-TECNICA (ano pela data do depósito) ({titulos('patente')})")
ok(titulos("outra_producao_tecnica") == ["Blog Exemplo", "Outra producao tecnica"], f"outra produção técnica sem absorver a patente aninhada ({titulos('outra_producao_tecnica')})")
ok(titulos("software") == ["Software Exemplo"] and titulos("texto_jornal") == ["Texto de jornal"] and titulos("trabalho_tecnico") == ["Trabalho Tecnico Exemplo"]
   and titulos("produto_tecnologico") == ["Processo Exemplo"], "títulos de software, texto em jornal, trabalho técnico e processo (atributos específicos)")
ok(titulos("registro_propriedade") == ["Cultivar Exemplo", "Marca Exemplo"], f"marca e cultivar ({titulos('registro_propriedade')})")
ok(por["premio"][0]["ano"] == "2019", "prêmio: ANO-DA-PREMIACAO")
ok(titulos("formacao_academica") == ["Colegio Exemplo", "Tecnico em Quimica"] and titulos("formacao_complementar") == ["MBA Exemplo"], "ensino médio, técnico e MBA")
ok(titulos("producao_artistica") == ["Composicao Exemplo"] and titulos("curso_ministrado") == ["Oficina de arte"],
   "o CURSO-DE-CURTA-DURACAO da produção artística é curso ministrado, não formação")
ok(titulos("demais_trabalhos") == ["Demais trabalhos exemplo"], "demais trabalhos")
ok(titulos("orientacao_andamento") == ["Curso do orientando"] and por["orientacao_andamento"][0]["ano"] == "2024", "outras orientações em andamento")
a = por["atuacao_profissional"][0]
ok(a["titulo"] == "Universidade Exemplo" and a["ano"] == "2010" and a["ano_fim"] == "2012",
   f"atuação: título é a instituição (não o curso de um sub-item) e o período vem de VINCULOS ({a['titulo']}, {a['ano']}-{a['ano_fim']})")
ok(cur["nao_classificados"] == {}, f"nada sem classificar ({cur['nao_classificados']})")

print(f"\n{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
