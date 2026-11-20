# Auditoria Completa — Barra Vertical Lateral Esquerda ("Menu Secundário" — 10 Ícones)

- **Data:** 2026-11-20
- **Escopo:** Todos os **10 ícones** da barra vertical azul à esquerda (`<div class="menu">`) em `PKG_MENU.menu`, ordenados de cima para baixo (`#1` a `#10`).
- **Modo de inspeção:** 100% somente leitura / não-destrutivo (nenhum registro do currículo foi alterado).

---

## 1. Visão Geral dos 10 Ícones (De Cima para Baixo)

| # | Ícone Visual | Classe CSS (`tabindex`) | Título Oficial (`title`) | Endpoint Principal (`modalCV1` / `modalCV2`) | Função na Plataforma Lattes |
| --- | --- | --- | --- | --- | --- |
| **1** | Crachá c/ pessoa e grade | `menuLateral_autores` (`201`) | `Menu secundário - Autores citados no currículo` | `pkg_dic_autor.lista` → `pkg_dic_autor.form?f_seq=<seq>` | Dicionário global de autores/coautores do CV (`50` registros atuais); alimenta o modal `Listar todos` de `Autores` |
| **2** | Crachá c/ lupa | `menuLateral_identificar` (`202`) | `Menu secundário - Identificar co-autor` | `pkg_identificacao_coautor.form?f_check=ID` | Busca um pesquisador na Base Lattes do CNPq e vincula o ID Lattes oficial dele às variantes de nome do dicionário de autores |
| **3** | Letra `A` c/ lupa | `menuLateral_palavras` (`203`) | `Menu secundário - Palavras-chaves citadas no currículo` | `pkg_dic_plv_nv.lista` → `PKG_DIC_PLV_NV.form?f_seq=<seq>` | Dicionário global de palavras-chave do CV (`24` registros atuais); permite editar/unificar ou excluir palavras-chave |
| **4** | Silhueta de cabeça/cérebro | `menuLateral_areas` (`204`) | `Menu secundário - Áreas citadas no currículo` | `pkg_dic_area.lista` → `pkg_dic_area.form?f_codarea=<cod>` | Dicionário de subáreas/especialidades customizadas do CV (`3` registros atuais), permitindo editar nome e tradução em inglês |
| **5** | Prédio c/ colunas | `menuLateral_instituicoes` (`205`) | `Menu secundário - Instituições citadas no currículo` | `pkg_dic_instituicao_nova.lista` → `PKG_DIC_INSTITUICAO_NOVA.form?f_cod_inst_outra=<cod>` | Dicionário de instituições cadastradas manualmente pelo usuário (`17` registros atuais), permitindo editar Nome, Sigla e País |
| **6** | Folha c/ elo de corrente | `menuLateral_vincular` (`206`) | `Menu secundário - Vincular artigo ao periódico` | `pkg_alteracao_periodico.lista` → `pkg_alteracao_periodico.form?f_check=PER&f_seq_per=<seq>` | Permite reassociar artigos publicados a periódicos oficiais da base CAPES/ISSN |
| **7** | Duas folhas sobrepostas | `<span class="menuLateral_importacao">` *(sem `<a>`)* | *(Sem `title` — desativado no DOM)* | *(Sem `href` e sem `onclick`)* | **Ícone inativo no HTML atual do Lattes** (antiga função de importação de produção de coautor, renderizada hoje como `<span>` não-clicável) |
| **8** | Olho | `menuLateral_impressao` (`209`) | `Menu secundário - Gerar arquivo para visualização e conferência` | `pkg_impcv.form` → `POST pkg_impcv.trata` | Configura e gera a versão de impressão/conferência do currículo (`36` checkboxes de seções + modelo/estilo/idioma/ABNT); o `POST pkg_impcv.trata` está retornando **HTTP 404** no servidor do CNPq |
| **9** | Folha c/ seta saindo (`→`) | `menuLateral_exportar` (`210`) | `Menu secundário - Exportar` | `pkg_impcv.get_arquivo` | Exportação do currículo em XML/ZIP; atualmente o servidor do CNPq responde **HTTP 200 `text/html`** devolvendo o próprio `PKG_MENU.menu` sem download |
| **10** | Folha c/ seta entrando (`→`) | `menuLateral_importar` (`211`) | `Menu secundário - Importar` | `pkg_importa_xml.inicio` | Importação de arquivo `.xml` (compatível com a `LMPLCurriculo.DTD`) para dentro do Currículo Lattes |

---

## 2. Detalhamento Técnico de Cada Seção (Campos, Hidden Inputs e Fluxos)

