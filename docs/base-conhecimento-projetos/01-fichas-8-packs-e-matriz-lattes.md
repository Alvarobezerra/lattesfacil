# Fichas dos 8 Packs por Especialidade e Matriz Consolidada Lattes / CAPES

> **Base de Conhecimento e Referência — LattesData (Documento 01)**  
> **Escopo:** especificação técnica e acadêmica da Espinha Dorsal Universal (6 Pilares Fixos), das Fichas Padronizadas dos 8 Packs Modulares por Especialidade e da Matriz Consolidada de Mapeamento entre artefatos de projeto, categorias reais do Currículo Lattes (`itens/especificacao/*.json`), indicadores da Avaliação CAPES/Sucupira e gatilhos de conversão do estudante no modelo *Host Pays, Guests Collaborate Free*.  
> **Referência arquitetural:** alinhado a `docs/arquitetura-projetos-pesquisa-lattesdata.md` e ao catálogo de 64 especificações reais do LattesData em `itens/especificacao/`.

---

## 1. Introdução e Estrutura da Espinha Dorsal Universal (6 Pilares Fixos)

Projetos científicos no Brasil variam radicalmente em método, regulação e tipo de entrega — da bancada de bioprospecção com `CEUA`/`SisGen` ao ensaio clínico com `CEP/CONEP`/`ReBEC`, da conferência de IA com *Artifact Evaluation* ao projeto guarda-chuva de História com coletânea organizada e pesquisa em acervos. Apesar dessa diversidade, a análise empírica de **1.150+ produções de 13 pesquisadores brasileiros nas 8 Grandes Áreas do CNPq** e dos fluxos de periódicos **Qualis A1/A2** demonstra que todo projeto acadêmico compartilha uma **Espinha Dorsal Universal de 6 Pilares Fixos**.

No LattesData, **todo projeto nasce sobre esses 6 pilares imutáveis**, e o orientador/coordenador ativa **1 ou mais Packs Modulares** apenas para destravar campos regulatórios, checklists de reprodutibilidade, marcos especializados e saídas técnicas específicas da sua área — mantendo a interface limpa e evitando o abandono típico de gerenciadores genéricos.

### 1.1 Os 6 Pilares Fixos do Núcleo Universal

| Pilar | Responsabilidade no Projeto | Integração com o LattesData e CNPq |
| :--- | :--- | :--- |
| **1. Identidade & Natureza** | Título, resumo, objetivos, vigência (início/fim), Grande Área CNPq, instituições envolvidas e natureza oficial do projeto. | Alinhado diretamente a `projeto.json` (5 naturezas reais do Lattes: **Pesquisa**, **Desenvolvimento**, **Extensão**, **Ensino** e **Outra**; situações: *Em andamento*, *Concluído*, *Desativado*). |
| **2. Equipe & Papéis por Projeto** | Papéis contextuais por projeto — o mesmo docente pode ser **Coordenador/Orientador** em um projeto e **Pesquisador Parceiro** em outro, junto a **Coorientadores**, **Parceiros Externos** e **Orientandos Convidados (IC, Mestrado, Doutorado, Pós-Doc)**. | Conecta-se a `orientacao_andamento.json`, `orientacao_concluida.json`, `pos_doutorado.json` e à gestão de coautoria/ORCID. |
| **3. Carteira de Fomentos & Bolsas (N:N)** | Cadastro único de editais, auxílios e bolsas (`CNPq`, `CAPES`, `FAPs`, `FINEP`, `EMBRAPII`, `BNB`, empresas), com vínculo **N:N** (um artigo/produto presta contas a vários processos simultâneos). Gera texto pronto de *Funding/Acknowledgements* (PT/EN) e relatório por processo. | Alimenta a aba de financiamento de `projeto.json` e o módulo de Dossiê de Prestação de Contas. |
| **4. Marcos de Execução & Repositório de Evidências** | Linha do tempo viva (plano de trabalho → qualificação → coleta/execução → congressos → defesa) com guarda permanente de PDFs, certificados, atas e comprovantes, eliminando o *Lab Turnover* (perda de documentos quando o aluno se forma). | Alimenta `participacao_evento.json`, `apresentacao.json`, `banca.json`, `relatorio_pesquisa.json` e o cofre permanente do orientador. |
| **5. Gestor de Produtos, Autoria e Versões** | Controle unificado de saídas bibliográficas, técnicas, tecnológicas e artísticas, com **Matriz CRediT + ORCID**, trilha **Preprint / Working Paper → Publicação Final** e **Agrupador Multilíngue (PT/EN/ES)** para impedir duplicidades no Lattes/Sucupira. | Mapeia diretamente para as especificações em `itens/especificacao/*.json` (`artigo.json`, `anais.json`, `livro_capitulo.json`, `patente.json`, `software_registro.json`, `produto.json`, `artes_visuais.json`, etc.). |
| **6. Motor de Propagação 1-para-N & Prestação de Contas** | Toda entrega validada pelo orientador entra **uma única vez** e é propagada automaticamente: (a) fila de preenchimento do Lattes do orientador e parceiros pagantes, (b) **Cofre Pessoal** de cada orientando coautor (gatilho de conversão), e (c) Dossiê de Prestação de Contas / Relatório CAPES-Sucupira. | Conecta o repositório do projeto à extensão de preenchimento assistido do Lattes e ao **EditalScore / Dossiê PDF**. |

### 1.2 Arquitetura de Encaixe: Espinha Dorsal + 8 Packs Plugáveis

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                   ESPINHA DORSAL UNIVERSAL (6 PILARES)                     │
│  [1] Identidade  [2] Equipe  [3] Fomentos N:N  [4] Marcos  [5] Produtos    │
│                         [6] Motor Lattes 1→N / Sucupira                    │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │ ativa 1 ou mais módulos
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
  [Pack 1] Bancada   [Pack 2] Ensaios [Pack 3] Saúde [Pack 4] IA &  [Pack 5] Eng. &
  Biol. & Farmácia   Clínicos         Col./Rev./PTT  Computação     Indústria (TRL)
        │              │              │              │              │
        └──────────────┴──────────────┼──────────────┴──────────────┘
                                      │
                       ┌──────────────┼──────────────┐
                       ▼              ▼              ▼
                 [Pack 6] Agrárias  [Pack 7] Humanas [Pack 8] Big Science,
                 Alim. & Ambientais Soc. Apl. & Artes Química & Consórcios
