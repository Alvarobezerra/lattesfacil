# Ficha de validação — Livros e Capítulos (`livro_capitulo`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `PKG_LVR_CAP.FORM_LVR` · `PKG_LVR_CAP.FORM_CAP`
- **Como abre:** `pkg_lvr_cap.lista` → `Incluir novo item` → wizard `winLivrosCaps` (2 passos com `prc_valida_issn`)
- **Abas (10):** `D.O.I`, `Dados gerais`, `Detalhamento`, `Autores`, `Palavras-chave`, `Áreas`, `Setores`, `Outras informações`, `Traduções`, `Visibilidade`
- **Listas (4):** `tabelaAutor` (max 60), `tabelapalavra` (max 50), `tabelaarea` (max 86), `tabelasetor` (CNAE)

## Fase 1 & Fase 2 — Captura e Diff
- **Divergências encontradas em `itens/especificacao/livro_capitulo.json`:**
  - `f_titulo` (Livro): spec = `255` vs ao vivo = **`400`**.
  - `f_ref_en` (Livro e Capítulo): spec = `3900` vs ao vivo = **`3800`**.
  - `F_COD_PROD` (Livro): spec não marcava obrigatório, mas ao vivo exige escolha (`Livro publicado` / `Organização de obra publicada`).
  - Lupa `dominio()` de `f_sub_prod` em Livro: `1#Coletânea`, `2#Texto integral`, `3#Verbete`, `4#Outro`.

## Fase 4/5 — Matriz de valores e preenchimento (leitura de volta) — PASSOU
1. **Livro (`PKG_LVR_CAP.FORM_LVR`):** `F_COD_PROD=Livro publicado`, `f_sub_prod="Coletânea"`, `f_pais="ARG"`, `F_IDIOMA="EN"`, `f_meio="D"`, `f_isbn="9780306406157"`, `f_edicao="1"`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `Autores` (`SANTOS, A. A. B.`), `f_titulo_en`, `f_ref_en`. Reabertura pós-save **100% idêntica**.
2. **Capítulo (`PKG_LVR_CAP.FORM_CAP`):** `f_titulo_cap`, `f_titulo`, `f_organizadores`, `f_pag_ini="10"`, `f_pag_fim="25"`, `f_edicao="1"`, `f_isbn="9780306406157"`, `f_pais="ARG"`, `F_IDIOMA="EN"`, `f_meio="D"`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `Autores` (`SANTOS, A. A. B.`), `f_titulo_cap_en`, `f_ref_en`. Reabertura pós-save **100% idêntica**.

## Fase 6 — Obrigatórios (Validada ao vivo)
- **Livro:** `Tipo` (`F_COD_PROD`), `Título do livro`, `Ano`, `ISBN` (válido), `Edição`, titular em `Autores`.
- **Capítulo:** `Título do capítulo`, `Ano`, `Título` (do livro), `ISBN` (válido), `Edição`, `Página inicial`, titular em `Autores`.

## Fase 7 — Salvamento de teste e Exclusão — PASSOU
- Ambos os registros `[ZZ-TESTE-ANTIGRAVITY]` salvos, listados, reabertos e **excluídos** imediatamente (sem `confirm()` nativo, toast `Sucesso / A operação foi realizada com sucesso! !`), retornando `pkg_lvr_cap.lista` a `0` registros.
