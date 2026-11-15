# Base de Conhecimento: Auditoria Estratégica e Otimização do Currículo Lattes
## Conformidade Métrica, Interoperabilidade e Atratividade na Divulgação Científica

Documento orientador para o motor de auditoria inteligente, regras de validação e arquitetura de conformidade do **LattesFácil**.

---

## 1. Visão Geral e Princípios Fundamentais

Auditar um Currículo Lattes exige ir além da revisão ortográfica ou da inserção esporádica de certificados: trata-se de uma intervenção técnica e narrativa dividida em duas frentes complementares:

1. **Auditoria de Conformidade Estrutural e de Barema:** Eliminar erros de classificação taxonômica, omissões de metadados verificáveis (como DOI, ISSN e ISBN) e falhas de vínculo institucional que causam perda direta de pontuação em seleções de pós-graduação, concursos públicos, editais de fomento (como bolsas de Produtividade em Pesquisa do CNPq) e na coleta anual da Plataforma Sucupira da CAPES.
2. **Engenharia de Atratividade e Divulgação Científica:** Transformar um repositório burocrático estático em uma vitrine dinâmica de resultados, competências práticas, produtos técnico-tecnológicos (PTT) e impacto social.

### Premissas Críticas para o Motor de Auditoria:
* **Princípio da Verificação Estrita:** Comissões avaliadoras e algoritmos de extração operam sob verificação estrita. Examinadores munidos de um barema (tabela de pontuação) não reclassificam itens cadastrados na aba incorreta; se um artigo completo publicado em periódico revisado por pares for registrado apenas como trabalho em evento, ou se um produto técnico for lançado como produção bibliográfica, o item é desconsiderado ou glosado. Da mesma forma, sistemas computacionais e comissões de avaliação descartam produções "órfãs" (desvinculadas de projetos e instituições) ou desprovidas de identificadores persistentes.
* **Janela de Processamento e Congelamento (24h / 30 dias):** Alterações salvas nos módulos de edição não se tornam públicas nem alimentam bases externas até que o usuário acione o comando "Enviar ao CNPq", cujo processamento leva cerca de 24 horas para consolidação pública. Por esse motivo, revisões profundas nunca devem ser deixadas para a véspera de submissões, observando-se uma antecedência mínima de um mês (30 dias) em relação ao prazo de inscrição em editais ou ao congelamento da base para avaliação.

---

## 2. Fase 1: Auditoria de Conformidade e Mitigação de Erros de Barema

A perda de competitividade raramente decorre apenas da falta de produção; na maioria das vezes, origina-se do desconhecimento da arquitetura de pontuação dos baremas e das regras de validação documental (janelas de 3, 5 ou 10 anos).

### 2.1. Referencial Concreto: Chamada de Produtividade em Pesquisa (PQ/CNPq)
* **Janelas Temporais:** 5 anos completos para o Nível C e 10 anos completos para os Níveis B e A.
* **Escala de Pontuação:**
  * Tese de doutorado concluída ou supervisão de pós-doutorado concluída: **40 pontos**.
  * Dissertação de mestrado concluída: **20 pontos**.
  * Iniciação científica (IC) concluída: **5 pontos**.
* **Travas Máximas:**
  * Nível C: até 5 orientações de IC (máx. 25 pts) e 2 supervisões de pós-doc (máx. 80 pts).
  * Níveis B e A: até 10 orientações de IC (máx. 50 pts) e 4 supervisões de pós-doc (máx. 160 pts).
* **Gargalo Crítico:** Os baremas pontuam estritamente orientações concluídas. Manter ex-orientandos na aba *"Orientações e supervisões em andamento"* anos após a defesa reduz a pontuação daquele trabalho a zero.
* **Direito à Extensão Parental:** Deixar de registrar licenças-maternidade, paternidade ou adoção na aba `Dados Gerais > Licenças` perde o direito à extensão de **dois anos na janela de avaliação produtiva** para cada parto ou adoção ocorrido no período estipulado pela chamada.

---

### 2.2. Matriz de Erros Taxonômicos e Procedimentos de Correção

