# Plano de implantação dos 23 itens (reconhecer → estruturar → preencher → enviar)

Objetivo: todo documento que o pesquisador enviar é **reconhecido**, vira um **formulário estruturado** na plataforma e é
**preenchido no Lattes** pela extensão/agente, que só para no "Salvar". Hoje 5 de 23 itens estão completos; este plano
leva os outros 18 ao mesmo nível, em ondas, com a mesma definição de "pronto" para todos.

## 1. Arquitetura: um item = uma especificação, não código novo

Em vez de escrever tela + leitor + script para cada item, cada item passa a ser **dados**:

| Peça | Onde | O que é |
| --- | --- | --- |
| Especificação do formulário | `itens/especificacao/<id>.json` | Gerada por `itens/gerar_specs.py` a partir do mapeamento real do Lattes (`docs/campos-lattes`): campos, nome técnico, tipo, opções, limite, obrigatórios, abas, como abrir. |
| Curadoria | `itens/curadoria.json` | O que só um humano sabe: rótulos faltantes, obrigatórios que o mapeamento não casou, de onde vem cada campo (documento, perfil do usuário, valor fixo) e valores-padrão. |
| Reconhecimento | `classificador.py` | Regras (regex + peso + motivo) por item. Já existem as 23; cada onda ajusta com documentos reais. |
| Leitor | `itens/leitores.py` | Função `extrair(texto, usuario) -> {chave: valor}` por item, usando auxiliares comuns (datas, carga horária, nomes, evento, instituição). |
| Formulário na tela | `static/` (renderizador genérico) | Desenha a especificação: grupos por aba, obrigatórios marcados, listas com as opções reais do Lattes, "faltam N obrigatórios". |
| Preenchimento no Lattes | `extensao/autofill_core.js` (genérico) | Recebe `{item, variante, abrir, campos:[{name,tipo,valor}]}`, abre o formulário (`modalCV2.setarUrl`) e preenche por `name`/`tipo`; cadastros controlados e grades têm tratadores próprios. |
| Casos de teste | `tests/amostras/<id>/` | Documentos de exemplo (anonimizados) + JSON esperado. |

Os 5 itens atuais continuam como estão; migram para o modelo só se houver ganho.

## 2. Definição de "pronto" (igual para todos os itens)

Um item só vira `implementado: true` quando **todos** os critérios passam:

1. **Reconhecimento**: ≥ 3 documentos reais diferentes são classificados no item certo (confiança ≥ 0,70) e nenhum documento de outro item é classificado nele (30/30 do conjunto de testes continua passando).
2. **Estrutura**: a especificação existe, os **obrigatórios do Lattes estão marcados** e conferem com as mensagens do botão Salvar.
3. **Leitura**: os campos que o documento realmente traz são extraídos; o que ele não traz fica vazio com **aviso explicando por quê** (nunca inventar).
4. **Revisão**: o formulário aparece na tela com listas reais, bloqueia o envio se faltar obrigatório e mostra o que veio do documento e o que é preenchimento do usuário.
5. **Preenchimento**: o formulário do Lattes é aberto e preenchido por completo, com relatório do que não foi possível; **nunca clica em Salvar**.
6. **Verificação no Lattes real**: execução de ponta a ponta com o usuário em currículo de teste, sem gravar, anotada no `docs/campos-lattes/VALIDACAO.md`.
7. **Documentação**: linha do item atualizada em `docs/fluxo-intuitivo.md`.

## 3. Ondas

Ordem por **volume de uso × simplicidade do formulário** (formulário único, URL direta, poucos obrigatórios, documento padronizado).

| Onda | Itens | Por quê | Campos / obrigatórios |
| --- | --- | --- | --- |
| **0. Fundação** | gerador de especificações, renderizador genérico, preenchedor genérico, API `/api/itens/<id>/spec`, amostras | Sem isso cada item custa dias; com isso custa horas. | — |
| **1. Certificados simples** | participacao_evento, curso_ministrado, formacao_complementar, organizacao_evento, premio | São os documentos mais comuns do pesquisador; todos de formulário único e URL direta. | 13/5, 20/3, 5/3, 21/4, 4/2 |
| **2. Declarações com vínculo** | banca, revisor_periodico, corpo_editorial, atuacao_profissional, idioma, licenca | Poucos campos; dependem de cadastros controlados (periódico, instituição) e de datas de período. | 16/5, 8/1, 8/1, 13/4, 10/1, 5/0 |
| **3. Produção com identificador** | artigo_aceito, livro_capitulo, relatorio_tecnico | DOI/ISBN permitem enriquecer por Crossref/OpenAlex; livro tem 2 formulários (livro e capítulo). | 15/4, 49/14, 20/3 |
| **4. Registros** | patente, software_registro | Muitos campos, mas documentos oficiais (INPI) muito estruturados. | 28/3, 30/7 |
| **5. Formulários múltiplos** | projeto (5 formulários), formacao_academica (10 formulários) | Escolha de variante por documento; equipe, financiador e instituição exigem grades. Por último pelo risco. | 173/54, 134/23 |

