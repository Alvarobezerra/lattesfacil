# Documento de Referência — Sistematização para Correlação (Antigravity × Claude)

- **Data:** 2026-11-20
- **Escopo:** Consolidação sistêmica de 100% da auditoria ao vivo da Plataforma Lattes (**9 abas superiores + 10 ícones do Menu Secundário lateral**) e do app `lattesdata` logado, estruturada especificamente para nortear a **correlação e unificação com o levantamento realizado pelo Claude** (`docs/validacao/`, `docs/campos-lattes/ref/`, `itens/especificacao/`).
- **Regra de ouro para correlação:** Em caso de divergência entre um spec gerado (`itens/especificacao/*.json`), uma captura antiga e o comportamento observado ao vivo, prevalece sempre a **evidência verificada ao vivo no DOM + resposta real do `check()`/`pre_check()` + leitura de volta pós-salvamento (F5)**.

---

## 1. Mapa de Fontes para Cruzamento

| Trilha | Localização no Repositório | Papel na Correlação |
| --- | --- | --- |
| **Levantamento Claude** | `docs/validacao/STATUS.md`, `docs/metodologia-validacao-formularios.md`, `docs/campos-lattes/ref/<item>/`, `itens/especificacao/*.json`, `ferramentas/valida_paridade.py` | Referência de implementação atual (Faixas 1–5, specs gerados, leitores, robô `extensao/autofill_core.js` e suítes `tests/teste_spec_*.py`) |
| **Auditoria Independente Antigravity** | `docs/auditoria-antigravity/` (62 JSONs em `capturas/`, 19 auditorias por seção, 12 fichas F4/F5 + F7, `DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md`, `BACKLOG_TECNICO_FASE2.md`, `RELATORIO_ETAPA4_APP_LOGADO.md`) | Contraprova independente ao vivo de 100% do Lattes (incluindo hidden inputs, lupas, condicionais, salvamento, reabertura persistida e exclusão) |

---

## 2. Tabela-Mestra de Cobertura (100% da Plataforma Lattes)

