# Auditoria Independente (Ao Vivo): Produção Técnica — Lote 1

**Data:** 2026-11-20  
**Capturas:** [assessoria_consultoria.json](capturas/assessoria_consultoria.json) · [extensao_tecnologica.json](capturas/extensao_tecnologica.json) · [software_sem_registro.json](capturas/software_sem_registro.json)

---

## Destaques
1. **Assessoria e consultoria (`PKG_ASSESSORIA_CONSULTORIA.FORM`)** & **Extensão tecnológica (`PKG_EXTENSAO_TECNOLOGICA.FORM`)**:
   - Compartilham exatamente o mesmo layout (`GN_RELATORIO`) e os mesmos campos/limites (`f_finalidade` 255, `f_duracao` 5, `f_paginas` 5, `f_disp` `""`/`Restrita`/`Irrestrita`, `f_cidade` 255, `f_inst` 255).
   - Única diferença estrutural: `Assessoria e consultoria` tem `F_COD_PROD` (`Assessoria` / `Consultoria`, obrigatório), enquanto `Extensão tecnológica` tem `F_COD_PROD` como `hidden`.
2. **Programa de computador sem registro (`PKG_PATENTE_REGISTRO.FORM`):**
   - **Regra condicional confirmada:** `f_sta_inovacao = Sim` mantém visível e obrigatório `<tr id="potencial">` (`f_txt_potencial`, `"Qual o potencial de inovação?"`, max 400); `Não` oculta a linha e remove a obrigatoriedade.
   - **Obrigatórios ao salvar:** `Título`, `Instituição(ções) financiadora(s)` (max 380), `Finalidade` (max 255), `Linguagens` (`f_plataforma`, max 255), `Ano de Desenvolvimento`, e `"O seu nome deverá ser incluído na lista de inventores."` (`f_natureza` **não** é obrigatório).
   - Possui **7 listas/grids** (incluindo `tabelaprograma`, `tabelatitularPessoa` e `titularInstHolder`).
