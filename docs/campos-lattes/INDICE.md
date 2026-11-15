# Mapeamento dos formulários do Currículo Lattes (v2: por aba, listas completas e obrigatórios)

Mapeado em 15/11/2026 no Lattes real, **somente leitura** (nada foi salvo). Cada arquivo lista os campos **por aba**,
com nome técnico, tipo, limite, opções completas de cada lista e campos obrigatórios (mensagens do botão Salvar).
Listas grandes (países, idiomas) estão em `catalogos/`. O código do currículo aparece como `<codigo_do_cv>`.


## Dados gerais

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Endereço | único | Residencial, Profissional, Eletrônico | 38 | 9 | tela única | [endereco.json](dados-gerais/endereco.json) |
| Identificação | único | Foto de perfil, Nome civil, Nome social, Dados pessoais, Dados do nasc | 30 | 11 | tela única | [identificacao.json](dados-gerais/identificacao.json) |
| Idiomas | único | Idioma, Visibilidade | 10 | 1 | URL direta | [idiomas.json](dados-gerais/idiomas.json) |
| Licença Maternidade, Paternidade e Adoção | único | Licença, Visibilidade | 5 | 0 | URL direta | [licenca-maternidade-paternidade-e-adocao.json](dados-gerais/licenca-maternidade-paternidade-e-adocao.json) |
| Outras informações relevantes | único | (sem aba) | 1 | 0 | tela única | [outras-informacoes-relevantes.json](dados-gerais/outras-informacoes-relevantes.json) |
| Prêmios e títulos | único | Prêmios e títulos honoríficos recebidos, Visibilidade | 4 | 2 | URL direta | [premios-e-titulos.json](dados-gerais/premios-e-titulos.json) |
| Texto inicial do Currículo Lattes | único | Texto inicial, Tradução | 2 | 0 | tela única | [texto-inicial-do-curriculo-lattes.json](dados-gerais/texto-inicial-do-curriculo-lattes.json) |

## Formação

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Formação acadêmica/titulação | Doutorado, Mestrado, Mestrado Profissional, Especialização,  | Dados Gerais, Período, Bolsa, Detalhamento, Visibilidade | 22, 22, 22, 11, 9, 19, 8, 5, 5 | 7, 7, 7, 7, 7, 7, 7, | janela (selecionarNivel) | [formacao-academica-titulacao.json](formacao/formacao-academica-titulacao.json) |
| Formação complementar | único | Dados gerais | 5 | 4 | URL direta | [formacao-complementar.json](formacao/formacao-complementar.json) |
| Pós-doutorado e/ou livre-docência | Pós-Doutorado, Livre Docência | Dados Gerais, Período, Bolsa, Visibilidade | 7, 5 | 7, 7 | janela (selecionarNivel) | [pos-doutorado-e-ou-livre-docencia.json](formacao/pos-doutorado-e-ou-livre-docencia.json) |

## Atuação

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Atuação profissional | único | Instituição, Vínculo, Período, Outras informações, Visibilidade | 13 | 6 | URL direta | [atuacao-profissional.json](atuacao/atuacao-profissional.json) |
| Linhas de pesquisa | — | — | — | — | tela única | [linhas-de-pesquisa.json](atuacao/linhas-de-pesquisa.json) |
| Membro de comitê de assessoramento | único | Agência de fomento, Comitê, Período, Outras informações, Visibilidade | 9 | 4 | URL direta | [membro-de-comite-de-assessoramento.json](atuacao/membro-de-comite-de-assessoramento.json) |
| Membro de corpo editorial | único | Periódico, Período, Outras informações, Visibilidade | 8 | 3 | URL direta | [membro-de-corpo-editorial.json](atuacao/membro-de-corpo-editorial.json) |
| Revisor de periódico | único | Periódico, Período, Outras informações, Visibilidade | 8 | 3 | URL direta | [revisor-de-periodico.json](atuacao/revisor-de-periodico.json) |
| Revisor de projeto de agência de fomento | único | Agência de fomento, Período, Outras informações, Visibilidade | 8 | 3 | URL direta | [revisor-de-projeto-de-agencia-de-fomento.json](atuacao/revisor-de-projeto-de-agencia-de-fomento.json) |
| Áreas de atuação | único |  | 0 | 0 | tela única | [areas-de-atuacao.json](atuacao/areas-de-atuacao.json) |

