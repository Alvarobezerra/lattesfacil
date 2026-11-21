# Briefing de Retomada (Handoff) — Construção do Ambiente "Gestão de Processos de Pesquisa" na Plataforma LattesData

> **Use este documento para iniciar uma nova conversa limpa** focada exclusivamente em implementar o ambiente de **Gestão de Processos / Projetos de Pesquisa Científica** dentro da plataforma **LattesData**.

---

## 1. Decisões Já Consolidadas (Não Precisa Rediscutir)

1. **Propósito & Modelo de Negócio (*Hub-and-Spoke*):**
   - **Orientador / Coordenador (Plano Pro — Pagante):** cria projetos, convida alunos gratuitamente, acompanha etapas/variáveis, aprova entregas em 1 clique (propagando para o Dossiê e para o próprio Lattes) e gera prestação de contas (`FAPs`, `CNPq`, `CAPES/Sucupira`, `FINEP`).
   - **Orientando Convidado (Gratuito no Projeto):** interage, envia entregas/arquivos, atualiza check-ins e vê seu **Cofre Pessoal** crescer sem barreira.
   - **Conversão do Aluno:** quando desejar sincronizar automaticamente suas entregas validadas com o próprio Currículo Lattes ou montar dossiê pessoal (`EditalScore`), ativa o **Plano Estudante** ou **Passe de Atualização via Pix**.
2. **Arquitetura Empírica (13 Pesquisadores nas 8 Grandes Áreas + Periódicos Qualis A1/A2):**
   - **Espinha Dorsal Universal (6 Pilares):** Identidade & Natureza · Equipe & Papéis por Projeto · Carteira de Fomentos (N:N) · Marcos & Pastas Permanentes · Produtos/CRediT/Versões (`Preprint → Final`, `PT/EN/ES`) · Motor de Propagação 1-para-N para o Lattes.
   - **8 Packs Modulares por Especialidade:** *Pack 1 (Bancada/Farmácia)*, *Pack 2 (Ensaios Clínicos)*, *Pack 3 (Saúde Coletiva/Revisões/PTT)*, *Pack 4 (Computação/IA)*, *Pack 5 (Engenharias/Indústria/TRL)*, *Pack 6 (Agrárias/Alimentos/Ambientais)*, *Pack 7 (Humanas/Sociais/Artes)*, *Pack 8 (Big Science/Química)*.
   - **MVP Prioritário:** Espinha Dorsal + **Packs 1 e 3** (perfil real do PPGST/UFMA — Prof. Aramys e colegas).
3. **Pré-Requisitos Inegociáveis de Sigilo (*Zero-Knowledge* / E2EE):**
   - Proibição de envio de dados inéditos para APIs externas de IA.
   - Criptografia ponta-a-ponta no navegador (`Web Crypto API` · `AES-256-GCM`, `X25519`, `Argon2id/PBKDF2`): **nem os operadores do servidor do LattesData leem o conteúdo**.
   - Mobilidade total (outro PC/celular) via *chaveiro criptografado* destrancado localmente com Senha-Mestra; continuidade após formatação; **Kit de Emergência em PDF gerado localmente no navegador (nunca enviado por e-mail)**.
   - **Audit Log imutável** (metadados de acesso/ações), prova de anterioridade (`SHA-256` + Carimbo de Tempo ICP-Brasil), **marca d'água dinâmica** no modo sigilo e botão **`🔍 Ver no servidor`** (Raio-X ao vivo).
   - Leitura de PDF/DOCX do projeto (para propor etapas, variáveis e Packs) executada **100% localmente** antes da cifragem.
