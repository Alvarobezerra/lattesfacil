# Auditoria Completa — Aba Produções (30 Subitens em 3 Submenus: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todos os **30 subitens** da aba **Produções** da Plataforma Lattes:
  - **Produção Bibliográfica (10 subitens / 11 variantes)**
  - **Produção Técnica (16 subitens)**
  - **Outra Produção Artística/Cultural (4 subitens)**
- **Status F4/F5 + F7:** **100% dos motores de formulário da aba Produções foram validados com salvamento real, reabertura persistida e exclusão imediata** (`Artigo completo`, `Artigo aceito`, `Livro`, `Capítulo`, `Anais`, `Apresentação`, `Prefácio/posfácio`, `Trabalhos técnicos`, `Processos ou técnicas`, `Curso de curta duração ministrado` e `Artes cênicas`), mantendo todos os registros originais do currículo intactos.

---

## 1. Arquitetura dos Motores de Formulário da Aba Produções

Todos os 30 subitens da aba **Produções** são governados por **8 motores de formulário** no Lattes, cada um com seu conjunto de `<input type="hidden">`, regras de abertura e particularidades de DOM:

| # | Motor no Lattes (`form[name]`) | Subitens Atendidos (Total: 30) | Hidden Inputs Principais | Regra de Abertura |
| --- | --- | --- | --- | --- |
| **M1** | `PKG_ARTIGO.FORM` (`GN_ARTIGO`) | 1. Artigos completos publicados em periódicos | `f_autores_l`..`l4`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_seq_per`, `f_cod_doi`, `f_issn_h` | **Wizard 2 passos (`findp` → `finfivip`)**: via DOI ou busca de periódico + `ISSN`, `Volume` e `Página inicial` (que chegam `disabled=true` no form) |
| **M2** | `PKG_ARTIGO_PR.FORM` (`GN_ARTIGO`) | 2. Artigos aceitos para publicação | **21 hidden inputs:** `F_COD_PROD`, `f_titulo_periodico_h`, `f_titulo_h`, `f_ano_h`, `f_cod_doi_h`, `f_issn_h`, `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`..`l4`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_seq_per`, `f_cod_doi`, `start`, `finish`, `status` | **Sem modal prévio de DOI** (auto-abre com 0 itens); `f_titulo_periodico` e `f_issn` são `disabled=true` e preenchidos via lupa **`periodico()`** (`prc_periodico_jcr`) ou DOI inline |
| **M3** | `PKG_LVR_CAP.FORM_LVR` e `FORM_CAP` | 3. Livros publicados ou organizados<br>4. Capítulos de livros publicados | `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_cod_doi`, `F_COD_PROD` (hidden em Capítulo) | **Wizard 2 passos (`winLivrosCaps`)**: Passo 1 exige `Tipo` (`Livro`/`Capitulo`) + `DOI/ISBN` válido via `prc_valida_issn`; Passo 2 exige `ISBN` + `Ano` + `Autor/Editor` |
| **M4** | `PKG_TRABALHO.FORM` (`GN_TRABALHO`) e `PKG_TEXTO.FORM` | 5. Trabalhos publicados em anais de eventos<br>6. Texto em jornal ou revista (magazine) | `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` | **Direta** (sem wizard de DOI/ISBN; `f_cod_doi` fica no topo do próprio form) |
| **M5** | `PRC_BIB_*` (`GN_BIB`) | 7. Partitura musical (`1B`)<br>8. Tradução (`1A`)<br>9. Prefácio, posfácio (`1C`)<br>10. Outra produção bibliográfica (`1Z`) | **7 hidden inputs:** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` (`+ F_COD_PROD` hidden em `1Z`) | **Direta** (auto-abre quando a lista tem `0` itens) |
| **M6** | `PKG_RELATORIO.FORM`, `PKG_ASSESSORIA_CONSULTORIA.FORM`, `PKG_EXTENSAO_TECNOLOGICA.FORM`, `PKG_PRODUTO.FORM`, `PKG_PROCESSO.FORM` (`GN_RELATORIO` / `GN_PRODUTO` / `GN_PROCESSO`) | 11. Trabalhos técnicos<br>12. Assessoria e consultoria<br>13. Extensão tecnológica<br>14. Produtos<br>15. Processos ou técnicas | `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` (`+ F_COD_PROD` hidden em Extensão tecnológica) | **Direta** (em `Produtos` e `Processos`, `f_sta_inovacao = Sim` revela e exige `f_txt_potencial`, `maxlength="400"`) |
| **M7** | `PRC_TEC_*` e `PRC_MIDIAS_SOCIAIS` (`GN_TEC`) | 16. Apresentação de trabalho e palestra (`2J`)<br>17. Cartas, mapas ou similares (`2A`)<br>18. Curso de curta duração ministrado (`2B`)<br>19. Material didático ou instrucional (`2C`)<br>20. Editoração (`2D`)<br>21. Manutenção de obra artística (`2E`)<br>22. Maquete (`2F`)<br>23. Entrevistas, mesas redondas e mídia (`2G`)<br>24. Relatório de pesquisa (`2H`)<br>25. Redes sociais, websites e blogs (`2L`)<br>26. Outra produção técnica (`2Z`) | **7 hidden inputs:** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` (`+ F_COD_PROD` hidden em `2C`, `2F`, `2H`, `2Z`) | **Direta** (auto-abre quando a lista tem `0` itens) |
| **M8** | `PKG_ARTE_NOVA.FORM` (`GN_ARTE`) | 27. Artes cênicas (`F_TIPO=AC`)<br>28. Música (`F_TIPO=MU`)<br>29. Artes visuais (`F_TIPO=AV`)<br>30. Outra produção artística/cultural (`F_TIPO=OU`) | `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`, `F_TIPO` | **Direta** (auto-abre quando a lista tem `0` itens) |

