# Plano Estruturado — Contravalidação e Escala (Lattes × `lattesdata`)

**Objetivo:** Unir o rigor de ponta a ponta da metodologia do Claude (diff, paridade de tela, leitura de volta e salvamento/exclusão) à cobertura completa que já capturamos ao vivo (**62 JSONs** em `docs/auditoria-antigravity/capturas/`), sem tocar em arquivos fora de `docs/auditoria-antigravity/` durante a fase de auditoria.

---

## Mapa de Execução (4 Etapas)

### Etapa 1 — Diff Global Automático + Auditoria das "80 Opções" *(Execução Imediata)*
- **O que faz:**
  1. Cruza **todas as capturas ao vivo** (`capturas/*.json`) contra **todos os specs** (`itens/especificacao/*.json`): campos ausentes, `maxlength`, tipos de controle e regras de obrigatoriedade obtidas ao vivo no `check()` / `pre_check()`.
  2. Investiga a divergência **"80 opções reais"** registrada em `docs/validacao/STATUS.md` vs **244 países / 152 idiomas** observados no DOM ao vivo.
- **Saída:** [DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md](DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md).
- **Critério de saída:** Mapa completo de divergências por item e confirmação da causa raiz das 80 opções.

### Etapa 2 — Backlog Unificado de Correções (Fase 2 de Implementação)
- **O que faz:** Consolida em um plano único (somando achados do Claude + achados do Antigravity) o que deve ser ajustado em `itens/gerar_specs.py`, `itens/curadoria.json`, `static/app.js` e `extensao/autofill_core.js`:
  - Wizards de abertura (`findp -> finfivip`, `winLivrosCaps`, `infDadPat`, seletores de nível).
  - Hierarquia em 3 níveis (`Atuação profissional`) e redirecionamento (`Linhas de pesquisa`).
  - Regras condicionais dinâmicas (`Libras`, `Ouvinte`, `f_tpo_doutorado`, `f_sta_inovacao`, `Anterior` em atuação/revisor, `Formação complementar` 2 telas).
  - Limites (`maxlength`), espaços à direita em `<select>` (`"31 "`, `"34 "`) e catálogos.
- **Critério de saída:** Checklist priorizado por família de formulário, pronto para aplicar quando o Claude encerrar a rotina dele.

### Etapa 3 — Validação por Famílias de Formulários (F4 + F5 + F7 com Exclusão)
Em vez de repetir manualmente 61 vezes o mesmo ciclo, validamos **1 representante completo por família** + **varredura automática das diferenças das variantes**:

| Família | Motor / Endpoint no Lattes | Itens Cobertos |
| --- | --- | --- |
| **F1. Projetos** | `pkg_projeto` | 5 variantes (já pilotado pelo Claude) |
| **F2. Artigos** | `PKG_ARTIGO` / `PKG_ARTIGO_PR` | Artigo publicado, Artigo aceito |
| **F3. Livros e Capítulos** | `PKG_LVR_CAP` | Livro, Capítulo |
| **F4. Eventos & Trabalhos** | `pkg_trabalho`, `prc_tec_apres`, `pkg_evento` | Anais, Apresentação, Participação em eventos |
| **F5. Demais Bibliográficas & Texto** | `PKG_TEXTO`, `PRC_BIB_*` | Texto jornal/revista, Partitura, Tradução, Prefácio, Outra bib. |
| **F6. Técnicas & Inovação** | `GN_RELATORIO`, `PKG_PRODUTO`, `PKG_PROCESSO`, `PRC_TEC_*` | 15 itens técnicos (exceto Software s/ registro) |
| **F7. Produção Artística** | `PKG_ARTE_NOVA.FORM` | Artes cênicas, Música, Artes visuais, Outra artística |
| **F8. Patentes & Registros** | `PKG_PATENTE_REGISTRO.FORM` | Patente, Software c/ e s/ registro, Cultivares (CP/CR), DI, MR, TC |
| **F9. Orientações & Bancas** | `PKG_ORIENT`, `PKG_BANCA_*` | Orientações concluídas/andamento, Bancas trabalho/comissão |
| **F10. Formação, Atuação, Citações & Dados Gerais** | `pkg_formacao`, `PKG_FORMACAO_COMPL`, `PKG_ATIV`, `PKG_REVISOR`, `PRC_INDICADORES`, `GN_IDENT/ENDERECO/LICENCA/IDIOMA/PREMIO` | Formação (3), Atuação (7), Citações (5), Dados Gerais (7) |

- **Critério de saída:** 100% das 10 famílias com matriz F4/F5 aprovada e salvamento+exclusão (F7) verificado.

### Etapa 4 — Teste Ponta-a-Ponta no App Logado (Zerar Pendências do `STATUS.md`)
- **O que faz:** Subir/acessar o `lattesdata` autenticado, percorrer todos os fluxos de entrada (documento enviado, em branco, caderno de resumos, histórico) → extensão → Lattes → leitura de volta → salvamento de teste + exclusão.
- **Critério de saída:** Zero pendências bloqueantes em `docs/validacao/STATUS.md`.
