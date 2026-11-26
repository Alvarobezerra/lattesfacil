# LattesFácil — Extração e Cadastro Assistido no Currículo Lattes

Projeto iniciado em 15/11/2026 para simplificar a extração de metadados de produções acadêmicas (como resumos em anais de eventos) e o preenchimento automatizado na Plataforma Lattes (CNPq).

## Estrutura da Pasta

- `server.py` — Servidor web e API REST (`http://127.0.0.1:8765`) para upload de PDFs, extração de metadados, busca externa (CrossRef / OpenAlex / Google Books) e armazenamento local em SQLite.
- `caderno.py` — Segmentação de cadernos de resumos (um resumo por página): título, autores, palavras-chave, eixo, idioma e dados do evento (nome, cidade, ISSN, ano); busca por nome do pesquisador.
- `certificado.py` — Leitor de certificados de apresentação ("Certificamos que..."): título, evento, promotora, cidade, forma de apresentação, autores com papéis; confere se o usuário selecionado consta no certificado.
- `artigo.py` — Leitor de artigos de periódico (PDF ou DOI colado): consulta o DOI no Crossref (título, autores, periódico, ISSN, volume, páginas), lê as palavras-chave do PDF e confere o autor selecionado.
- `orientacao.py` — Leitor de declarações, atas de defesa e certificados de orientação (mestrado, doutorado, TCC, IC...): natureza, orientando, instituição, curso, ano e papel do usuário (orientador/coorientador).
- `extractor.py` — Motor de extração de texto e metadados de PDFs (PyMuPDF), identificação de título, autores, palavras-chave, evento, ano, ISBN/ISSN, páginas e área do conhecimento.
- `requirements.txt` — Dependências Python (`pymupdf`, `requests`).
- `lattes_records.db` — Banco de dados SQLite local com os registros extraídos/salvos.
- `static/` — Interface web do **LattesFácil**:
  - `index.html` — Tela de envio de PDF/texto, revisão dos 3 blocos de campos e geração de script/JSON para preenchimento no Lattes.
  - `styles.css` — Estilização da interface.
  - `app.js` — Lógica de frontend e gerador de script de autopreenchimento para o formulário `pkg_trabalho.form` do Lattes.
- `exemplos/` — Arquivos PDF de teste utilizados na validação do projeto:
  - `2024-SEMICresumo.pdf` — Resumo individual (SEMIC 2024 / UFMA).
  - `bbr.ptm.23.384_FeSBE2026.pdf` — Caderno/anais com múltiplos resumos (FeSBE 2026) para rastreamento por nome de pesquisador/autor.

## Documentação e Base de Conhecimento

- `docs/base-conhecimento-auditoria-lattes.md` — **Base de Conhecimento Oficial**: Auditoria Estratégica e Otimização do Currículo Lattes (Conformidade Métrica, Interoperabilidade Sucupira/Bases Internacionais, Mapeamento dos 21 PTTs da CAPES e Protocolo de Manutenção).
- `docs/especificacao-modulo-barema-editais.md` — **Especificação do EditalScore**: Arquitetura e fluxo da Calculadora Automática de Editais & Baremas com geração de Dossiê Paginado.
- `docs/melhorias-e-roadmap.md` — Benchmark de mercado, proposta de valor e roadmap técnico do LattesFácil.
- `docs/auditoria-lattes-checklist.md` — Checklist de auditoria baseado em normas CAPES/CNPq.
- `docs/mockup-auditoria-lattes-v2.html` — Mockup visual interativo da Central de Conformidade (Command Center / Split-screen).
- `docs/campos-lattes/` — Mapeamento detalhado dos campos dos formulários da plataforma Lattes (`pkg_trabalho.form`, etc.).

## Como Executar

```bash
pip install -r requirements.txt
python server.py
```

Acesse em `http://127.0.0.1:8765`.

## Análise opcional com Gemini

