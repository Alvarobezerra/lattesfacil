# Consolidação de campos: mapeado (Claude Code + Antigravity) × plataforma hoje

Gerado por `python ferramentas/consolidar_campos.py` (não editar à mão; rode de novo após cada mudança). Dados brutos: `consolidacao_campos.json`.

## Critério de "pronto" (meta do projeto)

Um formulário só está pronto quando: (1) captura real e paridade 0; (2) matriz F5 sem falha; (3) catálogos completos; (4) nenhum campo mapeado pelo Antigravity ausente; (5) disponível no app (leitor + formulário); (6) **salvamento de teste com TODOS os campos e grades preenchidos**, conferido na lista e na reabertura; (7) **exclusão pela plataforma** testada e conferida. Registro único (identificação, endereço, textos): salvar com cópia e restauração do original no lugar da exclusão.

## Placar

| Indicador | Itens |
| --- | --- |
| Specs (formulários) na plataforma | 64 (79 variantes) |
| Captura real do Claude | 64 |
| Paridade spec × Lattes = 0 | 64 |
| Matriz F5 executada sem falha | 64 (executada em 64) |
| Catálogo truncado em 80 opções no spec | 0 |
| Com campos vistos só pelo Antigravity | 0 |
| Com `maxlength` divergente (spec × Antigravity) | 0 |
| Disponível no app (leitor) | 64 |
| Salvamento de teste conferido (Claude) | 44 |
| Salvamento de teste com todos os campos | 64 |
| Exclusão suportada pela plataforma | 60 |
| Salvar + reabrir + excluir validado pelo Antigravity (amostra manual) | 60 |
| **Pronto pelo critério acima** | **64** |

## Matriz por item

Legenda: Par = pendentes de paridade · F5 = casos OK/total · Cat80 = catálogo cortado · só AG = campos que só o Antigravity viu · Carga = campos preenchidos pelo salvamento de teste / preenchíveis (grades) · Excl = exclusão pela plataforma · F7-AG = salvar/reabrir/excluir pelo Antigravity.

