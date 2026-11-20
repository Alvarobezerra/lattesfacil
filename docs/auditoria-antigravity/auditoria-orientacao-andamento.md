# Auditoria Independente (Ao Vivo): Orientações e Supervisões em Andamento (`orientacao_andamento`)

**Data:** 2026-11-20  
**Captura ao vivo:** [capturas/orientacao_andamento.json](capturas/orientacao_andamento.json)  
**URL no Lattes:** `pkg_orient.form?f_tipo=A` (`PKG_ORIENT` / `PKG_ORIENT.FORM`)  
**Evidência visual:** `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/final_step_205.png`

---

## Diferenças Críticas vs `orientacao_concluida` e `static/index.html`
1. **Natureza (`F_COD_PROD`) tem apenas 6 opções em andamento:**
   - **NÃO existe** `"Trabalho de conclusão de curso de graduação"` em `pkg_orient.form?f_tipo=A`!
   - No `static/index.html`, `#natureza` permite escolher TCC mesmo quando `situacao_orientacao === "Em andamento"`, o que falha no Lattes.
2. **Rótulo de `f_ano`:** muda para `"Ano de início da orientação"` (em vez de `"Ano de término da orientação"`).
3. **Sem `capesdados()`:** o ícone de busca CAPES junto a `f_nme_orient` não aparece em andamento.
4. Demais campos, `maxlength`, lupas (`dominio()`, `sele_inst()`, `curso()`, `agencia()`) e listas (`tabelapalavra`, `tabelaarea`, `tabelasetor`) seguem a mesma estrutura de `orientacao_concluida`.

## Regra de Salvamento em Branco (`pre_check()`, validada ao vivo)
Ao clicar em **Salvar** com os campos vazios, o modal `.caixaMsg` exibe:
```
Campo Natureza obrigatório não informado.
Campo Título da produção obrigatório não informado.
Campo Ano obrigatório não informado.
Campo Nome do orientando obrigatório não informado.
Campo Instituição obrigatório não informado.
Campo Curso obrigatório não informado.
```
> **Nota:** Diferentemente de `Iniciação Científica` concluída (onde `Curso` não bloqueou o salvamento), em andamento `Campo Curso obrigatório não informado.` aparece na validação inicial.
