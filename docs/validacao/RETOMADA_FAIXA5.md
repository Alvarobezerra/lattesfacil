# Retomada da faixa 5 (produção técnica e registros) — passo a passo para uma conversa nova

Estado em 21/11/2026: capturas e paridade (0 pendentes) feitas para os 13 itens; matriz de valores em andamento na aba do Lattes (ver abaixo); salvamentos de teste ainda NÃO feitos.
Bancas (2) e patente já estão fechadas. Regras: zero pendência, só salvar itens `ZZ-TESTE-LATTESFACIL`, registrar cada salvamento em `docs/validacao/LOG_OPERACOES_NOITE.md`, reiniciar `server.py` e recarregar a extensão ao fim.

## 1. Matriz de valores (fases 4–5) — itens: software_registro, software_sem_registro, produto, processo_tecnica, trabalho_tecnico, relatorio_tecnico, extensao_tecnologica, material_didatico, desenho_industrial, marca_registrada, topografia_circuito, cultivar_protegida, cultivar_registrada
- Resultado parcial (todos OK, 0 falhas): software_registro 133/133, software_sem_registro 124/124, produto 218/218, processo_tecnica 215/215, trabalho_tecnico 217/217, relatorio_tecnico 213/213.
- Faltam rodar: extensao_tecnologica, material_didatico, desenho_industrial, marca_registrada, topografia_circuito, cultivar_protegida, cultivar_registrada (a rodada em curso na aba do Lattes pode já ter terminado: ler `window.top.__cicloM` na aba do currículo).
- Para rodar só os que faltam: `python ferramentas/gerar_ciclo_matriz.py <itens>` e carregar na aba do currículo (nesta ordem, por `<script src=http://127.0.0.1:8798/...>`): `auditoria_lattes.js`, `autofill_core.js`, `executor_preenchimento.js`, `saida/ciclo_matriz.js`. O receptor é `python ferramentas/receptor_captura.py` (porta 8798). Resultado em `window.top.__cicloM.resultados`; relatórios em `docs/campos-lattes/ref/<item>_f5/`.
- Se a aba travar com alerta nativo: o usuário clica OK.

## 2. Salvamentos de teste (fase 7)
- `python ferramentas/gerar_payload_generico.py <item>` (valores automáticos; ajustar `VALORES` no arquivo se o Lattes recusar) e `python ferramentas/gerar_ciclo_salvar.py <itens>`; carregar `saida/ciclo_salvar.js` na aba (mesmos scripts antes); resultado em `window.top.__cicloS` (resposta do Lattes + linha na lista).
- Esperado: "Operação realizada com sucesso" e o título `ZZ-TESTE-LATTESFACIL ...` na lista de cada item. Se faltar campo obrigatório, o relatório diz qual: ajustar os valores e repetir.

## 3. Fechamento
- Rodar os testes: `tests/teste_spec_*.py`, `teste_valida_paridade.py`, `teste_ponte_legado.py`; criar `tests/teste_spec_faixa5.py` (variante, paridade, grades, campos de abertura) como o `teste_spec_patente.py`.
- Registrar no `STATUS.md` e no `LOG_OPERACOES_NOITE.md` (um item por linha, com onde apagar), atualizar `ORDEM_DOS_ITENS.md`, commitar, reiniciar o servidor (porta 8765) e pedir ao usuário para recarregar a extensão.
- Depois da faixa 5: faixa 7 (participacao_evento, organizacao_evento, curso_ministrado), faixa 8 e itens fora da matriz.

## Achados da faixa 5 já tratados
Rótulos/visibilidade da captura aplicados no gerador; potencial de inovação Sim=S/Não=N com a pergunta "Possui potencial de inovação de produtos, processos ou serviços?"; grades de inventores/melhoristas e depositantes; órgão depositário e nº do registro como campos de abertura; exceções globais em `docs/campos-lattes/ref/_excecoes_globais.json`.