| Falha ou Erro Identificado | Impacto na Avaliação (Barema / Sucupira) | Procedimento Técnico de Correção no Lattes |
| :--- | :--- | :--- |
| **Artigo em periódico lançado apenas em Eventos** (ou resumo expandido lançado como artigo completo) | Perda severa de pontos (se artigo ficou em eventos) ou questionamento em banca (se resumo virou artigo). | Cadastrar o artigo definitivo em `Produções > Produção Bibliográfica > Artigos completos publicados em periódicos` (com ISSN, DOI, volume, número e páginas). Se houve versão nos anais e artigo posterior, ambas podem constar em suas seções. Resumos expandidos pertencem a `Trabalhos publicados em anais de eventos`. |
| **Textos de portais, blogs ou jornais em "Artigos Completos"** (ex.: Jota, ConJur, Folha) | Risco de glosa no CNPq e CAPES; a aba de periódicos destina-se apenas a journals/reviews com peer review. | Migrar publicações voltadas ao público geral, colunas e textos sem avaliação por pares para `Produção Bibliográfica > Texto em jornal ou revista (magazine)`. |
| **Artigo submetido/em avaliação lançado como "Artigo Aceito"** | Pode ser interpretado como desonestidade acadêmica; exige carta formal de aceite. | Registrar manuscritos submetidos apenas como `Trabalho em andamento`. Em `Artigos aceitos para publicação`, inserir exclusivamente artigos com carta de aceite formal. Quando publicado, transferir sem duplicar. |
| **Capítulo de livro registrado como Livro Completo** (ou Livro Organizado) | Desconsideração do item por erro de classificação durante conferência do ISBN e autoria. | Quem escreveu uma contribuição em obra organizada por terceiros registra em `Capítulo de livro`; quem organizou a obra inteira registra em `Livro organizado`. |
| **Trabalho aprovado em congresso, mas não apresentado**, lançado em Apresentações | Violação das instruções de preenchimento, que vedam listar trabalhos aprovados sem efetiva exposição. | Manter em `Apresentação de trabalho e palestra` apenas comunicações, conferências ou pôsteres efetivamente apresentados. Recomenda-se lançar primeiro a participação no evento em `Eventos`. |
| **Produção Técnica lançada como Produção Bibliográfica** (pareceres, apostilas, relatórios, softwares) | Avaliador desconsidera o item por inconsistência e não faz transferência para a seção técnica. | Realocar relatórios técnicos, pareceres, materiais didáticos, manuais, softwares e cursos ministrados para suas subcategorias específicas em `Produções > Produção Técnica`. |
| **Co-orientação registrada como Orientação Principal** | Comissões verificam atas e documentos comprobatórios, invalidando o registro incorreto. | Editar o registro em `Orientações` e selecionar especificamente a condição de **Co-orientação** em TCCs, ICs, dissertações ou teses. |
| **Cursos frequentados vs. Cursos ministrados trocados** | Confusão entre formação passiva (baixa pontuação) e produção técnica/docente ativa. | Cursos em que o titular participou como aluno vão para `Formação > Formação Complementar` (curta 8-40h, média 40-70h, longa 70-120h). Cursos ministrados vão para `Produção Técnica > Cursos de curta duração ministrados`. |

---

### 2.3. Auditoria de Metadados, Grafia e "Zumbis Curriculares"

O motor de auditoria deve executar seis verificações sequenciais:

1. **Preenchimento de Identificadores Persistentes (DOI, ISSN e ISBN):**
   * Artigo em periódico: Obrigatório ISSN e DOI. A inserção do DOI recupera metadados automaticamente via CrossRef. Na ausência de DOI, o ISSN deve ser validado para confirmação do estrato Qualis.
   * Livros e capítulos: Obrigatório ISBN, cidade e nome da editora.
2. **Conferência da Ordem Exata e Nome Completo dos Coautores:**
   * Jamais alterar a ordem de autoria para colocar o próprio nome em primeiro lugar (falha grave de integridade).
   * Verificação de autoria qualificada (1º, 2º, 3º, último ou autor correspondente).
   * Inserir nomes completos sem abreviações para localização automática na Plataforma Sucupira.
3. **Limpeza Tipográfica e Sintática:**
   * Remover aspas (`" "`) e travessões dos títulos (sistemas legados do CNPq frequentemente convertem aspas em `?` no currículo público).
   * Em eventos, evitar redundâncias como *"Participou da I Jornada de..."*, informando apenas o nome oficial.
4. **Encerramento de Vínculos e Completude da Formação:**
   * Encerrar vínculos de empregos/bolsas anteriores que continuam marcados como "Atual".
   * Na Formação Acadêmica: preencher datas de conclusão, títulos de TCC/dissertação/tese, nome do orientador e instituição completa com sigla e cidade.
5. **Migração Correta de Orientações Concluídas:**
   * Nunca recadastrar do zero nem deixar em andamento.
   * Abrir a ficha em `Orientações e supervisões em andamento` $\rightarrow$ clicar em **"Salvar como orientação concluída"** $\rightarrow$ ajustar o ano de término efetivo $\rightarrow$ Salvar.
