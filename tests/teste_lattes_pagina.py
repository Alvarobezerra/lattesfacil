"""Interpretador da página para impressão do Lattes (leitura em tempo real). Uso: python tests/teste_lattes_pagina.py
A página abaixo é FICTÍCIA, mas imita a estrutura observada numa página real: âncoras de seção, subtítulos de grupo e linhas td.ano + td.texto."""
import pathlib
import sys

raiz = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))
from lattes_pagina import ler_pagina  # noqa: E402

falhas = []


def ok(cond, msg):
    print(("OK     " if cond else "FALHA  ") + msg)
    if not cond:
        falhas.append(msg)


def linha(ano, texto):
    return f'<table class="IndicProdTabela"><tbody><tr><td class="ano">{ano}</td><td class="texto">{texto}</td></tr></tbody></table>'


HTML = f"""<html><head><meta charset="iso-8859-1"><title>Currículo Lattes</title></head><body>
<div class="header">Última atualização do currículo em 17/11/2026 · lattes.cnpq.br/0123456789012345</div>
<div class="subtitMenu">Produção Bibliográfica</div><div class="subtitMenu">Produção artística/cultural</div><table class="IndicProdTabela"><tr><td class="campos">Nome</td><td class="texto">Fulano de Tal Secreto</td></tr><tr><td class="campos">Nascimento</td><td class="texto">01/01/1980 - Cidade/UF - Brasil</td></tr></table>
<div class="conteudo-cv"><a name="DadosPessoais"></a><em>Dados pessoais</em></div>
<div class="conteudo-cv"><a name="Idiomas"></a><table class="IndicProdTabela"><tr><td class="campos">Inglês</td><td class="texto">Compreende Bem , Fala Razoavelmente</td></tr></table></div>
<div class="conteudo-cv"><a name="Premiosetitulos"></a>{linha('2019', 'PRÊMIO JÚLIA LIMA, Hospital Exemplo')}</div>
<div class="conteudo-cv"><a name="Formacaoacademica/Titulacao"></a>{linha('2020 - 2021', 'Especialização em Ciências da Melhoria. INSTITUTO EXEMPLO, Estados Unidos')}</div>
<div class="conteudo-cv"><a name="FormacaoComplementar"></a>{linha('2015', 'Curso de curta duração em Saúde Baseada em Evidência. (Carga horária: 120h).Hospital Exemplo')}</div>
<div class="conteudo-cv"><a name="Atuacaoprofissional"></a>{linha('2013 - 2014', 'Vínculo: Celetista , Enquadramento funcional: FARMACÊUTICO')}</div>
<div class="conteudo-cv"><a name="Areasdeatuacao"></a>{linha('1.', 'Grande área: Ciências da Saúde / Área: Farmácia')}</div>
<div class="conteudo-cv"><a name="Trabalhoseventos"></a><div class="agrupadorsub">Trabalhos publicados em anais de eventos (resumo)</div>
 {linha('1.', 'SANTOS, A. A. B.; LIMA, S. G. S.. Potencial do mesocarpo como inibidor da peroxidação In: XXXVI Seminário de Iniciação Científica, 2014, São Luís. <a href="https://doi.org/10.1000/xyz123">doi</a>')}
 {linha('2.', 'SANTOS, A. A. B.. Outro trabalho sem evento, 2015.')}</div>
<div class="conteudo-cv"><a name="ApresentacaoTrabalho"></a><div class="agrupadorsub">Apresentação de trabalho e palestra</div>
 {linha('1.', 'SANTOS, A. A. B.; REIS, A. S.. Atividade antioxidante do extrato, 2016. (Congresso,Apresentação de Trabalho)')}</div>
<div class="conteudo-cv"><a name="Participacaoemeventos"></a><div class="agrupadorsub">Participação em eventos</div>
 {linha('1.', 'Congresso Norte Nordeste de Nutrição Parenteral, 2014. (Congresso) .')}
 {linha('2.', 'Seminário de Farmácia, 2018. (Seminário) .')}</div>
<div class="conteudo-cv"><a name="softwarecompatente"></a><div class="agrupadorsub">Programa de computador</div>
 {linha('1.', 'Sistema Exemplo - Nutrição, 2020, Brasil. Instituição de Registro: INPI')}</div>
<div class="conteudo-cv"><a name="topografiadeci"></a><div class="agrupadorsub">Programa de computador</div>
 {linha('1.', 'Sistema Exemplo - Nutrição, 2020, Brasil. Instituição de Registro: INPI')}</div>
<div class="conteudo-cv"><a name="ApresentacaoTrabalhoPOP"></a><div class="agrupadorsub">Apresentação de trabalho e palestra</div>
 {linha('1.', 'SANTOS, A. A. B.. Palestra repetida da popularização, 2013. (Outra,Apresentação de Trabalho)')}</div>
<div class="conteudo-cv"><a name="ProjetoExtensao"></a>{linha('2014 - Atual', 'Projeto de extensão exemplo')}{linha('', 'Descrição: detalhe do projeto. Situação: Em andamento')}</div>
<div class="conteudo-cv"><a name="Producaoartistica"></a><div class="agrupadorsub">Produção artística/cultural</div>{linha('1.', 'Obra Exemplo, 2021. (Artes visuais)')}</div>
<div class="conteudo-cv"><a name="SecaoNovaDoFuturo"></a><div class="agrupadorsub">Grupo que o leitor não conhece</div>{linha('1.', 'Algo novo, 2024.')}</div>
</body></html>"""