| Seção | Item | Var | Campos spec | Par | F5 | Cat80 | só AG | App | Salvou | Carga | Excl | F7-AG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Atuação | `atuacao_profissional` | 1 | 13 | 0 | 36/36 |  |  | ✔ | ✘ | 12/12 (0/0) | ✔ | ✔ |
| Atuação | `comite_assessoramento` | 1 | 9 | 0 | 25/25 |  |  | ✔ | ✘ | 8/8 (0/0) | ✔ | ✔ |
| Atuação | `corpo_editorial` | 1 | 8 | 0 | 21/21 |  |  | ✔ | ✘ | 7/7 (0/0) | ✔ | ✔ |
| Atuação | `revisor_periodico` | 1 | 8 | 0 | 21/21 |  |  | ✔ | ✘ | 7/7 (0/0) | ✔ | ✔ |
| Atuação | `revisor_projeto_fomento` | 1 | 8 | 0 | 21/21 |  |  | ✔ | ✘ | 7/7 (0/0) | ✔ | ✔ |
| Bancas | `banca` | 1 | 16 | 0 | 196/196 |  |  | ✔ | ✔ | 13/13 (4/4) | ✔ | ✔ |
| Bancas | `banca_comissao_julgadora` | 1 | 13 | 0 | 190/190 |  |  | ✔ | ✔ | 10/10 (4/4) | ✔ | ✔ |
| Citações | `citacao_google_scholar` | 1 | 5 | 0 | 14/14 |  |  | ✔ | ✘ | 4/4 (0/0) | ✔ | ✔ |
| Citações | `citacao_outra_base` | 1 | 6 | 0 | 18/18 |  |  | ✔ | ✘ | 5/5 (0/0) | ✔ | ✔ |
| Citações | `citacao_scielo` | 1 | 5 | 0 | 14/14 |  |  | ✔ | ✘ | 4/4 (0/0) | ✔ | ✔ |
| Citações | `citacao_scopus` | 1 | 5 | 0 | 14/14 |  |  | ✔ | ✘ | 4/4 (0/0) | ✔ | ✔ |
| Citações | `citacao_web_of_science` | 1 | 7 | 0 | 21/21 |  |  | ✔ | ✘ | 6/6 (0/0) | ✔ | ✔ |
| Dados gerais | `endereco` | 1 | 37 | 0 | 604/604 |  |  | ✔ | único | 33/33 (0/0) | n/a | ✘ |
| Dados gerais | `identificacao` | 1 | 30 | 0 | 843/843 |  |  | ✔ | único | 20/20 (0/0) | n/a | ✘ |
| Dados gerais | `idioma` | 1 | 10 | 0 | 161/161 |  |  | ✔ | ✘ | 9/9 (0/0) | ✔ | ✔ |
| Dados gerais | `licenca` | 1 | 5 | 0 | 15/15 |  |  | ✔ | ✘ | 4/4 (0/0) | ✔ | ✔ |
| Dados gerais | `outras_informacoes` | 1 | 1 | 0 | 4/4 |  |  | ✔ | único | 1/1 (0/0) | n/a | ✘ |
| Dados gerais | `premio` | 1 | 4 | 0 | 11/11 |  |  | ✔ | ✔ | 3/3 (0/0) | ✔ | ✔ |
| Dados gerais | `texto_inicial` | 1 | 2 | 0 | 8/8 |  |  | ✔ | único | 2/2 (0/0) | n/a | ✘ |
| Eventos | `organizacao_evento` | 1 | 21 | 0 | 216/216 |  |  | ✔ | ✔ | 18/18 (4/4) | ✔ | ✔ |
| Eventos | `participacao_evento` | 1 | 13 | 0 | 121/121 |  |  | ✔ | ✔ | 11/11 (0/0) | ✔ | ✔ |
| Formação | `formacao_academica` | 10 | 23 | 0 | 288/288 |  |  | ✔ | ✘ | 109/109 (12/12) | ✔ | ✔ |
| Formação | `formacao_complementar` | 1 | 9 | 0 | 13/13 |  |  | ✔ | ✘ | 9/9 (0/0) | ✔ | ✔ |
| Formação | `pos_doutorado` | 2 | 10 | 0 | 25/25 |  |  | ✔ | ✘ | 10/10 (4/4) | ✔ | ✔ |
| Orientações | `orientacao_andamento` | 1 | 18 | 0 | 207/207 |  |  | ✔ | ✔ | 17/17 (3/3) | ✔ | ✔ |
| Orientações | `orientacao_concluida` | 1 | 18 | 0 | 207/207 |  |  | legado | ✔ | 17/17 (3/3) | ✔ | ✔ |
| Patentes e Registros | `cultivar_protegida` | 1 | 27 | 0 | 127/127 |  |  | ✔ | ✔ | 14/14 (6/6) | ✔ | ✔ |
| Patentes e Registros | `cultivar_registrada` | 1 | 23 | 0 | 114/114 |  |  | ✔ | ✔ | 11/11 (6/6) | ✔ | ✔ |
| Patentes e Registros | `desenho_industrial` | 1 | 26 | 0 | 122/122 |  |  | ✔ | ✔ | 13/13 (6/6) | ✔ | ✔ |
| Patentes e Registros | `marca_registrada` | 1 | 16 | 0 | 117/117 |  |  | ✔ | ✔ | 12/12 (4/4) | ✔ | ✔ |
| Patentes e Registros | `patente` | 1 | 28 | 0 | 129/129 |  |  | ✔ | ✔ | 15/15 (7/7) | ✔ | ✔ |
| Patentes e Registros | `software_registro` | 1 | 30 | 0 | 133/133 |  |  | ✔ | ✔ | 17/17 (6/6) | ✔ | ✔ |
| Patentes e Registros | `topografia_circuito` | 1 | 16 | 0 | 117/117 |  |  | ✔ | ✔ | 12/12 (4/4) | ✔ | ✔ |
| Produções | `anais` | 1 | 29 | 0 | 252/252 |  |  | ✔ | ✔ | 26/26 (4/4) | ✔ | ✔ |
| Produções | `apresentacao` | 1 | 19 | 0 | 212/212 |  |  | legado | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `artes_cenicas` | 1 | 30 | 0 | 272/272 |  |  | ✔ | ✔ | 27/27 (4/4) | ✔ | ✔ |
| Produções | `artes_visuais` | 1 | 24 | 0 | 267/267 |  |  | ✔ | ✔ | 21/21 (4/4) | ✔ | ✔ |
| Produções | `artigo` | 1 | 21 | 0 | 118/118 |  |  | legado | ✔ | 12/12 (4/4) | ✔ | ✔ |
| Produções | `artigo_aceito` | 1 | 15 | 0 | 107/107 |  |  | ✔ | ✘ | 9/9 (4/4) | ✔ | ✔ |
| Produções | `cartas_mapas` | 1 | 19 | 0 | 214/214 |  |  | ✔ | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `curso_ministrado` | 1 | 20 | 0 | 213/213 |  |  | ✔ | ✔ | 17/17 (4/4) | ✔ | ✔ |
| Produções | `editoracao` | 1 | 18 | 0 | 212/212 |  |  | ✔ | ✔ | 15/15 (4/4) | ✔ | ✔ |
| Produções | `entrevista_midia` | 1 | 19 | 0 | 211/211 |  |  | ✔ | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `extensao_tecnologica` | 1 | 19 | 0 | 211/211 |  |  | ✔ | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `livro_capitulo` | 2 | 30 | 0 | 465/465 |  |  | ✔ | ✔ | 42/42 (8/8) | ✔ | ✔ |
| Produções | `manutencao_obra` | 1 | 21 | 0 | 223/223 |  |  | ✔ | ✔ | 18/18 (4/4) | ✔ | ✔ |
| Produções | `maquete` | 1 | 16 | 0 | 201/201 |  |  | ✔ | ✔ | 13/13 (4/4) | ✔ | ✔ |
| Produções | `material_didatico` | 1 | 16 | 0 | 202/202 |  |  | ✔ | ✔ | 13/13 (4/4) | ✔ | ✔ |
| Produções | `musica` | 1 | 31 | 0 | 270/270 |  |  | ✔ | ✔ | 28/28 (4/4) | ✔ | ✔ |
| Produções | `outra_producao_artistica` | 1 | 31 | 0 | 254/254 |  |  | ✔ | ✔ | 28/28 (4/4) | ✔ | ✔ |
| Produções | `outra_producao_bibliografica` | 1 | 19 | 0 | 214/214 |  |  | ✔ | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `outra_producao_tecnica` | 1 | 18 | 0 | 207/207 |  |  | ✔ | ✔ | 15/15 (4/4) | ✔ | ✔ |
| Produções | `partitura_musical` | 1 | 19 | 0 | 216/216 |  |  | ✔ | ✔ | 16/16 (4/4) | ✔ | ✔ |
| Produções | `prefacio_posfacio` | 1 | 25 | 0 | 239/239 |  |  | ✔ | ✔ | 22/22 (4/4) | ✔ | ✔ |
| Produções | `processo_tecnica` | 1 | 20 | 0 | 451/451 |  |  | ✔ | ✔ | 17/17 (4/4) | ✔ | ✔ |
| Produções | `produto` | 1 | 21 | 0 | 218/218 |  |  | ✔ | ✔ | 18/18 (4/4) | ✔ | ✔ |
| Produções | `redes_sociais` | 1 | 15 | 0 | 195/195 |  |  | ✔ | ✔ | 12/12 (4/4) | ✔ | ✔ |
| Produções | `relatorio_pesquisa` | 1 | 16 | 0 | 435/435 |  |  | ✔ | ✔ | 13/13 (4/4) | ✔ | ✔ |
| Produções | `relatorio_tecnico` | 1 | 20 | 0 | 213/213 |  |  | ✔ | ✔ | 17/17 (4/4) | ✔ | ✔ |
| Produções | `software_sem_registro` | 1 | 26 | 0 | 124/124 |  |  | ✔ | ✔ | 14/14 (6/6) | ✔ | ✔ |
| Produções | `texto_jornal_revista` | 1 | 22 | 0 | 224/224 |  |  | ✔ | ✔ | 19/19 (4/4) | ✔ | ✔ |
| Produções | `trabalho_tecnico` | 1 | 20 | 0 | 217/217 |  |  | ✔ | ✔ | 17/17 (4/4) | ✔ | ✔ |
| Produções | `traducao` | 1 | 25 | 0 | 314/314 |  |  | ✔ | ✔ | 22/22 (4/4) | ✔ | ✔ |
| Projetos | `projeto` | 5 | 42 | 0 | 402/402 |  |  | ✔ | ✔ | 112/112 (15/15) | ✔ | ✔ |

