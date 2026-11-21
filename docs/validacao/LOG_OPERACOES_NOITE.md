# Log de operações no Lattes (validação noturna)

**Autorização do usuário (20/11/2026):** salvar itens de teste no currículo é permitido se necessário; o usuário revisa este log pela manhã e
apaga o que foi incluído. O envio ao CNPq é barrado pelo próprio LattesData/fluxo do usuário, então itens gravados não vão à base do CNPq.

**Convenção:** todo item gravado leva o prefixo `ZZ-TESTE-LATTESFACIL` no título/nome principal. Para encontrar: ordenar a lista do item por título
ou buscar esse prefixo. Operações apenas de leitura/preenchimento sem salvar não geram registro aqui, exceto quando algo pode ter sido salvo por engano.

## Registro (cronológico)
| Hora | Item / variante | Operação | Resultado | Como localizar/apagar |
| --- | --- | --- | --- | --- |
| 00:23 | Projetos / Projeto de extensão | **Salvar** (fase 7), formulário preenchido pelo autofill: título `ZZ-TESTE-LATTESFACIL Projeto de extensão (validação automática)`, natureza Extensão, situação Em andamento, ano 2025, instituição UFMA, órgão CCSST-Imperatriz, equipe: titular como coordenador | **Lattes aceitou** ("A operação foi realizada com sucesso!"); item aparece como nº 1 na lista de Projeto de extensão (2025, UFMA) | Projetos > Projeto de extensão: procurar o título com prefixo ZZ-TESTE-LATTESFACIL e excluir |
| 00:24 | Projetos / Projeto de ensino | **Salvar** (fase 7), preenchido pelo autofill: título `ZZ-TESTE-LATTESFACIL Projeto de ensino (validação automática)`, natureza Ensino, em andamento, 2025, cooperação IE, temática EA, objetivos e metas, titular como coordenador | **1ª tentativa recusada pelo Lattes (nada gravado):** faltavam Órgão/Unidade e Instituição de execução (obrigatórios no Ensino; o app não exigia). Segunda tentativa abaixo. | Projetos > Projeto de ensino: procurar o título com prefixo ZZ-TESTE-LATTESFACIL e excluir |
| 00:25 | Projetos / Projeto de ensino | **Salvar** (2ª tentativa, mesmo formulário, agora com instituição UFMA e órgão CCSST-Imperatriz) | **Lattes aceitou** ("A operação foi realizada com sucesso!"). Houve um 1º clique em Salvar sem resposta visível e um 2º que gravou; conferido na lista: **apenas 1 item** (sem duplicidade) | Idem: Projetos > Projeto de ensino, título com prefixo ZZ-TESTE-LATTESFACIL |

## Resumo para a revisão da manhã
**Itens gravados no seu currículo (apague os dois):**
1. Projetos > **Projeto de extensão** → `ZZ-TESTE-LATTESFACIL Projeto de extensão (validação automática)` (2025, UFMA)
2. Projetos > **Projeto de ensino** → `ZZ-TESTE-LATTESFACIL Projeto de ensino (validação automática)` (2025, UFMA)

**Rascunhos:** os demais testes preencheram formulários sem salvar e foram descartados ao abrir outro formulário ou fechar a janela. Uma tentativa de salvar o Ensino foi
recusada pelo Lattes (campos obrigatórios), sem gravar nada.

**Como apagar:** abrir o item na lista do Lattes e usar a opção de excluir do próprio formulário/lista. Confira também se a "Última atualização" do currículo mudou para hoje.

## Registro de 21/11/2026 (artigo em periódico)
| Hora | Item / variante | Operação | Resultado | Como localizar/apagar |
| --- | --- | --- | --- | --- |
| (ver abaixo) | Produções / Artigo completo em periódico (abertura manual) | **Salvar** (fase 7) pelo robô com `__semAlerta`: título `ZZ-TESTE-LATTESFACIL Artigo de teste (validação automática)`, periódico Revista de Saude Publica (ISSN 0034-8910), vol. 12, pág. 101-110, 2025, autores: titular + coautor de teste | resultado registrado na seção seguinte | Produções > Artigos completos publicados em periódicos: procurar o título com prefixo ZZ-TESTE-LATTESFACIL e excluir |

