# Auditoria Completa — Abas Orientações, Bancas e Citações (Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todas as **3 abas finais** do menu da Plataforma Lattes:
  1. **Orientações (2 subitens / 13 variantes):** `Orientações e supervisões concluídas` (`pkg_orient.form?f_tipo=C` — 7 naturezas) e `Orientações e supervisões em andamento` (`pkg_orient.form?f_tipo=A` — 6 naturezas).
  2. **Bancas (2 subitens / 11 variantes):** `Participação em bancas de trabalhos de conclusão` (`PKG_BANCA_TRAB.form` — 6 naturezas) e `Participação em bancas de comissões julgadoras` (`PKG_BANCA_JULG.form` — 5 naturezas).
  3. **Citações (5 subitens / 5 bases):** `Web of Science (f_base=1)`, `SciELO (f_base=2)`, `SCOPUS (f_base=3)`, `Google Scholar (f_base=4)`, `Outras bases (f_base=99)` (`prc_indicadores`).
- **Status F4/F5 + F7:** **100% dos formulários validados com salvamento real, reabertura persistida e exclusão** ([ficha-orientacao.md](ficha-orientacao.md), [ficha-bancas.md](ficha-bancas.md), [ficha-citacoes.md](ficha-citacoes.md)), mantendo todas as listas e bases originais do currículo limpas (`0` itens).

---

## 1. Aba Orientações (`pkg_orient.form?f_tipo=C|A`)

### 1.1 Todos os `<input type="hidden">` (`24` campos)
`f_sub_prod`, `f_agencia`, `f_ctr`, `f_ctr_natur`, `f_cod`, `f_seq`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_cod_curso`, `f_cod_curso2`, `f_cod_inst`, `f_cod_inst2`, `f_inst_old`, `f_curso_old`, `f_tipo`, `f_id_orientado`, `f_seq_form_orientado`, `f_cod_chk`, `f_seq_chk`, `start`, `finish`, `status`, `f_nme_orientado`.

### 1.2 Dinâmica das 4 Lupas e Regras Condicionais para Preenchimento Externo
1. **Diferença estrutural entre `Concluída (f_tipo=C)` e `Em andamento (f_tipo=A)`:**
   - **`Concluída (C)`** possui **7 naturezas (`F_COD_PROD`)**, incluindo `Trabalho de conclusão de curso de graduação` (TCC), e permite salvar `Iniciação Científica` **sem** preencher `f_curso`.
   - **`Em andamento (A)`** possui apenas **6 naturezas (`F_COD_PROD`)** (**não existe TCC de graduação em andamento no Lattes!**) e exige `f_curso` no salvamento em branco. *(No spec `orientacao_andamento.json`, TCC foi incluído indevidamente como 7ª opção).*
2. **Regra de `f_tpo_orient` (`Orientador principal` / `Co-orientador` — `onclick="test_ori()"`):**
   - Só aceita marcação quando `F_COD_PROD` é **`Dissertação de mestrado`** ou **`Tese de doutorado`** (onde é obrigatório).
   - Em **`Supervisão de pós-doutorado`** e demais naturezas, os rádios não têm atributo `disabled` no HTML, mas `test_ori()` **desmarca imediatamente qualquer clique (`checked = false`)**.
3. **As 4 Lupas de `pkg_orient.form`:**
   - **`dominio()` em `f_dsc_outra` (`Tipo`)**:
     - Em `Dissertação de mestrado`: abre modal com 2 opções (`Acadêmico` e `Profissional`), gravando o código no hidden **`f_sub_prod`**.
     - Em `Orientação de outra natureza`: abre modal com **1 única opção**: `{"text": "Outro Tipo", "value": "Outro Tipo"}`.
   - **`sele_inst()` em `f_inst`**: preenche `f_inst` (`disabled`, preservando espaço final ex.: `"Universidade Federal do Maranhão "`) + hidden **`f_cod_inst`** / **`f_cod_inst2`**.
   - **`curso()` em `f_curso`** *(depende de `f_cod_inst` + `F_COD_PROD`)*: lista os cursos da instituição; antes de salvar mostra `"NOME DO CURSO(CODIGO_CAPES)"` e popula hidden **`f_cod_curso`** / **`f_cod_curso2`**; ao reabrir após salvar, o servidor remove `(CODIGO_CAPES)` do texto visível.
   - **`agencia()` em `f_nme_agencia`**: marca `F_BOLSA = sim`, abre `prc_agencia` e popula `f_nme_agencia` (`disabled`) + hidden **`f_agencia`**.
4. **Duas formas de Exclusão em Orientações:**
   - Clicar no link `Excluir` na linha da tabela `pkg_orient.lista` dispara `window.confirm("Deseja excluir o item selecionado?")` nativo.
   - Clicar no botão `Excluir` dentro do formulário `pkg_orient.form` aberto executa **exclusão imediata** sem `confirm()`.

---

## 2. Aba Bancas (`PKG_BANCA_TRAB.form` e `PKG_BANCA_JULG.form`)

### 2.1 Todos os `<input type="hidden">`
- **`PKG_BANCA_TRAB.form` (`13` hidden inputs):**
  `f_ctr`, `f_cod`, `f_seq`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_cod_curso`, `f_cod_curso2`, `f_cod_inst`, `f_cod_inst2`, `f_inst_old`, `f_curso_old`, `f_autores_l`.
