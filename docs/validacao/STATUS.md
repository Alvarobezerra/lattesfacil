# Status da validação dos formulários

Metodologia: [../metodologia-validacao-formularios.md](../metodologia-validacao-formularios.md). Universo: 61 itens, 76 variantes.

> **Regra (21/11/2026): zero pendência.** Item com qualquer pendência abaixo fica "em andamento", não "pronto". Ver "Recomendações permanentes" em
> [../metodologia-validacao-formularios.md](../metodologia-validacao-formularios.md).

## Pendências bloqueantes (por item)
| Item | Pendência | Próximo passo |
| --- | --- | --- |
| Projetos (5 variantes) | Perfis diferentes (fluxo documento → formulário → envio pela extensão já testado no app logado). Escolha manual por desenho (não é pendência do robô): financiamento com o CNPq (dois cadastros DF/RJ) e instituições que não constam no cadastro do Lattes com o nome oficial (ex.: FAPEMA) — o robô avisa e deixa a janela aberta | Entrar no app (o usuário) e rodar o fluxo de projeto |
| Artigo em periódico | Perfis diferentes de usuário (documento, DOI, dados faltantes, reabrir registro e envio pela extensão já testados no app logado) | Conferir com outros perfis |
| Trabalho em anais | Perfis diferentes (caderno com PDF longo sintético no layout real, envio pela extensão e reabrir registro já testados) | Conferir com outros perfis e com um caderno real de congresso |
| Apresentação de trabalho e palestra | Perfis diferentes (documento e envio pela extensão já testados no app logado) | Conferir com outros perfis |
| Orientação concluída / em andamento | Perfis diferentes (documento, registro antigo e envio pela extensão já testados no app logado) | Conferir com outros perfis |
| Demais 55 itens | Specs gerados do mapeamento antigo, sem captura real, sem leitor/robô validados | Seguir o ciclo de 8 fases por item |

Fases: 1 captura · 2 diff · 3 paridade de tela · 4 matriz de valores · 5 preenchimento com leitura de volta · 6 obrigatórios · 7 salvamento de teste · 8 fechamento.
Log das operações feitas no Lattes real: [LOG_OPERACOES_NOITE.md](LOG_OPERACOES_NOITE.md).

| Item | Variante | F1 | F2 | F3 | F4+F5 | F6 | F7 | Observações |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Projetos | Projeto de extensão | ✔ | ✔ 0 div. | ✔ 0 div. | ✔ 69/69 + listas 5/5 + lupas | ✔ regras lidas | ✔ gravado e listado | Piloto |
| Projetos | Projetos de pesquisa | ✔ | ✔ 0 div. | ✔ 0 div. | ✔ 69/69 | ✔ (mesmo formulário da Extensão) | — | |
| Projetos | Projeto de desenvolvimento tecnológico | ✔ | ✔ 0 div. | ✔ 0 div. | ✔ 72/72 | ✔ | — | inclui "Técnico de nível médio" |
| Projetos | Projeto de ensino | ✔ | ✔ 0 div. | ✔ 0 div. | ✔ 86/86 | ✔ (achou obrigatórios que faltavam) | ✔ gravado e listado | 1ª tentativa recusada: instituição e órgão obrigatórios |
| Projetos | Outros tipos de projetos | ✔ | ✔ 0 div. | ✔ 0 div. | ✔ 69/69 + lupas 2/2 | ✔ | — | |

| Produções | Artigo completo em periódico | ✔ 19 campos, 4 listas (manual) + DOI em `ref/artigo_doi/` | ✔ 0 div. (idiomas: 80 do Lattes) | ✔ tela do app = Lattes (harness, 0 div.) | ✔ matriz 118/118 · DOI ✔ · listas ✔ · busca por nome ✔ (único, ambíguo, nenhum) | ✔ regras do Lattes (ISSN, nome x ISSN, volume, página) repetidas no robô | ✔ gravado e conferido | Convertido de legado em 21/11/2026. App logado não testado (exige o código de acesso do usuário) |
| Produções | Trabalho publicado em anais de evento | ✔ 27 campos, 4 listas | ✔ 0 div. (país e idioma: 80 opções reais) | ✔ spec = Lattes | ✔ matriz 252/252 + listas ✔ | ✔ regras lidas do Lattes (ISBN válido, 13 caracteres) | ✔ gravado e listado | Convertido de legado em 21/11/2026. Pendente: fluxo de caderno de resumos (ainda usa o formulário antigo) e app logado |

