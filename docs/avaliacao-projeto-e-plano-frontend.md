# Avaliação do LattesData e plano de fortalecimento do frontend

Documento produzido em 17/11/2026 a partir de uma leitura estrutural do projeto e dos arquivos atuais.

## 1. Resumo executivo

O projeto já possui um produto funcional bastante amplo: extração de documentos acadêmicos, classificação de evidências, leitura de currículos, auditoria, citações, editais, dossiês e integração com o Lattes por extensão de navegador.

Minha avaliação é que o backend tem boa cobertura funcional e preocupação acima da média com segurança, mas está centralizado demais em `server.py`. No frontend, existe uma base visual promissora e várias telas com bom nível de acabamento, porém a experiência ainda pode ganhar muito em consistência, orientação do usuário e tratamento de estados de carregamento/erro.

Enquanto a evolução do backend fica centralizada em outro fluxo, o melhor uso deste trabalho é fortalecer o frontend de forma independente, preservando os endpoints existentes e melhorando a camada de apresentação, navegação e feedback.

## 2. Arquitetura observada

- Backend Python com servidor HTTP próprio em `server.py`.
- Frontend estático em `static/`, com HTML, CSS e JavaScript sem framework.
- Persistência em SQLite.
- Módulos especializados para artigos, certificados, orientação, cadernos, classificação, auditoria, citações e editais.
- Extensão de navegador em `extensao/` para interação com a sessão do Lattes.
- Documentação e protótipos visuais em `docs/`.
- Testes funcionais e de segurança em `tests/`.

## 3. Avaliação do backend

### Pontos fortes

- Boa divisão dos domínios de negócio em módulos especializados.
- Autenticação por sessão, cookie `HttpOnly`, `SameSite=Strict` e expiração.
- Proteções contra CORS aberto, uploads excessivos, acesso entre sessões, path traversal e XML inseguro.
- Backup automático do SQLite e exclusão lógica de registros.
- Testes específicos para segurança, classificação, XML, lotes, duplicatas e APIs.
- Deploy preparado para Render em `render.yaml`.

### Principal risco encontrado

Existe um código de acesso fixo de fallback em `server.py`:

```python
if os.environ.get("RENDER"):
    return "merthiolate"
```

Esse fallback deve ser removido. Em produção, se `LATTESFACIL_CODIGO` não estiver configurado, o processo deve falhar explicitamente em vez de aceitar uma senha conhecida.

### Melhorias estruturais recomendadas

1. Dividir `server.py` em módulos de autenticação, uploads, currículo, registros, Lattes e editais.
2. Mover operações pesadas de PDF, lote e consultas externas para jobs assíncronos.
3. Avaliar persistência externa para uploads temporários e banco de produção.
4. Fixar versões das dependências.
5. Adicionar logging estruturado, identificador de requisição e métricas de duração.
6. Validar o comportamento do banco no ambiente de deploy, especialmente após reinício/redeploy.

## 4. Avaliação do frontend

### O que já está bom

- A landing page em `static/inicio.html` tem posicionamento claro, narrativa comercial e boa hierarquia visual.
- `static/abertura.html` apresenta uma visão de produto mais próxima de um painel real, com currículo, indicadores, produção anual e citações.
- A identidade LattesData é relativamente consistente nas telas principais: azul-marinho, ciano/teal, tipografia editorial para a marca e tipografia funcional para a interface.
- Há preocupação com acessibilidade básica: `aria-label`, navegação semântica, botões de período e textos alternativos.
- A interface já contempla fluxos avançados, como auditoria, currículo completo, instalação da extensão e acompanhamento de envios.

### Pontos de atenção

#### 1. Fragmentação visual

As telas principais usam linguagens visuais diferentes. `inicio.html` e `abertura.html` parecem pertencer ao mesmo produto, enquanto `auditoria.html` utiliza uma composição mais próxima de um mockup independente, com classes utilitárias e identidade “Lattes Shield”.

Isso pode fazer o usuário sentir que saiu do LattesData ao entrar em auditoria ou em algumas telas experimentais.

Recomendação: definir tokens compartilhados de cor, borda, raio, sombra, espaçamento, tipografia e estados. Depois aplicar esses tokens progressivamente às telas, sem reescrever tudo de uma vez.

#### 2. Fluxo principal pouco explicitado

O produto oferece muitos caminhos: enviar documento, abrir currículo, auditar, acompanhar citações, calcular edital e instalar extensão. Para um usuário novo, ainda não está completamente claro qual é a próxima ação recomendada.

Recomendação: adotar uma orientação contextual na abertura:

