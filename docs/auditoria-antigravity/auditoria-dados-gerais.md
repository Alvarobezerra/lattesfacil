# Auditoria Completa — Aba Dados Gerais (7 Subitens: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todos os **7 subitens** da aba **Dados gerais** da Plataforma Lattes (`Identificação`, `Endereço`, `Licenças`, `Idiomas`, `Prêmios e títulos`, `Texto inicial do Currículo Lattes`, `Outras informações relevantes`).
- **Objetivo:** Documentar 100% da dinâmica de campos, handlers JS, inputs `hidden`, grades, modais e regras de salvamento/exclusão para garantir preenchimento externo (autofill) sem falhas.

---

## 1. Resumo Executivo dos 7 Subitens

| # | Subitem | Endpoint (`form[name]`) | Abertura Real | Salvar + Reabrir + Excluir (F7) | Divergências Críticas no Spec (`itens/especificacao/`) |
| --- | --- | --- | --- | --- | --- |
| 1 | **Identificação** | `prc_ident?f_pcd=X` (`GN_IDENT`) | Direta (registro único) | Inspecionado s/ alterar titular (13 hidden inputs + grade `#holderDetNmeCit` via tecla `Enter`) | Falta grade `Nome em citações`; rótulos crus (`f_nome_social_r`, `f_sexo`, `f_pcd_r`, `f_pcd`); campos de passaporte marcados `obrigatorio: true` fixo |
| 2 | **Endereço** | `prc_endereco?modal2=1` (`GN_ENDERECO`) | Direta (registro único) | Inspecionado s/ alterar titular (22 hidden inputs + `getZipData` + 2 grades modais `.win-wrapper`) | Faltam as 2 grades (`Outra forma de contato` e `Redes Sociais`); `f_inst` e `f_orgao` mapeados como texto simples em vez de lupas (`sele_inst()`/`orgao()`); rótulo errado `"Não sei meu CEP"` em `f_cep_r`/`f_cep_i` |
| 3 | **Licenças** | `pkg_licenca.lista` → `pkg_licenca.form` | Lista (`Incluir novo item`) | ✔ **Salvo, reaberto (100%) e excluído (0 itens)** | Spec marca `"obrigatorio": false` nos 4 campos (todos os 4 são obrigatórios no Lattes); `f_dta_inicio` está com rótulo errado `"Data Fim"`; falta regra dinâmica de `#labelDataAdNasc` e `#periodoLicenca` |
| 4 | **Idiomas** | `pkg_idioma.lista` → `pkg_idioma.form` (`GN_IDIOMA`) | Lista (`Incluir novo item`) | ✔ **Salvo (`Esperanto`), reaberto (100%) e excluído (3 originais intactos)** | Rádios `F_LE`, `F_CONVERSA`, `F_ESCREVE`, `F_COMPR` têm **`value=""`** no DOM real (funcionam por índice `0, 1, 2` e handlers `rd_*()` / `ch_*()`, não por `"P"`, `"R"`, `"B"`); falta condicional `Libras (LB)` (`veriLibra`) |
| 5 | **Prêmios e títulos** | `pkg_premio.lista` → `pkg_premio.form` | Lista (`Incluir novo item`) | ✔ **Salvo, reaberto (100%) e excluído (1 original intacto)** | `abertura` marcada como `"direta"` em vez de lista (`pkg_premio.lista` exige clicar `Incluir novo item` quando já há prêmios) |
| 6 | **Texto inicial** | `pkg_resume.form` (`RES`) | Direta (registro único) | Registro único (`F_TEXTO` e `F_TEXTO_EN`, max `4000`) | Botão auxiliar `"Utilizar o Texto Padrão"` não documentado na curadoria |
| 7 | **Outras informações** | `prc_outras_inf` (`GN_OUTRA_INF_RELEV`) | Direta (registro único) | Registro único (`F_TEXTO`, max `2000`) | Rótulo truncado em 90 caracteres no spec |

---

## 2. Dinâmica Detalhada por Formulário (Para o Robô de Preenchimento Externo)

### 2.1 Identificação (`prc_ident?f_pcd=X` — `form[name="GN_IDENT"]`)
- **Hidden inputs (`13` no form principal `GN_IDENT`):**
  `f_dados_grid`, `f_nome_citacao`, `f_nome_citacao_h`, `fdados_new`, `f_nacionalidade`, `f_cpf`, `f_nome_pai`, `f_nome_mae`, `f_pcd`, `#UrlNovaRede`, `f_ctr`, `f_cod`, `f_nme_old`.
