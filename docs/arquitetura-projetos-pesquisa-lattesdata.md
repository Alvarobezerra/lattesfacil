# Arquitetura e Ambiente de Gestão de Projetos de Pesquisa — LattesData

> **Propósito deste documento:** consolidar a fundamentação empírica (13 pesquisadores brasileiros nas 8 Grandes Áreas do CNPq + levantamento de artigos Qualis A1/A2), definir a **Espinha Dorsal Universal** e os **8 Packs Modulares por Especialidade**, formalizar o modelo **Orientador Pagante ↔ Aluno Convidado Gratuito**, e construir de forma explicativa o **ambiente de produto** antes da prototipação de interface.

---

## 1. A Virada de Jogo: Do Registro Episódico para o Ambiente Vivo da Pesquisa

Na academia brasileira, a manutenção do Currículo Lattes costuma ser **episódica e reativa**: o pesquisador só abre o currículo sob pressão de um edital, relatório CAPES/Sucupira, progressão funcional ou processo seletivo.

Em contraste, **um projeto de pesquisa com orientandos acontece toda semana**.

Ao incorporar a **Gestão Colaborativa de Projetos de Pesquisa Científica**, o LattesData realiza três movimentos estratégicos simultâneos:

1. **Frequência semanal (hábito real):** o sistema deixa de ser visitado 2 vezes por ano e passa a ser o espaço de trabalho entre orientador, coorientadores, laboratórios parceiros e orientandos (IC, Mestrado, Doutorado, Pós-Doc).
2. **Eliminação do retrabalho coletivo (1 entrega → N currículos):** hoje, quando um grupo publica 1 artigo ou 1 resumo em anais com 8 autores, 8 pessoas digitam a mesma obra separadamente no Lattes (frequentemente com divergências que quebram o cruzamento na Plataforma Sucupira). No LattesData, a evidência entra **uma única vez** no projeto e fica pronta para todos os participantes.
3. **Fim do "Problema da Formatura" (*Lab Turnover*):** quando o aluno defende e deixa o laboratório, os PDFs dos artigos, certificados de congressos, protocolos regulatórios (`CEUA`, `CEP`, `SisGen`), dados e relatórios parciais **permanecem preservados e organizados no projeto do orientador** para prestação de contas de editais e avaliação quadrienal.

---

## 2. Fundamentação Empírica: 13 Pesquisadores Brasileiros e Periódicos Qualis A1/A2

Para não projetar um "gerenciador de tarefas genérico" (tipo Trello) que pesquisadores abandonam em duas semanas, fizemos engenharia reversa em duas camadas:
- **Camada A (Perfis Reais — OpenAlex/Crossref/Europe PMC):** análise de **1.150+ obras recentes** de **13 pesquisadores brasileiros** em todas as 8 Grandes Áreas do CNPq (incluindo 5 docentes do PPGST/UFMA com rede interna real).
- **Camada B (Fluxos Qualis A1/A2):** mapeamento das exigências reais de execução, compliance, artefatos e revisão em periódicos e conferências de topo (*Nature Communications*, *Science Advances*, *The Lancet*, *BMJ*, *Journal of Ethnopharmacology*, *Cadernos de Saúde Pública*, *REBEn*, *NeurIPS*, *ICML*, *IEEE Transactions*, *Chemical Engineering Journal*, *Ceramics International*, *The Astrophysical Journal*, *Physical Review Letters*, *ACS Omega*, *Field Crops Research*, *Food Chemistry*, *PAB*, *Science of the Total Environment*, *Dados*, *RBH*, *Educação & Sociedade*, *Psicologia: Reflexão e Crítica*, *Journal of Development Economics*, *Revista Direito GV*, *RAE*, *DELTA*, *ARS*).

### 2.1 Retrato Empírico Comparado