| # | Aba / Seção do Lattes | Subitens / Variantes | Motores no Lattes | Validação F4/F5 + F7 (Salvar + Reabrir + Excluir) | Documentos de Referência (Antigravity) |
| --- | --- | --- | --- | --- | --- |
| **1** | **Dados Gerais** | 7 subitens | `GN_IDENT`, `GN_ENDERECO`, `GN_LICENCA`, `GN_IDIOMA`, `GN_PREMIO`, `RES`, `GN_OUTRA_INF_RELEV` | ✔ 3/3 listas validadas (`Prêmios`, `Licenças`, `Idiomas`) + 4 formulários únicos inspecionados (hidden + grades + JS) | [auditoria-dados-gerais.md](auditoria-dados-gerais.md) · [ficha-dados-gerais.md](ficha-dados-gerais.md) |
| **2** | **Formação** | 3 subitens (13 variantes) | `GN_FORMACAO2` (`FA` 10 níveis + `AP` 2 níveis) + `PKG_FORMACAO_COMPL` (wizard 2 telas) | ✔ 3/3 validados (`Mestrado`, `Pós-Doutorado`, `Livre Docência` e `Formação complementar` 2 telas) + 4 modos de Doutorado mapeados | [auditoria-formacao.md](auditoria-formacao.md) · [ficha-formacao.md](ficha-formacao.md) |
| **3** | **Atuação** | 7 subitens (hierarquias 2 e 3 níveis) | `GN_ATIV` (`PKG_ATIV.inclui` → `cargos_vinculos` → `pkg_ativ.cargo` 9 naturezas), `PKG_REVISOR` (`MB`, `MA`, `RV`, `RA`), `GN_AREA_ATU` | ✔ Validado nos 3 níveis de `Atuação profissional` (Instituição + Vínculo + Atividade `Ensino`), `Corpo Editorial (MB)` e `Comitê (MA)` | [auditoria-atuacao.md](auditoria-atuacao.md) · [ficha-atuacao.md](ficha-atuacao.md) |
| **4** | **Projetos** | 5 variantes | `pkg_projeto` | Validado pelo Claude (5 variantes); contravalidado por Antigravity via capturas/diff (`f_pais_inst` = 79 países no Lattes vs 244 no spec) | [auditoria-projeto-e-artigo.md](auditoria-projeto-e-artigo.md) · [DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md](DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md) |
| **5** | **Produções** | 30 subitens (11 Bib + 15 Téc + 4 Art) | 8 motores: `PKG_ARTIGO`, `PKG_ARTIGO_PR`, `PKG_LVR_CAP`, `PKG_TRABALHO`/`PKG_TEXTO`, `PRC_BIB_*`, `GN_RELATORIO`/`PRODUTO`/`PROCESSO`, `PRC_TEC_*`, `PKG_ARTE_NOVA` | ✔ Todos os 8 motores validados (`Artigo aceito`, `Livro`, `Capítulo`, `Anais`, `Apresentação`, `Prefácio`, `Trabalhos técnicos`, `Processos`, `Curso curta duração`, `Artes cênicas`) | [auditoria-producoes.md](auditoria-producoes.md) · [ficha-livros-capitulos.md](ficha-livros-capitulos.md) · [ficha-tecnica-e-inovacao.md](ficha-tecnica-e-inovacao.md) · [ficha-artistica.md](ficha-artistica.md) · [validacao-f4-f5-f7-apresentacao-e-anais.md](validacao-f4-f5-f7-apresentacao-e-anais.md) |
| **6** | **Patentes e Registros** | 8 variantes (`PP, PC, PS, CP, CR, DI, MR, TC`) | `PKG_PATENTE_REGISTRO.FORM` (com `infDadPat()` vs abertura direta) | ✔ Validado nos 2 subgrupos (`Marca registrada MR` e `Cultivar protegida CP`) | [auditoria-patentes-registros.md](auditoria-patentes-registros.md) · [ficha-patentes-registros.md](ficha-patentes-registros.md) |
| **7** | **Eventos** | 2 subitens | `PKG_EVENTO.FORM` e `PRC_TEC_ORG` | ✔ 2/2 validados (`Participação em eventos` e `Organização de eventos`) | [auditoria-eventos.md](auditoria-eventos.md) · [ficha-participacao-evento.md](ficha-participacao-evento.md) |
| **8** | **Orientações** | 2 subitens (13 variantes) | `pkg_orient.form` (`f_tipo=C` 7 naturezas; `f_tipo=A` 6 naturezas) | ✔ 2/2 validados (`Concluída`, `Em andamento` c/ 4 lupas e `Outra natureza`) | [auditoria-orientacoes-bancas-citacoes.md](auditoria-orientacoes-bancas-citacoes.md) · [ficha-orientacao.md](ficha-orientacao.md) |
| **9** | **Bancas** | 2 subitens (11 variantes) | `PKG_BANCA_TRAB.form` e `PKG_BANCA_JULG.form` | ✔ 2/2 validados (`Trabalho de conclusão` e `Comissão julgadora`) | [auditoria-orientacoes-bancas-citacoes.md](auditoria-orientacoes-bancas-citacoes.md) · [ficha-bancas.md](ficha-bancas.md) |
| **10** | **Citações** | 5 bases (`1, 2, 3, 4, 99`) | `PRC_INDICADORES` (`prc_indicadores`) | ✔ Validado em `Outras bases (f_base=99)` + inspeção das 5 bases | [auditoria-orientacoes-bancas-citacoes.md](auditoria-orientacoes-bancas-citacoes.md) · [ficha-citacoes.md](ficha-citacoes.md) |
| **11** | **Menu Secundário Lateral** | 10 ícones (`#1`–`#10`) | 5 dicionários (`pkg_dic_*`), `pkg_identificacao_coautor`, `pkg_alteracao_periodico`, `pkg_impcv.*`, `pkg_importa_xml` | ✔ 10/10 inspecionados (somente leitura) + teste dedicado de `Exportar XML` e `Gerar arquivo` | [auditoria-menu-secundario-lateral.md](auditoria-menu-secundario-lateral.md) |

---

## 3. Os 10 Eixos Críticos de Correlação (Pontos Cegos e Divergências para Resolver em Conjunto)

Ao cruzar o material do Claude com o do Antigravity, estes **10 eixos** devem ser verificados obrigatoriamente antes de declarar qualquer item como "fechado":

### Eixo 1 — Catálogos de País e Idioma ("Bug das 80 opções" + `"Canadá"` em Idioma)
- **Divergência:** Em `docs/validacao/STATUS.md`, o Claude anotou `"80 opções reais"` e o `valida_paridade.py` reportou `0 divergências` porque comparou contra capturas truncadas.
- **Realidade ao vivo:**
  - `artigo`, `anais`, `apresentacao`, `orientacao_concluida` e `orientacao_andamento` possuem **`244` países** (`paises-244.json`) e **`152` idiomas** (`idiomas-152.json`) no DOM real do Lattes — hoje os specs têm apenas **80 opções inline**, e `"Canadá"` vazou para dentro de `F_IDIOMA`.
  - **Inverso em `projeto.json`:** o spec usa `paises-244.json`, mas o formulário de Projetos do Lattes só aceita **79 países** (`f_pais_inst`).