- **Regras condicionais e eventos JS:**
  - **Nome social (`f_nome_social_r`):** rádio `S` revela `tr#NomeSocial` (`input[name="f_nome_social"]`, `maxlength="60"`, passa a ser obrigatório); `N` oculta.
  - **Nacionalidade e Nascimento:**
    - `select[name="f_pais_nacio"]` (`id="sPNacio"`, `onchange="altNacio(this.value)"`).
    - `select[name="f_pais_nasc"]` (`onchange="checkpais();"`): ao trocar de `BRA` para outro país, limpa `select[name="f_uf_nasc"]` para `""`.
    - `select[name="f_uf_nasc"]` (`onchange="checkufnasc();"`).
  - **Pessoa com Deficiência (`f_pcd_r`):** rádio `S` revela `tr#listaPCD` contendo os 6 checkboxes `input[type="checkbox"][name="f_pcd"]` com valores:
    - `A` (`Deficiência Auditiva`), `F` (`Deficiência Física`), `I` (`Deficiência Intelectual`), `V` (`Deficiência Visual`), `E` (`Transtorno do Espectro Autista`), `M` (`Deficiência Múltipla`).
- **Grade `Nome em citações bibliográficas` (`#holderDetNmeCit`):**
  - Campo de entrada: `<input id="nmeCitacao" type="text" maxlength="255">` (`name=null`).
  - **Como adicionar:** não há botão `Adicionar` com `onclick`; um listener jQuery escuta a tecla **`Enter`** (`keydown`/`keypress` `keyCode === 13`) em `#nmeCitacao`. Ao pressionar `Enter`:
    1. Incrementa o contador `#totNmeCit` (`"Total de nomes em citação N"`).
    2. Insere uma `<tr class="odd hover">` em `#holderDetNmeCit tbody` com o texto na 1ª coluna (`95%`) e `<img src="/images/estatico/img/trash.png" title="clique para excluir">` na 2ª coluna (`5%`).
    3. *Nota:* a 1ª linha principal do currículo (`SANTOS, A. A. B.`) não possui ícone `trash.png`.

---

### 2.2 Endereço (`prc_endereco?modal2=1` — `form[name="GN_ENDERECO"]`)
- **Hidden inputs (`22` em `GN_ENDERECO`):**
  `modal2`, `f_dados_grid`, `f_dados_grid_contatos`, `f_cidade_r`, `f_cidade_i`, `f_ctr`, `f_origem`, `f_cod`, `f_cod_inst`, `f_cod_inst2`, `f_codorgao`, `f_codorgao2`, `f_inst_old`, `f_orgao_old`, `f_cod_munic_r`, `f_cod_munic_i`, `f_munic_r_old`, `f_munic_i_old`, `f_estado_r_old`, `f_estado_i_old`, `f_pais_r_old`, `f_pais_i_old`.
- **Auto-preenchimento por CEP (`formataCep` + `getZipData`):**
  - Residencial: `input[name="f_cep_r"]` (`onkeyup="formataCep(this,'R')"`, `onblur="getZipData(this.value,'R')"`).
  - Profissional: `input[name="f_cep_i"]` (`onkeyup="formataCep(this,'I')"`, `onblur="getZipData(this.value,'I')"`).
  - Ao digitar um CEP válido (ex.: `01001-000`) e disparar `blur`/`Tab`, `getZipData` preenche automaticamente `f_rua_r/i`, `f_bairro_r/i`, `f_munic_r/i` e `f_estado_r/i`.
- **Lupas do Endereço Profissional (`sele_inst()` e `orgao()`):**
  - `f_inst` e `f_orgao` são `<input type="text" disabled>` (não aceitam digitação direta).
  - `sele_inst()` abre a lupa de instituição e preenche `f_inst` + hidden `f_cod_inst` / `f_cod_inst2`.
  - `orgao()` abre `prc_orgao_cargo?f_cod=<cod>&f_cod_inst=<f_cod_inst>` em modal filho (`iframe`) — permite consultar ou cadastrar novo órgão e preenche `f_orgao` + hidden `f_codorgao` / `f_codorgao2`.
- **Grades Dinâmicas via Modal Top-Level (`.win-wrapper`):**
  1. **Outra forma de contato (`#holderContatos` → hidden `f_dados_grid_contatos`):**
     - Clicar em `<a href="#">Inserir nova</a>` dentro de `#holderContatos` abre modal `.win-wrapper` (`"Outra forma de contato"`):
       - `<select id="idNovacontato">` (`name=null`): `7` = `Telegram`, `3` = `MSN`, `6` = `WhatsApp`.
       - `<input id="enderecoNovaRede" type="text">` (`name=null`).
       - Visibilidade (`.ms-dd`): `Público` / `Privado`.
       - Botão `Confirmar` (`.botao.salvar a`): insere linha em `#holderContatos` e serializa em `input[name="f_dados_grid_contatos"]`.
  2. **Redes Sociais (`#holder` → hidden `f_dados_grid`):**
     - Clicar em `<a href="#">Inserir nova</a>` dentro de `#holder` abre modal `.win-wrapper` (`"Redes Sociais"`):
       - `<select id="idNovaRedeSocial">` (`name=null`): `1` = `Facebook`, `2` = `Linkedin`, `3` = `X(Twitter)`, `6` = `Academia.edu`, `8` = `Instagram`, `9` = `Threads`, `10` = `ResearchGate`, `11` = `Mendeley`, `12` = `Youtube`, `13` = `TikTok`, `14` = `Bluesky`, `15` = `GitHub`.
       - `<input id="enderecoNovaRede" type="text">` (`name=null`).
       - Visibilidade (`.ms-dd`): `Público` / `Privado`.
       - Botão `Confirmar` (`.botao.salvar a`): insere linha em `#holder` e serializa em `input[name="f_dados_grid"]`.

