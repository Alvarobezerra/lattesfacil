"""Catálogo dos documentos SIMULADOS de comprovação (um ou mais por tipo de cadastro do Lattes).

As regras de criação estão em docs/regras-documentos-sinteticos.md — leia antes de acrescentar casos.

Cada caso é um dict:
  arquivo   nome do PDF (sem extensão) = "<id_do_item>" ou "<id_do_item>__<variacao>"
  item      id do item do Lattes que o documento comprova (itens/especificacao/<id>.json) ou id do classificador
  titulo    título impresso no topo
  corpo     texto do documento (parágrafos separados por linha em branco)
  classe    id que o classificador DEVE devolver em 1º lugar; None = o item ainda não tem regra no classificador
            (o teste apenas avisa), "escolher" = o classificador deve recusar-se a decidir (casos negativos)
  campos    {nome_do_campo_do_Lattes: trecho que o leitor deve extrair} — só para itens com leitor em itens/leitores.py
Tudo é FICTÍCIO: pessoas, instituições, números de registro, DOIs e ISBNs não existem.
"""
from __future__ import annotations

# Personagem fictícia usada em todos os documentos (é o "usuário" do teste).
import os

# O nome do pesquisador (o "usuário" do teste) aparece em TODOS os documentos. Ordem: --nome/LATTES_NOME,
# arquivo nome.local.txt (ignorado pelo git) e, por fim, a personagem fictícia. Para usar o seu nome:
#   python tests/teste_amostras_sinteticas.py --nome "Seu Nome Completo"      (ou variável LATTES_NOME)
_LOCAL = os.path.join(os.path.dirname(__file__), "nome.local.txt")  # fora do git: guarda o nome do usuário
PESQUISADORA = (os.environ.get("LATTES_NOME", "").strip()
                or (open(_LOCAL, encoding="utf-8").read().strip() if os.path.isfile(_LOCAL) else "")
                or "Helena Moraes Tavares")


def nome_em_citacoes(nome: str) -> str:
    """'Helena Moraes Tavares' -> 'TAVARES, H. M.'"""
    partes = [p for p in nome.split() if p.lower() not in ("da", "de", "do", "das", "dos", "e")]
    return f"{partes[-1].upper()}, " + " ".join(p[0].upper() + "." for p in partes[:-1]) if len(partes) > 1 else nome.upper()

INST = "Universidade Federal do Vale Exemplar"
SIGLA = "UFVE"