- primeiro acesso: “Importe seu currículo ou envie seu primeiro documento”;
- currículo carregado: “Comece pela auditoria” ou “Envie uma evidência”;
- envio pendente: “Revise e preencha no Lattes”;
- extensão ausente: aviso com CTA para instalação.

#### 3. Estados de carregamento e erro

Há muitos elementos iniciados com “Carregando…”, mas a experiência pode ser mais informativa e consistente. É importante diferenciar:

- carregando;
- vazio porque ainda não há dados;
- erro temporário;
- sessão expirada;
- ação concluída;
- ação que exige intervenção do usuário.

Recomendação: criar componentes visuais reutilizáveis de `loading`, `empty`, `error`, `success` e `needs-action`, com uma ação clara em cada estado.

#### 4. Densidade de informação

O público é acadêmico e provavelmente tolera interfaces densas, mas a densidade precisa vir acompanhada de agrupamento e prioridade. Cards demais na abertura podem competir entre si.

Recomendação: destacar no máximo três ações prioritárias no topo e deixar indicadores secundários em seções recolhíveis ou abaixo da primeira dobra.

#### 5. Confiança antes de ações sensíveis

A plataforma lida com documentos pessoais, currículo e ações relacionadas ao Lattes. Antes de salvar, preencher ou remover algo, a interface deve explicar claramente:

- o que será alterado;
- onde será alterado;
- o que ainda precisa ser revisado;
- se a ação é reversível;
- se depende da extensão ou de uma sessão aberta no Lattes.

#### 6. Responsividade e uso em telas menores

O fluxo principal deve ser confortável em notebook pequeno e tablet. Painéis com gráficos, tabelas e cards precisam ter uma versão reduzida, com navegação horizontal somente quando necessário.

#### 7. Consistência de vocabulário

O projeto alterna termos como “LattesData”, “Lattes Shield”, “auditoria”, “conformidade”, “envio” e “preenchimento”. Recomendo um glossário de interface para decidir, por exemplo:

- “Documento” para o arquivo enviado;
- “Evidência” para o documento interpretado;
- “Registro” para o item salvo;
- “Envio” para o acompanhamento da operação no Lattes;
- “Auditoria” para a análise do currículo.

## 5. Plano recomendado para o frontend

### Fase 1 — Fundamentos

- Criar tokens visuais compartilhados em `styles.css`.
- Padronizar cabeçalho, navegação, botões, cards e mensagens.
- Definir estados de carregamento, vazio, erro e sucesso.
- Melhorar foco de teclado, contraste e mensagens de validação.

### Fase 2 — Abertura como centro de comando

- Transformar `abertura.html` na tela de orientação do produto.
- Mostrar uma ação principal baseada no estado do usuário.
- Agrupar currículo, documentos recentes, pendências e próximos passos.
- Evitar que todos os indicadores tenham o mesmo peso visual.

### Fase 3 — Fluxo de envio e revisão

- Tornar o upload um fluxo em etapas visíveis: enviar, interpretar, revisar, confirmar.
- Mostrar quais campos foram encontrados automaticamente e quais precisam de confirmação.
- Usar avisos claros para baixa confiança, dados ausentes e possíveis duplicatas.
- Preservar o documento original visível durante a revisão quando possível.

### Fase 4 — Auditoria e editais

- Unificar a identidade visual da auditoria com a plataforma principal.
- Transformar alertas em tarefas acionáveis, não apenas em números.
- Exibir impacto, prioridade e ação sugerida para cada pendência.
- Diferenciar “problema de conformidade” de “oportunidade de melhoria”.

### Fase 5 — Refinamento

- Revisar responsividade em 1280px, 1024px, 768px e 390px.
- Testar navegação completa sem mouse.
- Testar mensagens para falha de rede, sessão expirada e backend indisponível.
- Remover protótipos ou deixar explicitamente marcados como experimentais.

## 6. Direção recomendada

Eu manteria a identidade atual — azul profundo, ciano/teal e marca editorial — porque ela combina com confiança, pesquisa e tecnologia. A evolução deve ser de coerência e orientação, não de uma troca completa de visual.

O maior ganho de experiência provavelmente virá de três mudanças:

1. uma abertura que diga claramente “o que fazer agora”;
2. um fluxo de revisão de documentos com estados e confiança explícitos;
3. uma linguagem visual única entre painel, auditoria, currículo e envio.

## 7. Limitação desta avaliação

Os testes automatizados não foram executados neste ambiente porque os executáveis `python.exe` e `py.exe` disponíveis apontam para o alias do WindowsApps e não puderam ser iniciados. A avaliação dos testes foi feita por inspeção estática dos arquivos e da estrutura do projeto.