---

### 2.3 Licenças (`pkg_licenca.lista` → `pkg_licenca.form`)
- **Abertura:** `pkg_licenca.lista` **não** abre o formulário automaticamente quando vazia (`0` itens); exige clicar em `Incluir novo item`.
- **Campos (todos os 4 são obrigatórios no `check()`):**
  - `select[name="f_tipo_licenca"]`: `""`, `M` (`Maternidade`), `P` (`Paternidade`), `A` (`Adoção`).
  - `input[name="f_dta_inicio"]` (`DD/MM/YYYY`, `maxlength="10"`).
  - `input[name="f_dta_fim"]` (`DD/MM/YYYY`, `maxlength="10"`).
  - `input[name="f_dta_nasc_adoc"]` (`DD/MM/YYYY`, `maxlength="10"`).
- **Dinâmica JS:**
  - `f_tipo_licenca` altera `#labelDataAdNasc` para `"Data de nascimento"` (`M` ou `P`) ou `"Data de adoção"` (`A`).
  - Preencher `f_dta_inicio` e `f_dta_fim` dispara `calculaPeriodo()` e exibe `"N dias"` em `#periodoLicenca`.
  - Visibilidade padrão é **`Privado`**.
- **Exclusão:** `del();return false;` executa **exclusão imediata** sem `confirm()` nem modal.

---

### 2.4 Idiomas (`pkg_idioma.lista` → `pkg_idioma.form`)
- **Abertura:** `pkg_idioma.lista` → clicar em `Incluir novo item`.
- **Mecânica crítica para o robô de autofill:**
  - `<select name="F_COD_IDIOMA" onchange="veriLibra(this)">` (`150` opções).
  - Os 4 checkboxes (`FC_LE`, `FC_CONVERSA`, `FC_ESCREVE`, `FC_COMPR`) e os 12 rádios (`F_LE[0..2]`, `F_CONVERSA[0..2]`, `F_ESCREVE[0..2]`, `F_COMPR[0..2]`) têm **`value=""`** e **`id=null`**!
  - **Como o robô deve preencher cada habilidade (`Pouco = índice 0`, `Razoavelmente = índice 1`, `Bem = índice 2`):**
    - Basta clicar diretamente no rádio pelo índice (`document.getElementsByName("F_LE")[indice].click()`): o handler inline (`rd_le()`, `rd_cv()`, `rd_es()`, `rd_co()`) **marca automaticamente o checkbox correspondente (`FC_* = true`)**!
    - Se uma habilidade não deve ser marcada, garantir que o checkbox `FC_*` esteja desmarcado (clicar em um `FC_*` marcado chama `ch_*()` e limpa os 3 rádios).
  - **Condicional `Libras` (`F_COD_IDIOMA === "LB"`):** `veriLibra(this)` remove do DOM as linhas `FC_LE`/`F_LE` (`Lê`) e `FC_ESCREVE`/`F_ESCREVE` (`Escreve`), mantendo apenas `FC_CONVERSA`/`F_CONVERSA` (renomeado para **`Expressa-se`**) e `FC_COMPR`/`F_COMPR` (**`Compreende`**).
- **Exclusão:** `.botao.excluir a` executa **exclusão imediata** sem `confirm()` nem modal.

---

### 2.5 Prêmios e títulos (`pkg_premio.lista` → `pkg_premio.form`)
- **Abertura:** `pkg_premio.lista` → clicar em `Incluir novo item`.
- **Campos (todos texto livre, sem lupas):**
  - `input[name="f_titulo"]` (`Nome do prêmio ou título`, `maxlength="200"`, obrigatório).
  - `input[name="f_agencia"]` (`Entidade promotora`, `maxlength="100"`, obrigatório no `check()`).
  - `input[name="f_ano"]` (`Ano da premiação ou do título`, `maxlength="4"`, obrigatório).
  - Visibilidade padrão: `Público`.
- **Exclusão:** `del();return false;` executa **exclusão imediata** sem `confirm()` nem modal.

---

### 2.6 Texto inicial (`pkg_resume.form`) e Outras informações (`prc_outras_inf`)
- **Texto inicial (`pkg_resume.form`, `form[name="RES"]`):**
  - `textarea[name="F_TEXTO"]` (`Texto Inicial`, `maxlength="4000"`, botão auxiliar `"Utilizar o Texto Padrão"`).
  - `textarea[name="F_TEXTO_EN"]` (`Tradução`, `maxlength="4000"`, botão auxiliar `"Utilizar o Texto Padrão"`).
  - Sem seletor de visibilidade.
- **Outras informações relevantes (`prc_outras_inf`, `form[name="GN_OUTRA_INF_RELEV"]`):**
  - `textarea[name="F_TEXTO"]` (`maxlength="2000"`).
  - Sem seletor de visibilidade; botão `Excluir` (`del()`) limpa o texto cadastrado.
