# Relatório Técnico-Metodológico de Auditoria Curricular e Proposta do Sistema LattesFácil
**Documento para Validação de Avaliadores e Especialistas Acadêmicos**

* **Data do Documento:** 15 de Novembro de 2026  
* **Projeto:** LattesFácil / Lattes Shield (Módulo de Auditoria e Conformidade Curricular)  
* **Público-Alvo:** Coordenadores de Programas de Pós-Graduação (PPGs), Membros de Bancas Avaliadoras, Consultores de Avaliação CAPES/CNPq e Pesquisadores  

---

## 1. Contexto e Justificativa Institucional

O preenchimento e a manutenção do Currículo Lattes deixaram de ser meras rotinas burocráticas e tornaram-se elementos críticos de conformidade jurídica, métrica e acadêmica no Brasil:

1. **Rigor Normativo e Sanções Administrativas:**
   * A **Portaria CNPq nº 2.664/2026 (Art. 8º)** e a **Instrução Normativa CNPq nº 16/2026** estabelecem a obrigação de veracidade, completude e atualização fidedigna das informações cadastrais.
   * Inconsistências, omissões documentais e duplicidades são passíveis de enquadramento como infrações (**Leve, Grave e Gravíssima**), sujeitando o proponente a penalidades como advertência, glosa de pontuação em editais, cancelamento de bolsas de produtividade (PQ) com devolução de recursos e suspensão do Lattes por até um ano.
2. **Impacto na Coleta Sucupira e Avaliação Quadrienal da CAPES:**
   * A Plataforma Sucupira opera sob o princípio da **verificação estrita**: examinadores e algoritmos não reclassificam produções alocadas na aba incorreta. Artigos de periódicos registrados em anais de eventos, trabalhos técnicos em abas bibliográficas ou registros sem identificadores persistentes (DOI, ISSN) são desconsiderados ou pontuados em faixas inferiores.
   * Produções "órfãs" (desvinculadas de projetos de pesquisa e atuação profissional ativa no PPG) não migram para o relatório do programa, prejudicando a nota final do curso na CAPES.
3. **Sobrecarga dos Pesquisadores e Falhas Manuais:**
   * O modelo tradicional de preenchimento manual no ambiente legado do CNPq (`cvlattesweb`) consome em média 14 a 20 horas anuais por pesquisador produtivo e apresenta alto índice de erro humano na inserção de metadados, autores e vínculos.

---

## 2. Metodologia de Auditoria Curricular (Lattes Shield)

A metodologia desenvolvida no **LattesFácil** estrutura-se em um modelo de **Auditoria Multidimensional** dividido em três fases complementares:

```
                           ┌────────────────────────────────────────┐
                           │      Metodologia Lattes Shield         │
                           └───────────────────┬────────────────────┘
                                               │
         ┌─────────────────────────────────────┼─────────────────────────────────────┐
         ▼                                     ▼                                     ▼
 [ FASE 1: BAREMA & TAXONOMIA ]      [ FASE 2: INTEROPERABILIDADE ]        [ FASE 3: PTT & DIVULGAÇÃO ]
 • Verificação estrita de abas       • Tríade Projeto ↔ Produção ↔ Orient. • Mapeamento dos 21 PTTs CAPES
 • Conformidade DOI / ISSN / ISBN    • Sincronização CrossRef / ORCID      • Preenchimento Duplo (Inovação)
 • Mitigação de inflação de dados    • Sincronização WoS / Fator H         • Pitch Executivo de 30s
 • Janelas temporais de avaliação    • Código SNPG / Diretório CNPq        • Indexação CNAE e Árvore CNPq
```

### 2.1. Fase 1: Conformidade Estrutural e Eliminação de Erros de Barema
* **Princípio da Fidelidade Estrutural:** Cada item é classificado estritamente pela sua natureza documental real, e não pelo estrato que pontua mais no edital.
* **Erros Taxonômicos Monitorados:**
  * Artigo em periódico cadastrado apenas em Eventos (ou resumo de congresso lançado como artigo completo).
  * Textos de divulgação (blogs, colunas em jornais) lançados indevidamente como artigos de periódico com *peer review*.
  * Artigos submetidos cadastrados prematuramente como "Artigo Aceito" (sem carta formal de aceite).
  * Capítulos de livro registrados incorretamente como Livro Completo/Organizado.
  * Trabalhos aprovados em congressos que não foram efetivamente apresentados.
  * Cursos assistidos (formação passiva) confundidos com cursos ministrados (produção docente ativa).
