# Ficha de validação — Citações (`prc_indicadores?f_base=1|2|3|4|99`)

- **Data:** 2026-11-20 · **URL no Lattes:** `prc_indicadores?f_cod=<cod>&f_base=<1|2|3|4|99>` (`form[name="PRC_INDICADORES"]`)
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO (todas as 5 bases vazias/intactas)**

---

## 1. Estado Inicial e `<input type="hidden">` (`7` campos)

- Verificadas as 5 bases (`1` Web of Science, `2` SciELO, `3` SCOPUS, `4` Google Scholar, `99` Outra base bibliográfica): todas inicialmente vazias (`hasExcluir = 0`).
- **Hidden inputs em `f_base=99` (`7` campos):**
  `f_sta_validado`, `f_res_id`, `f_indiceh`, `f_ctr`, `f_cod`, `f_seq`, `f_base`.

---

## 2. F4/F5 + F7 nas 5 Bases (`f_base = 1, 2, 3, 4, 99`) — PASSOU (100% VALIDADO E LIMPO)

### 2.1 `citacao_web_of_science` (`f_base=1`)
- **F5 (truncamento `maxlength` e leitura de volta):** `f_res_id` (max `13`), `f_indiceh` (max `3`), `f_qtd_citacoes` e `f_qtd_trabalhos` (max `6`), `f_data` (max `10`), `f_query` (max `400`) — 21/21 casos `OK`.
- **F7 (Salvar 100% dos 6 campos + Reabrir + Excluir):** salvo (`f_res_id="A-1234-2024"`, `f_qtd_citacoes="12"`, `f_qtd_trabalhos="3"`, `f_data="21/11/2026"`, `f_indiceh="4"`, `f_query="ZZ-TESTE-LATTESFACIL Web of Science"`), reaberto com 100% de persistência e botão `Excluir` visível (`hasExcluir = 1`), e excluído imediatamente (confirmado retorno a `""` e `hasExcluir = 0`).

### 2.2 `citacao_scielo` (`f_base=2`)
- **F5:** `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` — 14/14 casos `OK`.
- **F7:** salvo (`f_qtd_citacoes="12"`, `f_qtd_trabalhos="3"`, `f_data="21/11/2026"`, `f_query="ZZ-TESTE-LATTESFACIL SciELO"`), reaberto com 100% de persistência (`hasExcluir = 1`), e excluído imediatamente (`hasExcluir = 0`).

### 2.3 `citacao_scopus` (`f_base=3`)
- **F5:** `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` — 14/14 casos `OK`.
- **F7:** salvo (`f_qtd_citacoes="12"`, `f_qtd_trabalhos="3"`, `f_data="21/11/2026"`, `f_query="ZZ-TESTE-LATTESFACIL SCOPUS"`), reaberto com 100% de persistência (`hasExcluir = 1`), e excluído imediatamente (`hasExcluir = 0`).

### 2.4 `citacao_google_scholar` (`f_base=4`)
- **F5:** `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` (rótulo `"Endereço na Web(URL) do perfil do autor"`) — 14/14 casos `OK`.
- **F7:** salvo (`f_qtd_citacoes="12"`, `f_qtd_trabalhos="3"`, `f_data="21/11/2026"`, `f_query="https://scholar.google.com/citations?user=ZZ-TESTE-LATTESFACIL"`), reaberto com 100% de persistência (`hasExcluir = 1`), e excluído imediatamente (`hasExcluir = 0`).

### 2.5 `citacao_outra_base` (`f_base=99`)
- **F5:** `f_txt_base` (max `200`), `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` — 18/18 casos `OK`.
- **F7:** salvo (`f_txt_base="ZZ-TESTE-LATTESFACIL Base Teste"`, `f_qtd_citacoes="12"`, `f_qtd_trabalhos="3"`, `f_data="21/11/2026"`, `f_query="ZZ-TESTE-LATTESFACIL Outra base"`), reaberto com **100% dos 5 campos idênticos** e botão **`Excluir`** (`onclick="del();return false;"`, `hasExcluir = 1`), e excluído imediatamente confirmando retorno ao **estado vazio inicial** (`hasExcluir = 0`).
