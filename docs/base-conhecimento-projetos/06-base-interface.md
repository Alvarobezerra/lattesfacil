# Base de interface — Gestão de projetos

## Referência e escopo

Revisada a partir da leitura das oito páginas de
`resumo-executivo-projetos-lattesdata.pdf`, incluindo inspeção visual das telas
nas páginas 6 e 7. Mantém `platform.css`, `platform-shell.js`, menu lateral,
tipografia e cores do novo layout. Entrada: `/projetos.html`.

| Diretriz do PDF | Base implementada |
| --- | --- |
| Central visual (p. 6) | Destaque, imagens do material, progresso calculado por entregas, grupos Coordeno/Colaboro, busca e filtros |
| Quadro científico (p. 7) | A fazer, Em execução, Revisar, Concluído; criação de entregas e avanço simulado |
| Pastas e variáveis (p. 7) | Seis categorias, filtro Todas, contadores, progresso, indicador da pesquisa e pendências |
| Seis pilares e oito Packs (p. 2) | Estrutura consultável, seleção múltipla de Packs, natureza, papel e vigência no rascunho |
| Monitoramento (p. 4) | Radar, fomentos/metas, esteira editorial/cobertura e cadência de check-in como áreas de preparação |
| Orientador e aluno (pp. 1, 7) | Aprovação simulada restrita ao papel Coordeno; área conceitual da trajetória do aluno |
| Privacidade (pp. 4–5) | Recursos previstos explicitados sem selos de E2EE, certificação ou auditoria ativa |

Os exemplos de Babaçu e mHealth são cenários ilustrativos inspirados no PDF,
não dados reais de acompanhamento. As imagens são cópias das referências locais
em `docs/base-conhecimento-projetos/img/`. Percentuais são calculados a partir
 das entregas da prévia, não reproduzem os percentuais ilustrativos do PDF.

## Limites deliberados

Tudo permanece em memória; recarregar descarta rascunhos e alterações.
Nenhum conteúdo de projeto é persistido ou enviado. A consulta de conexão
Lattes do shell continua independente do módulo. A rota mantém a proteção de
sessão padrão do servidor da aplicação.

Não há upload, convites, processamento de PDF/DOCX, sincronização, planos,
pagamentos, exportação, E2EE ou auditoria imutável. Importação e dossiê estão
visivelmente indisponíveis. O histórico exibido é somente atividade temporária.
A restrição por papel nesta demonstração não substitui autorização no servidor.

## Próximas etapas

1. Contratos de identidade, equipe e autorização por projeto.
2. Cofre privado e ciclo de chaves, recuperação, revogação e auditoria conforme
   `05-prerequisitos-sigilo-zero-knowledge.md`, antes de guardar dados inéditos.
3. Adaptador de dados com carregamento, falhas e coleção vazia, substituindo os exemplos.
4. Ingestão local de PDF/DOCX com revisão de fases, Packs e cadência antes da ativação.
5. Relações N:N de fomentos/produtos, autoria CRediT e versões multilíngues.
6. Revisão e propagação autorizada por autor, separadas da camada privada.

## Validação

Sintaxe JavaScript e referências locais/IDs conferidas automaticamente.
A inspeção visual da interface e os testes interativos permanecem pendentes:
o navegador de prévia não alcançou o servidor local, e a consulta HTTP recebeu
bloqueio de socket do ambiente.

Roteiro de aceite: buscar por área, combinar filtros e limpar; abrir os dois
papéis; filtrar cada pasta; criar entrega; avançar até revisão e simular aprovação
como coordenador; verificar ausência dessa ação como colaborador; criar projeto
com vários Packs, rejeitar vigência invertida; testar voltar/avançar, Escape,
teclado, tela pequena e descarte ao recarregar.