* **Auditoria de Metadados e "Zumbis Curriculares":**
  * Presença obrigatória de DOI e ISSN em 100% dos artigos.
  * Conferência da ordem original dos coautores (preservação da integridade e verificação de autoria qualificada para comitês da CAPES).
  * Limpeza de caracteres corrompidos (aspas e travessões convertidos em `?`).
  * Encerramento de vínculos de bolsas e empregos anteriores que continuam marcados como "Atual".
  * Migração formal de orientações concluídas pelo comando nativo *"Salvar como orientação concluída"*.

### 2.2. Fase 2: Arquitetura Relacional e Interoperabilidade (CAPES / Bases Globais)
* **A Tríade da Sucupira:** Amarrar cada produção científica e cada orientação a um **Projeto de Pesquisa** e a uma **Atuação Profissional ativa no PPG** (com código SNPG do curso e instituição certificada no Diretório do CNPq).
* **Sincronização de Identificadores Persistentes:**
  * Integração com ORCID ID, CrossRef, DataCite e Scopus ID.
  * Diagnóstico e recuperação do **Fator H (Web of Science)** no Lattes via arquivos `.ris` no perfil ResearcherID ou importação direta pelo Portal de Periódicos CAPES.
  * Autorização de importação no módulo *"Autores citados na Produção"* para garantir a correlação entre orientadores e discentes.

### 2.3. Fase 3: Engenharia de Atratividade e Produção Técnico-Tecnológica (PTT)
* **Texto Inicial Executivo (Pitch de 30 segundos):** Reestruturação do resumo em quatro blocos: (1) O que pesquisa e vínculos institucionais; (2) Abordagem metodológica; (3) Onde publica e resultados; (4) Competências práticas e contato.
* **Tradução Manual para o Inglês:** Inserção manual da versão em inglês do resumo e projetos (o sistema do CNPq traduz automaticamente apenas campos estruturados fechados).
* **Mapeamento dos 21 Produtos Técnico-Tecnológicos (PTTs da CAPES):** Conversão sistemática de patentes, softwares, POPs/protocolos, materiais didáticos, relatórios conclusivos de fomento e cursos de formação para os submódulos específicos de Produção Técnica.
* **Mecanismo de Preenchimento Duplo:** Utilização das caixas nativas de *Educação e Popularização de C&T* e *Inovação* na aba de origem, garantindo exibição em ambas as seções sem duplicar registros na base de dados.

---

## 3. Estudo de Caso Prático: Avaliação Piloto

