# Auditoria Independente — Antigravity

Pasta isolada para rastreio independente ao vivo na Plataforma Lattes, validação cruzada e comparação com o `lattesdata` (`static/index.html`, `itens/especificacao/`, `extensao/autofill_core.js`).

> **Regra de isolamento:** Nenhum arquivo fora de `docs/auditoria-antigravity/` foi alterado por esta trilha.

## Documento Principal e Plano de Execução
- [RELATORIO_FINAL_MAPEAMENTO.md](RELATORIO_FINAL_MAPEAMENTO.md) — Consolidação completa de 100% da Plataforma Lattes.
- [PLANO_CONTRALIDACAO_E_ESCALA.md](PLANO_CONTRALIDACAO_E_ESCALA.md) — Roteiro estruturado em 4 etapas (Diff Global → Backlog → Validação por Famílias → App Logado).
- [DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md](DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md) — Resultado da Etapa 1: cruzamento global das 62 capturas ao vivo × `itens/especificacao/`.
- [BACKLOG_TECNICO_FASE2.md](BACKLOG_TECNICO_FASE2.md) — Resultado da Etapa 2: backlog técnico consolidado por prioridade (sem alterações de código).
- [RELATORIO_ETAPA4_APP_LOGADO.md](RELATORIO_ETAPA4_APP_LOGADO.md) — Resultado da Etapa 4: auditoria ponta-a-ponta do app `lattesdata` logado (`http://127.0.0.1:8765`).

## Auditorias por Seção
- [auditoria-dados-gerais.md](auditoria-dados-gerais.md) — Aba Dados Gerais completa (7 subitens: `Identificação`, `Endereço`, `Licenças`, `Idiomas`, `Prêmios`, `Texto inicial`, `Outras informações`)
- [auditoria-formacao.md](auditoria-formacao.md) — Aba Formação completa (3 subitens / 13 variantes: `Formação acadêmica` 10 níveis, `Pós-doutorado / Livre-docência` 2 níveis, `Formação complementar` wizard 2 telas)
- [auditoria-atuacao.md](auditoria-atuacao.md) — Aba Atuação completa (7 subitens: `Atuação profissional` 3 níveis + 9 naturezas de atividades, `Linhas de pesquisa`, `Corpo editorial`, `Comitê de assessoramento`, `Revisor de periódico/projeto`, `Áreas de atuação`)
- [auditoria-producoes.md](auditoria-producoes.md) — Aba Produções completa (30 subitens em 8 motores: `Produção Bibliográfica` [11], `Produção Técnica` [15] e `Outra Produção Artística/Cultural` [4])
- [auditoria-patentes-registros.md](auditoria-patentes-registros.md) — Aba Patentes e Registros completa (8 variantes em `PKG_PATENTE_REGISTRO`: 19 hidden inputs, `infDadPat()` vs abertura direta, exclusão via `.caixaMsg`)
- [auditoria-eventos.md](auditoria-eventos.md) — Aba Eventos completa (2 subitens: `Participação em eventos` e `Organização de eventos`)
- [auditoria-orientacoes-bancas-citacoes.md](auditoria-orientacoes-bancas-citacoes.md) — Abas Orientações (2 subitens / 13 variantes), Bancas (2 subitens / 11 variantes) e Citações (5 bases `prc_indicadores`)
- [auditoria-menu-secundario-lateral.md](auditoria-menu-secundario-lateral.md) — Barra vertical lateral esquerda ("Menu secundário" — 10 ícones: dicionários de autores, coautores, palavras-chave, áreas, instituições, periódicos, impressão, exportar e importar XML)
- [auditoria-projeto-e-artigo.md](auditoria-projeto-e-artigo.md)
- [auditoria-anais.md](auditoria-anais.md)
- [auditoria-apresentacao.md](auditoria-apresentacao.md)
- [auditoria-orientacao-concluida.md](auditoria-orientacao-concluida.md)
- [auditoria-orientacao-andamento.md](auditoria-orientacao-andamento.md)
- [auditoria-livro.md](auditoria-livro.md)
- [auditoria-capitulo-e-texto.md](auditoria-capitulo-e-texto.md)
- [auditoria-artigo-aceito-e-partitura.md](auditoria-artigo-aceito-e-partitura.md)
- [auditoria-demais-bibliograficas.md](auditoria-demais-bibliograficas.md)
- [auditoria-tecnica-lote1.md](auditoria-tecnica-lote1.md)
- [auditoria-tecnica-lote2.md](auditoria-tecnica-lote2.md)
- [auditoria-tecnica-lote3.md](auditoria-tecnica-lote3.md)

## Fichas de Validação Ponta a Ponta (F4/F5 + F7: Salvar, Reabrir e Excluir)
- [validacao-f4-f5-f7-apresentacao-e-anais.md](validacao-f4-f5-f7-apresentacao-e-anais.md) — Contravalidação de `Apresentação de trabalho` e `Trabalhos em anais`
- [ficha-orientacao.md](ficha-orientacao.md) — Orientações (concluída + em andamento + outra natureza)
- [ficha-participacao-evento.md](ficha-participacao-evento.md) — Participação em eventos
- [ficha-bancas.md](ficha-bancas.md) — Bancas (trabalho de conclusão + comissão julgadora)
- [ficha-livros-capitulos.md](ficha-livros-capitulos.md) — Livros e Capítulos
- [ficha-formacao.md](ficha-formacao.md) — Formação Acadêmica e Complementar
- [ficha-tecnica-e-inovacao.md](ficha-tecnica-e-inovacao.md) — Produção Técnica e Inovação (`f_sta_inovacao`)
- [ficha-artistica.md](ficha-artistica.md) — Produção Artística (`Artes cênicas`)
- [ficha-patentes-registros.md](ficha-patentes-registros.md) — Patentes e Registros (`Marca registrada`)
- [ficha-atuacao.md](ficha-atuacao.md) — Atuação Profissional (3 níveis + `Membro de corpo editorial` + `Comitê de assessoramento`)
- [ficha-dados-gerais.md](ficha-dados-gerais.md) — Dados Gerais (`Prêmios e títulos`, `Licença` e `Idiomas`)
- [ficha-citacoes.md](ficha-citacoes.md) — Citações (`prc_indicadores` — 5 bases)

## Capturas Brutas (`capturas/`)
Contém os 62 arquivos `.json` extraídos diretamente do DOM ao vivo da Plataforma Lattes.
