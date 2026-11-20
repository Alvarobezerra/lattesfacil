# Status da validação dos formulários

Metodologia: [../metodologia-validacao-formularios.md](../metodologia-validacao-formularios.md). Universo: 61 itens, 76 variantes.

> **Regra (21/11/2026): zero pendência.** Item com qualquer pendência abaixo fica "em andamento", não "pronto". Ver "Recomendações permanentes" em
> [../metodologia-validacao-formularios.md](../metodologia-validacao-formularios.md).

## Pendências bloqueantes (por item)
| Item | Pendência | Próximo passo |
| --- | --- | --- |
| Projetos (5 variantes) | Perfis diferentes (fluxo documento → formulário → envio pela extensão já testado no app logado). Escolha manual por desenho (não é pendência do robô): financiamento com o CNPq (dois cadastros DF/RJ) e instituições que não constam no cadastro do Lattes com o nome oficial (ex.: FAPEMA) — o robô avisa e deixa a janela aberta | Entrar no app (o usuário) e rodar o fluxo de projeto |
| Artigo em periódico | Perfis diferentes de usuário (documento, DOI, dados faltantes, reabrir registro e envio pela extensão já testados no app logado) | Conferir com outros perfis |
| Trabalho em anais | Caderno de resumos com PDF longo de verdade; perfis diferentes (envio pela extensão e reabrir registro já testados no app logado) | Testar com um caderno real |
| Apresentação de trabalho e palestra | Perfis diferentes (documento e envio pela extensão já testados no app logado) | Conferir com outros perfis |
| Orientação concluída / em andamento | Formulário antigo no app (existe spec, não é usado); sem captura e sem validação | Capturar, validar paridade, ligar o app e o robô ao spec, matriz, salvamento |
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
