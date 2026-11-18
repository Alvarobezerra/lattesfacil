# Regras para criar documentos simulados de comprovação (rotina de teste)

Objetivo: ter, para **cada tipo de cadastro do Lattes**, um documento de exemplo que percorra o mesmo caminho do
documento real: **PDF → texto → classificador → leitor → campos do formulário**. Os documentos são gerados por código,
são **fictícios** e servem para testar o LattesFácil sem expor dados reais.

## Como rodar a rotina

```bash
python tests/teste_amostras_sinteticas.py              # gera os PDFs e confere tudo
python tests/teste_amostras_sinteticas.py --so-gerar   # só (re)gera os PDFs, para subir na tela
python tests/teste_amostras_sinteticas.py banca premio # só estes itens
```

- Casos: `tests/amostras_sinteticas/catalogo.py` · PDFs gerados: `tests/amostras_sinteticas/pdf/`.
- Resultado por documento: `OK`, `FALHA` (quebra o código de saída), `LACUNA` (limite conhecido do leitor, marcado no
  catálogo), `AVISO` (item sem regra no classificador ainda; não quebra).
- A rotina também falha se **algum item de `itens/especificacao/` ficar sem documento** (cobertura obrigatória).

## Regras de criação

0. **O nome do pesquisador aparece em TODOS os documentos** (exceto os negativos). É o nome do usuário do teste, o mesmo
   que o sistema usa para achar "quem é você" no documento (papel na banca, coordenador do projeto, autoria). Escreva o
   nome completo como o documento real o faria; documentos de citações, ficha cadastral e afins também levam o nome
   (a forma de citação `SOBRENOME, I. N.` é aceita). A rotina falha (`FALHA ... o nome do pesquisador não aparece`) se um
   documento ficar sem ele. O nome vem da constante `PESQUISADORA` do catálogo, nunca é digitado dentro do texto; para
   usar o seu: `python tests/teste_amostras_sinteticas.py --nome "Seu Nome Completo"` (ou a variável `LATTES_NOME`), ou grave o nome uma vez em `tests/amostras_sinteticas/nome.local.txt` (ignorado pelo git; a pasta `pdf/` também é ignorada, pois passa a conter dado pessoal).
   Atenção: com nome real, os PDFs gerados passam a conter dado pessoal; não os publique nem versione sem querer.

1. **Um documento por item, no mínimo.** O nome do arquivo é o id do item (`premio.pdf`). Variações do mesmo item usam
   `<id>__<variacao>.pdf` (`premio__so_ano.pdf`). Todo id novo em `itens/especificacao/` exige um caso novo no catálogo.
2. **Tudo é fictício e identificável como tal.** Pessoa: a personagem `Helena Moraes Tavares` (ou o nome passado em `--nome`); instituições
   com nome "Exemplar" (`Universidade Federal do Vale Exemplar`); nunca nomes, CPFs, matrículas, e-mails ou endereços reais.
   Números de registro usam ano 2099 (`BR 10 2099 000001 0`); CPF `000.000.000-00`; DOI `10.9999/...`; ISBN `978-00-...`;
   URLs `.invalid`. Todo PDF leva o rodapé "DOCUMENTO FICTÍCIO - ... sem valor legal" e metadado `subject` equivalente.
3. **Não imitar documento oficial de identidade nem timbre real.** Nada de RG/CPF/CNH, brasão ou logotipo. Para
   *identificação* e *endereço* use "ficha cadastral institucional" e "comprovante de endereço profissional". Órgãos
   citados só pelo nome quando o classificador precisa da palavra (ex.: INPI), sempre com a marca de fictício.
4. **Redigir como o documento real.** Use o vocabulário que o tipo de documento realmente usa ("Certificamos que...",
   "Declaramos que...", "Portaria", "Carta de aceite"), em português com acentos, e inclua **todos os dados que o
   formulário do Lattes pede** para aquele item (consulte os campos obrigatórios na especificação): título, instituição,
   datas completas (`20 de outubro de 2023`), carga horária, papel, número de registro etc.
5. **Texto selecionável, uma página**, salvo o caderno de anais (≥ 13 páginas e ≥ 10 resumos). Fonte padrão do PDF,
   sem imagem de fundo. Só use caracteres do Latin-1 (acentos, `º`, `ª`); evite travessões e aspas curvas no corpo.
6. **A resposta certa vem do catálogo, não do leitor.** Em `campos`, escreva o que o documento *realmente* contém.
   Nunca ajuste o texto do documento ou o valor esperado só para o teste passar: se o leitor falhar, o teste deve falhar.
