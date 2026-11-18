# Banco de instituições e captação gradual

A lupa de instituições do Lattes (`sele_inst()` → `prc_inst_form`) só pesquisa por texto no servidor do CNPq. O LattesData
guarda o que ela devolve e consulta esse banco antes de tocar no Lattes.

## Peças

| Peça | Onde | O que faz |
|---|---|---|
| Banco, dicionário e fila | `instituicoes.py` (tabelas `inst_*` no SQLite do app) | Nomes, siglas, códigos, confirmações de usuários, fila de prefixos, métricas por consulta |
| API | `server.py` → `/api/instituicoes/{buscar,gerenciador,proximo-lote,registrar,confirmar,desfazer,config,importar}` | Tudo exige sessão; as rotas que gravam exigem Origin do próprio app |
| Lupa no preenchimento | `static/app.js` (template do preenchimento; gerar a extensão com `python extensao/build.py`) | Escolhe instituição/curso pela lupa nos campos desabilitados; cada consulta é guardada (gravação oportunista) |
| Modo coleta | mesmo template, `G.coleta` | Só pesquisa os termos recebidos, com intervalo mínimo; não preenche nada |
| Extensão | `extensao/background.js`, `content-app.js` (v0.9.5) | Roda a coleta na aba do Lattes e devolve os lotes às abas do app |
| Ponte | `static/instituicoes-ponte.js` | Grava os lotes no servidor; `lote_id` evita gravar duas vezes se houver várias abas |
| Gerenciador | `static/captacao.html`, `captacao.js` | Liga/desliga, tetos, executar lote, prefixos, desempenho, busca e importação de semente |
| Revisão | `genAssistirInstituicao()` em `static/app.js` | No campo Instituição mostra o que o banco sabe, deixa escolher/confirmar e avisa quando falta conexão com o Lattes |

## Regras da coleta

- Desligada por padrão. Teto por dia (padrão 40, máx. 200), por lote (10, máx. 25) e intervalo (4 s, mín. 2 s).
- Ordem fixa: **Universidade, Instituto, Faculdade, Hospital, Centro, Fundação**. Só depois de esgotar esses 6 é que se aprofunda.
- Um prefixo "satura" quando devolve o máximo que a lupa mostra (detectado quando o maior número de resultados se repete em 3+ consultas ou fixado em `cap_resultados`). Aí entram as próximas palavras mais frequentes nos nomes já guardados (e qualificadores iniciais).
- Consulta com erro não conta como feita.
- Consultas de uso (preenchimentos) não gastam o teto da coleta.

## Ainda não verificado no Lattes real

- Formato do `href` do resultado (`seleciona(...)`): o código é lido do primeiro argumento. O gerenciador guarda amostras reais em "Formato dos links da lupa" para conferir.
- Limite de resultados por busca, paginação e como a lupa trata prefixos curtos: aparecem em "Desempenho" depois das primeiras consultas.
- A coleta abre o formulário de bancas só para alcançar a lupa e o deixa aberto; fechar depois.
- Termos de uso do Lattes quanto à coleta em volume: conferir antes de ligar para todos os usuários.
- A lista do e-MEC não é baixada pelo sistema: importar o CSV pelo gerenciador.