| Grande Área / Foco | Pesquisadores Analisados | Mediana de Autores | Multi-inst. | Produtos e Padrões Dominantes |
| :--- | :--- | :---: | :---: | :--- |
| **Saúde / Biotecnologia** | Aramys Reis · Richard Dutra · Márcia Maciel *(UFMA)* | **7 a 10** | 42%–64% | Artigos, patentes, bioprodutos, `CEUA`/`SisGen`, múltiplos fomentos simultâneos (`FAPEMA`/`CNPq`/`CAPES`/`FINEP`/`BNB`) |
| **Enfermagem / Saúde Coletiva** | Adriana Ferreira · Marcelino Santos Neto *(UFMA)* | **6 a 8** | 38%–45% | Artigos (muitas vezes bilíngues/trilíngues com múltiplos DOIs), protocolos de revisão (`PROSPERO`/`OSF`), PTTs, `CEP`/`Dispensa 510` |
| **Computação / IA** | André Ponce de Leon de Carvalho *(USP/ICMC)* | **6** *(máx. 96)* | **77%** | **Anais de conferência (41%)** superam periódicos (37%), preprints (`arXiv`), código GitHub/Docker, *Rebuttal* e *Artifact Evaluation* |
| **Engenharias (Química/Elétrica/Materiais/Prod.)** | José Carlos Pinto *(COPPE/UFRJ)* + casos *IEEE/CEJ/Ceramics* | **6** *(máx. 17)* | **67%** | Artigos, protótipos/HIL/*scale-up*, **TRL 4–6**, contratos **EMBRAPII/ANP/ANEEL**, **NDA/embargo** até depósito no INPI |
| **Agrárias / Alimentos / Ambientais** | Mariangela Hungria *(Embrapa Soja)* + *FCR/Food Chem./PAB* | **6** *(máx. 60)* | **91%** | Artigos, **datasets plurianuais (6%)**, ciclos multi-safra (DBCA), **MAPA (RNC/SNPC/VCU)**, **ICMBio/SISBIO**, **CEP para sensorial** |
| **Humanas / Psicologia** | Sílvia Helena Koller *(UFRGS)* + *Psicol. R&C* | **4** *(máx. 49)* | **72%** | Artigos (68%), **livros e capítulos (22%)**, datasets (5%), pré-registro (`OSF`), pesquisa comunitária |
| **Sociais Aplicadas (Economia/Direito/Adm.)** | Naércio Menezes-Filho *(Insper/USP)* + *JDE/Direito GV/RAE* | **2** *(máx. 25)* | 35% | **Working Papers (SSRN/NBER)**, microdados (`RAIS`/`PNAD`), *AEA RCT Registry*, *Policy Briefs*, pareceres, casos de ensino |
| **Humanas (História/Sociologia/Educação)** | Lília Moritz Schwarcz *(USP)* + *RBH/Dados/Ed.&Soc.* | **1** *(máx. 6)* | 14% | **Livros e capítulos (46%)**, arquivos/etnografia, **Res. CNS 510/2016**, *Editoria de Replicabilidade* (*Dados*), pesquisa-ação |
| **Linguística, Letras e Artes** | Lucia Santaella *(PUC-SP)* + *DELTA/TLA/ARS* | **1** *(máx. 14)* | 18% | Artigos/ensaios, capítulos internacionais, *corpora* digitais, traduções comentadas, **exposições/curadorias**, direitos autorais de imagem |
| **Física / Astrofísica / Química** | Thaisa Storchi-Bergmann *(UFRGS)* + *ApJ/PRL/ACS Omega* | **10** *(média 17)* | **91%** | Grandes consórcios (revisão interna prévia), tempo de telescópio/síncrotron (`Sirius`), `arXiv`, **Datasets Zenodo (DOI)**, *Supporting Information* |

### 2.2 As 5 Descobertas Estruturais que Moldam o Sistema

1. **O papel do pesquisador varia por projeto:** na amostra do Prof. Aramys (58 obras), ele é último autor em 7, primeiro em 4 e **colaborador intermediário em 47**. O sistema não deve fixar um papel global rígido; o mesmo docente é **Coordenador/Orientador** em seus projetos e **Pesquisador Parceiro** em projetos de colegas.
2. **A colaboração é simultaneamente vertical (Orientador → Alunos) e horizontal (Docente ↔ Docente do mesmo PPG):** os 5 docentes do PPGST/UFMA compartilham vários artigos entre si. A plataforma cresce tanto por orientandos quanto por colegas de programa (abrindo caminho para o **Plano de PPG / Institucional**).
3. **Um único artigo presta contas para múltiplas agências e bolsas (relação N:N):** no artigo real *Foods* (2026) do grupo do Prof. Aramys, uma única publicação cita 4 agências simultâneas (`FAPEMA BM`, `BEPP`, `INFRA`, `APP` + `FINEP` + `CAPES 001 / Pró-Equipamentos` + `FUNDECI/BNB`).
4. **Autoria individual em Humanas/Artes não inviabiliza o modelo colaborativo:** nessas áreas, o orientador conduz **Projetos Guarda-Chuva** e **Coletâneas Organizadas** com 5 a 15 orientandos (cada aluno publica sua dissertação/artigo/capítulo com 1 ou 2 autores, mas todos interagem no mesmo espaço de projeto).
5. **Conformidade regulatória e reprodutibilidade acontecem ANTES da publicação:** periódicos Qualis A1/A2 rejeitam manuscritos sem comprovação prévia (`CAAE`, `CEUA`, `SisGen`, `SISBIO`, `ReBEC`, `PROSPERO`, `Reproducibility Checklist`, `NDA/INPI`). O sistema precisa guardar isso **desde o início do projeto**, não apenas na hora de preencher o Lattes.

---

## 3. A Espinha Dorsal Universal (Os 6 Pilares Fixos)

Todo projeto no LattesData — seja de História, Computação, Agronomia ou Biotecnologia — nasce sobre os mesmos **6 blocos universais**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ESPINHA DORSAL DO PROJETO LATTESDATA                 │
├──────────────────────────┬──────────────────────┬───────────────────────┤
│ 1. IDENTIDADE & NATUREZA │ 2. EQUIPE & PAPÉIS   │ 3. CARTEIRA FOMENTOS  │
│ Pesquisa · Extensão      │ Coordenador/Orient.  │ Editais e Bolsas N:N  │
│ Ensino · Desenv. Tecnol. │ Parceiro Externo     │ Texto Funding pronto  │
│ Vigência e Resumo        │ Orientandos (Grátis) │ Prestação de Contas   │
├──────────────────────────┼──────────────────────┼───────────────────────┤
│ 4. MARCOS & ENTREGAS     │ 5. PRODUTOS & VERSÕES│ 6. MOTOR LATTES/DOSSIÊ│
│ Plano → Execução → Defesa│ Artigo · Conf. · PTT │ Fila do Orientador ✓  │
│ Repositório de PDFs e    │ Livro · Dataset · PI │ Cofre do Aluno (Conv.)│
│ Certificados dos Alunos  │ CRediT · PT/EN/ES    │ Relatório Sucupira    │
└──────────────────────────┴──────────────────────┴───────────────────────┘
```

1. **Identidade & Natureza:** título, objetivo, vigência, grande área e natureza alinhada ao CNPq (*Pesquisa*, *Extensão*, *Ensino* ou *Desenvolvimento Tecnológico*).
2. **Equipe & Papéis por Projeto:** gestão de membros com papéis distintos (*Coordenador*, *Orientador*, *Coorientador*, *Pesquisador Parceiro Multi-institucional*, *Orientando Convidado — IC/Mestrado/Doutorado/Pós-Doc*).
3. **Carteira de Fomentos & Bolsas (N:N):** cadastro único de editais, auxílios e bolsas (`CNPq`, `CAPES`, `FAPs`, `FINEP`, `EMBRAPII`, `BNB`), vinculáveis a múltiplos projetos e produtos. Gera automaticamente o parágrafo de *Funding/Acknowledgements* e o relatório por processo.
4. **Marcos de Execução & Repositório de Evidências:** linha do tempo de entregas dos alunos (plano, qualificação, coleta, resultados parciais, congressos, defesa) com guarda permanente dos PDFs e certificados comprobatórios.
5. **Gestor de Produtos, Autoria e Versões:** suporta todos os tipos de saída científica, técnica, educacional e artística, com **Matriz CRediT + ORCID**, trilha **Preprint / Working Paper → Publicação Final** e **Agrupador Multilíngue (PT/EN/ES)** para evitar duplicidades no Lattes.
6. **Motor de Propagação para Carreira & Prestação de Contas:** toda entrega validada pelo orientador já nasce estruturada segundo as especificações do Lattes (`itens/especificacao/*.json`) para sincronização imediata do orientador e fila pronta para cada aluno/coautor.

---

## 4. Os 8 Packs Modulares de Dinâmicas por Especialidade

Para manter a interface limpa e respeitar a cultura de cada área, ao criar um projeto o docente ativa **1 ou mais Packs de Especialidade** (como módulos plugáveis sobre a Espinha Dorsal):

| Pack | Áreas-Alvo | Dinâmicas, Campos e Alertas Ativados |
| :--- | :--- | :--- |
| **Pack 1 — Bancada, Biológicas & Farmácia** | Biológicas, Farmácia, Biotecnologia, Imunologia | Cofre regulatório (`CEUA`, `SisGen`, `SISBIO`, `CTNBio/CIBio`); número de exsicata/*voucher* em herbário/coleção; checklist `ARRIVE`; **Gate de Patente (INPI/NIT)** antes de submeter artigo. |
| **Pack 2 — Ensaios Clínicos & Intervenções** | Medicina, Odontologia, Fisioterapia, Enfermagem Clínica | Dupla via regulatória (`CEP/CONEP — CAAE` + `ANVISA`); registro prospectivo obrigatório (`ReBEC` / `ClinicalTrials.gov`); protocolos `SPIRIT` / `CONSORT`; controle de centros, `eCRF/REDCap`, `SAP` e `DSMB`. |
| **Pack 3 — Saúde Coletiva, Revisões & PTT** | Saúde Coletiva, Enfermagem, Educação em Saúde | Opção de **Dispensa de CEP (Res. CNS 510/2016)** para bases públicas (`SINAN`, `SIM`, `DATASUS`, `IBGE`); registro prospectivo de revisão (`PROSPERO` / `OSF` + `PRISMA 2020`/`PRISMA-ScR` + triagem pareada); `STROBE`/`COREQ`; fluxo de **Validação com Juízes (IVC)** e comprovação de impacto de **PTTs (T1–T3 CAPES)**. |
| **Pack 4 — Computação, IA & Ciência de Dados** | Ciência da Computação, IA, Eng. Software, Estatística | **Ciclo de Conferência A1** (*Submission → Reproducibility Checklist → Rebuttal → Artifact Evaluation → Camera-Ready*); vínculo nativo com **GitHub/GitLab**, ambiente (`Docker`), **Hugging Face / Zenodo** e `arXiv`; **Registro de Software (INPI)**. |
| **Pack 5 — Engenharias, Indústria & TRL** | Eng. Química, Elétrica, Materiais, Mecânica, Produção | Contratos **EMBRAPII / ANP / ANEEL**; controle de **NDA / Sigilo Industrial**, **embargo de publicação** e defesa sigilosa até depósito de patente no INPI; marcador de maturidade **TRL (1–9)**; protótipos/HIL/*scale-up*; propostas de tempo de feixe (**Sirius/LNLS**). |
| **Pack 6 — Agrárias, Alimentos & Ambientais** | Agronomia, Zootecnia, Alimentos, Ciências Ambientais | **Calendário Multi-Safra / Multi-Local** (delineamento DBCA/DIC, estações experimentais/Embrapa); **MAPA (`RNC`, `SNPC`, `VCU/DHE`)** para cultivares e bioinsumos; `ICMBio/SISBIO`; **alerta de CEP para análise sensorial de alimentos com humanos** (com garantia microbiológica prévia); **URTs, Boletins Técnicos e Dias de Campo**. |
| **Pack 7 — Humanas, Sociais Aplicadas & Artes** | História, Sociologia, Educação, Psicologia, Economia, Direito, Adm., Letras, Artes | Modo **Projeto Guarda-Chuva** (autoria individual/dupla dos alunos sob o mesmo projeto); **Res. CNS 510/2016** (consentimento flexível + termo de assentimento escolar + anonimização indireta); **Gestor de Livro / Coletânea** (com alerta contra endogenia CAPES); **Working Papers (`SSRN`/`NBER`) + `AEA RCT Registry` / `SciELO Data`**; **Direitos Autorais de Imagem/Acervos/Traduções**; saídas para *Policy Briefs*, pareceres, casos de ensino, *corpora* e exposições/curadorias. |
| **Pack 8 — Big Science, Química & Consórcios** | Física, Astrofísica, Química Estrutural, Redes Globais | Etapa de **Revisão Interna do Consórcio** antes da revista; tempo de telescópio/observatório (*proprietary period*); `arXiv` + **Datasets com DOI (`Zenodo/CERN`)**; pacote de **Supporting Information (SI)** (espectros RMN/HRMS, coordenadas DFT, arquivos CIF) e centrais analíticas multiusuário. |

---

## 5. Modelo de Negócio, Dinâmica Viral e Conversão (*Hub-and-Spoke*)

Inspirado nos modelos de maior eficiência de aquisição em ciência e SaaS (**Benchling**, **Overleaf**, **Figma**, **Miro** e **Notion**), o LattesData opera no modelo ***Host Pays, Guests Collaborate Free***:

### 5.1 Os Três Perfis Econômicos

| Perfil | Modelo de Acesso | O que usa | Por que adota / paga |
| :--- | :--- | :--- | :--- |
| **Orientador / Líder de Projeto** *(Plano Pesquisador Pro)* | **Pagante (assinatura mensal/anual)** | Cria projetos ilimitados, ativa Packs, convida orientandos e parceiros, aprova entregas, sincroniza 1-clique no próprio Lattes e exporta Dossiê de Prestação de Contas / Sucupira. | Economiza horas por semana, nunca mais perde comprovantes de ex-alunos, elimina retrabalho de digitação e tem relatórios de fomento prontos. |
| **Aluno / Orientando** *(IC, Mestrado, Doutorado)* | **100% Gratuito dentro dos projetos convidados** | Interage com o orientador, envia relatórios/certificados/rascunhos, acompanha marcos e visualiza sua **Trajetória Viva** sendo montada automaticamente. | Usa porque é o ambiente oficial do projeto com seu orientador — zero barreira de entrada. |
| **Aluno / Pesquisador no Momento Pessoal** *(Conversão Individual)* | **Plano Estudante acessível OU Passe de Atualização / Passe de Edital (Pix avulso)** | Destrava: (1) **Sincronizar suas entregas do projeto no próprio Lattes com 1 clique**, (2) subir comprovantes pessoais fora do projeto, (3) **Valorização & Conformidade** completa, (4) **EditalScore + Dossiê PDF numerado** para seleção/concurso/bolsa. | Paga no momento exato em que já enxerga *8, 12 ou 20 produções prontas e validadas* esperando apenas 1 clique para entrar no CNPq. |

### 5.2 Expansão Natural para Programas de Pós-Graduação (PPG)
Como comprovado na rede do PPGST/UFMA (onde 5 docentes coautoram entre si), quando 3 ou mais docentes do mesmo programa usam o LattesData, surge a demanda natural pelo **Plano Institucional / PPG**: consolidação automática das produções discentes/docentes, vínculos Projeto ↔ Orientação ↔ Produção e checagem de aderência para a **Plataforma Sucupira (CAPES)**.

---

## 6. Construção Explicativa do Ambiente (Guia Conceitual das Telas)

Esta seção descreve **como o ambiente funciona na prática**, tela por tela, antes da etapa de prototipação visual e implementação de código.

### 6.1 Tela 1 — Central "Meus Projetos & Grupos"
É a porta de entrada da camada de projetos dentro do LattesData, separando com clareza os papéis que o usuário exerce:
- **Aba "Projetos que Coordeno / Oriento":** cards dos projetos sob liderança do docente, exibindo vigência, agências vinculadas, quantidade de orientandos ativos, pendências de aprovação e saúde regulatória (ex.: *"SisGen OK · CEUA vence em 45 dias"*).
- **Aba "Projetos em que Colaboro":** projetos de colegas ou redes multi-institucionais onde o usuário atua como pesquisador parceiro (ou, no caso do estudante, os projetos em que foi convidado gratuitamente pelo orientador).
- **Ação rápida de entrada ("Importar Projetos do meu Lattes"):** lê os projetos e orientações já existentes no XML/PDF do currículo para criar os workspaces sem obrigar o orientador a redigitar tudo do zero.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MEUS PROJETOS & GRUPOS                   [ + Novo Projeto ] [ Importar ]│
│ (●) Coordeno / Oriento (4)     ( ) Colaboro como Parceiro (7)           │
├────────────────────────────────────┬────────────────────────────────────┤
│ 🧪 Bioprospecção do Babaçu (LaFIT) │ 📱 mHealth & Educação em Saúde     │
│ Pesquisa · 2024–2027 · FAPEMA/FINEP│ Desenv. Tecnol. · 2025–2027 · CNPq │
│ Packs: [Bancada/Farmácia]          │ Packs: [Saúde Coletiva/PTT]        │
│ Equipe: 1 orient. · 2 parc. · 6 al.│ Equipe: 2 doc. · 4 alunos          │
│ ✓ SisGen OK · ⚠ 3 entregas p/ aprovar│ ✓ CAAE OK · ✓ Prot. OSF ativo     │
│               [ Abrir Projeto → ]  │               [ Abrir Projeto → ]  │
└────────────────────────────────────┴────────────────────────────────────┘
```

### 6.2 Tela 2 — Espaço do Projeto (Visão do Orientador)
Ao abrir um projeto, o orientador encontra um ambiente limpo com a **Espinha Dorsal** no topo e apenas os **Packs ativados** nas abas internas:

1. **Visão Geral & Marcos:** linha do tempo das etapas do projeto, orientandos vinculados (cada um com seu plano de trabalho/dissertação) e caixa **"Aguardando sua Aprovação"** (comprovantes e produções enviados pelos alunos).
2. **Equipe & Convites:** lista de docentes parceiros e orientandos com botão **"Copiar Link de Convite Gratuito para Orientando"** (indicando claramente: *seu aluno entra de graça para interagir no projeto*).
3. **Carteira de Fomentos:** processos vinculados (ex.: `FAPEMA APP-01415/25`, `BM-02164/23`, `FINEP 2362/24`, `CAPES 001`) com botão **"Copiar texto de Agradecimentos/Funding"** (em PT e EN) e contador de produtos vinculados a cada processo.
4. **Conformidade & Packs (Dinâmico):** exibe apenas os cartões dos packs ativados.
   - *Cenário A — Projeto Babaçu / LaFIT (Pack 1 ativo):* cartões de `SisGen`, `CEUA`, parceria com Cooperativa de Quebradeiras de Coco e **Gate de Patente (INPI)** antes da submissão do artigo.
   - *Cenário B — Projeto Revisão de Escopo & Cartilha/App (Pack 3 ativo):* cartões de `CEP/CAAE` (ou `Dispensa 510/2016`), registro de protocolo `OSF/PROSPERO`, checklist `PRISMA-ScR`, validação por juízes (`IVC`) e ficha de **PTT para a CAPES**.
5. **Produtos & Manuscritos:** lista de artigos, resumos em anais, patentes, PTTs e defesas nascidos do projeto. Cada produto tem sua **Matriz de Autoria (CRediT + ORCID)**, status (*Rascunho → Em Revisão → Aceito → Publicado*), vínculo com Preprint/Versão Bilíngue e status de sincronização com o Lattes.
6. **Dossiê & Prestação de Contas:** botão único para baixar o **Pacote do Projeto** (relatório executivo + pasta com todos os PDFs comprobatórios padronizados por ano/categoria + tabela de produtos por edital).

### 6.3 Tela 3 — Visão do Orientando Convidado (Acesso Gratuito + Gatilho de Conversão)
Quando o aluno clica no link de convite do orientador, entra sem pagar nada e sem barreiras burocráticas:
- **O que ele faz livremente (Grátis):**
  - Vê seus marcos combinados com o orientador;
  - Sobe PDFs de certificados de congressos, resumos publicados em anais, relatórios parciais e rascunhos de artigos;
  - Confirma seu **ORCID** e seus papéis na **Matriz CRediT** dos artigos do grupo;
  - Visualiza na sua tela inicial a **Trajetória Viva** crescendo a cada entrega aprovada pelo orientador.
- **O Momento de Conversão Natural (Paywall Transparente, sem bloquear a colaboração):**
  - No topo do painel pessoal do aluno aparece o cartão **Meu Cofre Pronto para o Lattes**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ✨ SEU COFRE PESSOAL LATTESDATA (ACUMULADO NOS PROJETOS)                │
│                                                                         │
│ Você tem 7 produções e certificados validados pelo Prof. Aramys         │
│ que já estão 100% estruturados nas normas do CNPq:                      │
│   • 1 Artigo em periódico (Foods, 2026 — DOI validado)                  │
│   • 3 Trabalhos publicados em anais de congresso                        │
│   • 2 Apresentações de trabalho com certificado                         │
│   • 1 Participação em Projeto de Pesquisa (vigente)                     │
│                                                                         │
│ [ 🔒 Atualizar meu Currículo Lattes em 1 clique ]                       │
│ [ 🔒 Montar Dossiê & EditalScore para Seleção de Mestrado/Bolsa ]       │
│                                                                         │
│ Plano Estudante ou Passe de Atualização via Pix · Interagir no projeto  │
│ do seu orientador continua sempre gratuito.                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Tela 4 — Fluxo de Propagação 1-para-N (O Coração Técnico)
Exemplo passo a passo de como uma única ação resolve o trabalho de todo o grupo:

1. **Passo 1 (Aluno — Grátis):** A mestranda sobe o PDF de um resumo publicado em anais (ou informa o DOI do artigo recém-publicado na *Foods*) dentro do *Projeto Babaçu*.
2. **Passo 2 (Motor LattesData):** O extrator que já existe no sistema (`artigo.py`, `caderno.py`, `certificado.py`, `itens/leitores.py`) lê o PDF/DOI, identifica autores, periódico/evento, ano, páginas, financiamento e já associa automaticamente ao **Projeto de Pesquisa** e às **Orientações** cadastradas.
3. **Passo 3 (Orientador — 1 clique):** O orientador recebe o aviso *"Nova entrega de [Aluna] no Projeto Babaçu"*, revisa os campos extraídos e clica em **"Aprovar e Vincular ao Projeto"**.
4. **Passo 4 (Propagação Automática):**
   - O PDF entra no **Dossiê de Prestação de Contas** do projeto (vinculado aos processos FAPEMA/FINEP/CAPES);
   - O registro entra pronto na **fila de preenchimento do Lattes do Orientador** (e dos docentes parceiros pagantes);
   - O registro entra no **Cofre Pessoal** de cada aluno coautor (pronto para sincronizar assim que o aluno ativar seu acesso pessoal).

---

## 7. Modelo de Dados Conceitual e Integração com o LattesData Atual

A arquitetura aproveita diretamente os módulos já validados na base do projeto:

| Entidade Conceitual | Responsabilidade | Integração com o Código Atual |
| :--- | :--- | :--- |
| `Projeto` | Identidade, natureza, vigência, grande área e lista de `packs_ativos` | Alinhado a [projeto.json](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/itens/especificacao/projeto.json) (5 naturezas validadas no Lattes real) |
| `MembroProjeto` | Usuário, papel no projeto (`coordenador`, `orientador`, `parceiro`, `orientando`), nível (`IC`/`M`/`D`/`PD`), ORCID e status de convite | Conecta-se a [orientacao.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/orientacao.py) e [autores_cv.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/autores_cv.py) |
| `FomentoProcesso` | Agência, modalidade (`APP`, `BM`, `PQ`, `INFRA`, `Universal`, `EMBRAPII`), número do processo, vigência e relação N:N com projetos e produtos | Alimenta financiamento do projeto e relatórios de prestação de contas |
| `RegulatorioProjeto` | Itens modulares dos Packs (`CEUA`, `CEP/CAAE`, `Dispensa 510`, `SisGen`, `SISBIO`, `ReBEC`, `PROSPERO/OSF`, `NDA/Embargo`, `TRL`, `MAPA`) com validade e anexo PDF | Gera alertas preventivos e parágrafos padronizados de submissão |
| `EntregaEvidencia` | Upload feito por orientando/membro, vínculo com marco, status de revisão (`pendente`, `aprovada`, `ajustar`) e arquivo PDF | Reutiliza [extractor.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/extractor.py), [classificador.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/classificador.py) e [organizer.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/organizer.py) |
| `ProdutoProjeto` | Artigo, conferência, livro/capítulo, dataset, software, patente, PTT ou obra artística + matriz `CRediT` + agrupamento de versões (`preprint` / `PT-EN-ES`) | Conecta-se a [curriculo_store.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/curriculo_store.py), [abertura.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/abertura.py) e às especificações em `itens/especificacao/` |
| `FilaPropagacaoLattes` | Distribuição 1-para-N do registro aprovado para a fila de preenchimento do orientador (liberado) e para o cofre pessoal dos alunos (gate de conversão) | Conecta-se ao fluxo de envio da extensão e ao [edital.py](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/edital.py) (EditalScore) |

---

## 8. Sequência Recomendada de Validação e Evolução

1. **Fase Atual (Validação Conceitual com Docentes):** testar este modelo diretamente na escuta com o Prof. Dr. Aramys Silva dos Reis e docentes de outras áreas (Bloco 9 do questionário no Espaço Colaborativo).
2. **MVP do Ambiente de Projetos (Foco inicial):** implementar a **Espinha Dorsal Universal** + **Packs 1 e 3** (Saúde/Bancada e Saúde Coletiva/Revisões/PTT — exatamente o perfil do PPGST/UFMA), validando o fluxo real de 1 orientador convidando 3 a 5 orientandos.
3. **Expansão Multi-Áreas:** ativar gradualmente os demais Packs (Computação/IA, Engenharias/TRL, Agrárias/Alimentos, Humanas/Sociais/Artes e Big Science) conforme novos grupos e PPGs entrarem na plataforma.