## Detalhe das diferenças por item

### `banca` — Participação em bancas de trabalhos de conclusão

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `banca_comissao_julgadora` — Participação em bancas de comissões julgadoras

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `endereco` — Endereço

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais_i`, `f_pais_r`

### `identificacao` — Identificação

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais_nacio`, `f_pais_nasc`, `fpaispassaporte`

### `idioma` — Idiomas

- captura Claude com opções cortadas (`slice(0, 80)`): `F_COD_IDIOMA`

### `outras_informacoes` — Outras informações relevantes

- sem captura do Antigravity

### `texto_inicial` — Texto inicial do Currículo Lattes

- sem captura do Antigravity

### `organizacao_evento` — Organização de eventos, congressos, exposições, feiras e olimpíadas

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `participacao_evento` — Participação em eventos, congressos, exposições, feiras e olimpíadas

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`

### `orientacao_andamento` — Orientações e supervisões em andamento

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `orientacao_concluida` — Orientações e supervisões concluídas

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `cultivar_protegida` — Cultivar protegida

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `cultivar_registrada` — Cultivar registrada

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `desenho_industrial` — Desenho industrial registrado

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `marca_registrada` — Marca registrada

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`

### `patente` — Patente

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `software_registro` — Programa de Computador Registrado

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `topografia_circuito` — Topografia de circuito integrado registrada

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`

### `anais` — Trabalhos publicados em anais de eventos

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `apresentacao` — Apresentação de trabalho e palestra

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `artes_cenicas` — Artes cênicas

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `artes_visuais` — Artes visuais

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `artigo` — Artigos completos publicados em periódicos

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`

