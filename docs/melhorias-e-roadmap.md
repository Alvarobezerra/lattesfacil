# LattesFácil: Proposta de Valor, Benchmark e Roadmap de Melhorias

Documento de balizamento estratégico e técnico para a evolução do **LattesFácil**, consolidado a partir do estudo regulatório recente do CNPq, do ecossistema de ferramentas existentes e do mapeamento dos serviços de consultoria acadêmica terceirizada.

---

## 1. Contexto Regulatório e Dores do Usuário

O preenchimento e a manutenção do Currículo Lattes deixaram de ser apenas uma tarefa burocrática e passaram a envolver riscos administrativos, jurídicos e financeiros:

* **Portaria CNPq nº 2.664/2026 (art. 8º) e Instrução Normativa CNPq nº 16/2026:**
  * Instituem penalidades expressas para dados inverídicos, desatualizados ou inconsistentes no Lattes.
  * Infrações classificadas em **Leve, Grave e Gravíssima**.
  * Sanções incluem: **advertência formal, cancelamento/devolução de bolsas, suspensão em editais de fomento e suspensão do Lattes por até 1 ano**.
* **Dores Centrais do Pesquisador e Estudante:**
  * **Falta de tempo crônica:** dezenas de certificados, resumos e artigos acumulados ao longo do ano em pastas desorganizadas ou caixas de e-mail.
  * **Interface legada e lenta:** formulários complexos no sistema `cvlattesweb` (múltiplas telas, iframes, modais lentos para cadastrar cada autor e campos obrigatórios com regras rígidas como ISBN de 13 dígitos).
  * **O Dilema da Segurança (Gov.br):** para terceirizar a atualização, o pesquisador precisava entregar seu login pessoal do Gov.br (que dá acesso a IRPF, CNH, carteira de trabalho e contas bancárias), gerando enorme receio.
  * **Risco de Inconsistências:** medo de preencher campos incorretamente ou em seções erradas e sofrer glosa em auditorias de editais ou concursos.

---

## 2. Benchmark de Mercado: Plataformas, Ferramentas e Consultorias

O ecossistema em torno da Plataforma Lattes divide-se em três vertentes principais:

### 2.1. Plataformas e Ferramentas Tecnológicas

| Solução / Ferramenta | Abordagem / Tecnologia | Pontos Fortes | Limitações e Fricções |
| :--- | :--- | :--- | :--- |
| **"Lattes com IA"** (`lovable.app`) | Infoproduto (R$ 147) ensinando prompts para o **Claude in Chrome** (Computer Use). | Utiliza visão computacional e agentes de IA avançados. | **Custo oculto alto** (exige Claude Pro a ~US$ 20/mês); lento (a IA move o cursor na tela); não é um software integrado. |
| **Lattes em Dia** (`lattesemdia.com.br`) | Plataforma web + Extensão Chrome com IA para triagem de comprovantes. | Interface amigável; organiza comprovantes e orienta a tela correta do Lattes. | **Não realiza autopreenchimento direto no formulário**; atua apenas como guia/checklist lateral para o usuário digitar. |
| **QLattes / Qualis no Lattes** | Extensões de navegador (Chrome/Firefox). | Visualização imediata do estrato Qualis-CAPES e métricas (JCR) em currículos públicos. | Focado estritamente em **leitura e métricas**, sem recursos de inserção ou cadastro. |
| **scriptLattes / LattesScraper** | Scripts em Python / Open Source (GitHub). | Extração e mineração em lote de currículos públicos para grupos de pesquisa e universidades. | Ferramentas estritamente acadêmicas/CLI voltadas a administradores, sem suporte à escrita/atualização. |

### 2.2. Mercado de Consultoria Humana e Assessoria Acadêmica

Devido à complexidade do sistema oficial, existe um mercado maduro de profissionais e agências que cobram para atualizar o Lattes manualmente:

