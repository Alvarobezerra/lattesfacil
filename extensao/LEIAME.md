# Extensão LattesData — cadastro no Lattes com 1 clique (Chrome / Edge / Brave)

## Instalar (uma única vez)
1. Baixe `lattesdata-extensao.zip` no LattesData e **extraia** a pasta.
2. Abra `chrome://extensions` (ou `edge://extensions`) e ative o **Modo do desenvolvedor**.
3. Clique em **Carregar sem compactação** e escolha a pasta extraída.
4. Recarregue a página do LattesData (F5).

A extensão carrega sozinha sempre que o navegador abre; não há nada para iniciar no Windows.

## O que ela faz
1. Ao clicar em **Enviar e Cadastrar no Lattes**, define os cookies exigidos pelo CNPq e abre o login do Lattes.
2. Espera você entrar (Login Único / gov.br). O LattesData nunca vê sua senha.
3. Assim que o currículo abre, abre o formulário certo, preenche os campos e salva (ou destaca o botão Salvar).
4. Informa ao LattesData se o Lattes está conectado e de quem é o currículo.

## Desenvolvimento
`autofill_core.js` é gerado a partir de `static/app.js`: rode `python extensao/build.py` sempre que o template mudar.
