"""Snapshots do XML, comparação, dashboard e conciliação de envios. Uso: python tests/teste_curriculo_store.py"""
import pathlib
import sqlite3
import sys

raiz = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))
sys.path.insert(0, str(raiz / "tests"))
import curriculo_store as cs  # noqa: E402
from lattes_xml import ler_curriculo  # noqa: E402
from teste_novos_modulos import XML  # noqa: E402

falhas = []


def ok(cond, msg):
    print(("OK     " if cond else "FALHA  ") + msg)
    if not cond:
        falhas.append(msg)


conn = sqlite3.connect(":memory:")
conn.execute("""CREATE TABLE lattes_envios (id TEXT PRIMARY KEY, owner TEXT NOT NULL, titulo TEXT NOT NULL, tipo TEXT NOT NULL, ano TEXT,
    status TEXT NOT NULL, mensagem TEXT, lattes_seq TEXT, enviado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL, removido_em TEXT, oculto_em TEXT)""")
cs.criar_tabelas(conn)
ok(all(c in [r[1] for r in conn.execute("PRAGMA table_info(lattes_envios)")] for c in ("xml_status", "xml_verificado_em")), "migração cria colunas de conciliação")

xml1 = XML.encode("iso-8859-1")
cur1 = ler_curriculo(xml1)
ok(cur1["atualizacao_iso"].startswith("2026-01-01T03:00"), f"data de atualização em UTC ({cur1['atualizacao_iso']})")
s1, novo = cs.salvar(conn, cur1, cs.hash_arquivo(xml1))
s1b, novo_b = cs.salvar(conn, cur1, cs.hash_arquivo(xml1))
ok(novo and not novo_b and s1 == s1b, "mesmo XML não duplica o snapshot")
ok(cs.carregar(conn, s1)["itens"] == cur1["itens"], "snapshot volta idêntico")

# segunda versão: entra um artigo novo, sai o livro
xml2 = xml1.replace(b'TITULO-DO-LIVRO="Livro de testes"', b'TITULO-DO-LIVRO="Outro livro"').replace(
    b'</ARTIGOS-PUBLICADOS>',
    b'<ARTIGO-PUBLICADO><DADOS-BASICOS-DO-ARTIGO TITULO-DO-ARTIGO="Artigo recem incluido" ANO-DO-ARTIGO="2025" DOI=""/></ARTIGO-PUBLICADO></ARTIGOS-PUBLICADOS>')
cur2 = ler_curriculo(xml2)
s2, novo2 = cs.salvar(conn, cur2, cs.hash_arquivo(xml2))
ok(novo2 and cs.anterior(conn, s2) == s1, "snapshot anterior é encontrado")
c = cs.comparar(cur1, cur2)
ok([i["titulo"] for i in c["adicionados"]] == ["Artigo recem incluido", "Outro livro"] or
   {i["titulo"] for i in c["adicionados"]} == {"Artigo recem incluido", "Outro livro"}, f"adicionados: {[i['titulo'] for i in c['adicionados']]}")
ok([i["titulo"] for i in c["removidos"]] == ["Livro de testes"], f"removidos: {[i['titulo'] for i in c['removidos']]}")
ok(cs.comparar(cur1, cur1) == {"adicionados": [], "removidos": [], "total_antes": len(cur1["itens"]), "total_depois": len(cur1["itens"])}, "versões iguais não têm diferença")

d = cs.dashboard(cur2, 2026)
ok(d["artigos"]["total"] == 4 and d["artigos"]["sem_doi"] >= 2, f"dashboard: artigos {d['artigos']}")
ok(sum(a["total"] for a in d["por_ano"]) <= d["total_itens"] and d["por_categoria"]["artigo"] == 4, "dashboard: totais coerentes")
ok(all(a[0] != "João da Silva" for a in d["coautores_top"]), "dashboard: o próprio pesquisador não conta como coautor")

# conciliação: envio posterior ao XML não prova nada; anterior e presente confirma; removido e ausente confirma remoção
def envio(eid, titulo, status, enviado, ano="2025", removido=None):
    conn.execute("INSERT INTO lattes_envios (id, owner, titulo, tipo, ano, status, enviado_em, atualizado_em, removido_em) VALUES (?,?,?,?,?,?,?,?,?)",
                 (eid, "Joao da Silva", titulo, "artigo", ano, status, enviado, enviado, removido))


