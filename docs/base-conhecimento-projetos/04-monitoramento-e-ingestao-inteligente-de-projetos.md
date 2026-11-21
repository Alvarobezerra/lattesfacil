# Monitoramento de Processos & Ingestão Inteligente de Projetos — LattesData

> **Propósito:** definir como o **LattesData** elimina a *"síndrome da tela em branco"* ao criar projetos (lendo diretamente o PDF/DOCX do projeto submetido) e como oferece **monitoramento leve, preventivo e orientado a resultados** sem transformar a rotina científica em burocracia corporativa.

---

## 1. Ingestão Inteligente do Projeto (Upload PDF/DOCX → Sistemática Proposta)

A principal causa de abandono de ferramentas de gestão na academia é obrigar o pesquisador a redigitar tudo o que já escreveu na proposta enviada à agência de fomento (`FAPEMA`, `CNPq`, `CAPES`, `FINEP`), ao PPG ou à Plataforma Brasil.

No **LattesData**, o onboarding do projeto segue o mesmo princípio do cadastro de evidências no currículo: **o pesquisador sobe o documento; o sistema lê, estrutura e propõe — preservando a decisão humana**.

### Fluxo em 4 Etapas

1. **Upload Único do Projeto (PDF ou DOCX):** o orientador envia o projeto aprovado (ou minuta avançada) ou importa projetos já listados no XML do seu Lattes.
2. **Leitura e Diagnóstico Baseado nos 8 Packs:** o motor analisa o texto, as tabelas e o cronograma para extrair automaticamente:
   - **Identidade & Vigência:** título, objetivos gerais/específicos, natureza (*Pesquisa, Extensão, Ensino, Desenvolvimento Tecnológico*) e período de execução.
   - **Detecção Automática de Pack(s) e Compliance:**
     - Menção a modelos animais (*camundongos, ratos, biotério*) → sugere **Pack 1** + alerta de `CEUA` e checklist `ARRIVE`.
     - Menção a biodiversidade brasileira (*babaçu, Melipona, flora/fauna nativa, CTA*) → sugere `SisGen` e, se houver coleta em campo/UC, `SISBIO/ICMBio`.
     - Menção a pacientes, entrevistas, questionários ou análise sensorial de alimentos → sugere `CEP/Plataforma Brasil (CAAE)` (ou `Dispensa Res. 510/2016` se usar apenas dados públicos como `DATASUS/SINAN/IBGE`).
     - Menção a revisão sistemática/escopo → sugere **Pack 3** (`PROSPERO`/`OSF` + `PRISMA`).
     - Menção a software, app, formulação, bioproduto ou parceria empresarial → sugere **Gate de Patente / Registro de Software (INPI)** e, se aplicável, controle de `NDA/Embargo` e `TRL`.
     - Menção a código/datasets/conferências → sugere **Pack 4** (*Reproducibility Checklist*, GitHub/Zenodo).
     - Menção a safras/parcelas/cultivares → sugere **Pack 6** (calendário multi-safra, `MAPA`).
     - Menção a arquivos históricos, coletâneas, etnografia ou working papers → sugere **Pack 7** (*Projeto Guarda-Chuva*, `Res. 510`, gestor de capítulos).
   - **Cronograma → Marcos de Acompanhamento:** converte a tabela de atividades/meses do documento em marcos datados na linha do tempo do projeto.
   - **Metas Prometidas → Termômetro de Edital:** identifica quantidades previstas de artigos, orientações (IC/Mestrado/Doutorado), patentes, PTTs e relatórios.
   - **Equipe & Fomentos:** identifica coordenador, parceiros, perfis de bolsistas e número do processo/edital.
3. **Proposta Editável de Sistemática (Ajuste antes de Ativar):**
   Antes de criar o espaço, o sistema exibe uma tela de confirmação editável:
   - *Fases e marcos sugeridos* (ajustar datas, renomear ou agrupar);
   - *Packs e alertas regulatórios detectados* (ligar/desligar módulos);
   - *Cadência de check-in dos alunos* (semanal, quinzenal ou mensal — ou apenas por marco);
   - *Metas do edital* (confirmar produtos esperados para prestação de contas).
4. **Ativação + Convite Gratuito dos Alunos:** em 1 clique, o Espaço do Projeto nasce pronto e gera o link de convite gratuito para os orientandos e docentes parceiros.

---

## 2. Seção "Projeto em Progresso": Etapas Cadastradas & Variáveis de Monitoramento

No centro da tela de gestão do projeto, o orientador e os alunos acompanham o andamento real por meio de **dois componentes integrados** (gerados automaticamente na leitura local do PDF do projeto e totalmente editáveis):