* **Microserviços e Freelancers (*VintePila, GetNinjas, Workana, Superprof*):**
  * *Criação do zero:* R$ 30,00 a R$ 50,00.
  * *Atualizações pontuais (lotes de 5 a 10 certificados):* R$ 20,00 a R$ 50,00.
  * *Cobrança por volume ou páginas geradas:* R$ 70,00 a R$ 150,00 (ou taxa base de R$ 70 + R$ 3 a R$ 6 por página impressa excedente).
* **Empresas Especializadas em Assessoria Acadêmica (*HelpsMed, Atualizar Lattes*):**
  * *Pacotes de Atualização Completa:* Na faixa de **R$ 350,00 a R$ 497,00** para lotes de até 50 documentos com conferência minuciosa.
  * *Adequação a Editais e Baremas de Concurso / Residência Médica:* De **R$ 400,00 a R$ 800,00+**. O consultor confere os comprovantes com as regras de pontuação da banca examinadora.
* **Mentorias e Workshops Individuais ao Vivo (Hotmart / Zoom):**
  * Sessões de 1h a 2h cobrando de **R$ 100,00 a R$ 300,00**, onde o especialista orienta por chamada de vídeo para que o cliente não precise ceder sua senha do Gov.br.

---

## 3. Posicionamento e Proposta de Valor do LattesFácil

O **LattesFácil** ocupa um espaço único e inexplorado: uma **ferramenta de software dedicada, determinística, rápida e local-first**, que une a extração inteligente de documentos ao autopreenchimento no navegador, eliminando custos de assinaturas internacionais e garantindo sigilo absoluto.

```
       [ Documentos Acadêmicos: PDFs, Anais de Eventos, Certificados ]
                                      │
                                      ▼
                        LattesFácil (Motor Local/Web)
       ├── Extração Estruturada (PyMuPDF, Regex, IA Especializada)
       ├── Segmentação de Cadernos de Resumos (Busca por Autor/Nome)
       ├── Enriquecimento com Bases Externas (CrossRef, OpenAlex, Google Books)
       ├── Validação Anti-Alucinação (Protocolo 3V / Schema CNPq)
       └── Sincronização e Anti-Duplicação (Leitura de XML do Lattes)
                                      │
                                      ▼
             [ Extensão / Injetor DOM no Lattes (cvlattesweb) ]
       * Usuário logado de forma segura via Gov.br (zero risco de credencial)
       * Injeção instantânea nos campos e na grade de coautores
                                      │
                                      ▼
                 [ Usuário confere e clica em Salvar ]
```

### Vantagens Competitivas Frente ao Mercado:

1. **Privacidade e Segurança Absoluta (Sem Senha Gov.br):** Diferente das consultorias humanas, o usuário opera logado em sua própria máquina; nenhuma credencial pessoal é compartilhada.
2. **Zero Assinatura Recorrente em Dólar:** Não obriga o usuário a pagar US$ 20/mês de Claude Pro (modelo do *Lattes com IA*).
3. **Autopreenchimento Real vs. Apenas Guia:** Diferente do *Lattes em Dia*, o LattesFácil preenche de fato os formulários HTML e as grades de autores em 1 segundo.
4. **Extração de Cadernos Complexos:** Capacidade única de processar anais inteiros de congressos (300+ páginas) e localizar automaticamente as páginas exatas do pesquisador.
5. **Autonomia e Agilidade:** O que levaria dias aguardando um consultor ou horas de digitação manual é feito em minutos pelo próprio usuário.

---

## 4. Pilares de Qualidade: O Protocolo 3V Adaptado

Para assegurar total compliance com a Portaria CNPq nº 2.664/2026 e evitar autuações de integridade acadêmica:

1. **01. Verificar (Fidelidade Documental Estrita):**
   * O sistema apenas preenche dados explicitamente comprovados no documento ou confirmados via bases oficiais (CrossRef/OpenAlex).
   * O que não for detectado é marcado como `pendente` para revisão manual, **sem jamais inventar ou alucinar dados**.
2. **02. Vincular (Organização e Dossiê Comprobatório):**
   * Cada registro preenchido é indexado ao seu comprovante digital padronizado: `ANO_TIPO_PRIMEIRO-AUTOR_TITULO-CURTO.pdf`.
