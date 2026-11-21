# Metodologia de validação dos formulários (LattesFácil × Lattes)

**Objetivo.** Provar, item por item e variante por variante, que o formulário do LattesFácil é uma réplica fiel do formulário
do Currículo Lattes: **mesmos campos, mesmos títulos, mesmo tipo de controle, mesmos valores aceitos e mesmo comportamento**
(campos que aparecem/somem, listas, lupas, pop-ups), e que o **preenchimento** de cada campo funciona no Lattes real.

**Por que mudar o método.** Até aqui cada item foi conferido "a olho" e só o que apareceu na conversa foi corrigido. No projeto
isso deixou escapar: radios Sim/Não com opções trocadas, grupos de marcação desenhados como caixa única, listas inteiras da aba
Equipe e do Financiamento ausentes, campos de lupa tratados como texto livre. O método abaixo troca "olhar" por **captura
sistemática + comparação automática + prova de preenchimento com leitura de volta**, com critério de aceite numérico.

**Universo.** 61 itens, 76 variantes, 1.347 campos nomeados e 185 listas (grades) no spec atual (`itens/especificacao/`).

---

## 1. Princípios

1. **O Lattes real é a única fonte de verdade.** O spec é derivado da captura, nunca o contrário.
2. **Nada se dá por validado sem evidência arquivada** (JSON da captura, relatório do diff, relatório do preenchimento).
3. **Só leitura por padrão.** Nenhum teste clica em Salvar. Salvar só com autorização explícita por item e em currículo de teste
   (ver fase 7).
4. **Um item (variante) por vez, até fechar.** Só avança com a ficha 100% resolvida.
5. **Defeito vira regra.** Todo tipo de falha achada entra na lista de verificação da fase 1 e passa a ser checada em todos os itens.
6. **Correção no gerador, não no JSON.** Os specs são regenerados por `itens/gerar_specs.py`; ajustes manuais nos JSON se perdem.

### Recomendações permanentes (valem para todo item, todas as etapas)
Definidas pelo usuário em 21/11/2026: a plataforma atenderá vários usuários com necessidades distintas, então precisa ter **toda a oferta do Lattes**,
sem ponto faltante em nenhuma etapa.

1. **Zero pendência.** Um item só é "fechado" com todas as fases completas e a lista de pendências vazia. "Ressalva", "limitação conhecida" ou
   "ficou para depois" **não fecham** o item: viram **pendência bloqueante** em `docs/validacao/STATUS.md` (com o próximo passo) e o item
   permanece "em andamento". Não se anuncia item como pronto com pendência aberta.
2. **Espelho completo da oferta.** Todas as opções de cada lista (sem amostragem; só catálogos acima de 250 valores podem ser amostrados, com
   justificativa), todas as variantes, todos os caminhos de abertura do formulário (por DOI, manual, por nome do periódico...), todos os estados
   condicionais e todas as listas. O app oferece exatamente o que o Lattes oferece naquele formulário (nem mais, nem menos).
3. **Todos os caminhos do produto, um só formulário.** O formulário gerado por spec vale em todos os fluxos: documento enviado, formulário em
   branco, caderno/lote de resumos, histórico (reabrir registro), enriquecimento e sanitização, revisão e envio no app logado. Não pode haver dois
   formulários para o mesmo item (um completo e um antigo).
4. **Robô que nunca trava nem depende do usuário.** Silenciar alert/confirm/prompt do Lattes em todas as janelas e registrar as mensagens;
   detectar e tratar falhas intermitentes do Lattes (reabrir o formulário); ser idempotente (preencher de novo não duplica); ler pop-ups de erro e
   de sucesso; repetir no robô as validações que o próprio Lattes faz antes de abrir ou de salvar (ISSN, nome x ISSN, ISBN, obrigatórios).
5. **Prova no Lattes real, não só no teste.** Matriz de valores completa com leitura de volta; salvamento de teste autorizado (prefixo
   `ZZ-TESTE-LATTESFACIL`, registrado em `LOG_OPERACOES_NOITE.md`) com conferência do registro gravado; app logado testado de ponta a ponta
   (peça o acesso ao usuário no início do item, não no fim).
6. **Perfis diferentes.** Verificar se o formulário varia por perfil ou por estado do currículo (outros usuários, currículo vazio, currículo com
   muitos itens) e registrar; HTML/capturas de outros perfis entram como evidência.
7. **As ferramentas também são auditadas.** Defeito de captura, de comparador ou de executor conta como defeito e é corrigido antes de confiar
   no resultado (ex.: captura que lia o texto dos radios deslocado; comparador que ignorava catálogos).