## Projetos

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Outros tipos de projetos | único | Dados gerais, Equipe, Traduções, Visibilidade, Instituições, Informe o | 34 | 12 | URL direta | [outros-tipos-de-projetos.json](projetos/outros-tipos-de-projetos.json) |
| Projeto de desenvolvimento tecnológico | único | Dados gerais, Equipe, Traduções, Visibilidade, Instituições, Informe o | 35 | 12 | URL direta | [projeto-de-desenvolvimento-tecnologico.json](projetos/projeto-de-desenvolvimento-tecnologico.json) |
| Projeto de ensino | único | Dados gerais, Equipe, Traduções, Visibilidade, Instituições, Informe o | 36 | 13 | URL direta | [projeto-de-ensino.json](projetos/projeto-de-ensino.json) |
| Projeto de extensão | único | Dados gerais, Equipe, Traduções, Visibilidade, Instituições, Informe o | 34 | 12 | URL direta | [projeto-de-extensao.json](projetos/projeto-de-extensao.json) |
| Projetos de pesquisa | único | Dados gerais, Equipe, Traduções, Visibilidade, Instituições, Informe o | 34 | 12 | URL direta | [projetos-de-pesquisa.json](projetos/projetos-de-pesquisa.json) |

## Produções

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Apresentação de trabalho e palestra | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 4 | URL direta | [apresentacao-de-trabalho-e-palestra.json](producoes/apresentacao-de-trabalho-e-palestra.json) |
| Artes cênicas | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 30 | 11 | URL direta | [artes-cenicas.json](producoes/artes-cenicas.json) |
| Artes visuais | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 24 | 11 | URL direta | [artes-visuais.json](producoes/artes-visuais.json) |
| Artigos aceitos para publicação | único | D.O.I, Dados gerais, Detalhamento, Outras informações, Traduções, Visi | 15 | 4 | URL direta | [artigos-aceitos-para-publicacao.json](producoes/artigos-aceitos-para-publicacao.json) |
| Artigos completos publicados em periódicos | aberto pela janela do DOI | D.O.I, Dados gerais, Detalhamento, Outras informações, Traduções, Visi | 21 | 6 | janela (informaDOI) | [artigos-completos-publicados-em-periodicos.json](producoes/artigos-completos-publicados-em-periodicos.json) |
| Assessoria e consultoria | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 20 | 4 | URL direta | [assessoria-e-consultoria.json](producoes/assessoria-e-consultoria.json) |
| Cartas, mapas ou similares | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 4 | URL direta | [cartas-mapas-ou-similares.json](producoes/cartas-mapas-ou-similares.json) |
| Curso de curta duração ministrado | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 20 | 4 | URL direta | [curso-de-curta-duracao-ministrado.json](producoes/curso-de-curta-duracao-ministrado.json) |
| Desenvolvimento de material didático ou instrucional | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 16 | 4 | URL direta | [desenvolvimento-de-material-didatico-ou-instrucional.json](producoes/desenvolvimento-de-material-didatico-ou-instrucional.json) |
| Editoração | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 18 | 5 | URL direta | [editoracao.json](producoes/editoracao.json) |
| Entrevistas, mesas redondas, programas e comentários na mídia | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 4 | URL direta | [entrevistas-mesas-redondas-programas-e-comentarios-na-midia.json](producoes/entrevistas-mesas-redondas-programas-e-comentarios-na-midia.json) |
| Extensão tecnológica | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 4 | URL direta | [extensao-tecnologica.json](producoes/extensao-tecnologica.json) |
| Livros e capítulos | Livro, Capitulo | D.O.I, Dados gerais, Detalhamento, Outras informações, Traduções, Visi | 24, 25 | 7, 8 | janela (informaDOI) | [livros-e-capitulos.json](producoes/livros-e-capitulos.json) |
| Manutenção de obra artística | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 21 | 4 | URL direta | [manutencao-de-obra-artistica.json](producoes/manutencao-de-obra-artistica.json) |
| Maquete | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 16 | 3 | URL direta | [maquete.json](producoes/maquete.json) |
| Música | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 31 | 11 | URL direta | [musica.json](producoes/musica.json) |
| Outra produção artística/cultural | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 31 | 11 | URL direta | [outra-producao-artistica-cultural.json](producoes/outra-producao-artistica-cultural.json) |
| Outra produção bibliográfica | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 5 | URL direta | [outra-producao-bibliografica.json](producoes/outra-producao-bibliografica.json) |
| Outra produção técnica | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 18 | 4 | URL direta | [outra-producao-tecnica.json](producoes/outra-producao-tecnica.json) |
| Partitura musical | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 19 | 5 | URL direta | [partitura-musical.json](producoes/partitura-musical.json) |
| Prefácio, posfácio | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 25 | 5 | URL direta | [prefacio-posfacio.json](producoes/prefacio-posfacio.json) |
| Processos ou técnicas | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 20 | 5 | URL direta | [processos-ou-tecnicas.json](producoes/processos-ou-tecnicas.json) |
| Produtos | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 21 | 6 | URL direta | [produtos.json](producoes/produtos.json) |
| Programa de computador sem registro | único | Dados gerais, Resumo, Traduções, Visibilidade, Instituições | 26 | 8 | URL direta | [programa-de-computador-sem-registro.json](producoes/programa-de-computador-sem-registro.json) |
| Redes sociais, websites e blogs | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 15 | 4 | URL direta | [redes-sociais-websites-e-blogs.json](producoes/redes-sociais-websites-e-blogs.json) |
| Relatório de pesquisa | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 16 | 3 | URL direta | [relatorio-de-pesquisa.json](producoes/relatorio-de-pesquisa.json) |
| Texto em jornal ou revista (magazine) | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 22 | 6 | URL direta | [texto-em-jornal-ou-revista-magazine.json](producoes/texto-em-jornal-ou-revista-magazine.json) |
| Trabalhos publicados em anais de eventos | único | D.O.I, Dados gerais, Detalhamento do evento, Detalhamento da publicaçã | 29 | 6 | URL direta | [trabalhos-publicados-em-anais-de-eventos.json](producoes/trabalhos-publicados-em-anais-de-eventos.json) |
| Trabalhos técnicos | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 20 | 4 | URL direta | [trabalhos-tecnicos.json](producoes/trabalhos-tecnicos.json) |
| Tradução | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 25 | 5 | URL direta | [traducao.json](producoes/traducao.json) |

