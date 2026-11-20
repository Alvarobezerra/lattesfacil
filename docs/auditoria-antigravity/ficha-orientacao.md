# Ficha de validação — Orientações (`orientacao_concluida` e `orientacao_andamento`)

- **Data:** 2026-11-20 · **Formulário aberto por:** `pkg_orient.lista?f_tipo=C` / `f_tipo=A` (auto-abre quando 0 itens)
- **URLs no Lattes:** `pkg_orient.form?f_tipo=C` (Concluída) · `pkg_orient.form?f_tipo=A` (Em andamento)
- **Abas (9):** `Dados Gerais`, `Detalhamento`, `Bolsa`, `Palavras-chave`, `Áreas`, `Setores`, `Outras informações`, `Traduções`, `Visibilidade`
- **Listas (3):** `tabelapalavra` (max 50), `tabelaarea` (max 86), `tabelasetor` (CNAE, `Listar todos`)

## Fase 1 — Captura (Concluída ao vivo)
- [x] Campos, tipos, `maxlength`, desabilitado/somente leitura, obrigatórios
- [x] Opções completas (valor e texto) de seleções, radios e marcações
- [x] Abas e listas (colunas, popup, lupas `dominio()`, `sele_inst()`, `curso()`, `agencia()`, `capesdados()`)
- [x] Estados: `F_COD_PROD` (`testa_nivel`), `f_tpo_orient` (`test_ori`), `F_BOLSA` (`agnull`)
- Arquivos: [capturas/orientacao_concluida.json](capturas/orientacao_concluida.json) · [capturas/orientacao_andamento.json](capturas/orientacao_andamento.json)

| Gatilho | Valor | Aparece / Muda | Some / Bloqueia | Obrigatório novo |
| --- | --- | --- | --- | --- |
| `f_tipo` (situação) | `A` (Em andamento) | Rótulo `f_ano` = `Ano de início da orientação`; 6 opções em `F_COD_PROD` | Remove `Trabalho de conclusão de curso de graduação` e `capesdados()` | `Curso` exigido no `pre_check()` |
| `f_tipo` (situação) | `C` (Concluída) | Rótulo `f_ano` = `Ano de término da orientação`; 7 opções em `F_COD_PROD`; `capesdados()` ativo | — | `Iniciação Científica` salva sem `Curso` |
| `F_COD_PROD` | `Supervisão de pós-doutorado` | — | `f_tpo_orient` bloqueia marcação (`test_ori()`) | — |
| `F_COD_PROD` | `Dissertação de mestrado` / `Outra natureza` | — | — | `f_dsc_outra` (`dominio()`) aplicável |

## Fase 2 — Diff spec × captura (Ganhos sobre o método padrão)
| Categoria | Qtde | Resolução Planejada |
| --- | --- | --- |
| `opcoes_diferentes` (`f_pais`, `F_IDIOMA`) | 2 | Specs têm `80` opções; Lattes real tem `244` países e `152` idiomas |
| `opcoes_diferentes` (`F_COD_PROD` em andamento) | 1 | Spec tem `7` opções (inclui TCC); Lattes em andamento tem apenas `6` (sem TCC) |
| `obrigatorio_diferente` (`F_COD_PROD`) | 1 | Spec marca `False`; Lattes exige `Natureza` nas duas variantes |
| `obrigatorio_diferente` (`f_tpo_orient`) | 1 | Spec marca `True` global; Lattes restringe a Mestrado/Doutorado (e bloqueia em Pós-doc) |
| `obrigatorio_diferente` (`f_curso` em concluída) | 1 | Spec marca `True` global; Lattes salvou `Iniciação Científica` sem `Curso` |
| `legado_nao_migrado` | 1 | `static/index.html` ainda usa formulário legado (`data-tipos="orientacao"`) |

## Fase 3 — Paridade de tela (Pendente)
- Aguardando migração de `orientacao` do formulário legado para o motor de specs (`static/app.js`) antes da implantação.

## Fase 4/5 — Matriz de valores e preenchimento (leitura de volta)
- **Concluída (`pkg_orient.form?f_tipo=C` — PASSOU):**
  - `Supervisão de pós-doutorado`: confirmado que `f_tpo_orient` não fica `disabled` no HTML, mas `test_ori()` bloqueia a marcação ao clicar (`checked=false`).
  - `Orientação de outra natureza`: lupa `dominio()` em `f_dsc_outra` possui **1 opção exata**: `{"text": "Outro Tipo", "value": "Outro Tipo"}`.
- **Em andamento (`pkg_orient.form?f_tipo=A` — PASSOU):**
  - Testadas as 4 lupas ao vivo: `dominio()` (`Acadêmico`/`Profissional`), `sele_inst()` (`Universidade Federal do Maranhão `), `curso()` (45 opções de Mestrado com código CAPES `Nome(código)`), `agencia()` (`CAPES`).
  - Todos os campos (`F_COD_PROD=Dissertação de mestrado`, `f_tpo_orient=Orientador principal`, `f_pais=ARG`, `F_IDIOMA=EN`, `F_BOLSA=sim`, `f_titulo_en`, `f_ref_en`) lidos de volta 100% iguais antes e depois de salvar.
  - **Normalização observada ao reabrir registro salvo:** `f_curso` remove o código CAPES entre parênteses (`"Ciência dos Materias(20001010031P0)"` → `"Ciência dos Materias"`); `f_inst` preserva espaço à direita (`"Universidade Federal do Maranhão "`).

## Fase 6 — Obrigatórios (Validada ao vivo)
- **Concluída (`pre_check()`):** `Natureza`, `Título do trabalho orientado`, `Ano de término da orientação`, `Nome do orientando`, `Instituição`.
- **Em andamento (`pre_check()`):** `Natureza`, `Título da produção`, `Ano`, `Nome do orientando`, `Instituição`, **`Curso`**.

## Fase 7 — Salvamento de teste (Validado nas 2 variantes)
- **Concluída (`Iniciação Científica`):** Salvo via lupa `sele_inst()`, conferido na lista `pkg_orient.lista?f_tipo=C`, e **excluído** (`confirm("Deseja excluir o item selecionado?")`), retornando a 0 registros.
- **Em andamento (`Dissertação de mestrado` c/ bolsa):** Salvo com as 4 lupas, conferido na lista `pkg_orient.lista?f_tipo=A`, reaberto para F5 pós-save, e **excluído** (`Sucesso / A operação foi realizada com sucesso! !`), retornando a 0 registros.
