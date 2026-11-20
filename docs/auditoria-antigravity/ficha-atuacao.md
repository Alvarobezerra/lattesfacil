# Ficha de validação — Aba Atuação (`atuacao_profissional`, `corpo_editorial`, `comite_assessoramento`, `revisor_*`, `areas_atuacao`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `pkg_ativ.lista` → `PKG_ATIV.inclui` → `PKG_ATIV.cargos_vinculos` → `pkg_ativ.cargo` · `pkg_revisor.lista?f_natur=MB|MA|RV|RA`
- **Status:** **F4/F5 + F7 VALIDADO COM SUCESSO E LIMPO NOS 3 NÍVEIS DE ATUAÇÃO PROFISSIONAL E EM CORPO EDITORIAL / COMITÊ**

---

## 1. Atuação profissional — Hierarquia Completa de 3 Níveis (`pkg_ativ.lista`)

### 1.1 Nível 1 — Inclusão de Instituição e Vínculo (`PKG_ATIV.inclui` / `form[name="GN_ATIV"]`)
- **Estado inicial preservado:** `7` instituições originais do usuário mantidas intactas.
- **Hidden inputs (`10` campos em `GN_ATIV`):**
  `f_vinculo`, `f_cod_inst`, `f_cod_inst2`, `f_instold`, `f_inst_old`, `f_ctr`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_hist`.
- **Dinâmica da lupa `dominio()` em `f_vinc`:**
  - `f_vinc` inicia `disabled=true`.
  - Opções da lupa: `Servidor público`, `Celetista`, `Professor Visitante`, `Bolsista`, `Outro (especifique)`.
  - Escolher `"Outro (especifique)"` define `f_vinc.disabled = false` e `f_vinc.value = ""` (liberando digitação livre).
  - Escolher qualquer opção fixa define `f_vinc.disabled = true` e preenche `f_vinc.value`.
- **Preenchimento e Salvamento (F4/F5 + F7):**
  - Instituição selecionada via `sele_inst()` (`prc_inst_ativ`): `Centro de Apoio à Faculdade de Saúde Pública da Universidade de São Paulo` (`CEAP/FSP`).
  - `f_vinc = "Professor Visitante"`, `f_stavinc = "0"` (`Não`), `f_enqua = "[ZZ-TESTE-ANTIGRAVITY]"`, `f_mes_ini = "01"`, `f_ano_ini = "2024"`, `f_status = Anterior (finalizado)` → revelou `f_mes_fim = "12"`, `f_ano_fim = "2024"`.
  - Salvo com toast `"Sucesso: A operação foi realizada com sucesso! !"`.

### 1.2 Nível 2 — Hub da Instituição e Edição de Vínculo (`PKG_ATIV.cargos_vinculos` → `PKG_ATIV.vinculos`)
- Clicar na instituição em `pkg_ativ.lista` abre **`PKG_ATIV.cargos_vinculos`**, que contém:
  - Aba **`Vínculos`** (lista os vínculos cadastrados naquela instituição).
  - Aba **`Atividades`** (lista as atividades de ensino, pesquisa, direção, extensão, etc. naquela instituição).
  - Botão **`Excluir`** no rodapé direito (exclui a instituição inteira do currículo).
- **Reabertura persistida do vínculo (`PKG_ATIV.vinculos` — F5):**
  - Clicar no vínculo `1 · 01/2024 · 12/2024 · [ZZ-TESTE-ANTIGRAVITY]` abriu `PKG_ATIV.vinculos` com **100% dos campos persistidos**.

### 1.3 Nível 3 — Atividades (`pkg_ativ.cargo` / `form[name="GN_ATIV_CARGO"]`)
- Na aba `Atividades` do Hub (`PKG_ATIV.cargos_vinculos`), clicar em `Incluir novo item` abre o modal `Selecione a natureza da Atividade` com **9 naturezas (`f_natur_ativ`)**:
  - `1`: `Direção e Administração` (`f_orgao` + lupa `orgao()`, grade `Cargo ou função`)
  - `2`: `Pesquisa e Desenvolvimento` (`f_orgao` + lupa `orgao()`, grade **`Linhas de pesquisa`**)
  - `4`: `Ensino` (`<select name="f_nivel">` com opções `401` Graduação, `402` Pós-graduação, `403` Especialização, `404` Aperfeiçoamento, `405` Ensino fundamental, `406` Ensino médio, `409` Outro; `f_curso` `disabled` + lupa `curso()` → `prc_curso_form?f_inst=...&f_nivel=...&f_pgm=ATIV`; grade **`Disciplinas ministradas`**)
  - `5`: `Estágio` (`f_orgao`, grade `Estagio Realizado`)
  - `6`: `Serviço Técnico Especializado` (`f_orgao`, grade `Serviço realizado`)
  - `7`: `Extensão Universitária` (`f_orgao`, grade `Atividade de extensão realizada`)
  - `8`: `Treinamento` (`f_orgao`, grade `Treinamento ministrado`)
  - `9`: `Outra atividade técnico-científica` (`f_orgao`, grade `Outra atividade técnico-científica`)
  - `B`: `Conselhos, Comissões e Consultoria` (`f_orgao`, grade `Cargo ou função`)
- **Hidden inputs (`15` campos em `GN_ATIV_CARGO`):**
  `f_natur_ativ`, `f_ctr`, `f_espec_l`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_funcao`, `f_codorgao`, `f_codorgao2`, `f_exc`, `f_natur_old`, `f_cod_curso`, `f_cod_curso2`, `f_curso_old`, `f_orgao_old`.
