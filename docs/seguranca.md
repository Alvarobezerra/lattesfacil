# Segurança e proteção de dados do LattesFácil

## Regra principal
**Nada é entregue sem o código de acesso.** Páginas, API, exemplos e arquivos enviados exigem sessão. Só duas rotas são
públicas de propósito: `/api/health` (devolve apenas `{"ok": true}`) e `/api/lattes/ping` (sinal do conector que roda
na aba do Lattes e não consegue enviar cookie; só grava "online/nome" sob um identificador aleatório de 128 bits).

## Como usar
- Na primeira execução o servidor gera um código aleatório e o salva em `.acesso` (fora do git). Ele aparece uma vez no console.
- Para definir o seu: variável `LATTESFACIL_CODIGO` (mínimo 10 caracteres). Para trocar o código: apague `.acesso` e reinicie.
- Entrar: abrir a plataforma e digitar o código. Sair: botão **Sair** no topo. A sessão dura 12 horas.
- Por padrão o servidor escuta **só em 127.0.0.1**. Para hospedar, defina `HOST=0.0.0.0` **e** `LATTESFACIL_HTTPS=1`.

## O que cada proteção impede
| Risco | Proteção |
| --- | --- |
| Qualquer pessoa com o link ler, gravar ou apagar registros | Sessão obrigatória em todas as rotas (401 / redireciona ao login) |
| Adivinhar o código | Comparação em tempo constante, atraso por erro, bloqueio de 5 min após 5 erros por IP |
| Outro site mandar o seu navegador agir (CSRF) | Cookie `SameSite=Strict` + verificação de `Origin` em tudo que altera dados |
| Roubo da sessão por script injetado | Cookie `HttpOnly` (o JavaScript não lê) + `Secure` em HTTPS + CSP `script-src 'self'` |
| Ver PDFs enviados por outra sessão | Cada envio fica preso à sessão que o criou (403/404 para as demais) |
| Injeção de cabeçalho pelo nome do arquivo baixado | Nome sanitizado e `filename*` em UTF-8 |
| Ler arquivos do servidor (`server.py`, banco, `.acesso`) | Verificação de caminho nas rotas de arquivos |
| Página embutida em site falso (clickjacking) | `X-Frame-Options: DENY` e `frame-ancestors 'none'` |
| Vazamento de detalhes em erros | Mensagens genéricas; a query string não vai para o log |
| Conexões penduradas | Timeout de 60 s |
| Perder dados por engano | **Exclusão lógica** (o registro some da lista, mas fica no banco) |
| Perder dados por falha | **Backup automático** do banco ao iniciar e a cada 6 h em `backups/` (30 cópias, API de backup do SQLite) |

## Dados que merecem cuidado
- `lattes_records.db`: registros salvos (títulos, autores, eventos). Para recuperar uma exclusão:
  `UPDATE records SET deleted_at = NULL WHERE id = '...'`. Para restaurar o banco: copie um arquivo de `backups/` por cima.
- Arquivos enviados ficam **só na memória** por 30 minutos e não vão para o disco.
- `docs/campos-lattes/_raw/` (fora do git) traz trechos do currículo do usuário de teste: apague quando não precisar mais.
- Ative a criptografia de disco (BitLocker) no computador: protege o banco e os backups contra furto do equipamento.

## Antes de hospedar (Render ou outro)
1. Defina `LATTESFACIL_CODIGO` no painel da hospedagem (o `render.yaml` já aponta para isso com `sync: false`).
2. **O plano gratuito do Render apaga o disco a cada reinício**: o banco e os backups somem. Use disco persistente ou um banco gerenciado.
3. Use sempre HTTPS (`LATTESFACIL_HTTPS=1`). Nunca abra túnel público sem o código ativo.
4. Um código compartilhado serve para o teste com poucas pessoas. Antes de abrir para mais gente, migre para login por usuário
   (cada pessoa vê só os seus registros) e dois fatores.

## Ainda não coberto
- Login individual por usuário e registro de auditoria (quem apagou o quê).
- Criptografia do banco em repouso (hoje depende do disco).
- Limite de requisições para rotas além do login (a API autenticada não tem limite por IP).
- Os módulos `radar`, `compliance`, `organizer` e `email_parser` foram revisados só nas rotas do servidor, não internamente.

Testes: `python tests/teste_seguranca.py` (40 verificações contra o servidor em execução).
