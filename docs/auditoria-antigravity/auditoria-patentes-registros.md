# Auditoria Completa — Aba Patentes e Registros (8 Variantes em `PKG_PATENTE_REGISTRO`: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todas as **8 variantes** do motor `PKG_PATENTE_REGISTRO.FORM` (7 na aba **Patentes e registros** + `Programa de computador sem registro` na aba Produção Técnica):
  1. **Patente (`f_cod_tipo=PP`)**
  2. **Programa de computador registrado (`f_reg=S&f_cod_tipo=PC`)**
  3. **Programa de computador sem registro (`f_cod_tipo=PS`)**
  4. **Cultivar protegida (`f_cod_tipo=CP`)**
  5. **Cultivar registrada (`f_cod_tipo=CR`)**
  6. **Desenho industrial registrado (`f_cod_tipo=DI`)**
  7. **Marca registrada (`f_cod_tipo=MR`)**
  8. **Topografia de circuito integrado registrada (`f_cod_tipo=TC`)**
- **Status F4/F5 + F7:** Validado com salvamento real, reabertura persistida e exclusão nos **2 subgrupos estruturais** da família ([ficha-patentes-registros.md](ficha-patentes-registros.md)):
  - Subgrupo com wizard `infDadPat()` + lupa `escolhe_inst()`: **`Marca registrada` (`MR`)** — validado e limpo (`0` itens).
  - Subgrupo de abertura direta com `f_inst` livre + grade `Melhoristas`: **`Cultivar protegida` (`CP`)** — validado e limpo (`0` itens).

---

## 1. Arquitetura do Motor `PKG_PATENTE_REGISTRO.FORM`

### 1.1 Todos os `<input type="hidden">` (`19` elementos)
- **17 com `name`:** `f_dados_grid_datas`, `F_COD_PROD`, `f_sta_validado`, `f_sta_validado_mapa`, `f_origem`, `f_dta_dep_pct`, `f_dta_exp`, `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_depositante_pessoa_l`, `f_depositante_inst_l`, `f_cod_tipo`.
- **2 apenas com `id` (`name=null`):** `#f_melhoristas`, `#f_melhoristas_formatado`.

### 1.2 Dois Padrões de Abertura (`infDadPat()` vs Abertura Direta)
1. **Variantes com modal prévio `infDadPat()` (`PP`, `PC`, `DI`, `MR`, `TC`):**
   - Ao clicar em `Incluir novo item`, **não** abre o formulário direto: abre o modal `infDadPat()`, que exige:
     - `f_inst`: selecionado obrigatoriamente via lupa **`escolhe_inst()`** (lista fechada de 12 instituições depositárias, como `INPI`).
     - `f_cod_reg` (`Número do registro`, `maxlength="16"`): quando a instituição é `INPI`, valida máscara específica antes de liberar o formulário:
       - `PC` e `DI`: exige formato `9999999-9` ou `BR9999999999-9` / `BR99999999999-9`.
       - `MR` e `TC`: aceita `9999999-9`, `PI9999999`, `MU9999999`, `BRZZXXXXYYYYYYK`.
2. **Variantes de abertura direta sem `infDadPat()` (`PS`, `CP`, `CR`):**
   - **`PS` (`Programa de computador sem registro`)**: não tem `f_inst` de registro nem `f_cod_reg`; usa `f_ano` (`Ano de desenvolvimento`), `f_plataforma` (`Linguagens`), `f_finalidade` e `f_inst_financ`.
   - **`CP` (`Cultivar protegida`) e `CR` (`Cultivar registrada`)**: abrem direto (auto-abrem quando a lista tem `0` itens); `f_inst` (`Autoridade Nacional`, `maxlength="75"`) e `f_cod_reg` (`Número do processo`/`Número do registro`) são campos `<input type="text">` **de digitação livre no próprio formulário** (sem lupa `escolhe_inst()`!).

### 1.3 Regra Exclusiva de Exclusão (Modal `.caixaMsg` de Confirmação)
- Diferente das abas `Formação`, `Atuação`, `Produções`, `Eventos` e `Bancas` (onde clicar em `Excluir` dentro do formulário aberto remove o registro imediatamente sem confirmação), **em todas as variantes de `PKG_PATENTE_REGISTRO.FORM` testadas (`MR` e `CP`)**:
  - Clicar em **Excluir** dentro do formulário **abre um modal customizado `.caixaMsg`** com:
    > `"Atenção\nConfirma a exclusão?"`
  - O robô ou usuário precisa clicar no botão de confirmação desse `.caixaMsg` para efetivar a exclusão e receber o toast `"Sucesso\nA operação foi realizada com sucesso! !"`.