7. **Lacuna conhecida = variação marcada.** Para exercitar um redator diferente (ex.: só o ano, sem data completa), crie
   a variação com `lacuna="motivo"`. Ela aparece como `LACUNA` e não quebra a rotina; quando o leitor passar a lê-la,
   a rotina avisa `RESOLVIDA` e a marca deve ser removida.
8. **`classe` diz o que o classificador deve devolver em 1º lugar.** Item sem regra no classificador usa `classe=None`
   (gera `AVISO`); ao criar a regra, troque para o id do item. Documentos de itens vizinhos não podem "roubar" o item
   (confira o `AVISO` quando um documento cai em outro item: é falso positivo a corrigir).
9. **Sempre incluir casos negativos.** Um documento irrelevante e um PDF sem camada de texto (escaneado): o
   classificador deve responder `escolher`, nunca inventar um item.
10. **Ao acrescentar um item novo no sistema:** (a) criar a especificação; (b) criar o caso no catálogo com `classe=None`;
    (c) ao implementar regra e leitor, preencher `classe` e `campos`; (d) rodar a rotina completa e a suíte
    `tests/` antes de fechar. Ao tirar uma regra ou leitor, ajustar o catálogo na mesma alteração.
11. **Dados que mudam no tempo** (data da consulta de citações, vigência "atual") usam datas fixas no catálogo, nunca
    `hoje()`, para a rotina ser repetível.
12. **Não versionar PDFs reais aqui.** Documentos reais (anonimizados) continuam em `tests/teste_amostras.py` e na
    pasta `Teste` ao lado do projeto; os sintéticos nunca substituem a rodada com documentos reais exigida no plano de
    implantação (critérios 1 e 6).

## Modelo de caso

```python
dict(arquivo="premio", item="premio", classe="premio",
     titulo="MENÇÃO HONROSA",
     corpo=f"Conferimos a {PESQUISADORA} menção honrosa pelo melhor trabalho ..., em 20 de outubro de 2023.",
     campos={"f_titulo": "Menção honrosa", "f_ano": "2023"})   # nome do campo do Lattes: trecho esperado
```

## Cobertura (17/11/2026)

- 59 itens da especificação + 5 itens só do classificador (anais, apresentação, artigo, orientação concluída e em
  andamento) + caderno de anais + 2 negativos, mais 4 variações com lacuna conhecida.
- Com regra no classificador: 23 itens (todos `OK`). Sem regra ainda: 41 itens (`AVISO`), que são o backlog das ondas
  seguintes; os que hoje caem em item errado (prefácio, editoração, tradução, partitura, manutenção de obra e banca de
  comissão julgadora) são os falsos positivos a tratar primeiro.
- Leitores com campos conferidos: 16 itens.

## Execução ponta a ponta no Lattes (rotina autônoma, hoje só "apresentação")

Valida de verdade: enviar → salvar → conferir na lista → excluir → reconferir. Só o tipo **apresentação** tem lista,
confirmação e exclusão automáticas (`LISTAS_LATTES` em `extensao/background.js`); os demais salvam, mas a exclusão
é manual até serem mapeados.

**Pré-requisitos (únicos passos humanos):** servidor no ar (`python server.py`), extensão instalada, login no Lattes
(gov.br) numa aba do currículo e login no LattesFácil. A sessão do Lattes dura; se cair, a rotina para e pede o login.

**Passos**
1. Gerar os PDFs (`python tests/teste_amostras_sinteticas.py`) e subir `apresentacao.pdf` no LattesFácil.
2. Conferir no formulário: título limpo, ano, cidade, e que o titular está nos autores. Clicar em *Enviar e Cadastrar no
   Lattes*. O sucesso é a mensagem "salvo: o formulário fechou após Salvar".
3. **Conferir na lista do currículo** (não confiar só na mensagem): ler `prc_tec_demais_lista?f_cod_tipo=2J&f_cod=<cv>`
   dentro de uma aba do currículo e achar o item novo pelo título fictício; anotar o `f_seq`.
4. **Excluir só o item de teste**: abrir `prc_tec_apres?f_cod=<cv>&f_seq=<seq>` pelo `modalCV2.setarUrl`, **conferir que o
   título aberto é o fictício** (se divergir, não excluir), trocar `confirm` por `() => true` na janela do formulário
   **antes** de chamar `del()` e chamar `del()` depois de um `setTimeout`. A caixa nativa de confirmação trava a aba e a
   automação, por isso ela nunca pode ser aberta.
