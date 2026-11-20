# Auditoria Independente (Ao Vivo): Capítulo de Livro e Texto em Jornal/Revista

**Data:** 2026-11-20  
**Capturas:** [capitulo_livro.json](capturas/capitulo_livro.json) · [texto_jornal_revista.json](capturas/texto_jornal_revista.json)

---

## 1. Capítulo de Livro Publicado (`PKG_LVR_CAP.FORM_CAP`)
- **Wizard de abertura:** mesmo modal `winLivrosCaps` de Livro (exige ISBN válido + Ano + Autor/Editor).
- **Diferenças sutis vs Livro (`FORM_LVR`):**
  - `F_COD_PROD` é `<input type="hidden">` (sem radio de Tipo).
  - `f_titulo_cap` (Título do capítulo) e `f_titulo` (Título do livro) têm `maxlength=255` (em Livro, `f_titulo` é `400`).
  - Tradução usa `f_titulo_cap_en` (`maxlength=400`), e não `f_titulo_en`.
  - Inclui `f_organizadores` (`maxlength=255`), `f_pag_ini` (`maxlength=15`) e `f_pag_fim` (`maxlength=15`).
  - `f_cidade_ed` mantém limite curto de **30 caracteres**.
- **Obrigatórios ao salvar (`check()`):** `Título do capítulo`, `Ano`, `Título` (do livro), `ISBN` (válido), `Edição`, `Página inicial` e o próprio usuário na lista de autores.

## 2. Texto em Jornal ou Revista (`PKG_TEXTO.FORM`)
- **Abertura direta:** sem modal prévio de DOI/ISBN.
- **Natureza (`F_COD_PROD`):** `Jornal de notícias` / `Revista (Magazine)` — alternar não altera o DOM.
- **Campos específicos:** `f_titulo_periodico` (livre, max 255 — não usa lupa!), `f_issn` (max 10), `f_data` (`hasDatepicker`, max 10), `f_volume` (max 10), `f_pag_ini` / `f_pag_fim` (max 15) e `f_local` (**max 30**).
- **Obrigatórios ao salvar (`check()`):** `Natureza`, `Título`, `Ano`, `Título do jornal/revista em que o texto foi publicado` e o próprio usuário na lista de autores.
