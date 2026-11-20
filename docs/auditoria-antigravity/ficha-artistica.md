# Ficha de validação — Produção Artística/Cultural (`artes_cenicas`, `musica`, `artes_visuais`, `outra_producao_artistica`)

- **Data:** 2026-11-20 · **URL no Lattes:** `pkg_arte_nova.form?F_TIPO=<AC|MU|AV|OU>` (`PKG_ARTE_NOVA.FORM`)
- **Como abre:** `pkg_arte_nova.lista?f_cod_tipo=<AC|MU|AV|OU>` (auto-abre com 0 itens)

## Fase 4/5 & Fase 7 — Artes Cênicas (`F_TIPO=AC`) — PASSOU
- **Descoberta condicional ao vivo (F7):** quando `f_inedito` (`Ineditismo da obra`) está marcado e `f_dta_ini` preenchida, **`f_local_estreia` torna-se obrigatório** (`"Informe o local de estréia"`).
- **Testado:** 22 campos (`F_COD_PROD="3A8"` Teatral, `f_pais="ARG"`, `F_IDIOMA="EN"`, `f_meio="I"`, `f_tpo_evento="Festival"`, `f_tpo_ativ="Diretor"`, `f_inedito=true`, `f_dta_ini="15/05/2024"`, `f_local_estreia="Teatro Arthur Azevedo"`, `f_duracao="90"`, `f_inst`, `f_local`, `f_cidade`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `f_titulo_en`, `f_ref_en`, e `Autores` `SANTOS, A. A. B.`).
- **Reabertura pós-save + Exclusão:** 100% dos 22 campos persistiram com fidelidade; **Excluir** imediato (sem `confirm()` nativo) retornando `pkg_arte_nova.lista?f_cod_tipo=AC` a `0` itens.
