# Auditoria Completa — Aba Formação (3 Subitens / 13 Variantes: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todos os **3 subitens** da aba **Formação** da Plataforma Lattes:
  1. **Formação acadêmica/titulação** (`pkg_formacao.lista?f_tipo=FA` → **10 níveis** `4, 3, 9, 2, D, 1, 7, C, B, X`)
  2. **Pós-doutorado e/ou Livre-docência** (`pkg_formacao.lista?f_tipo=AP` → **2 níveis** `5, 6`)
  3. **Formação complementar** (`pkg_formacao_compl.lista` → **Wizard de 2 telas** `PKG_FORMACAO_COMPL.form` → `PKG_FORMACAO_COMPL.FORM2`)
- **Status F4/F5 + F7:** **100% dos 3 subitens validados com salvamento real, reabertura persistida e exclusão imediata** ([ficha-formacao.md](ficha-formacao.md)), mantendo os itens originais do currículo intactos (`6` em Formação acadêmica, `0` em Pós-doutorado/Livre-docência, `4` em Formação complementar).

---

## 1. Resumo Executivo dos 3 Subitens e Divergências nos Specs

| # | Subitem | Endpoint (`form[name]`) | Abertura Real | Teste F4/F5 + F7 (Salvar + Reabrir + Excluir) | Divergências Críticas no Spec (`itens/especificacao/`) |
| --- | --- | --- | --- | --- | --- |
| 1 | **Formação acadêmica/titulação** | `pkg_formacao.form?f_tipo=FA&f_nivel=<N>` (`GN_FORMACAO2`) | Lista → modal `selecionarNivel` (10 níveis) | ✔ **Validado e limpo** (`Mestrado` `f_nivel=3`; `6` itens originais intactos) | `f_inst` marcado `obrigatorio: false` nas 10 variantes (é obrigatório em todas); `janelas_auxiliares` omite `sele_inst(1..4)` e `curso()`; `obrigatorios_mensagens` copiado de Doutorado para todos os 10 níveis |
| 2 | **Pós-doutorado e/ou Livre-docência** (`pos_doutorado.json`) | `pkg_formacao.form?f_tipo=AP&f_nivel=5\|6` (`GN_FORMACAO2`) | Lista → modal `selecionarNivel` (2 níveis: `5` e `6`) | ✔ **Validado e limpo nos 2 níveis** (`Pós-Doutorado` `5` e `Livre Docência` `6`; `0` itens restantes) | `f_inst` marcado `obrigatorio: false` nos 2 níveis; `janelas_auxiliares` omite `sele_inst(1)`; `obrigatorios_mensagens` traz campos inexistentes (`Tipo de doutorado`, `Curso`) |
| 3 | **Formação complementar** (`formacao_complementar.json`) | `PKG_FORMACAO_COMPL.form` → `PKG_FORMACAO_COMPL.FORM2` | Lista → Wizard em **2 telas** (`Avançar` → `Salvar`) | ✔ **Validado e limpo nas 2 telas** (`Curso De Curta Duração`; `4` itens originais intactos) | **FALHA BLOQUEANTE:** **100% da Tela 2 (`FORM2`) está ausente** no `formacao_complementar.json` (`f_ano_ini`, `f_ano_fim`, `F_BOLSA`, `f_nme_agencia`, `Palavras-chave`, `Visibilidade`); `curso()` ausente em `janelas_auxiliares` da Tela 1 |

---

## 2. Dinâmica Detalhada para Preenchimento Externo (Autofill)

### 2.1 `Formação acadêmica/titulação` e `Pós-doutorado / Livre-docência` (`form[name="GN_FORMACAO2"]`)

#### A) Todos os `<input type="hidden">` (`24` campos em `GN_FORMACAO2`)
`f_carga`, `f_agencia`, `f_ctr`, `f_cod`, `f_seq`, `f_cod_inst`, `f_cod_curso`, `f_cod_inst2`, `f_cod_curso2`, `f_inst_old`, `f_curso_old`, `f_tipo`, `f_nivel`, `f_id_orientador`, `f_seq_orientacao`, `f_cod_inst_dout`, `f_cod_inst2_dout`, `f_cod_inst_dout_sw`, `f_cod_inst2_dout_sw`, `f_cod_inst_dout_ct`, `f_cod_inst2_dout_ct`, `f_plv_l`, `f_setor_l`, `f_area_l`.
*(Há ainda um `<form>` auxiliar no rodapé com 6 hidden inputs de controle: `f_cod_chk`, `f_seq_chk`, `start`, `finish`, `status`, `f_nme_orientador`.)*