```

> **Composição híbrida:** um mesmo projeto pode combinar packs quando sua natureza é interdisciplinar — por exemplo, um projeto de bioprospecção com protótipo industrial ativa **Pack 1 + Pack 5**; uma pesquisa de IA aplicada à saúde pública com aplicativo validado ativa **Pack 3 + Pack 4**.

---

## 2. Fichas Detalhadas dos 8 Packs por Especialidade

---

### Pack 1 — Bancada, Biológicas & Farmácia

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Ciências Biológicas I, II e III; Farmácia; Biotecnologia; Biodiversidade; Imunologia; Microbiologia; Bioquímica; Farmacologia; Química Medicinal / Produtos Naturais.
- **Periódicos de referência (Qualis A1/A2):** *Nature Communications*, *Science Advances*, *Journal of Ethnopharmacology*, *Phytomedicine*, *Foods*, *Frontiers in Pharmacology*, *Biomedicine & Pharmacotherapy*, *PLOS Pathogens*, *Memórias do Instituto Oswaldo Cruz*, *International Journal of Biological Macromolecules*.

#### 2. Fluxo de etapas
1. **Pré-execução:** delimitação do alvo biológico/bioproduto; levantamento de anterioridade patentária (busca no INPI/Espacenet); submissão e aprovação regulatória (`CEUA`, `SisGen`, `SISBIO`, `CTNBio/CIBio`); coleta botânica/biológica com depósito de exsicata/*voucher* em herbário ou coleção de cultura; definição de protocolos operacionais padrão (POPs) e planejamento estatístico/amostral (*n* mínimo).
2. **Execução:** extração, fracionamento e caracterização fitoquímica/molecular (HPLC, LC-MS, RMN); ensaios *in vitro* (citotoxicidade, atividade antimicrobiana/antioxidante/imunomoduladora) e *in vivo* em modelos animais; registro contínuo em caderno de bancada e guarda de espectros/dados brutos; relatórios parciais de bolsas (`PIBIC`, `FAPs`, `CNPq`).
3. **Validação / Submissão:** **Gate de Propriedade Intelectual (NIT/INPI)** — avaliação obrigatória de patenteabilidade *antes* da divulgação pública ou submissão do manuscrito; consolidação do checklist `ARRIVE 2.0` (para modelos animais); conferência de `CRediT`, `ORCID` e parágrafo de *Funding* multiagência; submissão ao periódico e resposta aos pareceristas (*rebuttal* experimental com eventuais experimentos complementares).
4. **Pós-publicação:** arquivamento definitivo do PDF publicado, *Supplementary Material* e licenças regulatórias; atualização do depósito/exame de patente; prestação de contas aos editais (ex.: `FAPEMA`, `FINEP`, `CAPES`, `CNPq`, `BNB`); disseminação em congressos e relatórios de PPG.

#### 3. Papéis dos atores
- **Orientador / PI:** coordena a linha de pesquisa, assina a responsabilidade legal na `CEUA`/`SisGen`/`CIBio`, articula o NIT para patentes, capta editais (`Universal`, `FINEP`, `FAPs`) e valida manuscritos e entregas.
- **Coorientador / Pesquisadores Parceiros:** lideram frentes analíticas complementares (ex.: espectrometria de massas, histopatologia, modelagem *in silico*, biotério parceiro) em rede intra-PPG ou multi-institucional.
- **Iniciação Científica (IC):** preparo de extratos/soluções, manutenção de culturas celulares/cepas, tabulação de dados primários, apresentação de pôsteres e resumos em jornadas/congressos.
- **Mestrado:** executa um recorte experimental completo (caracterização + ensaios *in vitro*/*in vivo*), redige o primeiro manuscrito, apoia a supervisão de ICs e defende a dissertação.
- **Doutorado / Pós-Doc:** conduz mecanismos de ação aprofundados, otimização de formulações/bioprodutos, redação de múltiplos artigos Qualis A1/A2, redação técnica do pedido de patente e coorientação informal de ICs/mestrandos.
- **Parceiros Externos:** cooperativas extrativistas (ex.: acesso a conhecimento tradicional associado / repartição de benefícios), herbários, biotérios centrais, NITs universitários e indústrias farmacêuticas/cosméticas.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **CEUA / CONCEA:** aprovação prévia obrigatória para qualquer uso de animais vertebrados (número de protocolo e vigência).
- **SisGen (Lei nº 13.123/2015):** cadastro obrigatório de acesso ao Patrimônio Genético Brasileiro (PG) e/ou Conhecimento Tradicional Associado (CTA) antes de publicação, patenteamento ou remessa ao exterior.
- **SISBIO / ICMBio:** autorização para coleta de material biológico em unidades de conservação ou fauna silvestre.
- **CTNBio / CIBio:** Certificado de Qualidade em Biossegurança (CQB) para Organismos Geneticamente Modificados (OGMs).
- **Reprodutibilidade:** diretrizes `ARRIVE 2.0` (experimentação animal), identificação taxonômica com número de tombo/*voucher* em herbário reconhecido, disponibilização de cromatogramas/espectros brutos e bloqueio de sigilo pré-patente (**Gate INPI**).

#### 5. Evidências e artefatos gerados (além do artigo)
- Certificados `CEUA`, recibos `SisGen`, autorizações `SISBIO`, pareceres `CIBio` e comprovantes de depósito de exsicata.
- Pedidos de patente (BR/PCT), relatórios de busca de anterioridade e pareceres de viabilidade do NIT.
- Protocolos experimentais padronizados (POPs), extratos/formulações/protótipos de bioprodutos e dados suplementares (espectros, imagens de microscopia/histologia).
- Resumos expandidos em anais de congressos, prêmios de melhor trabalho, relatórios técnicos de fomento e atas de defesa.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 1 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto de bioprospecção / bancada | `projeto.json` (*Pesquisa* ou *Desenvolvimento*) | Projetos de Pesquisa / Desenvolvimento Tecnológico | Vínculo obrigatório Projeto ↔ Orientação ↔ Produção |
| Artigo original em periódico A1/A2 | `artigo.json` / `artigo_aceito.json` | Produção Bibliográfica > Artigos completos publicados / aceitos | Estrato Qualis A1/A2 (peso central na produção intelectual) |
| Depósito/concessão de patente | `patente.json` | Patentes e Registros > Patente | **PTT de alto impacto (T1/T2)**; fortalece inovação e transferência |
| Bioproduto / formulação / processo | `produto.json`, `processo_tecnica.json` | Produção Técnica > Produtos Tecnológicos / Processos ou Técnicas | Produção Técnica/Tecnológica (PTT) no PPG |
| Resumo / trabalho em congresso | `anais.json`, `apresentacao.json` | Trabalhos publicados em anais / Apresentação de trabalho | Formação discente (IC/M/D) e visibilidade científica |
| Relatório de fomento / pesquisa | `relatorio_pesquisa.json` | Produção Técnica > Relatório de pesquisa | Comprovação de captação e execução de recursos |
| Dissertação, tese e IC | `orientacao_andamento.json`, `orientacao_concluida.json`, `banca.json` | Orientações e Bancas | Indicador de formação de RH e titulação no prazo |

---

### Pack 2 — Ensaios Clínicos & Intervenções

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Medicina I, II e III; Odontologia; Fisioterapia e Terapia Ocupacional; Enfermagem Clínica; Educação Física (intervenção clínica); Nutrição Clínica; Fonoaudiologia.
- **Periódicos de referência (Qualis A1/A2):** *The Lancet*, *BMJ*, *NEJM*, *JAMA*, *Journal of Dental Research*, *Physical Therapy*, *International Journal of Nursing Studies*, *Archives of Physical Medicine and Rehabilitation*, *Brazilian Journal of Physical Therapy*, *Clinics*.

#### 2. Fluxo de etapas
1. **Pré-execução:** elaboração do protocolo clínico completo seguindo `SPIRIT`; cálculo amostral e definição do plano de análise estatística (`SAP`); submissão na **Plataforma Brasil (`CEP/CONEP` — geração do `CAAE`)** e, quando envolver medicamento/dispositivo sob investigação, anuência da **ANVISA**; **registro prospectivo obrigatório** do ensaio no `ReBEC` ou `ClinicalTrials.gov` antes da inclusão do 1º participante; construção do `eCRF` (`REDCap`) e definição do comitê de monitoramento de dados (`DSMB`).
2. **Execução:** recrutamento de participantes com assinatura do `TCLE` (e `TALE`, se menores); randomização, sigilo de alocação e cegamento (*blinding*); aplicação da intervenção/placebo em centro único ou multicêntrico; coleta padronizada de desfechos primários/secundários e notificação rigorosa de eventos adversos graves (`EAG`) ao `CEP`/`DSMB`.
3. **Validação / Submissão:** fechamento e travamento da base de dados (*database lock*); execução da análise estatística por intenção de tratar (`ITT`) conforme `SAP`; redação do manuscrito aderente ao `CONSORT` (com fluxograma de participantes e checklist preenchido); submissão do protocolo publicado e do artigo de resultados finais.
4. **Pós-publicação:** atualização obrigatória dos resultados no `ReBEC`/`ClinicalTrials.gov`; relatório final à Plataforma Brasil (`CEP/CONEP`); incorporação dos achados em diretrizes clínicas, protocolos assistenciais hospitalares e nota de imprensa científica.

#### 3. Papéis dos atores
- **Orientador / PI (Investigador Principal):** assume a responsabilidade ética e sanitária do ensaio perante `CEP/CONEP` e `ANVISA`, supervisiona segurança dos participantes, coordena centros colaboradores e responde pela integridade dos dados.
- **Coorientador / Investigadores de Centros Parceiros:** conduzem recrutamento e intervenção em hospitais/clínicas parceiras, garantem padronização de aferição e revisam o manuscrito.
- **Iniciação Científica (IC):** apoio no agendamento, triagem supervisionada, conferência de formulários (`REDCap`), digitação dupla e apresentação de resultados preliminares/metodológicos.
- **Mestrado:** gerencia a operacionalização de um braço ou desfecho secundário do ensaio, conduz avaliações cegas, publica o protocolo ou desfecho específico e defende a dissertação.
- **Doutorado / Pós-Doc:** coordena o ensaio completo ou a rede multicêntrica, executa análises longitudinais avançadas, interage com o `DSMB`, redige o artigo principal *CONSORT* e apoia a tradução do conhecimento para protocolos clínicos.
- **Parceiros Externos:** hospitais universitários (`EBSERH`), secretarias de saúde, estatísticos independentes, membros do `DSMB`, farmacêuticos responsáveis por cegamento e comitês de pacientes.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **CEP/CONEP (Res. CNS nº 466/2012 e Lei nº 14.874/2024):** parecer consubstanciado aprovado e número `CAAE` obrigatório antes de qualquer recrutamento.
- **ANVISA (RDC nº 9/2015 e atualizações):** Dossiê de Desenvolvimento Clínico de Medicamento (`DDCM`) ou anuência para dispositivos médicos quando aplicável.
- **Registro Prospectivo Obrigatório:** `ReBEC` (Registro Brasileiro de Ensaios Clínicos) ou `ClinicalTrials.gov` **antes** do recrutamento do primeiro participante (exigência do ICMJE — periódicos A1 rejeitam registros retrospectivos).
- **LGPD (dados sensíveis de saúde):** pseudonimização, controle de acesso no `REDCap`, guarda segura de `TCLEs` e plano de compartilhamento de dados desidentificados (*Data Sharing Statement*).
- **Reprodutibilidade:** checklists `SPIRIT` (protocolo), `CONSORT 2010/2025` (ensaio randomizado), `TIDieR` (descrição da intervenção) e publicação prévia do `SAP`.

#### 5. Evidências e artefatos gerados (além do artigo)
- Parecer consubstanciado `CEP/CONEP` (`CAAE`), anuência `ANVISA`, comprovante de registro prospectivo (`ReBEC`/`ClinicalTrials.gov`) e relatórios de `DSMB`.
- Artigo de protocolo clínico (*study protocol*), dicionário de dados/`eCRF` (`REDCap`) e `SAP` arquivado.
- Protocolos clínicos assistenciais, manuais de intervenção fisioterapêutica/odontológica/médica e diretrizes terapêuticas adotadas por serviços de saúde.
- Relatórios finais à Plataforma Brasil e certificados de Boas Práticas Clínicas (`GCP/BPC`) da equipe.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 2 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto de ensaio clínico | `projeto.json` (*Pesquisa*) | Projetos de Pesquisa | Evidência de pesquisa clínica estruturada e multicêntrica |
| Artigo de protocolo e artigo principal | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos em periódicos | Alto impacto Qualis A1/A2 e citações internacionais |
| Protocolo clínico / diretriz assistencial | `processo_tecnica.json`, `trabalho_tecnico.json`, `relatorio_tecnico.json` | Produção Técnica > Processos ou Técnicas / Trabalhos Técnicos | **PTT de impacto assistencial (SUS/hospitais)** |
| Material educativo para pacientes/equipe | `material_didatico.json` | Desenvolvimento de material didático ou instrucional | PTT de formação e impacto social na saúde |
| Curso de capacitação na intervenção | `curso_ministrado.json` | Cursos de curta duração ministrados | Transferência tecnológica e inserção social |
| Apresentações em congressos médicos | `anais.json`, `apresentacao.json` | Trabalhos em anais / Apresentação de trabalho | Produção discente e internacionalização |
| Orientações e bancas clínicas | `orientacao_andamento.json`, `orientacao_concluida.json`, `banca.json` | Orientações e Bancas | Formação qualificada em programas acadêmicos e profissionais |

---

### Pack 3 — Saúde Coletiva, Coortes, Revisões & PTT

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Saúde Coletiva; Enfermagem; Interdisciplinar em Saúde; Educação em Saúde; Epidemiologia; Política, Planejamento e Gestão em Saúde; Programas Profissionais (Mestrado/Doutorado Profissional em Saúde).
- **Periódicos de referência (Qualis A1/A2):** *Cadernos de Saúde Pública*, *Ciência & Saúde Coletiva*, *Revista de Saúde Pública*, *Epidemiologia e Serviços de Saúde*, *Revista Brasileira de Enfermagem (REBEn)*, *Revista Latino-Americana de Enfermagem (RLAE)*, *BMC Public Health*, *Lancet Global Health*, *BMJ Open*, *JBI Evidence Synthesis*.

#### 2. Fluxo de etapas
1. **Pré-execução:** definição do desenho (estudo ecológico/coorte em bases públicas, pesquisa qualitativa, revisão sistemática/de escopo ou desenvolvimento de Produto Técnico-Tecnológico — PTT); enquadramento ético (**CEP/CAAE** para dados primários OU **Dispensa formal de CEP pela Res. CNS nº 510/2016** para bases públicas agregadas como `DATASUS`, `SINAN`, `SIM`, `SIH`, `IBGE`); registro prospectivo de protocolo de revisão (`PROSPERO`, `OSF`, `JBI` ou `INPLASY`).
2. **Execução:**
   - *Epidemiologia/Coortes:* extração, *linkage* e limpeza de bases (`DATASUS`/`IBGE`), análise espacial/temporal ou seguimento de coorte.
   - *Revisões:* busca estruturada em bases (`PubMed`, `Embase`, `Scopus`, `WoS`, `LILACS`, literatura cinzenta), triagem pareada e independente por 2 revisores + 3º juiz (`Rayyan`/`Covidence`), avaliação de risco de viés (`RoB 2`, `ROBINS-I`, `JBI`).
   - *PTTs:* prototipagem de cartilha, aplicativo *mHealth*, protocolo operacional, vídeo educativo ou curso, seguida de **validação de conteúdo/aparência com comitê de juízes especialistas** (cálculo de `IVC` ≥ 0,80 / `CVR`) e validação semântica com o público-alvo.
3. **Validação / Submissão:** aplicação dos checklists `PRISMA 2020` / `PRISMA-ScR` (revisões), `STROBE` (observacionais) ou `COREQ` (qualitativos); atenção ao **agrupamento multilíngue** (periódicos como *REBEn* e *RLAE* publicam em PT/EN/ES com múltiplos DOIs, que não devem ser duplicados no Lattes); emissão de registro de ISBN/ISSN, registro de software (se app) e **declaração de aplicação/adoção real do PTT** pelo serviço de saúde.
4. **Pós-publicação:** registro estruturado da ficha de PTT para a CAPES (evidenciando aderência, impacto, aplicabilidade, inovação e complexidade); entrega de devolutiva às Secretarias de Saúde/serviços do SUS; prestação de contas e arquivamento de declarações de implementação.

#### 3. Papéis dos atores
- **Orientador / PI:** define a pergunta epidemiológica ou a demanda real do serviço de saúde, valida a estratégia de busca/modelagem, atua como 3º revisor (juiz de desempate) em revisões e articula gestores do SUS para adoção do PTT.
- **Coorientador / Parceiros:** especialistas em bioestatística, geoprocessamento, biblioteconomia (estratégia de busca), design instrucional ou gestão em saúde.
- **Iniciação Científica (IC):** apoio na extração de bases públicas (`DATASUS`), triagem de títulos/resumos sob supervisão, tabulação de formulários de juízes e apresentações em congressos.
- **Mestrado (Acadêmico ou Profissional):** lidera revisão sistemática/de escopo, estudo epidemiológico ou ciclo completo de construção + validação de um PTT (dissertação + produto validado e aplicado).
- **Doutorado / Pós-Doc:** conduz coortes longitudinais, modelagem espaço-temporal complexa, metanálises em rede, avaliação de efetividade de PTTs em larga escala e múltiplos artigos A1/A2.
- **Parceiros Externos:** juízes especialistas (painel Delphi/IVC), Secretarias Municipais e Estaduais de Saúde, Atenção Primária/ESF, bibliotecários de referência e associações de usuários.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **Dupla via ética:** `CEP/CAAE` (Res. CNS nº 466/2012) para coleta com seres humanos ou prontuários nominais **OU** justificativa formal de **Dispensa de CEP (Res. CNS nº 510/2016, Art. 1º, parágrafo único)** para dados secundários de domínio público sem identificação individual.
- **Registro Prospectivo de Revisões:** `PROSPERO` (revisões sistemáticas de saúde) ou `OSF` / `Figshare` (revisões de escopo) antes da extração de dados.
- **Diretrizes de Relato (EQUATOR):** `PRISMA 2020`, `PRISMA-ScR`, `STROBE`, `RECORD` (dados rotineiramente coletados) e `COREQ` (pesquisa qualitativa).
- **Rastreabilidade de PTT (CAPES):** comprovação documental de validação (ata/relatório de `IVC`), registro público (ISBN, INPI, repositório institucional) e **carta/declaração de aplicação real** emitida pelo serviço adotante.

#### 5. Evidências e artefatos gerados (além do artigo)
- Protocolo registrado (`PROSPERO`/`OSF`), estratégia de busca completa por base e planilha de triagem/extração de dados.
- Declaração de dispensa de CEP ou parecer `CAAE`; relatórios de validação por juízes (`IVC`) e certificados de participação dos juízes.
- **Produtos Técnico-Tecnológicos (PTTs):** cartilhas, e-books técnicos, protocolos assistenciais, aplicativos *mHealth*, vídeos educativos, cursos de capacitação, notas técnicas e boletins epidemiológicos.
- Declarações oficiais de adoção/impacto emitidas por Secretarias de Saúde ou hospitais.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 3 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto epidemiológico / de PTT | `projeto.json` (*Pesquisa*, *Extensão* ou *Desenvolvimento*) | Projetos de Pesquisa / Extensão / Desenvolvimento | Base estruturante da linha de pesquisa do PPG |
| Artigo original / revisão (com agrupamento PT/EN/ES) | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Qualis A1/A2; evita erro grave de duplicidade bilíngue na Sucupira |
| Cartilha, manual, vídeo ou guia educativo (PTT) | `material_didatico.json`, `livro_capitulo.json` | Desenvolvimento de material didático / Livros técnicos | **PTT classificado T1–T3** (peso máximo em Mestrados/Doutorados Profissionais) |
| App *mHealth* / sistema de saúde | `software_registro.json` / `software_sem_registro.json` | Programas de Computador (com ou sem registro) | **PTT de alta complexidade e inovação** |
| Protocolo operacional / boletim / nota técnica | `processo_tecnica.json`, `relatorio_tecnico.json`, `trabalho_tecnico.json` | Processos ou Técnicas / Relatórios e Trabalhos Técnicos | Evidência de impacto social e transferência para o SUS |
| Curso de formação para profissionais de saúde | `curso_ministrado.json`, `extensao_tecnologica.json` | Cursos ministrados / Extensão tecnológica | Inserção social e qualificação profissional |
| Mídia educativa / divulgação em saúde | `entrevista_midia.json`, `redes_sociais.json`, `outra_producao_tecnica.json` | Entrevistas, mídias sociais e outras produções técnicas | Divulgação científica e impacto na sociedade |

---

### Pack 4 — Computação, IA & Ciência de Dados

#### 1. Áreas atendidas e periódicos/conferências Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Ciência da Computação; Inteligência Artificial e Aprendizado de Máquina; Engenharia de Software; Ciência de Dados; Estatística Computacional; Sistemas de Informação; Bioinformática; Visão Computacional e PLN.
- **Conferências e Periódicos de referência (Qualis A1/A2 — *na Computação, conferências de topo equivalem ou superam periódicos*):** *NeurIPS*, *ICML*, *ICLR*, *CVPR*, *ACL*, *AAAI*, *KDD*, *ICSE*, *FSE*, *CHI*, *IEEE TPAMI*, *IEEE Transactions on Knowledge and Data Engineering (TKDE)*, *Information Sciences*, *Expert Systems with Applications*, *Journal of Systems and Software (JSS)*.

#### 2. Fluxo de etapas
1. **Pré-execução:** definição do problema, hipótese algorítmica e *baselines* estado da arte; verificação de licenças de datasets e conformidade ética/LGPD (especialmente em dados clínicos, biométricos ou redes sociais); criação do repositório versionado (`GitHub`/`GitLab`) com estrutura reprodutível (`Docker`/`Conda`, `seed` fixo, `README`); alocação de infraestrutura de GPU/HPC.
2. **Execução:** desenvolvimento de arquitetura/algoritmo, estudos de ablação (*ablation studies*), validação cruzada e testes estatísticos de significância contra *baselines*; versionamento de modelos e experimentos (`Weights & Biases`/`MLflow`); publicação opcional de **preprint no `arXiv`** para estabelecer prioridade científica.
3. **Validação / Submissão (Ciclo de Conferência A1):** submissão em *double-blind review* com código anonimizado (`Anonymous GitHub`) + preenchimento do **Reproducibility Checklist**; fase de **Rebuttal / Author Response** (prazo curto de 5–7 dias com experimentos extras); após aceite, etapa de **Artifact Evaluation** (selo *Artifacts Available / Functional / Reusable*) e entrega do **Camera-Ready** com código público definitivo.
4. **Pós-publicação:** vinculação do **Preprint (`arXiv`) → Publicação Final (`DOI` em anais ou periódico)** para evitar duplicação; arquivamento permanente do código/dataset no **Zenodo (DOI)** ou **Hugging Face**; avaliação de **Registro de Programa de Computador no INPI** (via NIT); apresentação oral/pôster na conferência.

#### 3. Papéis dos atores
- **Orientador / PI:** define a agenda científica e arquitetural, negocia acesso a clusters/GPUs e editais (`CNPq`, `FAPESP`, `EMBRAPII`, *Big Techs*), revisa o posicionamento teórico do artigo e conduz a estratégia de *rebuttal*.
- **Coorientador / Pesquisadores Parceiros:** colaboram com domínio de aplicação (saúde, direito, agronegócio, indústria), validação estatística ou infraestrutura computacional internacional.
- **Iniciação Científica (IC):** limpeza e curadoria de datasets, implementação de *baselines*, execução de *benchmarks* e documentação de scripts.
- **Mestrado:** propõe e implementa um método/modelo completo, executa estudos de ablação, prepara o pacote de reprodutibilidade e publica em conferência ou periódico A1/A2.
- **Doutorado / Pós-Doc:** lidera contribuições teóricas/algorítmicas originais de fronteira, coordena grandes *benchmarks* e artefatos *open-source*, atua como revisor em conferências de topo e orienta tecnicamente ICs e mestrandos.
- **Parceiros Externos:** empresas de tecnologia, centros de PD&I, laboratórios internacionais de IA, NIT (registro de software) e mantenedores de bases de dados abertas.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **Reprodutibilidade obrigatória (NeurIPS/ICML/ACM):** disponibilização de código-fonte, hiperparâmetros, sementes aleatórias, especificação de hardware/tempo de treino e container `Docker` ou ambiente declarativo.
- **Artifact Evaluation (ACM/IEEE):** empacotamento auditável para obtenção de selos de disponibilidade e reprodutibilidade.
- **Ética em IA, Viés e LGPD:** declaração de impacto mais amplo (*Broader Impact / Ethics Statement*), licenciamento de dados de treinamento, anonimização/LGPD quando houver dados pessoais e `CEP` se envolver avaliação com usuários humanos (*user studies* em IHC/Eng. Software).
- **Licenciamento e Propriedade Intelectual:** escolha consciente de licença *open-source* (`MIT`, `Apache 2.0`, `GPL`) vs. proteção proprietária (**Registro de Software no INPI**).

#### 5. Evidências e artefatos gerados (além do artigo)
- Repositório `GitHub`/`GitLab` arquivado com DOI no **Zenodo** ou **Software Heritage**; modelos e datasets publicados no **Hugging Face** ou **Kaggle**.
- Certificado de **Registro de Programa de Computador no INPI**; selos de *Artifact Evaluation*; preprints (`arXiv`) vinculados à versão final.
- Documentação de *rebuttal*, vídeos de demonstração (*demo papers*), bibliotecas/pacotes (`PyPI`, `CRAN`, `npm`) e métricas de adoção (*stars*, downloads, citações de software).

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 4 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto de IA / Computação / Dados | `projeto.json` (*Pesquisa* ou *Desenvolvimento*) | Projetos de Pesquisa / Desenvolvimento Tecnológico | Vínculo formal de linhas e captação (inclusive com empresas) |
| Artigo completo em conferência A1/A2 | `anais.json` (*Trabalho completo publicado em anais*) | Trabalhos completos publicados em anais de congressos | **Na área de Computação da CAPES, anais Qualis A1/A2 têm peso equivalente a periódicos** |
| Artigo em periódico (IEEE/ACM/Elsevier) | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Estrato Qualis A1/A2 |
| Software registrado no INPI | `software_registro.json` | Patentes e Registros > Programa de computador registrado | **PTT de alto peso (T1/T2)**; indicador de inovação |
| Código aberto / pacote / modelo sem registro INPI | `software_sem_registro.json` | Produção Técnica > Programas de computador sem registro | PTT técnico e evidência de ciência aberta |
| Dataset / *benchmark* com DOI (Zenodo/HF) | `outra_producao_tecnica.json` / `produto.json` | Produção Técnica > Produtos Tecnológicos / Outra produção técnica | Reprodutibilidade e impacto da infraestrutura aberta |
| Atuação como revisor / comitê de programa | `revisor_periodico.json`, `organizacao_evento.json` | Revisor de periódico / Organização de eventos | Reconhecimento internacional na área |

---

### Pack 5 — Engenharias, Indústria & TRL

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Engenharias I, II, III e IV (Química, Materiais e Metalúrgica, Elétrica, Mecânica, Civil, Produção, Aeroespacial, Biomédica, Petróleo e Energia).
- **Periódicos de referência (Qualis A1/A2):** *Chemical Engineering Journal*, *Ceramics International*, *IEEE Transactions on Power Electronics / Industrial Electronics*, *Applied Energy*, *Journal of Cleaner Production*, *Materials & Design*, *Composites Part B*, *International Journal of Production Economics*, *Industrial & Engineering Chemistry Research*.

#### 2. Fluxo de etapas
1. **Pré-execução:** definição do problema industrial e da meta de maturidade tecnológica (**TRL inicial → TRL alvo**, tipicamente TRL 2–3 para TRL 4–6); negociação de contrato **EMBRAPII, ANP (cláusula de P&D), ANEEL, FINEP ou convênio empresa-universidade**; assinatura de **NDA (Acordo de Confidencialidade)** e definição de cotitularidade de PI; se houver caracterização avançada, submissão de proposta de tempo de feixe (ex.: **Sirius/LNLS**).
2. **Execução:** modelagem/simulação numérica (CFD, FEM, *digital twin*); fabricação de protótipos em bancada, testes *Hardware-in-the-Loop (HIL)* ou planta piloto (*scale-up*); caracterização físico-química/mecânica/elétrica sob normas técnicas (`ABNT`, `ASTM`, `ISO`, `IEEE`); reuniões de marco contratual (*stage-gates*) com a empresa parceira e entregas de relatórios técnicos confidenciais.
3. **Validação / Submissão:** **Gate de Sigilo, Embargo e PI** — revisão obrigatória pela empresa parceira e pelo NIT antes de qualquer publicação ou defesa; se houver matéria patenteável, **depósito de patente/desenho industrial no INPI** e acionamento de **banca de defesa sigilosa / embargo temporário da dissertação/tese**; somente após o protocolo no INPI, liberação do manuscrito para o periódico A1/A2.
4. **Pós-publicação:** validação do novo nível **TRL** alcançado, eventual licenciamento ou transferência de tecnologia para a indústria, prestação de contas técnica e financeira (auditável por `ANP`/`ANEEL`/`EMBRAPII`/`FINEP`) e desbloqueio programado de embargos vencidos.

#### 3. Papéis dos atores
- **Orientador / PI:** coordena o contrato de P&D&I, negocia cláusulas de PI/NDA com a empresa e o NIT, gerencia os marcos *stage-gate* e equilibra entregas industriais com produção científica A1/A2.
- **Coorientador / Pesquisadores Parceiros:** lideram laboratórios de caracterização, simulações especializadas ou frentes complementares em redes de engenharia.
- **Iniciação Científica (IC):** ensaios padronizados, montagem de bancadas, instrumentação, desenho CAD e coleta de curvas experimentais.
- **Mestrado:** desenvolve modelo, protótipo ou processo otimizado (ex.: TRL 3 → 4/5), entrega relatório técnico à empresa, participa de eventual depósito de PI e defende dissertação (com ou sem termo de sigilo).
- **Doutorado / Pós-Doc:** lidera o *scale-up* ou arquitetura tecnológica completa, integra simulação e planta piloto, redige patentes e artigos A1/A2 e atua como ponte técnica direta com engenheiros da empresa.
- **Parceiros Externos:** engenheiros e gestores de P&D das empresas financiadoras, Unidades EMBRAPII, agentes reguladores (`ANP`/`ANEEL`), NIT/Agência de Inovação e laboratórios nacionais (`LNLS/CNPEM`, `IPT`, `INMETRO`).

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **NDA e Sigilo Industrial:** controle rígido de documentos confidenciais, prazo de revisão pré-publicação pela empresa (geralmente 30 a 90 dias) e controle de **embargo de teses/dissertações** na biblioteca institucional.
- **Gate de Patente (INPI):** bloqueio de submissão pública antes do protocolo de pedido de patente, modelo de utilidade, desenho industrial ou topografia de circuito integrado.
- **Conformidade Contratual de Fomento Industrial:** regras de prestação de contas e auditoria de `EMBRAPII`, `ANP`, `ANEEL` e `FINEP` (comprovação de horas, entregas técnicas e indicadores de TRL).
- **Normas Técnicas e Segurança Laboratorial:** rastreabilidade de calibração de equipamentos, aderência a normas `ABNT`/`ISO`/`ASTM`/`IEEE` e segurança operacional/ambiental.

#### 5. Evidências e artefatos gerados (além do artigo)
- Contratos de P&D&I, termos de `NDA`, acordos de cotitularidade e comprovantes de evolução de **TRL**.
- Pedidos de patente, desenhos industriais, topografias de circuitos, marcas, protótipos físicos, maquetes/plantas piloto e contratos de licenciamento/transferência.
- Relatórios técnicos confidenciais/públicos para empresas e agências (`ANP`/`ANEEL`/`EMBRAPII`), normas técnicas propostas e atas de defesa sigilosa.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 5 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto de P&D&I com indústria | `projeto.json` (*Desenvolvimento* ou *Pesquisa*) | Projetos de Desenvolvimento Tecnológico / Pesquisa | Forte pontuação em interação universidade-empresa e captação |
| Artigo técnico-científico A1/A2 | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Estrato Qualis A1/A2 |
| Patente / Desenho Industrial / Topografia / Marca | `patente.json`, `desenho_industrial.json`, `topografia_circuito.json`, `marca_registrada.json` | Patentes e Registros | **PTT de estrato máximo (T1)** na área de Engenharias |
| Protótipo, piloto, processo ou técnica | `produto.json`, `processo_tecnica.json`, `maquete.json` | Produção Técnica > Produtos Tecnológicos / Processos / Maquetes | Comprovação direta de avanço de TRL e inovação |
| Contrato de licenciamento / transferência | `licenca.json`, `extensao_tecnologica.json` | Licenciamento / Extensão Tecnológica | Impacto econômico e transferência tecnológica |
| Relatório técnico contratual (`EMBRAPII`/`ANP`/`ANEEL`) | `relatorio_tecnico.json`, `trabalho_tecnico.json` | Relatórios Técnicos / Trabalhos Técnicos | Evidência de demanda contratada e impacto no setor produtivo |
| Software de simulação / controle embarcado | `software_registro.json`, `software_sem_registro.json` | Programas de Computador | PTT complementar em automação e engenharia |

---

### Pack 6 — Agrárias, Alimentos & Ambientais

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Ciências Agrárias I (Agronomia, Recursos Florestais, Engenharia Agrícola); Zootecnia e Recursos Pesqueiros; Medicina Veterinária; Ciência de Alimentos; Ciências Ambientais.
- **Periódicos de referência (Qualis A1/A2):** *Field Crops Research*, *Food Chemistry*, *Science of the Total Environment*, *Pesquisa Agropecuária Brasileira (PAB)*, *Industrial Crops and Products*, *Food Research International*, *Agricultural Water Management*, *Journal of Dairy Science*, *Forest Ecology and Management*.

#### 2. Fluxo de etapas
1. **Pré-execução:** planejamento experimental de campo ou laboratório (delineamento **DBCA**, **DIC**, parcelas subdivididas) distribuído em **múltiplas safras (2+ ciclos) e múltiplos locais**; enquadramento regulatório: `ICMBio/SISBIO` (coleta ambiental/fauna/flora), `SisGen` (biodiversidade brasileira), `CEUA` (se zootecnia/veterinária), **CEP/CAAE (obrigatório quando houver análise sensorial de alimentos com provadores humanos)** e planejamento de ensaios de `VCU`/`DHE` junto ao **MAPA** (se cultivar ou bioinsumo).
2. **Execução:** condução de experimentos em estações experimentais/fazendas parceiras com monitoramento edafoclimático contínuo; colheita, pós-colheita e análises bromatológicas, físico-químicas e microbiológicas; **para análise sensorial de alimentos, liberação condicionada à comprovação prévia de segurança microbiológica** do lote; organização de **Datasets Plurianuais** e condução de **Unidades de Referência Tecnológica (URTs)** e **Dias de Campo**.
3. **Validação / Submissão:** análise conjunta de safras e interação genótipo × ambiente; consolidação dos dossiês de registro/proteção no **MAPA (`RNC` / `SNPC` / registro de bioinsumo)**; redação do manuscrito para periódicos A1/A2 (que frequentemente exigem mínimo de 2 safras agrícolas para aceite) com disponibilização de datasets e dados meteorológicos.
4. **Pós-publicação:** publicação de **Boletins Técnicos, Comunicados Técnicos e Circulares** voltados a produtores e extensionistas; transferência de tecnologia em feiras agropecuárias e cooperativas; arquivamento de datasets plurianuais e prestação de contas (`Embrapa`, `CNPq`, `FAPs`, `MAPA`).

#### 3. Papéis dos atores
- **Orientador / PI:** coordena o desenho multi-safra/multi-local, articula estações experimentais (`Embrapa`, universidades, fazendas), assina responsabilidades perante `MAPA`/`SISBIO`/`SisGen`/`CEP` e lidera a transferência ao setor produtivo.
- **Coorientador / Pesquisadores Parceiros:** especialistas em solos, fitopatologia, microbiologia agrícola, estatística experimental, tecnologia de alimentos ou sensoriamento remoto (frequentemente com **>90% de coautoria multi-institucional**).
- **Iniciação Científica (IC):** apoio na condução de parcelas em campo, coleta de amostras de solo/planta/água, preparo de amostras laboratoriais e registro de variáveis fenológicas.
- **Mestrado:** conduz pelo menos 1 a 2 ciclos experimentais completos, analisa dados agronômicos/bromatológicos/ambientais, apoia URTs e defende a dissertação.
- **Doutorado / Pós-Doc:** coordena ensaios multi-locais/multi-safra, integra dados genômicos, climáticos e de campo, prepara dossiês `MAPA`/cultivares e redige artigos de alto impacto.
- **Parceiros Externos:** pesquisadores da **Embrapa**, produtores rurais anfitriões de URTs, cooperativas agroindustriais, empresas de bioinsumos/sementes, órgãos ambientais (`ICMBio`, `IBAMA`, secretarias estaduais) e laboratórios de análise de solo/alimentos.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **MAPA (`RNC`, `SNPC`, `VCU`/`DHE`):** ensaios oficiais de Valor de Cultivo e Uso (`VCU`) e Distinguibilidade, Homogeneidade e Estabilidade (`DHE`) para registro e proteção de cultivares, além de registro de bioinsumos/inoculantes.
- **CEP/CAAE para Análise Sensorial:** todo teste afetivo ou descritivo com provadores humanos exige aprovação prévia em Comitê de Ética (`CEP`), `TCLE` e **laudo microbiológico prévio** comprovando inocuidade da amostra.
- **ICMBio/SISBIO, SisGen e CEUA:** licenças ambientais de coleta, cadastro de acesso ao patrimônio genético e aprovação ética para experimentação animal (zootecnia/veterinária).
- **Rigor Multi-Safra e Georreferenciamento:** periódicos A1 (como *Field Crops Research* e *PAB*) exigem repetição em múltiplas safras/ambientes, coordenadas geográficas, classificação do solo e dados climáticos do período.

#### 5. Evidências e artefatos gerados (além do artigo)
- Certificados de **Cultivar Registrada (`RNC`)** ou **Cultivar Protegida (`SNPC`)**; registros de bioinsumos/produtos no MAPA.
- **Datasets plurianuais** (clima, solo, produtividade, microbioma) e **mapas temáticos/zoneamentos agroclimáticos** (`SIG`).
- **Boletins Técnicos, Circulares Técnicas, Comunicados**, registros fotográficos/listas de presença de **Dias de Campo** e relatórios de **URTs**.
- Laudos microbiológicos + pareceres `CEP` (alimentos), licenças `SISBIO`/`SisGen` e `CEUA`.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 6 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto agronômico / alimentos / ambiental | `projeto.json` (*Pesquisa*, *Desenvolvimento* ou *Extensão*) | Projetos de Pesquisa / Desenvolvimento / Extensão | Articulação em rede (Embrapa/Universidades) e impacto regional |
| Artigo multi-safra / alimentos / ambiental | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Qualis A1/A2 (alta citação internacional) |
| Cultivar protegida ou registrada (MAPA) | `cultivar_protegida.json`, `cultivar_registrada.json` | Patentes e Registros > Cultivar protegida / registrada | **PTT de estrato máximo (T1)** em Ciências Agrárias |
| Bioinsumo, formulação alimentar ou processo | `produto.json`, `processo_tecnica.json`, `patente.json` | Produtos Tecnológicos / Processos ou Técnicas / Patentes | Inovação agroindustrial e transferência de tecnologia |
| Mapa temático / zoneamento ambiental (`SIG`) | `cartas_mapas.json` | Produção Técnica > Cartas, mapas ou similares | Produto técnico especializado em Agrárias e Ambientais |
| Boletim técnico / comunicado / manual ao produtor | `relatorio_tecnico.json`, `material_didatico.json`, `trabalho_tecnico.json` | Relatórios Técnicos / Material didático / Trabalhos técnicos | Forte evidência de impacto econômico, ambiental e social |
| Dia de Campo / URT / transferência rural | `extensao_tecnologica.json`, `organizacao_evento.json`, `curso_ministrado.json` | Extensão tecnológica / Organização de eventos / Cursos | Indicador de inserção social e transferência direta |

---

### Pack 7 — Humanas, Sociais Aplicadas & Artes

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Ciências Humanas (História, Sociologia, Antropologia, Ciência Política, Educação, Psicologia, Filosofia, Geografia Humana); Ciências Sociais Aplicadas (Economia, Direito, Administração, Comunicação, Arquitetura e Urbanismo, Serviço Social); Linguística, Letras e Artes.
- **Periódicos de referência (Qualis A1/A2):** *Dados*, *Revista Brasileira de História (RBH)*, *Educação & Sociedade*, *Psicologia: Reflexão e Crítica*, *Journal of Development Economics (JDE)*, *Revista Direito GV*, *Revista de Administração de Empresas (RAE)*, *DELTA*, *Trabalhos em Linguística Aplicada (TLA)*, *ARS (USP)*, *Horizontes Antropológicos*.

#### 2. Fluxo de etapas
1. **Pré-execução:** estruturação do projeto (frequentemente no modo **Projeto Guarda-Chuva**, no qual 5 a 15 orientandos desenvolvem pesquisas individuais ou em dupla sob um mesmo eixo teórico); enquadramento ético específico pela **Res. CNS nº 510/2016** (Ciências Humanas e Sociais, prevendo registro flexível de consentimento — oral, audiovisual ou escrito — e **Termo de Assentimento** para crianças/adolescentes em escolas); em Economia/Psicologia/Ciência Política, pré-registro no `OSF` ou `AEA RCT Registry`; em História/Artes/Letras, levantamento de acervos, licenças de uso de imagem e direitos autorais.
2. **Execução:** pesquisa documental/arquivística, etnografia, entrevistas em profundidade, pesquisa-ação escolar/comunitária, construção de *corpora* digitais, análise de microdados (`PNAD`, `RAIS`, `Censo Escolar`, jurisprudência) ou processo criativo/curatorial; publicação intermediária de **Working Papers (`SSRN`, `NBER`, textos para discussão)** em Economia/Administração/Direito; organização de seminários internos do grupo e capítulos de **Coletânea Organizada**.
3. **Validação / Submissão:** preparação de manuscritos para periódicos A1/A2 (incluindo **pacote de replicabilidade** em periódicos como *Dados* e *JDE* via `SciELO Data` / `Harvard Dataverse`); **verificação editorial de livro/coletânea com alerta contra endogenia CAPES** (equilíbrio de autores externos ao PPG, conselho editorial qualificado, revisão por pares e ISBN); liberação formal de direitos autorais de imagens, obras de terceiros e traduções.
4. **Pós-publicação:** lançamento de livros/coletâneas (qualificação no **Qualis Livros — L1 a L4**), publicação de *Policy Briefs*, pareceres jurídicos/técnicos e casos de ensino; realização de **exposições, concertos, peças ou curadorias** com documentação comprobatória completa (catálogo, fôlder, registro fotográfico/audiovisual, crítica publicada).

#### 3. Papéis dos atores
- **Orientador / PI:** lidera o **Projeto Guarda-Chuva**, define o marco teórico-metodológico comum, organiza coletâneas e dossiês temáticos (cuidando das regras anti-endogenia da CAPES), conduz negociações com editoras/acervos/instituições culturais e orienta a autoria individual ou em dupla dos discentes.
- **Coorientador / Pesquisadores Parceiros:** colaboram em redes interinstitucionais (essenciais para evitar endogenia em coletâneas e dossiês), codirigem curadorias, *corpora* ou pesquisas comparadas.
- **Iniciação Científica (IC):** levantamento documental/bibliográfico, transcrição e codificação qualitativa, catalogação de acervos/corpora, organização de microdados e apresentações em simpósios temáticos.
- **Mestrado:** desenvolve recorte autoral completo (dissertação + artigo ou capítulo de livro), executa trabalho de campo/arquivo/estúdio e publica frequentemente como autor único ou em dupla com o orientador.
- **Doutorado / Pós-Doc:** realiza tese autoral de fôlego (muitas vezes convertida em livro autoral), lidera frentes de pesquisa internacional/comparada, atua em traduções comentadas, curadorias ou avaliação de políticas públicas.
- **Parceiros Externos:** escolas públicas e secretarias de educação, arquivos históricos, museus, galerias, editoras universitárias/comerciais, órgãos públicos/tribunais (demandas de *policy briefs* e pareceres), coletivos comunitários e movimentos sociais.

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **Res. CNS nº 510/2016 (Ética em CHS):** garante especificidade metodológica para Humanas e Sociais, permitindo dispensa para pesquisas de opinião pública sem identificação, bases públicas e pesquisa teórica/documental, e formas não burocráticas de consentimento (inclusive oral gravado) + **anonimização indireta** de comunidades e escolas.
- **Direitos Autorais e Patrimônio Cultural (Lei nº 9.610/1998):** cessão formal de direitos de imagem, autorização de acervos/arquivos e licenciamento para traduções e obras derivadas.
- **Qualis Livros e Alerta Anti-Endogenia CAPES:** livros e coletâneas precisam de conselho editorial, avaliação por pares, ISBN, ficha catalográfica e proporção adequada de autores externos ao PPG para atingir estratos L1/L2.
- **Replicabilidade Empírica (Sociais Aplicadas / Psicologia / Ciência Política):** depósito de scripts (`R`/`Stata`/`Python`) e dados anonimizados em `SciELO Data`, `OSF` ou `Dataverse`, além de pré-registro (`AEA RCT Registry` / `OSF`).

#### 5. Evidências e artefatos gerados (além do artigo)
- **Livros autorais, coletâneas organizadas, capítulos de livro, prefácios/posfácios e traduções comentadas** (com ISBN, conselho editorial e comprovante de tiragem/distribuição).
- **Working Papers (`SSRN`/`NBER`)**, *Policy Briefs*, pareceres jurídicos/técnicos, relatórios de pesquisa-ação e **casos de ensino** (Administração/Direito).
- ***Corpora* linguísticos digitais**, bancos de microdados tratados e pacotes de replicabilidade (`SciELO Data`/`OSF`).
- **Produção Artística e Cultural:** catálogos de exposição, curadorias, partituras, gravações musicais, espetáculos cênicos, restauração/manutenção de obras e artigos em mídia/imprensa qualificada.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 7 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto Guarda-Chuva / pesquisa / extensão | `projeto.json` (*Pesquisa*, *Extensão* ou *Ensino*) | Projetos de Pesquisa / Extensão / Ensino | Agrega múltiplas teses/dissertações e produções individuais |
| Artigo em periódico A1/A2 | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Estrato Qualis A1/A2 |
| Livro autoral, coletânea organizada ou capítulo | `livro_capitulo.json`, `editoracao.json`, `prefacio_posfacio.json` | Livros e capítulos / Editoração / Prefácio e Pósfacio | **Peso equivalente ou superior a artigo A1 nas áreas de Humanas/Letras (Qualis Livros L1–L4)** |
| Tradução comentada / texto em jornal ou revista | `traducao.json`, `texto_jornal_revista.json`, `outra_producao_bibliografica.json` | Traduções / Textos em jornais ou revistas / Outra prod. bibliográfica | Produção qualificada em Letras, Filosofia, História e Comunicação |
| *Policy Brief*, parecer, caso de ensino, consultoria | `trabalho_tecnico.json`, `relatorio_tecnico.json`, `material_didatico.json` | Trabalhos Técnicos / Relatórios Técnicos / Material Didático | **PTT de alto impacto social e de políticas públicas** |
| Exposições, artes visuais, cênicas, música, partituras | `artes_visuais.json`, `artes_cenicas.json`, `musica.json`, `partitura_musical.json`, `manutencao_obra.json`, `outra_producao_artistica.json` | Produção Artística / Cultural | **Indicador central (equivalente a Qualis) nas áreas de Artes e Música** |
| Organização de simpósios, dossiês e corpos editoriais | `organizacao_evento.json`, `corpo_editorial.json`, `revisor_periodico.json` | Organização de eventos / Membro de corpo editorial / Revisor | Liderança acadêmica e inserção nacional/internacional |

---

### Pack 8 — Big Science, Química & Consórcios

#### 1. Áreas atendidas e periódicos Qualis A1/A2 de referência
- **Áreas CNPq/CAPES:** Astronomia e Física; Química (Orgânica, Inorgânica, Físico-Química, Analítica, Estrutural); Geociências; Oceanografia; Redes Globais e Grandes Consórcios Científicos.
- **Periódicos de referência (Qualis A1/A2):** *The Astrophysical Journal (ApJ)*, *Monthly Notices of the Royal Astronomical Society (MNRAS)*, *Physical Review Letters (PRL)*, *Astronomy & Astrophysics*, *Journal of the American Chemical Society (JACS)*, *Angewandte Chemie*, *ACS Omega*, *Inorganic Chemistry*, *Journal of Physical Chemistry Letters*.

#### 2. Fluxo de etapas
1. **Pré-execução:** submissão de propostas competitivas de tempo em grandes instalações (**telescópios** como `JWST`, `VLT/ESO`, `Gemini`, `SOAR`; aceleradores/síncrotrons como **Sirius/LNLS** ou **CERN**; ou centrais analíticas multiusuário de RMN/Difração de Raios X); formalização de adesão ao **consórcio internacional** e suas regras de política de autoria (*authorship policy*) e período proprietário de dados (*proprietary period*).
2. **Execução:** aquisição de dados observacionais/espectroscópicos ou síntese química e caracterização estrutural completa; redução de dados e simulações em HPC; montagem sistemática do pacote de **Supporting Information (SI)** (espectros de RMN ¹H/¹³C, HRMS, arquivos cristalográficos `CIF`, coordenadas cartesianas `DFT`, tabelas de fotometria/espectroscopia).
3. **Validação / Submissão:** **etapa obrigatória de Revisão Interna do Consórcio** (*Internal Collaboration Review*) com janela de comentários de coautores (frequentemente 10 a 50+ coautores em múltiplos países) *antes* da submissão à revista; depósito simultâneo do **preprint no `arXiv` / `ChemRxiv`**, depósito de **estruturas cristalográficas (`CCDC`)** e publicação do **Dataset com DOI no `Zenodo` / `CERN Open Data`**; submissão ao periódico A1 com *Supporting Information* completa.
4. **Pós-publicação:** vinculação automática do `arXiv` à publicação final com `DOI` (`ADS`/`INSPIRE-HEP`/`Crossref`); liberação pública dos dados após o fim do *proprietary period*; monitoramento de citações internacionais (`Web of Science`, `Scopus`, `NASA ADS`) e prestação de contas às agências (`CNPq`, `FAPs`, `CAPES-PrInt`, acordos internacionais).

#### 3. Papéis dos atores
- **Orientador / PI:** lidera o grupo brasileiro dentro do consórcio internacional, coordena propostas de tempo de observatório/feixe/central analítica, negocia posição de autoria do grupo e revisa rigorosamente os dados e o pacote de *Supporting Information*.
- **Coorientador / Pesquisadores Parceiros:** colaboradores internacionais do consórcio (>90% de coautoria multi-institucional), especialistas em instrumentação, química teórica/computacional (`DFT`) ou astrofísica observacional.
- **Iniciação Científica (IC):** redução preliminar de espectros/imagens, tratamento de curvas, síntese de intermediários sob supervisão e organização de tabelas suplementares.
- **Mestrado:** executa análise de um conjunto específico de objetos/compostos, gera a documentação de *Supporting Information*, apresenta em reuniões do consórcio e redige artigo em colaboração.
- **Doutorado / Pós-Doc:** atua como primeiro autor em artigos de consórcio, participa de turnos de observação/feixe (remotos ou presenciais), desenvolve pipelines de redução de dados e interage diretamente com comitês internos de revisão.
- **Parceiros Externos:** observatórios internacionais (`ESO`, `NOIRLab`, `STScI`), laboratórios nacionais (`LNLS/CNPEM`, `LNA`, `CBPF`), centrais analíticas multiusuário e repositórios científicos globais (`CERN`, `CCDC`, `Zenodo`).

#### 4. Exigências regulatórias, éticas e de reprodutibilidade
- **Política de Autoria e Revisão Interna de Consórcio:** aprovação obrigatória pelo *Publication Board* do consórcio antes de submeter à revista ou ao `arXiv`.
- **Período Proprietário (*Proprietary Period*):** controle de embargo de dados observacionais (normalmente 12 meses) até abertura pública obrigatória nos arquivos do observatório.
- **Padrões de Supporting Information (ACS/RSC/APS/AAS):** validação cristalográfica (`checkCIF` / depósito no `CCDC`), pureza e caracterização completa (RMN, HRMS, IV, análise elementar), coordenadas de cálculos quânticos (`DFT`) e metadados astronômicos padronizados (`FITS`).
- **Segurança Química e Radiológica:** conformidade com normas de controle de reagentes químicos (`Polícia Federal` / `Exército`, quando aplicável), descarte de resíduos químicos e proteção radiológica em linhas de feixe.

#### 5. Evidências e artefatos gerados (além do artigo)
- Propostas aprovadas de tempo de telescópio, síncrotron (`Sirius/LNLS`) ou supercomputação (`SDumont`).
- **Datasets com DOI (`Zenodo`, `CERN Open Data`, `Vizier`)**, códigos/pipelines científicos (`GitHub`/`ASCL`) e arquivos `CIF` depositados no `CCDC`.
- Pacotes completos de **Supporting Information (SI)** e preprints (`arXiv`/`ChemRxiv`) vinculados ao artigo final.
- Relatórios de participação em comitês científicos, revisões de periódicos de topo e missões internacionais de pesquisa.

#### 6. Mapeamento Lattes (CNPq) e Avaliação CAPES/Sucupira
| Artefato do Pack 8 | Spec no LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes | Impacto CAPES / Sucupira |
| :--- | :--- | :--- | :--- |
| Projeto de consórcio / rede internacional | `projeto.json` (*Pesquisa*) | Projetos de Pesquisa | Forte pontuação em **internacionalização** e inserção em redes globais |
| Artigo em periódico A1 (com vínculo `arXiv` → DOI) | `artigo.json` / `artigo_aceito.json` | Artigos completos publicados / aceitos | Estrato Qualis A1 de altíssimo impacto e citações globais |
| Pipeline de redução / código científico | `software_sem_registro.json`, `software_registro.json` | Programas de Computador | PTT de ciência aberta e reprodutibilidade |
| Dataset com DOI (`Zenodo`) / pacote SI / `CIF` | `outra_producao_tecnica.json`, `produto.json` | Produção Técnica > Produtos Tecnológicos / Outra prod. técnica | Evidência de Ciência Aberta e compartilhamento de infraestrutura |
| Instrumentação / método analítico desenvolvido | `processo_tecnica.json`, `patente.json` | Processos ou Técnicas / Patentes | Inovação instrumental e analítica |
| Métricas de citação internacional | `citacao_web_of_science.json`, `citacao_scopus.json`, `citacao_google_scholar.json` | Citações em bases bibliográficas | Indicador de impacto internacional do docente/PPG |
| Revisão de periódicos e projetos internacionais | `revisor_periodico.json`, `revisor_projeto_fomento.json`, `comite_assessoramento.json` | Revisão de periódicos / projetos / Comitês | Reconhecimento científico internacional |

---

## 3. Matriz Consolidada de Mapeamento (Projeto → Lattes → CAPES/Sucupira → Conversão do Aluno)

A tabela a seguir consolida a engenharia de conversão do LattesData: cada artefato produzido dentro de um projeto colaborativo (nos 6 Pilares ou nos 8 Packs) é mapeado simultaneamente para:
1. A **especificação real suportada pelo LattesData** (`itens/especificacao/*.json`);
2. A **categoria oficial do Currículo Lattes (CNPq)**;
3. O **peso e papel na Avaliação Quadrienal CAPES / Plataforma Sucupira**;
4. O **gatilho natural de conversão do orientando** (que colabora **100% grátis** no projeto e converte para o *Plano Estudante* ou *Passe de Atualização / Edital via Pix* quando quer sincronizar suas produções validadas no próprio Lattes ou gerar seu Dossiê/EditalScore).

| Artefato Gerado no Projeto | Packs Principais | Spec LattesData (`itens/especificacao/`) | Categoria no Currículo Lattes (CNPq) | Peso / Papel na CAPES & Sucupira | Gatilho de Conversão do Aluno (*Cofre Pessoal*) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vínculo formal no Projeto** (Pesquisa, Desenv., Extensão, Ensino, Outra) | Todos (Espinha Dorsal) | `projeto.json` | Projetos > Projetos de Pesquisa / Desenvolvimento / Extensão / Ensino | **Estruturante:** amarra Docentes ↔ Discentes ↔ Produções ↔ Financiadores na Sucupira | Aluno vê o projeto oficial validado pelo orientador pronto para entrar no Lattes ao concorrer a bolsa (`PIBIC`/M/D) |
| **Orientação / Coorientação** (IC, TCC, Mestrado, Doutorado, Pós-Doc) | Todos (Espinha Dorsal) | `orientacao_andamento.json`, `orientacao_concluida.json`, `pos_doutorado.json` | Orientações e Supervisões (Em andamento / Concluídas) e Pós-Doutorado | **Alto:** taxa de titulação, tempo médio e distribuição de orientações no PPG | Comprovação imediata de vínculo de orientação/bolsa para processos seletivos e relatórios |
| **Artigo publicado ou aceito em periódico** (com agrupamento PT/EN/ES e `arXiv` → DOI) | Todos (1–8) | `artigo.json`, `artigo_aceito.json` | Produção Bibliográfica > Artigos completos publicados / aceitos em periódicos | **Máximo (Qualis A1–A4):** principal indicador de produção intelectual acadêmica | **Gatilho #1 de conversão:** artigo com DOI e CRediT já preenchido e validado pelo orientador esperando 1 clique para subir no Lattes |
| **Trabalho completo ou resumo em anais de congresso** | Todos (crítico no Pack 4) | `anais.json` | Produção Bibliográfica > Trabalhos publicados em anais de eventos | **Máximo em Computação (Pack 4, A1/A2);** importante para produção discente nas demais áreas | **Gatilho de volume:** após 2–3 congressos, o aluno acumula vários resumos prontos no Cofre e paga para sincronizar tudo de uma vez |
| **Apresentação de trabalho / Pôster / Palestra** | Todos (1–8) | `apresentacao.json`, `participacao_evento.json` | Produção Técnica > Apresentações de Trabalho; Eventos > Participação | Comprova inserção discente e circulação da pesquisa | Certificados de jornadas/congressos sobem no projeto e já pontuam no **EditalScore** para seleção de Mestrado/Doutorado |
| **Livro autoral, Coletânea organizada, Capítulo, Prefácio ou Tradução** | Pack 7 (e Pack 3) | `livro_capitulo.json`, `editoracao.json`, `prefacio_posfacio.json`, `traducao.json` | Produção Bibliográfica > Livros e Capítulos / Editoração / Prefácio / Tradução | **Máximo em Humanas, Sociais e Letras (Qualis Livros L1–L4);** exige checagem anti-endogenia | Capítulo da coletânea do grupo pronto e padronizado (ISBN + organizadores + páginas) no Cofre do orientando |
| **Patente, Desenho Industrial, Marca ou Topografia de Circuito** | Packs 1, 5, 6, 8 | `patente.json`, `desenho_industrial.json`, `marca_registrada.json`, `topografia_circuito.json` | Patentes e Registros | **Máximo em Inovação (PTT T1/T2):** diferencial decisivo em Engenharias, Biotec e Farmácia | Aluno inventor recebe o registro estruturado com número INPI/titularidade para valorizar currículo em concursos e indústria |
| **Programa de Computador (com ou sem registro INPI)** | Packs 3, 4, 5, 8 | `software_registro.json`, `software_sem_registro.json` | Patentes e Registros / Produção Técnica > Programas de Computador | **Alto (PTT T1–T3):** peso expressivo em Computação, Engenharias e PPGs Profissionais | Código/app desenvolvido na dissertação pronto para o Lattes + destaque no Dossiê de seleção/emprego |
| **Cultivar Registrada (`RNC`) ou Protegida (`SNPC` / MAPA)** | Pack 6 | `cultivar_registrada.json`, `cultivar_protegida.json` | Patentes e Registros > Cultivar registrada / protegida | **Máximo (PTT T1)** em Ciências Agrárias | Pesquisador/doutorando registra coinvenção oficial com número MAPA sem risco de erro de preenchimento |
| **PTTs: Cartilha, Manual, App, Protocolo, Vídeo, Curso ou Caso de Ensino** | Packs 2, 3, 6, 7 | `material_didatico.json`, `processo_tecnica.json`, `produto.json`, `curso_ministrado.json` | Produção Técnica > Material Didático / Processos / Produtos / Cursos | **Máximo em Mestrados/Doutorados Profissionais (PTT T1–T3)** e relevante em acadêmicos | Mestrando profissional sai da defesa com o PTT estruturado para Lattes e Dossiê de progressão funcional |
| **Relatório Técnico, Nota Técnica, Parecer, *Policy Brief* ou Relatório de Pesquisa** | Packs 2, 3, 5, 6, 7 | `relatorio_tecnico.json`, `relatorio_pesquisa.json`, `trabalho_tecnico.json` | Produção Técnica > Relatórios / Trabalhos Técnicos | Evidência de impacto social, contratual (`EMBRAPII`/`ANP`/`SUS`) e transferência | Aluno converte para exportar Dossiê PDF numerado comprovando atuação técnica em editais e concursos |
| **Dataset com DOI (`Zenodo`/`SciELO Data`), Mapa (`SIG`), Maquete ou Extensão Tecnológica** | Packs 4, 5, 6, 7, 8 | `cartas_mapas.json`, `maquete.json`, `extensao_tecnologica.json`, `outra_producao_tecnica.json` | Produção Técnica > Cartas e Mapas / Maquetes / Extensão / Outra prod. técnica | Crescente valorização em **Ciência Aberta**, reprodutibilidade e impacto regional | Artefatos técnicos que alunos costumam esquecer de lançar no Lattes já ficam prontos e classificados |
| **Contrato de Licenciamento / Transferência de Tecnologia** | Packs 1, 5, 6 | `licenca.json` | Produção Técnica / Inovação > Licenciamento | **Altíssimo impacto econômico** na avaliação de inovação do PPG | Comprovação de impacto real no mercado para egressos e pós-docs |
| **Obra Artística, Exposição, Curadoria, Espetáculo, Música ou Partitura** | Pack 7 | `artes_visuais.json`, `artes_cenicas.json`, `musica.json`, `partitura_musical.json`, `manutencao_obra.json`, `outra_producao_artistica.json` | Produção Artística / Cultural | **Máximo nas áreas de Artes e Música** (equivalente ao Qualis bibliográfico) | Discente de Artes consolida portfólio comprovado (catálogos/certificados) e sincroniza no Lattes sem retrabalho |
| **Prêmios, Distinções e Menções Honrosas** | Todos (1–8) | `premio.json` | Dados Gerais > Prêmios e Títulos | Indicador de excelência discente e visibilidade do PPG | Certificado de melhor trabalho em congresso gera alto apelo emocional e pontuação direta no **EditalScore** |
| **Bancas, Organização de Eventos, Revisão de Periódicos e Divulgação Científica** | Todos (1–8) | `banca.json`, `banca_comissao_julgadora.json`, `organizacao_evento.json`, `revisor_periodico.json`, `entrevista_midia.json`, `redes_sociais.json` | Bancas / Eventos / Revisão / Mídia e Divulgação | Nucleação, internacionalização e impacto na sociedade (Quesito 3 CAPES) | Doutorandos e pós-docs acumulam bancas de TCC, organização de simpósios e pareceres prontos para concursos docentes |

---

### Síntese Operacional para Produto e Apresentação Acadêmica

1. **Para o Docente / Orientador:** um único ambiente cobre da conformidade prévia (`CEUA`, `CEP/CAAE`, `Dispensa 510`, `SisGen`, `ReBEC`, `PROSPERO`, `NDA/INPI`, `MAPA`) até o **Dossiê de Prestação de Contas** e a sincronização direta com as **64 especificações do Currículo Lattes** — sem perder comprovantes quando os alunos se formam.
2. **Para o Programa de Pós-Graduação (PPG / Sucupira):** elimina divergências de título/autoria entre docente e discente, previne duplicidades multilíngues (PT/EN/ES) e de preprints (`arXiv`/`SSRN`), e estrutura nativamente os **PTTs (T1–T3)** e vínculos **Projeto ↔ Orientação ↔ Produção ↔ Fomento**.
3. **Para o Estudante / Orientando:** entrada **100% gratuita** no projeto do orientador com construção automática do **Cofre Pessoal**; a conversão para *Plano Estudante* ou *Passe via Pix* ocorre de forma orgânica quando o valor já está visível e acumulado (produções validadas prontas para 1 clique no Lattes + Dossiê PDF numerado + EditalScore).