- **Mecânica das grades (`Linhas de pesquisa`, `Disciplinas ministradas`, etc.):**
  - O campo de texto da grade adiciona itens ao pressionar a tecla **`Enter`** (`keyCode === 13`), inserindo a linha em `.grid-content` e serializando os valores no hidden input **`f_espec_l`**.
- **Regra condicional de `f_curso` em `Ensino` (`f_natur_ativ=4`):**
  - Em `f_nivel = 401` (`Graduação`), `f_curso` é **obrigatório** ao salvar.
  - Em `405`, `406` e `409` (`Outro`), `f_curso` permanece visível e `disabled`, mas **permite salvar sem curso**.
- **Salvamento e Reabertura de Atividade (F5):**
  - Salva atividade de `Ensino` (`f_nivel=409`, período `02/2024` a `11/2024`, disciplina `[ZZ-TESTE-ANTIGRAVITY] Disciplina Teste`); reabertura confirmou **100% de persistência**.

### 1.4 Exclusão nos 3 Níveis (F7)
1. **Exclusão da Atividade (`pkg_ativ.cargo`):** clicar em `Excluir` removeu a atividade **imediatamente** (sem `confirm()` nem modal `.caixaMsg`), voltando a aba `Atividades` para `"Nenhum registro cadastrado."`.
2. **Exclusão do Vínculo (`PKG_ATIV.vinculos`):** clicar em `Excluir` removeu o vínculo **imediatamente** (sem `.caixaMsg`), voltando a aba `Vínculos` para `"Nenhum registro cadastrado."`.
3. **Exclusão da Instituição (`PKG_ATIV.cargos_vinculos`):** clicar em `Excluir` no rodapé do Hub removeu a instituição de teste **imediatamente** (sem `confirm()` nem `.caixaMsg`), restaurando `pkg_ativ.lista` exatamente às **`7` instituições originais** do usuário.

---

## 2. Membro de corpo editorial (`pkg_revisor.lista?f_natur=MB` → `PKG_REVISOR.inclui?f_natur=MB`)

- **Lupa de periódico (`periodico()`):** Busca por `"Revista"` (8.609 resultados) → `"Revista de economia e sociologia rural (1806-9479)"` → `f_nme_agencia = "Revista de economia e sociologia rural "`.
- **Campos condicionais (`f_status`):** `Anterior (finalizado)` revelou `f_mes_fim = "12"` e `f_ano_fim = "2024"`.
- **Reabertura persistida em 2 níveis (F5):** `pkg_revisor.lista?f_natur=MB` → `PKG_REVISOR.lista_periodico` → `PKG_REVISOR.inclui` (**100% match**).
- **Exclusão (F7):** Imediata sem `confirm()`; excluir o único vínculo remove automaticamente o periódico-pai da tabela principal (`0` itens restantes).