4. **Design de Interface Aprovado pelo Usuário:**
   - **Tela Inicial (Hub Estilo Netflix):** fundo **branco limpo**, destaque principal (*Hero*) do projeto em foco e trilhos horizontais (*Projetos que Coordeno* · *Projetos em que Colaboro como Parceiro*) com **encartes fotográficos *full-bleed*** (sem degradês CSS problemáticos sobre fotos), barra de progresso, semáforo e card `+ Novo Projeto via PDF`.
   - **Tela Interna Oficial (Opção 2 — Kanban Científico + Pastas E2EE):**
     - Topo com selo `🔒 E2EE Zero-Knowledge`, `🔍 Ver no servidor`, `📋 Copiar Funding`, `📦 Baixar Dossiê ZIP`, `+ Nova Entrega`.
     - Faixa clicável das **6 Pastas Otimizadas** (`Todas`, `02 · Ética`, `03 · Etapas`, `04 · Congressos`, `05 · Artigos/INPI`, `06 · Contas`).
     - Faixa de **Variáveis de Monitoramento editáveis** (`Progresso Geral`, `Amostras / N exp.`, `Protocolos validados`, `Meta do Edital`).
     - **Quadro Kanban de 4 colunas** (`A Fazer` · `Em Execução` · `Revisar / Aprovar` com botão `✓ Aprovar → Lattes` · `Concluído / Lattes`).
     - Rodapé com **Audit Log**, **Compliance** e alternador **Visão Orientador ↔ Visão Aluno Convidado (Grátis)**.

---

## 2. Arquivos de Referência Já Prontos no Repositório

* **Arquitetura geral e modelo de dados:** [arquitetura-projetos-pesquisa-lattesdata.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/arquitetura-projetos-pesquisa-lattesdata.md)
* **Base de Conhecimento completa:**
  * [01-fichas-8-packs-e-matriz-lattes.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/01-fichas-8-packs-e-matriz-lattes.md)
  * [02-benchmark-plataformas-globais.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/02-benchmark-plataformas-globais.md)
  * [03-estudos-de-caso-aramys-e-template.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/03-estudos-de-caso-aramys-e-template.md)
  * [04-monitoramento-e-ingestao-inteligente-de-projetos.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/04-monitoramento-e-ingestao-inteligente-de-projetos.md)
  * [05-prerequisitos-sigilo-zero-knowledge.md](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/05-prerequisitos-sigilo-zero-knowledge.md)
* **Referências Visuais Aprovadas:**
  * [resumo-executivo-projetos-lattesdata.html](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/resumo-executivo-projetos-lattesdata.html) e `.pdf` (8 páginas: Página 6 = Hub Netflix fundo branco; Página 7 = Kanban Científico)
  * [tela-interna-opcao2-kanban.html](file:///C:/Users/icrim/Downloads/Projeto/lattes-facil/docs/base-conhecimento-projetos/tela-interna-opcao2-kanban.html) e `.pdf`
  * Capas em `docs/base-conhecimento-projetos/img/`
* **Restrições Técnicas do Servidor (`server.py`):**
  * **CSP rígida (`script-src 'self'`):** toda tela em `static/` deve usar **JavaScript externo** (zero `<script>` inline!) e evitar `innerHTML` com dados de usuário (usar `textContent` / criação segura de DOM).
  * **Git no Windows:** usar `& "C:\Program Files\Git\cmd\git.exe"` (pois `C:\Windows\System32\git` é um stub).
  * **Testes:** rodar individualmente (`python tests/teste_curriculo_store.py`, `python tests/teste_seguranca.py`, etc.), nunca via `unittest discover`.

---

## 3. Escopo Inicial Sugerido para a Nova Sessão (Implementação na Plataforma)

1. **Backend (`projetos_store.py` + rotas em `server.py`):** tabelas SQLite para projetos, pastas/entregas cifradas (E2EE payload + metadados mínimos), cards Kanban, variáveis de monitoramento, carteira de fomentos (N:N), audit log e convites de alunos.
2. **Frontend na Plataforma (`static/projetos.html`, `static/projetos.js`, `static/projetos.css`):**
   - Tela 1: **Hub Estilo Netflix** (fundo branco, Hero, trilhos *Coordeno* e *Colaboro*, botão `+ Novo Projeto via PDF` com leitor local);
   - Tela 2: **Workspace Kanban Científico** (6 pastas clicáveis, 4 colunas com movimentação de cards, variáveis editáveis, modal `🔍 Ver no servidor` E2EE, Audit Log, aprovação `✓ Aprovar → Lattes` e alternador `Visão Orientador / Aluno`);
   - Link no menu de navegação principal (`abertura.html`, `index.html`, `meu-curriculo.html`, `auditoria.html`, `painel.html`) para **"Gestão de Processos / Projetos"**.
3. **Módulo Criptográfico Cliente (`static/projetos-e2ee.js`):** implementação limpa usando `Web Crypto API` (`AES-256-GCM`, derivação local de chave via `PBKDF2`, Kit de Emergência em PDF local e visualização de *ciphertext*).
