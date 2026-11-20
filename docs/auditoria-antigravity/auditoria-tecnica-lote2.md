# Auditoria Independente (Ao Vivo): Produção Técnica — Lote 2

**Data:** 2026-11-20  
**Capturas:** [produtos.json](capturas/produtos.json) · [processos_tecnicas.json](capturas/processos_tecnicas.json) · [trabalhos_tecnicos.json](capturas/trabalhos_tecnicos.json)

---

## Destaques
1. **Produtos (`PKG_PRODUTO.FORM`):**
   - Exige **Tipo** (`F_COD_PROD`: `Piloto`, `Projeto`, `Protótipo`, `Outro`) **e Natureza** (`F_SUB_PROD`: `12..16`).
   - `f_sta_inovacao` (default `Não`): quando `Sim`, insere/exibe dinamicamente `f_txt_potencial` (`"Qual o potencial de inovação?"`).
2. **Processos ou técnicas (`PKG_PROCESSO.FORM`):**
   - `F_COD_PROD`: `Analítica`, `Instrumental`, `Pedagógica`, `Processual`, `Terapêutica`, `Outra` (obrigatório).
   - `f_sta_inovacao` (default `Não`): quando `Sim`, exibe e torna **obrigatório** `f_txt_potencial` (max 400).
3. **Trabalhos técnicos (`PKG_RELATORIO.FORM`):**
   - `F_COD_PROD`: `Parecer`, `Elaboração de projeto`, `Relatório técnico`, `Serviços na área da saúde`, `Extensão tecnológica`, `Outra` (obrigatório).
   - Não possui `f_sta_inovacao`; inclui `f_duracao` (max 5) e `f_paginas` (max 5).