*(Nota: `Programa de computador sem registro` aparece no menu de Produção Técnica do Lattes, mas utiliza o motor `PKG_PATENTE_REGISTRO.FORM?f_cod_tipo=PS`, auditado em detalhe junto à família de Patentes e Registros e no Lote 1 Técnico).*

---

## 2. Regras Críticas Descobertas ao Vivo para Preenchimento Externo (Autofill)

### 2.1 Armadilhas de Rádios com `value=""` e `<select>` com Espaço à Direita (`PRC_BIB_*` e `PRC_TEC_*`)
1. **Rádios `F_COD_PROD` com `value=""` no DOM (`Prefácio, posfácio`, `Curso de curta duração ministrado`, etc.):**
   - Confirmado ao vivo no F4/F5 + F7 de `Prefácio, posfácio` (`PRC_BIB_PREFACIO`) e `Curso de curta duração ministrado` (`PRC_TEC_CURSO`): os `<input type="radio" name="F_COD_PROD">` possuem **`value=""`** no HTML real!
   - **Como o robô deve selecionar:** localizar o rádio pelo **rótulo adjacente ou pelo índice (`0, 1, 2, 3...`)** e acionar `.click()` (que dispara o handler inline do Lattes), em vez de buscar apenas por `input.value === codigo`.
2. **Espaço à direita obrigatório em `<select name="f_sub_tipo">` (`Prefácio, posfácio`):**
   - Os valores reais das `<option>` são **`"31 "` (`Livro`)**, **`"32 "` (`Revistas ou periódicos`)** e **`"33 "` (`Outra`)** — todos com espaço à direita. Se o spec ou robô fizer `.trim()`, o `<select>` não seleciona a opção.

### 2.2 Regras Exclusivas de Validação (`check()` / `pre_check()`)
1. **`Artigos aceitos para publicação` (`PKG_ARTIGO_PR.form`):**
   - **Regra invertida de ano:** diferente de todas as produções publicadas (onde `f_ano` não pode ser maior que o ano atual), em `Artigos aceitos` o Lattes bloqueia qualquer ano menor que o ano corrente:
     > `"Ano previsto para publicação não pode ser menor que o ano atual."` (`f_ano >= 2026`).
   - Exige periódico selecionado via lupa `periodico()` (`prc_periodico_jcr`) ou DOI com **ISSN válido** (`f_titulo_periodico` e `f_issn` são `disabled=true`).
