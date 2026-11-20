# Ficha de validação — Citações (`prc_indicadores?f_base=1|2|3|4|99`)

- **Data:** 2026-11-20 · **URL no Lattes:** `prc_indicadores?f_cod=<cod>&f_base=<1|2|3|4|99>` (`form[name="PRC_INDICADORES"]`)
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO (todas as 5 bases vazias/intactas)**

---

## 1. Estado Inicial e `<input type="hidden">` (`7` campos)

- Verificadas as 5 bases (`1` Web of Science, `2` SciELO, `3` SCOPUS, `4` Google Scholar, `99` Outra base bibliográfica): todas inicialmente vazias (`hasExcluir = 0`).
- **Hidden inputs em `f_base=99` (`7` campos):**
  `f_sta_validado`, `f_res_id`, `f_indiceh`, `f_ctr`, `f_cod`, `f_seq`, `f_base`.

---

## 2. F4/F5 + F7 em `Citações em outra base bibliográfica` (`f_base=99`) — PASSOU

- **Preenchimento e Read-Back Pré-Save (F4/F5):**
  - `f_txt_base = "[ZZ-TESTE-ANTIGRAVITY]"`
  - `f_qtd_citacoes = "10"`
  - `f_qtd_trabalhos = "5"`
  - `f_data = "20/11/2026"`
  - `f_query = "SANTOS, A. A. B."`
  - Botão `Excluir` ausente antes do salvamento (`hasExcluir = 0`).
- **Salvamento e Reabertura Persistida (F5):**
  - Clicar em **Salvar** exibiu toast `"Sucesso / A operação foi realizada com sucesso! !"` e fechou o modal.
  - Ao reabrir `prc_indicadores?f_base=99`, **100% dos 5 campos retornaram idênticos** e o botão **`Excluir`** (`onclick="del();return false;"`) passou a ser exibido (`excluirCount = 1`).
- **Exclusão (F7):**
  - Clicar em **Excluir** (`del();return false;`) executou **exclusão imediata** (sem `confirm()` nativo e sem modal `.caixaMsg` de confirmação), exibindo `"Sucesso / A operação foi realizada com sucesso! !"`.
  - Ao reabrir `f_base=99` após a exclusão, o formulário confirmou retorno ao **estado vazio inicial** (todos os 5 campos = `""` e `excluirCount = 0`).
