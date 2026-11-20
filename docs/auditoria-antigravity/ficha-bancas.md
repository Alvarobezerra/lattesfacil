# Ficha de validação — Bancas (`banca` e `banca_comissao_julgadora`)

- **Data:** 2026-11-20 · **URLs no Lattes:** `PKG_BANCA_TRAB.form` · `PKG_BANCA_JULG.form`
- **Como abre:** `pkg_banca_trab.lista` / `pkg_banca_julg.lista` (auto-abre com 0 itens)
- **Abas (9):** `Dados gerais`, `Detalhamento`, `Participantes`, `Palavras-chave`, `Áreas`, `Setores`, `Outras informações`, `Traduções`, `Visibilidade`
- **Listas (4):** `tabelaAutor` (`Participantes`, max 60), `tabelapalavra` (max 50), `tabelaarea` (max 86), `tabelasetor` (CNAE)

## Fase 1 & Fase 2 — Captura e Diff (`capturas/banca_*.json` × `itens/especificacao/`)
- [x] Paridade de campos e `maxlength` = **0 divergências**
- **Atenção:** em `PKG_BANCA_TRAB`, `f_sub_prod` ("Tipo (apenas para mestrado)") usa valores com espaço à direita (`"34 "` Acadêmico, `"35 "` Profissional). Em `PKG_BANCA_JULG`, `f_inst` tem typo `disable="true"` no HTML do Lattes.

## Fase 4/5 — Matriz de valores e preenchimento (leitura de volta) — PASSOU
1. **Bancas de trabalhos de conclusão (`PKG_BANCA_TRAB`):**
   - Testado `F_COD_PROD=Mestrado`, `f_sub_prod="34 "`, `f_pais=ARG`, `F_IDIOMA=EN`, `f_inst` via `sele_inst()`, `f_curso` via `curso()` (`"ARTES CÊNICAS(20001010045P0)"`), `Participantes` (`SANTOS, A. A. B.`), `f_titulo_en`, `f_ref_en`.
   - **Normalização observada ao reabrir pós-save:** `f_curso` remove o código CAPES (`"ARTES CÊNICAS"`), igual ao comportamento de `pkg_orient`.
   - *Nota técnica:* `pkg_banca_trab.lista` serve HTML malformado quando tem itens (requer atenção se o robô precisar clicar na lista).
2. **Bancas de comissões julgadoras (`PKG_BANCA_JULG`):**
   - Testado `F_COD_PROD=Concurso público`, `f_pais=ARG`, `F_IDIOMA=EN`, `f_inst` via `sele_inst()`, `Participantes` (`SANTOS, A. A. B.`), `f_titulo_en`, `f_ref_en`.
   - **Reabertura pós-save:** 100% dos campos persistiram com fidelidade absoluta.

## Fase 6 — Obrigatórios (Validada ao vivo)
- `PKG_BANCA_TRAB`: `Natureza`, `Título`, `Ano`, `Nome do candidato`, titular em `Participantes/autores`.
- `PKG_BANCA_JULG`: `Natureza`, `Título`, `Ano`, titular em `Participantes/autores`.

## Fase 7 — Salvamento de teste e Exclusão — PASSOU
- Ambos os registros `[ZZ-TESTE-ANTIGRAVITY]` foram salvos, listados, reabertos para conferência e **excluídos** imediatamente (sem `confirm()` nativo, toast `Sucesso / A operação foi realizada com sucesso! !`), retornando ambas as listas a `0` registros.
