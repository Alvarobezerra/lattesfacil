# Benchmark de Plataformas Globais de Gestão Científica e Referências PLG

> **Propósito deste documento:** consolidar a inteligência competitiva e de modelo de negócio que fundamenta a camada de **Gestão Colaborativa de Projetos de Pesquisa** do **LattesData**. Analisa 7 plataformas científicas/acadêmicas líderes globais, 4 referências SaaS de crescimento liderado pelo produto (*Product-Led Growth — PLG*) no padrão *Host Pays, Guests Collaborate Free*, e conecta essas lições diretamente à arquitetura proposta em [arquitetura-projetos-pesquisa-lattesdata.md](file:///c:/Users/icrim/Downloads/Projeto/lattes-facil/docs/arquitetura-projetos-pesquisa-lattesdata.md).

---

## 1. Panorama do Mercado Global de Gestão Científica

### Por que nenhum laboratório usa uma ferramenta só?

No ecossistema científico global, a jornada de uma pesquisa — da ideação e captação do *grant* à execução experimental, escrita do manuscrito, prestação de contas e avaliação de carreira — é profundamente **fragmentada em silos especializados**. Nenhum laboratório ou grupo de pesquisa consegue operar com uma única ferramenta porque o mercado evoluiu por **recortes verticais desconectados**:

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  1. EXECUÇÃO     │   │  2. ESCRITA &    │   │  3. CIÊNCIA      │   │  4. PRESTAÇÃO DE │
│  DE BANCADA      │   │  PUBLICAÇÃO      │   │  ABERTA & DOI    │   │  CONTAS & RIMS   │
│                  │   │                  │   │                  │   │                  │
│  Benchling       │   │  Overleaf        │   │  OSF             │   │  Researchfish    │
│  Labguru         │   │  Word / Docs     │   │  Zenodo / arXiv  │   │  Symplectic      │
│  Protocols.io    │   │  Zotero / EndNote│   │  PROSPERO        │   │  Elsevier Pure   │
└────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
         │                      │                      │                      │
         └──────────────────────┴──────────────────────┴──────────────────────┘
                                           │
                      ▼ ONDE NASCEM AS LACUNAS NO DIA A DIA ▼
          • O dado experimental morre no caderno ou no laptop do aluno formado.
          • A gestão de orientandos cai no WhatsApp, Google Drive e planilhas soltas.
          • A prestação de contas e o currículo viram retrabalho manual sob pressão.
```

### Onde nascem as 4 grandes lacunas estruturais

1. **Abismo entre "Operação Semanal" e "Prestação de Contas / Carreira":** ferramentas de bancada (ELNs/LIMS) não conversam com sistemas de prestação de contas de agências de fomento nem com currículos oficiais. Por outro lado, sistemas institucionais (RIMS/CRIS) só enxergam o produto *depois* de publicado e indexado — tarde demais para organizar certificados, relatórios parciais, aprovações éticas e entregas de orientandos.
2. **Hiperespecialização disciplinar (Viés de *Wet Lab*):** os principais softwares de gestão de laboratório (Benchling, Labguru, Protocols.io) foram desenhados para biologia molecular, química e biotecnologia. Grupos de Saúde Coletiva, Computação, Engenharias, Agrárias, Humanas, Sociais Aplicadas e Artes ficam órfãos e recorrem a ferramentas genéricas (Trello, Notion, Google Drive) que não entendem autoria científica, bolsas ou fomentos.
3. **O "Problema da Formatura" (*Lab Turnover*):** estudantes de IC, Mestrado e Doutorado permanecem no grupo por 1 a 4 anos. Quando defendem e saem, certificados de congressos, PDFs comprobatórios, comprovantes de submissão e documentos regulatórios ficam dispersos em e-mails pessoais — gerando prejuízo direto ao orientador na avaliação quadrienal ou na prestação de contas do edital.
4. **Custo e Barreira de Adoção (Enterprise em Dólar vs. Orçamento Acadêmico):** soluções corporativas (Labguru, Symplectic Elements, Elsevier Pure) exigem contratos institucionais de dezenas a centenas de milhares de dólares por ano. Pesquisadores individuais e PPGs ficam sem opção acessível que combine gestão colaborativa e conformidade local.

---

## 2. Análise Individual de 7 Plataformas Científicas e Acadêmicas

### 2.1 Benchling
- **Categoria:** *Electronic Lab Notebook* (ELN) + Suíte de Biologia Molecular em nuvem.
- **Proposta de Valor Central:** substituir o caderno de papel em laboratórios de ciências da vida, integrando anotações experimentais, sequências genéticas (plasmídeos, CRISPR, primers) e histórico imutável com *timestamps* e trilhas de auditoria.
- **Solução para Continuidade de Dados (*Lab Turnover*):** o grande ganho do Benchling em universidades é garantir que protocolos, anotações e resultados experimentais de doutorandos e pós-docs permaneçam acessíveis e pesquisáveis para o *Principal Investigator* (PI) e para os próximos alunos após a formatura.
- **Modelo de Preço / Freemium:** oferece um **Plano Acadêmico 100% Gratuito** (mediante e-mail institucional `.edu` ou universitário) com ELN completo, colaboração em grupo e ferramentas de biologia molecular. Entretanto, módulos corporativos (Registro estruturado de entidades, Gestão de Inventário/LIMS avançado, automação de bioprocessos e controles *Enterprise* FDA 21 CFR Part 11) são restritos aos planos pagos voltados para indústria *biotech/pharma*.
- **O que o LattesData aprende:** o posicionamento contra a perda de memória institucional após a saída do aluno é um argumento de venda fortíssimo para orientadores; porém, o Benchling é restrito a *wet labs* e não possui qualquer camada de gestão de carreira, fomentos ou currículo.

### 2.2 Labguru
- **Categoria:** Plataforma *All-in-One* de Gestão de Laboratório (ELN + LIMS + Inventário + Equipamentos).
- **Proposta de Valor Central:** unificar caderno de laboratório, rastreamento físico de amostras (freezers, caixas, poços de microplacas), linhagens celulares, estoque de reagentes, lista de compras centralizada e agendamento de equipamentos, além de assinatura digital (*Sign and Witness*) para proteção de propriedade intelectual.
- **Gestão de Grupo:** permite ao PI acompanhar projetos, experimentos, estoque e orçamento de insumos em um só lugar, evitando compras duplicadas e perda de amostras.
- **Modelo de Preço / Freemium:** **não possui plano gratuito permanente** nem tabela pública; a contratação é baseada em cotação comercial (*quote-based*) por assento/ano e módulos contratados, com pacotes negociados para grupos acadêmicos/startups.
- **O que o LattesData aprende:** a barreira de entrada sem *self-serve* e o custo por assento travam a adoção orgânica na academia brasileira, onde alunos bolsistas giram rápido e o docente não tem verba contínua para pagar licenças por estudante.

### 2.3 Protocols.io
- **Categoria:** Repositório colaborativo de protocolos metodológicos reprodutíveis.
- **Proposta de Valor Central:** transformar métodos científicos em protocolos passo a passo executáveis, versionáveis e citáveis (com emissão gratuita de **DOI** sob licença *Creative Commons* quando publicados abertamente), combatendo a crise de reprodutibilidade.
- **Modelo de Preço / Freemium (Público vs. Privado):** adota um recorte elegante de monetização por **privacidade e escala de equipe**:
  - **Plano Gratuito (*Open Research*):** protocolos **públicos ilimitados** (com DOI) e leitura/execução gratuita; porém limitado a **2 protocolos privados ativos** e 100 MB de armazenamento.
  - **Planos Pagos / Licenças Institucionais:** ~US\$ 310–350/usuário/ano para workspaces individuais/pequenas equipes (protocolos privados ilimitados, 10 GB+, histórico completo e pastas de laboratório) ou licenças *campus-wide* financiadas por bibliotecas universitárias.
- **O que o LattesData aprende:** a mecânica de oferecer utilidade real no gratuito e cobrar por governança/escala funciona bem, mas o recorte do Protocols.io cobre apenas a etapa metodológica — sem gestão de entregas de alunos, compliance brasileiro ou prestação de contas.

### 2.4 Overleaf
- **Categoria:** Editor colaborativo de LaTeX em nuvem para escrita científica.
- **Proposta de Valor Central:** eliminar a dor de compilar LaTeX localmente e trocar arquivos `.tex` por e-mail, oferecendo edição simultânea em tempo real, comentários, controle de alterações e milhares de templates oficiais de periódicos e conferências.
- **Dinâmica Viral (Orientador ↔ Coautores):** é o caso clássico de viralidade na academia. Basta um orientador ou primeiro autor criar o manuscrito no Overleaf e enviar o link para 4 coautores; todos entram imediatamente no mesmo documento e passam a associar o fluxo de escrita à plataforma.
- **Modelo de Preço / Freemium:**
  - **Free (\$0):** projetos ilimitados, mas restrito a **1 colaborador editor por projeto** (visualizadores ilimitados), *timeout* de compilação de 10 segundos e histórico de 24h.
  - **Student (~US\$ 8,25/mês anual) e Standard (~US\$ 16,75/mês anual):** até **10 colaboradores por projeto**, histórico completo, integração Git/GitHub/Dropbox/Zotero/Mendeley e assistente de IA.
  - **Pro (~US\$ 33,25/mês anual):** **colaboradores ilimitados** por projeto.
  - **Overleaf Commons (Institucional):** universidades assinam para liberar recursos *premium* a docentes e discentes via login institucional.
- **O que o LattesData aprende:** o limite de colaboradores no plano gratuito do Overleaf mostra como a colaboração multi-autoral (mediana de 6 a 10 autores em áreas brasileiras) é um gatilho poderoso de conversão do líder do projeto. No LattesData, porém, o aluno convidado **nunca** deve ser bloqueado na colaboração dentro do projeto pago pelo orientador.

### 2.5 OSF — Open Science Framework
- **Categoria:** Infraestrutura aberta de gestão de ciclo de vida de pesquisa (mantida pela organização sem fins lucrativos *Center for Open Science — COS*).
- **Proposta de Valor Central:** estruturar **projetos-mãe** com subcomponentes hierárquicos, armazenar arquivos/datasets, conectar integrações (GitHub, Google Drive, Dropbox, OneDrive) e oferecer **pré-registro de estudos (*preregistration*)** com carimbo de tempo, opção de embargo de até 4 anos e emissão gratuita de **DOI (DataCite/Crossref)**.
- **Modelo de Preço / Sustentabilidade:**
  - **Gratuito para pesquisadores individuais:** contas, pré-registros e emissão de DOI sem custo, com armazenamento nativo de até **5 GB para projetos privados** e **50 GB para projetos públicos** (sem limite para armazenamento via *add-ons* externos).
  - **OSF for Institutions (Pago):** universidades e bibliotecas pagam assinatura anual para obter SSO institucional, vitrine agregada da produção aberta da instituição, painéis administrativos e registros customizados (*OSF Registries* a partir de ~US\$ 5.000/ano).
- **O que o LattesData aprende:** o conceito de **Projeto-Mãe / Projeto Guarda-Chuva** (essencial no Pack 7 de Humanas/Artes e no Pack 3 de Revisões Sistemáticas do LattesData) e a rastreabilidade de pré-registros são referências diretas. Contudo, a interface do OSF é árida para gestão semanal de orientandos e não se integra ao Lattes nem às agências brasileiras.

### 2.6 Researchfish
- **Categoria:** Plataforma de prestação de contas e rastreamento de impacto de financiamentos (*Grant Outcomes Reporting*), adquirida pela Elsevier.
- **Proposta de Valor Central:** conectar diretamente **processos de fomento (*grants*) ↔ produtos e impactos** (artigos, propriedade intelectual, colaborações, políticas públicas, engajamento social). É o padrão adotado por grandes financiadores como o **UKRI** (Reino Unido), onde coordenadores de projetos são contratualmente obrigados a reportar anualmente os resultados — inclusive por até **5 anos após o término do auxílio**, sob pena de sanções ou bloqueio de novos recursos.
- **Modelo de Preço e Status Estratégico:** vendido em contratos corporativos B2G/B2B para agências financiadoras e universidades (faixas contratuais de £50.000 a £1.000.000+ em editais públicos britânicos). **Fato crítico recente:** a Elsevier anunciou o **encerramento oficial do Researchfish para 31 de julho de 2027**, sinalizando a transição do mercado de formulários anuais burocráticos e isolados para ecossistemas integrados (CRIS/RIMS) que capturam evidências continuamente.
- **O que o LattesData aprende:** comprova a dor real e permanente da relação **N:N entre Fomentos e Produtos** (como visto na amostra empírica brasileira, onde um único artigo presta contas simultaneamente a FAPEMA, FINEP, CAPES e BNB). Ao mesmo tempo, o fim do Researchfish prova que pesquisadores odeiam preencher sistemas *exclusivamente* burocráticos uma vez por ano — o relato de fomento precisa nascer como **subproduto automático do trabalho semanal do projeto**.

### 2.7 Symplectic Elements e Elsevier Pure
- **Categoria:** *Research Information Management Systems* (RIMS) / *Current Research Information Systems* (CRIS) institucionais.
- **Proposta de Valor Central:** atuar como a "fonte única da verdade" da produção científica de uma universidade, cruzando perfis de docentes, publicações, financiamentos, patentes e impacto para alimentar portais públicos de especialistas, repositórios institucionais (DSpace) e avaliações nacionais (como o *REF* britânico).
- **Colheita de Metadados (*Metadata Harvesting*):** ambos operam robôs que colhem continuamente metadados de bases bibliográficas (Scopus, Web of Science, PubMed, arXiv, Crossref, DataCite, Dimensions) usando identificadores persistentes (**ORCID** e **ROR**). No *Symplectic Elements*, o foco é o fluxo *"claim and verify"* para o docente; no *Elsevier Pure*, a força está na integração nativa com Scopus e painéis analíticos da RELX/Elsevier.
- **Modelo de Preço:** software *Enterprise* sob cotação institucional (baseado em número de docentes/FTE, módulos contratados e custos altos de implementação e integração com sistemas de RH/ERP). Inacessível para laboratórios isolados ou docentes individuais.
- **O que o LattesData aprende:** a colheita automática de metadados (que o LattesData já executa via DOI/PDF/OpenAlex/Crossref) reduz drasticamente a digitação manual. Porém, RIMS institucionais são vendidos *top-down* para reitorias e não resolvem a gestão cotidiana do orientador nem o preenchimento direto da Plataforma Lattes/Sucupira.

---

## 3. Referências SaaS PLG (*Host Pays, Guests Collaborate Free*)

Para desenhar a mecânica de aquisição viral e monetização do LattesData sem criar atrito para estudantes bolsistas, analisamos 4 líderes globais de *Product-Led Growth* (PLG). Todos compartilham uma regra de ouro: **a colaboração convidada é gratuita e sem fricção; a monetização acontece quando o convidado precisa de autonomia, escala ou valor individual fora do espaço do anfitrião (o "PLG Flip")**.

### 3.1 Figma — *Permissões Granulares e Assento por Papel*
- **Mecanismo de Aquisição sem Fricção:** um designer (anfitrião) envia um link de arquivo para PMs, engenheiros e clientes. **Visualizadores e comentaristas são 100% gratuitos e ilimitados** em todos os planos. O link abre direto no navegador, sem exigir instalação ou cartão de crédito.
- **Arquitetura de Preço:** plano *Starter* gratuito (limitado a 3 arquivos Design/FigJam/Slides) e assentos pagos segmentados por papel (*Full Seat* a US\$ 16/mês no Pro, *Dev Mode* e *Collab*).
- **Momento do "PLG Flip":** ocorre quando um convidado acostumado a apenas comentar ou inspecionar precisa **criar ou editar seus próprios arquivos** em um projeto próprio — cruzando a fronteira de *Viewer* gratuito para *Full Seat* pagante.
- **Tradução no LattesData:** o aluno entra pelo link do orientador com fricção zero para enviar entregas e comentar marcos. O *flip* acontece quando ele quer levar aquele patrimônio validado para a **própria carreira** (sincronizar o próprio Lattes ou gerar seu Dossiê de Edital).

### 3.2 Miro — *Canvas Viral e Teto de Propriedade*
- **Mecanismo de Aquisição sem Fricção:** um facilitador compartilha um quadro visual e coloca toda a equipe colaborando em minutos (inclusive via visitantes em links públicos ou *guests* nos planos corporativos *Business* a US\$ 20/mês).
- **Arquitetura de Preço:** plano gratuito com membros ilimitados, mas restrito a **apenas 3 quadros editáveis** (os mais antigos ficam somente leitura).
- **Momento do "PLG Flip":** o grupo adota o hábito colaborativo rapidamente e, ao criar o 4º quadro ou precisar de espaços privados com convidados externos sem pagar assento por eles, o líder converte para *Starter* (US\$ 8/mês) ou *Business* (US\$ 20/mês).
- **Tradução no LattesData:** o orientador pode testar a dinâmica com 1 projeto inicial; assim que enxerga a economia de tempo de gerir vários orientandos e múltiplos editais com Packs especializados, o *Plano Pesquisador Pro* se paga na primeira semana.

### 3.3 Notion — *Separação Estrita entre Membro Pagante e Convidado Gratuito*
- **Mecanismo de Aquisição sem Fricção:** diferencia claramente **Members** (construtores internos que pagam assento) de **Guests** (colaboradores externos convidados para páginas específicas, que editam e comentam gratuitamente).
- **Arquitetura de Preço:** gratuito para uso solo (com teto de **10 convidados no workspace** e upload de 5 MB); nos planos pagos (*Plus* a US\$ 10/mês e *Business* a US\$ 20/mês), o limite de convidados cai e poucos pagantes gerenciam dezenas de convidados externos gratuitamente.
- **Momento do "PLG Flip":** dois gatilhos distintos — (1) o anfitrião ultrapassa o limite de convidados/upload e assina o plano pago; (2) o convidado externo experimenta a fluidez da ferramenta no projeto do cliente e cria seu próprio workspace pessoal.
- **Tradução no LattesData:** o orientador é o *Member* pagante; todos os seus orientandos de IC, Mestrado e Doutorado são *Guests* 100% gratuitos dentro dos projetos do orientador — garantindo adesão imediata de 100% do laboratório.

### 3.4 Loom — *Assimetria Criador vs. Consumidor*
- **Mecanismo de Aquisição sem Fricção:** quem grava paga (*Creator-based pricing*); **quem assiste, comenta com marcação de tempo e reage é 100% gratuito e ilimitado**. Cada vídeo compartilhado funciona como um outdoor interativo do produto.
- **Arquitetura de Preço:** plano gratuito limitado a **25 vídeos** de até **5 minutos** por pessoa; ao atingir o limite de utilidade real, o criador faz upgrade.
- **Momento do "PLG Flip":** o destinatário que assistiu dezenas de vídeos de colegas decide gravar sua primeira explicação própria e, ao ultrapassar o teto gratuito, converte-se em criador pagante.
- **Tradução no LattesData:** a assimetria é **Orientador (Orquestrador/Aprovador) vs. Orientando (Colaborador no Projeto)**. O *PLG Flip* do aluno ocorre no momento de maior valor percebido: quando seu **Cofre Pessoal** já acumula 8, 12 ou 20 produções validadas pelo orientador e basta 1 clique (via Plano Estudante ou **Passe de Atualização / Passe de Edital via Pix**) para injetar tudo no Currículo Lattes ou montar o dossiê numerado de seleção.

### Síntese Comparativa dos Mecanismos PLG

| Referência PLG | Quem Paga (Host) | Quem Usa Grátis (Guest) | Gatilho Exato do "PLG Flip" | Aplicação Direta no LattesData |
| :--- | :--- | :--- | :--- | :--- |
| **Figma** | Designer / Editor (*Full Seat*) | Visualizadores e comentaristas ilimitados | Convidado precisa editar/criar arquivos próprios | Aluno colabora grátis no projeto; paga ao sincronizar o **próprio** Lattes |
| **Miro** | Líder / Empresa (*Starter/Business*) | Visitantes / *Guests* em planos pagos | Estouro de quadros ativos ou necessidade de gestão privada | Orientador assina Pro para projetos ilimitados, Packs e Dossiê de Prestação de Contas |
| **Notion** | Membros construtores do workspace | *Guests* convidados por página (ilimitados no pago) | Teto de convidados/upload ou criação de workspace próprio | 1 Orientador pagante convida toda a equipe (IC/M/D/PD) sem pagar por assento de aluno |
| **Loom** | Criador de vídeos ilimitados | Espectadores e comentaristas ilimitados | Exceder 25 vídeos / 5 min ao virar criador | Aluno vê o **Cofre Pronto** cheio de entregas aprovadas e destrava via Pix / Plano Estudante |

---

## 4. Matriz Comparativa: Plataformas Globais vs. LattesData

| Dimensão | Benchling | Labguru | Protocols.io | Overleaf | OSF | Researchfish* | Symplectic / Pure | **LattesData** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gestão de Projeto Científico Multi-Áreas** | Parcial *(foco Bio/Wet Lab)* | Parcial *(foco Bio/Quím.)* | Baixa *(só métodos)* | Baixa *(só manuscrito)* | **Alta** *(projetos-mãe)* | Baixa *(só relato pós-fato)* | Parcial *(visão institucional)* | **Completa** *(Espinha Dorsal + 8 Packs CNPq)* |
| **Colaboração Orientador ↔ Aluno** | Boa *(caderno de bancada)* | Boa *(tarefas/estoque)* | Parcial *(protocolos)* | **Alta** *(coautoria de texto)* | Média *(repositório)* | Nula *(foco no PI)* | Nula *(foco no docente)* | **Nativa** *(marcos, entregas, aprovação 1-clique e 1→N)* |
| **Compliance Brasileiro (`CEP`, `CEUA`, `SisGen`, `INPI`, `MAPA`)** | Não | Não | Não | Não | Não | Não | Não | **Nativo por Pack** *(alertas, validades, Dispensa 510, Gate INPI)* |
| **Prestação de Contas (`FAPs`, `CNPq`, `CAPES`, `Sucupira`)** | Não | Não | Não | Não | Não | Não *(foco UKRI/Europa)* | Parcial *(foco REF/Scopus)* | **Nativa** *(Carteira Fomentos N:N + Dossiê + aderência Sucupira)* |
| **Preenchimento do Currículo Lattes** | Não | Não | Não | Não | Não | Não | Não | **Nativo** *(propagação 1→N + extensão automatizada + EditalScore)* |
| **Modelo de Preço / Acesso** | Free Acadêmico *(ELN)* / Enterprise US\$ | Pago sob cotação *(US\$)* | Free *(2 priv.)* / ~US\$ 310+/ano | Free *(1 colab.)* / US\$ 8–33/mês | Free indiv. / Pago instit. | Enterprise B2G/Univ. *(£50k+)* | Enterprise Univ. *(US\$ alto)* | **Host Pays (R\$)** · Aluno Grátis no Projeto · **Pix avulso / Estudante** |

*\*Nota: Researchfish tem encerramento programado pela Elsevier para julho de 2027.*

---

## 5. A Lacuna Única do Brasil e o Posicionamento do LattesData

### Por que as ferramentas globais não resolvem o ecossistema brasileiro?

Mesmo que um laboratório brasileiro tivesse orçamento ilimitado em dólar para assinar Benchling, Overleaf Pro, Protocols.io e Elsevier Pure simultaneamente, **quatro realidades exclusivas do Brasil continuariam sem solução**:

1. **A Centralidade Absoluta da Plataforma Lattes e da Avaliação CAPES/Sucupira:** fora do Brasil, o perfil do pesquisador é descentralizado (ORCID, Google Scholar, CV em PDF). No Brasil, o **Currículo Lattes** é infraestrutura obrigatória para bolsas, editais, progressão funcional, concursos públicos e avaliação quadrienal dos PPGs na **Plataforma Sucupira**. Nenhuma plataforma estrangeira conhece a taxonomia do CNPq (`itens/especificacao/*.json`), a classificação de Produtos Técnico-Tecnológicos (**PTTs T1–T3**), o agrupamento de versões bilíngues ou o risco de divergência entre coautores que quebra o cruzamento na Sucupira.
2. **Arquitetura Regulatória Nacional Própria:** a pesquisa brasileira opera sob um conjunto único de marcos legais e portais — **Plataforma Brasil (`CEP/CONEP — CAAE`)**, **Resolução CNS 510/2016** (dispensa/consentimento em Humanas e bases públicas como `DATASUS`/`SINAN`), **`CEUA`**, **`SisGen`** (patrimônio genético e conhecimento tradicional), **`SISBIO/ICMBio`**, **`INPI`** (patentes e registro de software), **`MAPA`** (`RNC`/`SNPC`/`VCU`) e contratos **`EMBRAPII`/`ANP`/`ANEEL`**. Ferramentas gringas ignoram completamente esses requisitos.
3. **Financiamento Pulverizado em Múltiplas Agências Nacionais (Relação N:N):** um grupo brasileiro típico combina simultaneamente bolsas e auxílios de **CNPq**, **CAPES**, **FAPs estaduais** (`FAPESP`, `FAPEMA`, `FAPERJ`, `FAPEMIG`, etc.), **FINEP** e bancos regionais (`BNB`). Um único artigo frequentemente precisa prestar contas a 3 ou 4 processos distintos, exigindo guarda permanente dos PDFs comprobatórios e geração ágil de textos de *Funding/Acknowledgements*.
4. **Economia Acadêmica em Reais e Alta Sensibilidade a Assinaturas em Dólar:** cobrar US\$ 20 a US\$ 35/mês por assento (incluindo alunos bolsistas de IC ou Mestrado) inviabiliza a adoção em massa no Brasil. A realidade local exige precificação em reais, isenção total para o aluno colaborador e opções flexíveis sem cartão de crédito internacional — como o **Pix**.

### O Posicionamento Estratégico do LattesData

O LattesData não compete com o Benchling na edição de plasmídeos nem com o Overleaf na compilação de LaTeX. Ele ocupa a **camada de orquestração que falta no Brasil** — conectando a **gestão semanal do projeto** diretamente à **conformidade brasileira**, à **prestação de contas de fomentos** e ao **preenchimento automático do Currículo Lattes**.

Esse posicionamento se fecha em um motor econômico de três tempos, perfeitamente adaptado à realidade acadêmica brasileira:

```
┌─────────────────────────────────────────────────────────────────────────┐
│             MOTOR PLG BRASILEIRO DO LATTESDATA (HUB-AND-SPOKE)          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ORIENTADOR PAGANTE (Plano Pesquisador Pro — R$/mês ou anual)        │
│     • Cria projetos com Espinha Dorsal + Packs de Especialidade         │
│     • Preserva evidências (fim do Lab Turnover) e compliance BR         │
│     • Gera Dossiê de Prestação de Contas (FAPs/CNPq/CAPES) e sincroniza │
│       o próprio Lattes com 1 clique                                     │
│                                  │                                      │
│                    Convite sem fricção (Link Gratuito)                  │
│                                  ▼                                      │
│  2. ALUNO GRATUITO NO PROJETO (IC · Mestrado · Doutorado · Pós-Doc)     │
│     • Barreira zero: interage, envia PDFs/certificados/DOIs e confirma  │
│       ORCID + Matriz CRediT sem pagar nada                              │
│     • Aprovações do orientador alimentam automaticamente seu Cofre      │
│       Pessoal (propagação 1 → N, eliminando redigitação no grupo)       │
│                                  │                                      │
│                Momento do "PLG Flip" (Valor Acumulado Visível)          │
│                                  ▼                                      │
│  3. CONVERSÃO INDIVIDUAL DO ALUNO (Plano Estudante ou Passe via Pix)    │
│     • Com 8, 12 ou 20 produções já estruturadas e validadas no Cofre,   │
│       o aluno paga no momento exato da necessidade (seleção, bolsa,     │
│       concurso ou atualização semestral) via Pix avulso (Passe de       │
│       Atualização / Passe de Edital + EditalScore) ou assinatura leve   │
│                                                                         │
│  ► EXPANSÃO NATURAL B2B: 3+ docentes do mesmo programa usando juntos    │
│    geram pull orgânico para o Plano Institucional / PPG (Sucupira).     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Síntese Executiva

- **Por que o orientador paga:** economiza horas semanais, blinda seu grupo contra perda de documentos na formatura dos alunos, mantém compliance brasileiro em dia (`CEP`/`CEUA`/`SisGen`/`INPI`) e tem prestação de contas e Lattes sempre prontos.
- **Por que o aluno adota sem resistência:** entrar no projeto do orientador é **100% gratuito** e substitui a bagunça de PDFs perdidos no WhatsApp/e-mail.
- **Por que o aluno converte com altíssima eficiência:** ele não compra uma promessa vazia — ele destrava, via **Pix** ou **Plano Estudante**, um **Cofre Pessoal** que já contém suas produções reais, validadas pelo orientador e prontas para entrar no CNPq ou compor o dossiê numerado de um edital.