8. **Defeito vira regra e teste.** Todo defeito achado entra no registro (seção 8), na lista da fase 1 e na suíte automática.
9. **Rastro e limpeza.** Todo item gravado no Lattes de teste é registrado com onde apagar; o usuário revisa e remove.

## 2. Papéis

| Quem | Faz |
| --- | --- |
| Você | Abre o formulário do item no Chrome (aba controlada pelo Claude), entra no app (código de acesso), recarrega a extensão, autoriza qualquer salvamento. |
| Claude | Roda a captura, o diff, a tela de teste e o preenchimento; corrige o gerador/app/extensão; arquiva as evidências; reinicia o servidor. |

## 3. O ciclo por item (8 fases, com critério de saída)

### Fase 0 — Escopo do item
- Listar as **variantes** (ex.: projeto = 5; formação = 10), as **abas** e como o formulário abre (URL direta, janela, nível).
- **Saída:** ficha criada (`docs/validacao/<item>.md`, modelo em `docs/validacao/_modelo-ficha.md`).

### Fase 1 — Captura de referência (a "verdade")
No formulário real aberto, uma auditoria registra, por variante:
- **Campos:** `name`, tipo de controle (texto, área, seleção, radio, grupo de marcação, data, lupa), `maxlength`, desabilitado
  (lupa), somente leitura, obrigatório (mensagens do Salvar), rótulo exato exibido (texto ao lado/acima, não o `name`).
- **Opções:** valor e texto de cada seleção, radio e marcação (lista completa, incluindo grandes catálogos).
- **Abas e listas:** cada aba; cada lista (colunas, botão "Incluir novo", popup de inclusão e os campos dele, lupa/"Listar todos").
- **Estados (os "ambientes"):** para **cada gatilho** (radio, caixa, seleção que muda outras), percorrer **cada valor** e registrar
  o que aparece, some, muda de opções ou fica obrigatório. Inclui seleções dependentes (ex.: A define as opções de B).
- **Regras de formato:** máscaras (data, CNPJ, ISSN, ano), só dígitos, limite de caracteres, formato aceito/recusado.
- **Verificações fixas (lições do projeto):** radios com valores/rótulos reais; grupos de marcação; campos desabilitados com lupa
  e árvore de órgãos; campos condicionais; listas por aba; abas que são só vínculo com itens já cadastrados; campo oculto que
  existe no DOM mas não aparece; textos de ajuda e avisos fixos.
- **Evidência:** `docs/campos-lattes/ref/<item>/<variante>.json` (captura canônica, com data e versão do formulário).
- **Saída:** captura completa; nenhuma aba sem registro.

### Fase 2 — Diff automático spec × captura
Comparador compara spec (`itens/especificacao`) e captura e emite o relatório:
`ausente_no_spec`, `sobrando_no_spec`, `tipo_diferente`, `maxlength_diferente`, `opcoes_diferentes`, `rotulo_diferente`,
`obrigatorio_diferente`, `condicional_ausente`, `lista_ausente`, `colunas_diferentes`.
- **Critério de saída:** **zero divergências** ou cada exceção justificada por escrito na ficha (campo que o Lattes mantém mas o
  usuário nunca vê, por exemplo).
- Correção sempre no gerador (`gerar_specs.py` + curadoria), seguida de regeneração e novo diff.

### Fase 3 — Paridade de tela (o app reproduz o formulário)
Renderizar o formulário do app e comparar com a captura, **em cada estado da fase 1**:
- rótulo visível igual; **tipo de controle igual** (radio é radio, grupo é grupo, lupa é busca, lista é tabela com as mesmas colunas);
- opções iguais (texto e código); `maxlength` e máscaras iguais; obrigatório sinalizado igual;
- campos condicionais aparecem/somem nos mesmos gatilhos; seleções dependentes trocam as opções como no Lattes;
- abas e listas na mesma ordem e com os mesmos nomes.
- **Critério de saída:** checklist da ficha 100% marcado, com captura de tela de cada estado.

### Fase 4 — Matriz de valores (o que é aceito)
Gerada do spec, por campo:

| Tipo | Casos mínimos |
| --- | --- |
| Texto | vazio · 1 caractere · típico · exatamente `maxlength` · `maxlength`+1 · acentos/cedilha · aspas e `;` · só espaços |
| Número/ano | válido · fora da faixa · letras · máscara (com e sem pontuação) |
| Data | válida · inválida · formato alternativo |
| Seleção/radio | **cada opção** (inclui a vazia) |
| Grupo de marcação | nenhuma · cada uma · todas · combinações que acionam condicionais |
| Lupa | nome exato · sigla · nome parcial · inexistente · ambíguo |
| Lista | 0 · 1 · vários itens · item duplicado · exclusão |
| Condicional | gatilho ligado · desligado · alternado (valor residual some?) |
- Cada caso traz o **resultado esperado** vindo da captura (aceito, cortado, recusado, mensagem do Lattes).
- **Saída:** matriz arquivada na ficha.