## Patentes e Registros

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Cultivar protegida | único | Dados gerais, Outras informações, Traduções, Visibilidade, Instituiçõe | 27 | 7 | URL direta | [cultivar-protegida.json](patentes-e-registros/cultivar-protegida.json) |
| Cultivar registrada | único | Dados gerais, Outras informações, Traduções, Visibilidade, Instituiçõe | 23 | 7 | URL direta | [cultivar-registrada.json](patentes-e-registros/cultivar-registrada.json) |
| Desenho industrial registrado | f_cod_tipo=DI | Dados gerais, Outras informações, Traduções, Visibilidade, Instituiçõe | 26 | 10 | janela (infDadPat) | [desenho-industrial-registrado.json](patentes-e-registros/desenho-industrial-registrado.json) |
| Marca registrada | f_cod_tipo=MR | Dados gerais, Outras informações, Traduções, Visibilidade | 16 | 10 | janela (infDadPat) | [marca-registrada.json](patentes-e-registros/marca-registrada.json) |
| Patente | f_cod_tipo=PP | Dados gerais, Situação do Depósito/Patente, Resumo, Informações Adicio | 28 | 11 | janela (infDadPat) | [patente.json](patentes-e-registros/patente.json) |
| Programa de Computador Registrado | f_cod_tipo=PC | Dados gerais, Outras informações, Traduções, Visibilidade, Instituiçõe | 30 | 13 | janela (infDadPat) | [programa-de-computador-registrado.json](patentes-e-registros/programa-de-computador-registrado.json) |
| Topografia de circuito integrado registrada | f_cod_tipo=TC | Dados gerais, Outras informações, Traduções, Visibilidade | 16 | 9 | janela (infDadPat) | [topografia-de-circuito-integrado-registrada.json](patentes-e-registros/topografia-de-circuito-integrado-registrada.json) |