envio("a1", "Artigo recem incluido", "salvo", "2025-12-01T00:00:00+00:00")
envio("a2", "Artigo que nunca entrou", "salvo", "2025-12-01T00:00:00+00:00")
envio("a3", "Artigo enviado depois do XML", "salvo", "2026-06-01T00:00:00+00:00")
envio("a4", "Livro de testes", "removido", "2025-01-01T00:00:00+00:00", "2020", removido="2025-12-02T00:00:00+00:00")
envio("a5", "Outro livro", "removido", "2025-01-01T00:00:00+00:00", "2020", removido="2025-12-02T00:00:00+00:00")
conn.execute("INSERT INTO lattes_envios (id, owner, titulo, tipo, ano, status, enviado_em, atualizado_em) VALUES ('b1','Maria Souza','Artigo recem incluido','artigo','2025','salvo','2025-12-01','2025-12-01')")
res = cs.conciliar_envios(conn, cur2)
st = dict(conn.execute("SELECT id, xml_status FROM lattes_envios").fetchall())
ok(st["a1"] == "confirmado" and st["a2"] == "ausente" and st["a3"] == "xml_anterior", f"inclusões: {st}")
ok(st["a4"] == "remocao_confirmada" and st["a5"] == "ainda_presente", f"exclusões: {st}")
ok(st["b1"] is None, "envio de outro pesquisador não é tocado")

for i in range(cs.MANTER_POR_CURRICULO + 5):
    cs.salvar(conn, {**cur1, "itens": cur1["itens"][: 1 + i % 3], "nome": "João da Silva", "x": i}, f"h{i}")
ok(len(cs.listar(conn, cur1["id_lattes"])) == cs.MANTER_POR_CURRICULO, "retenção limita o número de versões")

# estrutura real do XML do Lattes (nomes de tags conferidos num currículo exportado; conteúdo fictício)
XML_REAL = """<?xml version="1.0" encoding="ISO-8859-1"?>
<CURRICULO-VITAE NUMERO-IDENTIFICADOR="1" DATA-ATUALIZACAO="05052023" HORA-ATUALIZACAO="172224">
 <DADOS-GERAIS NOME-COMPLETO="Fulano de Tal">
  <AREAS-DE-ATUACAO>
   <AREA-DE-ATUACAO NOME-GRANDE-AREA-DO-CONHECIMENTO="Ciencias da Saude" NOME-DA-AREA-DO-CONHECIMENTO="Farmacia" NOME-DA-ESPECIALIDADE="Farmacia Hospitalar"/>
   <AREA-DE-ATUACAO NOME-GRANDE-AREA-DO-CONHECIMENTO="Ciencias da Saude" NOME-DA-AREA-DO-CONHECIMENTO="Farmacia" NOME-DA-ESPECIALIDADE="Farmacologia"/>
  </AREAS-DE-ATUACAO>
 </DADOS-GERAIS>
 <DADOS-COMPLEMENTARES>
  <FORMACAO-COMPLEMENTAR>
   <FORMACAO-COMPLEMENTAR-CURSO-DE-CURTA-DURACAO NOME-CURSO="Curso A" ANO-DE-CONCLUSAO="2020"/>
   <OUTROS NOME-CURSO="Curso B" ANO-DE-CONCLUSAO="2021"/>
  </FORMACAO-COMPLEMENTAR>
  <INFORMACOES-ADICIONAIS-CURSOS><INFORMACAO-ADICIONAL-CURSO NOME-INSTITUICAO="UFX"/></INFORMACOES-ADICIONAIS-CURSOS>
  <PARTICIPACAO-EM-EVENTOS-CONGRESSOS>
   <PARTICIPACAO-EM-CONGRESSO SEQUENCIA-PRODUCAO="1"><DADOS-BASICOS-DA-PARTICIPACAO-EM-CONGRESSO TITULO="Congresso X" ANO="2019"/></PARTICIPACAO-EM-CONGRESSO>
   <PARTICIPACAO-EM-SEMINARIO SEQUENCIA-PRODUCAO="2"><DADOS-BASICOS-DA-PARTICIPACAO-EM-SEMINARIO TITULO="Seminario Y" ANO="2018"/></PARTICIPACAO-EM-SEMINARIO>
   <OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS SEQUENCIA-PRODUCAO="3"><DADOS-BASICOS-DE-OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS TITULO="Outro evento" ANO="2017"/></OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS>
  </PARTICIPACAO-EM-EVENTOS-CONGRESSOS>
 </DADOS-COMPLEMENTARES>
</CURRICULO-VITAE>"""
real = ler_curriculo(XML_REAL.encode("iso-8859-1"))
cats_real = [i["categoria"] for i in real["itens"]]
ok(sorted(i["titulo"] for i in real["itens"] if i["categoria"] == "participacao_evento") == ["Congresso X", "Outro evento", "Seminario Y"],
   f"cada participação em evento vira um item ({cats_real})")
ok(cats_real.count("formacao_complementar") == 2, "formação complementar real (curso de curta duração + OUTROS)")
ok(real["nao_classificados"] == {}, f"nada relevante fica sem classificar ({real['nao_classificados']})")
ok(len(real["perfil"]["areas"]) == 2 and "Farmacia Hospitalar" in real["perfil"]["areas"][0], f"áreas com especialidade ({real['perfil']['areas']})")
ok(real["atualizacao_iso"].startswith("2023-05-05T20:22:24"), "data e hora de atualização")

print(f"\n{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