2. **`Livros e Capítulos` (`PKG_LVR_CAP.FORM_LVR` e `FORM_CAP`):**
   - O wizard inicial `winLivrosCaps` valida o dígito verificador do ISBN via `prc_valida_issn` antes mesmo de abrir o formulário.
   - Em **Livro**, `F_COD_PROD` (`Livro publicado` / `Organização de obra publicada`) e `f_edicao` (`Número da edição/revisão`, `maxlength="3"`) são **obrigatórios**; `f_sub_prod` (`Natureza`) é `disabled=true` e preenchido via lupa **`dominio()`** (`1#Coletânea`, `2#Texto integral`, `3#Verbete`, `4#Outro`), sendo apagado (`onclick="apaga();"`) se o usuário trocar `F_COD_PROD`.
   - Em **Capítulo**, a tradução do título usa **`f_titulo_cap_en`** (e não `f_titulo_en`), e `f_pag_ini` é obrigatório.
3. **`Produção Artística/Cultural` (`PKG_ARTE_NOVA.FORM?F_TIPO=AC|MU|AV|OU`):**
   - **Regra condicional oculta descoberta no F7 (`Artes cênicas`, `Música`, `Outra artística`):** quando o checkbox `f_inedito` (`Ineditismo da obra`) é marcado e `f_dta_ini` (`Data de estréia`) é preenchida, o campo **`f_local_estreia` (`Local de estréia`) torna-se obrigatório** (`"Informe o local de estréia"`).
   - **Diferenças de obrigatoriedade entre as 4 variantes de `PKG_ARTE_NOVA`:**
     - Em ** todas as 4 variantes (`AC`, `MU`, `AV`, `OU`)**, além de `Natureza`, `Título`, `Ano` e `Autores`, são **obrigatórios**: `f_meio` (`Meio de divulgação`), `f_tpo_ativ` (`Atividade dos autores`), `f_inst` (`Instituição promotora do evento`) e `f_cidade` (`Cidade do evento`)!
     - Em **`AC` (`Artes cênicas`)** e **`MU` (`Música`)**, também são **obrigatórios**: `f_tpo_evento` (`Tipo de evento`) e `f_duracao` (`Duração (minutos)`).
     - Em **`MU` (`Música`)**, existe um campo adicional **obrigatório**: **`f_form_instr`** (`Formação instrumental`, `maxlength="255"`).
     - Em **`AV` (`Artes visuais`)**, `f_tpo_evento` é obrigatório, **não** existe `f_duracao` nem `f_inedito`/`f_dta_ini`/`f_local_estreia`, e entra o checkbox `f_itinerante` (`Itinerante`).
     - Em **`OU` (`Outra produção artística`)**, `f_natureza` (`maxlength="100"`), `f_tpo_evento` (`maxlength="28"`, opcional) e `f_tpo_ativ` (`maxlength="50"`, obrigatório) são `<input type="text">` livres (em vez de `<select>`), e `f_duracao` é obrigatório.
4. **Inovação (`f_sta_inovacao`) em Produção Técnica (`Produtos`, `Processos ou técnicas`, `Software sem registro`):**
   - Quando `f_sta_inovacao = Sim`, revela `<tr id="potencial">` com `<textarea name="f_txt_potencial" maxlength="400">`, que passa a ser **obrigatório** (`"Informe o potencial de inovação"`).
5. **Limites curtos (`maxlength="30"`) de Cidade:**
   - Atenção ao preencher cidades: enquanto na maioria das produções técnicas e artísticas `f_cidade` aceita `255` caracteres, o limite é de apenas **`30` caracteres** em:
     - `Trabalhos em anais`: `f_cidade_evento` (`30`) e `f_cidade_ed` (`30`)
     - `Livros` e `Capítulos`: `f_cidade_ed` (`30`)
     - `Texto em jornal/revista`: `f_local` (`30`)
     - `Partitura musical`: `f_cidade` (`30`)
     - `Tradução`, `Prefácio/posfácio` e `Outra produção bibliográfica`: `f_cidade` (`30`)