6. **Padronização de Pareceres (Peer Review e Fomento):**
   * Cadastrar em `Produção Técnica > Trabalhos técnicos`.
   * Realizar 1 registro para cada parecer emitido (ex: 5 pareceres = 5 registros), com título preservando anonimato (ex: *"Parecer Artigo xx21 Local"*), indicando a revista/agência e a finalidade de peer review.

---

## 3. Fase 2: Arquitetura Relacional e Interoperabilidade (Lattes, Sucupira e Bases Globais)

Um currículo livre de erros de digitação pode ser descartado se falhar na arquitetura relacional entre instituições, projetos e produções.

### 3.1. A Regra de Ouro do Vínculo Institucional e a Tríade da Sucupira
* **Itens Órfãos:** Projetos, disciplinas, linhas de pesquisa e orientações desvinculadas de uma Atuação Profissional ativa são descartados pelas avaliações da CAPES e Sucupira.
* **Data de Vínculo:** Na Plataforma Sucupira, só podem ser declaradas produções intelectuais publicadas a partir do ano em que o docente ou discente foi formalmente vinculado ao PPG.
* **Padronização da Instituição:** Selecionar o nome exato no Diretório de Instituições do CNPq (usando a lupa de busca) e vincular a unidade e o código do curso no SNPG/CAPES.

```
                   ┌────────────────────────────────────────┐
                   │    Tríade Relacional da Sucupira       │
                   └───────────────────┬────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
[ PROJETO DE PESQUISA ]     [ PRODUÇÕES ASSOCIADAS ]     [ ORIENTAÇÕES VINCULADAS ]
- Título oficial do PPG     - Conexão interna na ficha   - Alunos e bolsistas
- Financiadores e valores   - Artigos, patentes e PTTs   - CPF e linha de pesquisa
```

1. **Cadastro Integral de Projetos:** Título oficial, objetivos, situação coerente (*Em andamento*, *Concluído* ou *Desativado*), agência financiadora com número do processo e equipe completa com CPF.
2. **Vinculação Interna no Formulário:** Dentro da ficha de cada Projeto, vincular as produções C&T e as orientações resultantes. Em projetos de extensão, registrar alunos em `Orientações de outra natureza`.
3. **Permissão de Importação em "Autores Citados na Produção":** Na barra lateral esquerda do Lattes, abrir *"Autores citados na Produção"* e marcar a opção *"Autorizo este autor a importar produções do meu Currículo Lattes"* para orientadores, alunos e coautores chave.

### 3.2. Sincronização de Identificadores e Correção do Fator H
* **Variações de Nome em Citações:** Cadastrar todas as variações com que assinou trabalhos para evitar desindexação externa.
* **Meus Dados CAPES & ORCID:** Conectar ORCID ID, atualizar e-mails e autorizar sincronização com CrossRef, DataCite, Scopus ID e Web of Science (ResearcherID).
* **Google Scholar para ORCID:** Exportar arquivo `.bib` do perfil do Google Scholar Citations e importar em `Works > Add works > Import BibTeX` no ORCID.
* **Auditoria do Fator H no Lattes:**
  * Se o Fator H da Web of Science no Lattes estiver subdimensionado, os artigos faltam no perfil ResearcherID.
  * **Método A (via RIS):** Baixar `.ris` das publicações no Lattes/web, subir no ResearcherID e acionar *"Recuperar dados"* no módulo Citações do Lattes.
  * **Método B (via Portal CAPES):** Buscar no Web of Science via Portal de Periódicos CAPES e enviar diretamente para ResearcherID.
  * Dados de SciELO e Scopus: atualização manual periódica na aba Citações.

---

## 4. Fase 3: Engenharia de Atratividade e Divulgação Científica

Com as avaliações multidimensionais da CAPES e CNPq, o currículo deve comunicar liderança científica, formação de recursos humanos e aplicação prática.

### 4.1. Reengenharia do Texto Inicial (Pitch de 30 Segundos)
Substituir o resumo automático gerado pelo CNPq por uma síntese estruturada em quatro pilares:
1. **O que pesquisa e vínculos:** Formação acadêmica, atuação profissional atual, credenciamento em PPG, grupos de pesquisa e bolsas de produtividade.
2. **Abordagem metodológica:** Ênfases de pesquisa, recorte técnico e conexões interdisciplinares.
3. **Onde publica e resultados:** Produções de alto impacto, projetos financiados e redes de pesquisa.
4. **Competências práticas aplicadas:** Desenvolvimento tecnológico, produtos técnicos e contato imediato.
* **Tradução Manual para o Inglês:** O sistema do CNPq só traduz automaticamente 6 módulos estruturados (níveis, grandes áreas, idiomas). Textos descritivos livres (Resumo Inicial e descrição de Projetos) **não são traduzidos automaticamente**; a versão em língua inglesa deve ser redigida manualmente.

