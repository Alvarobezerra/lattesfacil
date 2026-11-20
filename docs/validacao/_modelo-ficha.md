# Ficha de validação — <Item> / <Variante>

- **Data:** ____ · **Versão do app:** ____ · **Formulário aberto por:** ____
- **Como abre:** ____ · **Abas:** ____ · **Listas:** ____

## Fase 1 — Captura
- [ ] Campos, tipos, `maxlength`, desabilitado/somente leitura, obrigatórios
- [ ] Opções completas (valor e texto) de seleções, radios e marcações
- [ ] Abas e listas (colunas, popup de inclusão, lupa, "Listar todos")
- [ ] Estados: cada gatilho × cada valor (tabela abaixo)
- [ ] Máscaras e regras de formato
- Arquivo: `docs/campos-lattes/ref/<item>/<variante>.json`

| Gatilho | Valor | Aparece | Some | Opções que mudam | Obrigatório novo |
| --- | --- | --- | --- | --- | --- |

## Fase 2 — Diff spec × captura
| Categoria | Qtde | Resolução |
| --- | --- | --- |
| ausente_no_spec | | |
| sobrando_no_spec | | |
| tipo_diferente | | |
| maxlength_diferente | | |
| opcoes_diferentes | | |
| rotulo_diferente | | |
| obrigatorio_diferente | | |
| condicional_ausente | | |
| lista_ausente / colunas_diferentes | | |
- **Exceções justificadas:** ____

## Fase 3 — Paridade de tela (por estado)
| Estado | Rótulos | Controles | Opções | Limites/máscaras | Condicionais | Captura de tela |
| --- | --- | --- | --- | --- | --- | --- |

## Fase 4/5 — Matriz de valores e preenchimento (leitura de volta)
| Campo | Caso | Enviado | Lido de volta | Esperado | Resultado |
| --- | --- | --- | --- | --- | --- |
- Resultado ∈ OK · cortado (esperado) · divergente · não preenchido · aviso do Lattes · exige ação manual

## Fase 6 — Obrigatórios
- Lattes: ____ · App: ____ · Iguais? ☐

## Fase 7 — Salvamento de teste (só com autorização)
- Autorizado por: ____ · Resultado: ____ · Item de teste excluído: ☐

## Fechamento
- Pendências: ____
- Testes de regressão adicionados: ☐ · Servidor reiniciado: ☐ · Extensão reconstruída: ☐
- Status: ☐ Pronto ☐ Pronto com exceções ☐ Em andamento
