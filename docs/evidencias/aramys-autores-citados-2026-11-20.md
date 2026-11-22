# Evidência — Autores citados no currículo de Aramys

## Identificação da consulta

- Pesquisador: Aramys Silva dos Reis
- ID Lattes informado: `1040580590566490`
- URL pública tentada: `https://lattes.cnpq.br/1040580590566490`
- Data da tentativa: 20/11/2026
- Objetivo: coletar o menu/tela pública **Autores citados no currículo**.

## Dados brutos observados

### Navegador

- A janela disponível do Chrome estava intitulada `Currículo Lattes - Google Chrome`.
- O documento efetivamente carregado era:
  `https://wwws.cnpq.br/cvlattesweb/PKG_MENU.menu?f_cod=1091B2D13BB2647986D06A0344B2BACF`
- O documento carregado identificava o currículo como **Álvaro Antônio Bezerra dos Santos**, não Aramys.
- O menu exibido continha o item `Menu secundário - Autores citados no currículo`, mas esse item pertencia ao currículo de Álvaro e não foi usado como evidência de Aramys.
- Ao tentar substituir o endereço por `https://lattes.cnpq.br/1040580590566490`, a barra de endereço passou a mostrar o endereço, porém o documento não navegou: continuou exibindo o currículo de Álvaro.

### Acesso HTTP direto

Tentativa feita com a mesma URL pública:

```text
https://lattes.cnpq.br/1040580590566490
```

Resultado bruto:

```text
Este host não é conhecido. (lattes.cnpq.br:443)
```

Também foi tentada a abertura pelo mecanismo de consulta web, que retornou que a URL não era acessível pela ferramenta.

## Lista normalizada

Nenhum autor foi registrado.

```json
{
  "pesquisador": "Aramys Silva dos Reis",
  "id_lattes": "1040580590566490",
  "fonte": "menu público 'Autores citados no currículo'",
  "autores": [],
  "status": "não_coletado"
}
```

## Limitação

Não foi possível acessar uma sessão pública ou autenticada do currículo de Aramys que exibisse a tela solicitada. A página observada pertencia a outro currículo, e a tentativa de acesso direto ao domínio público falhou por resolução de host. Por isso, nenhum nome foi copiado de listas de coautoria, ORCID ou fontes secundárias: isso não comprovaria a lista do menu **Autores citados no currículo**.

## Próximo passo necessário

Para completar a coleta, é necessário abrir o currículo de Aramys em uma sessão do Lattes com acesso ao ID informado e acionar o menu **Autores citados no currículo**. A tabela visível deverá ser salva junto com a lista normalizada, preservando ao menos `nome_do_autor`, `nome_em_citacoes`, `producao` e `projetos`, quando esses campos estiverem presentes.
