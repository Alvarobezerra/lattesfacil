# Pré-Requisitos de Privacidade e Sigilo (*Zero-Knowledge* / E2EE) — Gestão de Projetos de Pesquisa

> **Status:** Pré-requisito arquitetural **inegociável** para qualquer implementação da camada de Gestão Colaborativa de Projetos de Pesquisa no **LattesData**.

---

## 1. Princípio Fundamental

> **"Os dados inéditos compartilhados entre orientador, orientandos e parceiros pertencem exclusivamente ao grupo de pesquisa. Nem APIs externas de IA, nem terceiros, nem os próprios operadores do servidor do LattesData podem ter acesso ao conteúdo."**

Na pesquisa científica — especialmente envolvendo resultados inéditos, propriedade intelectual/patentes (**INPI**), contratos sob sigilo (**NDA / EMBRAPII / ANP**), amostras biológicas/biodiversidade (**SisGen**) e dados de participantes humanos (**LGPD / CEP**) — a confiança depende de **garantia criptográfica real**, não apenas de promessa em termos de uso.

---

## 2. Os 6 Pré-Requisitos Obrigatórios da Arquitetura

### Pré-Requisito 1 · Proibição de Envio de Dados Inéditos para APIs Externas de IA
* Nenhum projeto de pesquisa, relatório de aluno, rascunho de manuscrito, dado experimental, protocolo ou conversa orientador ↔ orientando pode ser enviado para APIs externas de Inteligência Artificial.
* A operação do módulo de projetos **não depende** de APIs externas de LLM.

### Pré-Requisito 2 · Criptografia Ponta-a-Ponta (E2EE / *Zero-Knowledge*)
* Todo conteúdo sensível do projeto (arquivos PDF/DOCX, entregas dos alunos, feedbacks, notas metodológicas, comprovantes internos e textos em construção) é **criptografado localmente no navegador/dispositivo do usuário** antes de trafegar pela rede (ex.: `Web Crypto API` com `AES-256-GCM` e chave exclusiva por projeto).
* O servidor do **LattesData** armazena exclusivamente **blocos criptografados indecifráveis** (*ciphertext*), operando sob arquitetura ***Zero-Knowledge***: nem a equipe operadora do servidor nem eventuais invasões ao banco conseguem ler o conteúdo científico.
* O servidor enxerga apenas **metadados mínimos estritamente operacionais** (identificador opaco do projeto, vínculo de membros autorizados, datas de alertas/prazos e flags de status como `pendente`/`aprovado`).

### Pré-Requisito 3 · Separação Estrita entre Cofre Privado e Camada Pública
A plataforma mantém duas fronteiras técnicas claramente isoladas:
1. **Cofre Privado do Projeto (100% E2EE — *Zero-Knowledge*):** proposta do projeto, dados de coleta/bancada, patentes, documentos NDA, rascunhos de artigos/dissertações e trocas entre orientador e orientandos.
2. **Camada Pública / Pós-Publicação (dados já públicos por natureza):** obras já publicadas com **DOI**, registros oficiais no **Crossref/ORCID** e metadados bibliográficos destinados ao **Currículo Lattes público (CNPq)** — liberados somente mediante confirmação explícita do pesquisador.

### Pré-Requisito 4 · Processamento Inteligente 100% Local no Dispositivo do Usuário
* Recursos de apoio como **leitura do PDF/DOCX do projeto**, **detecção automática de Packs e exigências (`CEUA`, `CEP`, `SisGen`, `INPI`)**, **geração do fluxograma de acompanhamento** e extração inicial de cronograma devem executar **localmente na máquina/navegador do usuário** (JavaScript/WebAssembly ou módulo local), antes de qualquer criptografia e envio ao servidor.
* Caso o pesquisador deseje recursos futuros de avaliação linguística ou síntese assistida por IA sobre textos inéditos, isso só poderá ocorrer via **modelos locais rodando no próprio computador do pesquisador** (ex.: `WebGPU` / `Ollama`), preservando **zero saída de dados para nuvens de IA**.

### Pré-Requisito 5 · Governança de Chaves e Continuidade do Grupo
* Cada projeto possui uma **chave criptográfica própria** compartilhada apenas entre os membros ativos autorizados pelo coordenador/orientador.
* Deve existir mecanismo seguro de **chave de recuperação do orientador** (garantindo que a memória do projeto nunca se perca em caso de troca de computador) e **revogação/rotação de acesso** quando um membro deixa o projeto, mantendo o histórico preservado sob controle do coordenador.

### Pré-Requisito 6 · Trilha de Auditoria Imutável, Prova de Anterioridade e Marca d'Água Dinâmica
* **Log Imutável de Auditoria (*Audit Log*):** o sistema registra com carimbo de data/hora e identificação do usuário quem entrou no projeto, quem visualizou ou baixou cada documento, quem criou/editou/aprovou registros e quem revogou acessos — gravando apenas os **metadados do evento** (sem violar o *Zero-Knowledge* do conteúdo).
* **Prova de Anterioridade (`SHA-256`):** cada versão salva de entrega, protocolo ou manuscrito gera uma assinatura criptográfica imutável com data e hora, servindo como evidência rastreável de autoria e anterioridade (inclusive para depósitos no **INPI**).
* **Visualizador Seguro com Marca d'Água Dinâmica (Modo Sigilo):** como navegadores não conseguem impedir fisicamente fotos externas da tela ou capturas do sistema operacional, documentos sensíveis exibem **marca d'água dinâmica** sobreposta com *nome do usuário + data/hora* e registram no log ações de saída (download, cópia, impressão e atalhos de captura) — padrão de *Virtual Data Rooms* de patentes, tornando o ambiente muito mais seguro e rastreável do que pastas em computadores, Drive ou WhatsApp.

