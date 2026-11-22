# Preparação para o modo headless — LattesData

> Situação: **somente estruturação.** A implantação começa apenas quando **inserção e exclusão** estiverem sem falhas
> na extensão (critério na seção 7). Até lá, nada aqui altera o comportamento atual.

## 1. Modelo adotado

1. O pesquisador faz o login no Lattes **ele mesmo**, numa janela visível. O LattesData **nunca recebe nem guarda senha**.
2. Detectado o currículo aberto (`modalCV2` + `f_cod`), a sessão é entregue a um navegador headless.
3. O headless executa a fila (inserir, conferir, alterar, excluir) com o **mesmo** `autofill_core.js` e as mesmas funções de página.
4. A sessão é descartada no fim da fila ou quando expira. Não há reaproveitamento entre dias.

## 2. Decisões que precisam ser tomadas agora

| # | Decisão | Opções | Recomendação inicial |
|---|---|---|---|
| D1 | **Onde o headless roda** | (a) na máquina do usuário (agente local) · (b) no servidor do LattesData | (a) primeiro: mesmo IP do login, sem custo de servidor, sem risco de bloqueio por IP de data center |
| D2 | **Como a sessão passa do login ao headless** | (a) extensão exporta cookies `.cnpq.br` · (b) Playwright abre a janela de login e exporta `storage_state` | (b) se for agente local (não depende da extensão); (a) se a extensão continuar sendo a porta de entrada |
| D3 | **Ferramenta** | Playwright (Python) · Puppeteer (Node) | Playwright Python: integra com `server.py` e com os testes em Python |
| D4 | **Tempo de vida da sessão** | medir quanto o Lattes mantém a sessão ociosa e ativa | levantar empiricamente (ver 6.1) e fixar um teto abaixo dele |
| D5 | **Concorrência** | 1 currículo por vez · N em paralelo | 1 por usuário, itens em sequência (o Lattes recarrega a página ao salvar/excluir) |
| D6 | **Quem confirma exclusões** | sempre confirmadas antes no LattesData · permitir lote | sempre confirmação individual no app, mesmo em headless |
| D7 | **Retomada após falha** | recomeçar do zero · retomar do item seguinte | retomar, usando o mesmo controle de "já clicou em Salvar" (`lfSalvou`) para nunca gravar duas vezes |
| D8 | **Registro de execução** | o que guardar de cada passo | estado, nº do item (seq), avisos do Lattes, captura de tela só em erro — nunca cookies |

## 3. Separação de camadas (estruturar já, sem mudar comportamento)

Hoje o `background.js` mistura **lógica de negócio** com **transporte da extensão**. Mapeamento das chamadas:

| API `chrome.*` | Ocorrências | Papel | Equivalente headless |
|---|---|---|---|
| `scripting.executeScript` | 14 | rodar código na página | `page.evaluate` / `page.add_script_tag` |
| `tabs.query` / `tabs.get` / `tabs.create` / `tabs.update` | 15 | achar/abrir/esperar aba | `context.pages`, `page.goto`, `wait_for_load_state` |
| `tabs.sendMessage` | 6 | devolver resultado ao app | HTTP/WebSocket para o `server.py` |
| `storage.local` | 6 | fila pós-login e último resultado | fila no banco/servidor |
| `cookies.set` | 2 | cookies `imp`/`idioma` do CNPq | `context.add_cookies` |
| `windows.update` | 5 | trazer janela à frente | não se aplica |

`autofill_core.js` **não usa nenhuma API `chrome.*`** (verificado): já é portável.

### 3.1 Refatoração preparatória proposta

Criar um arquivo único de **funções de página** (`extensao/pagina_lattes.js`), sem `chrome.*`, contendo o que hoje está
dentro do `background.js` e roda no mundo MAIN:

- `rodarComFeedback(d)` — preenchimento + leitura de avisos
- `lerListaNaPagina(listaPath)` — lista de itens (ISO-8859-1)
- `abrirEExcluirNaPagina(itemPath, seq, titulo)` — exclusão com conferência de identidade
- `lerAutoresNaPagina()`, `rodarColeta(d)`
- `verificarSeAbaLogada` (corpo da função injetada)

E um **orquestrador** com interface fixa, implementado duas vezes:

```
interface Navegador {
  logado(): {logado, nome}
  injetar(arquivo)
  executar(funcao, args)          // devolve o resultado da página
  aguardarCarregada(ms)
  definirCookiesCnpq()
}
```

