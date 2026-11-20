# Ficha de validação — Patentes e Registros (`marca_registrada` como representante)

- **Data:** 2026-11-20 · **URL no Lattes:** `PKG_PATENTE_REGISTRO.LISTA?f_cod_tipo=MR` → `PKG_PATENTE_REGISTRO.FORM?f_cod_tipo=MR`
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO (0 itens restantes)**

---

## 1. F4/F5 — Lupas, campos condicionais e preenchimento testado

Ao clicar em **Incluir novo item** em `PKG_PATENTE_REGISTRO.LISTA?f_cod_tipo=MR`:
- **Dados básicos:**
  - `f_tit` = `[ZZ-TESTE-ANTIGRAVITY] Marca Teste`
  - `f_ano` = `2025`
  - `f_pais` = `Brasil` (`BRA`)
- **Subformulário de depósito/registro (`infDadPat()`):**
  - Acionada a lupa `escolhe_inst()` → selecionada instituição **INPI**
  - `f_cod_reg` = `1234567-8`
- **Inovação (campo condicional):**
  - `f_sta_inovacao` = `Sim` → revelou/habilitou `f_txt_potencial` = `Potencial marca teste`
- **Inventores / Autores:**
  - Adicionado autor existente: `SANTOS, A. A. B.`

---

## 2. F7 — Salvamento, Reabertura Persistida e Exclusão

- **Salvamento:** Salvo com sucesso (`[ZZ-TESTE-ANTIGRAVITY] Marca Teste`), aparecendo na listagem de Marcas Registradas.
- **Reabertura persistida (F5):** Reaberto o registro salvo diretamente pela listagem após recarregamento; **100% dos campos retornaram exatamente iguais** ao que foi salvo (`f_tit`, `f_ano`, `f_pais`, instituição `INPI`, `f_cod_reg="1234567-8"`, `f_sta_inovacao="Sim"`, `f_txt_potencial="Potencial marca teste"` e inventor `SANTOS, A. A. B.`).
- **Exclusão (regra crítica descoberta):**
  - Ao clicar em **Excluir** dentro do formulário aberto, o Lattes **não** usa `window.confirm()` nativo nem exclui imediatamente: ele abre um **modal customizado `.caixaMsg`** com o texto:
    > `"Atenção\nConfirma a exclusão?"`
  - Após confirmar no modal `.caixaMsg`, exibe:
    > `"Sucesso\nA operação foi realizada com sucesso! !"`
  - **Listagem final verificada:** `0` itens restantes (ambiente 100% limpo).

---

## 3. Cultivar protegida (`PKG_PATENTE_REGISTRO.LISTA?f_cod_tipo=CP` → `PKG_PATENTE_REGISTRO.FORM`) — PASSOU

- **Abertura e `<input type="hidden">` (`19` elementos):**
  - Auto-abre com `0` itens (sem modal `infDadPat()`).
  - **17 hidden inputs com `name`:** `f_dados_grid_datas`, `F_COD_PROD`, `f_sta_validado`, `f_sta_validado_mapa`, `f_origem`, `f_dta_dep_pct`, `f_dta_exp`, `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_depositante_pessoa_l`, `f_depositante_inst_l`, `f_cod_tipo`.
  - **2 hidden inputs somente com `id`:** `#f_melhoristas`, `#f_melhoristas_formatado`.
- **Campos reais preenchidos (F4/F5):**
  - Em `CP`, `f_inst` (`Autoridade Nacional`) é texto livre (sem lupa `escolhe_inst()`):
  - `f_titulo = "[ZZ-TESTE-ANTIGRAVITY] Cultivar"`, `f_pais = "BRA"`, `f_inst = "SNPC/MAPA"`, `f_cod_reg = "20240001"`, `f_dta_dep = "10/05/2024"`, `f_sta_inovacao = "Não"`, melhorista `SANTOS, A. A. B.`.
- **Salvamento, Reabertura (F5) e Exclusão (F7):**
  - Salvo e listado como `1 · [ZZ-TESTE-ANTIGRAVITY] Cultivar · 2024`; reabertura confirmou **100% de persistência**.
  - **Exclusão:** Confirmado o mesmo padrão de `Marca registrada`: clicar em **Excluir** abre o modal customizado `.caixaMsg` **`"Atenção\nConfirma a exclusão?"`**; após confirmar, exibe `"Sucesso\nA operação foi realizada com sucesso! !"` e retorna a lista a **`0` itens**.
