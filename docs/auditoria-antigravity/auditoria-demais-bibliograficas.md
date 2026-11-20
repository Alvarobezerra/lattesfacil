# Auditoria Independente (Ao Vivo): Demais Produções Bibliográficas (1A, 1C, 1Z)

**Data:** 2026-11-20  
**Capturas:** [traducao.json](capturas/traducao.json) · [prefacio_posfacio.json](capturas/prefacio_posfacio.json) · [outra_producao_bibliografica.json](capturas/outra_producao_bibliografica.json)

---

## Resumo Consolidado
1. **Tradução (`prc_bib_traducao`):**
   - `F_COD_PROD`: `Artigo`, `Livro`, `Outra` (obrigatório).
   - Inclui `F_IDIOMA_OBRA` (153 opções: vazia + 152 idiomas), `f_autor_trad` (max 60), `f_tit_obra` (max 255). **Não** possui `F_STA_DIVULGACAO_CIENTIFICA`.
   - Obrigatórios: `Natureza`, `Título`, `Ano`, autor titular.
2. **Prefácio, posfácio (`prc_bib_prefacio`):**
   - `F_COD_PROD` (`Tipo`: `Prefácio`, `Posfácio`, `Apresentação`, `Introdução` — **obrigatório**) + `f_sub_tipo` (`Natureza`: `"31 "`=`Livro`, `"32 "`=`Revistas ou periódicos`, `"33 "`=`Outra` — **opcional**, atenção ao espaço à direita no `value`!).
   - **Não** possui `F_STA_DIVULGACAO_CIENTIFICA`.
3. **Outra produção bibliográfica (`prc_bib_outraprod`):**
   - `f_natureza` é texto livre obrigatório (`maxlength=100`); `F_COD_PROD` é `hidden`.
   - **Possui** `F_STA_DIVULGACAO_CIENTIFICA`.
   - Obrigatórios: `Natureza`, `Título`, `Ano`, autor titular.