Cada onda termina com: conjunto de testes verde, rodada no Lattes real, e atualização do catálogo (`implementado: true`).

## 4. Fluxo de trabalho de cada item (checklist de 1 a 2 dias na onda 1)

1. **Amostras**: reunir 3+ documentos reais (o usuário envia; anonimizar), colocar em `tests/amostras/<id>/` com o JSON esperado.
2. **Curadoria**: revisar `itens/especificacao/<id>.json`; completar rótulos e obrigatórios em `itens/curadoria.json`; definir a origem de cada campo (`documento` | `usuario` | `fixo`).
3. **Reconhecimento**: ajustar regras do `classificador.py` até as amostras caírem no item certo sem roubar de outro.
4. **Leitor**: implementar `extrair()` e testar contra o JSON esperado.
5. **Tela**: conferir o formulário gerado; ajustar ordem e dicas.
6. **Preenchimento**: rodar no Lattes de teste (sem salvar); registrar divergências.
7. **Fechamento**: marcar `implementado`, atualizar documentação, abrir PR da onda.

## 5. Decisões e riscos

- **Cadastros controlados** (periódico, instituição, curso, área, agência): tratador único com escolha por nome idêntico ou parecido (limiar), pergunta prévia na plataforma quando ambíguo. Já existe para instituição/curso/área.
- **Campos que o documento não traz** (ex.: forma de participação, natureza, país): valor-padrão curado + marcação "confira"; só obrigatórios sem valor bloqueiam o envio.
- **Perfil do usuário** como origem: nome, instituição de vínculo e idioma vêm do currículo/cadastro, não do documento.
- **Sem amostras reais, não há "pronto"**: leitor escrito sem documento real é palpite. Por isso o passo 1 de cada item pede amostras ao usuário.
- **Lattes muda**: o mapeamento é versionado (`docs/campos-lattes`); rodar `gerar_specs.py` após novo mapeamento e ver o diff.
- **Segurança**: o preenchimento nunca salva; o envio ao Lattes só ocorre na sessão já logada do usuário.

## 6. Estado atual (16/11/2026)

- **Completos (5)**: anais, apresentacao, artigo, orientacao_concluida, orientacao_andamento.
- **Onda 0 (fundação) feita**: `itens/gerar_specs.py` + `itens/especificacao/*.json` (18 itens, 21 variantes de formulário), registro `itens/__init__.py`, API `GET /api/itens/<id>/spec`, formulário genérico na tela (abas, obrigatórios *, listas reais do Lattes) e preenchedor genérico (`tipo_producao: "generico"`) no `AUTOFILL_TEMPLATE`/extensão, que abre o formulário pelo `modalCV2.setarUrl`.
- **Onda 1 em beta**: leitores de participacao_evento, organizacao_evento, curso_ministrado e formacao_complementar (`itens/leitores.py`). Reconhecidos e com formulário estruturado, **mas sem amostras reais e sem rodada no Lattes** (critérios 1 e 6 abertos).
- **Ondas 2 a 4 em beta (16/11/2026)**: leitores em `itens/leitores_onda2.py` para revisor_periodico, corpo_editorial, atuacao_profissional, idioma, licenca, artigo_aceito, relatorio_tecnico e software_registro, testados só com textos sintéticos (`tests/teste_leitores_onda2.py`, 8/8). Banca, premio, projeto e patente já tinham leitor testado com documentos reais. Faltam amostras reais e rodada no Lattes para fechar os critérios 1 e 6 de todos eles.
- **Sem leitor ainda**: livro_capitulo (2 formulários) e formacao_academica (10 formulários), por dependerem de escolha de variante.
- **Pendente**: leitores de livro_capitulo e formacao_academica, curadoria dos obrigatórios (o casamento automático errou em campos sem rótulo, ex.: `F_FORMA`), campos dependentes (ex.: `F_TPO` depende de `F_FORMA`), cadastros controlados no genérico (periódico, instituição, agência) e variantes múltiplas (livro/capítulo, projeto, formação acadêmica: hoje usa a 1ª variante).