#### B) Dinâmica dos 4 modos de `f_tpo_doutorado` (`onclick="testa_mudanca_de_rotulo(this.value)"`)
- Presente com **4 opções** em `Doutorado` (`f_nivel=4`) e com **2 opções** (`normal` / `sanduíche`) em `Mestrado` (`3`), `Mestrado Profissional` (`9`) e `Graduação` (`1`):

| Modo (`f_tpo_doutorado`) | Rótulo `#lblIdInst` de `f_inst` | Campos Extras Revelados | Lupas de Instituição Secundária Acionadas | Hidden Inputs Populados pelas Lupas Extras |
| --- | --- | --- | --- | --- |
| **`normal`** (`N`, idx 0) | `"Instituição"` | Nenhum | Apenas `sele_inst(1)` (principal) | `f_cod_inst`, `f_cod_inst2` |
| **`sanduíche`** (`S`, idx 1) | `"Instituição outorgadora do título de doutor"` | `f_orient_dout` (texto livre), `f_inst_dout` (`disabled`), `f_meses_sw` (`maxlength="2"`) | `sele_inst(2);return false;` (ao lado de `f_inst_dout`) | `f_cod_inst_dout`, `f_cod_inst2_dout` |
| **`co-tutela`** (`C`, idx 2) | `"Instituição outorgadora do título de doutor"` | `f_orient_dout` (texto livre), `f_inst_dout` (`disabled`) | `sele_inst(2);return false;` (ao lado de `f_inst_dout`) | `f_cod_inst_dout`, `f_cod_inst2_dout` |
| **`co-tutela/sanduíche`** (`CS`, idx 3) | `"Instituição outorgadora do título de doutor"` | **Sanduíche:** `f_orient_dout_sw`, `f_inst_dout_sw` (`disabled`), `f_meses_sw_aux` (`max 2`)<br>**Co-tutela:** `f_orient_dout_ct`, `f_inst_dout_ct` (`disabled`) | `sele_inst(3);return false;` (`f_inst_dout_sw`)<br>`sele_inst(4);return false;` (`f_inst_dout_ct`) | `f_cod_inst_dout_sw`, `f_cod_inst2_dout_sw`<br>`f_cod_inst_dout_ct`, `f_cod_inst2_dout_ct` |

> **Observação importante:** Não existe lupa para orientador de sanduíche/co-tutela (`f_orient_dout`, `f_orient_dout_sw`, `f_orient_dout_ct`) — todos são campos `<input type="text" maxlength="60">` de digitação livre.

#### C) Comportamento de `F_STATUS` e `F_BOLSA`
- **`F_STATUS` (`onclick="alteraRotuloAno(this.value);"`):**
  - `em andamento` (`N`) e `concluído` (`S`): `#lblAnoFim` = `"Conclusão (ano)"`; todos os campos permanecem visíveis e `disabled=false` (a diferença ocorre na validação `check()`, onde `concluído` exige `f_ano_fim`, `f_mes_obten`/`f_ano_obten` e `f_titulo`).
  - `incompleto` (`I`): muda `#lblAnoFim` para **`"Interrupção (ano)"`**.
- **`F_BOLSA` (`Sim` / `Não`):**
  - `f_nme_agencia` (`disabled=true`) e sua lupa `onclick="agencia();return false;"` permanecem sempre visíveis no DOM; marcar `Sim` torna obrigatório o preenchimento via lupa `agencia()` (que popula `f_nme_agencia` + hidden `f_agencia`).
- **Normalização do servidor na reabertura (`f_curso`):**
  - Ao selecionar um curso na lupa `curso()`, o campo `f_curso` exibe `"NOME DO CURSO(CODIGO_CAPES)"` antes de salvar; ao reabrir o item persistido, o servidor retorna apenas `"NOME DO CURSO"` (sem o sufixo entre parênteses).

#### D) Matriz Comparativa das 12 Variantes de `pkg_formacao.form` (`FA` 10 níveis + `AP` 2 níveis)

