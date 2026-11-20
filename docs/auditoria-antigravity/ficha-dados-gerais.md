# Ficha de validação — Dados Gerais (`Prêmios e títulos`, `Licença` e `Idiomas`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `pkg_premio.lista` → `pkg_premio.form` · `pkg_licenca.lista` → `pkg_licenca.form` · `pkg_idioma.lista` → `pkg_idioma.form`
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO NOS 3 ITENS DE LISTA DE DADOS GERAIS**

---

## 1. Prêmios e títulos (`pkg_premio.lista` → `pkg_premio.form`)

### 1.1 F4/F5 — Campos reais e preenchimento testado
Ao clicar em **Incluir novo item** (mantendo intacto o `1` item original do usuário):
- Não há lupa `escolhe_inst()` nem `f_nme_prem`; todos os 3 campos são texto livre (`<input type="text">`):
  - `f_titulo` (`Nome do prêmio ou título`, `maxlength="200"`): `[ZZ-TESTE-ANTIGRAVITY] Premio Teste`
  - `f_agencia` (`Entidade promotora`, `maxlength="100"`, sem lupa): `CNPq`
  - `f_ano` (`Ano da premiação ou do título`, `maxlength="4"`): `2025`
  - Visibilidade (`.ms-dd`): `Público` (padrão)

### 1.2 F7 — Salvamento, Reabertura Persistida e Exclusão
- **Salvamento:** `check();return false;` exibiu `.caixaMsg` `"Sucesso / A operação foi realizada com sucesso! !"` e listou `2` itens.
- **Reabertura persistida (F5):** Reaberto apenas o item `[ZZ-TESTE-ANTIGRAVITY] Premio Teste`; **100% dos campos retornaram exatamente iguais** (`f_titulo`, `f_agencia`, `f_ano`, `visibilidade="Público"`).
- **Exclusão:** Clicar em **Excluir** (`del();return false;`) executou **exclusão imediata** (sem `confirm()` nativo e sem modal `.caixaMsg` de confirmação), exibindo diretamente `"Sucesso / A operação foi realizada com sucesso! !"`.
- **Listagem final verificada:** **`1` item** (apenas o item original `PRÊMIO JÚLIA LIMA · Hospital Israelita Albert Einstein · 2019` preservado intacto).

---

## 2. Licença (`pkg_licenca.lista` → `pkg_licenca.form`)

### 2.1 F4/F5 — Campos reais e regras condicionais
Ao clicar em **Incluir novo item** (`pkg_licenca.lista` com `0` itens):
- `pkg_licenca.form` não possui campos de texto livre, título, motivo, instituição ou país — apenas `Tipo`, 3 datas (`DD/MM/YYYY`, `hasDatepicker`) e `Visibilidade` (padrão **`Privado`**).
- Campos preenchidos:
  - `f_tipo_licenca` (`<select>`, opções `""`, `M`, `P`, `A`): `P` (`Paternidade`)
  - `f_dta_inicio` (`Data Início`): `01/03/2023`
  - `f_dta_fim` (`Data Fim`): `20/03/2023`
  - `f_dta_nasc_adoc` (`Data de nascimento/adoção`): `01/03/2023`
  - Visibilidade: `Privado` (padrão)
- **Comportamentos dinâmicos observados:**
  - Selecionar `f_tipo_licenca = "P"` alterou dinamicamente `#labelDataAdNasc` de `"Data de nascimento/adoção"` para **`"Data de nascimento"`**.
  - Preencher `f_dta_inicio` + `f_dta_fim` disparou `calculaPeriodo()` e calculou `#periodoLicenca` = **`"20 dias"`**.

### 2.2 F7 — Salvamento, Reabertura Persistida e Exclusão
- **Salvamento:** `check();return false;` exibiu `"Sucesso / A operação foi realizada com sucesso! !"` e listou `1` item: `1 · Paternidade · 01/03/2023 · 20/03/2023 · 01/03/2023 · 20 dias` (`Privado`).
- **Reabertura persistida (F5):** Reaberto (`pkg_licenca.form?f_cod=K4298460T6&f_seq=1`); **100% dos campos e rótulos calculados retornaram iguais** (`f_tipo_licenca="P"`, datas, `labelDataAdNasc="Data de nascimento"`, `periodoLicenca="20 dias"`, `visibilidade="Privado"`).
- **Exclusão:** Clicar em **Excluir** (`del();return false;`) executou **exclusão imediata** (sem `confirm()` nativo e sem modal `.caixaMsg` de confirmação).
- **Listagem final verificada:** **`0` itens** (ambiente 100% limpo).

