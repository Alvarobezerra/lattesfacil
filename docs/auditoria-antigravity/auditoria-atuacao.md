# Auditoria Completa — Aba Atuação (7 Subitens: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todos os **7 subitens** da aba **Atuação** da Plataforma Lattes:
  1. **Atuação profissional** (`pkg_ativ.lista` → **Hierarquia de 3 níveis**: `PKG_ATIV.inclui` → `PKG_ATIV.cargos_vinculos` / `PKG_ATIV.vinculos` → `pkg_ativ.cargo` com **9 naturezas de atividades**)
  2. **Linhas de pesquisa** (`pkg_linhapesq.lista` — tela informativa que redireciona para `Atuação profissional > Atividades > Pesquisa e Desenvolvimento`)
  3. **Membro de corpo editorial** (`pkg_revisor.lista?f_natur=MB` → **Hierarquia de 2 níveis**)
  4. **Membro de comitê de assessoramento** (`pkg_revisor.lista?f_natur=MA` → **Hierarquia de 2 níveis**)
  5. **Revisor de periódico** (`pkg_revisor.lista?f_natur=RV` → **Hierarquia de 2 níveis**)
  6. **Revisor de projeto de agência de fomento** (`pkg_revisor.lista?f_natur=RA` → **Hierarquia de 2 níveis**)
  7. **Áreas de atuação** (`prc_area_atuacao` — grade direta com árvore de 9 Grandes Áreas)
- **Status F4/F5 + F7:** Validado com salvamento real, reabertura persistida em múltiplos níveis e exclusão imediata em `Atuação profissional` (todos os 3 níveis: Instituição, Vínculo e Atividade de Ensino), `Membro de corpo editorial` (`MB`) e `Membro de comitê de assessoramento` (`MA`) ([ficha-atuacao.md](ficha-atuacao.md)), mantendo intactas as `7` instituições e `3` áreas originais do currículo.

---

## 1. Resumo Executivo dos 7 Subitens e Divergências nos Specs

| # | Subitem | Endpoint (`form[name]`) | Abertura e Hierarquia Real | Teste F4/F5 + F7 (Salvar + Reabrir + Excluir) | Divergências Críticas no Spec (`itens/especificacao/`) |
| --- | --- | --- | --- | --- | --- |
| 1 | **Atuação profissional** | `PKG_ATIV.inclui` (`GN_ATIV`) → `PKG_ATIV.cargos_vinculos` → `pkg_ativ.cargo` (`GN_ATIV_CARGO`) | **3 níveis** (Lista → Hub Instituição c/ abas `Vínculos` e `Atividades` → 9 naturezas `f_natur_ativ`) | ✔ **Validado e limpo nos 3 níveis** (`7` instituições originais intactas) | **FALHA BLOQUEANTE:** **100% dos Níveis 2 e 3 (`PKG_ATIV.cargos_vinculos` e `pkg_ativ.cargo` — 9 naturezas de atividades, Ensino/Disciplinas, P&D/Linhas de pesquisa, Direção, etc.) estão ausentes** em `atuacao_profissional.json`; no Nível 1, `f_mes_ini`/`f_ano_ini` estão com `obrigatorio: false` e `f_regime`/`f_status` têm rótulos crus |
| 2 | **Linhas de pesquisa** | `pkg_linhapesq.lista` | Sem formulário próprio (orienta cadastrar via `Atuação profissional > Atividades > P&D` `f_natur_ativ=2`) | N/A (cadastrado e testado via Nível 3 de Atuação profissional) | **Sem arquivo em `itens/especificacao/`** |
| 3 | **Membro de corpo editorial** | `PKG_REVISOR.inclui?f_natur=MB` (`GN_ATIV`) | **2 níveis** (`lista` → `lista_periodico` → `inclui`) | ✔ **Validado e limpo** (`0` itens restantes) | `f_status` com rótulo cru `"f_status"` e opções `"S"`/`"N"` (em vez de `"Atual (não finalizado)"` / `"Anterior (finalizado)"`); `f_mes_ini`/`f_ano_ini` com `obrigatorio: false` |
| 4 | **Membro de comitê de assessoramento** | `PKG_REVISOR.inclui?f_natur=MA` (`GN_ATIV`) | **2 níveis** (`lista` → `lista_periodico` → `inclui`) | ✔ **Validado e limpo** (`0` itens restantes) | Mesmas falhas de `f_status` (`"S"`/`"N"`, rótulo cru) e `f_mes_ini`/`f_ano_ini` (`obrigatorio: false`) |
| 5 | **Revisor de periódico** | `PKG_REVISOR.inclui?f_natur=RV` (`GN_ATIV`) | **2 níveis** (`lista` → `lista_periodico` → `inclui`) | Mesmo motor `PKG_REVISOR.inclui` de `MB` (`0` itens) | Mesmas falhas de `f_status` e `f_mes_ini`/`f_ano_ini` |
| 6 | **Revisor de projeto de fomento** | `PKG_REVISOR.inclui?f_natur=RA` (`GN_ATIV`) | **2 níveis** (`lista` → `lista_periodico` → `inclui`) | Mesmo motor `PKG_REVISOR.inclui` de `MA` s/ `f_comite` (`0` itens) | Mesmas falhas de `f_status` e `f_mes_ini`/`f_ano_ini` |
| 7 | **Áreas de atuação** | `prc_area_atuacao` (`GN_AREA_ATU`) | Direta (grade de áreas com árvore de 9 Grandes Áreas) | Inspecionado s/ alterar titular (`3` áreas originais intactas) | **Sem arquivo em `itens/especificacao/`** |

