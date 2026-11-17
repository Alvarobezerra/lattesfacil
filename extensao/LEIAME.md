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
5. (v0.6.0) Lê o quadro de avisos do currículo: "alterações ainda não enviadas ao CNPq". No LattesData, **Verificar pendências** só lê;
   **Enviar ao CNPq…** pede confirmação, abre a tela de envio do Lattes e deixa o clique final em Enviar para o usuário
   (o envio substitui a versão que o CNPq e a busca pública mostram). Depois do envio, recarregue a aba do Lattes (F5) se o aviso persistir.
6. (v0.7.0) **Ler do Lattes agora** (página Meu currículo): pede ao próprio Lattes a "página para impressão" (modelo Completo), que é gerada na hora
   a partir do currículo atual (o XML exportado pode estar anos defasado), e entrega o HTML ao LattesData, que o interpreta (`lattes_pagina.py`).
   Só leitura. Funciona com qualquer aba do Lattes logada no currículo; as outras abas (login antigo, página inicial) são ignoradas.

## Desenvolvimento
`autofill_core.js` é gerado a partir de `static/app.js`: rode `python extensao/build.py` sempre que o template mudar.