**Resultado (21/11/2026):** o Lattes aceitou o salvamento do artigo (sem mensagem; voltou para a lista). Item nº 1 na lista de Artigos completos publicados em periódicos:
`ZZ-TESTE-LATTESFACIL Artigo de teste (validação automática)` — Revista de Saude Publica, 2025. Conferido ao reabrir: ISSN 0034-8910, vol. 12, edição 3, pág. 101-110,
autores (titular + "ZZ Coautor de Teste"), palavras-chave probiotics/babassu/beverages, área Microbiologia. **Apague este item.**
Antes do salvamento houve duas tentativas que NÃO gravaram nada (a lista seguiu vazia): a 1ª foi bloqueada pelo próprio robô por causa do aviso espúrio "DOI não encontrado.",
a 2ª foi interrompida porque o formulário já tinha dados da tentativa anterior (o robô agora pula o que já está nas listas).

## Registro de 21/11/2026 (trabalho em anais)
| Hora | Item / variante | Operação | Resultado | Como localizar/apagar |
| --- | --- | --- | --- | --- |
| (ver abaixo) | Produções / Trabalhos publicados em anais de eventos | **Salvar** (fase 7) pelo robô: título `ZZ-TESTE-LATTESFACIL Trabalho de teste em anais (validação automática)`, natureza Resumo, evento "Simpósio Exemplar de Iniciação Científica" (Nacional), 2024, autores titular + coautor de teste | resultado na linha seguinte | Produções > Trabalhos publicados em anais de eventos: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir |

**Resultado (21/11/2026, anais):** o Lattes aceitou ("A operação foi realizada com sucesso!") e o item aparece na lista de Trabalhos publicados em anais de eventos (nº 2, 2024):
`ZZ-TESTE-LATTESFACIL Trabalho de teste em anais (validação automática)`. **Apague este item.** Antes houve 2 tentativas que NÃO gravaram nada: a 1ª foi bloqueada pelo robô
(ISBN com hífens passava de 13 caracteres) e a 2ª foi recusada pelo Lattes com "O ISSN informado é inválido" (ISBN de teste sem dígito verificador válido).

## Registro de 21/11/2026 (projetos: salvamento nas variantes que faltavam)
Salvamento de teste pelo robô novo, título `ZZ-TESTE-LATTESFACIL <variante> (validação automática)`, 2025, UFMA, titular como coordenador, em:
Projetos de pesquisa; Projeto de desenvolvimento tecnológico; Outros tipos de projetos. Resultado por variante nas linhas seguintes.
Para apagar: Projetos > (cada tipo) > procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir.

**Resultado (21/11/2026, projetos):** Lattes aceitou os 3 salvamentos; cada item aparece uma única vez na lista do seu tipo: `ZZ-TESTE-LATTESFACIL Projetos de pesquisa (validação automática)`,
`ZZ-TESTE-LATTESFACIL Projeto de desenvolvimento tecnológico (validação automática)`, `ZZ-TESTE-LATTESFACIL Outros tipos de projetos (validação automática)` (2025, UFMA). **Apague os três.**
(Antes houve uma tentativa que NÃO gravou: o robô bloqueou o salvamento porque o órgão foi escolhido por aproximação e exige confirmação.)

## Registro de 21/11/2026 (apresentação de trabalho)
| Hora | Item | Operação | Resultado | Como apagar |
| --- | --- | --- | --- | --- |
| (ver abaixo) | Produções / Apresentação de trabalho e palestra | **Salvar** pelo robô: título `ZZ-TESTE-LATTESFACIL Apresentação de teste (validação automática)`, natureza Comunicação, 2024, São Luís - MA, autores titular + coautor de teste | resultado na linha seguinte | Produções > Apresentação de trabalho e palestra: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir |

**Resultado (21/11/2026, apresentação):** o Lattes aceitou ("Operação realizada com sucesso") e o item aparece na lista de Apresentação de trabalho e palestra (nº 2, 2024):
`ZZ-TESTE-LATTESFACIL Apresentação de teste (validação automática)`. **Apague este item.**

**Ocorrência (21/11/2026):** durante um teste de captura (campo "Nome do orientando" das orientações) a aba do Lattes saiu do currículo e abriu uma página pública
(buscatextual.cnpq.br, currículo de terceiro: só leitura, nada foi alterado ou salvo). Causa: o teste disparava `change`/`blur` no campo e o Lattes pesquisa o nome. Corrigido na ferramenta.

