# Relatório da Etapa 4 — Auditoria Ponta-a-Ponta do App Logado (`lattesdata`)

- **Data:** 2026-11-20 · **Ambiente auditado:** `http://127.0.0.1:8765` (usuário autenticado: `Álvaro Antônio Bezerra dos Santos`)
- **Regra de isolamento:** Nenhum código ou registro pré-existente do usuário foi alterado (`Registros 53` preservado intacto).

---

## 1. Visão Geral da Sessão Logada e Infraestrutura

1. **Login (`/login` → `/abertura.html` → `/`):**
   - Autenticação com código de acesso (`.acesso`) funcional.
   - **Falha de API detectada em `/abertura.html`:** `GET /api/curriculo/dashboard` retorna **`HTTP 409 Conflict`**.
   - **Aviso de versão em execução no rodapé:** o próprio app exibe alerta de que o processo `python server.py` ativo na porta `8765` foi iniciado antes das últimas edições em disco (`"O servidor está rodando com código antigo: as mudanças do projeto só valem depois de reiniciá-lo"`).
2. **Conexão com Extensão / Lattes:**
   - No navegador de auditoria (sem a extensão Chrome instalada), o cabeçalho indica **`Lattes desconectado`** (`GET /api/lattes/status?sid=...` → `{"seen": false}`) e exibe banner para download (`/api/extensao.zip`).
3. **Falha de validação pré-envio (`🚀 Enviar ao Lattes`):**
   - Ao clicar em **`🚀 Enviar ao Lattes`** mesmo com **`Lattes desconectado`** e **todos os campos obrigatórios vazios** (testado em `Trabalhos publicados em anais de eventos`), o app **não bloqueia nem valida os campos obrigatórios (`obrigatorio: true`) no cliente**: ele enfileira imediatamente um envio `"Sem título"` com status `"⏳ Enviando — Enviado à extensão; aguardando o Lattes."` (o item de teste foi removido em seguida via `DELETE /api/lattes/envios/58fdfd02579d`, restaurando `Registros 53`).

---

## 2. Cobertura do Seletor de Tipos (`#chooserLista`) vs Universo de 61 Itens

Dos **61 itens** mapeados na Plataforma Lattes, o seletor `#chooserLista` do app expõe atualmente **23 itens** (**21 `pronto`** + **2 `em breve`**), todos os 21 renderizando via **spec novo** (`#genModo`, zero formulários legados `[data-tipos]` visíveis):

| # | Item em `#chooserLista` | Badge no App | Motor de Renderização | Observações da Auditoria |
| --- | --- | --- | --- | --- |
| 1 | Trabalhos publicados em anais de eventos | `pronto` | Spec novo (`#genModo`) | `País` e `Idioma` truncados em **80 opções** (`81` c/ `—`); `"Canadá"` aparece na lista de idiomas |
| 2 | Apresentação de trabalho e palestra | `pronto` | Spec novo (`#genModo`) | `País` e `Idioma` truncados em **80 opções**; `"Canadá"` aparece na lista de idiomas |
| 3 | Participação em eventos, congressos, exposições, feiras e olimpíadas | `pronto` | Spec novo (`#genModo`) | — |
| 4 | Organização de eventos, congressos, exposições, feiras e olimpíadas | `pronto` | Spec novo (`#genModo`) | — |
| 5 | Artigos completos publicados em periódicos | `pronto` | Spec novo (`#genModo`) | Possui busca por DOI e busca Crossref/OpenAlex; `Idioma` com **80 opções** |
| 6 | Artigos aceitos para publicação | `pronto` | Spec novo (`#genModo`) | `#gen_F_IDIOMA` renderiza como `<input type="text">` em vez de `<select>`; exibe labels técnicos crus `F_RELEV` e `F_STA_DIVULGACAO_CIENTIFICA` |
| 7 | Livros e capítulos | `em breve` | Bloqueado na UI | Exibe aviso de que o preenchimento automático ainda não está pronto |
| 8 | Orientações e supervisões concluídas | `pronto` | Spec novo (`#genModo`) | 24 campos no spec novo (`País` e `Idioma` com 80 opções) |
| 9 | Orientações e supervisões em andamento | `pronto` | Spec novo (`#genModo`) | 24 campos no spec novo (`País` e `Idioma` com 80 opções) |
| 10 | Participação em bancas de trabalhos de conclusão | `pronto` | Spec novo (`#genModo`) | — |
| 11 | Curso de curta duração ministrado | `pronto` | Spec novo (`#genModo`) | Exibe labels técnicos crus `F_COD_PROD`, `F_RELEV`, `F_STA_DIVULGACAO_CIENTIFICA` |
| 12 | Formação complementar | `pronto` | Spec novo (`#genModo`) | No Lattes real é wizard em 2 etapas (`FORM` → `FORM2`) |
| 13 | Formação acadêmica/titulação | `em breve` | Bloqueado na UI | Exibe aviso de "em breve" |
| 14 | Atuação profissional | `pronto` | Spec novo (`#genModo`) | — |
| 15 | Revisor de periódico | `pronto` | Spec novo (`#genModo`) | — |
| 16 | Membro de corpo editorial | `pronto` | Spec novo (`#genModo`) | Exibe label técnico cru `f_status` (`S`/`N`), contador `"3 de 15 campos principais"` incompatível com o total de campos e alerta `"Função no corpo editorial não identificada"` sem campo correspondente |
| 17 | Patente | `pronto` | Spec novo (`#genModo`) | — |
| 18 | Programa de Computador Registrado | `pronto` | Spec novo (`#genModo`) | — |
| 19 | Prêmios e títulos | `pronto` | Spec novo (`#genModo`) | No spec do app usa `f_nme_prem`/`f_entidade`, enquanto o Lattes real (`pkg_premio.form`) usa `f_titulo`/`f_agencia` |
| 20 | Projetos de pesquisa | `pronto` | Spec novo (`#genModo`) | — |
| 21 | Idiomas | `pronto` | Spec novo (`#genModo`) | — |
| 22 | Licença Maternidade, Paternidade e Adoção | `pronto` | Spec novo (`#genModo`) | No Lattes real (`pkg_licenca.form`) os campos são `f_tipo_licenca`, `f_dta_inicio`, `f_dta_fim`, `f_dta_nasc_adoc` (visibilidade padrão `Privado`) |
| 23 | Trabalhos técnicos | `pronto` | Spec novo (`#genModo`) | — |