**Achado: itens legados (21/11/2026).** `artigo`, `anais`, `apresentacao` e `orientacao_concluida` NÃO são gerados por `itens/gerar_specs.py`: têm formulário fixo em
`static/index.html` (campos com `data-tipos`) e mapeamento próprio no autofill. Por isso o validador de paridade não os cobre. Captura do artigo em
`docs/campos-lattes/ref/artigo/artigo_periodico.json` (aberto por lista > Incluir novo item > DOI de exemplo; sem DOI o Lattes devolve ORA-06503).
Campos do Lattes que o formulário do app para artigo **não tem**: Idioma, Home page, "É um dos 10 trabalhos mais relevantes" (F_RELEV), "Produção para educação e
popularização de C&T" (F_STA_DIVULGACAO_CIENTIFICA), Fator de Impacto (JCR), Outras informações, Title/Other information (inglês), listas Palavras-chave,
Áreas de conhecimento e Setores de aplicação, privacidade. O app tem "Fascículo", que o Lattes não tem no artigo.

**Ressalvas do piloto**
- A matriz de valores (F4/F5) rodou nos campos de texto, área, seleção, radio e grupos de marcação das cinco variantes. Listas e lupas foram testadas na
  Extensão (listas) e em "Outros tipos" (lupas); as demais variantes usam o mesmo código.
- **Financiamento com CNPq:** o Lattes tem dois cadastros de mesmo nome (DF e RJ) → escolha manual (comportamento correto). Instituições de nome longo só são
  achadas pela busca do Lattes por sigla ou parte curta; o autofill tenta sigla e nome completo, mas nomes sem sigla conhecida podem exigir a lupa.
- F7 feita só em Extensão e Ensino (as duas formas estruturalmente diferentes). Pesquisa, Desenvolvimento e Outros não foram gravados.
- F6 usou as mensagens do `check()` do próprio formulário (sem salvar) e o teste de salvamento do Ensino.

**Defeitos encontrados e corrigidos nesta etapa** (ver tabela do roteiro): lupa de instituição de projeto usa outra janela (`pp_lista_inst`); botão de incluir
financiamento é imagem (`img.botaoAdicionar`) e a busca pegava o botão da lista de projetos; janela da lupa é recarregada a cada busca (documento obsoleto);
espera fixa curta no fechamento da janela de financiamento; textarea sem limite de 3900; Ano fim obrigatório só se concluído; empresa/potencial obrigatórios
quando visíveis; equipe exige um coordenador; instituição e órgão obrigatórios no Ensino.

Capturas em `docs/campos-lattes/ref/<item>/`, resultados de preenchimento em `docs/campos-lattes/ref/<item>_f5/`.
Comandos: `python ferramentas/valida_paridade.py projeto` · `python ferramentas/relatorio_f5.py projeto` · `python tests/teste_spec_projeto.py`.

**Defeitos do robô de preenchimento achados no artigo (21/11/2026)**
- Alertas nativos do Lattes ("DOI não encontrado.", "Crossref fora do ar", "Palavra já existente") travavam a página: o robô agora silencia alert/confirm/prompt em todas as janelas, guarda as mensagens no relatório e restaura no fim; modo `__semAlerta` para automação.
- O Lattes limpa campos depois de "complete": espera de 3,5 s no artigo.
- Lattes às vezes abre o formulário sem os dados do periódico ou sem a grade de autores (serviços externos): o robô detecta e reabre (lista + formulário) até 2 vezes.
- Preenchimento repetido incluía de novo palavras, áreas e autores: agora pula o que já está na lista.
- Abertura pelo periódico: o Lattes valida ISSN (`prc_valida_issn`), nome x ISSN (`valida_nome_issn_periodico`), volume e página antes de abrir; busca por nome só aceita uma palavra (`find_periodico`). O robô repete tudo isso.
- Validador de paridade comparava mal seleções por catálogo (idioma: 80 no Lattes, 152 no catálogo); captura confundia o texto dos radios quando o texto vem depois do botão.