## Registro de 21/11/2026 (orientações)
Salvamento de teste pelo robô nas duas orientações: títulos `ZZ-TESTE-LATTESFACIL Orientação concluída de teste (validação automática)` (2023) e
`ZZ-TESTE-LATTESFACIL Orientação em andamento de teste (validação automática)` (2025), orientando "ZZ Orientando de Teste", UFMA, Farmácia.
Para apagar: Orientações > Orientações e supervisões concluídas / em andamento: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir. Resultado nas linhas seguintes.

**Resultado (21/11/2026, orientações):** o Lattes aceitou as duas ("Operação realizada com sucesso") e cada item aparece uma vez na lista:
`ZZ-TESTE-LATTESFACIL Orientação concluída de teste (validação automática)` (2023, Graduação) e `ZZ-TESTE-LATTESFACIL Orientação em andamento de teste (validação automática)` (2025, Graduação). **Apague os dois.**
Antes houve 2 tentativas que NÃO gravaram: o Lattes recusou o tipo de orientação com natureza TCC, e na "em andamento" o robô reaproveitou o formulário da "concluída" (corrigido: só reaproveita se o subtipo for o mesmo).

## Registro de 21/11/2026 (bancas de trabalhos de conclusão)
Salvamento de teste pelo robô: `ZZ-TESTE-LATTESFACIL Banca de teste (validação automática)` (2024, natureza Graduação, candidato "ZZ Candidato de Teste", UFMA, Farmácia).
Para apagar: Bancas > Participação em bancas de trabalhos de conclusão: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir.
**Resultado:** o Lattes aceitou ("Operação realizada com sucesso") e o item aparece uma vez na lista (Graduação, 2024). **Apague este item.**

## Registro de 21/11/2026 (bancas de comissões julgadoras)
Salvamento de teste pelo robô: `ZZ-TESTE-LATTESFACIL Comissão julgadora de teste (validação automática)` (2024, natureza Concurso público, UFMA).
Para apagar: Bancas > Participação em bancas de comissões julgadoras: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir.
**Resultado:** o Lattes aceitou ("Operação realizada com sucesso") e o item aparece uma vez na lista (Concurso público, 2024). **Apague este item.**

## Registro de 21/11/2026 (patente)
Salvamento de teste pelo robô: `ZZ-TESTE-LATTESFACIL Patente de teste (validação automática)` (depósito em 15/03/2020, INPI, nº BR1020200000001 fictício, invenção, inventores: você e "ZZ Coautor de Teste").
Para apagar: Patentes e Registros > Patente: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir.
**Resultado:** aceito ("Operação realizada com sucesso") e aparece uma vez na lista (2020). Tentativas anteriores desta noite não gravaram (faltavam depositante e situação). **Apague este item.**


## Registro de 21/11/2026 (faixa 5: produção técnica e registros, 13 itens)
Salvamento de teste pelo robô (`gerar_ciclo_salvar.py`), todos com o prefixo `ZZ-TESTE-LATTESFACIL`; cada item foi conferido na lista do Lattes (uma ocorrência por item).
Para apagar: Produções (ou Patentes e Registros) > a lista indicada: procurar o prefixo ZZ-TESTE-LATTESFACIL e excluir. **Apague os 13 itens.**
| Item | Onde apagar | Título gravado |
| --- | --- | --- |
| software_registro | Patentes e Registros > Programa de computador com registro | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (2020) |
| software_sem_registro | Produções técnicas > Programa de computador sem registro | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (2024) |
| produto | Produções técnicas > Produto tecnológico | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (Piloto, 2024) |
| processo_tecnica | Produções técnicas > Processos ou técnicas | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (Analítica, 2024) |
| trabalho_tecnico | Produções técnicas > Trabalhos técnicos | `ZZ-TESTE-LATTESFACIL Teste de Trabalhos técnicos (validação automática)` (2024) |
| relatorio_tecnico | Produções técnicas > Assessoria e consultoria / relatório técnico | `ZZ-TESTE-LATTESFACIL Teste de Assessoria e consultoria (validação automática)` (2024) |
| extensao_tecnologica | Produções técnicas > Trabalhos técnicos (mesma lista do trabalho técnico) | `ZZ-TESTE-LATTESFACIL Teste de Extensão tecnológica (validação automática)` (2024) |
| material_didatico | Produções técnicas > Desenvolvimento de material didático ou instrucional | `ZZ-TESTE-LATTESFACIL Teste de Desenvolvimento de material didático ou instrucional (validação automática)` (2024) |
| desenho_industrial | Patentes e Registros > Desenho industrial | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (2020) |
| marca_registrada | Patentes e Registros > Marca | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (2024) |
| topografia_circuito | Patentes e Registros > Topografia de circuito integrado | `ZZ-TESTE-LATTESFACIL Teste de único (validação automática)` (2024) |
| cultivar_protegida | Patentes e Registros > Cultivar protegida | `ZZ-TESTE-LATTESFACIL Teste de Cultivar protegida (validação automática)` (2020) |
| cultivar_registrada | Patentes e Registros > Cultivar registrada | `ZZ-TESTE-LATTESFACIL Teste de Cultivar registrada (validação automática)` (2024) |