3. **03. Validar (Supervisão Humana Soberana):**
   * O sistema automatiza o preenchimento dos campos, mas a confirmação de gravação e o botão final de **"Enviar ao CNPq"** permanecem sob o comando humano.

---

## 5. Roadmap Estruturado de Funcionalidades

### Fase 1: Motor Central e Formulários Essenciais (Em Execução)
- [x] Extração de textos de PDFs individuais (PyMuPDF) e metadados.
- [x] Segmentação de cadernos de resumos/anais volumosos com busca por autor (`caderno.py`).
- [x] Enriquecimento de metadados via CrossRef, OpenAlex e Google Books.
- [x] Mapeamento do formulário de eventos (`pkg_trabalho.form`).
- [ ] Schema unificado (`lattes_schema.json`) e expansão para outros tipos de produção:
  - Artigos publicados em periódicos (com busca de DOI e ISSN).
  - Apresentações de trabalho, conferências e palestras.
  - Capítulos de livros e livros autorais/organizados (ISBN).
- [ ] Suporte à manipulação direta da grade de coautores e palavras-chave.

### Fase 2: Experiência do Usuário (Extensão Chrome / Firefox)
*Elimina a necessidade de abrir o Console de Desenvolvedor ou usar bookmarklets manuais.*
- [ ] **Extensão Oficial de Navegador (Manifest V3)**:
  - Comunicação fluida com o servidor local (`http://127.0.0.1:8765`).
  - Detecção automática da tela ativa do Lattes (`cvlattesweb`).
  - Botão flutuante limpo: *"Preencher com LattesFácil"*.
  - Automação de modais auxiliares de cadastro de autores e instituições.
- [ ] Interface integrada e responsiva com preview lado a lado (PDF do comprovante à esquerda, campos detectados à direita).

> **Atualização 16/11/2026:** implementados e acessíveis em `/painel.html` (testes em `tests/teste_novos_modulos.py` e `tests/teste_api_novos.py`): upload em lote com ZIP organizado por ano (`lote.py`), importação do XML do Lattes com checagem de duplicatas (`lattes_xml.py`), auditor de conformidade com risco Leve/Grave/Gravíssimo (`auditor.py`) e EditalScore com leitura de barema, cálculo, simulação "e se" e dossiê PDF (`edital.py`). Limites conhecidos: estrato Qualis depende de base informada pelo usuário; leitura do edital é heurística (o candidato revisa); renomeação física no disco do usuário e entrada por e-mail encaminhado seguem pendentes.

### Fase 3: Anti-Duplicação, Auditoria e Diagnóstico (Lattes Audit)
*Garante conformidade com as novas regras punitivas do CNPq e fundamenta-se na [Base de Conhecimento de Auditoria Estratégica](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-auditoria-lattes.md).*
- [ ] **Importação do XML do Lattes**:
  - Leitura do currículo exportado pelo próprio pesquisador.
  - Checagem automática de duplicações antes de preencher novos itens.
- [ ] **Auditor de Conformidade CNPq**:
  - Identificação de artigos sem DOI, ISSNs inválidos ou dados essenciais ausentes.
  - Alerta de inconsistências em nomes de autores e vínculos institucionais pendentes de término.
  - Emissão de relatório de pendências classificado por risco (Leve, Grave e Gravíssimo).