---

## 3. Proteção Contra Acesso Administrativo ("E se o operador tentar entrar na conta do pesquisador?")

Uma pergunta frequente de pesquisadores, NITs e comitês de segurança é: *"Mesmo criptografado, o dono do servidor não poderia logar com a minha conta ou adicionar um usuário fantasma para ler meus arquivos?"*

Na arquitetura *Zero-Knowledge* do LattesData, isso é **tecnicamente impedido por 3 barreiras**:

1. **Chave derivada exclusivamente no dispositivo do usuário:** a chave que destranca os projetos nasce localmente no navegador a partir da **Senha-Mestra / Chave de Recuperação** do pesquisador (via `Argon2id` / `PBKDF2`) e **nunca trafega nem é salva no servidor**. Mesmo que um administrador force uma sessão na conta do usuário ou acesse o banco de dados diretamente, sem a senha-mestra local o conteúdo permanece indecifrável.
2. **Impossibilidade de "membro fantasma":** para um novo participante (ex.: orientando) ler o projeto, a chave secreta do projeto precisa ser cifrada com a chave pública desse participante **pelo dispositivo do orientador** no momento da autorização. O servidor, por não possuir a chave do projeto, não consegue conceder acesso criptográfico a terceiros.
3. **Proteção do código cliente (Extensão Assinada / *Open-Source Crypto Core*):** manter o módulo criptográfico enxuto, auditável e — quando possível — embarcado na **extensão assinada do navegador** impede que uma alteração silenciosa no servidor capture a chave no momento do login.

---

## 4. Como Demonstrar e Provar a Criptografia ao Usuário na Interface

Para que o sigilo seja **visível e verificável** (e não apenas um ícone genérico de cadeado):

1. **Chave de Recuperação exclusiva do Orientador:** entregue ao criar o primeiro cofre, com aviso transparente de que nem o suporte do LattesData possui cópia.
2. **Botão "Ver o que o Servidor Enxerga" (Raio-X ao vivo):** compara lado a lado o arquivo/texto decifrado localmente com o bloco cifrado (`AES-256-GCM`) realmente armazenado no servidor — verificável também pelo inspetor de rede (*DevTools*) pela TI da universidade.
3. **Código de Segurança do Projeto (*Fingerprint*):** impressão digital visual da chave que orientador e orientando podem conferir entre si (padrão Signal/WhatsApp).
4. **Selo Clicável de Integridade por Documento:** exibe algoritmo (`AES-256-GCM`), hash `SHA-256`, **Carimbo de Tempo ICP-Brasil** e log de quem acessou.

---

## 5. Trilha de Validação, Auditoria Criptográfica e Selos

| Fase | Validação / Selo | Objetivo e Viabilidade |
| :--- | :--- | :--- |
| **Fase 1 · Curto Prazo (MVP)** | **Carimbo de Tempo ICP-Brasil (ACT/ITI)** + **Módulo Criptográfico Aberto (*Open-Source Crypto Core*)** + **Conformidade LGPD (RIPD/DPO)** + **Padrões NIST (`AES-256-GCM`, `X25519`, `Argon2id`)** | Credibilidade imediata e prova de anterioridade com validade jurídica plena no Brasil (inclusive para **INPI**). |
| **Fase 2 · Médio Prazo (Validação Acadêmica)** | **Auditoria Criptográfica Independente** (ex.: laboratórios públicos de referência como **LabSEC/UFSC**, **LARC/USP**, **LASCA/UNICAMP** ou consultoria AppSec/OWASP ASVS — financiável via editais *FAPEMA/Centelha/Tecnova/FINEP/EMBRAPII* ou cooperação científica) + **Homologação RNP/CAFe** e piloto com **NIT universitário** | Emissão de **Atestado Público de Auditoria *Zero-Knowledge*** com altíssimo peso institucional diante de PPGs e Pró-Reitorias. |
| **Fase 3 · Escala Institucional** | **ISO/IEC 27001** (Segurança) + **ISO/IEC 27701** (Privacidade/LGPD) via organismos acreditados pelo INMETRO + **SOC 2 Tipo II** | Padrão ouro para contratos institucionais com universidades, fundações de amparo e parcerias industriais. |

---

## 6. Posicionamento Estratégico Gerado por Estes Pré-Requisitos

Ao adotar *Zero-Knowledge / E2EE* verificável, trilha de auditoria e carimbo de tempo ICP-Brasil desde a concepção, o **LattesData** se diferencia de ferramentas genéricas de nuvem (Google Drive, Notion, Trello, WhatsApp) e atende diretamente às exigências de **NITs universitários**, **comitês de ética**, **projetos com patentes no INPI** e **parcerias com a indústria**.