| Nível (`f_tipo` / `f_nivel`) | `f_tpo_doutorado` | `f_curso` (lupa `curso()`) | `f_carga` (`max 4`) | `F_STATUS` + `f_ano_ini`/`fim` | `f_mes_obten` / `f_ano_obten` | `F_BOLSA` + `f_nme_agencia` | `f_titulo` (rótulo) | `f_orient` / `f_coorient` | Grades (`Palavras`, `Áreas`, `Setores`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`FA` · `4` (Doutorado)** | 4 opções (`N,S,C,CS`) | ✔ | — | ✔ | ✔ | ✔ | `"Título da dissertação/tese"` | `f_orient` + `f_coorient` | 3 grades |
| **`FA` · `3` (Mestrado)** | 2 opções (`N,S`) | ✔ | — | ✔ | ✔ | ✔ | `"Título da dissertação/tese"` | `f_orient` + `f_coorient` | 3 grades |
| **`FA` · `9` (Mestrado Prof.)** | 2 opções (`N,S`) | ✔ | — | ✔ | ✔ | ✔ | `"Título da dissertação/tese"` | `f_orient` + `f_coorient` | 3 grades |
| **`FA` · `2` (Especialização)** | — | ✔ | ✔ | ✔ | — | ✔ | `"Título monografia"` | Apenas `f_orient` | — |
| **`FA` · `D` (Residência médica)** | — | — | — | ✔ | — | ✔ | `"Residência médica em"` | `f_orient` = **`"Número do registro"`** | 3 grades |
| **`FA` · `1` (Graduação)** | 2 opções (`N,S`) | ✔ | — | ✔ | — | ✔ | `"Título monografia"` | Apenas `f_orient` | — |
| **`FA` · `7` (Ensino Técnico)** | — | ✔ | — | ✔ | — | ✔ | — | — | — |
| **`FA` · `C` (Ensino Médio)** | — | — | — | ✔ | — | — | — | — | — |
| **`FA` · `B` (Ensino Fund.)** | — | — | — | ✔ | — | — | — | — | — |
| **`FA` · `X` (Aperfeiçoamento)** | — | ✔ | ✔ | ✔ | — | ✔ | `"Título monografia"` | Apenas `f_orient` | — |
| **`AP` · `5` (Pós-Doutorado)** | — | — | — | ✔ | — | ✔ | — | — | Apenas `Áreas` (1 grade) |
| **`AP` · `6` (Livre Docência)** | — | — | — | — | ✔ | — | `"Título do trabalho"` | — | 3 grades |

---

### 2.2 `Formação complementar` (`PKG_FORMACAO_COMPL.form` → `PKG_FORMACAO_COMPL.FORM2`)

- **Fluxo obrigatório em 2 telas (Wizard):**
  1. **Tela 1 (`PKG_FORMACAO_COMPL.form?f_cod=<cod>&f_tipo=FA`):**
     - **10 hidden inputs:** `f_ctr`, `f_cod`, `f_seq`, `f_cod_inst`, `f_cod_curso`, `f_cod_inst2`, `f_cod_curso2`, `f_inst_old`, `f_curso_old`, `f_tipo`.
     - **Campos visíveis:**
       - `select[name="f_nivel"]` (obrigatório): `F` (`Curso De Curta Duração`), `8` (`Extensão Universitária`), `E` (`Mba`), `Y` (`Outros`).
       - `input[name="f_inst"]` (`disabled`, `maxlength="75"`, obrigatório): preenchido via lupa `sele_inst()`.
       - `input[name="f_curso"]` (`disabled`, `maxlength="50"`, obrigatório): preenchido via lupa `curso()` (exibe `"Nome do Curso()"` antes de salvar e normaliza para `"Nome do Curso"` na reabertura).
       - `input[name="f_carga"]` (`maxlength="4"`, opcional): Carga Horária.
       - `input[type="radio"][name="F_STATUS"]` (obrigatório): `em andamento` (`N`), `concluído` (`S`), `incompleto` (`I`).
     - **Transição:** Clicar no botão **Avançar** valida os 4 obrigatórios da Tela 1 e submete para `PKG_FORMACAO_COMPL.FORM2`.
  2. **Tela 2 (`PKG_FORMACAO_COMPL.FORM2` — ausente no spec atual):**
     - **Abas:** `Período (ano)`, `Bolsa`, `Palavras-chave`, `Visibilidade`.
     - **Campos visíveis:**
       - `input[name="f_ano_ini"]` (`maxlength="4"`, obrigatório): `"Início"`.
       - `input[name="f_ano_fim"]` (`maxlength="4"`):
         - Se `F_STATUS = concluído`: rótulo `"Conclusão"`, **obrigatório**.
         - Se `F_STATUS = incompleto`: rótulo `"Interrupção"`, **obrigatório** (`"Informe o ano de Conclusão"`).
         - Se `F_STATUS = em andamento`: campo fica **`disabled=true`** e opcional.
       - `input[type="radio"][name="F_BOLSA"]`: `Sim` (`S`) / `Não` (`N`, default).
       - `input[name="f_nme_agencia"]` (`disabled`, `maxlength="75"`): preenchido via lupa `agencia()` (obrigatório quando `F_BOLSA = Sim`).
       - Grade **`Palavras-chave`** (até 6 palavras) e seletor de **`Visibilidade`** (`Público`/`Privado`).
     - **Salvamento e Exclusão:** Os botões **Salvar** e **Excluir** ficam na **Tela 2 (`FORM2`)**. A exclusão é **imediata sem `confirm()` nativo nem modal `.caixaMsg`**.
