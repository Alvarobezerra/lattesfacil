# Auditoria Completa — Aba Eventos (2 Subitens: Lattes ao Vivo × `itens/especificacao/`)

- **Data:** 2026-11-20
- **Escopo:** Todos os **2 subitens** da aba **Eventos** da Plataforma Lattes:
  1. **Participação em eventos, congressos, exposições, feiras e olimpíadas** (`pkg_evento.lista` → `PKG_EVENTO.FORM`)
  2. **Organização de eventos, congressos, exposições, feiras e olimpíadas** (`prc_tec_demais_lista?f_cod_tipo=2G` → `PRC_TEC_ORG`)
- **Status F4/F5 + F7:** **100% dos 2 subitens validados com salvamento real, reabertura persistida e exclusão imediata** ([ficha-participacao-evento.md](ficha-participacao-evento.md)), preservando intactos os registros originais do currículo (`37` em Participação em eventos e `6` em Organização de eventos).

---

## 1. Resumo Executivo e Comparativo dos 2 Subitens

| # | Subitem | Endpoint (`form[name]`) | Hidden Inputs | Teste F4/F5 + F7 (Salvar + Reabrir + Excluir) | Divergências e Regras Críticas para o Robô |
| --- | --- | --- | --- | --- | --- |
| 1 | **Participação em eventos** | `PKG_EVENTO.FORM` (`GN_TEC`) | **3 hidden inputs:** `f_ctr`, `f_cod`, `f_seq` *(não possui grades de autores/palavras/áreas!)* | ✔ **Validado e limpo** (`37` itens originais intactos) | Cascata dinâmica `F_FORMA` (`montaTipoApres`) → popula `F_TPO` (`muda_titulo_evento`) → altera rótulo `#lblIdTitt`; modo `Ouvinte` esvazia `F_TPO` e dispensa `F_TPO` e `f_titulo` |
| 2 | **Organização de eventos** | `PRC_TEC_ORG` (`GN_TEC`) | **7 hidden inputs:** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` | ✔ **Validado e limpo** (`6` itens originais intactos) | Rádios `F_COD_PROD` (`Tipo`: `Concerto`..`Outro`) têm `value=""` no DOM (seleção por índice/rótulo) e são **obrigatórios**; `F_SUB_PROD` (`Natureza`: `24:Curadoria`, `25:Montagem`, `27:Museologia`, `26:Organização`, `28:Outra`) também é **obrigatório** |

---

## 2. Dinâmica Detalhada para Preenchimento Externo (Autofill)

### 2.1 `Participação em eventos, congressos, exposições, feiras e olimpíadas` (`PKG_EVENTO.FORM`)
- **Hidden inputs (`3` campos):** `f_ctr`, `f_cod`, `f_seq`.
- **Cascata obrigatória em 3 etapas (`F_FORMA` → `F_TPO` → `f_titulo`):**
  1. **Passo 1 — `F_FORMA` (`input[type="radio"]`, `onclick="montaTipoApres(this.value)"`):**
     - `Convidado`: popula dinamicamente `<select name="F_TPO">` com 5 opções (`Conferencista`, `Simposista`, `Moderador`, `Avaliador`, `Homenageado`).
     - `Participante`: popula dinamicamente `<select name="F_TPO">` com 3 opções (`Poster / Painel`, `Apresentação oral`, `Outras formas`).
     - `Ouvinte`: esvazia `<select name="F_TPO">` (`0` opções) e **remove a obrigatoriedade** de `F_TPO` e de `f_titulo`!
  2. **Passo 2 — `F_TPO` (`select[name="F_TPO"]`, `onchange="muda_titulo_evento()"`):**
     - O robô **só pode selecionar `F_TPO` depois de acionar `.click()` no rádio `F_FORMA`** (pois antes disso o `<select name="F_TPO">` não contém as opções daquela forma).
     - Ao selecionar `F_TPO`, `muda_titulo_evento()` reescreve o rótulo `#lblIdTitt` de `f_titulo` (ex.: `"Título da conferência..."`).
  3. **Passo 3 — Demais campos obrigatórios e lupa opcional:**
     - `select[name="F_COD_PROD"]` (`Natureza`, obrigatório): `A31` (`Congresso`), `A32` (`Seminário`), `A33` (`Simpósio`), `A34` (`Oficina`), `A35` (`Encontro`), `A36` (`Olimpíada`), `A37` (`Feira`), `A38` (`Exposição`), `A39` (`Outra`).
     - `input[name="f_nme_evento"]` (`maxlength="400"`, obrigatório): aceita digitação livre ou seleção via lupa `evento_comunicacao()` (que reaproveita nomes de eventos já cadastrados no currículo).
     - `input[name="f_ano"]` (`maxlength="4"`, obrigatório).
     - `input[name="f_titulo"]` (`maxlength="255"`, `onfocus="verifica_forma(this)"`): obrigatório quando `F_FORMA` é `Convidado` ou `Participante`; dispensado quando `Ouvinte`.
- **Exclusão:** Clicar em **Excluir** dentro de `PKG_EVENTO.FORM` executa **exclusão imediata** sem `confirm()` nem modal `.caixaMsg`.

---

### 2.2 `Organização de eventos, congressos, exposições, feiras e olimpíadas` (`PRC_TEC_ORG`)
- **Endpoint da lista no menu do Lattes:** `prc_tec_demais_lista?f_cod_tipo=2G` → `prc_tec_org`.
- **Hidden inputs (`7` campos em `GN_TEC`):** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`.
- **Campos e regras de obrigatoriedade (`check()`):**
  - `input[type="radio"][name="F_COD_PROD"]` (`Tipo`, **obrigatório**): 8 opções com `value=""` no DOM (`0: Concerto`, `1: Concurso`, `2: Congresso`, `3: Exposição`, `4: Festival`, `5: Feira`, `6: Olimpíada`, `7: Outro`) — selecionar por índice/rótulo e `.click()`.
  - `select[name="F_SUB_PROD"]` (`Natureza`, **obrigatório** — atenção: o nome no DOM é **`F_SUB_PROD`** e não `f_natureza`!):
    - `""`, `"24"` (`Curadoria`), `"25"` (`Montagem`), `"27"` (`Museologia`), `"26"` (`Organização`), `"28"` (`Outra`).
  - `input[name="f_titulo"]` (`maxlength="400"`, **obrigatório**).
  - `input[name="f_ano"]` (`maxlength="4"`, **obrigatório**).
  - Grade **`Autores`** (`f_autores_l`, **obrigatório** incluir o titular do currículo).
  - Campos opcionais de detalhamento: `f_inst` (`Instituição promotora`, `max 255`), `f_duracao` (`Duração (semanas)`, `max 5`), checkboxes `f_itinerante` (`Evento itinerante`) e `f_catalogo` (`Catálogo`), `f_local` (`max 255`), `f_cidade` (`max 255`), `f_ref` (`max 3950`), `f_titulo_en` (`max 400`), `f_ref_en` (`max 3800`) e grades `Palavras-chave`, `Áreas` e `Setores`.
- **Exclusão:** Clicar em **Excluir** dentro de `PRC_TEC_ORG` executa **exclusão imediata** sem `confirm()` nem modal `.caixaMsg`.