### #1. Autores citados no currículo (`pkg_dic_autor.lista` → `pkg_dic_autor.form`)
- **Lista (`modalCV1` — `pkg_dic_autor.lista`):**
  - `<form action="PKG_DIC_AUTOR.DEL" name="GN_AUTOR">` com **3 hidden inputs**: `f_plv`, `f_ctr`, `f_cod`.
  - Tabela `#lista.ext` (**50 autores** no currículo atual): colunas `#`, `Nome do autor`, `Nome em citações`, `Produção` (contador de produções vinculadas), `Projeto` (contador de projetos vinculados).
  - Clicar em uma linha dispara `onclick="pp_autor(<seq>)"`, abrindo o submodal em `modalCV2`.
- **Submodal de Edição (`modalCV2` — `pkg_dic_autor.form?f_cod=...&f_seq=<seq>`):**
  - **12 hidden inputs:** `f_cod`, `f_seq`, `f_tipo`, `f_ctr`, `f_id`, `f_sta_old`, `f_cod_chk`, `f_seq_chk`, `start`, `finish`, `status`, `f_nme_orientado`.
  - **Campos visíveis:**
    1. `<input type="text">`: `Nome completo ou apelido (para seu uso) do autor`
    2. `<input type="text">`: `Nome como citado`
    3. `<input type="checkbox">`: `Autorizo este autor a importar produções do meu Currículo Lattes`
  - **Botões:** `Salvar` e `Excluir`.

### #2. Identificar co-autor (`pkg_identificacao_coautor.form?f_check=ID`)
- **Form (`modalCV2` — `<form method="POST" action="PKG_IDENTIFICACAO_COAUTOR.FORM" name="GN_ARTIGO">`):**
  - **6 hidden inputs:** `f_check`, `f_ctr`, `f_cod`, `f_cod_coa`, `f_id`, `f_lista_ident`.
  - **Estrutura em 2 passos na mesma tela:**
    1. `1. Localize o co-autor na Base Lattes`: `<input type="text">` (`Nome do Co-autor`) + lupa de busca na base do CNPq.
    2. `2. Selecione o(s) co-autores que deseja vincular ao co-autor acima`: tabela listando os **50 autores** do currículo com checkboxes de seleção, `Nome` e `Nome em Citação Bibliográfica`.
  - **Botão:** `Salvar`.

### #3. Palavras-chaves citadas no currículo (`pkg_dic_plv_nv.lista` → `PKG_DIC_PLV_NV.form`)
- **Lista (`modalCV1` — `pkg_dic_plv_nv.lista`):**
  - 2 forms: `GN_PLV` (`action="PKG_DIC_PLV_NV.DEL"`, hidden: `f_plv`, `f_ctr`, `f_cod`) e `GN_EDIT` (`action="PKG_DIC_PLV_NV.EDITAR"`, hidden: `F_COD`, `f_seq`, `f_nome`).
  - Tabela `#lista.ext` (**24 palavras-chave** no currículo atual): colunas `#`, `Palavra-chave`, `Produções`. Clicar dispara `pp_plv(<seq>)`.
- **Submodal de Edição (`modalCV2` — `PKG_DIC_PLV_NV.form?f_cod=...&f_seq=<seq>`):**
  - `<form method="POST" action="PKG_DIC_PLV.FORM" name="GN_PLV">` com **3 hidden inputs**: `f_cod`, `f_ctr`, `f_seq`.
  - **Campo visível:** `1` `<input type="text">` (`Palavra-chave`) + botões `Salvar` e `Excluir`.

### #4. Áreas citadas no currículo (`pkg_dic_area.lista` → `pkg_dic_area.form`)
- **Lista (`modalCV1` — `pkg_dic_area.lista`):**
  - `<form action="pkg_dic_area.DEL" name="pkg_dic_area">` com **3 hidden inputs**: `f_ctr`, `f_cod`, `f_plv`.
  - Tabela `#lista.ext` (**3 áreas** no currículo atual): colunas `#`, `Áreas do conhecimento`, `Tradução`, `Produção`. Clicar dispara `pp_area(<codarea>)`.
- **Submodal de Edição (`modalCV2` — `pkg_dic_area.form?f_cod=...&f_codarea=<codarea>`):**
  - `<form method="post" action="PKG_DIC_AREA.FORM" name="area">` com **3 hidden inputs**: `f_cod`, `f_ctr`, `f_codarea`.
  - Exibe a árvore pai (`Grande Área > Área > Subárea`) e **2 `<input type="text">`**: `Áreas do conhecimento` e `Tradução` + botões `Salvar` e `Excluir`.