6. **Normalização de Aspas no Servidor (`f_titulo`):**
   - Em `Apresentação de trabalho` e `Trabalhos em anais`, aspas duplas `"..."` enviadas em `f_titulo` são convertidas pelo servidor do CNPq para aspas simples `'...'` ao salvar.

---

## 3. Matriz Completa dos 30 Subitens de Produções × Divergências nos Specs (`itens/especificacao/`)

| # | Submenu | Subitem | Endpoint | Status F7 (Save + Re-open + Delete) | Principais Divergências em `itens/especificacao/` |
| --- | --- | --- | --- | --- | --- |
| 1 | Bibliográfica | **Artigos completos em periódicos** | `PKG_ARTIGO.form` | ✔ Validado | `F_IDIOMA` truncado em 80 opções (`"Canadá"` incluso) |
| 2 | Bibliográfica | **Artigos aceitos para publicação** | `PKG_ARTIGO_PR.form` | ✔ **Validado e limpo** (`0` itens) | `F_IDIOMA` sem catálogo no app (renderiza texto livre); labels crus `F_RELEV` e `F_STA_DIVULGACAO_CIENTIFICA`; falta regra `f_ano >= ano_atual` e lupa `periodico()` |
| 3 | Bibliográfica | **Livros publicados ou organizados** | `PKG_LVR_CAP.FORM_LVR` | ✔ **Validado e limpo** (`0` itens) | `f_titulo` com `maxlength: 255` no spec (real = `400`); `f_ref_en` com `3900` (real = `3800`); `F_COD_PROD` sem `obrigatorio: true` |
| 4 | Bibliográfica | **Capítulos de livros publicados** | `PKG_LVR_CAP.FORM_CAP` | ✔ **Validado e limpo** (`0` itens) | `f_ref_en` com `3900` (real = `3800`); tradução usa `f_titulo_cap_en` |
| 5 | Bibliográfica | **Texto em jornal ou revista** | `PKG_TEXTO.form` | Motor M4 validado | `F_COD_PROD` (`Jornal` / `Revista`) com `obrigatorio: false` no spec (é obrigatório) |
| 6 | Bibliográfica | **Trabalhos publicados em anais** | `pkg_trabalho.form` | ✔ **Validado e limpo** (`17` originais intactos) | `f_pais` e `F_IDIOMA` truncados em 80 opções (`"Canadá"` em idioma) |
| 7 | Bibliográfica | **Apresentação de trabalho e palestra** | `prc_tec_apres` | ✔ **Validado e limpo** (`9` originais intactos) | `f_pais` e `F_IDIOMA` truncados em 80 opções (`"Canadá"` em idioma) |
| 8 | Bibliográfica | **Partitura musical** | `prc_bib_partitura` | Motor M5 validado | `F_COD_PROD` com `obrigatorio: false` e `value=""` nos rádios |
| 9 | Bibliográfica | **Tradução** | `prc_bib_traducao` | Motor M5 validado | `F_COD_PROD` com `obrigatorio: false` e `value=""` nos rádios |
| 10 | Bibliográfica | **Prefácio, posfácio** | `prc_bib_prefacio` | ✔ **Validado e limpo** (`0` itens) | `F_COD_PROD` com `value=""` nos rádios; `f_sub_tipo` exige espaço à direita (`"31 "`, `"32 "`, `"33 "`); campos reais da obra são `f_autor_trad` e `f_tit_obra` |
| 11 | Bibliográfica | **Outra produção bibliográfica** | `prc_bib_outraprod` | Motor M5 validado | `f_natureza` texto livre obrigatório (`max 100`) |
| 12 | Técnica | **Assessoria e consultoria** | `PKG_ASSESSORIA_CONSULTORIA.form` | Motor M6 validado | **Sem arquivo em `itens/especificacao/`** |
| 13 | Técnica | **Extensão tecnológica** | `PKG_EXTENSAO_TECNOLOGICA.form` | Motor M6 validado | Mesmo motor `GN_RELATORIO` com `F_COD_PROD` hidden |
| 14 | Técnica | **Programa de computador s/ registro** | `PKG_PATENTE_REGISTRO.FORM?f_cod_tipo=PS` | Motor Patentes validado | `f_sta_inovacao = Sim` exige `f_txt_potencial`; `f_inst_financ`, `f_finalidade`, `f_plataforma` obrigatórios |
| 15 | Técnica | **Produtos** | `pkg_produto.form` | Motor M6 validado | `F_COD_PROD` (Tipo) e `F_SUB_PROD` (Natureza) obrigatórios; condicional `f_sta_inovacao` |
| 16 | Técnica | **Processos ou técnicas** | `pkg_processo.form` | ✔ **Validado e limpo** (`0` itens) | Condicional `f_sta_inovacao = Sim` → `f_txt_potencial` obrigatório validado ao vivo |
| 17 | Técnica | **Trabalhos técnicos** | `pkg_relatorio.form` | ✔ **Validado e limpo** (`0` itens) | `F_COD_PROD` com `obrigatorio: false` no spec (é obrigatório) |
| 18 | Técnica | **Cartas, mapas ou similares** | `prc_tec_carta` | Motor M7 validado | `F_COD_PROD` com `obrigatorio: false` e `value=""` nos rádios |
| 19 | Técnica | **Curso de curta duração ministrado** | `prc_tec_curso` | ✔ **Validado e limpo** (`0` itens) | Exibe labels técnicos crus `F_COD_PROD`, `F_RELEV`, `F_STA_DIVULGACAO_CIENTIFICA` na UI do app |
| 20 | Técnica | **Desenv. de material didático** | `prc_tec_desen` | Motor M7 validado | `f_natureza` texto livre obrigatório (`max 100`) |
| 21 | Técnica | **Editoração** | `prc_tec_edit` | Motor M7 validado | `F_COD_PROD` obrigatório com `value=""` nos rádios |
| 22 | Técnica | **Manutenção de obra artística** | `prc_tec_manut` | Motor M7 validado | `F_COD_PROD` (Tipo) obrigatório + `F_SUB_PROD` (`17..23`) |
| 23 | Técnica | **Maquete** | `prc_tec_maquete` | Motor M7 validado | Sem `F_COD_PROD` visível (`f_titulo`, `f_ano` e `Autores` obrigatórios) |
| 24 | Técnica | **Entrevistas, mesas redondas e mídia** | `prc_tec_radiotv` | Motor M7 validado | Grade usa rótulo `Participantes` (`f_autores_l`); `f_meio` tem apenas 3 opções (`I`, `W`, `O`) |
| 25 | Técnica | **Relatório de pesquisa** | `prc_tec_relat` | Motor M7 validado | Sem `F_COD_PROD` visível; inclui `f_projeto`, `f_paginas`, `f_inst`, `f_disp` |
| 26 | Técnica | **Redes sociais, websites e blogs** | `prc_midias_sociais` | Motor M7 validado | Sem `f_meio`; `F_COD_PROD` (`Rede Social`, `Forum`, `Blog`, `Site`) obrigatório |
| 27 | Técnica | **Outra produção técnica** | `prc_tec_outraprod` | Motor M7 validado | `f_natureza` texto livre obrigatório (`max 100`) |
| 28 | Artística | **Artes cênicas** | `pkg_arte_nova.form?F_TIPO=AC` | ✔ **Validado e limpo** (`0` itens) | 10 campos obrigatórios + condicional `f_inedito` + `f_dta_ini` → `f_local_estreia` obrigatório |
| 29 | Artística | **Música** | `pkg_arte_nova.form?F_TIPO=MU` | Motor M8 validado | 11 campos obrigatórios (inclui `f_form_instr` obrigatório) + condicional `f_inedito` |
| 30 | Artística | **Artes visuais** / **Outra artística** | `pkg_arte_nova.form?F_TIPO=AV\|OU` | Motor M8 validado | `AV`: 9 obrigatórios (sem `f_duracao`/`f_inedito`, com `f_itinerante`); `OU`: `f_natureza`, `f_tpo_evento` e `f_tpo_ativ` são inputs de texto |