### 4.2. Curadoria de Impacto: Os 10 Trabalhos Mais Relevantes
* **Ícone da Estrela:** O manual vigente do CNPq permite destacar os **10 trabalhos mais relevantes** da trajetória acadêmica (marcar *"Sim"* na relevância durante a edição).
* **Prêmios e Títulos:** Registrar menções honrosas, prêmios de melhor trabalho e títulos acadêmicos (distinguindo formalmente prêmio de título).
* **Outras Informações Relevantes:** Utilizar o campo livre para síntese qualitativa do perfil, comentários sobre o conjunto da obra, bolsas/apoios e corpo editorial.

---

### 4.3. Matriz dos 21 Produtos Técnico-Tecnológicos (PTT / CAPES) no Lattes

Conforme deliberação da 185ª reunião do CTC-ES da CAPES, as produções aplicadas devem ser alocadas nos submódulos exatos do Lattes:

| Produto Técnico-Tecnológico (PTT) | Submódulo Exato no Lattes | Diretrizes de Registro e Valorização |
| :--- | :--- | :--- |
| **1. Produto bibliográfico técnico/tecnológico** | `Produção Bibliográfica > Texto em jornal ou revista` ou `Outra produção bibliográfica` | Artigos em revistas técnicas, textos em catálogos, resenhas. Preencher veículo, páginas e URL. |
| **2. Ativos de Propriedade Intelectual** | `Patentes e Registros` ou `Inovação` | Patente, cultivar, desenho industrial, marca. Informar instituição de depósito e número de registro INPI. |
| **3. Software / Aplicativo** | `Patentes e Registros > Programa de computador registrado` OU `Produção Técnica > Programa sem registro` | Para software sem registro, manter PDF da estrutura de código; marcar disponibilidade como "Restrita" se não aberto. |
| **4. Tecnologia Social e Extensão** | `Produção Técnica > Extensão tecnológica` e `Trabalhos técnicos` | Serviços prestados a governos, empresas e ONGs com impacto social; vincular ao Projeto de Extensão. |
| **5. Cursos de Capacitação Ministrados** | `Produção Técnica > Cursos de curta duração ministrados` | Explicitar na descrição se atuou na formulação da proposta (estrato T2 CAPES) ou execução docente (T4). |
| **6. Produto de Editoração** | `Produção Bibliográfica > Livro organizado` OU `Produção Técnica > Editoração` | Organização de livros, anais, revistas e corpo editorial. Indicar ISBN/ISSN e conselho editorial. |
| **7. Material Didático ou Instrucional** | `Produção Técnica > Desenvolvimento de material didático ou instrucional` | Apostilas, glossários, vídeos pedagógicos. Inserir URL pública de acesso. |
| **8. Protocolo Tecnológico / POP** | `Produção Técnica > Processos ou técnicas` ou `Outra produção técnica` | POPs, manuais de operação técnica, protocolos clínicos e diretrizes terapêuticas. Vincular ao projeto de origem. |
| **9. Norma ou Marco Regulatório** | `Produção Técnica > Trabalhos técnicos` ou `Outra produção técnica` | Estudos de regulamentação, anteprojetos de normas, sentenças arbitrais e estudos jurisprudenciais. |
| **10. Relatório Conclusivo e Consultoria** | `Produção Técnica > Relatório de pesquisa`, `Assessoria e consultoria` | Em Relatórios, citar número de processo da agência de fomento e resumo dos resultados. Em Consultoria, comprovar via declaração. |
| **11. Mídia e Divulgação Científica** | `Produção Técnica > Entrevistas, mesas redondas` e `Redes sociais, websites e blogs` | Incluir URL do vídeo/entrevista. Em blogs/sites, cadastrar apenas portais acadêmicos e Moodle (nunca redes pessoais). |
| **12. Produtos de P&D e Protótipos** | `Produção Técnica > Produtos` (Piloto, Projeto, Protótipo) | Piloto para resultados preliminares, Protótipo para prova de conceito. Informar contratos em sigilo como "Restrita". |

---

### 4.4. Recurso de "Preenchimento Duplo" (Inovação e Popularização de C&T)
* **Regra Anti-Duplicidade:** Nunca recadastrar manualmente o mesmo item em abas diferentes.
* **Preenchimento Duplo Nativo:** Ao cadastrar uma produção em sua aba primária (Bibliográfica, Técnica, Patentes ou Eventos), responder **"Sim"** às perguntas sobre *Educação e Popularização de C&T* ou *Inovação*. O Lattes replica a exibição automaticamente nos módulos da barra superior sem duplicar o registro na base de dados.

