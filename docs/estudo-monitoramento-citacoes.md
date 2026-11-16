# Estudo: monitorar a vida de pesquisador (citações em várias plataformas)

Objetivo: o pesquisador vê, num só lugar, **quem o cita, onde, quando e quanto**, com o **maior recall possível** e sem
contar a mesma citação duas vezes. Hoje o projeto já tem `radar.py` (OpenAlex + Crossref por ORCID/nome → obras).
Este estudo propõe a extensão para citações.

## 1. Princípio central

Nenhuma base cobre tudo. Para maximizar citações encontradas é preciso **(a) resolver bem a identidade do autor e das
obras, (b) consultar várias fontes de citação em paralelo, (c) unir por identificador (DOI) e por similaridade de
título/ano/autores, e (d) guardar a proveniência** (qual fonte viu cada citação). O ganho vem da *união* das fontes:
cada uma enxerga um pedaço diferente do mundo.

## 2. Fontes (ordenadas por valor/custo)

| Fonte | O que dá | Acesso | Observações |
| --- | --- | --- | --- |
| **OpenAlex** | Citantes de cada obra (`filter=cites:W…`), contagens por ano, `referenced_works` | API aberta; desde 2026 pede chave gratuita com cota em créditos (confirmar em developers.openalex.org) | Melhor cobertura aberta e global; base de partida. Já usada em `radar.py`. |
| **Crossref** | `is-referenced-by-count` e, via `reference` de outros DOIs, quem cita | API aberta | Só cita se o editor depositou referências; contagem subestima. |
| **OpenCitations (COCI/Index)** | Pares DOI→DOI abertos | API aberta sem chave; dump completo para uso em massa | Cobertura menor que OpenAlex, mas independente e auditável (verificar caminhos v1/v2 no site oficial). |
| **Semantic Scholar** | Citantes com **contexto/intenção** (trecho que cita) | Graph API, chave gratuita sob pedido | Único com trecho da citação — ótimo para o usuário ver *como* foi citado. Limites a confirmar. |
| **Europe PMC** | Citantes em biomédica, inclusive preprints e patentes | API aberta | Forte em saúde/vida. |
| **PubMed / PMC (E-utilities, `elink` cited-in)** | Citantes dentro de PMC | API aberta | Complementa Europe PMC. |
| **SciELO / Redalyc / LA Referencia / BDTD / OASISBR** | Citações em periódicos e teses lusófonas/latino-americanas | OAI-PMH, APIs do SciELO Citation Index, texto aberto | **Diferencial Brasil**: OpenAlex/Scopus pegam pouco de teses e periódicos nacionais. Aqui entra a busca em texto completo (item 3.4). |
| **CORE, BASE, DOAJ** | Texto completo de repositórios abertos | APIs (CORE com chave gratuita) | Base para busca por título/DOI dentro de texto. |
| **Scopus / Web of Science** | Contagens e citantes de bases comerciais | API paga/institucional (chave do usuário ou da instituição) | Opcional, "traga sua chave". Não redistribuir dados; ver licenças. |
| **Google Scholar** | Maior recall prático | **Sem API; scraping viola termos e bloqueia por CAPTCHA** | Não automatizar. Oferecer apenas: link direto "ver no Scholar" e importação manual do perfil (CSV/ BibTeX). |
| **Dimensions, Lens.org** | Citações + patentes, políticas, ensaios clínicos | Lens tem API com token; Dimensions é paga | Lens é valioso para **citações em patentes**. |
| **Altmetric / PlumX / Crossref Event Data** | Menções em mídia, políticas públicas, Wikipédia, redes sociais | Variada; Event Data aberta | Vão além de citação acadêmica: "impacto" da vida de pesquisador. |
| **Unpaywall** | Versão aberta (OA) da obra | API aberta (e-mail) | Ajuda a achar o texto para busca em full-text. |
| **ORCID** | Lista de obras e identificadores (autoritativa, escolhida pelo autor) | API pública | Entrada principal de identidade; Lattes não tem API pública. |

