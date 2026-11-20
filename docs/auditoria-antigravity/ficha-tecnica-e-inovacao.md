# Ficha de validação — Produção Técnica (`trabalho_tecnico` e `processo_tecnica`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `pkg_relatorio.form` · `pkg_processo.form`
- **Como abre:** auto-abrem com 0 itens

## 1. Trabalhos Técnicos (`pkg_relatorio.form`) — PASSOU
- **F4/F5 + F7:** 18 campos (`F_COD_PROD=Relatório técnico`, `f_pais="ARG"`, `F_IDIOMA="EN"`, `f_meio="D"`, `f_duracao="6"`, `f_paginas="25"`, `f_disp="Irrestrita"`, `f_titulo_en`, `f_ref_en`) + `Autores` (`SANTOS, A. A. B.`) salvos, reabertos com 100% de fidelidade e **excluídos** imediatamente (sem `confirm()` nativo), voltando a `0` itens.

## 2. Processos ou Técnicas (`pkg_processo.form` com `f_sta_inovacao = Sim`) — PASSOU
- **Condicional testado ao vivo:** marcar `f_sta_inovacao = Sim` tornou `[name="f_txt_potencial"]` visível (`"Potencial de inovacao testado ao vivo"`).
- **F4/F5 + F7:** todos os campos + `f_sta_inovacao = Sim` + `f_txt_potencial` + `Autores` (`SANTOS, A. A. B.`) salvos, reabertos com **100% de fidelidade** (inclusive `f_sta_inovacao = Sim` e `f_txt_potencial` visível com o texto exato), e **excluídos** imediatamente (sem `confirm()` nativo), voltando a `0` itens.

---

## 3. Artigos Aceitos para Publicação (`pkg_artigo_pr.lista` → `PKG_ARTIGO_PR.form`) — PASSOU
- **21 hidden inputs em `GN_ARTIGO`:** `F_COD_PROD`, `f_titulo_periodico_h`, `f_titulo_h`, `f_ano_h`, `f_cod_doi_h`, `f_issn_h`, `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_autores_l2`, `f_autores_l3`, `f_autores_l4`, `f_plv_l`, `f_setor_l`, `f_area_l`, `f_seq_per`, `f_cod_doi`, `start`, `finish`, `status`.
- **Regra exclusiva de ano descoberta no F7:** `"Ano previsto para publicação não pode ser menor que o ano atual."` (`f_ano >= 2026`).
- **F4/F5 + F7:** Selecionado periódico `REVISTA DE SAUDE PUBLICA` via lupa `periodico()` (`f_issn="0034-8910"`, `f_jcr="2,4000"`), `f_titulo="[ZZ-TESTE-ANTIGRAVITY] Artigo Aceito"`, `f_ano="2026"`, `F_IDIOMA="PT"`, autor `SANTOS, A. A. B.` → salvo, reaberto com 100% de fidelidade e excluído imediatamente sem `confirm()` (`0` itens restantes).

## 4. Prefácio, Posfácio (`prc_bib_demais_lista?f_cod_tipo=1C` → `PRC_BIB_PREFACIO`) — PASSOU
- **7 hidden inputs em `GN_BIB`:** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`.
- **F4/F5 + F7:** Rádio `F_COD_PROD[0]` (`Prefácio`, `value=""` no DOM), `f_sub_tipo="31 "` (`Livro`, com espaço à direita), `f_titulo="[ZZ-TESTE-ANTIGRAVITY] Prefacio"`, `f_ano="2024"`, `f_autor_trad="Autor"`, `f_tit_obra="Obra"`, autor `SANTOS, A. A. B.` → salvo, reaberto com 100% de fidelidade e excluído imediatamente sem `confirm()` (`0` itens restantes).

## 5. Curso de Curta Duração Ministrado (`prc_tec_demais_lista?f_cod_tipo=2B` → `PRC_TEC_CURSO`) — PASSOU
- **7 hidden inputs em `GN_TEC`:** `f_ctr`, `f_cod`, `f_seq`, `f_autores_l`, `f_plv_l`, `f_setor_l`, `f_area_l`.
- **F4/F5 + F7:** Rádio `F_COD_PROD[0]` (`Extensão`, `value=""` no DOM), `f_titulo="[ZZ-TESTE-ANTIGRAVITY] Curso"`, `f_ano="2024"`, `f_participacao="Docente"`, `f_duracao="8"`, `f_unidade="horas"`, autor `SANTOS, A. A. B.` → salvo, reaberto com 100% de fidelidade e excluído imediatamente sem `confirm()` (`0` itens restantes).