1. **Etapas Cadastradas com Progresso e Dependências:**
   - Cada etapa do cronograma possui: *nome*, *responsável(is)*, *prazo*, *percentual concluído*, *status* (`Concluída`, `Em curso`, `Bloqueada`, `Aguardando`) e *evidência vinculada*.
   - Exemplo real (*Projeto Babaçu / LaFIT*): `1. Coleta & Padronização (100%)` → `2. Extração & Caracterização HPLC (100%)` → `3. Ensaios Biológicos & Citotoxicidade (65%)` → `4. Formulação & Gate Patente INPI (20%)` → `5. Redação & Prestação de Contas (Aguardando)`.
2. **Variáveis de Monitoramento (Customizáveis por Área / Pack):**
   - Além do percentual subjetivo, cada etapa pode acompanhar **variáveis objetivas de progresso** (*meta vs. realizado*):
     - *Bancada / Farmácia:* `Amostras / N experimental (24/36)`, `Ensaios validados (7/10)`, `Estabilidade em dias (30/90d)`.
     - *Clínicos / Saúde Coletiva:* `Participantes recrutados (n)`, `Artigos triados no PRISMA`, `Juízes validadores (IVC)`.
     - *Agrárias / Alimentos:* `Safras concluídas`, `Parcelas colhidas`, `Análises sensoriais`.
     - *Computação / Engenharias:* `Benchmarks/Seeds rodados`, `Nível TRL (1–9)`, `Testes HIL`.
     - *Humanas / Sociais:* `Arquivos consultados`, `Entrevistas transcritas`, `Capítulos entregues`.
   - Variáveis transversais automáticas: *desvio de prazo (dias)* e *taxa de check-ins da equipe*.

---

## 3. Os 5 Recursos Complementares de Monitoramento de Processos Científicos

Projetados para dar **visibilidade imediata ao orientador** sem sobrecarregar os orientandos com planilhas ou microgerenciamento:

| Recurso | Como funciona na prática | Valor para o Orientador | Cuidado Anti-Burocracia (Aluno) |
| :--- | :--- | :--- | :--- |
| **1. Semáforo de Saúde + Check-in Assíncrono (2 min)** | O aluno responde periodicamente 3 campos curtos (*Avancei em… · Travado em… · Próximo passo*) e anexa evidência se houver. O projeto exibe status visual (`Em dia`, `Atenção`, `Bloqueado`). | Em 5 segundos, enxerga quais dos seus 5–10 projetos precisam de destrave, sem reuniões longas só para cobrar status. | Leva menos de 2 minutos, substitui cobranças soltas no WhatsApp e funciona bem no celular. |
| **2. Radar de Prazos Críticos & *Gates* de Proteção** | Alertas preventivos para vencimento de `CEUA`, `CEP/CAAE`, `SISBIO`, vigência de bolsas e entrega de relatórios de fomento (`FAPs/CNPq/CAPES/FINEP`), além de *gates* antes de submeter artigos (*SisGen? Patente INPI? Funding completo?*). | Evita perda de prazo de bolsa/edital, rejeição editorial por falta de protocolo ou perda de novidade de patente. | O sistema avisa apenas nos momentos críticos (sem spam diário de notificações). |
| **3. Esteira Editorial (Funil de Produtos)** | Visualização de cada artigo, conferência, livro, patente ou PTT nas etapas: `Dados` → `Rascunho` → `Revisão Orientador` → `Gate PI/Compliance` → `Submetido` → `Revisão/Rebuttal` → `Aceito` → `Publicado (DOI)` → `Lattes`. | Identifica gargalos reais (ex.: *manuscrito parado há 35 dias aguardando coautor ou resposta da revista*). | Dá clareza ao aluno sobre onde está o texto dele e qual é a próxima ação esperada. |
| **4. Termômetro de Metas por Edital** | Cruza a **Carteira de Fomentos (N:N)** com os produtos entregues: mostra *Previsto vs. Realizado* por processo (`FAPEMA APP`, `Universal CNPq`, `FINEP`, `CAPES`). | Elimina o susto na semana de fechar a prestação de contas do edital ou o relatório quadrienal da **Sucupira**. | Alimentado automaticamente pelas entregas já feitas — zero preenchimento duplicado. |
| **5. Monitor de Evidências & Cobertura no Lattes** | Painel de integridade do grupo: quantas entregas já têm **PDF comprobatório arquivado**, quantas já estão no **Lattes do Orientador** e quantas já foram **sincronizadas pelos alunos**. | Garante que nenhum comprovante se perca quando o aluno se forma e elimina divergências de grafia na Sucupira. | Mostra ao aluno o **Cofre Pessoal cheio** de itens prontos para o CNPq (gatilho natural de conversão). |

---

## 3. Regra de Calibração (O que Evitar)

- **Nunca impor microgerenciamento por hora trabalhada** (time-tracking ou quadros rígidos de dezenas de subtarefas diárias): ciência tem incerteza experimental, dependência de reagentes, safra, comitê de ética e revisão por pares.
- **Monitorar por Marcos, Evidências e Desbloqueios:** o foco do monitoramento no LattesData é **proteger o pesquisador contra esquecimentos caros** (prazos, protocolos, comprovantes, fomentos) e **transformar o avanço real do projeto em trajetória reconhecida**.