cur = ler_pagina(HTML, "Fulano de Tal")
por = {}
for i in cur["itens"]:
    por.setdefault(i["categoria"], []).append(i)

ok(cur["fonte"] == "pagina" and cur["nome"] == "Fulano de Tal", "fonte e nome")
ok(cur["id_lattes"] == "0123456789012345" and cur["atualizacao"] == "17112026", f"id e data da página ({cur['id_lattes']}, {cur['atualizacao']})")
ok(len(por.get("trabalho_evento", [])) == 2, "trabalhos em eventos")
t = por["trabalho_evento"][0]
ok(t["titulo"] == "Potencial do mesocarpo como inibidor da peroxidação" and t["ano"] == "2014" and t["veiculo"].startswith("XXXVI Seminário")
   and t["autores"] == ["SANTOS, A. A. B.", "LIMA, S. G. S."] and t["doi"] == "10.1000/xyz123", f"autores, título, veículo, ano e DOI ({t})")
ok(por["trabalho_evento"][1]["titulo"] == "Outro trabalho sem evento" and por["trabalho_evento"][1]["ano"] == "2015", "trabalho sem 'In:'")
ok([i["titulo"] for i in por["participacao_evento"]] == ["Congresso Norte Nordeste de Nutrição Parenteral", "Seminário de Farmácia"]
   and por["participacao_evento"][0]["ano"] == "2014", "participações em eventos (sem autores)")
ok(len(por.get("apresentacao", [])) == 1, "seção 'popularização' não duplica apresentações")
ok(len(por.get("software", [])) == 1, "item repetido sob âncora velha vira um só")
f = por["formacao_academica"][0]
ok(f["titulo"] == "Especialização em Ciências da Melhoria" and f["ano"] == "2020" and f["ano_fim"] == "2021", f"formação com período ({f['titulo']}, {f['ano']}-{f['ano_fim']})")
ok(por["premio"][0]["titulo"] == "PRÊMIO JÚLIA LIMA" and por["premio"][0]["ano"] == "2019", "prêmio")
ok(por["formacao_complementar"][0]["ano"] == "2015" and por["atuacao_profissional"][0]["ano_fim"] == "2014", "formação complementar e atuação")
ok(cur["perfil"]["areas"] == ["Ciências da Saúde › Farmácia"] and cur["perfil"]["idiomas"] == ["Inglês"], f"perfil ({cur['perfil']})")
ok(len(por.get("projeto", [])) == 1 and por["projeto"][0]["titulo"] == "Projeto de extensão exemplo", "linha de detalhe de projeto não vira item")
ok(len(por.get("producao_artistica", [])) == 1, "produção artística/cultural")
ok(not any("Secreto" in i["titulo"] or "1980" in i["titulo"] for i in cur["itens"]), "cabeçalho de identificação (dado pessoal) não vira item")
ok(cur["nao_classificados"] == {"SecaoNovaDoFuturo | Grupo que o leitor não conhece": 1}, f"o que não é reconhecido aparece em 'não classificados' ({cur['nao_classificados']})")
ok(cur["atualizacao_iso"].endswith("+00:00") and cur["atualizacao_iso"][:4].isdigit(), "instante da leitura")