### #5. Instituições citadas no currículo (`pkg_dic_instituicao_nova.lista` → `PKG_DIC_INSTITUICAO_NOVA.form`)
- **Lista (`modalCV1` — `pkg_dic_instituicao_nova.lista`):**
  - `<form action="PKG_DIC_INSTITUICAO_NOVA.DEL" name="GN_INST">` com **3 hidden inputs**: `f_plv`, `f_ctr`, `f_cod`.
  - Tabela `#lista.ext` (**17 instituições** cadastradas pelo usuário): colunas `#`, `Nome da Instituição`, `Sigla`.
- **Submodal de Edição (`modalCV2` — `PKG_DIC_INSTITUICAO_NOVA.form?f_cod=...&f_cod_inst_outra=<cod>`):**
  - `<form action="PKG_DIC_INSTITUICAO_NOVA.FORM" name="GN_INST">` com **3 hidden inputs**: `f_cod`, `f_cod_inst_outra`, `f_ctr`.
  - **Campos visíveis:** `2` `<input type="text">` (`Nome da Instituição`, `Sigla da Instituição`) + `1` `<select>` (`País`, `245` opções) + botões `Salvar` e `Excluir`.

### #6. Vincular artigo ao periódico (`pkg_alteracao_periodico.lista` → `pkg_alteracao_periodico.form`)
- **Lista (`modalCV1` — `pkg_alteracao_periodico.lista`):**
  - `<form method="post" action="PKG_ALTERACAO_PERIODICO.LISTA" name="periodico">` (`0` hidden inputs).
  - Lista periódicos e títulos de artigos que podem ser vinculados à tabela oficial de periódicos da CAPES.
- **Submodal (`modalCV2` — `pkg_alteracao_periodico.form?f_check=PER&f_cod=...&f_seq_per=<seq>`):**
  - `<form method="POST" action="PKG_ALTERACAO_PERIODICO.FORM" name="GN_ARTIGO">` com **11 hidden inputs**: `f_check`, `f_titulo_periodico_h`, `f_issn_h`, `f_volume`, `f_serie`, `f_pag_ini`, `f_pag_fim`, `f_ctr`, `f_cod`, `f_seq`, `f_seq_per`.
  - **Campos visíveis:** `Título do periódico/revista`, `ISSN`, tabela de seleção dos artigos daquele periódico (checkbox, `Título`, `Ano`) e botão `Salvar`.

### #7. Ícone `menuLateral_importacao` (Inativo no DOM)
- Renderizado como `<span class="menuLateral_importacao"></span>` (dimensões `50x45px`), sem tag `<a>`, sem `title` e sem handler `onclick`. Funciona apenas como ícone inativo/separador entre os 6 dicionários de curadoria (`#1`–`#6`) e as 3 ferramentas de documento (`#8`–`#10`).

### #8. Gerar arquivo para visualização e conferência (`pkg_impcv.form` → `pkg_impcv.trata`)
- **Form (`modalCV1` — `<form action="pkg_impcv.trata" name="GN_IMP" method="POST">`):**
  - **5 hidden inputs:** `f_cod`, `f_check`, `f_ctr`, `f_fmt`, `f_tpo_arq`.
  - **60 controles visíveis:**
    - **Coluna esquerda (`36` checkboxes `name="f_check"`):** permite marcar/desmarcar quais das 35 seções do currículo entrarão na visualização (`Selecionar todos` + 35 seções).
    - **Coluna direita (`14` rádios, `8` checkboxes, `2` inputs de ano):** `Modelo de currículo` (`Resumido`, `Ampliado`, `Completo`, `Personalizado`), `Estilo` (`Com cores` / `Sem cores`), `Idioma` (`Português` / `Inglês`), `Padrão de referência` (`ABNT` / `Chicago`), `Indexador`, `Período da atuação profissional`, `Produção` e `Período da produção`.
  - **Botão `Confirmar`:** submete `POST /cvlattesweb/pkg_impcv.trata` em nova janela (atualmente retornando **HTTP 404 Not Found** no servidor do CNPq).

### #9. Exportar (`pkg_impcv.get_arquivo`)
- Chama `modalCV1.setarUrl('pkg_impcv.get_arquivo?f_cod=K4298460T6', true)`.
- Atualmente o servidor do CNPq responde **`HTTP 200 OK` (`text/html`, `201.966` bytes)** devolvendo o HTML do próprio `PKG_MENU.menu` e fechando o modal sem iniciar download de `.zip`/`.xml`.

### #10. Importar (`pkg_importa_xml.inicio`)
- **Form (`modalCV1` — `<form action="pkg_importa_xml.inicio" method="POST" enctype="multipart/form-data" name="fl">`):**
  - **3 hidden inputs:** `f_cod`, `f_ctr`, `f_ret`.
  - **Controles:** link para download da `DTD` oficial do Currículo Lattes, `<input type="file">` (`Escolher arquivo`) e `<input type="submit" value="Enviar">`.