### 4.5. Coerência de Trajetória: "Lattes Vazio" vs. "Lattes Fraco"
* **Lattes Vazio (Recém-iniciado e Coerente):** Poucos itens, mas com Iniciação Científica documentada, agência de fomento (CNPq/FAPESP), monitoria e apresentações na área. É competitivo para sua etapa de carreira.
* **Lattes Fraco (Volumoso e Desfocado):** Repleto de cursos genéricos de curta duração e publicações em periódicos Qualis C desconexos do tema de pesquisa, demonstrando falta de foco científico.
* **Indexação na Busca Textual:**
  * **Áreas de Atuação:** Atualizar Grande Área, Área e Subárea eliminando enquadramentos defasados da graduação.
  * **Setores de Aplicação (CNAE):** Selecionar os códigos CNAE correspondentes e ordenar por relevância (setas ▲▼).
  * **Palavras-Chave Específicas:** Substituir termos vagos por termos técnicos exatos procurados na área.

---

## 5. Fase 4: Ferramentas Digitais e Protocolo Operacional de Manutenção

### 5.1. Ferramentas Automatizadas de Auditoria

| Ferramenta | Ambiente | Aplicação Prática |
| :--- | :--- | :--- |
| **Qualis no Lattes / QLattes** | Extensão Chrome | Classifica artigos pelo Qualis CAPES na página pública; calcula pontuação típica CNPq dos últimos 5 anos; aponta ISSN ausente. |
| **Exportação XML (.zip)** | Nativo CNPq | Baixa arquivo compactado com identificador de 16 dígitos estruturado no schema XSD para auditorias em lote. |
| **lucyLattes** | Script Python | Lê XMLs do Lattes, gera planilhas CSV e relatório HTML com indicadores: IndOri, IndAut, IndDis e IndProdArt. |
| **scriptLattes / OpenLattes** | Python / R / IA | Compilação de redes de coautoria para PPGs e grupos de pesquisa; uso de LLM para interpretação de campos não estruturados. |
| **Numeração Manual & Impressão** | Técnica de entrega | Inserção de numeração correspondente aos PDFs dos comprovantes; impressão via Ctrl+P nativo do navegador para evitar quebras. |

---

### 5.2. Protocolo Passo a Passo em 5 Etapas

1. **Passo 1 · Cotejo Documental Inicial (PDF vs. Acervo Real):** Gerar PDF atual, ativar Qualis no Lattes e cruzar com certificados, diplomas, portarias e comprovantes reais.
2. **Passo 2 · Saneamento por Ordem de Impacto:**
   * *Produções Bibliográficas:* DOI e ISSN em periódicos; ISBN, editora e cidade em livros; transferir artigos aceitos já publicados; mover textos não revisados para jornal/revista.
   * *Formação Acadêmica:* Datas de conclusão, títulos de monografias/dissertações/teses e orientadores.
   * *Orientações:* Migrar defesas concluídas via botão *"Salvar como orientação concluída"*.
3. **Passo 3 · Fechamento da Arquitetura Relacional e Produção Técnica:**
   * Amarrar disciplinas, linhas e projetos à Atuação Profissional ativa.
   * Vincular produções e orientações dentro de cada Projeto de Pesquisa.
   * Cadastrar PTTs nas 12 subcategorias de Produção Técnica com flag de Preenchimento Duplo (Inovação / C&T) e marcar os 10 trabalhos mais relevantes com a Estrela.
4. **Passo 4 · Otimização Narrativa, Sincronização de IDs e Envio:**
   * Reescrever Resumo Inicial em 4 pilares (português e inglês manual).
   * Sincronizar ORCID e ResearcherID (recuperar dados do Fator H).
   * Ativar autorização de importação em *Autores citados na Produção*.
   * **Acionar "Enviar ao CNPq"** e aguardar a consolidação de 24 horas.
5. **Passo 5 · Rotina Permanente de Manutenção (Tempo Real + 4 Janelas Anuais):**
   * *Tempo Real:* Cadastrar cada artigo, evento ou parecer no próprio dia do acontecimento (leva menos de 10 minutos).
   * *4 Marcos Trimestrais:* Revisões com a agenda em **Janeiro**, **Páscoa**, **Julho** e **Setembro** para atualizar disciplinas, orientações e vínculos.
   * *Antecedência Mínima:* Auditoria fina com o barema **30 dias antes** de qualquer edital ou coleta Sucupira.
