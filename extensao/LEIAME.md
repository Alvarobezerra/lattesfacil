# Extensão LattesData — Automação 1-Clique (Chrome / Edge / Brave)

## Como instalar (uma única vez):
1. Abra `chrome://extensions` (ou `edge://extensions`).
2. Ative a chave **Modo do desenvolvedor** (canto superior direito).
3. Clique em **Carregar sem compactação** e selecione a pasta `extensao/` (ou a pasta extraída do ZIP).

## O que ela faz automaticamente:
1. **Status instantâneo:** Detecta se o Currículo Lattes (`wwws.cnpq.br`) está aberto e atualiza o selo no topo do LattesData sem precisar colar nada no Console.
2. **Fila de 1º Login:** Se você clicar em **Enviar ao Lattes** sem estar logado, ela abre a página de login do CNPq e aguarda. Assim que você entra no Lattes, ela continua o cadastro sozinha.
3. **Abertura Automática de Formulário:** Usa `modalCV2.setarUrl` do próprio Lattes para abrir direto o formulário correto (`anais`, `artigo` com DOI, `apresentacao` ou `orientacao`), sem você precisar procurar nos menus.
4. **Preenchimento e Salvamento:** Preenche todos os campos, autores, palavras-chave e áreas, e salva automaticamente (ou destaca o botão Salvar em verde, conforme sua preferência).
