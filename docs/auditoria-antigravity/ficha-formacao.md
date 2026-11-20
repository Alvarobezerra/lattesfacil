# Ficha de validação — Formação (`formacao_academica`, `pos_doutorado`, `formacao_complementar`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `pkg_formacao.form?f_tipo=FA&f_nivel=...` · `pkg_formacao.form?f_tipo=AP&f_nivel=...` · `PKG_FORMACAO_COMPL.form` → `FORM2`
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO NOS 3 SUBITENS DA ABA FORMAÇÃO**

---

## 1. Formação acadêmica/titulação (`pkg_formacao.lista?f_tipo=FA` → `pkg_formacao.form`)

- **Abertura:** Modal de seleção de nível (`selecionarNivel`) com **10 níveis**:
  `4` (`Doutorado`), `3` (`Mestrado`), `9` (`Mestrado Profissional`), `2` (`Especialização`), `D` (`Especialização - Residência médica`), `1` (`Graduação`), `7` (`Ensino Profissional de nível técnico`), `C` (`Ensino Médio (2o grau)`), `B` (`Ensino Fundamental (1o grau)`), `X` (`Aperfeiçoamento`).
- **F4/F5 + F7 em Mestrado (`f_nivel=3`) — VALIDADO E LIMPO:**
  - Preenchido: `f_tpo_doutorado = normal`, `f_inst` (via `sele_inst()`: `"Universidade Federal do Maranhão "`), `f_curso` (via `curso()`: `"ARTES CÊNICAS(20001010045P0)"`), `F_STATUS = concluído`, `f_ano_ini = "2018"`, `f_ano_fim = "2020"`, `f_mes_obten = "03"`, `f_ano_obten = "2020"`, `F_BOLSA = Não`, `f_titulo = "[ZZ-TESTE-ANTIGRAVITY] Dissertacao Teste"`, `f_orient = "Orientador Teste"`.
  - **Reabertura persistida (F5):** 100% fiel (com normalização do servidor removendo o sufixo de código CAPES em `f_curso`: `"ARTES CÊNICAS"`).
  - **Exclusão (F7):** Imediata sem `confirm()` nativo nem modal `.caixaMsg`, restaurando os **`6` itens originais** do currículo.

---

## 2. Pós-doutorado e/ou Livre-docência (`pkg_formacao.lista?f_tipo=AP` → `pkg_formacao.form`)

- **Abertura:** `Incluir novo item` abre modal top-level `Nível` com `<select>` de **2 opções**: `Pós-Doutorado` (`5`) e `Livre Docência` (`6`).
- **A) F4/F5 + F7 em `Pós-Doutorado` (`f_nivel=5`) — VALIDADO E LIMPO:**
  - Abas: `Dados Gerais`, `Período`, `Bolsa`, `Áreas`, `Visibilidade` (**não** possui campo `f_titulo` visível).
  - Preenchido: `f_inst` (via `sele_inst()`): `"Universidade Federal do Maranhão "`, `F_STATUS = concluído`, `f_ano_ini = "2021"`, `f_ano_fim = "2023"`, `F_BOLSA = Não`.
  - **Salvamento e Reabertura (F5):** Listado como `1 · 2021... 2023 · Pós-Doutorado · Universidade Federal do Maranhão`; reabertura (`f_seq=14`) confirmou **100% de persistência**.
  - **Exclusão (F7):** Imediata sem `confirm()` nativo nem modal `.caixaMsg`, retornando a lista para **`0` itens**.
- **B) F4/F5 + F7 em `Livre Docência` (`f_nivel=6`) — VALIDADO E LIMPO:**
  - Abas: `Dados Gerais`, `Período`, `Detalhamento`, `Palavras-chave`, `Áreas`, `Setores`, `Visibilidade`.
  - Preenchido: `f_inst` (via `sele_inst()`): `"Universidade Federal do Maranhão "`, `f_mes_obten = "06"`, `f_ano_obten = "2024"`, `f_titulo = "[ZZ-TESTE-ANTIGRAVITY] Livre Docencia Teste"`.
  - **Salvamento e Reabertura (F5):** Listado como `1 · ... (2024) · Livre Docência · Universidade Federal do Maranhão`; reabertura (`f_seq=14`) confirmou **100% de persistência**.
  - **Exclusão (F7):** Imediata sem `confirm()` nativo nem modal `.caixaMsg`, retornando a lista para **`0` itens**.

---

## 3. Formação complementar (`pkg_formacao_compl.lista` → `PKG_FORMACAO_COMPL.form` → `FORM2`)

- **Abertura e Wizard de 2 Telas:**
  - **Tela 1 (`PKG_FORMACAO_COMPL.form`):** `f_nivel` (`Curso De Curta Duração = F`, `Extensão Universitária = 8`, `Mba = E`, `Outros = Y`), `f_inst` (`disabled`, lupa `sele_inst()`), `f_curso` (`disabled`, lupa `curso()`), `f_carga` (`maxlength="4"`), `F_STATUS` (`em andamento`, `concluído`, `incompleto`) → botão **Avançar**.
  - **Tela 2 (`PKG_FORMACAO_COMPL.FORM2`):** `f_ano_ini` (`maxlength="4"`), `f_ano_fim` (`maxlength="4"` — rótulo `Conclusão` se concluído, `Interrupção` se incompleto, ou `disabled` se em andamento), `F_BOLSA` (`Sim`/`Não`), `f_nme_agencia` (`disabled`, lupa `agencia()`), grade `Palavras-chave` e `Visibilidade`.
- **F4/F5 + F7 — VALIDADO E LIMPO:**
  - **Tela 1:** `f_nivel = Curso De Curta Duração`, `f_inst = Universidade Federal do Maranhão`, `f_curso = Curso de Auditoria Interna()`, `f_carga = "40"`, `F_STATUS = concluído` → **Avançar**.
  - **Tela 2 (`FORM2`):** `f_ano_ini = "2023"`, `f_ano_fim = "2024"`, `F_BOLSA = Não` → **Salvar**.
  - **Reabertura persistida (F5):** Reabertura nas 2 telas 100% fiel (`f_curso` normaliza removendo `()` → `"Curso de Auditoria Interna"`).
  - **Exclusão (F7):** Clicar em **Excluir** na Tela 2 removeu imediatamente sem `confirm()` nativo, restaurando os **`4` itens originais** do currículo.
