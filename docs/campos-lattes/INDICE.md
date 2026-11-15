# Mapeamento dos formulários do Currículo Lattes

Mapeado em 15/11/2026 no Lattes real, **somente leitura** (nenhum item foi salvo). Cada arquivo traz nome técnico,
tipo, limite de caracteres, opções de selects e rádios, grades, janelas auxiliares e a função do botão Salvar.
O código do currículo aparece como `<codigo_do_cv>`. Rótulos são o texto mais próximo do campo e podem estar deslocados;
o `name` é a referência confiável.


## Dados gerais

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Endereço | único | 45 | tela única | grades: holder | [endereco.json](dados-gerais/endereco.json) |
| Identificação | único | 46 | tela única | grades: holder | [identificacao.json](dados-gerais/identificacao.json) |
| Idiomas | único | 12 | URL direta |  | [idiomas.json](dados-gerais/idiomas.json) |
| Licença Maternidade, Paternidade e Adoção | único | 7 | URL direta |  | [licenca-maternidade-paternidade-e-adocao.json](dados-gerais/licenca-maternidade-paternidade-e-adocao.json) |
| Outras informações relevantes | único | 1 | tela única |  | [outras-informacoes-relevantes.json](dados-gerais/outras-informacoes-relevantes.json) |
| Prêmios e títulos | único | 6 | URL direta |  | [premios-e-titulos.json](dados-gerais/premios-e-titulos.json) |
| Texto inicial do Currículo Lattes | único | 2 | tela única |  | [texto-inicial-do-curriculo-lattes.json](dados-gerais/texto-inicial-do-curriculo-lattes.json) |

## Formação

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Formação acadêmica/titulação | Doutorado, Mestrado, Mestrado Profissional, Especialização, Especializ | 29, 29, 29, 13, 16, 21, 10, 7, 7, 13 | tela única | grades: palavras-chave, setores de atividade, áreas do conhecimento | [formacao-academica-titulacao.json](formacao/formacao-academica-titulacao.json) |
| Formação complementar | único | 5 | URL direta |  | [formacao-complementar.json](formacao/formacao-complementar.json) |
| Pós-doutorado e/ou livre-docência | Pós-Doutorado, Livre Docência | 11, 12 | tela única | grades: palavras-chave, setores de atividade, áreas do conhecimento | [pos-doutorado-e-ou-livre-docencia.json](formacao/pos-doutorado-e-ou-livre-docencia.json) |

## Atuação

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Atuação profissional | único | 15 | URL direta |  | [atuacao-profissional.json](atuacao/atuacao-profissional.json) |
| Linhas de pesquisa | — | — | tela única | Item abre direto uma janela/tela sem lista. | [linhas-de-pesquisa.json](atuacao/linhas-de-pesquisa.json) |
| Membro de comitê de assessoramento | único | 11 | URL direta |  | [membro-de-comite-de-assessoramento.json](atuacao/membro-de-comite-de-assessoramento.json) |
| Membro de corpo editorial | único | 10 | URL direta |  | [membro-de-corpo-editorial.json](atuacao/membro-de-corpo-editorial.json) |
| Revisor de periódico | único | 10 | URL direta |  | [revisor-de-periodico.json](atuacao/revisor-de-periodico.json) |
| Revisor de projeto de agência de fomento | único | 10 | URL direta |  | [revisor-de-projeto-de-agencia-de-fomento.json](atuacao/revisor-de-projeto-de-agencia-de-fomento.json) |
| Áreas de atuação | único | 5 | tela única | grades: áreas do conhecimento | [areas-de-atuacao.json](atuacao/areas-de-atuacao.json) |

## Projetos

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Outros tipos de projetos | único | 39 | URL direta | grades: autores, titularInstHolder, titularPessoaHolder | [outros-tipos-de-projetos.json](projetos/outros-tipos-de-projetos.json) |
| Projeto de desenvolvimento tecnológico | único | 40 | URL direta | grades: autores, titularInstHolder, titularPessoaHolder | [projeto-de-desenvolvimento-tecnologico.json](projetos/projeto-de-desenvolvimento-tecnologico.json) |
| Projeto de ensino | único | 41 | URL direta | grades: autores, titularInstHolder, titularPessoaHolder | [projeto-de-ensino.json](projetos/projeto-de-ensino.json) |
| Projeto de extensão | único | 39 | URL direta | grades: autores, titularInstHolder, titularPessoaHolder | [projeto-de-extensao.json](projetos/projeto-de-extensao.json) |
| Projetos de pesquisa | único | 39 | URL direta | grades: autores, titularInstHolder, titularPessoaHolder | [projetos-de-pesquisa.json](projetos/projetos-de-pesquisa.json) |