---

## 2. Dinâmica Detalhada para Preenchimento Externo (Autofill)

### 2.1 `Atuação profissional` — Arquitetura Completa dos 3 Níveis

#### Nível 1 — Inclusão de Instituição + 1º Vínculo (`PKG_ATIV.inclui` / `form[name="GN_ATIV"]`)
- **10 hidden inputs:** `f_vinculo`, `f_cod_inst`, `f_cod_inst2`, `f_instold`, `f_inst_old`, `f_ctr`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_hist`.
- **Campos e regras condicionais:**
  - `input[name="f_inst"]` (`disabled=true`, `maxlength="75"`, obrigatório): preenchido via lupa `sele_inst()` (`prc_inst_ativ`), que popula `f_inst` + hidden `f_cod_inst`, `f_cod_inst2`, `f_codinst`.
  - `input[name="f_vinc"]` (`disabled=true` inicialmente, `maxlength="30"`, obrigatório): preenchido via lupa `dominio()`:
    - Opções fixas (`"Servidor público"`, `"Celetista"`, `"Professor Visitante"`, `"Bolsista"`): mantêm `f_vinc.disabled = true` e preenchem `f_vinc.value` + hidden `f_vinculo`.
    - Opção **`"Outro (especifique)"`**: altera **`f_vinc.disabled = false`** e limpa `f_vinc.value = ""`, permitindo digitar livremente o tipo de vínculo!
  - `select[name="f_stavinc"]` (obrigatório): `""`, `"0"` (`Não`), `"1"` (`Sim`).
  - `input[name="f_enqua"]` (`maxlength="45"`, obrigatório): Enquadramento funcional.
  - `input[name="f_carga"]` (`maxlength="3"`, opcional): Carga horária semanal.
  - `input[type="checkbox"][name="f_regime"]` (`value="3"`, opcional): Dedicação exclusiva.
  - `input[name="f_mes_ini"]` (`maxlength="2"`) e `input[name="f_ano_ini"]` (`maxlength="4"`): **obrigatórios**.
  - `input[type="radio"][name="f_status"]`: `"S"` (`Atual (não finalizado)`, default) ou `"N"` (`Anterior (finalizado)` — revela `tr#periodoFim` com `f_mes_fim` e `f_ano_fim`, que passam a ser **obrigatórios**).
  - `textarea[name="f_outras_inf"]` (`maxlength="3950"`, opcional) e `Visibilidade` (`.ms-dd`, default `Público`).

#### Nível 2 — Hub da Instituição (`PKG_ATIV.cargos_vinculos`) e Edição de Vínculo (`PKG_ATIV.vinculos`)
- Quando a instituição já existe em `pkg_ativ.lista`, clicar nela **não** abre `PKG_ATIV.inclui`: abre o **Hub da Instituição (`PKG_ATIV.cargos_vinculos`)**, que possui:
  1. **Aba `Vínculos`:** lista os vínculos naquela instituição (clicar em um vínculo abre `PKG_ATIV.vinculos`; clicar em `Incluir novo item` na aba Vínculos adiciona um novo vínculo à mesma instituição).
  2. **Aba `Atividades`:** lista as atividades exercidas naquela instituição (clicar em `Incluir novo item` abre o seletor das 9 naturezas de atividades e leva ao Nível 3 `pkg_ativ.cargo`).
  3. **Botão `Excluir` no rodapé do Hub:** exclui a instituição inteira do currículo (imediato, sem `confirm()` nem `.caixaMsg`).