### `artigo_aceito` — Artigos aceitos para publicação

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`

### `cartas_mapas` — Cartas, mapas ou similares

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `curso_ministrado` — Curso de curta duração ministrado

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `editoracao` — Editoração

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `entrevista_midia` — Entrevistas, mesas redondas, programas e comentários na mídia

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `extensao_tecnologica` — Extensão tecnológica

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`
- sem captura do Antigravity

### `livro_capitulo` — Livros e capítulos

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `manutencao_obra` — Manutenção de obra artística

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `maquete` — Maquete

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `material_didatico` — Desenvolvimento de material didático ou instrucional

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `musica` — Música

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `outra_producao_artistica` — Outra produção artística/cultural

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `outra_producao_bibliografica` — Outra produção bibliográfica

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `outra_producao_tecnica` — Outra produção técnica

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `partitura_musical` — Partitura musical

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `prefacio_posfacio` — Prefácio, posfácio

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `processo_tecnica` — Processos ou técnicas

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `produto` — Produtos

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `redes_sociais` — Redes sociais, websites e blogs

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `relatorio_pesquisa` — Relatório de pesquisa

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `relatorio_tecnico` — Assessoria e consultoria

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `software_sem_registro` — Programa de computador sem registro

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais`, `f_pais_inst`

### `texto_jornal_revista` — Texto em jornal ou revista (magazine)

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `trabalho_tecnico` — Trabalhos técnicos

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `f_pais`

### `traducao` — Tradução

- captura Claude com opções cortadas (`slice(0, 80)`): `F_IDIOMA`, `F_IDIOMA_OBRA`, `f_pais`

### `projeto` — Outros tipos de projetos

- captura Claude com opções cortadas (`slice(0, 80)`): `f_pais_inst`
- sem captura do Antigravity

## Formulários mapeados sem spec

- `areas_atuacao`: Áreas de atuação (GN_AREA_ATU): grade editável com árvore de áreas, sem spec
- `atuacao_atividades`: Atividades de atuação (pkg_ativ.cargo): subformulário interno de instituição já cadastrada (Nível 3)
- `linhas_de_pesquisa`: Linhas de pesquisa: não tem formulário próprio; entra por Atuação > Atividades > Pesquisa e desenvolvimento