---

## 3. Idiomas (`pkg_idioma.lista` → `pkg_idioma.form`)

### 3.1 F4/F5 — Mecânica real dos checkboxes/rádios e regra de `Libras (LB)`
Ao clicar em **Incluir novo item** (preservando intactos os `3` idiomas originais do titular: `Espanhol`, `Inglês` e `Português`):
- **Descoberta crítica para o preenchimento externo (autofill):**
  - Todos os 4 checkboxes (`FC_LE`, `FC_CONVERSA`, `FC_ESCREVE`, `FC_COMPR`) e todos os 12 rádios (`F_LE[0..2]`, `F_CONVERSA[0..2]`, `F_ESCREVE[0..2]`, `F_COMPR[0..2]`) têm **`value=""`** e **`id=null`** no DOM real do Lattes!
  - Diferente do que assume `itens/especificacao/idioma.json` (`"P"`, `"R"`, `"B"`), os rádios são diferenciados **pelo índice (`0 = Pouco`, `1 = Razoavelmente`, `2 = Bem`)** e sincronizados por funções inline:
    - Checkboxes: `FC_LE` (`onclick="ch_le()"`), `FC_CONVERSA` (`onclick="ch_cv()"`), `FC_ESCREVE` (`onclick="ch_es()"`), `FC_COMPR` (`onclick="ch_co()"`).
    - Rádios: `F_LE` (`onclick="rd_le()"`), `F_CONVERSA` (`onclick="rd_cv()"`), `F_ESCREVE` (`onclick="rd_es()"`), `F_COMPR` (`onclick="rd_co()"`).
  - **Comportamento dos handlers JS:**
    - Os rádios **nunca ficam `disabled`** (`disabled: false` mesmo com o checkbox desmarcado).
    - Clicar no checkbox para **marcar** (`FC_LE.click()`) marca o checkbox e **auto-seleciona o rádio índice `1` (`Razoavelmente`)**.
    - Clicar no checkbox para **desmarcar** (`FC_LE.click()`) desmarca o checkbox e **limpa todos os 3 rádios (`[false, false, false]`)**.
    - Clicar diretamente em um rádio (`F_CONVERSA[1].click()`, via `rd_cv()`) **auto-marca o checkbox correspondente (`FC_CONVERSA = true`)**.
- **Regra condicional de `Libras` (`F_COD_IDIOMA = "LB"`, `onchange="veriLibra(this)"`):**
  - Substitui a tabela de 4 linhas (`Lê`, `Fala`, `Escreve`, `Compreende`) por uma tabela de apenas **2 linhas**:
    1. `FC_CONVERSA` (`onclick="ch_cv()"`) com rótulo alterado para **`Expressa-se`** + 3 rádios `F_CONVERSA` (`Pouco`, `Razoavelmente`, `Bem`).
    2. `FC_COMPR` (`onclick="ch_co()"`) com rótulo **`Compreende`** + 3 rádios `F_COMPR` (`Pouco`, `Razoavelmente`, `Bem`).
  - `FC_LE`/`F_LE` (`Lê`) e `FC_ESCREVE`/`F_ESCREVE` (`Escreve`) são **removidos do DOM**.

### 3.2 F7 — Salvamento, Reabertura Persistida e Exclusão (`Esperanto` / `EO`)
- **Preenchimento de teste:** `F_COD_IDIOMA="EO"` (`Esperanto`), `FC_LE=true` (`F_LE[0]` = `Pouco`), `FC_CONVERSA=true` (`F_CONVERSA[1]` = `Razoavelmente`), `FC_ESCREVE=true` (`F_ESCREVE[2]` = `Bem`), `FC_COMPR=true` (`F_COMPR[1]` = `Razoavelmente`), `visibilidade="Público"`.
- **Salvamento:** Exibiu `.caixaMsg` `"Sucesso\nA operação foi realizada com sucesso! !"` e listou `4` itens em `pkg_idioma.lista` (`2 · Esperanto · Pouco · Razoavelmente · Bem · Razoavelmente`).
- **Reabertura persistida (F5):** Reaberto `Esperanto`; **100% dos checkboxes e índices de rádio (`[0]`, `[1]`, `[2]`, `[1]`) retornaram idênticos**.
- **Exclusão:** Clicar em `.botao.excluir a` no registro `Esperanto` executou **exclusão imediata** (sem `confirm()` nativo e sem modal `.caixaMsg` de confirmação).
- **Listagem final verificada:** **`3` itens** (apenas os 3 idiomas originais: `Espanhol`, `Inglês`, `Português`).
