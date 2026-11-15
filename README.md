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

## Próximos Passos Mapeados

1. ~~**Cadernos de Resumos com Múltiplos Artigos**~~ — implementado: em "Caderno de resumos" (Passo 1), envie o PDF dos anais e o nome do pesquisador (`POST /api/caderno`); escolha o resumo encontrado para carregar no formulário.
2. **Fluxo de Login e Preenchimento no Lattes**:
   - Como o Lattes exige autenticação individual (sessão `cvlattesweb`), o usuário realiza o login normalmente ou utiliza o script/extensão no próprio navegador logado, preenchendo todos os campos de uma vez.
   - Tratamento de limites específicos dos campos do Lattes (ex.: `f_isbn` aceita apenas 13 dígitos numéricos sem hífens) e adição direta na grade de autores.