---

## 2. Matriz Comparativa das 8 Variantes e Divergências nos Specs (`itens/especificacao/`)

| # | Variante (`f_cod_tipo`) | Abertura | Default de `f_sta_inovacao` | Grades de Titular e Autores | Obrigatórios no Spec vs Lattes ao Vivo (`check()`) |
| --- | --- | --- | --- | --- | --- |
| 1 | **Patente (`PP`)** | `infDadPat()` (`escolhe_inst` + `f_cod_reg`) | **Desmarcado (`null`)** — obriga escolher `Sim` ou `Não`! | `Depositante/Titular` (**obrigatório**: `#titularPessoaHolder` / `#titularInstHolder`) + `Inventores` (`f_autores_l`) + `Situação/Datas` (`f_dados_grid_datas`) | Spec marca **1** obrigatório vs **9 obrigatórios reais** (`Depositante/Titular`, `f_sta_inovacao`, `f_titulo`, `f_natureza`, `f_tipo`, `f_inst`, `f_cod_reg`, `Data de depósito`, `Inventores`) |
| 2 | **Software registrado (`PC`)** | `infDadPat()` (`INPI` c/ máscara) | **`Sim` (marcado por padrão!)** → `f_txt_potencial` já inicia visível e obrigatório | `Depositante/Titular` (opcional) + `Autores/Inventores` | Spec omite `f_dta_dep`, `f_dta_conc`, `f_txt_potencial` (quando `Sim`), `f_inst_financ`, `f_finalidade`, `f_plataforma` como obrigatórios |
| 3 | **Software s/ registro (`PS`)** | Direta | **`Não`** (se `Sim`, exige `f_txt_potencial`) | `Depositante/Titular` + `Autores/Inventores` + `tabelaprograma` | `f_natureza` está marcado obrigatório no spec, mas no Lattes ao vivo **não é obrigatório**; faltam `f_inst_financ`, `f_finalidade`, `f_plataforma` |
| 4 | **Cultivar protegida (`CP`)** | Direta (auto-abre c/ 0 itens) | **`Não`** (se `Sim`, exige `f_txt_potencial`) | `Titular` + **`Melhoristas`** (`f_autores_l` / `#f_melhoristas`) | Spec marca **3** obrigatórios vs **5 reais** (`f_titulo`, `f_inst` texto livre, `f_cod_reg`, `f_dta_dep`, `Melhoristas`); `f_nme_comum` e `f_nme_cientifico` têm `maxlength="16"` |
| 5 | **Cultivar registrada (`CR`)** | Direta (auto-abre c/ 0 itens) | **`Não`** (se `Sim`, exige `f_txt_potencial`) | `Titular` + **`Melhoristas`** | Spec marca **2** obrigatórios vs **6 reais** (`f_titulo`, `f_ano`, `f_inst` texto livre, `f_cod_reg`, `f_dta_dep`, `Melhoristas/Inventores`) |
| 6 | **Desenho industrial (`DI`)** | `infDadPat()` (`INPI` c/ máscara) | **`Sim` (marcado por padrão!)** → `f_txt_potencial` já inicia visível e obrigatório | `Depositante/Titular` + `Inventores` | Spec omite `f_dta_dep`, `f_txt_potencial` (quando `Sim`), `f_inst_financ` e `f_finalidade` como obrigatórios |
| 7 | **Marca registrada (`MR`)** | `infDadPat()` (`escolhe_inst` + `f_cod_reg`) | **`Não`** (se `Sim`, exige `f_txt_potencial`) | `Inventores` (sem aba Titular) | 7 obrigatórios reais: `f_titulo`, `f_ano`, `f_natureza` (`Figurativa`..), `f_tipo` (`de Produto`..), `f_inst`, `f_cod_reg`, `Inventores` |
| 8 | **Topografia de circuito (`TC`)** | `infDadPat()` (`escolhe_inst` + `f_cod_reg`) | **`Não`** (se `Sim`, exige `f_txt_potencial`) | `Inventores` (sem aba Titular) | Spec marca **5** obrigatórios vs **7 reais** (faltam `f_inst_financ`, `f_finalidade` e `Inventores`) |