**Defeitos achados nos anais (21/11/2026)**
- Captura lia o texto dos radios deslocado ("Natureza" virava opção) quando o texto vem depois do botão: agora usa o texto mais próximo do botão (geometria).
- ISBN do documento com hífens (17 caracteres) era cortado no limite de 13 do Lattes: o leitor grava só os dígitos.
- O Lattes valida o dígito verificador do ISBN/ISSN ao salvar ("O ISSN informado é inválido"): o robô agora lê os pop-ups de erro do Lattes depois de salvar e reconhece a mensagem de sucesso.
- Leitor não trazia título dos anais nem nome do evento mesmo com "Anais do ..." no documento.

**Projetos — fechado em 21/11/2026 com o robô novo:** matriz 71/71 (pesquisa), 71/71 (extensão), 88/88 (ensino), 74/74 (desenvolvimento), 71/71 (outros), todas com lupas;
listas da aba Equipe (pesquisadores com coordenador, instituição envolvida, financiamento) 5/5 em cada uma das 5 variantes; salvamento real aceito em todas as 5 variantes (extensão e ensino na noite anterior; pesquisa, desenvolvimento e outros em 21/11) e conferido nas listas.
**Ferramentas corrigidas na rodada:** o executor travava no fim sem o envio de resultados carregado, lia o formulário antigo depois do preenchimento e não capturava as mensagens do robô; o detector de erros de salvamento pegava texto de script do Lattes.
**Robô (anais/projeto):** busca de instituição por palavras do nome e comparação ignorando sigla e UF no fim do nome.
**App logado (21/11/2026):** 11 testes do artigo/anais passaram (formulário do spec pelo documento, DOI x manual, 80 idiomas/países, ISBN, botão de dados faltantes, endereço de envio) e 7 do caderno/histórico (abrir resumo do caderno, registro do histórico, natureza e evento mapeados).

**Apresentação (21/11/2026):** captura real (17 campos, 8 listas), spec com 0 divergências (país e idioma 80 opções), leitor, servidor, app e robô ligados ao spec;
matriz 212/212; salvamento real aceito e conferido na lista (nº 2, 2024, Comunicação): `ZZ-TESTE-LATTESFACIL Apresentação de teste (validação automática)`.