Tentativas que NÃO gravaram (nada ficou no currículo): (a) trabalho/relatório/extensão/material com "É um dos 10 mais relevantes = sim": o Lattes avisou "Já existem cadastradas 5 produções relevantes" e não salvou; o gerador passou a usar "não"; (b) cultivares sem "Autoridade Nacional": "Campo Instituição de registro obrigatório não informado"; o gerador passou a preencher; (c) duas rodadas se sobrepuseram e deixaram um formulário vazio aberto (fechado, nada gravado).


## Registro de 21/11/2026 (faixa 7: eventos e cursos, 3 itens)
Salvamento de teste pelo robô, conferido na lista do Lattes (uma ocorrência por item). **Apague os 3 itens** (procure o prefixo ZZ-TESTE-LATTESFACIL):
| Item | Onde apagar | Título gravado |
| --- | --- | --- |
| participacao_evento | Eventos > Participação em eventos, congressos, exposições, feiras e olimpíadas | `ZZ-TESTE-LATTESFACIL Evento de teste (validação automática)` (Convidado, Conferencista, 2024) |
| organizacao_evento | Eventos > Organização de eventos, congressos, exposições, feiras e olimpíadas | `ZZ-TESTE-LATTESFACIL Teste de Organização de eventos, congressos, exposições, feiras e olimpíadas (validação automática)` (2024) |
| curso_ministrado | Produções > Curso de curta duração ministrado | `ZZ-TESTE-LATTESFACIL Teste de Curso de curta duração ministrado (validação automática)` (Extensão, 2024) |
Tentativas sem gravar: participação 2x (tipo da participação não escolhido: o robô só o escolhia sem a trava de salvamento; corrigido).
**Limite de "mais relevantes":** o Lattes responde "Já existem cadastradas 5 produções relevantes." e desmarca a opção Sim; por isso a matriz de organização (215/216) e de curso (212/213) tem 1 divergência esperada em F_RELEV=Sim. Não é defeito do app; ao apagar produções relevantes (inclusive os itens de teste da faixa 5 gravados com relevante=Sim antes da correção: programa sem registro, produto, processo/técnica, trabalho/relatório) a matriz passa 100%.