### Fase 4: Caixa de Entrada Acadêmica e Lote Inteligente
*Captura a dor dos usuários que acumulam dezenas de comprovantes no ano.*
- [ ] **Integração Inteligente de E-mail (Privacidade Estrita — Sem IMAP Invasivo)**:
  - **Mecanismo 1 · Suporte Nativo a Arquivos de E-mail (`.eml` / `.msg`)**:
    - Permite ao usuário arrastar o e-mail salvo do Gmail, Outlook ou Thunderbird diretamente no Passo 1 da plataforma.
    - O extrator analisa o formato MIME, extrai automaticamente os PDFs anexos (certificados) e rastreia links de emissão de certificados (Even3, Doity, Sympla, Galoá).
    - *Vantagem:* 100% processado no ambiente do usuário, sem risco de acesso à caixa de entrada completa e sem necessidade de senhas de aplicativo.
  - **Mecanismo 2 · Encaminhamento Rápido ("Encaminhe para o LattesFácil")**:
    - Endereço de recepção seguro (`certificados@lattesfacil.com.br` ou `inbox+{id}@lattesfacil.com.br`).
    - O pesquisador apenas clica em "Encaminhar" no seu próprio e-mail (web ou celular).
    - Webhook de entrada processa a mensagem isolada, extrai os comprovantes e notifica o usuário com os dados prontos no formulário.
    - *Vantagem:* Simplicidade extrema (1 toque), sem exigir configurações complexas de 2FA/senhas de aplicativo e com consentimento expresso a cada envio (compliance total com LGPD).
- [ ] **Upload em Lote de Certificados (ZIP ou Arrastar Pasta)**:
  - Fila de processamento em background com OCR/PyMuPDF para certificados de participação, ouvinte e apresentação.
  - Classificação automática por categoria do Lattes.
- [ ] **Organizador Físico de Comprovantes**:
  - Renomeação automática e padronização dos arquivos PDF no disco do usuário.
  - Estruturação em pastas organizadas por ano acadêmico (`2024/`, `2025/`, etc.).

### Fase 5: Módulo de Alto Valor — EditalScore & Dossiê para Concursos e Seleções
*Substitui os pacotes de assessoria acadêmica mais caros do mercado (R$ 400 a R$ 800 por processo seletivo). Documentação técnica completa em [Especificação do Módulo de Baremas](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/especificacao-modulo-barema-editais.md).*

- [ ] **EditalScore: Leitor Inteligente de Editais e Baremas**:
  - Upload do PDF do edital ou anexo de pontuação (Concursos Docentes EBTT/Magistério Superior, Mestrado/Doutorado, Residências ENARE, Bolsas CNPq/FAPESP).
  - Extração automática de tabelas de pontuação para o padrão estruturado `barema_schema.json` (blocos, itens, pesos unitários, subtetos e teto global).
  - Editor visual rápido para o candidato revisar, calibrar ou personalizar os critérios de pontuação da banca.

- [ ] **Motor de Matching e Cálculo Instantâneo de Pontuação**:
  - Cruzamento do barema com o `curriculo.xml` do candidato e com os comprovantes já indexados no LattesFácil.
  - Aplicação automática de **janelas temporais** (ex.: últimos 3, 5 ou 10 anos) e classificação de periódicos pelo **Qualis-CAPES** mais recente.
  - Tratamento determinístico de **subtetos e tetos de blocos**, evitando falsa sensação de pontos em itens saturados.
  - Alerta de status por item: *Pontuou com comprovante*, *Pontuou pendente de comprovante*, *Excedente ao teto* e *Desqualificado*.

- [ ] **Painel de Oportunidades & Gap Analysis ("What-If")**:
  - Exibição de Score Total vs. Teto Máximo com gráfico de radar por competências (Ensino, Pesquisa, Extensão, Gestão).
  - Recomendações estratégicas: alerta onde faltam pontos para atingir o teto e onde não vale a pena gastar tempo submetendo comprovantes por teto já esgotado.
  - Simulação de cenários: quanto a nota aumentará se for adicionado determinado artigo, certificado ou tempo de docência.

- [ ] **Gerador de Dossiê Comprobatório Paginado e Indexado**:
  - Compilação automatizada de todos os comprovantes (artigos, certificados, declarações de docência e atas) em um **PDF único consolidado**.
  - Folha de rosto e sumário com tabela de autodeclaração preenchida item a item.
  - Cabeçalho carimbado no topo de cada página vinculando ao item do edital (ex.: `[Item 2.1] Artigo em Periódico A1 — Página 12 de 85`), pronto para envio à banca examinadora.
