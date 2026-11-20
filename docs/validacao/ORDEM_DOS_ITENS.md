# Ordem de validação dos itens (cruzada com a matriz de prioridade)

Fonte da prioridade: `docs/matriz-prioridade/README.md` (volume real no currículo de Aramys e coautores). Estado em 21/11/2026.

| Faixa | Fluxo (matriz) | Itens do spec | Estado |
| --- | --- | --- | --- |
| 1 | Artigos completos em periódicos | `artigo` (e `artigo_aceito`) | artigo fechado (pendente: perfis); **artigo aceito para publicação não validado** |
| 2 | Orientações concluídas/em andamento | `orientacao_concluida`, `orientacao_andamento` | fechadas (pendente: perfis) |
| 3 | Projetos (pesquisa 34, tecnológico 13, extensão 7) | `projeto` (5 variantes) | fechado (pendente: perfis) |
| 4 | **Bancas** (85 no diagnóstico) | `banca`, `banca_comissao_julgadora` | **fechadas em 21/11/2026** (captura, matriz 197/197 e 189/189, salvamento real; pendente: perfis) |
| 5 | **Produção tecnológica e patentes** | `patente`, `software_registro`, `software_sem_registro`, `produto`, `processo_tecnica`, `trabalho_tecnico`, `relatorio_tecnico`, `extensao_tecnologica`, `material_didatico`, `cultivar_*`, `desenho_industrial`, `marca_registrada`, `topografia_circuito` | **fechada em 21/11/2026** (13 itens: captura, paridade 0, matrizes sem falha, salvamento real conferido; pendente: perfis) |
| 6 | Trabalhos em anais e apresentações | `anais`, `apresentacao` | fechados (pendente: perfis) |
| 7 | Participação/organização de eventos e cursos ministrados | `participacao_evento`, `organizacao_evento`, `curso_ministrado` | a fazer |
| 8 | Livros, capítulos, prêmios e demais produções | `livro_capitulo`, `premio`, `texto_jornal_revista`, `traducao`, `prefacio_posfacio`, `partitura_musical`, `musica`, `artes_*`, `cartas_mapas`, `maquete`, `editoracao`, `entrevista_midia`, `redes_sociais`, `relatorio_pesquisa`, `outra_producao_*`, `manutencao_obra` | a fazer |
| fora da matriz | Dados gerais, formação, atuação, revisor/corpo editorial/comitês, citações | `identificacao`, `endereco`, `idioma`, `licenca`, `outras_informacoes`, `texto_inicial`, `formacao_*`, `pos_doutorado`, `atuacao_profissional`, `revisor_*`, `corpo_editorial`, `comite_assessoramento`, `citacao_*` | a fazer, depois da faixa 8 (a matriz não os mede) |

## Observações da análise
- As faixas 1, 2, 3, 4, 5 e 6 já estão fechadas no Lattes real; a faixa 5 (produção técnica e patentes) fechou em 21/11/2026; a próxima é a **faixa 7**.
- **Perfis diferentes:** os currículos de Richard e Márcia (PDF) e os coautores do Ciclo 1 servem de evidência de outros perfis. O README diz que os PDFs de Adriana e Marcelino estavam vazios (0 bytes) e o `CICLO_1_EXECUCAO.md` já os dá como carregados (121 e 138 páginas): confirmar. Os PDFs são imagem; sem OCR a matriz não mede campos reais por pesquisador.
- Faltam dois itens que a matriz não cita mas que o Lattes cobra: **artigo aceito** e os itens "fora da matriz".
- A amostra do Ciclo 1 mede VOLUME, não variações de formulário; o que valida o espelho continua sendo a captura do formulário real + matriz + salvamento.
