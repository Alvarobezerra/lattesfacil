# Auditoria Independente (Ao Vivo): Artigos Aceitos e Partitura Musical

**Data:** 2026-11-20  
**Capturas:** [artigo_aceito.json](capturas/artigo_aceito.json) · [partitura_musical.json](capturas/partitura_musical.json)

---

## 1. Artigos Aceitos para Publicação (`PKG_ARTIGO_PR.form`)
- **Abertura:** Sem modal prévio de DOI (diferente de `artigo` publicado); o campo `f_cod_doi` aparece inline na aba `D.O.I`.
- **Campos bloqueados (`disabled=true`):** tanto `f_titulo_periodico` (max 255) quanto `f_issn` (max 10) são preenchidos apenas pela lupa `periodico()` ou via DOI.
- **Campos ausentes (vs artigo publicado):** não tem `f_pais`, `f_meio`, `f_volume`, `f_serie`, `f_pag_ini`, `f_pag_fim`, `f_jcr`.
- **Obrigatórios ao salvar (`pre_check()`):** `Título`, `Ano previsto para publicação`, `Título do periódico/revista em que o artigo será publicado`, **ISSN válido** e o próprio usuário na lista de autores.

## 2. Partitura Musical (`PRC_BIB_PARTITURA`)
- **Abertura:** Direta (abre o formulário automaticamente quando há 0 itens).
- **Natureza (`F_COD_PROD`):** `Canto`, `Coral`, `Orquestral`, `Outra` — alternar não altera o DOM.
- **Detalhamento:** `f_formacao` (max 255), `f_editora` (max 100), `f_cidade` (max 30), `f_paginas` (max 5), `f_issn` ("Número do catálogo", max 10).
- **Obrigatórios ao salvar (`check()`):** `Natureza`, `Título`, `Ano` e o próprio usuário na lista de autores.