---

## 3. Membro de comitê de assessoramento (`pkg_revisor.lista?f_natur=MA` → `PKG_REVISOR.inclui?f_natur=MA`)

- **Abertura:** `0` itens iniciais → auto-abre `PKG_REVISOR.inclui?f_cod=...&f_natur=MA&f_origem=L`.
- **Hidden inputs (`16` campos — idênticos em `MB`, `MA`, `RV` e `RA`):**
  `f_nme_agencia_h`, `f_seq_per`, `f_natur`, `f_issn`, `f_issn_h`, `f_cod_inst`, `f_cod_inst2`, `f_instold`, `f_inst_old`, `f_origem`, `f_ctr`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_hist`, `f_seq_funcao_ativ`.
- **Lupa de agência (`agencia()` → `pkg_revisor.agencia`):**
  - Selecionada `(FAPESPA) FUNDACAO AMAZONIA DE AMPARO A ESTUDOS E PESQUISAS - FAPESPA`, populando `f_nme_agencia`, `f_nme_agencia_h` e `f_cod_inst`.
- **Campos preenchidos e F4/F5:**
  - `f_comite = "[ZZ-TESTE-ANTIGRAVITY]"`, `f_mes_ini = "01"`, `f_ano_ini = "2024"`, `f_status = Anterior (finalizado)` → revelou `f_mes_fim = "12"`, `f_ano_fim = "2024"`.
  - **Reabertura em 2 níveis (F5):** `pkg_revisor.lista?f_natur=MA` → `PKG_REVISOR.lista_periodico?...&f_cod_inst=IZJ800000006` (`1 · De 2024 até 2024`) → `PKG_REVISOR.inclui?...&f_origem=P&f_seq_funcao_ativ=1` (**100% persistido**).
- **Exclusão (F7):**
  - Clicar em **Excluir** em `PKG_REVISOR.inclui` executou **exclusão imediata** (sem `confirm()` nem modal `.caixaMsg`), removendo automaticamente a agência-pai e retornando `pkg_revisor.lista?f_natur=MA` para **`0` itens**.

---

## 4. Revisor de periódico (`f_natur=RV`) e Revisor de projeto de agência de fomento (`f_natur=RA`)

- Ambos usam o mesmo motor `PKG_REVISOR.inclui` (`form[name="GN_ATIV"]`) com os mesmos **16 hidden inputs** de `MB` e `MA`:
  - `RV` (`0` itens): usa lupa `periodico()` (popula `f_nme_agencia`, `f_nme_agencia_h`, `f_seq_per`, `f_issn`, `f_issn_h`).
  - `RA` (`0` itens): usa lupa `agencia()` (popula `f_nme_agencia`, `f_nme_agencia_h`, `f_cod_inst`, `f_cod_inst2`), sem o campo `f_comite`.

---

## 5. Áreas de atuação (`prc_area_atuacao` / `form[name="GN_AREA_ATU"]`)

- **Estado preservado (somente leitura):** `3` áreas originais do titular mantidas intactas (`1º Farmácia`, `2º Famácia Hospitalar`, `3º Farmácia Clínica`).
- **Hidden inputs (`5` campos em `GN_AREA_ATU`):**
  `f_cod`, `f_area_l`, `f_ctr`, `f_setor_prod`, `f_privacidade`.
- **Mecânica de adição na grade:**
  - **Input suggest:** `"Digite, selecione ou inclua uma nova área de conhecimento..."`
  - **Modal inline `Listar todos` (`Seleção de área`):** árvore expansível (`+`) em **4 níveis** (`Grande Área → Área → Subárea → Especialidade`) a partir das 9 Grandes Áreas CNPq.
  - **Modal inline `Incluir nova` (`Inclusão de área`):** `<input type="text">` (`Área:`) + árvore das **9 Grandes Áreas** (expansível até o nível de `Área`) para vincular uma especialidade/subárea nova.
  - Todas as áreas da grade são serializadas no hidden **`f_area_l`**.
