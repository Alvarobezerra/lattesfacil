# Orientação para o confronto com a avaliação do Antigravity

Elaborado em 21/11/2026 para ser usado na retomada de segunda-feira. Serve para comparar, sem se perder, o que o Claude Code registrou neste repositório com o que o Antigravity levantou (`docs/auditoria-antigravity/`).

## 1. O que foi feito (resumo por etapa)
Metodologia: `docs/metodologia-validacao-formularios.md` (8 fases: captura, diff, paridade, matriz de valores, preenchimento com leitura de volta, obrigatórios, salvamento de teste, fechamento).

| Frente | Situação em 21/11/2026 |
| --- | --- |
| Faixas 1 a 7 da matriz de prioridade (artigo, orientações, projetos, bancas, produção técnica/registros/patente, anais/apresentação, eventos/cursos) | fechadas no Lattes real: captura, paridade 0, matriz de valores sem falha, salvamento de teste conferido na lista |
| Faixa 8 (livros, prêmios e demais, 19 itens) | captura, paridade 0 e salvamentos feitos; 5 formulários com matriz em rodada na hora da pausa (`relatorio_pesquisa`, `outra_producao_artistica`, `outra_producao_bibliografica`, `outra_producao_tecnica`, `manutencao_obra`) |
| Fora da matriz (31 formulários: identificação, endereço, formação, atuação, citações, revisores, comitê, corpo editorial, idioma, licença...) | capturados, paridade 0 (exceto formação, em ajuste); lupas de formação/atuação tratadas no código; matrizes e salvamentos `ZZ-TESTE` em andamento |
| Itens pendentes transversais | perfis diferentes de usuário; caderno de resumos real; artigo aceito (salvamento); decisão dos PDFs de Adriana e Marcelino |

## 2. Onde estão os registros (o que o Antigravity deve ser comparado com)
| O que | Onde |
| --- | --- |
| Estado geral, pendências bloqueantes, achados por item | `docs/validacao/STATUS.md` |
| Ordem dos itens cruzada com a matriz de prioridade | `docs/validacao/ORDEM_DOS_ITENS.md` |
| Operações feitas no Lattes real e itens de teste a apagar | `docs/validacao/LOG_OPERACOES_NOITE.md` |
| Roteiro das ferramentas em lote | `docs/validacao/RETOMADA_FAIXA5.md` |
| Capturas reais dos formulários (campos, opções, estados, listas) | `docs/campos-lattes/ref/<item>/` |
| Resultados da matriz de valores por caso | `docs/campos-lattes/ref/<item>_f5/` |
| Exceções justificadas da paridade | `docs/campos-lattes/ref/<item>/excecoes.json`, `_excecoes_globais.json`, `_excecoes_matriz.json` |
| Especificações geradas (o espelho) | `itens/especificacao/<item>.json` (gerado por `itens/gerar_specs.py`) |
| Testes de regressão | `tests/teste_spec_*.py`, `tests/teste_valida_paridade.py`, `tests/teste_ponte_legado.py` |
| Histórico dos commits por frente | `git log --oneline` (mensagens `feat(faixaN)`, `feat(bancas)`, `feat(patente)`, `wip(fora-da-matriz)`) |

Arquivos do Antigravity já presentes: `docs/auditoria-antigravity/` (README, DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO, DOCUMENTO_REFERENCIA_CORRELACAO_CLAUDE_ANTIGRAVITY, PLANO_CONTRALIDACAO_E_ESCALA, BACKLOG_TECNICO_FASE2, RELATORIO_FINAL_MAPEAMENTO e auditorias por item). Comece pelo `DOCUMENTO_REFERENCIA_CORRELACAO_CLAUDE_ANTIGRAVITY.md`.

## 3. Como conduzir o confronto (passo a passo)
1. **Fixe a unidade de comparação: o item e o campo.** Compare por `<item>` + `name` do campo do Lattes (ex.: `patente` + `f_sta_inovacao`), não por texto livre dos relatórios.
2. **Para cada item, monte 5 colunas:** campos (nº e nomes), opções de cada seleção/rádio, regras de obrigatório, dependências entre campos (um campo só vale depois de outro) e listas/lupas (grades). Preencha com o que cada ferramenta registrou.
3. **Classifique cada diferença** em: (a) campo/opção ausente de um lado; (b) rótulo diferente; (c) opção diferente; (d) regra diferente (obrigatório, dependência, limite); (e) estado do item (um diz "fechado", outro "pendente").
4. **Resolva as diferenças só olhando o Lattes real**, nunca escolhendo um lado pela confiança: abra o formulário, leia o HTML/valores e registre a evidência (campo, valor lido, data).
5. **Registre o resultado** em um arquivo novo (`docs/validacao/CONFRONTO_ANTIGRAVITY.md`): item, diferença, evidência, decisão, e atualize `STATUS.md` se algo reabrir um item "fechado".