### Eixo 2 — Rádios com `value=""` no DOM Real (Armadilha para o Robô)
- **Descoberta ao vivo:** Em vários formulários do Lattes, os `<input type="radio">` possuem **`value=""`** no HTML e são controlados por índice (`0, 1, 2...`) + evento `.click()`:
  - **`Idiomas` (`pkg_idioma.form`):** todos os 4 checkboxes (`FC_LE`, `FC_CONVERSA`, `FC_ESCREVE`, `FC_COMPR`) e os 12 rádios (`F_LE`, `F_CONVERSA`, `F_ESCREVE`, `F_COMPR`) têm `value=""` (e não `"P"`, `"R"`, `"B"` como consta em `idioma.json`). Clicar no rádio pelo índice (`0=Pouco`, `1=Razoavelmente`, `2=Bem`) dispara `rd_*()` e marca o checkbox `FC_*` automaticamente.
  - **Famílias `PRC_BIB_*`, `PRC_TEC_*` e `PRC_TEC_ORG`:** os rádios `F_COD_PROD` (`Prefácio`, `Curso de curta duração`, `Organização de eventos`, etc.) têm `value=""` no DOM — devem ser selecionados por índice/rótulo adjacente + `.click()`.

### Eixo 3 — Códigos de `<select>` com Espaço à Direita Obrigatório
- O robô e o gerador de specs **não podem aplicar `.trim()`** nos `value` de `<option>` de:
  - `Prefácio, posfácio` (`prc_bib_prefacio`): `f_sub_tipo` = **`"31 "` (`Livro`)**, **`"32 "` (`Revistas ou periódicos`)**, **`"33 "` (`Outra`)**.
  - `Bancas de trabalho de conclusão` (`PKG_BANCA_TRAB`): `f_sub_prod` = **`"34 "` (`Acadêmico`)**, **`"35 "` (`Profissional`)**.

### Eixo 4 — Telas, Níveis e Grades Inteiros Ausentes em `itens/especificacao/`
1. **`formacao_complementar.json`:** falta **100% da Tela 2 (`PKG_FORMACAO_COMPL.FORM2`)** (`f_ano_ini`, `f_ano_fim`, `F_BOLSA`, `f_nme_agencia`, `Palavras-chave`, `Visibilidade`) e falta `curso()` em `janelas_auxiliares` da Tela 1.
2. **`atuacao_profissional.json`:** faltam **100% dos Níveis 2 e 3 (`PKG_ATIV.cargos_vinculos` e `pkg_ativ.cargo` — 9 naturezas de atividades)**, incluindo `Ensino` (`f_nivel` `401..409` + `f_curso` + grade `Disciplinas ministradas`) e `Pesquisa e Desenvolvimento` (único lugar para cadastrar `Linhas de pesquisa`).
3. **`endereco.json`:** faltam as 2 grades dinâmicas via modal `.win-wrapper` (`Outra forma de contato` → `f_dados_grid_contatos` e `Redes Sociais` → `f_dados_grid`), além de `f_inst`/`f_orgao` estarem como texto livre em vez de lupas.
4. **`identificacao.json`:** falta a grade `Nome em citações bibliográficas` (`#nmeCitacao` via tecla `Enter` → `#holderDetNmeCit`).
5. **Itens sem arquivo em `itens/especificacao/`:** `assessoria_consultoria`, `linhas_de_pesquisa` e `areas_atuacao`.

### Eixo 5 — Arquitetura das 7 Lupas e Ordem de Dependência
No Lattes, campos com lupa são `disabled` e salvam via **`<input type="hidden">`** preenchidos pelo clique dentro do modal da lupa:
1. **`sele_inst()` / `sele_inst(1..4)`** → `f_cod_inst`, `f_cod_inst2` (e `f_cod_inst_dout*` nos modos `sanduíche` / `co-tutela` / `co-tutela/sanduíche` de Formação — **hoje `autofill_core.js` não cobre `sele_inst(2..4)`**).
2. **`orgao()`** → `f_codorgao`, `f_codorgao2` *(exige `f_cod_inst` preenchido antes)*.
3. **`curso()`** → `f_cod_curso`, `f_cod_curso2` *(exige `f_cod_inst` e `f_nivel`/`F_COD_PROD` preenchidos antes)*.
4. **`agencia()`** → `f_agencia` (`prc_agencia`) ou `f_nme_agencia_h` + `f_cod_inst` (`pkg_revisor.agencia` — **URL diferente em `PKG_REVISOR`**).
5. **`periodico()`** → `f_seq_per`, `f_issn`, `f_issn_h`, `f_nme_agencia_h` (**falta handler dedicado em `autofill_core.js`**).
6. **`dominio()`** → `f_vinculo` / `f_sub_prod` / `f_cod_tipo` (**falta handler dedicado em `autofill_core.js`**; em `Atuação`, `"Outro (especifique)"` destrava `f_vinc.disabled = false`).
7. **`escolhe_inst()`** → `f_cod_inst` dentro do modal `infDadPat()` em Patentes/Registros (`PP, PC, DI, MR, TC`).