## 3. Como obter o MÁXIMO de citações

### 3.1 Identidade: descobrir *todas* as obras
1. Entradas combinadas: **ORCID** (obras), **Lattes** (o produto já lê o currículo: títulos, DOIs, ISSN, ano),
   OpenAlex Author ID, Scopus Author ID, ResearcherID, Google Scholar ID (informado pelo usuário).
2. Cada obra do Lattes vira uma "obra-semente" com DOI quando houver; sem DOI, resolve-se por busca
   título+ano+primeiro autor (Crossref `query.bibliographic`, OpenAlex `title.search`) com limiar de similaridade e
   **confirmação do usuário** para casos ambíguos (evita citar obra de homônimo).
3. Variantes de nome (ABNT: "SILVA, A. B."; "A. B. Silva"; sem acentos; nome de casada) guardadas por usuário e usadas
   na busca em texto completo.
4. Obras sem DOI (teses, relatórios, capítulos, software): usar identificadores alternativos (handle, ISBN, URL do
   repositório, DOI do Zenodo/SciELO Data) e busca por título.

### 3.2 Citações "diretas" por identificador (alta precisão)
Para cada obra-semente, consultar **em paralelo** OpenAlex, Semantic Scholar, OpenCitations, Crossref, Europe PMC,
Lens. Resultado: lista de citantes (DOI/título/ano/periódico/autores) + a fonte que o viu.

### 3.3 União e desduplicação (onde nasce o recall)
- Chave 1: DOI normalizado (já existe `normalize_doi`). Chave 2: título normalizado + ano ±1 + sobrenome do 1º autor
  (já existe `normalize_title`). Chave 3: similaridade (Jaro-Winkler/token-set) com limiar alto para o restante.
- Preservar `fontes: ["openalex","s2",…]` em cada citação. Contagem exibida = **união**, mostrando também a de cada
  fonte e "visto só em X" (ajuda o usuário a entender discrepâncias).
- Autocitação: marcar quando o citante tem coautor em comum com a obra (padrão do mercado); exibir contagem com e sem.

### 3.4 Citações "ocultas" por texto (recall adicional)
Quem cita sem DOI ou onde as bases não indexaram:
- Busca de **título exato entre aspas** e de "SOBRENOME, A. B. Título" em texto completo de CORE, BASE, OASISBR/BDTD,
  SciELO, Europe PMC full text, arXiv/SSRN/SciELO Preprints.
- Rastrear **referências dentro de teses e dissertações** (BDTD): parsear a lista de referências dos PDFs abertos e
  casar com as obras do usuário (o projeto já tem extração de PDF em `extractor.py`; reutilizar).
- Resultado entra como "citação por texto" com **confiança menor** e trecho para o usuário confirmar/rejeitar.

### 3.5 Expansão por grafo
- **Citantes de citantes** não interessam; mas **versões da mesma obra** sim: preprint, versão publicada, versão em
  repositório, tradução. OpenAlex agrupa versões; Crossref tem `relation` (`is-preprint-of`, `has-version`).
  Consultar citações de **todas as versões** e somar sem duplicar.
- Obras citantes de capítulos: consultar também o DOI do livro.

### 3.6 Fora da academia (impacto)
Patentes (Lens, Europe PMC), políticas públicas e documentos de agências (Overton, se licenciado), Wikipédia e mídia
(Crossref Event Data, Altmetric), repositórios de código (citações de software via CITATION.cff/Zenodo). Exibir como
categorias separadas de "impacto", não somadas às citações acadêmicas.

## 4. Monitoramento contínuo ("vida de pesquisador")

- **Varredura incremental**: guardar o último estado por obra; consultar filtros por data (`from_publication_date`,
  `from_created_date` no OpenAlex) em vez de rebaixar tudo. Frequência: semanal (suficiente; bases atualizam com atraso).