### Fase 5 — Prova de preenchimento com leitura de volta
Para cada caso da matriz:
1. O autofill preenche o formulário aberto no Lattes (sem salvar).
2. Um **leitor** lê de volta o formulário real (valor de cada campo, opção marcada, linhas das listas) e compara com o enviado.
3. Resultado por campo: `OK` · `cortado (esperado)` · `divergente` · `não preenchido` · `aviso do Lattes` · `exige ação manual`
   (lupa ambígua).
4. Fecha o formulário **sem salvar** e confirma que não restou rascunho.
- **Critério de saída:** 100% `OK` ou `exige ação manual` documentado; **nenhum** `divergente` nem `não preenchido` sem causa.

### Fase 6 — Validação do Lattes (sem salvar)
Capturar as **mensagens de obrigatórios** do Lattes (já vêm do próprio formulário, sem salvar) e comparar com os obrigatórios
do app. Quando a regra só se revela ao salvar, ela fica pendente para a fase 7.
- **Saída:** lista de obrigatórios do app = lista do Lattes, por variante.

### Fase 7 — Aceite com salvamento (opcional e autorizado)
Só se você autorizar, **em currículo de teste** (ou com item marcado "TESTE" e excluído em seguida): salvar uma amostra por
variante, ver o Lattes aceitar e conferir que a lista do currículo mostra o item certo; depois excluir. Sem autorização, a fase 6
é o limite.

**Regras permanentes (decisão do usuário, 21/11/2026):**
- Formulários que sobrescreveriam dado real do currículo (identificação, endereço, idioma, licença, formação acadêmica, pós-doutorado, texto inicial, outras informações) **não têm salvamento de teste**: matriz de preenchimento + leitura de volta bastam; não é pendência.
- "É um dos 10 trabalhos mais relevantes" = Sim: o Lattes recusa acima do limite de relevantes; é **exceção justificada "limite do Lattes"** (`ref/_excecoes_matriz.json`), não falha.

### Fase 8 — Fechamento e registro
- Ficha assinada com data, versão do app, resultado e pendências.
- Testes automáticos do item adicionados à suíte (diff e matriz viram teste de regressão).
- Itens fechados entram em `docs/validacao/STATUS.md` (matriz item × variante × fase).

## 4. Definição de "pronto" (por variante)
- Fase 2: 0 divergências (ou exceções justificadas).
- Fase 3: 100% do checklist de paridade, em todos os estados.
- Fase 5: 100% dos campos `OK`/`exige ação manual` documentada; 0 `divergente`.
- Fase 6: obrigatórios iguais.
- Fase 4 sem amostragem: todas as opções oferecidas pelo Lattes; todos os caminhos de abertura.
- Fase 7 feita nas formas estruturalmente diferentes (e no item todo, quando o usuário autoriza), com o registro gravado conferido.
- Todos os fluxos do app usam o formulário do spec (documento, em branco, caderno/lote, histórico, enriquecimento, app logado).
- Robô: sem travamento por alertas, com reabertura em falha intermitente e idempotente.
- **Lista de pendências do item vazia** (recomendação 1). Com qualquer pendência aberta o item fica "em andamento".
- Testes da suíte passando e servidor reiniciado; extensão reconstruída quando o preenchimento mudou.

## 5. Ferramentas a construir (hoje não existem prontas)
| Ferramenta | Função | Base existente |
| --- | --- | --- |
| `auditoria_lattes.js` | Captura da fase 1 (campos, opções, abas, listas, estados), rodando no formulário aberto; saída sem URLs/cookies | scripts avulsos desta conversa; `docs/campos-lattes/_raw` |
| `tests/valida_paridade.py` | Diff da fase 2 (spec × captura) com relatório por categoria | `itens/gerar_specs.py`, `docs/campos-lattes` |
| Teste de tela | Renderiza o app e compara com a captura (fase 3) | `static/app.js` (`genCampo`, `genDesenhar`) |
| `matriz_valores.py` | Gera os casos da fase 4 a partir do spec | `itens/especificacao` |
| `leitor_formulario.js` | Leitura de volta da fase 5 (valores e listas) | `extensao/autofill_core.js` |
| `docs/validacao/` | Ficha por item e `STATUS.md` | `docs/campos-lattes/VALIDACAO.md` (só compara nomes de campo hoje) |