## Produções

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Apresentação de trabalho e palestra | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [apresentacao-de-trabalho-e-palestra.json](producoes/apresentacao-de-trabalho-e-palestra.json) |
| Artes cênicas | único | 38 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [artes-cenicas.json](producoes/artes-cenicas.json) |
| Artes visuais | único | 32 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [artes-visuais.json](producoes/artes-visuais.json) |
| Artigos aceitos para publicação | único | 23 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [artigos-aceitos-para-publicacao.json](producoes/artigos-aceitos-para-publicacao.json) |
| Assessoria e consultoria | único | 28 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [assessoria-e-consultoria.json](producoes/assessoria-e-consultoria.json) |
| Cartas, mapas ou similares | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [cartas-mapas-ou-similares.json](producoes/cartas-mapas-ou-similares.json) |
| Curso de curta duração ministrado | único | 28 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [curso-de-curta-duracao-ministrado.json](producoes/curso-de-curta-duracao-ministrado.json) |
| Desenvolvimento de material didático ou instrucional | único | 24 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [desenvolvimento-de-material-didatico-ou-instrucional.json](producoes/desenvolvimento-de-material-didatico-ou-instrucional.json) |
| Editoração | único | 26 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [editoracao.json](producoes/editoracao.json) |
| Entrevistas, mesas redondas, programas e comentários na mídia | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [entrevistas-mesas-redondas-programas-e-comentarios-na-midia.json](producoes/entrevistas-mesas-redondas-programas-e-comentarios-na-midia.json) |
| Extensão tecnológica | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [extensao-tecnologica.json](producoes/extensao-tecnologica.json) |
| Livros e capítulos | Livro, Capitulo | 32, 33 | janela (informaDOI) | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [livros-e-capitulos.json](producoes/livros-e-capitulos.json) |
| Manutenção de obra artística | único | 29 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [manutencao-de-obra-artistica.json](producoes/manutencao-de-obra-artistica.json) |
| Maquete | único | 24 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [maquete.json](producoes/maquete.json) |
| Música | único | 39 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [musica.json](producoes/musica.json) |
| Outra produção artística/cultural | único | 39 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [outra-producao-artistica-cultural.json](producoes/outra-producao-artistica-cultural.json) |
| Outra produção bibliográfica | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [outra-producao-bibliografica.json](producoes/outra-producao-bibliografica.json) |
| Outra produção técnica | único | 26 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [outra-producao-tecnica.json](producoes/outra-producao-tecnica.json) |
| Partitura musical | único | 27 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [partitura-musical.json](producoes/partitura-musical.json) |
| Prefácio, posfácio | único | 33 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [prefacio-posfacio.json](producoes/prefacio-posfacio.json) |
| Processos ou técnicas | único | 28 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [processos-ou-tecnicas.json](producoes/processos-ou-tecnicas.json) |
| Produtos | único | 29 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [produtos.json](producoes/produtos.json) |
| Programa de computador sem registro | único | 37 | URL direta | grades: autores, palavras-chave, programaHolder, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do  | [programa-de-computador-sem-registro.json](producoes/programa-de-computador-sem-registro.json) |
| Redes sociais, websites e blogs | único | 23 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [redes-sociais-websites-e-blogs.json](producoes/redes-sociais-websites-e-blogs.json) |
| Relatório de pesquisa | único | 24 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [relatorio-de-pesquisa.json](producoes/relatorio-de-pesquisa.json) |
| Texto em jornal ou revista (magazine) | único | 30 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [texto-em-jornal-ou-revista-magazine.json](producoes/texto-em-jornal-ou-revista-magazine.json) |
| Trabalhos publicados em anais de eventos | único | 37 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [trabalhos-publicados-em-anais-de-eventos.json](producoes/trabalhos-publicados-em-anais-de-eventos.json) |
| Trabalhos técnicos | único | 28 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [trabalhos-tecnicos.json](producoes/trabalhos-tecnicos.json) |
| Tradução | único | 33 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [traducao.json](producoes/traducao.json) |