- **Alertas**: nova citação, novo citante de interesse (país, periódico, autor), salto de contagem, nova obra do usuário
  detectada em ORCID/OpenAlex que ainda não está no Lattes (**ligação com o produto**: "esta obra não está no seu
  Lattes — preencher agora" usando o autofill existente).
- **Painel**: citações por ano, por obra, por país/instituição de quem cita, índice h/i10 calculados *sobre a união*
  (documentar o método; difere de Scholar/Scopus), co-citação e parceiros novos.
- **Linha do tempo de carreira**: junta o que o usuário já registra no Lattes (itens/certificados) com impacto, para
  relatórios de progressão/CAPES/CNPq.
- **Exportação**: CSV/JSON/BibTeX e relatório PDF para comprovar citações (preservando fonte e data da consulta).

## 5. Arquitetura sugerida (encaixa no projeto atual)

```
radar.py (obras)  ──►  citacoes/
                         fontes/openalex.py, semanticscholar.py, opencitations.py,
                                 crossref.py, europepmc.py, lens.py, texto_aberto.py
                         resolvedor.py   (identidade: ORCID/Lattes/OpenAlex → obras-semente)
                         unificador.py   (desduplicação, proveniência, autocitação)
                         monitor.py      (varredura incremental, diffs, alertas)
server.py: /api/citacoes/<obra>, /api/citacoes/resumo, /api/alertas
SQLite (lattes_records.db): obras, citacoes(obra_id, citante_key, fontes, 1ª_vez_visto), execucoes
```
- Cada fonte implementa a mesma interface `citantes(obra) -> list[Citacao]`, com timeout, cache e *retry* com backoff;
  falha de uma fonte não derruba as outras (resultado parcial com aviso).
- Executar em fila/worker (o agente/fila de jobs já existe) e não na requisição web.
- Cache por DOI (TTL de dias) e respeito aos limites; `mailto`/chaves via variáveis de ambiente, **sem expor chaves no
  front-end**.

## 6. Riscos e decisões

| Tema | Decisão recomendada |
| --- | --- |
| Google Scholar | Não raspar. Link e importação manual (CSV). Maior recall prático, mas inviável legal/tecnicamente. |
| Licenças | OpenAlex/OpenCitations/Crossref são abertos (CC0/CC-BY); Scopus/WoS só com chave do próprio usuário e sem redistribuição. |
| Homônimos | Nunca atribuir obra sem DOI por nome sozinho; pedir confirmação; manter lista de "rejeitadas". |
| LGPD | Só dados bibliográficos públicos; consentimento para monitorar; permitir apagar histórico. |
| Cotas de API | Orçamento por usuário/dia; varredura incremental; cache compartilhado por DOI (não por usuário). |
| Transparência | Mostrar sempre fontes e data da consulta; contagem diverge entre plataformas e isso é normal. |
| Fatos a confirmar | Limites atuais de OpenAlex (créditos/chave), Semantic Scholar e caminhos v2 do OpenCitations — checar nas documentações oficiais antes de implementar. |

## 7. Roteiro por fases

1. **MVP (1–2 sem.)**: resolver obras por ORCID + Lattes; citantes via OpenAlex + OpenCitations + Crossref; unificador por
   DOI/título; tela "Minhas citações" com contagem, lista e fontes.
2. **Recall (2–3 sem.)**: Semantic Scholar (com contexto), Europe PMC, Lens (patentes), versões da obra, autocitação.
3. **Brasil (2–3 sem.)**: SciELO/BDTD/OASISBR/CORE em texto completo, parsing de referências de teses, confirmação manual.
4. **Contínuo (2 sem.)**: varredura semanal, alertas por e-mail, painel e exportação.
5. **Integração Lattes**: obra nova detectada → sugestão de cadastro com autofill; relatório de impacto.

## 8. Métrica de sucesso
Medir **recall** num conjunto-ouro: 5–10 pesquisadores reais, contar manualmente citantes (incluindo Scholar) e comparar
com a união do sistema; meta inicial ≥ 80% do Scholar com precisão ≥ 95%. Repetir a cada fase para ver o ganho de cada fonte.
