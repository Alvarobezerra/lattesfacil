# Contravalidação F4/F5 + F7: Apresentação e Anais

**Data:** 2026-11-20  
**Escopo:** Execução independente no Lattes ao vivo (matriz não-padrão + leitura de volta + salvamento de teste `[ZZ-TESTE-ANTIGRAVITY]` + reabertura + exclusão limpa).

---

## 1. Apresentação de Trabalho e Palestra (`prc_tec_apres`) — PASSOU
- **Matriz F4/F5 testada:** `Comunicação`, `f_pais=ARG`, `F_IDIOMA=EN`, `f_meio=D`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `F_RELEV=não`, `f_titulo` com `;`, `"Aspas"` e acentos, `f_titulo_en`, `f_ref_en`, e titular em `Autores` (`SANTOS, A. A. B.`).
- **Normalização observada no servidor:** aspas duplas `"Aspas"` em `f_titulo` foram convertidas automaticamente pelo Lattes para aspas simples `'Aspas'` ao salvar.
- **Reabertura (F5 pós-save):** 100% dos 16 campos + `Autores` persistiram exatamente como enviados (considerando a normalização de aspas).
- **Exclusão (F7):** clicar em **Excluir** em `prc_tec_demais_lista?f_cod_tipo=2J` removeu imediatamente sem diálogo `confirm()`, exibindo `Sucesso / A operação foi realizada com sucesso! !` e restaurando os 9 itens originais.

## 2. Trabalhos Publicados em Anais de Eventos (`pkg_trabalho.form`) — PASSOU
- **Matriz F4/F5 testada:** `Resumo`, `f_pais=ARG`, `F_IDIOMA=EN`, `f_meio=D`, `F_STA_DIVULGACAO_CIENTIFICA=sim`, `f_tipo_evento=Nacional`, `f_isbn=9780306406157`, `f_titulo` com `"Aspas"`, `f_titulo_en`, `f_ref_en`, e titular em `Autores`.
- **Normalização observada no servidor:** mesma conversão automática de `"Aspas"` para `'Aspas'` em `f_titulo`.
- **Reabertura (F5 pós-save):** 100% dos campos e `Autores` persistiram identicamente.
- **Exclusão (F7):** clicar em **Excluir** removeu imediatamente sem diálogo `confirm()`, exibindo `Sucesso / A operação foi realizada com sucesso! !` e restaurando os 17 itens originais.