#### Nível 3 — Atividades (`pkg_ativ.cargo` / `form[name="GN_ATIV_CARGO"]`)
- **15 hidden inputs:** `f_natur_ativ`, `f_ctr`, `f_espec_l`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_funcao`, `f_codorgao`, `f_codorgao2`, `f_exc`, `f_natur_old`, `f_cod_curso`, `f_cod_curso2`, `f_curso_old`, `f_orgao_old`.
- **Matriz das 9 Naturezas de Atividade (`f_natur_ativ`):**

| Código `f_natur_ativ` | Natureza da Atividade | Campos de Órgão / Nível / Curso | Grade Dinâmica (inserção via tecla **`Enter`** → serializa no hidden **`f_espec_l`**) |
| --- | --- | --- | --- |
| **`1`** | Direção e Administração | `f_orgao` (`disabled`, lupa `orgao()`) | **`Cargo ou função`** |
| **`2`** | Pesquisa e Desenvolvimento | `f_orgao` (`disabled`, lupa `orgao()`) | **`Linhas de pesquisa`** *(único caminho do Lattes para cadastrar Linhas de Pesquisa!)* |
| **`4`** | Ensino | Substitui `f_orgao` por `<select name="f_nivel">` (`401` Graduação, `402` Pós-graduação, `403` Especialização, `404` Aperfeiçoamento, `405` Ensino fundamental, `406` Ensino médio, `409` Outro) + `f_curso` (`disabled`, lupa `curso()`) | **`Disciplinas ministradas`** |
| **`5`** | Estágio | `f_orgao` (`disabled`, lupa `orgao()`) | **`Estagio Realizado`** |
| **`6`** | Serviço Técnico Especializado | `f_orgao` (`disabled`, lupa `orgao()`) | **`Serviço realizado`** |
| **`7`** | Extensão Universitária | `f_orgao` (`disabled`, lupa `orgao()`) | **`Atividade de extensão realizada`** |
| **`8`** | Treinamento | `f_orgao` (`disabled`, lupa `orgao()`) | **`Treinamento ministrado`** |
| **`9`** | Outra atividade técnico-científica | `f_orgao` (`disabled`, lupa `orgao()`) | **`Outra atividade técnico-científica`** |
| **`B`** | Conselhos, Comissões e Consultoria | `f_orgao` (`disabled`, lupa `orgao()`) | **`Cargo ou função`** |

- **Regra condicional de `f_curso` em `Ensino` (`f_natur_ativ=4`):**
  - Em `401` (`Graduação`), `f_curso` é **obrigatório** no `Salvar`.
  - Em `405`, `406` e `409` (`Outro`), `f_curso` continua visível e `disabled`, mas o formulário **salva normalmente sem curso**.

---

### 2.2 Família `PKG_REVISOR` (`MB`, `MA`, `RV`, `RA`) — Hierarquia de 2 Níveis
- **16 hidden inputs compartilhados pelas 4 variantes:**
  `f_nme_agencia_h`, `f_seq_per`, `f_natur`, `f_issn`, `f_issn_h`, `f_cod_inst`, `f_cod_inst2`, `f_instold`, `f_inst_old`, `f_origem`, `f_ctr`, `f_cod`, `f_codinst`, `f_seq_ativ`, `f_seq_hist`, `f_seq_funcao_ativ`.
- **Diferenças entre as 4 variantes (`f_natur`):**
  - **`MB` (`Membro de corpo editorial`)** e **`RV` (`Revisor de periódico`)**: `f_nme_agencia` (`disabled`, `maxlength="255"`) é preenchido via lupa **`periodico()`** (que popula `f_nme_agencia`, `f_nme_agencia_h`, `f_seq_per`, `f_issn`, `f_issn_h`).
  - **`MA` (`Membro de comitê de assessoramento`)**: `f_nme_agencia` é preenchido via lupa **`agencia()`** (`pkg_revisor.agencia`, populando `f_nme_agencia`, `f_nme_agencia_h`, `f_cod_inst`, `f_cod_inst2`) + campo adicional obrigatório **`input[name="f_comite"]`** (`maxlength="200"`).
  - **`RA` (`Revisor de projeto de agência de fomento`)**: `f_nme_agencia` via lupa **`agencia()`**, sem `f_comite`.
- **Fluxo de Reabertura e Exclusão em 2 Níveis:**
  1. Na lista principal (`pkg_revisor.lista?f_natur=MB|MA|RV|RA`), clicar no periódico ou agência abre o nível intermediário **`PKG_REVISOR.lista_periodico`** (que lista os períodos de vínculo naquele periódico/agência).
  2. Clicar no período abre **`PKG_REVISOR.inclui?...&f_origem=P&f_seq_funcao_ativ=1`**.
  3. Clicar em **Excluir** dentro de `PKG_REVISOR.inclui` executa **exclusão imediata** (sem `confirm()` nem `.caixaMsg`) e, se for o único período daquele periódico/agência, **remove automaticamente o registro-pai** da lista principal.

---

### 2.3 `Áreas de atuação` (`prc_area_atuacao` / `form[name="GN_AREA_ATU"]`)
- **5 hidden inputs:** `f_cod`, `f_area_l`, `f_ctr`, `f_setor_prod`, `f_privacidade`.
- **Funcionamento da grade:**
  - Permite adicionar áreas pelo campo suggest (`"Digite, selecione ou inclua uma nova área de conhecimento..."`), pelo modal inline **`Listar todos`** (`Seleção de área`: árvore CNPq de 4 níveis `Grande Área → Área → Subárea → Especialidade`) ou pelo modal inline **`Incluir nova`** (`Inclusão de área`: input `Área:` + escolha da `Grande Área / Área` na árvore).
  - As áreas selecionadas e sua ordem (`1º`, `2º`, `3º`...) são serializadas no hidden **`f_area_l`**.