**Envio pelo app + extensão (21/11/2026, app logado):** apresentação ✔ ("preenchido — falta você salvar", formulário do Lattes conferido) e artigo por DOI ✔.
Anais e projeto preencheram certo, mas a extensão acusou falso "o item pode NÃO ter sido salvo": o detector do `background.js` lia rótulos fixos ("Informe o Digital Object
Identifier...") e texto de script do Lattes. Corrigido (extensão 0.9.7, teste `teste_extensao_avisos.py`); **repetir anais e projeto depois de recarregar a extensão**.

**Envio pelo app + extensão 0.9.7 (21/11/2026):** anais ✔ e projeto ✔ ("preenchido — falta você salvar"); com apresentação e artigo, os 4 itens convertidos/fechados passaram no envio de ponta a ponta.

**Orientação (21/11/2026, em andamento — limite de uso atingido):** spec/paridade 0, leitor, servidor, app e robô ligados; matriz 204/210 nas duas variantes. Descoberto: o tipo de orientação só "pega" com natureza mestrado/doutorado
(`exige_antes`, gerado da captura de aceitação) e a agência financiadora é campo de LUPA (lista `prc_agencia`; robô `gLupaAgencia` e app com `exige_antes` já escritos).
**Falta:** reabrir o Lattes, recapturar a andamento com a aceitação, rodar de novo a matriz (esperado 210/210), salvar as duas orientações de teste e testar a lupa da agência; depois caderno com PDF longo, perfis diferentes, executor genérico e os 55 itens.

**Orientações fechadas no Lattes (21/11/2026):** paridade 0, matriz 207/207 nas duas (com lupa da agência e dependência do tipo de orientação) e salvamento real conferido nas listas. Nova regra do robô: reaproveita formulário aberto só se o subtipo (f_tipo / f_cod_tipo) for o mesmo.

**App logado, orientações (21/11/2026):** 9 testes OK (documento → formulário do spec, endereço C/A, registro antigo) e envio pela extensão OK nas duas. **Caderno:** `tests/teste_caderno.py` (PDF longo no layout real, 14 resumos → formulário de anais). Achado: o leitor do caderno só entende o layout "título em caixa alta + autores em maiúsculas com índice + afiliação numerada"; outros layouts de congresso podem exigir ajuste.

**Bancas de trabalhos de conclusão (21/11/2026) — fechado:** captura real (14 campos, 8 listas), spec com 0 divergências, matriz 197/197 (com as lupas de instituição e curso) e salvamento real conferido na lista.
Descobertas: o Lattes só aceita as lupas de instituição/curso depois de escolher a natureza ("Informe a natureza") → `exige_antes` no spec; o tipo do mestrado (Acadêmico/Profissional) só vale com natureza Mestrado e seus valores têm espaço no fim ("34 ", "35 ");
o curso "Farmácia" só existe no nível de graduação (a matriz escolhe Graduação antes da lupa do curso e a instituição antes do curso). Teste: `tests/teste_spec_banca.py`.
**Ferramentas:** `gerar_casos.py` põe instituição e natureza antes da lupa do curso; novo `gerar_payload_generico.py` (carga de salvamento de teste a partir do spec) para os itens ainda sem gerador próprio.

**Bancas de comissões julgadoras (21/11/2026) — fechado:** captura real (11 campos, 8 listas), spec com 0 divergências (1 justificada: o rótulo da instituição vem como "*"), matriz 189/189 com a lupa de instituição e salvamento real conferido na lista.
Defeito do robô achado: na comissão julgadora a instituição é lupa mas o campo vem habilitado (o atributo do Lattes está escrito "disable"); o robô só usava a lupa em campo bloqueado e deixava o texto no campo. Agora usa a lupa também quando o campo tem a classe `input-lupa` (extensão a recarregar).
A instituição é obrigatória nesta variante (asterisco vermelho), embora a mensagem de obrigatórios do servidor não a liste.

**Faixa 8 (21/11/2026) — livros, prêmios e demais produções (19 itens, 20 formulários):** captura real, paridade 0 pendentes (`tests/teste_spec_faixa8.py`), matriz no Lattes real sem falha além de F_RELEV=Sim (limite de 5 produções relevantes do Lattes) e salvamento de teste conferido na lista de cada item. Achados: valores reais com espaço no fim (prefácio), natureza do livro bloqueada, ISBN do capítulo só com dígitos, lista de artes visuais corrigida, autores em entrevista/mídia e redes sociais. **Pendência bloqueante (a mesma da faixa 7):** repetir a matriz F_RELEV=Sim dos 16 itens afetados depois que o usuário apagar produções relevantes de teste.

**Faixa 7 (21/11/2026) — eventos e cursos (3 itens):** captura real, paridade 0 pendentes (`tests/teste_spec_faixa7.py`), matriz no Lattes real: participação 121/121, organização 215/216 e curso 212/213 (a divergência é F_RELEV=Sim: o Lattes limita a 5 produções relevantes e o currículo já tem 5; confirmado pela mensagem do Lattes), salvamento de teste conferido na lista. Achados: o tipo da participação depende da forma (Convidado: 5 tipos; Participante: 3; Ouvinte: sem tipo) e só é exigido para Convidado/Participante; o salvamento automático não ficava mais travado pela escolha automática do tipo. **Pendência bloqueante:** repetir a matriz de organização e curso (F_RELEV=Sim) depois que o usuário apagar produções relevantes de teste, para fechar 100%.

**Faixa 5 (21/11/2026) — fechada para os 13 itens** (software com e sem registro, produto, processo/técnica, trabalho técnico, relatório técnico, extensão tecnológica, material didático, desenho industrial, marca, topografia, cultivar protegida e registrada): captura real, paridade 0 pendentes (`tests/teste_spec_faixa5.py`), matriz de valores sem falha no Lattes real (133, 124, 218, 215, 217, 213, 211, 202, 122, 117, 117, 127, 114) e salvamento de teste conferido na lista de cada item (ver LOG_OPERACOES_NOITE.md). Achados do salvamento: limite de itens "mais relevantes" (o teste usa "não") e "Autoridade Nacional" obrigatória nas cultivares. Sem ponto em aberto além do "Perfis diferentes" comum a todos os itens.

**Patente (21/11/2026) — fechada:** captura real (22 campos, 11 listas, 1 estado), spec com 0 pendentes (2 justificadas), matriz 128/128 e salvamento real conferido na lista.
Defeitos achados: (1) o spec trazia as opções do "potencial de inovação" deslocadas (Não=S, "Qual o potencial?"=N) porque no Lattes o texto vem ANTES do botão — corrigido no gerador; (2) a instituição de depósito não é a lupa de instituições: é lista fechada de órgãos (INPI etc.) e vem no endereço de abertura (`entra_pela_abertura`); o robô não tenta mais a lupa nesse caso; (3) a sugestão de pessoas (depositante) falhava porque o Lattes mostra "Nome (CITAÇÃO)": o robô agora aceita a sugestão que contém o nome inteiro e tenta também o nome curto;
(4) obrigatórios reais da patente: natureza, categoria, tipo, país, depositante/titular, situação (Depósito, Depósito PCT, Pedido do Exame, Licenciamento, Concessão, Comercialização, Cessão, Em Domínio Público, Aguardando Negociação) e, se houver potencial de inovação, o texto do potencial.
**Aviso "máximo até 15 registros" (investigado em 21/11/2026):** não é limite da grade de inventores nem da de depositantes. No formulário real da patente (sem salvar) entraram 18 inventores digitados à mão pelo robô, 20 inventores escolhidos em "Listar todos" e 18 depositantes escolhidos na lista, sem esse aviso (só "Informação já existente" ao repetir um nome); repetir o preenchimento também não duplica inventores. O aviso da captura de tela não foi reproduzido por nenhum caminho do robô; a causa provável é uma ação manual na janela de seleção de outra grade. Se voltar, anotar qual aba e qual lista estava aberta.

**Faixa 5 (21/11/2026) — capturas e paridade feitas, matrizes e salvamentos em andamento:** capturados no Lattes real os 13 formulários (software com e sem registro, produto, processo, trabalho técnico, relatório técnico, extensão tecnológica, material didático, desenho industrial, marca, topografia de circuito, cultivar protegida e registrada); paridade 0 pendentes em todos.
Ajustes gerais no gerador do spec: rótulo vindo da captura quando o mapeamento só tinha o nome do campo; campo que o mapeamento dava como condicional mas aparece sempre (ex.: texto do potencial de inovação nos softwares); potencial de inovação com Sim=S/Não=N em todos; grades de inventores/melhoristas e de depositantes que faltavam (desenho industrial, marca, topografia, cultivares, softwares); órgão depositário e nº do registro como campos de abertura.
Ferramentas novas: `gerar_ciclo_captura.py` e `gerar_ciclo_matriz.py` (rodam vários itens em sequência no Lattes), `ref/_excecoes_globais.json` (artefatos conhecidos da captura valendo para todos os itens).
**Pendente:** rodar as 13 matrizes e os salvamentos de teste (a aba do Lattes travou com um alerta nativo no início da rodada de matrizes).