## 6. Ordem sugerida
1. **Projeto (5 variantes)** como piloto: já conhecemos os defeitos e calibramos o método e as ferramentas.
2. Itens mais usados: artigo em periódico, trabalho em evento, orientações, bancas, formação, atuação.
3. Demais produções (27 itens, 28 variantes) agrupadas por semelhança de formulário.
4. Patentes e registros, citações, dados gerais.
Após o piloto, calibrar o tempo por variante e fechar o cronograma.

## 7. Regras de segurança
- Nunca clicar em Salvar sem autorização por item; fechar formulários sem salvar.
- Dados de teste identificáveis ("TESTE") e removidos ao final.
- Sem digitar senhas ou códigos de acesso: quem entra no app é o usuário.
- Evidências sem URL de sessão, `f_cod` ou cookies (o Chrome também bloqueia essas saídas).

## 8. Registro de defeitos encontrados (alimenta a fase 1)
| Defeito | Onde apareceu | Verificação fixa |
| --- | --- | --- |
| Radio com opções/rótulo errados (`"Não"="S"`, nome técnico como rótulo) | 11 itens | Comparar valor e texto de cada radio |
| Grupo de marcação desenhado como caixa única e preenchido pela primeira opção | Projeto de ensino, Identificação (`f_pcd`) | Contar opções por `name` e testar o preenchimento de cada uma |
| Campo desabilitado com lupa tratado como texto | Instituição, Órgão, Curso, Agência | Flag `disabled` e função da lupa |
| Órgão é árvore por instituição, sem a coordenação do documento | Projeto | Abrir a lupa e listar níveis |
| Campo condicional não reproduzido | CNPJ/empresa, potencial de inovação, "Especifique" | Alternar cada gatilho e comparar campos visíveis |
| Listas por aba ausentes | Equipe, Instituições envolvidas, Financiamento | Inventariar tabelas/`Holder` e botões "Incluir novo" |
| Aba que só vincula itens já cadastrados | Produção C&T, Orientações | Registrar como vínculo, não como campo |
| Campo presente no DOM mas invisível ao usuário | `f_tpo_pesq_emp` no Ensino | Medir visibilidade real, não só existência |
| Janela da lupa com outro nome de página em cada item | Projeto (`pp_lista_inst`, não `prc_inst_form`) | Listar os iframes que a lupa abre e testar o autofill de cada lupa |
| Botão "Incluir novo item" é imagem sem texto; a lista de projetos por baixo tem um botão igual | Financiamento do projeto | Procurar `img.botaoAdicionar` dentro da tabela certa, só no formulário aberto |
| Lupa recarrega a janela a cada busca (documento antigo fica obsoleto) | Instituição de financiamento | Reler a janela a cada tentativa, nunca guardar o documento |
| Esperas fixas curtas para janelas que demoram a fechar | Financiamento | Esperar por condição (janela fechou / linha apareceu) |
| Campo de texto longo sem `maxlength` na tela | Descrição, Objetivos e metas, Description | Comparar `maxlength` de textarea também |
| Obrigatoriedade condicional (Ano fim só se concluído; empresa/potencial só se visíveis; equipe com 1 coordenador) | Projeto | Ler o `check()` do formulário (F6) e o teste de salvamento |
| Obrigatório que o spec não trazia (instituição e órgão no Ensino) | Projeto de ensino | Só o salvamento de teste revelou: validar F6 também por tentativa de salvar em item de teste |

## 9. Ferramentas disponíveis (piloto do projeto)
| Ferramenta | Uso |
| --- | --- |
| `ferramentas/receptor_captura.py` | Recebe capturas/diagnósticos da página do Lattes por pedidos de imagem em partes (o Lattes bloqueia `fetch`); serve também o autofill e a matriz para teste. Porta 8798, só local |
| `ferramentas/auditoria_lattes.js` | F1: captura campos, opções, estados e listas do formulário aberto |
| `ferramentas/valida_paridade.py` | F2: diff spec × captura |
| `ferramentas/gerar_harness_tela.py` + `harness_tela_modelo.html` | F3: renderiza o app com as funções reais e compara por estado |
| `ferramentas/gerar_casos.py` | F4: matriz de casos de valores |
| `ferramentas/executor_preenchimento.js` | F5: roda o autofill real e lê de volta; `rodarTodas` percorre as variantes; `listas` testa a aba Equipe |
| `ferramentas/relatorio_f5.py` | Resume os resultados da F5 |
| `tests/teste_valida_paridade.py`, `tests/teste_spec_projeto.py` | Regressão do comparador e das regras do projeto |
