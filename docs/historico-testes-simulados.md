# Histórico consolidado dos testes simulados

Gerado por `tests/amostras_sinteticas/painel.py` a partir de `tests/historico/execucoes.jsonl` — 723 registros em 21 execuções (de 2026-11-17 a 2026-11-17), 65 itens.

Legenda: ✅ ok · ❌ falha · 🟡 lacuna conhecida · 🟠 parcial (precisou de ajuda manual / não observado) · ⚪ aviso (sem regra ou tratador ainda) · · não testado.
Etapas, na ordem do caminho do documento até o Lattes: **Módulos** (classificador+leitor direto), **Plataforma** (caminho do /api/extract), **Vínculo** (abertura do formulário, lista mapeada e tratador), **Lista Lattes** (leitura da lista no currículo real), **Salvar**, **Conferir**, **Excluir** e **Reconferir** (ciclo no currículo real).

## 1. Resumo por etapa (último resultado de cada item)

| Etapa | ✅ ok | 🟡 lacuna | 🟠 parcial | ⚪ aviso | ❌ falha | · não testado | % ok (sem os avisos) |
| --- | --: | --: | --: | --: | --: | --: | --: |
| Módulos | 24 | 0 | 0 | 41 | 0 | 0 | 100% (24/24) |
| Plataforma | 23 | 0 | 0 | 41 | 0 | 1 | 100% (23/23) |
| Vínculo | 63 | 0 | 0 | 0 | 0 | 2 | 100% (63/63) |
| Lista Lattes | 11 | 0 | 6 | 38 | 0 | 10 | 65% (11/17) |
| Salvar | 5 | 0 | 0 | 0 | 1 | 59 | 83% (5/6) |
| Conferir | 5 | 0 | 0 | 0 | 0 | 60 | 100% (5/5) |
| Excluir | 5 | 0 | 0 | 0 | 0 | 60 | 100% (5/5) |
| Reconferir | 5 | 0 | 0 | 0 | 0 | 60 | 100% (5/5) |

## 2. Matriz item × etapa