### Eixo 6 — Os 3 Padrões de Exclusão no Lattes (Crítico para Automação de Exclusão)
| Padrão | Onde ocorre | Comportamento Exato |
| --- | --- | --- |
| **1. Exclusão imediata (sem confirmação)** | Dentro do formulário aberto em: `Dados Gerais` (`Prêmio`, `Licença`, `Idioma`), `Formação` (todos), `Atuação` (todos os 3 níveis + `PKG_REVISOR`), `Produções` (todos os 8 motores), `Eventos` (2), `Orientações` (dentro do form), `Bancas` (2), `Citações` (`prc_indicadores`) | Clicar em `Excluir` (`del()`) remove imediatamente e exibe toast `"Sucesso / A operação foi realizada com sucesso! !"`. Em `PKG_REVISOR`, remover o único vínculo apaga também o periódico/agência-pai. |
| **2. `window.confirm()` nativo** | Link `Excluir` direto na tabela `pkg_orient.lista` | Dispara `confirm("Deseja excluir o item selecionado?")`. |
| **3. Modal customizado `.caixaMsg`** | **Toda a família `PKG_PATENTE_REGISTRO.FORM`** (confirmado em `Marca registrada MR` e `Cultivar protegida CP`) | Clicar em `Excluir` abre `.caixaMsg` **`"Atenção\nConfirma a exclusão?"`**, exigindo clique no botão de confirmação do modal. |

### Eixo 7 — Regras Condicionais, Validações Exclusivas e Normalizações do Servidor
- **`Artigos aceitos` (`PKG_ARTIGO_PR`):** `f_ano` **não pode ser menor que o ano atual** (`f_ano >= ano_atual`).
- **`Produção Artística` (`PKG_ARTE_NOVA`):** `f_inedito` marcado + `f_dta_ini` preenchida tornam **`f_local_estreia` obrigatório**; `Música` exige `f_form_instr`.
- **`Inovação` (`f_sta_inovacao`):** default `Sim` em `PC` e `DI` (já exige `f_txt_potencial`); default `null` em `PP` (obriga escolher); default `Não` nos demais.
- **`Orientações` (`pkg_orient`):** `Em andamento` tem apenas **6 naturezas** (sem TCC) e exige `f_curso`; `Supervisão de pós-doutorado` bloqueia `f_tpo_orient` via `test_ori()`.
- **`Participação em eventos` (`PKG_EVENTO`):** `F_FORMA` popula `F_TPO`; `Ouvinte` esvazia `F_TPO` e dispensa `F_TPO` e `f_titulo`.
- **`Idiomas` (`pkg_idioma`):** `Libras (LB)` (`veriLibra`) remove `Lê` e `Escreve` do DOM e renomeia `Fala` para `Expressa-se`.
- **`Licenças` (`pkg_licenca`):** todos os 4 campos são obrigatórios (spec marca `false`), default de visibilidade é **`Privado`**, `f_tipo_licenca` altera `#labelDataAdNasc` e `calculaPeriodo()` calcula `#periodoLicenca`.
- **Normalizações do servidor na reabertura (F5):**
  - `f_titulo` em `Apresentação` e `Anais`: converte `"Aspas"` → `'Aspas'`.
  - `f_curso` em `Orientações`, `Bancas` e `Formação`: remove `(CODIGO_CAPES)` / `()` ao reabrir.

### Eixo 8 — Limites Curtos (`maxlength`) que Causam Truncamento/Rejeição
- `maxlength="30"`: `f_cidade_evento` e `f_cidade_ed` (`Anais`), `f_cidade_ed` (`Livro`/`Capítulo`), `f_local` (`Texto jornal/revista`), `f_cidade` (`Partitura`, `Tradução`, `Prefácio`, `Outra bibliográfica`).
- `maxlength="16"`: `f_nme_comum` e `f_nme_cientifico` (`Cultivar protegida`), `f_cod_reg` (`Patentes/Registros`).
- `maxlength="3800"`: `f_ref_en` em `Livro` e `Capítulo` (specs tinham `3900`).
- `maxlength="400"`: `f_titulo` em `Livro` (spec tinha `255`).