Para validar a metodologia e o algoritmo de auditoria em um cenário de alta complexidade acadêmica, foi realizada a auditoria diagnóstica do currículo público do **Prof. Dr. Aramys Silva dos Reis** ([ID Lattes 1040580590566490](http://lattes.cnpq.br/1040580590566490)), Professor Associado da UFMA e Coordenador do Programa de Pós-Graduação em Saúde e Tecnologia (PPGST).

### 3.1. Dados Quantitativos Analisados
* **Produção Bibliográfica:** 61 artigos completos em periódicos nacionais e internacionais.
* **Inovação:** 3 patentes de privilégio de invenção depositadas junto ao INPI.
* **Projetos:** 34 projetos de pesquisa, 13 de desenvolvimento tecnológico e 7 de extensão.
* **Métricas de Citação:** Web of Science: 702 citações, **Fator H = 16**; SciELO: 100 citações.
* **Orientações e Bancas:** Mais de 200 orientações concluídas e 85 bancas examinadoras.

### 3.2. Diagnóstico de Vulnerabilidades Detectadas

A auditoria identificou **19 pendências estruturais**, categorizadas em quatro áreas críticas:

| Área Crítica | Ocorrências Identificadas | Impacto na Avaliação (CAPES / CNPq) | Risco Classificado |
| :--- | :--- | :--- | :--- |
| **1. Coleta CAPES / Sucupira** | **12 artigos** em periódicos sem link DOI cadastrado no Lattes. | O Sucupira importa a produção do quadriênio via CrossRef/DOI. Artigos sem DOI exigem digitação manual e sofrem frequente descarte ou perda de pontuação na avaliação do PPGST. | 🚨 **Crítico** (-120 pts estimados) |
| **2. Portaria CNPq 2.664/2026** | **7 projetos de pesquisa** financiados (FAPEMA/CNPq) com vigência expirada constando como *"Em andamento"*. | Infração ao Art. 8º (obrigação de atualização fidedigna e encerramento de vigências de projetos subvencionados). Risco de diligência formal em chamadas de bolsas PQ. | ⚠️ **Grave** |
| **3. Propriedade Intelectual (PTT)** | **3 patentes INPI** cadastradas com formatações divergentes no código de processo do depósito. | Dificuldade de indexação automatizada no banco de patentes da CAPES e no Qualis Tecnológico da área de Farmácia/Biotecnologia. | 💡 **Médio** |
| **4. Inserção Discente (PPG)** | Artigos do quadriênio com coautores discentes/egressos sem anotação explícita da linha do PPG. | Perda de pontuação no Quesito 2 (Inserção Discente e Formação de Recursos Humanos) da Ficha de Avaliação da CAPES. | 👥 **Médio** |

* **Índice Global de Saúde Curricular Calculado:** **72 / 100 Pontos**.  
* **Impacto Estimado:** Risco de glosa de até **-180 pontos** no somatório de indicadores do quadriênio do programa de pós-graduação.

---

## 4. O Sistema LattesFácil: Arquitetura e Engenharia de Solução

O **LattesFácil** foi concebido para fechar a lacuna entre o diagnóstico do erro e a sua correção automática, superando as deficiências das ferramentas existentes no mercado.

### 4.1. Módulos Técnicos do Sistema
1. **Motor Extrator Especializado (`extractor.py`, `caderno.py`, `artigo.py`, `certificado.py`, `orientacao.py`):**
   * Processamento determinístico de documentos PDF utilizando `PyMuPDF` (`fitz`) e `pdfplumber`.
   * Capacidade nativa de processar anais inteiros (livros de resumos de mais de 300 páginas) e isolar o trabalho do pesquisador por busca textual de autoria.
   * Consulta automatizada às bases CrossRef, OpenAlex e Google Books para enriquecimento automático de DOIs e metadados ausentes.
2. **Motor de Injeção Direta no DOM (`static/app.js`):**
   * Em vez de utilizar automação visual por IA (lenta e com risco de falha em formulários antigos), o sistema gera injeção estruturada diretamente nos nós do formulário do Lattes (`GN_TRABALHO` / `pkg_trabalho.form`).
   * Automação completa de campos de texto, botões de rádio, seletores e a grade dinâmica de autores (`#autorHolder`).
   * **Garantia de Não-Interferência no Botão "Salvar":** O script preenche os dados com rigor e o pesquisador valida visualmente antes de clicar em salvar.
3. **Módulo Lattes Shield / Auditor (Em Validação):**
   * Leitura do XML público ou raspagem autorizada do currículo.
   * Varredura contra a matriz de conformidade da Portaria 2.664/2026 e regras CAPES.
   * Geração de relatório visual de vulnerabilidades e script automático de blindagem em 1 clique.

### 4.2. Modelos de Interface Desenvolvidos para Avaliação
Foram construídos dois modelos de apresentação gráfica para o relatório de auditoria e contratação da solução:
* **Modelo 1 — Dashboard Vertical Contínuo:** [docs/mockup-auditoria-lattes.html](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/mockup-auditoria-lattes.html) (Apresentação linear de diagnóstico com gauge central e relatório de pendências em tema luminoso).
* **Modelo 2 — Command Center Split-Screen:** [docs/mockup-auditoria-lattes-v2.html](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/mockup-auditoria-lattes-v2.html) (Painel duplo com barra lateral fixa de métricas, abas reativas de navegação por categoria de pendência e botões de ação corretiva contextual).

---

## 5. Instrumento de Validação para os Avaliadores

Solicitamos aos pareceristas e avaliadores que analisem as proposições deste documento e respondam aos seguintes itens de validação:

### Bloco A: Rigor Metodológico e Normativo
1. A matriz de erros taxonômicos (Fase 1) cobre as principais causas de perda de pontuação e glosas observadas em bancas de concursos e avaliações de PPG da sua área?
2. O critério de ponderação de risco (Crítico para ausência de DOI em periódicos e Grave para projetos vencidos) reflete a realidade das auditorias institucionais atuais?
3. Há alguma exigência específica de comitê de área da CAPES (ex.: Medicina, Farmácia, Engenharias, Humanas) que deva ser parametrizada de forma customizada no motor de auditoria?

### Bloco B: Arquitetura Técnica e Segurança
1. O princípio de injeção determinística no navegador (onde a ferramenta preenche os campos, mas a responsabilidade de gravação e envio permanece com o usuário) atende aos requisitos de ética e integridade científica?
2. A dispensa do compartilhamento de credenciais (conta gov.br / senha) confere a segurança necessária para adoção institucional em universidades e institutos de pesquisa?

### Bloco C: Experiência Visual e Usabilidade (Mockups)
1. Qual dos dois modelos visuais ([Modelo 1 — Linear](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/mockup-auditoria-lattes.html) ou [Modelo 2 — Split-Screen](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/mockup-auditoria-lattes-v2.html)) comunica com maior clareza a urgência das correções sem criar atrito de interpretação para o pesquisador?
2. A estimativa de impacto em pontuação (-180 pontos no caso examinado) funciona como um indicador eficaz para sensibilizar docentes e discentes sobre a necessidade de saneamento curricular?

---

*Documento consolidado no repositório oficial do projeto LattesFácil em `docs/relatorio-auditoria-metodologia-validacao.md`.*