| Item | Módulos | Plataforma | Vínculo | Lista Lattes | Salvar | Conferir | Excluir | Reconferir | Registros | Última execução |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | --: | --- |
| `apresentacao` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 27 | 2026-11-17 10:05 |
| `curso_ministrado` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 19 | 2026-11-17 15:11 |
| `organizacao_evento` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 17 | 2026-11-17 17:10 |
| `participacao_evento` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 18 | 2026-11-17 16:40 |
| `premio` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 26 | 2026-11-17 13:20 |
| `formacao_complementar` | ✅ | ✅ | ✅ | ✅ | ❌ | · | · | · | 14 | 2026-11-17 17:40 |
| `anais` | ✅ | ✅ | ✅ | ✅ | · | · | · | · | 12 | 2026-11-17 10:05 |
| `artigo` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 12 | 2026-11-17 10:05 |
| `atuacao_profissional` | ✅ | ✅ | ✅ | ✅ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `banca` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 20 | 2026-11-17 11:20 |
| `formacao_academica` | ✅ | ✅ | ✅ | ✅ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `idioma` | ✅ | ✅ | ✅ | ✅ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `licenca` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 13 | 2026-11-17 11:20 |
| `livro_capitulo` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 13 | 2026-11-17 11:20 |
| `orientacao_concluida` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 13 | 2026-11-17 11:20 |
| `projeto` | ✅ | ✅ | ✅ | ✅ | · | · | · | · | 20 | 2026-11-17 11:20 |
| `revisor_periodico` | ✅ | ✅ | ✅ | 🟠 | · | · | · | · | 13 | 2026-11-17 11:20 |
| `artigo_aceito` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `corpo_editorial` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `orientacao_andamento` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `patente` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 20 | 2026-11-17 11:20 |
| `relatorio_tecnico` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `software_registro` | ✅ | ✅ | ✅ | ⚪ | · | · | · | · | 13 | 2026-11-17 11:20 |
| `artes_cenicas` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `artes_visuais` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `banca_comissao_julgadora` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `caderno` | ✅ | · | · | · | · | · | · | · | 3 | 2026-11-17 10:05 |
| `cartas_mapas` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `citacao_google_scholar` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `citacao_outra_base` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `citacao_scielo` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `citacao_scopus` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `citacao_web_of_science` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `comite_assessoramento` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `cultivar_protegida` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `cultivar_registrada` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `desenho_industrial` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `editoracao` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `endereco` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `entrevista_midia` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `extensao_tecnologica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `identificacao` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `manutencao_obra` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `maquete` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `marca_registrada` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `material_didatico` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `musica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `outra_producao_artistica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `outra_producao_bibliografica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `outra_producao_tecnica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `outras_informacoes` | ⚪ | ⚪ | ✅ | · | · | · | · | · | 8 | 2026-11-17 11:20 |
| `partitura_musical` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `pos_doutorado` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `prefacio_posfacio` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `processo_tecnica` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `produto` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `redes_sociais` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `relatorio_pesquisa` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `revisor_projeto_fomento` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `software_sem_registro` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `texto_jornal_revista` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `topografia_circuito` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `trabalho_tecnico` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `traducao` | ⚪ | ⚪ | ✅ | ⚪ | · | · | · | · | 9 | 2026-11-17 11:20 |
| `texto_inicial` | ⚪ | ⚪ | · | · | · | · | · | · | 7 | 2026-11-17 10:05 |

## 3. Onde testamos mais e onde menos

- **Testados de ponta a ponta no currículo real (Salvar → Excluir → Reconferir):** `apresentacao`, `curso_ministrado`, `organizacao_evento`, `participacao_evento`, `premio`.
- **Profundidade ≥ 5 etapas:** `apresentacao`, `curso_ministrado`, `formacao_complementar`, `organizacao_evento`, `participacao_evento`, `premio`.
- **Só testados no simulado (sem salvar no Lattes), com vínculo/lista prontos:** `anais`, `atuacao_profissional`, `formacao_academica`, `idioma`, `projeto`.
- **Menos testados (sem regra no classificador, só o documento simulado existe):** 41 itens — `artes_cenicas`, `artes_visuais`, `banca_comissao_julgadora`, `cartas_mapas`, `citacao_google_scholar`, `citacao_outra_base`, `citacao_scielo`, `citacao_scopus`, `citacao_web_of_science`, `comite_assessoramento`, `cultivar_protegida`, `cultivar_registrada`, `desenho_industrial`, `editoracao`, `endereco`, `entrevista_midia`, `extensao_tecnologica`, `identificacao`, `manutencao_obra`, `maquete`, `marca_registrada`, `material_didatico`, `musica`, `outra_producao_artistica`, `outra_producao_bibliografica`, `outra_producao_tecnica`, `outras_informacoes`, `partitura_musical`, `pos_doutorado`, `prefacio_posfacio`, `processo_tecnica`, `produto`, `redes_sociais`, `relatorio_pesquisa`, `revisor_projeto_fomento`, `software_sem_registro`, `texto_inicial`, `texto_jornal_revista`, `topografia_circuito`, `trabalho_tecnico`, `traducao`.

## 4. Onde já temos êxito

`anais`, `apresentacao`, `artigo_aceito`, `atuacao_profissional`, `corpo_editorial`, `curso_ministrado`, `formacao_academica`, `idioma`, `organizacao_evento`, `orientacao_andamento`, `participacao_evento`, `patente`, `premio`, `projeto`, `relatorio_tecnico`, `software_registro`

## 5. Onde aprimorar (do mais grave ao menos grave)

| Item | Etapa | Resultado | O que aconteceu |
| --- | --- | :-: | --- |
| `formacao_complementar` | Salvar | ❌ | Lattes recusou: 'Os campos Instituição e Curso não devem ser alterados manualmente. Utilize o link para fazer a seleção.' Instituição e curso são cadastros controlados: precisam ser escolhidos pela lupa/lista do Lattes,  |
| `apresentacao (variação `apresentacao__autoria_no_titulo`)` | Salvar | 🟠 | Lattes recusou salvar: titular ausente da lista de autores (certificado fora do layout real: título engoliu os autores). Salvo após adicionar o titular manualmente por 'Listar todos'. |
| `apresentacao (variação `apresentacao__autoria_no_titulo`)` | Excluir | 🟠 | Caixa nativa de confirmação travou a aba e a automação; a exclusão só concluiu com o OK do usuário (aba fechada/confirmada). |
| `artigo` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `banca` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `licenca` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `livro_capitulo` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `orientacao_concluida` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `revisor_periodico` | Lista Lattes | 🟠 | a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado. |
| `apresentacao (variação `apresentacao__autoria_no_titulo`)` | Módulos | 🟡 | autores='[]', esperado conter '<titular>' |
| `apresentacao (variação `apresentacao__autoria_no_titulo`)` | Plataforma | 🟡 | valor autores='[]', esperado conter '<titular>'; nome do arquivo sem o seu sobrenome (2024_APRESENTACAO_AUTOR_ATIVIDADE-ANTIOXIDANTE-EXTRATOS-VEGETAIS.pdf) |
| `banca (variação `banca__sem_cargo`)` | Módulos | 🟡 | f_nme_orient=None, esperado conter 'Lucas Ferreira Andrade' |
| `banca (variação `banca__sem_cargo`)` | Plataforma | 🟡 | valor f_nme_orient='None', esperado conter 'Lucas Ferreira Andrade'; nome do arquivo sem o seu sobrenome (2024_PRODUCAO_AUTOR_DOCUMENTO.pdf) |
| `patente (variação `patente__carta`)` | Módulos | 🟡 | f_titulo=None, esperado conter 'Bebidas mistas probióticas' |
| `patente (variação `patente__carta`)` | Plataforma | 🟡 | valor f_titulo='None', esperado conter 'Bebidas mistas probióticas'; nome do arquivo sem o seu sobrenome (SEM-ANO_PATENTE_AUTOR_DOCUMENTO.pdf) |
| `premio (variação `premio__so_ano`)` | Módulos | 🟡 | f_ano=None, esperado conter '2023' |
| `premio (variação `premio__so_ano`)` | Plataforma | 🟡 | valor f_ano='None', esperado conter '2023'; nome do arquivo sem o seu sobrenome (SEM-ANO_PRODUCAO_AUTOR_MENCAO-HONROSA.pdf) |
| `projeto (variação `projeto__sem_intitulado`)` | Módulos | 🟡 | f_titulo=None, esperado conter 'Ciência na Rede' |
| `projeto (variação `projeto__sem_intitulado`)` | Plataforma | 🟡 | valor f_titulo='None', esperado conter 'Ciência na Rede'; nome do arquivo sem o seu sobrenome (SEM-ANO_PROJETO_AUTOR_DOCUMENTO.pdf) |

**Recorrentes** (mesma causa em vários itens):

- Lista vazia no currículo: formato da linha não observado: 6 item(ns)
- Nome padronizado do arquivo sem o sobrenome do usuário: 5 item(ns)

## 6. Registro das ações testadas (cronológico)

| Execução | Origem | Registros | ✅ | 🟡 | 🟠 | ⚪ | ❌ | Itens com ocorrência não-ok (resumo) |
| --- | --- | --: | --: | --: | --: | --: | --: | --- |
| 2026-11-17 08:52:00 | `manual_lattes_real` | 4 | 2 | 0 | 2 | 0 | 0 | apresentacao |
| 2026-11-17 09:12:00 | `manual_lattes_real` | 4 | 4 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 09:29:33 | `teste_amostras_sinteticas` | 70 | 24 | 5 | 0 | 41 | 0 | — |
| 2026-11-17 09:29:34 | `teste_plataforma_sinteticos` | 92 | 38 | 5 | 0 | 41 | 8 | artigo_aceito, formacao_academica, livro_capitulo, orientacao_andamento, orientacao_concluida, patente, software_registro |
| 2026-11-17 10:03:11 | `teste_plataforma_sinteticos` | 92 | 38 | 5 | 0 | 41 | 8 | artigo_aceito, formacao_academica, livro_capitulo, orientacao_andamento, orientacao_concluida, patente, software_registro |
| 2026-11-17 10:03:27 | `teste_plataforma_sinteticos` | 92 | 41 | 5 | 0 | 41 | 5 | atuacao_profissional, corpo_editorial, curso_ministrado, organizacao_evento, revisor_periodico |
| 2026-11-17 10:05:00 | `manual_lattes_real` | 55 | 10 | 0 | 7 | 38 | 0 | artigo, banca, curso_ministrado, licenca, livro_capitulo, orientacao_concluida, revisor_periodico |
| 2026-11-17 10:05:30 | `teste_amostras_sinteticas` | 70 | 24 | 5 | 0 | 41 | 0 | — |
| 2026-11-17 10:05:32 | `teste_plataforma_sinteticos` | 92 | 46 | 5 | 0 | 41 | 0 | — |
| 2026-11-17 10:05:46 | `teste_amostras_sinteticas` | 70 | 24 | 5 | 0 | 41 | 0 | — |
| 2026-11-17 11:20:00 | `manual_lattes_real` | 60 | 60 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 12:05:00 | `manual_lattes_real` | 1 | 0 | 0 | 0 | 0 | 1 | premio |
| 2026-11-17 13:10:00 | `manual_lattes_real` | 4 | 4 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 13:20:00 | `manual_lattes_real` | 1 | 1 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 14:05:00 | `manual_lattes_real` | 1 | 0 | 0 | 0 | 0 | 1 | curso_ministrado |
| 2026-11-17 15:10:00 | `manual_lattes_real` | 4 | 4 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 15:11:00 | `manual_lattes_real` | 1 | 1 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 16:00:00 | `manual_lattes_real` | 1 | 0 | 0 | 0 | 0 | 1 | participacao_evento |
| 2026-11-17 16:40:00 | `manual_lattes_real` | 4 | 4 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 17:10:00 | `manual_lattes_real` | 4 | 4 | 0 | 0 | 0 | 0 | — |
| 2026-11-17 17:40:00 | `manual_lattes_real` | 1 | 0 | 0 | 0 | 0 | 1 | formacao_complementar |

### Detalhe das execuções no currículo real

**2026-11-17 08:52:00**

- `apresentacao` · Salvar · 🟠 Lattes recusou salvar: titular ausente da lista de autores (certificado fora do layout real: título engoliu os autores). Salvo após adicionar o titular manualmente por 'Listar todos'.
- `apresentacao` · Conferir · ✅ Item novo apareceu na linha 1 da lista de apresentações (9 itens).
- `apresentacao` · Excluir · 🟠 Caixa nativa de confirmação travou a aba e a automação; a exclusão só concluiu com o OK do usuário (aba fechada/confirmada).
- `apresentacao` · Reconferir · ✅ Reentrada em nova aba: lista voltou a 8 itens; o item de teste não existe mais.

**2026-11-17 09:12:00**

- `apresentacao` · Salvar · ✅ Salvou sozinho (mensagem 'o formulário fechou após Salvar'); item nº 70, título limpo.
- `apresentacao` · Conferir · ✅ Lista de apresentações passou de 8 para 9 itens; nº 70 com o título de teste.
- `apresentacao` · Excluir · ✅ Título conferido, confirm() aceito por código antes de del(); sem caixa nativa.
- `apresentacao` · Reconferir · ✅ Lista voltou a 8 itens; nºs originais 69,45,55,29,31,28,30,53 intactos; nº 70 ausente.

**2026-11-17 10:05:00**

- `participacao_evento` · Lista Lattes · ✅ lista lida no currículo real: 37 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `organizacao_evento` · Lista Lattes · ✅ lista lida no currículo real: 6 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `curso_ministrado` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `formacao_complementar` · Lista Lattes · ✅ lista lida no currículo real: 4 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `formacao_academica` · Lista Lattes · ✅ lista lida no currículo real: 6 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `apresentacao` · Lista Lattes · ✅ lista lida no currículo real: 8 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `anais` · Lista Lattes · ✅ lista lida no currículo real: 16 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `artigo` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `livro_capitulo` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `banca` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `orientacao_concluida` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `atuacao_profissional` · Lista Lattes · ✅ lista lida no currículo real: 7 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `revisor_periodico` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.
- `premio` · Lista Lattes · ✅ lista lida no currículo real: 1 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `projeto` · Lista Lattes · ✅ lista lida no currículo real: 3 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `idioma` · Lista Lattes · ✅ lista lida no currículo real: 3 linhas, todas com nº e formulário do item (tratador genérico da extensão).
- `licenca` · Lista Lattes · 🟠 a lista abre (HTTP 200) mas está vazia no currículo: formato das linhas ainda não observado.

**2026-11-17 11:20:00**

- `artes_cenicas` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `artes_visuais` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `artigo_aceito` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `atuacao_profissional` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `banca` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `banca_comissao_julgadora` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `cartas_mapas` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `citacao_google_scholar` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `citacao_outra_base` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `citacao_scielo` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `citacao_scopus` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `citacao_web_of_science` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `comite_assessoramento` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `corpo_editorial` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `cultivar_protegida` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `cultivar_registrada` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `curso_ministrado` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `desenho_industrial` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `editoracao` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `endereco` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `entrevista_midia` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `extensao_tecnologica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `formacao_academica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `formacao_complementar` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `identificacao` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `idioma` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `licenca` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `livro_capitulo` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `manutencao_obra` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `maquete` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `marca_registrada` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `material_didatico` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `musica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `organizacao_evento` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `orientacao_andamento` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `orientacao_concluida` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `outra_producao_artistica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `outra_producao_bibliografica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `outra_producao_tecnica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `outras_informacoes` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `participacao_evento` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `partitura_musical` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `patente` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `pos_doutorado` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `prefacio_posfacio` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `premio` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `processo_tecnica` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `produto` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `projeto` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `redes_sociais` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `relatorio_pesquisa` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `relatorio_tecnico` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `revisor_periodico` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `revisor_projeto_fomento` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `software_registro` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `software_sem_registro` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `texto_jornal_revista` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `topografia_circuito` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `trabalho_tecnico` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.
- `traducao` · Vínculo · ✅ Formulário aberto direto pela URL da variante no currículo real (sem salvar): todas as variantes testadas abriram e trazem os campos obrigatórios do mapeamento.

**2026-11-17 12:05:00**

- `premio` · Salvar · ❌ Itens genéricos só preenchiam o formulário e paravam em 'falta você salvar': o Salvar automático não existia no caminho genérico (corrigido na extensão 0.9.1, ainda não repetido no Lattes). Nada foi gravado em lugar errado (listas de prêmio e tradução conferidas).

**2026-11-17 13:10:00**

- `premio` · Salvar · ✅ Pela plataforma (extensão 0.9.2): salvou sozinho; 'salvo e confirmado no currículo (item nº 2)'. Antes, 2 defeitos corrigidos: Salvar automático ausente no caminho genérico e id do item.
- `premio` · Conferir · ✅ Lista de prêmios: nº 2 'Menção honrosa' criado; nº 1 (original) intacto.
- `premio` · Excluir · ✅ Botão Remover da plataforma (confirm() aceito por código): 'removido do Lattes (o item nº 2 saiu da lista)'.
- `premio` · Reconferir · ✅ Currículo recarregado: lista voltou só com o nº 1 original.

**2026-11-17 13:20:00**

- `premio` · Salvar · ✅ ALTERAÇÃO pela plataforma: escolhido o nº 2 na lista do Lattes e trocado o título; 'alteração salva: o item nº 2 continua na lista'. Lista conferida: título novo, nº 1 intacto, mesma contagem.

**2026-11-17 14:05:00**

- `curso_ministrado` · Salvar · ❌ Lattes recusou salvar duas vezes: 'O seu nome deverá ser incluído na lista de autores'. O titular digitado na grade de autores não é reconhecido; só funciona escolhido por 'Listar todos'. Nada gravado (lista do curso continuou vazia). Em seguida, o alerta nativo da extensão travou a aba do currículo.

**2026-11-17 15:10:00**

- `curso_ministrado` · Salvar · ✅ Pela plataforma (extensão 0.9.3): titular escolhido por 'Listar todos'; 'salvo e confirmado no currículo (item nº 70)'. Antes: titular digitado era recusado (2 tentativas).
- `curso_ministrado` · Conferir · ✅ Lista de cursos de curta duração: de 0 para 1 item (nº 70, 'Introdução à Bioinformática Aplicada', Extensão, 2023). Formato da linha observado: Título | Tipo | Ano.
- `curso_ministrado` · Excluir · ✅ Botão Remover da plataforma: 'removido do Lattes (o item nº 70 saiu da lista)'.
- `curso_ministrado` · Reconferir · ✅ Currículo recarregado: lista de cursos voltou a 0 itens.

**2026-11-17 15:11:00**

- `curso_ministrado` · Lista Lattes · ✅ Formato da linha observado com um item real: Título | Tipo | Ano; seq e URL do formulário lidos pelo tratador genérico.

**2026-11-17 16:00:00**

- `participacao_evento` · Salvar · ❌ Não salvou: o campo 'Tipo da apresentação/participação' depende da forma e fica sem opções para 'Ouvinte' (conferido no Lattes real: Convidado e Participante têm opções, Ouvinte não). O preenchedor tratava a lista vazia como erro e não salvava (corrigido na extensão 0.9.4). Lista de participação ficou em 37: nada gravado. A mensagem 'cliquei em Salvar' aparece mesmo quando o Salvar não foi clicado

**2026-11-17 16:40:00**

- `participacao_evento` · Salvar · ✅ Extensão 0.9.4: 'salvo e confirmado no currículo (item nº 70)'. Documento empatou com formação complementar (1 clique de confirmação na tela); 'Ouvinte' sem tipo tratado.
- `participacao_evento` · Conferir · ✅ Lista de participação em eventos: 37 -> 38; nº 70 '12º Congresso Brasileiro de Ciências Exemplares | Ouvinte | 2025'.
- `participacao_evento` · Excluir · ✅ Botão Remover da plataforma: 'removido do Lattes (o item nº 70 saiu da lista)'.
- `participacao_evento` · Reconferir · ✅ Currículo recarregado: lista de participação voltou a 37 itens.

**2026-11-17 17:10:00**

- `organizacao_evento` · Salvar · ✅ Salvou de primeira (extensão 0.9.4): 'salvo e confirmado no currículo (item nº 70)'; titular escolhido em 'Listar todos'.
- `organizacao_evento` · Conferir · ✅ Lista de organização de eventos: 6 -> 7; nº 70 'Simpósio de Inovação em Saúde Exemplar | Outro | 2024'.
- `organizacao_evento` · Excluir · ✅ Botão Remover da plataforma: 'removido do Lattes (o item nº 70 saiu da lista)'.
- `organizacao_evento` · Reconferir · ✅ Currículo recarregado: lista de organização voltou a 6; participação 37, cursos 0, prêmios 1 (inalterados).

**2026-11-17 17:40:00**

- `formacao_complementar` · Salvar · ❌ Lattes recusou: 'Os campos Instituição e Curso não devem ser alterados manualmente. Utilize o link para fazer a seleção.' Instituição e curso são cadastros controlados: precisam ser escolhidos pela lupa/lista do Lattes, não digitados. Além disso o leitor extrai o curso com prefixo e aspas (extensão "Estatística com R...). Lista de formação complementar não mudou (nada gravado).

## 7. Notas e decisões

- **17/11/2026 — tratador genérico (extensão 0.8.0):** a extensão passou a listar, confirmar e excluir qualquer item de `itens/listas_lattes.json`
  (55 itens). A linha de cada lista traz o formulário do item (`setarUrl`); o item novo é reconhecido por diferença de nºs antes/depois de salvar.
  Validado só na leitura das listas do currículo real; salvar/excluir fora da apresentação ainda não rodaram no Lattes.
- **Regra do ciclo real:** nunca excluir item cujo título não seja o fictício; `confirm()` é trocado antes de `del()` para a caixa nativa não travar.
- **Pendências de teste:** ciclo salvar → conferir → excluir → reconferir nos itens com leitor e abertura direta (participação em evento,
  organização, curso ministrado, formação complementar, prêmio, projeto, atuação, revisor, corpo editorial, idioma, licença); depois os de janela de escolha.
- **17/11/2026 — melhorias:** (1) o "problema" das janelas de escolha (patente, livro, formação...) era do teste: os formulários abrem direto pela URL da variante;
  75 variantes foram abertas no currículo real (sem salvar) e todas trouxeram os campos obrigatórios. (2) Orientações ganharam especificação (18 campos).
  (3) Leitores: periódico em inglês ("Journal of ...") e País da instituição no registro de software. (4) Formulários de registro agora levam o nº/instituição
  reais na URL (antes iam com um nº de exemplo). (5) Alteração: a plataforma lista os itens do Lattes e altera o escolhido (extensão 0.9.0); ainda não
  executada no Lattes real.
- **17/11/2026 — 1º teste real fora da apresentação (prêmio):** o formulário abriu e foi preenchido, mas parou em "falta você salvar": o caminho genérico não tinha Salvar
  automático. Corrigido (extensão 0.9.1: clica em Salvar quando não há obrigatório vazio nem alerta). Atenção para o próximo teste: uma janela de formulário esquecida
  aberta no currículo pode atrapalhar (recarregar o currículo antes de cada ciclo).
- **17/11/2026 — 2º defeito no 1º teste real:** a tela passava o nome do item ("Prêmios e títulos") onde a extensão e o registro de envios esperam o id (`premio`);
  a lista, a confirmação e a remoção nunca casariam. Corrigido (`__generico.id`, extensão 0.9.2).
- **17/11/2026 — ciclo real do prêmio completo (incluir, alterar, remover, reconferir) e 3º defeito:** em itens com autores (ex.: curso ministrado) o Lattes recusa o titular
  digitado na grade; ele precisa ser escolhido em "Listar todos". A correção parcial (garantir o titular na lista de autores) está em `genGrades()`, mas a extensão ainda
  precisa selecionar o titular pela lista do Lattes. Outro risco: o `alert()` final do preenchedor trava a aba do Lattes na automação quando o Salvar falha.
- **17/11/2026 — titular nos autores (extensão 0.9.3):** inspecionado no Lattes real (sem salvar): "Listar todos" mostra `a.label` com "Nome (CITAÇÃO)" e clicar nele põe o titular na tabela de
  autores. O preenchedor genérico agora escolhe o titular por essa lista e só digita os demais autores. Ainda falta repetir o ciclo do curso ministrado com ela.
- **17/11/2026 — 2º item testado de ponta a ponta no Lattes real: curso ministrado** (incluir, confirmar na lista, remover pela plataforma, reconferir). Defeitos que apareceram no caminho e foram
  corrigidos: titular nos autores por "Listar todos". Itens com autores agora seguem o mesmo caminho. Próximos: participação em evento, organização de evento, idioma, atuação profissional.
- **17/11/2026 — participação em evento (1ª tentativa):** o documento empatou com formação complementar (a tela pede 1 clique de confirmação). O Lattes não oferece "tipo" para a forma
  "Ouvinte"; o preenchedor tratava isso como erro e deixava de salvar. Corrigido na extensão 0.9.4. Defeito de mensagem: "cliquei em Salvar, mas o item não apareceu" é exibido
  também quando o Salvar não foi clicado; vale separar os dois casos.
- **17/11/2026 — participação em evento: ciclo real completo** (37 -> 38 -> 37) após o ajuste do campo dependente (extensão 0.9.4). Itens validados de ponta a ponta no Lattes real: apresentação, prêmio (incl. alteração), curso ministrado, participação em evento.
- **17/11/2026 — organização de evento: ciclo real completo** (6 -> 7 -> 6), sem defeito novo. Validados de ponta a ponta: apresentação, prêmio (incl. alteração), curso ministrado, participação e organização de evento.
- **17/11/2026 — formação complementar (1ª tentativa):** o Lattes recusa instituição e curso digitados; é preciso escolhê-los pelo link (cadastros controlados). Esse é o mesmo bloqueio esperado para
  formação acadêmica, atuação profissional, bancas e projetos (instituição/curso/órgão). Próxima melhoria: tratador de cadastro controlado no preenchedor (abrir a lupa, buscar por nome e escolher a opção idêntica).
  Também: o leitor extrai o curso com prefixo e aspas (`extensão "Estatística com R...`).