## Patentes e Registros

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Cultivar protegida | único | 37 | URL direta | grades: autores, palavras-chave, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do conhecimento | [cultivar-protegida.json](patentes-e-registros/cultivar-protegida.json) |
| Cultivar registrada | único | 33 | URL direta | grades: autores, palavras-chave, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do conhecimento | [cultivar-registrada.json](patentes-e-registros/cultivar-registrada.json) |
| Desenho industrial registrado | f_cod_tipo=DI | 36 | janela (infDadPat) | grades: autores, palavras-chave, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do conhecimento | [desenho-industrial-registrado.json](patentes-e-registros/desenho-industrial-registrado.json) |
| Marca registrada | f_cod_tipo=MR | 24 | janela (infDadPat) | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [marca-registrada.json](patentes-e-registros/marca-registrada.json) |
| Patente | f_cod_tipo=PP | 38 | janela (infDadPat) | grades: autores, palavras-chave, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do conhecimento | [patente.json](patentes-e-registros/patente.json) |
| Programa de Computador Registrado | f_cod_tipo=PC | 41 | janela (infDadPat) | grades: autores, palavras-chave, programaHolder, setores de atividade, titularInstHolder, titularPessoaHolder, áreas do  | [programa-de-computador-registrado.json](patentes-e-registros/programa-de-computador-registrado.json) |
| Topografia de circuito integrado registrada | f_cod_tipo=TC | 24 | janela (infDadPat) | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [topografia-de-circuito-integrado-registrada.json](patentes-e-registros/topografia-de-circuito-integrado-registrada.json) |

## Eventos

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Organização de eventos, congressos, exposições, feiras e olimpíadas | único | 29 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json](eventos/organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json) |
| Participação em eventos, congressos, exposições, feiras e olimpíadas | único | 15 | URL direta |  | [participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json](eventos/participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json) |

## Orientações

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Orientações e supervisões concluídas | único | 25 | URL direta | grades: palavras-chave, setores de atividade, áreas do conhecimento | [orientacoes-e-supervisoes-concluidas.json](orientacoes/orientacoes-e-supervisoes-concluidas.json) |
| Orientações e supervisões em andamento | único | 25 | URL direta | grades: palavras-chave, setores de atividade, áreas do conhecimento | [orientacoes-e-supervisoes-em-andamento.json](orientacoes/orientacoes-e-supervisoes-em-andamento.json) |

## Bancas

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Participação em bancas de comissões julgadoras | único | 21 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [participacao-em-bancas-de-comissoes-julgadoras.json](bancas/participacao-em-bancas-de-comissoes-julgadoras.json) |
| Participação em bancas de trabalhos de conclusão | único | 24 | URL direta | grades: autores, palavras-chave, setores de atividade, áreas do conhecimento | [participacao-em-bancas-de-trabalhos-de-conclusao.json](bancas/participacao-em-bancas-de-trabalhos-de-conclusao.json) |

## Citações

| Item | Formulários | Campos | Abertura | Observações | Arquivo |
| --- | --- | --- | --- | --- | --- |
| Citações em outra base bibliográfica | único | 8 | tela única |  | [citacoes-em-outra-base-bibliografica.json](citacoes/citacoes-em-outra-base-bibliografica.json) |
| Citações no Google Scholar | único | 7 | tela única |  | [citacoes-no-google-scholar.json](citacoes/citacoes-no-google-scholar.json) |
| Citações no SCOPUS | único | 7 | tela única |  | [citacoes-no-scopus.json](citacoes/citacoes-no-scopus.json) |
| Citações no SciELO | único | 7 | tela única |  | [citacoes-no-scielo.json](citacoes/citacoes-no-scielo.json) |
| Citações no Web of Science | único | 9 | tela única |  | [citacoes-no-web-of-science.json](citacoes/citacoes-no-web-of-science.json) |
