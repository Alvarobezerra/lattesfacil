- **17/11/2026 — tratador genérico (extensão 0.8.0):** a extensão passou a listar, confirmar e excluir qualquer item de `itens/listas_lattes.json`
  (55 itens). A linha de cada lista traz o formulário do item (`setarUrl`); o item novo é reconhecido por diferença de nºs antes/depois de salvar.
  Validado só na leitura das listas do currículo real; salvar/excluir fora da apresentação ainda não rodaram no Lattes.
- **Regra do ciclo real:** nunca excluir item cujo título não seja o fictício; `confirm()` é trocado antes de `del()` para a caixa nativa não travar.
- **Pendências de teste:** ciclo salvar → conferir → excluir → reconferir nos itens com leitor e abertura direta (participação em evento,
  organização, curso ministrado, formação complementar, prêmio, projeto, atuação, revisor, corpo editorial, idioma, licença); depois os de janela de escolha.
- **17/11/2026 — melhorias:** (1) o "problema" das janelas de escolha (patente, livro, formação...) era do teste: os formulários abrem direto pela URL da variante;
  75 variantes foram abertas no currículo real (sem salvar) e todas trouxeram os campos obrigatórios. (2) Orientações ganharam especificação (18 campos).
  (3) Leitores: periódico em inglês ("Journal of ...") e País da instituição no registro de software. (4) Formulários de registro agora levam o nº/instituição
  reais na URL (antes iam com um nº de exemplo). (5) Alteração: a plataforma lista os itens do Lattes e altera o escolhido (extensão 0.9.0); ainda não
  executada no Lattes real.
- **17/11/2026 — 1º teste real fora da apresentação (prêmio):** o formulário abriu e foi preenchido, mas parou em "falta você salvar": o caminho genérico não tinha Salvar
  automático. Corrigido (extensão 0.9.1: clica em Salvar quando não há obrigatório vazio nem alerta). Atenção para o próximo teste: uma janela de formulário esquecida
  aberta no currículo pode atrapalhar (recarregar o currículo antes de cada ciclo).
- **17/11/2026 — 2º defeito no 1º teste real:** a tela passava o nome do item ("Prêmios e títulos") onde a extensão e o registro de envios esperam o id (`premio`);
  a lista, a confirmação e a remoção nunca casariam. Corrigido (`__generico.id`, extensão 0.9.2).
- **17/11/2026 — ciclo real do prêmio completo (incluir, alterar, remover, reconferir) e 3º defeito:** em itens com autores (ex.: curso ministrado) o Lattes recusa o titular
  digitado na grade; ele precisa ser escolhido em "Listar todos". A correção parcial (garantir o titular na lista de autores) está em `genGrades()`, mas a extensão ainda
  precisa selecionar o titular pela lista do Lattes. Outro risco: o `alert()` final do preenchedor trava a aba do Lattes na automação quando o Salvar falha.
- **17/11/2026 — titular nos autores (extensão 0.9.3):** inspecionado no Lattes real (sem salvar): "Listar todos" mostra `a.label` com "Nome (CITAÇÃO)" e clicar nele põe o titular na tabela de
  autores. O preenchedor genérico agora escolhe o titular por essa lista e só digita os demais autores. Ainda falta repetir o ciclo do curso ministrado com ela.
- **17/11/2026 — 2º item testado de ponta a ponta no Lattes real: curso ministrado** (incluir, confirmar na lista, remover pela plataforma, reconferir). Defeitos que apareceram no caminho e foram
  corrigidos: titular nos autores por "Listar todos". Itens com autores agora seguem o mesmo caminho. Próximos: participação em evento, organização de evento, idioma, atuação profissional.
- **17/11/2026 — participação em evento (1ª tentativa):** o documento empatou com formação complementar (a tela pede 1 clique de confirmação). O Lattes não oferece "tipo" para a forma
  "Ouvinte"; o preenchedor tratava isso como erro e deixava de salvar. Corrigido na extensão 0.9.4. Defeito de mensagem: "cliquei em Salvar, mas o item não apareceu" é exibido
  também quando o Salvar não foi clicado; vale separar os dois casos.
- **17/11/2026 — participação em evento: ciclo real completo** (37 -> 38 -> 37) após o ajuste do campo dependente (extensão 0.9.4). Itens validados de ponta a ponta no Lattes real: apresentação, prêmio (incl. alteração), curso ministrado, participação em evento.
- **17/11/2026 — organização de evento: ciclo real completo** (6 -> 7 -> 6), sem defeito novo. Validados de ponta a ponta: apresentação, prêmio (incl. alteração), curso ministrado, participação e organização de evento.
- **17/11/2026 — formação complementar (1ª tentativa):** o Lattes recusa instituição e curso digitados; é preciso escolhê-los pelo link (cadastros controlados). Esse é o mesmo bloqueio esperado para
  formação acadêmica, atuação profissional, bancas e projetos (instituição/curso/órgão). Próxima melhoria: tratador de cadastro controlado no preenchedor (abrir a lupa, buscar por nome e escolher a opção idêntica).
  Também: o leitor extrai o curso com prefixo e aspas (`extensão "Estatística com R...`).