A integração fica desligada por padrão. Para testar, crie uma chave em
[Google AI Studio](https://aistudio.google.com/api-keys). No terminal da pasta do
projeto, a forma recomendada é:

```powershell
python iniciar_gemini.py
```

Esse iniciador pede a chave completa em uma janela com campo de senha no Windows
(aceita Ctrl+V), quando a variável estiver ausente ou incompleta. Copie pelo botão
de copiar do AI Studio: não digite os
asteriscos exibidos na tela. A chave fica apenas na memória do processo.
Antes de iniciar, ele testa classificação, transcrição de um PDF fictício e extração
de campos (três chamadas reais). Só inicia se o teste passar. O acesso será em
`http://127.0.0.1:8766`, restrito ao computador local. Para outra porta, use
`python iniciar_gemini.py --port 8767`. Ctrl+C encerra sem traceback.

Alternativamente, configure **no terminal que inicia o servidor** (Windows
PowerShell ou PowerShell 7):

```powershell
$env:GEMINI_ENABLED = "1"
$env:GEMINI_MODEL = "gemini-3.5-flash-lite"
$chave = Read-Host "Cole a chave Gemini" -AsSecureString
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new("", $chave).Password
python server.py
```

Se já houver um servidor aberto, encerre-o e inicie novamente nesse terminal.
Essas variáveis valem para a sessão atual; não são gravadas em arquivos. O projeto
não carrega `.env` automaticamente. Em hospedagem, configure as mesmas variáveis
no painel de ambiente/segredos do serviço e reinicie a aplicação. Nunca coloque a
chave em `static/`, no navegador, no Git ou em mensagens.

Em **Atualizar**, envie uma evidência ou cole seu texto como de costume. A mensagem
de leitura indica a consulta ao Gemini. Se a classificação divergir da leitura
local, confirme o tipo de documento. No formulário, os avisos mostram os campos
extraídos pela IA e seus trechos de origem. Revise antes de enviar ao Lattes.

Com a integração ligada, o texto é enviado ao Google para classificação e, quando
o formulário é aberto, para extração dos campos simples definidos na especificação
do item. Grades de autores e outros campos compostos continuam com os leitores
locais. PDFs, PNG, JPEG e WebP com menos de 40 caracteres extraídos são enviados
para transcrição visual; PDFs mistos com texto suficiente ainda usam a leitura local.
Cadernos identificados pelo fluxo próprio de busca não são enviados integralmente.

Cada análise pode fazer duas chamadas (classificação e campos), mais uma quando
precisar de transcrição. Confirmar ou trocar o tipo faz nova extração. Os limites
iniciais são 60 mil caracteres de texto e 10 MB para envio visual. Erros 503
(modelo temporariamente sobrecarregado) têm até duas novas tentativas, com pausas
de 1 e 2 segundos; erros de chave, cobrança ou requisição não são repetidos.
Acompanhe tokens e custos no painel do AI Studio; não há
um teto financeiro implementado no aplicativo.

Chave ausente, erro da API, limite excedido ou resposta inválida preservam a leitura
local e exibem um aviso. Para desligar: `$env:GEMINI_ENABLED = "0"` e reinicie.
Para documentos pessoais, configure o serviço pago e confira as condições de
tratamento de dados do Google; use documentos sintéticos no primeiro teste.

Os testes automatizados usam respostas simuladas, sem chave nem cobrança:

```powershell
python -m unittest discover -s tests -p test_gemini.py -v
```

### Diagnosticar erros da API

No mesmo terminal em que configurou a chave, pare o servidor com Ctrl+C e execute:

```powershell
python ferramentas/diagnosticar_gemini.py
```

O comando faz uma chamada real com um certificado fictício, usando o mesmo cliente
da aplicação. Se falhar e a chave tiver formato compatível, compara uma chamada mínima,
uma consulta de modelos e uma consulta sem chave. Salva `tmp/diagnostico-gemini.json`
(fora do Git), com o código HTTP e o motivo retornado pelo Google, ocultando a chave.
Não envia documentos pessoais.
Depois execute `python server.py` novamente, preservando as variáveis dessa sessão.
A interface distingue erros de chave, permissões, modelo, cota, cobrança e esquema
JSON; o código HTTP 400 sozinho não prova que a chave esteja incorreta.

## Próximos Passos Mapeados

1. ~~**Cadernos de Resumos com Múltiplos Artigos**~~ — implementado: em "Caderno de resumos" (Passo 1), envie o PDF dos anais e o nome do pesquisador (`POST /api/caderno`); escolha o resumo encontrado para carregar no formulário.
2. **Fluxo de Login e Preenchimento no Lattes**:
   - Como o Lattes exige autenticação individual (sessão `cvlattesweb`), o usuário realiza o login normalmente ou utiliza o script/extensão no próprio navegador logado, preenchendo todos os campos de uma vez.
   - Tratamento de limites específicos dos campos do Lattes (ex.: `f_isbn` aceita apenas 13 dígitos numéricos sem hífens) e adição direta na grade de autores.