## Eventos

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Organização de eventos, congressos, exposições, feiras e olimpíadas | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 21 | 5 | URL direta | [organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json](eventos/organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json) |
| Participação em eventos, congressos, exposições, feiras e olimpíadas | único | Dados gerais, Traduções, Visibilidade | 13 | 6 | URL direta | [participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json](eventos/participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json) |

## Orientações

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Orientações e supervisões concluídas | único | Dados Gerais, Detalhamento, Bolsa, Outras informações, Traduções, Visi | 18 | 9 | URL direta | [orientacoes-e-supervisoes-concluidas.json](orientacoes/orientacoes-e-supervisoes-concluidas.json) |
| Orientações e supervisões em andamento | único | Dados Gerais, Detalhamento, Bolsa, Outras informações, Traduções, Visi | 18 | 9 | URL direta | [orientacoes-e-supervisoes-em-andamento.json](orientacoes/orientacoes-e-supervisoes-em-andamento.json) |

## Bancas

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Participação em bancas de comissões julgadoras | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 13 | 5 | URL direta | [participacao-em-bancas-de-comissoes-julgadoras.json](bancas/participacao-em-bancas-de-comissoes-julgadoras.json) |
| Participação em bancas de trabalhos de conclusão | único | Dados gerais, Detalhamento, Outras informações, Traduções, Visibilidad | 16 | 7 | URL direta | [participacao-em-bancas-de-trabalhos-de-conclusao.json](bancas/participacao-em-bancas-de-trabalhos-de-conclusao.json) |

## Citações

| Item | Formulários | Abas | Campos | Obrigatórios | Abertura | Arquivo |
| --- | --- | --- | --- | --- | --- | --- |
| Citações em outra base bibliográfica | único | Dados da busca, Visibilidade | 6 | 5 | tela única | [citacoes-em-outra-base-bibliografica.json](citacoes/citacoes-em-outra-base-bibliografica.json) |
| Citações no Google Scholar | único | Dados da busca, Visibilidade | 5 | 6 | tela única | [citacoes-no-google-scholar.json](citacoes/citacoes-no-google-scholar.json) |
| Citações no SCOPUS | único | Dados da busca, Visibilidade | 5 | 5 | tela única | [citacoes-no-scopus.json](citacoes/citacoes-no-scopus.json) |
| Citações no SciELO | único | Dados da busca, Visibilidade | 5 | 5 | tela única | [citacoes-no-scielo.json](citacoes/citacoes-no-scielo.json) |
| Citações no Web of Science | único | Dados da busca, Visibilidade | 7 | 5 | tela única | [citacoes-no-web-of-science.json](citacoes/citacoes-no-web-of-science.json) |

## Catálogos (listas completas)

| Catálogo | Total | Campos que usam |
| --- | --- | --- |
| [catalogos/idiomas-149.json](catalogos/idiomas-149.json) | 149 | F_COD_IDIOMA |
| [catalogos/idiomas-152.json](catalogos/idiomas-152.json) | 152 | F_IDIOMA, F_IDIOMA_OBRA |
| [catalogos/paises-244.json](catalogos/paises-244.json) | 244 | f_pais, f_pais_i, f_pais_inst, f_pais_nacio, f_pais_nasc, f_pais_r, fpaispassaporte |
| [catalogos/areas-do-conhecimento.json](catalogos/areas-do-conhecimento.json) | 1354 (9 grandes áreas, 86 áreas, 375 subáreas, 884 especialidades) | grade de Áreas de todos os formulários |
| [catalogos/setores-de-atividade.json](catalogos/setores-de-atividade.json) | 87 | grade de Setores de todos os formulários |