## 4. Cuidados (erros que já aconteceram e que contaminam comparações)
- **Texto de rádio deslocado:** no Lattes o texto de "Sim/Não" vem ANTES do botão; capturas por proximidade atribuem o texto ao botão errado (achado na patente). Se o outro levantamento mostrar "Não" para o valor `S`, confira no HTML antes de concluir que há divergência.
- **Valores com espaço no fim:** `34 `, `35 ` (tipo de mestrado em bancas), valores de prefácio. Comparação exata falha por causa disso; normalize espaços, mas registre que o valor real tem espaço.
- **Rótulo vazio ou só "*":** alguns campos (ex.: instituição na comissão julgadora) só têm o asterisco vermelho como texto ao lado; a obrigatoriedade pode vir do asterisco e não da mensagem do servidor.
- **Campo habilitado que parece bloqueado e o inverso:** o Lattes escreve `disable="true"` (atributo errado) em campos de lupa que ficam editáveis; confira pela classe `input-lupa` e pela função da lupa (`sele_inst`, `escolhe_inst`).
- **Dependências escondidas:** instituição/curso só aceitam valor depois da natureza; tipo de orientação só com mestrado/doutorado; tipo da participação em evento depende da forma. Um levantamento que só preencheu o campo isolado pode dizer "aceita" onde o Lattes recusa.
- **Limites do Lattes:** F_RELEV=Sim aceita no máximo 5 produções relevantes; listas têm limites que variam. Falha por limite não é divergência de formulário (virou exceção `limite do Lattes` em `_excecoes_matriz.json`).
- **Listas que não gravam sem requisitos:** o salvamento da patente só passou com depositante e situação; "salvou sem erro" é diferente de "apareceu na lista". A prova do Claude Code é sempre a linha na lista do Lattes.
- **Estado do currículo muda os resultados:** o currículo do usuário já tem 5 relevantes, itens de teste e dados reais. Duas rodadas em momentos diferentes podem divergir só por isso; anote a data/hora e o que mudou.
- **Número de casos não é comparável:** a matriz do Claude Code gera 100 a 270 casos por item (opção por opção, limites de tamanho, acentos). Compare resultado (OK/falha e quais campos), não a contagem.
- **Dois sistemas no mesmo login do Lattes:** não rode as duas ferramentas ao mesmo tempo no currículo; alertas nativos e a sessão (que expira em 15 a 20 minutos) causam falsos erros.
- **Dados pessoais e credenciais:** não cole o código do currículo (`f_cod`), senhas ou códigos de acesso em relatórios que vão para o repositório; ao compartilhar evidências com outra ferramenta, remova URLs com `f_cod`.
- **Itens de teste no Lattes:** títulos com `ZZ-TESTE-LATTESFACIL` listados em `LOG_OPERACOES_NOITE.md` devem ser apagados antes de qualquer envio do currículo ao CNPq. Nada foi enviado ao CNPq.

## 5. Critérios para aceitar ou rejeitar uma divergência
- **Aceitar a favor do Claude Code** quando houver captura em `ref/<item>/` + leitura de volta na matriz + item gravado na lista.
- **Aceitar a favor do Antigravity** quando ele trouxer evidência reproduzível no Lattes real que a captura não tinha (ex.: estado que só aparece com certa escolha). Nesse caso: recapturar o item, ajustar o spec e rodar paridade e matriz de novo.
- **Em dúvida:** não decidir por documento; reabrir o formulário e conferir. Registrar como pendência bloqueante no `STATUS.md` até conferir (regra de zero pendência).

## 6. Próximos passos na retomada (segunda-feira)
1. **Ler o estado final das rodadas** deixadas em andamento: faixa 8 (5 formulários) e fora da matriz (formação, pós-doutorado, formação complementar e demais matrizes); conferir `STATUS.md` e `git log`; commitar os relatórios `*_f5` que ficaram modificados.
2. **Fechar fora da matriz:** matrizes restantes (citações, comitê, corpo editorial, revisores, endereço, identificação, idioma, licença, outras informações, texto inicial), salvamentos `ZZ-TESTE` dos itens com título livre (artigo aceito, formação complementar, atuação, revisores, comitê, corpo editorial), `tests/teste_spec_fora_matriz.py` e a suíte.
3. **Executar o confronto** (seções 3 a 5) com os arquivos do Antigravity e abrir pendências onde houver diferença não resolvida.
4. **Perfis diferentes de usuário:** escolher 2 a 3 perfis (Richard, Márcia e os coautores do Ciclo 1; confirmar o estado dos PDFs de Adriana e Marcelino) e repetir o fluxo documento → formulário → envio pela extensão; o OCR dos PDFs de imagem é pré-requisito.
5. **Caderno de resumos real:** testar com um PDF de congresso real além do layout sintético.
6. **Fechamento operacional:** apagar os itens `ZZ-TESTE-LATTESFACIL` no Lattes, rodar `python extensao/build.py`, recarregar a extensão, reiniciar `server.py` (porta 8765) e atualizar `STATUS.md` (a tabela de pendências no topo ainda cita "demais 55 itens sem captura real" e precisa ser corrigida).

## 7. Como retomar com custo baixo
Abra uma conversa nova por frente, com contexto limpo, mandando ler primeiro este arquivo, o `STATUS.md` e o `RETOMADA_FAIXA5.md`. Garanta antes: Lattes logado numa aba do mesmo grupo do Chrome da sessão, receptor local ativo (`python ferramentas/receptor_captura.py`, porta 8798) e app na porta 8765. Rode uma sessão por vez na aba do currículo.