5. **Reentrar e reconferir**: ler a lista de novo; o `f_seq` e o título de teste não podem existir e os demais itens
   (reais) têm de continuar, com a mesma contagem de antes do envio.
6. Se uma janela "carregando" ficar presa depois de salvar, fechá-la pelo X da janela modal.

**Segurança:** nunca clicar em *Enviar ao CNPq*; nunca excluir item cujo título não seja o fictício; registrar a lista
de `f_seq` antes e depois. O currículo fica com o aviso "alterações ainda não enviadas ao CNPq" até o usuário decidir.

**Resultado de 17/11/2026:** 2 ciclos. No 1º, o título saiu com "de autoria de…" e a lista de autores vazia (documento
fora do layout real), então o Lattes recusou salvar até adicionar o titular à mão; hoje isso é a variação
`apresentacao__autoria_no_titulo` (LACUNA). No 2º, com o layout real, salvou sozinho (nº 70), foi excluído e a lista
voltou ao estado original.

## Etapa PLATAFORMA (reconhecimento, valores e vínculo com o Lattes)

```bash
python tests/teste_amostras_sinteticas.py --so-gerar    # PDFs com o seu nome
python tests/teste_plataforma_sinteticos.py              # passa cada PDF pelo caminho do /api/extract
```

Confere, por documento: (1) item reconhecido; (2) valores extraídos (`campos` do catálogo); (3) obrigatórios do Lattes
que o documento traz mas ficaram vazios (`nao_traz` isenta o que o documento não contém); (4) vínculo com o Lattes:
especificação com forma de abertura, lista do Lattes mapeada (`itens/listas_lattes.json`) e tratador da extensão para
aberturas por "janela de escolha". Empate de itens vira observação ("pediu confirmação do usuário"), e a leitura é feita
como o servidor faz depois do clique. O relatório vai para `tests/amostras_sinteticas/pdf/relatorio_plataforma.json`.

**Resultado de 17/11/2026 (18 OK, 5 lacunas, 41 sem regra, 7 falhas):**
- `livro_capitulo`, `patente`, `software_registro`, `formacao_academica`: o Lattes abre uma janela de escolha antes do
  formulário (`informaDOI`, `infDadPat`, `selecionarNivel`) e a extensão não trata (19 variantes no total). `orientacao_*`
  não têm especificação de formulário.
- `artigo_aceito`: o periódico (que a carta traz) não é lido. `software_registro`: o País não é preenchido.
- Empates que pedem confirmação do usuário: participação em evento x formação complementar; formação complementar x
  formação acadêmica.
- O nome padronizado do arquivo usa `AUTOR` em vários itens (e `PINHEIRO` nos anais) em vez do sobrenome do usuário.

## Histórico consolidado dos testes (para saber onde testamos mais, onde há êxito e onde aprimorar)

- **Registro:** `tests/historico/execucoes.jsonl` (uma linha por execução × item × etapa; sem dado pessoal: o nome do titular
  vira `<titular>`). As duas rotinas automáticas gravam sozinhas ao rodar completas (sem filtro de item). O que roda no
  currículo real (salvar, conferir, excluir, reconferir) é registrado pelo executor:
  `python tests/amostras_sinteticas/historico.py registrar manual_lattes_real <item> <etapa> <ok|falha|lacuna|aviso|parcial> "<o que aconteceu>"`
- **Etapas:** `modulos`, `plataforma`, `vinculo_lattes`, `lista_lattes`, `lattes_salvar`, `lattes_conferir`, `lattes_excluir`,
  `lattes_reconferir` (definidas em `tests/amostras_sinteticas/historico.py`).
- **Painel:** `python tests/amostras_sinteticas/painel.py` gera [historico-testes-simulados.md](historico-testes-simulados.md)
  com o resumo por etapa, a matriz item × etapa, onde testamos mais/menos, onde já há êxito, onde aprimorar (por gravidade),
  o registro cronológico das ações e as notas de `tests/historico/notas.md`. Não edite o painel à mão.
- **Regra:** toda ação testada (inclusive as manuais no Lattes) precisa de um registro no histórico, com o resultado e o que
  aconteceu; ao fechar uma rodada, rodar o painel e conferir a seção 5 ("Onde aprimorar").
- Variações de documento (`<id>__<variacao>`) entram no histórico mas não substituem o resultado do item na matriz.