- **`PKG_BANCA_JULG.form` (`14` hidden inputs — inclui `f_curso` como hidden):**
  `f_ctr`, `f_cod`, `f_seq`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_cod_curso`, `f_cod_curso2`, `f_cod_inst`, `f_cod_inst2`, `f_inst_old`, `f_curso`, `f_curso_old`, `f_autores_l`.

### 2.2 Regras Críticas para Preenchimento Externo
1. **Espaço à direita em `<select name="f_sub_prod">` (`PKG_BANCA_TRAB.form`):**
   - Campo `"Tipo (apenas para mestrado)"`: os valores reais das `<option>` têm espaço à direita: **`"34 "` (`Acadêmico`)** e **`"35 "` (`Profissional`)**.
2. **Lupas `sele_inst()` e `curso()`:**
   - Em `PKG_BANCA_TRAB.form`, usam-se `sele_inst()` (`f_inst` → `f_cod_inst`/`f_cod_inst2`) e `curso()` (`f_curso` → `f_cod_curso`/`f_cod_curso2`, com mesma remoção do sufixo `(CODIGO_CAPES)` na reabertura pós-save).
   - Em `PKG_BANCA_JULG.form`, existe apenas `sele_inst()` (`f_inst` tem typo `disable="true"` no HTML do Lattes, portanto `input.disabled` é `false` no DOM embora deva ser preenchido via `sele_inst()`).
3. **Grade `Participantes` (`f_autores_l`):**
   - Usa o mesmo componente `tabelaAutor` / `#autorHolder` de `Autores`, exigindo a inclusão do titular do currículo.
4. **Exclusão:** Imediata ao clicar em **Excluir** dentro do formulário aberto (sem `confirm()` nem `.caixaMsg`).

---

## 3. Aba Citações (`prc_indicadores?f_base=1|2|3|4|99`)

### 3.1 Todos os `<input type="hidden">` (`7` campos em `form[name="PRC_INDICADORES"]`)
`f_sta_validado`, `f_res_id`, `f_indiceh`, `f_ctr`, `f_cod`, `f_seq`, `f_base`.
*(Nota: em `f_base=2, 3, 4, 99`, `f_res_id` e `f_indiceh` ficam ocultos como `<input type="hidden">`; em `f_base=1` Web of Science, ambos são `<input type="text">` visíveis!)*

### 3.2 Matriz das 5 Bases de Citações e Dinâmica de Salvamento/Exclusão

| Código `f_base` | Base no Menu do Lattes | Campos Específicos / Diferenças | Campos Comuns Obrigatórios (todas as 5 bases) |
| --- | --- | --- | --- |
| **`1`** | **Web of Science** | `f_res_id` (`ResearcherID`, `max 13`, **obrigatório**) + `f_indiceh` (`Fator H`, `max 3`, opcional) | `f_qtd_citacoes` (`max 6`), `f_qtd_trabalhos` (`max 6`), `f_data` (`DD/MM/YYYY`, `max 10`), `f_query` (`Parâmetros da busca`, `max 400`) |
| **`2`** | **SciELO** | Apenas os 4 campos comuns | `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` |
| **`3`** | **SCOPUS** | Apenas os 4 campos comuns | `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` |
| **`4`** | **Google Scholar** | Rótulo de `f_query` muda para **`"Endereço na Web(URL) do perfil do autor"`** | `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` |
| **`99`** | **Outras bases** | Adiciona **`f_txt_base`** (`Base bibliográfica`, `max 200`, **obrigatório**) | `f_txt_base`, `f_qtd_citacoes`, `f_qtd_trabalhos`, `f_data`, `f_query` |

- **Dinâmica do botão `Excluir` em `prc_indicadores` (validado em `f_base=99`):**
  - Quando a base ainda não possui dados salvos, o formulário abre diretamente em branco **sem botão `Excluir`** (`hasExcluir = 0`).
  - Após preencher e clicar em **Salvar**, o modal fecha com `"Sucesso / A operação foi realizada com sucesso! !"`.
  - Ao reabrir a mesma base (`f_base=99`), os dados vêm **100% preenchidos** e o botão **`Excluir`** (`onclick="del();return false;"`) aparece no rodapé (`hasExcluir = 1`).
  - Clicar em **Excluir** limpa o registro **imediatamente** (sem `confirm()` nativo nem modal `.caixaMsg`), fazendo a base voltar ao estado vazio inicial (`hasExcluir = 0`).
