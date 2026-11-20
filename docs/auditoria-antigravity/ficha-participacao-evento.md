# Ficha de validação — Participação em Eventos (`participacao_evento`)

- **Data:** 2026-11-20 · **URL no Lattes:** `PKG_EVENTO.form`
- **Como abre:** `pkg_evento.lista` → **Incluir novo item** (37 itens existentes)
- **Abas (3):** `Dados gerais`, `Traduções`, `Visibilidade` · **Listas:** nenhuma

## Fase 1 & Fase 2 — Captura e Diff (`capturas/participacao_evento.json` × `itens/especificacao/participacao_evento.json`)
- [x] Paridade de campos e `maxlength` = **0 divergências**
- **Condicionais mapeados:**
  - `F_FORMA` (`montaTipoApres`): `Convidado` popula `F_TPO` (5 opções); `Participante` popula `F_TPO` (3 opções); `Ouvinte` esvazia `F_TPO` e dispensa obrigatoriedade de `F_TPO` e `f_titulo`.
  - `F_TPO` (`muda_titulo_evento`): altera dinamicamente `#lblIdTitt` (`Conferencista` → `"Título da conferência..."`).

## Fase 4/5 — Matriz de valores e preenchimento (leitura de volta) — PASSOU
- **Testado:** `F_FORMA=Convidado`, `F_TPO=Conferencista`, `f_nme_evento="[ZZ-TESTE-ANTIGRAVITY] Evento Teste"`, `f_ano="2024"`, `f_classif=Nacional`, `F_COD_PROD="A31"`, `f_cidade="São Luís"`, `f_pais="ARG"`, `f_homepage`, `f_titulo="Palestra Teste"`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `f_titulo_en="Test Lecture"`.
- **Reabertura pós-save:** 100% dos campos persistiram com fidelidade absoluta.

## Fase 6 — Obrigatórios (Validada ao vivo)
- Padrão (`Convidado`/`Participante`): `Forma de participação`, `Tipo da apresentação/participação`, `Natureza`, `Nome do evento`, `Ano`, `Título da apresentação`.
- `Ouvinte`: `Natureza`, `Nome do evento`, `Ano`.

## Fase 7 — Salvamento de teste e Exclusão — PASSOU
- Salvo com sucesso (`Sucesso / A operação foi realizada com sucesso! !`), listado na posição 1 (38 itens), reaberto e **excluído** imediatamente sem diálogo `confirm()` nativo, restaurando os 37 itens originais.

---

## 2. Organização de Eventos (`prc_tec_demais_lista?f_cod_tipo=2G` → `PRC_TEC_ORG`) — PASSOU

- **Estado inicial preservado:** `6` itens originais do titular mantidos intactos.
- **Hidden inputs (`7` campos em `GN_TEC`):** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l` (em `PKG_EVENTO.FORM` de Participação são apenas 3: `f_ctr`, `f_cod`, `f_seq`).
- **F4/F5 + F7:**
  - Preenchido: `F_COD_PROD[2]` (`Congresso`, `value=""`), `F_SUB_PROD = "26"` (`Organização`), `f_titulo = "[ZZ-TESTE-ANTIGRAVITY] Org Evento"`, `f_ano = "2024"`, `f_duracao = "3"`, autor `SANTOS, A. A. B.`.
  - Salvo (`1 · [ZZ-TESTE-ANTIGRAVITY] Org Evento · Congresso · 2024`), reaberto com **100% de persistência** e **excluído imediatamente** sem `confirm()` nem `.caixaMsg`, restaurando os **`6` itens originais**.