# a página REAL é HTML 4 com tags de fechamento omitidas (sem </td> nem </tr>), em maiúsculas
HTML4 = ("<!DOCTYPE HTML><html><body>Última atualização do currículo em 17/11/2026"
         '<A NAME="Premiosetitulos"></A><BR><div class="conteudo-cv"><em>Prêmios</em><TABLE class="IndicProdTabela"><TR><TD width="20%" class="ano">2019<TD class="texto">PRÊMIO EXEMPLO, Hospital X<BR></TABLE></table>'
         '<A NAME="Participacaoemeventos"></A><div class="conteudo-cv"><div class="agrupadorsub">Participação em eventos</div>'
         '<TABLE class="IndicProdTabela"><TR><TD class="ano">1.<TD class="texto">Congresso A, 2014. (Congresso) .<BR>'
         '<TR><TD class="ano">2.<TD class="texto">Seminário B, 2018. (Seminário) .<BR></TABLE></table>'
         '<A NAME="Trabalhoseventos"></A><div class="conteudo-cv"><div class="agrupadorsub">Trabalhos publicados em anais de eventos (resumo)</div>'
         '<TABLE class="IndicProdTabela"><TR><TD class="ano">1.<TD class="texto">SANTOS, A. A. B.. Título do trabalho In: Evento Z, 2020, Cidade. <A href="https://doi.org/10.1000/abc">x</A><BR></TABLE>'
         "</body></html>")
c4 = ler_pagina(HTML4, "Fulano")
cats4 = [(i["categoria"], i["titulo"], i["ano"]) for i in c4["itens"]]
ok(("premio", "PRÊMIO EXEMPLO", "2019") in cats4, f"HTML 4 sem fechamento: prêmio ({cats4})")
ok([x for x in cats4 if x[0] == "participacao_evento"] == [("participacao_evento", "Congresso A", "2014"), ("participacao_evento", "Seminário B", "2018")], "HTML 4 sem fechamento: linhas seguidas viram itens separados")
ok(any(i["categoria"] == "trabalho_evento" and i["doi"] == "10.1000/abc" and i["autores"] == ["SANTOS, A. A. B."] for i in c4["itens"]), "HTML 4 sem fechamento: autores e DOI")

# célula sem fechamento seguida de âncora de seção: a âncora não pode ser engolida pela célula (o projeto tem de continuar sendo 'projeto')
HTML5 = ("<!DOCTYPE HTML><html><body>Última atualização do currículo em 17/11/2026"
         '<A NAME="Atuacaoprofissional"></A><div class="conteudo-cv"><TABLE class="IndicProdTabela"><TR><TD class="campos">Rótulo<TD class="texto">Vínculo: Celetista, 2013 - 2014'
         '<A NAME="ProjetoExtensao"></A><div class="conteudo-cv"><TABLE class="IndicProdTabela"><TR><TD class="ano">2014 - Atual<TD class="texto">Projeto Y de extensão<BR></TABLE>'
         "</body></html>")
c5 = ler_pagina(HTML5, "Fulano")
ok(any(i["categoria"] == "projeto" and i["titulo"] == "Projeto Y de extensão" for i in c5["itens"]), f"âncora de seção encerra a célula aberta ({[(i['categoria'], i['titulo']) for i in c5['itens']]})")

for ruim in ("<html>nada</html>", ""):
    try:
        ler_pagina(ruim)
        ok(False, "HTML que não é a página do Lattes deve ser recusado")
    except ValueError:
        ok(True, f"recusa HTML que não é a página do Lattes ({ruim[:12]!r})")

print(f"\n{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