## Registro de 21/11/2026 (faixa 8: livros, prêmios e demais produções, 19 itens)
Salvamento de teste pelo robô, conferido na lista do Lattes (uma ocorrência por item; livros e capítulos: duas, uma por formulário). Todos com o prefixo `ZZ-TESTE-LATTESFACIL`. **Apague os 20 registros** (procure o prefixo em cada lista):
| Item | Onde apagar | Título gravado (após o prefixo: `Teste de ...`) |
| --- | --- | --- |
| premio | Prêmios e títulos (lista de prêmios) | `ZZ-TESTE-LATTESFACIL Teste de Prêmios e títulos (validação automática)` |
| texto_jornal_revista | Produção bibliográfica > Textos em jornais ou revistas | `ZZ-TESTE-LATTESFACIL Teste de Texto em jornal ou revista (magazine) (validação automática)` |
| traducao | Produção bibliográfica > Traduções | `ZZ-TESTE-LATTESFACIL Teste de Tradução (validação automática)` |
| prefacio_posfacio | Produção bibliográfica > Prefácio, posfácio | `ZZ-TESTE-LATTESFACIL Teste de Prefácio, posfácio (validação automática)` |
| partitura_musical | Produção bibliográfica > Partitura musical | `ZZ-TESTE-LATTESFACIL Teste de Partitura musical (validação automática)` |
| musica | Produção artística > Música | `ZZ-TESTE-LATTESFACIL Teste de Música (Apresentação de Obra, 2024) (validação automática)` |
| artes_cenicas | Produção artística > Artes cênicas | `ZZ-TESTE-LATTESFACIL Teste de Artes cênicas (Audiovisual, 2024) (validação automática)` |
| artes_visuais | Produção artística > Artes visuais | `ZZ-TESTE-LATTESFACIL Teste de Artes visuais (Animação, 2024) (validação automática)` |
| cartas_mapas | Produção técnica > Cartas, mapas ou similares | `ZZ-TESTE-LATTESFACIL Teste de Cartas, mapas ou similares (validação automática)` |
| maquete | Produção técnica > Maquete | `ZZ-TESTE-LATTESFACIL Teste de Maquete (validação automática)` |
| editoracao | Produção técnica > Editoração | `ZZ-TESTE-LATTESFACIL Teste de Editoração (validação automática)` |
| entrevista_midia | Produção técnica > Entrevistas, mesas redondas, programas e comentários na mídia | `ZZ-TESTE-LATTESFACIL Teste de Entrevistas, mesas redondas... (validação automática)` |
| redes_sociais | Produção técnica > Redes sociais, websites e blogs | `ZZ-TESTE-LATTESFACIL Teste de Redes sociais, websites e blogs (validação automática)` |
| relatorio_pesquisa | Produção técnica > Relatório de pesquisa | `ZZ-TESTE-LATTESFACIL Teste de Relatório de pesquisa (validação automática)` |
| outra_producao_artistica | Produção artística > Outra produção artística/cultural | `ZZ-TESTE-LATTESFACIL Teste de Outra produção artística/cultural (validação automática)` |
| outra_producao_bibliografica | Produção bibliográfica > Outra produção bibliográfica | `ZZ-TESTE-LATTESFACIL Teste de Outra produção bibliográfica (validação automática)` |
| outra_producao_tecnica | Produção técnica > Outra produção técnica | `ZZ-TESTE-LATTESFACIL Teste de Outra produção técnica (validação automática)` |
| manutencao_obra | Produção técnica > Manutenção de obra artística | `ZZ-TESTE-LATTESFACIL Teste de Manutenção de obra artística (Conservação, 2024) (validação automática)` |
| livro_capitulo (2 formulários) | Produção bibliográfica > Livros e capítulos (apagar o livro e o capítulo) | `ZZ-TESTE-LATTESFACIL Teste de Livros e capítulos: um livro e um capítulo (validação automática)` |

Tentativas sem gravar (nada ficou no currículo): música e artes cênicas (duração com texto, cortada em 5 caracteres), artes visuais e outra produção artística (instituição promotora obrigatória), livros e capítulos (ISBN, edição e página com texto longo demais). O gerador de teste passou a usar valores no formato real.
A lista de artes visuais no spec estava errada (`prc_arte_lista?f_cod_tipo=36`); a do Lattes é `pkg_arte_nova.lista?f_cod_tipo=AV` (corrigido em `itens/listas_lattes.json`).
**Limite de "mais relevantes":** como na faixa 7, a matriz de 16 itens tem 1 divergência esperada em F_RELEV=Sim ("Já existem cadastradas 5 produções relevantes"). Passam 100%: prêmio 11/11, tradução 314/314, livro 228/228, capítulo 237/237 (ISBN só com dígitos: o Lattes descarta letras).

## Registro de 21/11/2026 (ajuste do limite de relevantes, autorizado pelo usuário)
Varredura das 43 listas: 6 itens de teste ZZ-TESTE estavam com 'mais relevante = sim' (software PC seq 67, 78, 79; processo seq 81; produto seq 80; apresentação seq 45). Desmarcados (F_RELEV=não, salvos pela tela) processo/técnica seq 81 e produto seq 80; ficaram 4 marcados. Matriz da faixa 7 refeita: participação 121/121, organização 216/216, curso 213/213. Para voltar ao estado anterior, marcar 'sim' nesses dois itens (ou apagá-los).