CASOS: list[dict] = [
    # ------------------------------------------------------------------ Eventos
    dict(arquivo="participacao_evento", item="participacao_evento", classe="participacao_evento",
         titulo="CERTIFICADO DE PARTICIPAÇÃO",
         corpo=f"Certificamos que {PESQUISADORA} participou do 12º Congresso Brasileiro de Ciências Exemplares, realizado em "
               "Belo Horizonte - MG, de 10 a 13 de setembro de 2025, na qualidade de ouvinte, com carga horária de 40 horas.\n\n"
               "Belo Horizonte, 13 de setembro de 2025.\nComissão Organizadora",
         campos={"f_nme_evento": "Congresso Brasileiro de Ciências Exemplares", "f_ano": "2025", "F_FORMA": "Ouvinte"}),
    dict(arquivo="organizacao_evento", item="organizacao_evento", classe="organizacao_evento",
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} integrou a comissão organizadora do Simpósio de Inovação em Saúde Exemplar, "
               "realizado em São Luís - MA, entre 4 e 6 de junho de 2024, atuando na coordenação científica.\n\n"
               "São Luís, 10 de junho de 2024.\nPró-Reitoria de Extensão",
         campos={"f_ano": "2024"}),
    dict(arquivo="curso_ministrado", item="curso_ministrado", classe="curso_ministrado",
         titulo="CERTIFICADO",
         corpo=f"Certificamos que {PESQUISADORA} ministrou o minicurso \"Introdução à Bioinformática Aplicada\", com carga horária "
               "de 8 horas, durante a Semana Acadêmica da Faculdade de Ciências Exemplares, em 18 de outubro de 2023, "
               "na modalidade presencial.\n\nCoordenação de Extensão",
         campos={"f_ano": "2023"}),
    dict(arquivo="formacao_complementar", item="formacao_complementar", classe="formacao_complementar",
         titulo="CERTIFICADO DE CONCLUSÃO",
         corpo=f"Certificamos que {PESQUISADORA} concluiu o curso de extensão \"Estatística com R para Pesquisa em Saúde\", "
               "oferecido pelo Instituto Exemplar de Educação Continuada, com carga horária de 60 horas, no período de "
               "03 de março de 2022 a 28 de abril de 2022.\n\nDiretoria de Ensino",
         campos={"f_curso": "Estatística com R", "f_carga": "60", "f_inst": "Instituto Exemplar de Educação Continuada"}),
    dict(arquivo="apresentacao", item="apresentacao", classe="apresentacao",
         titulo="CERTIFICADO DE APRESENTAÇÃO",
         corpo="Certificamos que o trabalho intitulado Atividade antioxidante de extratos vegetais do cerrado foi apresentado "
               "no 5º Encontro Regional de Química Exemplar (ERQE), realizado pela Universidade Federal do Vale Exemplar, "
               "no período de 19 a 21 de agosto de 2024, em Teresina - PI, apresentado por "
               f"{PESQUISADORA} e coautoria de Carlos Eduardo Pinheiro no formato pôster.\n\nComissão Científica",
         campos={"titulo": "Atividade antioxidante de extratos vegetais do cerrado", "nome_evento": "Encontro Regional de Química",
                 "cidade_evento": "Teresina - PI", "ano": "2024", "autores": PESQUISADORA}),
    dict(arquivo="apresentacao__autoria_no_titulo", item="apresentacao", classe="apresentacao",
         titulo="CERTIFICADO DE APRESENTAÇÃO",
         corpo="Certificamos que o trabalho científico intitulado \"Atividade antioxidante de extratos vegetais do cerrado\", "
               f"de autoria de {PESQUISADORA} e Carlos Eduardo Pinheiro, foi apresentado na modalidade pôster durante o "
               "Encontro Regional de Química Exemplar, em Teresina - PI, em 21 de agosto de 2024.\n\nComissão Científica",
         campos={"titulo": "Atividade antioxidante de extratos vegetais do cerrado", "autores": PESQUISADORA},
         lacuna="o leitor de certificados exige 'apresentado por <Nome> e coautoria de ...'; com 'de autoria de' o título engole os autores e a lista de autores sai vazia"),
    dict(arquivo="anais", item="anais", classe="anais",
         titulo="Efeito do extrato de babaçu sobre a viabilidade celular in vitro",
         corpo=f"{PESQUISADORA}¹, Carlos Eduardo Pinheiro¹\n¹ {INST}\n\n"
               "Resumo: Este trabalho avaliou o efeito do extrato hidroalcoólico de babaçu sobre a viabilidade de células "
               "em cultura. Introdução: o babaçu é amplamente utilizado na região. Metodologia: ensaio de MTT em 24 e 48 horas. "
               "Resultados: não houve citotoxicidade até 200 µg/mL.\n\n"
               "Palavras-chave: babaçu; viabilidade celular; extrato vegetal.\n\nAnais do Simpósio Exemplar de Iniciação Científica, 2024."),
    # ------------------------------------------------------------------ Produção bibliográfica
    dict(arquivo="artigo", item="artigo", classe="artigo",
         titulo="Probiotic beverages from babassu: formulation and stability",
         corpo=f"{PESQUISADORA}, Carlos Eduardo Pinheiro\n{INST}\n\n"
               "Journal of Exemplary Food Science, Volume 12, Issue 3, pp. 101-110, 2025. ISSN 0000-0000. "
               "DOI 10.9999/jefs.2025.0123\nReceived: 10 January 2025; Accepted: 02 March 2025; Published: 20 April 2025\n\n"
               "Abstract: We developed probiotic beverages based on babassu and evaluated their stability during 28 days of storage.\n"
               "Keywords: probiotics; babassu; beverages."),
    dict(arquivo="artigo_aceito", item="artigo_aceito", classe="artigo_aceito",
         titulo="Letter of acceptance",
         corpo=f"Dear Dr. {PESQUISADORA}, we are pleased to inform you that your manuscript \"Probiotic beverages from babassu\" "
               "has been accepted for publication in the Journal of Exemplary Food Science. DOI 10.9999/jefs.2025.0123. "
               "12 de maio de 2025\nThe Editors",
         campos={"f_cod_doi": "10.9999/jefs.2025.0123", "f_ano": "2025"}),
    dict(arquivo="livro_capitulo", item="livro_capitulo", classe="livro_capitulo",
         titulo="FICHA CATALOGRÁFICA",
         corpo="Fundamentos de Bioprocessos no Cerrado. Organizadores: Carlos Eduardo Pinheiro e Marta Lúcia Andrade.\n"
               f"Capítulo 4: Fermentação de matrizes vegetais, por {PESQUISADORA}, p. 85-112.\n"
               "Editora Exemplar, São Paulo, 2024. 1ª edição. ISBN 978-00-00000-00-0. 250 páginas."),
    dict(arquivo="outra_producao_bibliografica", item="outra_producao_bibliografica", classe=None,
         titulo="DECLARAÇÃO DE PUBLICAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} publicou a resenha \"Novas rotas de fermentação\" no Boletim Exemplar de Ciência, "
               "número 18, em 2024, com 4 páginas."),
    dict(arquivo="prefacio_posfacio", item="prefacio_posfacio", classe=None,
         titulo="CARTA DO ORGANIZADOR",
         corpo=f"Agradecemos a {PESQUISADORA} pela redação do prefácio do livro \"Ciência e Cerrado\", publicado pela Editora "
               "Exemplar em 2023, ISBN 978-00-00000-01-7."),
    dict(arquivo="texto_jornal_revista", item="texto_jornal_revista", classe=None,
         titulo="DECLARAÇÃO DA REDAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} publicou o artigo de divulgação \"O que são probióticos?\" no jornal Gazeta do "
               "Vale Exemplar, caderno Ciência, em 14 de julho de 2024, páginas 12-13."),
    dict(arquivo="traducao", item="traducao", classe=None,
         titulo="DECLARAÇÃO DE TRADUÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} traduziu do inglês para o português o livro \"Applied Food Microbiology\", "
               "publicado pela Editora Exemplar em 2022, 320 páginas."),
    dict(arquivo="editoracao", item="editoracao", classe=None,
         titulo="DECLARAÇÃO DE EDITORAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} atuou como editora do livro \"Anais do Simpósio Exemplar de Saúde\", Editora "
               "Exemplar, 2023, ISBN 978-00-00000-02-4."),
    # ------------------------------------------------------------------ Produção técnica
    dict(arquivo="relatorio_tecnico", item="relatorio_tecnico", classe="relatorio_tecnico",
         titulo="PARECER TÉCNICO",
         corpo="Parecer técnico sobre a viabilidade de produção de bebidas probióticas, elaborado em 4 de junho de 2023 "
               f"por {PESQUISADORA} como consultoria à Cooperativa Exemplar de Extrativistas.",
         campos={"F_COD_PROD": "Consultoria", "f_ano": "2023"}),
    dict(arquivo="trabalho_tecnico", item="trabalho_tecnico", classe=None,
         titulo="DECLARAÇÃO DE SERVIÇO TÉCNICO",
         corpo=f"Declaramos que {PESQUISADORA} realizou análise físico-química de amostras de água para a Cooperativa Exemplar, "
               "em 2023, com entrega de laudo de 6 páginas."),
    dict(arquivo="software_sem_registro", item="software_sem_registro", classe=None,
         titulo="DECLARAÇÃO DE DESENVOLVIMENTO",
         corpo=f"Declaramos que {PESQUISADORA} desenvolveu o aplicativo \"Agenda Exemplar\" (Python, 2024), de uso interno, "
               "sem registro em órgão competente."),
    dict(arquivo="produto", item="produto", classe=None,
         titulo="FICHA DE PRODUTO",
         corpo=f"Produto: bebida mista probiótica de babaçu. Desenvolvido por {PESQUISADORA}, 2024, finalidade: alimentação funcional."),
    dict(arquivo="processo_tecnica", item="processo_tecnica", classe=None,
         titulo="DESCRIÇÃO DE PROCESSO",
         corpo=f"Processo de extração aquosa a frio de amido de babaçu, desenvolvido por {PESQUISADORA} em 2023."),
    dict(arquivo="material_didatico", item="material_didatico", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} desenvolveu o material didático \"Apostila de Bioquímica Experimental\" para a "
               "disciplina de Bioquímica, em 2023, com 90 páginas."),
    dict(arquivo="extensao_tecnologica", item="extensao_tecnologica", classe=None,
         titulo="DECLARAÇÃO DE EXTENSÃO TECNOLÓGICA",
         corpo=f"Declaramos que {PESQUISADORA} prestou extensão tecnológica à Associação Exemplar de Produtores em 2024 "
               "(capacitação em boas práticas de fabricação)."),
    dict(arquivo="entrevista_midia", item="entrevista_midia", classe=None,
         titulo="DECLARAÇÃO DA EMISSORA",
         corpo=f"Declaramos que {PESQUISADORA} concedeu entrevista ao programa Manhã Exemplar, da Rádio Vale Exemplar, em "
               "9 de abril de 2024, sobre alimentos probióticos."),
    dict(arquivo="redes_sociais", item="redes_sociais", classe=None,
         titulo="CAPTURA DE PÁGINA",
         corpo=f"Blog \"Ciência no Cerrado\" mantido por {PESQUISADORA} desde 2021. Endereço: https://ciencia-cerrado.exemplo.invalid. "
               "Finalidade: divulgação científica."),
    dict(arquivo="relatorio_pesquisa", item="relatorio_pesquisa", classe=None,
         titulo="RELATÓRIO DE PESQUISA",
         corpo=f"Relatório final do projeto \"Probióticos de matrizes regionais\", autora {PESQUISADORA}, 2024, 35 páginas, "
               "financiamento da Fundação Exemplar de Amparo à Pesquisa."),
    dict(arquivo="outra_producao_tecnica", item="outra_producao_tecnica", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} elaborou o regimento do Laboratório Exemplar de Alimentos em 2022."),
    # ------------------------------------------------------------------ Produção artística
    dict(arquivo="artes_cenicas", item="artes_cenicas", classe=None,
         titulo="DECLARAÇÃO DO TEATRO",
         corpo=f"Declaramos que {PESQUISADORA} atuou como preparadora vocal no espetáculo \"Ecos do Cerrado\", Teatro Exemplar, 2023."),
    dict(arquivo="artes_visuais", item="artes_visuais", classe=None,
         titulo="CERTIFICADO DE EXPOSIÇÃO",
         corpo=f"A obra \"Raízes\" (fotografia, 2023) de {PESQUISADORA} integrou a exposição coletiva Olhares Exemplares, Galeria Exemplar, 2023."),
    dict(arquivo="musica", item="musica", classe=None,
         titulo="DECLARAÇÃO DE COMPOSIÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} compôs a canção \"Vento do Vale\" (2022), gravada no álbum Vale Exemplar."),
    dict(arquivo="partitura_musical", item="partitura_musical", classe=None,
         titulo="FICHA DA PARTITURA",
         corpo=f"Partitura \"Vento do Vale\", para violão e voz, de {PESQUISADORA}, 2022, 4 páginas, editora Exemplar Música."),
    dict(arquivo="cartas_mapas", item="cartas_mapas", classe=None,
         titulo="DECLARAÇÃO CARTOGRÁFICA",
         corpo=f"Declaramos que {PESQUISADORA} elaborou a carta temática de uso do solo do município de Vale Exemplar, escala 1:50.000, em 2023."),
    dict(arquivo="maquete", item="maquete", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} projetou a maquete do Campus Exemplar (escala 1:200), exposta em 2022."),
    dict(arquivo="manutencao_obra", item="manutencao_obra", classe=None,
         titulo="ATESTADO DE RESTAURO",
         corpo=f"Atestamos que {PESQUISADORA} participou da conservação do painel \"Memória do Vale\", acervo do Museu Exemplar, em 2023."),
    dict(arquivo="outra_producao_artistica", item="outra_producao_artistica", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} fez a curadoria da mostra Cerrado em Cena, Centro Cultural Exemplar, 2024."),
    # ------------------------------------------------------------------ Patentes e registros
    dict(arquivo="patente", item="patente", classe="patente",
         titulo="COMPROVANTE DE PEDIDO DE PATENTE",
         corpo="Instituto Nacional da Propriedade Industrial - INPI (documento fictício). Número do Processo: BR 10 2099 000001 0 "
               "Depositante Nome ou Razão Social: Universidade Federal do Vale Exemplar Tipo de Pessoa: Jurídica "
               "Tipo de pedido: Patente de Invenção (PI) "
               "Título da Invenção ou Modelo de Utilidade (54): Bebidas mistas probióticas à base de babaçu "
               "Resumo: Bebida mista probiótica formulada com extrato de babaçu e cultura lática. "
               f"Dados do Inventor Nome: {PESQUISADORA} CPF: 000.000.000-00 Nome: Carlos Eduardo Pinheiro CPF: 000.000.000-00 "
               "Data de depósito: 15/03/2099",
         campos={"f_cod_reg": "BR1020990000010", "f_tipo": "Patente de Invenção", "f_titulo": "Bebidas mistas probióticas"}),
    dict(arquivo="patente__carta", item="patente", classe="patente", titulo="CARTA PATENTE",
         corpo="Instituto Nacional da Propriedade Industrial - INPI (documento fictício). Patente de Invenção. "
               "Número do pedido: BR 10 2099 000002 0. Título: Bebidas mistas probióticas à base de babaçu. "
               f"Inventores: {PESQUISADORA}; Carlos Eduardo Pinheiro. Concessão em 15 de março de 2099.",
         campos={"f_cod_reg": "BR1020990000020", "f_tipo": "Patente de Invenção", "f_titulo": "Bebidas mistas probióticas"},
         lacuna="o leitor só lê o título no layout do comprovante de peticionamento do INPI, não em carta patente"),
    dict(arquivo="software_registro", item="software_registro", classe="software_registro",
         titulo="CERTIFICADO DE REGISTRO DE PROGRAMA DE COMPUTADOR",
         corpo="Processo BR 51 2099 000001 0. Título: Sistema Agenda Exemplar. Linguagem: Python; JavaScript. "
               f"Campo de aplicação: Educação. Autora: {PESQUISADORA}. 20 de novembro de 2099.",
         campos={"f_cod_reg": "BR 51 2099 000001 0", "f_plataforma": "Python; JavaScript", "f_dta_conc": "20/11/2099"},
         nao_traz=["Finalidade", "Qual o potencial de inovação?"]),
    dict(arquivo="desenho_industrial", item="desenho_industrial", classe=None,
         titulo="CERTIFICADO DE REGISTRO DE DESENHO INDUSTRIAL",
         corpo=f"Registro DI 99 2099 000001-0. Título: Embalagem tubular. Autora: {PESQUISADORA}. Concessão em 2099."),
    dict(arquivo="marca_registrada", item="marca_registrada", classe=None,
         titulo="CERTIFICADO DE REGISTRO DE MARCA",
         corpo=f"Registro de marca nº 999999999. Marca: BabaçuVida. Titular: {PESQUISADORA}. Concessão em 2099."),
    dict(arquivo="topografia_circuito", item="topografia_circuito", classe=None,
         titulo="CERTIFICADO DE REGISTRO DE TOPOGRAFIA DE CIRCUITO INTEGRADO",
         corpo=f"Registro BR 99 2099 000001-0. Titular: {PESQUISADORA}. Concessão em 2099."),
    dict(arquivo="cultivar_protegida", item="cultivar_protegida", classe=None,
         titulo="CERTIFICADO DE PROTEÇÃO DE CULTIVAR",
         corpo=f"Cultivar Exemplar-1 (feijão-caupi), obtentora {PESQUISADORA}, certificado de proteção nº 99999, 2099."),
    dict(arquivo="cultivar_registrada", item="cultivar_registrada", classe=None,
         titulo="CERTIFICADO DE REGISTRO DE CULTIVAR",
         corpo=f"Cultivar Exemplar-2 (milho), mantenedora {PESQUISADORA}, registro nº 99999 no Registro Nacional de Cultivares, 2099."),
    # ------------------------------------------------------------------ Bancas, orientações
    dict(arquivo="banca", item="banca", classe="banca",
         titulo="DECLARAÇÃO DE PARTICIPAÇÃO EM BANCA",
         corpo=f"Declaramos que {PESQUISADORA} participou como membro da banca examinadora da defesa de dissertação de mestrado "
               f"do mestrando Lucas Ferreira Andrade, do curso de Saúde e Tecnologia, com a dissertação intitulada \"Probióticos de matrizes regionais\", "
               f"no Programa de Pós-Graduação em Saúde e Tecnologia da {INST}, em 12 de dezembro de 2024.",
         campos={"f_ano": "2024", "f_nme_orient": "Lucas Ferreira Andrade", "F_COD_PROD": "Mestrado"}),
    dict(arquivo="banca__sem_cargo", item="banca", classe="banca",
         titulo="DECLARAÇÃO DE PARTICIPAÇÃO EM BANCA",
         corpo=f"Declaramos que {PESQUISADORA} participou como membro da banca examinadora da defesa de dissertação de mestrado "
               "de Lucas Ferreira Andrade, intitulada \"Probióticos de matrizes regionais\", em 12 de dezembro de 2024.",
         campos={"f_nme_orient": "Lucas Ferreira Andrade"},
         lacuna="o leitor só acha o candidato após 'mestrando/candidato/aluno'; 'dissertação de <Nome>' não é lido"),
    dict(arquivo="banca_comissao_julgadora", item="banca_comissao_julgadora", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} integrou a comissão julgadora do concurso público para professor adjunto de "
               f"Bioquímica da {INST}, em 2024."),
    dict(arquivo="orientacao_concluida", item="orientacao_concluida", classe="orientacao_concluida",
         titulo="DECLARAÇÃO DE ORIENTAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} orientou como orientadora principal o trabalho de conclusão de curso de "
               "Lucas Ferreira Andrade, do curso de Saúde e Tecnologia, intitulado \"Atividade antioxidante de extratos do cerrado\", "
               "defendido e aprovado em 2023."),
    dict(arquivo="orientacao_andamento", item="orientacao_andamento", classe="orientacao_andamento",
         titulo="DECLARAÇÃO DE ORIENTAÇÃO EM ANDAMENTO",
         corpo=f"Declaramos que {PESQUISADORA} orienta atualmente o aluno Pedro Henrique Lima em projeto de iniciação científica "
               "(PIBIC), em andamento, com vigência da bolsa de 08/2025 a 07/2026."),
    # ------------------------------------------------------------------ Atuação / Dados gerais / Formação
    dict(arquivo="atuacao_profissional", item="atuacao_profissional", classe="atuacao_profissional",
         titulo="DECLARAÇÃO DE VÍNCULO",
         corpo=f"Declaramos que {PESQUISADORA} é servidora pública efetiva da {INST}, exerce o cargo de Professor Associado, "
               "com regime de dedicação exclusiva, desde 10 de março de 2015.",
         campos={"f_inst": "Universidade Federal do Vale Exemplar", "f_vinc": "Servidor público", "f_regime": "Dedicação exclusiva", "f_ano_ini": "2015"}),
    dict(arquivo="revisor_periodico", item="revisor_periodico", classe="revisor_periodico",
         titulo="CERTIFICADO",
         corpo=f"Certificamos que {PESQUISADORA} atuou como revisora ad hoc da Revista Exemplar de Saúde, no período de 03/2022 a "
               "05/2023, avaliando manuscritos submetidos ao periódico.",
         campos={"f_nme_agencia": "Exemplar de Saúde", "f_ano_ini": "2022", "f_mes_ini": "03", "f_ano_fim": "2023"}),
    dict(arquivo="revisor_projeto_fomento", item="revisor_projeto_fomento", classe=None,
         titulo="DECLARAÇÃO DA AGÊNCIA",
         corpo=f"Declaramos que {PESQUISADORA} emitiu parecer ad hoc em projetos do edital Universal da Fundação Exemplar de Amparo "
               "à Pesquisa em 2024."),
    dict(arquivo="corpo_editorial", item="corpo_editorial", classe="corpo_editorial",
         titulo="PORTARIA",
         corpo=f"Designa {PESQUISADORA} como Editora Associada da Revista Exemplar de Ciências Médicas desde 2021, integrando o corpo editorial.",
         campos={"f_nme_agencia": "Exemplar de Ciências Médicas", "f_ano_ini": "2021"}),
    dict(arquivo="comite_assessoramento", item="comite_assessoramento", classe=None,
         titulo="PORTARIA",
         corpo=f"Nomeia {PESQUISADORA} para o Comitê de Assessoramento de Saúde da Fundação Exemplar de Amparo à Pesquisa, "
               "biênio 2024-2025."),
    dict(arquivo="premio", item="premio", classe="premio",
         titulo="MENÇÃO HONROSA",
         corpo=f"Conferimos a {PESQUISADORA} menção honrosa pelo melhor trabalho na área de Ciências da Saúde, no Congresso "
               "Exemplar de Pós-Graduação, realizado em Teresina - PI, em 20 de outubro de 2023.",
         campos={"f_titulo": "Menção honrosa", "f_ano": "2023"}),
    dict(arquivo="premio__so_ano", item="premio", classe="premio", titulo="MENÇÃO HONROSA",
         corpo=f"Conferimos a {PESQUISADORA} menção honrosa pelo melhor trabalho na área de Ciências da Saúde, no Congresso "
               "Exemplar de Pós-Graduação, em 2023.",
         campos={"f_ano": "2023"}, lacuna="o ano só é lido quando o documento traz a data completa ('20 de outubro de 2023')"),
    dict(arquivo="projeto", item="projeto", classe="projeto",
         titulo="DECLARAÇÃO DE PARTICIPAÇÃO EM PROJETO",
         corpo="Declaramos que foi aprovado o projeto de extensão intitulado \"Ciência na Rede\", coordenado pela Professora "
               f"{PESQUISADORA}, do Departamento de Ciências Exemplares, vinculado ao Centro de Ciências da Saúde, da {INST}, "
               "financiado por edital da Fundação Exemplar de Amparo à Pesquisa. Vigência a partir de 02 de maio de 2023.",
         campos={"f_titulo": "Ciência na Rede", "F_TPO_NATUREZA": "Extensão", "F_ANO_INIC": "2023", "f_inst": "Universidade Federal do Vale Exemplar"},
         nao_traz=["Ano fim"]),
    dict(arquivo="projeto__sem_intitulado", item="projeto", classe="projeto", titulo="DECLARAÇÃO DE PARTICIPAÇÃO EM PROJETO",
         corpo=f"Declaramos que {PESQUISADORA} é coordenadora do projeto de extensão \"Ciência na Rede\", da {INST}, "
               "financiado por edital da Fundação Exemplar de Amparo à Pesquisa, no período de 2023 a 2025.",
         campos={"f_titulo": "Ciência na Rede"}, lacuna="o leitor exige 'intitulado <título>, coordenado pel...'; título solto entre aspas não é lido"),
    dict(arquivo="idioma", item="idioma", classe="idioma",
         titulo="CERTIFICADO DE PROFICIÊNCIA EM LÍNGUA INGLESA",
         corpo=f"{PESQUISADORA} obteve nível B2 (CEFR) no exame Cambridge English: First, realizado em 2022.",
         campos={"F_COD_IDIOMA": "Inglês"}),
    dict(arquivo="licenca", item="licenca", classe="licenca",
         titulo="PORTARIA",
         corpo=f"Concede licença-maternidade à servidora {PESQUISADORA}, de 01 de março de 2024 a 28 de agosto de 2024, por 180 dias.",
         campos={"f_tipo_licenca": "Maternidade", "f_dta_inicio": "01/03/2024", "f_dta_fim": "28/08/2024"}),
    dict(arquivo="formacao_academica", item="formacao_academica", classe="formacao_academica",
         titulo="DIPLOMA",
         corpo=f"A {INST}, no uso de suas atribuições, conferiu o grau de Doutora em Ciências da Saúde a {PESQUISADORA}, "
               "após colação de grau realizada em 15 de dezembro de 2018."),
    dict(arquivo="pos_doutorado", item="pos_doutorado", classe=None,
         titulo="DECLARAÇÃO DE PÓS-DOUTORADO",
         corpo=f"Declaramos que {PESQUISADORA} realizou estágio de pós-doutorado no Instituto Exemplar de Pesquisa, de 03/2020 a 02/2021, "
               "com bolsa da Fundação Exemplar."),
    dict(arquivo="identificacao", item="identificacao", classe=None,
         titulo="FICHA CADASTRAL INSTITUCIONAL",
         corpo=f"Nome: {PESQUISADORA}. Nome em citações bibliográficas: {nome_em_citacoes(PESQUISADORA)} Nacionalidade: brasileira. "
               "Lotação: Departamento de Ciências Exemplares."),
    dict(arquivo="endereco", item="endereco", classe=None,
         titulo="COMPROVANTE DE ENDEREÇO PROFISSIONAL",
         corpo=f"Pesquisadora: {PESQUISADORA}. Endereço profissional: {INST}, Departamento de Ciências Exemplares, Avenida das Palmeiras, 1000, Vale Exemplar - MA, CEP 00000-000, "
               "telefone (00) 0000-0000."),
    dict(arquivo="texto_inicial", item="texto_inicial", classe=None,
         titulo="RESUMO DO CURRÍCULO",
         corpo=f"{PESQUISADORA} é professora e pesquisadora em ciências da saúde, com foco em alimentos funcionais e probióticos."),
    dict(arquivo="outras_informacoes", item="outras_informacoes", classe=None,
         titulo="DECLARAÇÃO",
         corpo=f"Declaramos que {PESQUISADORA} coordenou ações de acolhimento de estudantes ingressantes em 2024 (informação relevante complementar)."),
    # ------------------------------------------------------------------ Citações
    dict(arquivo="citacao_scopus", item="citacao_scopus", classe=None,
         titulo="PERFIL DE AUTOR - SCOPUS",
         corpo=f"Autor: {PESQUISADORA}. Total de citações: 120. Índice h: 6. Documentos: 14. Consulta em 17/11/2026."),
    dict(arquivo="citacao_web_of_science", item="citacao_web_of_science", classe=None,
         titulo="RESEARCHER PROFILE - WEB OF SCIENCE",
         corpo=f"Author: {PESQUISADORA}. Times cited: 98. h-index: 5. Publications: 11. Accessed 17/11/2026."),
    dict(arquivo="citacao_google_scholar", item="citacao_google_scholar", classe=None,
         titulo="GOOGLE ACADÊMICO - PERFIL",
         corpo=f"{PESQUISADORA}. Citações: 210. Índice h: 8. Índice i10: 7. Consulta em 17/11/2026."),
    dict(arquivo="citacao_scielo", item="citacao_scielo", classe=None,
         titulo="SCIELO - CITAÇÕES",
         corpo=f"Autora: {PESQUISADORA}. Citações recebidas: 31. Documentos: 6. Consulta em 17/11/2026."),
    dict(arquivo="citacao_outra_base", item="citacao_outra_base", classe=None,
         titulo="BASE BIBLIOGRÁFICA EXEMPLAR - CITAÇÕES",
         corpo=f"Autora: {PESQUISADORA}. Citações: 17. Base: Biblioteca Digital Exemplar. Consulta em 17/11/2026."),
]

# Casos negativos: o classificador NÃO deve inventar um item.
NEGATIVOS: list[dict] = [
    dict(arquivo="negativo_irrelevante", item=None, classe="escolher", titulo="RECEITA DE BOLO",
         corpo="Misture dois ovos, uma xícara de açúcar e uma de farinha. Asse por quarenta minutos em forno médio."),
    dict(arquivo="negativo_sem_texto", item=None, classe="escolher", titulo="", corpo="", sem_texto=True),
]