### Eixo 9 — Achados do App Logado `lattesdata` (Etapa 4)
- Seletor `#chooserLista` expõe **23 itens** (21 `pronto` no spec novo + 2 `em breve`: `Livros e capítulos` e `Formação acadêmica`), faltando **38 tipos** do universo de 61.
- Labels técnicos crus visíveis na UI (`F_RELEV`, `F_STA_DIVULGACAO_CIENTIFICA`, `F_COD_PROD`, `f_status`), `#gen_F_IDIOMA` como texto livre em `Artigos aceitos`, e `f_dta_inicio` com rótulo errado `"Data Fim"` em `licenca.json`.
- Botão `🚀 Enviar ao Lattes` permite enfileirar `"Sem título"` com obrigatórios vazios e extensão desconectada.
- `GET /api/curriculo/dashboard` retorna `HTTP 409 Conflict` quando não há snapshot de currículo salvo.
- Heurísticas de extração (`POST /api/extract`): página `"193"` vazando em palavras-chave do SEMIC e falha de captura de título/cidade/autor em certificado de apresentação colado como texto.

### Eixo 10 — Infraestrutura CNPq (`pkg_impcv`) e Menu Secundário Lateral
- Os 5 dicionários do menu lateral (`#1 Autores`, `#2 Identificar co-autor`, `#3 Palavras-chave`, `#4 Áreas`, `#5 Instituições`) são a origem real das listas `Listar todos` de todos os formulários do Lattes.
- O ícone `#10 Importar` (`pkg_importa_xml.inicio`) aceita carga em lote por XML aderente à DTD do Lattes.
- Os ícones `#8 Gerar arquivo` (`POST pkg_impcv.trata` → **HTTP 404**) e `#9 Exportar` (`GET pkg_impcv.get_arquivo` → **HTTP 200 `text/html`** recarregando `PKG_MENU.menu`) estão bloqueados/indisponíveis no servidor do CNPq no momento — o que impacta diretamente `lerPaginaNaAba()` em `extensao/background.js`.

---

## 4. Protocolo Prático de Correlação (Passo a Passo para a Fase 2)

Quando formos correlacionar os resultados do Claude com os do Antigravity para aplicar as melhorias no código:
1. **Confrontar `itens/especificacao/<item>.json` com `docs/auditoria-antigravity/capturas/<item>.json` e `auditoria-<secao>.md`:**
   - Corrigir catálogos (`244` países / `152` idiomas vs `79` em Projetos), `maxlength`, `obrigatorio`, `janelas_auxiliares`, espaços à direita e telas/níveis ausentes (`FORM2`, `pkg_ativ.cargo`, grades de `Endereço`/`Identificação`).
2. **Alinhar o gerador (`itens/gerar_specs.py`) e a curadoria (`itens/curadoria.json`):**
   - Eliminar labels crus (`F_RELEV`, `F_COD_PROD`, `f_status`, `FC_*`), consertar rótulos errados (`"Data Fim"` em `f_dta_inicio`, `"Não sei meu CEP"` em `f_cep_*`) e declarar metadados de condicionais/dependências.
3. **Atualizar o robô (`extensao/autofill_core.js`):**
   - Adicionar handlers para `dominio()`, `periodico()`, `sele_inst(2..4)` e `pkg_revisor.agencia`; suportar rádios com `value=""` (seleção por índice/rótulo); suportar inserção em grades via tecla `Enter` (`#nmeCitacao`, `f_espec_l`); e suportar exclusão via `.caixaMsg` em `PKG_PATENTE_REGISTRO`.
4. **Atualizar a UI e o extrator (`static/app.js`, `extractor.py`, `server.py`):**
   - Validar campos obrigatórios antes de enfileirar em `🚀 Enviar ao Lattes`, expor gradualmente os 38 itens restantes no `#chooserLista`, corrigir o `HTTP 409` de `/api/curriculo/dashboard` (estado vazio amigável) e ajustar as regex de certificado/SEMIC.
5. **Revalidar de ponta a ponta:**
   - Rodar a suíte de testes (`tests/teste_spec_*.py` + `ferramentas/valida_paridade.py` corrigido para comparar contra os catálogos reais 244/152) e validar no app logado com a extensão ativa.