- `NavegadorExtensao` → usa `chrome.tabs` / `chrome.scripting` (o que existe hoje).
- `NavegadorHeadless` → usa Playwright (futuro).

As regras de **inserir → confirmar na lista → guardar seq** e **ler lista → conferir título → excluir → reconferir**
(`executarAutofillNaAba`, `confirmarNaLista`, `removerEnvio`) passam a depender só dessa interface. Assim, cada
correção feita agora na extensão vale automaticamente para o headless.

## 4. Contrato de mensagens (congelar)

Os tipos atuais viram o contrato da fila, independentemente do transporte:

| Pedido | Uso | Resultado |
|---|---|---|
| `fill` | inserir / alterar (`__alterar.seq`) | `estado`, `titulo`, `detalhes`, `seq` |
| `remove` | excluir (seq + título) | `removido` / `ausente` / `divergente` / `erro` |
| `verify` | conferir se o item existe | `ok` + `seq` / `ausente` |
| `list` | listar itens de um tipo | `itens[]` |
| `autores-coleta`, `inst-coleta` | coletas | conforme hoje |
| `cv-status`, `cv-live`, `cv-publish` | estado do currículo | conforme hoje |

Estados de resultado já usados e que devem permanecer fixos:
`ok`, `atencao`, `erro`, `login`, `ausente`, `removido`, `divergente`, `nao-suportado`.
Acrescentar para o headless: **`sessao-expirada`** (pedir novo login ao usuário).

Cada pedido deve ter **`envioId` único e idempotente**: repetir o mesmo `envioId` não pode gerar segundo cadastro.

## 5. Regras que o headless precisa respeitar (herdadas da extensão)

- Conferir o **titular** do currículo antes de qualquer ação (`__usuario` × nome logado).
- Nunca excluir sem a conferência de identidade do item aberto (`abrirEExcluirNaPagina`).
- Confirmar inserção pela **lista do Lattes** (seq novo), não pelo fechamento do formulário.
- Diálogos nativos: aceitar `confirm` só nas exclusões confirmadas no app; em headless usar `page.on("dialog")`
  registrando a mensagem, como o silenciador atual faz.
- Viewport fixo (ex.: 1366×900): o `autofill_core.js` usa `offsetParent` (8 pontos) para achar o quadro visível;
  headless com layout real (Chromium `--headless=new`) mantém isso funcionando.
- Intervalo mínimo entre itens (o mesmo ritmo humano da coleta, ~4 s), para não sobrecarregar o CNPq.

## 6. Levantamentos a fazer antes de implantar

1. **Duração da sessão** do Lattes (ociosa e em uso) e o que a página mostra quando expira → detector de `sessao-expirada`.
2. **Sessão com IP diferente**: o cookie do `wwws.cnpq.br` funciona se o headless rodar em outra rede? Decide D1.
3. **Cookies necessários**: quais cookies de `.cnpq.br` compõem a sessão (para exportar só eles, nunca os demais).
4. **Login gov.br**: se o usuário entrar pelo gov.br, a sessão final no CNPq é a mesma? (afeta D2).
5. **Termos de uso do CNPq** sobre acesso automatizado com a sessão do próprio titular.

## 7. Critério de entrada (gate) para iniciar a implantação

A implantação headless só começa quando, na extensão:

- [ ] Inserção confirmada pela lista em **100%** dos tipos com lista mapeada (`itens/listas_lattes.json`), sem duplicidade.
- [ ] Exclusão com conferência de identidade e reconferência na lista em **100%** dos mesmos tipos.
- [ ] Nenhuma falha em N execuções seguidas por tipo (sugestão: 20) na Fase 5 (`ferramentas/executor_preenchimento.js`).
- [ ] Recarga da página durante o salvar tratada sem gravar duas vezes (`lfSalvou`).
- [ ] Refatoração da seção 3.1 concluída, com os testes atuais passando.

## 8. Ordem sugerida

1. Agora: decidir D1–D8 e fazer os levantamentos da seção 6 (só leitura, sem risco).
2. Agora: refatoração 3.1 (funções de página + interface `Navegador`) — mesma extensão, mesmo comportamento.
3. Após o gate: `NavegadorHeadless` com Playwright rodando primeiro os testes da Fase 5 em headless.
4. Depois: fila real de usuários, começando por um pesquisador piloto.