- **38 itens restantes do universo de 61** (incluindo `Marca registrada`, `Produção artística`, `Bancas de comissões julgadoras`, `Texto em jornal/revista`, `Tradução`, `Partitura`, etc.) **ainda não estão expostos** em `#chooserLista`.

---

## 3. Testes de Extração e Classificação na UI

### 3.1 Exemplo nativo `⚡ Carregar Exemplo (SEMIC UFMA)`
- **Classificação:** `Trabalhos publicados em anais de eventos` (abre direto no formulário do **spec novo** `#genModo`).
- **Campos extraídos corretamente:** `Natureza = Resumo`, `Título`, `País = Brasil`, `Idioma = Português`, `Meio = meio digital`, `Classificação = Local`, `Nome do evento`, `Página inicial/final = 193`, `Autores` (2 autores formatados), `Áreas = Bioquímica`.
- **Defeitos observados:**
  1. O número da página (`"193"`) vazou para dentro da lista de **Palavras-chave** (`Babaçu`, `Peroxidação lipídica`, `In silico`, `193`).
  2. Campos obrigatórios do Lattes (`Ano *` do trabalho, `Ano *` do evento e `Título dos anais do evento *`) ficaram em branco.

### 3.2 Extração por Texto de Evidência (`POST /api/extract`)
- **Entrada testada:** `"Certificamos que Álvaro Antônio Bezerra dos Santos apresentou o trabalho intitulado 'Análise de Sistemas Térmicos' no XXV Congresso Brasileiro de Engenharia em 2024, em São Luís - Brasil."`
- **Classificação:** `Apresentação de trabalho e palestra` (`confiança: 0.95`, com sugestão secundária de `Participação em eventos`).
- **Defeitos observados no extrator (`extractor.py` / `itens/leitores`):**
  1. **`Título *` ficou vazio no formulário:** `extracted.titulo` recebeu o nome do evento (`"XXV Congresso Brasileiro de Engenharia em 2024"`) em vez do título entre aspas após `intitulado` (`"Análise de Sistemas Térmicos"`).
  2. **`Nome do evento` incluiu o sufixo `"em 2024"`** (`"XXV Congresso Brasileiro de Engenharia em 2024"`).
  3. **`Cidade` ficou vazia** (não extraiu `"São Luís"` antes de `"- Brasil"`).
  4. **`Autores` ficou vazio** e disparou falso positivo de conformidade: `"ATENÇÃO: Álvaro Antônio Bezerra dos Santos não aparece entre os autores deste certificado"`.

---

## 4. Resumo dos Bloqueadores Reais Identificados na Etapa 4 (Para Fase 2)

1. **Catálogos truncados em 80 opções + `"Canadá"` em `F_IDIOMA`** nos specs de `artigo`, `anais`, `apresentacao`, `orientacao_concluida` e `orientacao_andamento`.
2. **Nomes de campos divergentes do DOM real do Lattes** em itens não-convertidos (ex.: `premio` usa `f_titulo`/`f_agencia` no Lattes real vs `f_nme_prem`/`f_entidade` no spec; `licenca` usa `f_tipo_licenca`/`f_dta_inicio`/`f_dta_fim`/`f_dta_nasc_adoc`).
3. **Labels técnicos crus expostos na UI** (`F_RELEV`, `F_STA_DIVULGACAO_CIENTIFICA`, `F_COD_PROD`, `f_status`) em `Artigos aceitos`, `Curso de curta duração ministrado` e `Membro de corpo editorial`.
4. **Falta de validação de campos obrigatórios no botão `🚀 Enviar ao Lattes`** (permite enfileirar envio `"Sem título"` mesmo com obrigatórios vazios e extensão desconectada).
5. **Heurísticas de extração (`extractor.py` / `certificado.py`):** captura de título após `"intitulado '...' "`, limpeza de `"em <ANO>"` no nome do evento, extração de cidade `"em <CIDADE> - Brasil"`, reconhecimento do titular após `"Certificamos que <NOME>"` e filtro de números isolados (página `"193"`) nas palavras-chave do SEMIC.
6. **`GET /api/curriculo/dashboard` retornando `HTTP 409 Conflict`** em `/abertura.html`.
