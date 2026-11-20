# Backlog Técnico Consolidado — Fase 2 (Sem Alteração de Código Ainda)

**Data:** 2026-11-20  
**Base:** Consolidação das **62 capturas ao vivo** (`capturas/*.json`) + [DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md](DIFF_GLOBAL_SPEC_VS_LATTES_AO_VIVO.md) + achados da auditoria do Claude em `docs/validacao/STATUS.md`.  
**Regra:** Documento de planejamento para execução posterior em `itens/gerar_specs.py`, `itens/curadoria.json`, `static/app.js` e `extensao/autofill_core.js`.

---

## Prioridade 1 — Quebra de Domínio, Catálogos e Limites (`itens/gerar_specs.py` / `curadoria.json`)

| ID | Alvo | Problema Observado ao Vivo | Ação Planejada (Fase 2) |
| --- | --- | --- | --- |
| **B1.1** | `artigo.json`, `anais.json`, `apresentacao.json` | `f_pais` e `F_IDIOMA` gerados com apenas `80` opções inline; no Lattes real são `244` países e `152` idiomas | Ligar aos catálogos completos (`244` países / `152` idiomas) |
| **B1.2** | `projeto.json` | `f_pais_inst` usa `paises-244.json`, mas o formulário real de Projeto só aceita `79` países (+ vazia = 80) | Criar/aplicar subcatálogo `paises-79` específico para `f_pais_inst` |
| **B1.3** | `livro_capitulo.json` | `f_titulo` (Livro) está com `maxlength=255` (ao vivo é `400`); `f_ref_en` está `3900` (ao vivo é `3800`) | Ajustar `f_titulo` (Livro) para `400` e `f_ref_en` para `3800` |
| **B1.4** | `prefacio_posfacio.json`, `banca.json` | Valores reais de `<select>` têm espaço à direita (`"31 "`, `"32 "`, `"33 "` em `f_sub_tipo`; `"34 "`, `"35 "` em `f_sub_prod`) | Garantir preservação exata dos `value`s com espaço no spec e no autofill |
| **B1.5** | `entrevista_midia.json`, `artigo.json` | `f_meio` reduzido: `artigo` aceita só `I, D, V`; `entrevista_midia` aceita só `I, W, O` (`"Outrooutro"`) | Garantir que os specs reflitam exatamente essas 3 opções em cada item |
| **B1.6** | `orientacao_andamento.json` | No Lattes em andamento existem apenas **6** opções de Natureza (não existe TCC de graduação) | Bloquear/ocultar TCC quando situação for "Em andamento" |

---

## Prioridade 2 — Regras de Obrigatoriedade (`check()` / `pre_check()` ao vivo × Specs)

| ID | Item / Spec | Divergência Identificada | Ação Planejada (Fase 2) |
| --- | --- | --- | --- |
| **B2.1** | `licenca.json` | Spec com `0` obrigatórios; Lattes exige `4`: `f_tipo_licenca`, `f_dta_inicio`, `f_dta_fim`, `f_dta_nasc_adoc` | Marcar os 4 campos como obrigatórios (e default Visibilidade = `Privado`) |
| **B2.2** | `patente.json` | Spec com `1` obrigatório; Lattes exige `9` (incl. `Depositante/Titular`, `f_sta_inovacao`, `f_natureza`, `f_tipo`, `f_inst`, `f_cod_reg`, `Data de depósito`, `inventores`) | Atualizar flags de obrigatoriedade + validação condicional de `f_txt_potencial` |
| **B2.3** | `cultivar_protegida.json`, `cultivar_registrada.json` | Faltam obrigatórios de registro/autoridade/data/ano (`CR` exige `f_ano`, `f_inst`, `f_cod_reg`, `f_dta_dep`, `inventores`; `CP` exige `melhoristas`) | Atualizar flags de obrigatoriedade por variante |
| **B2.4** | `corpo_editorial`, `comite_assessoramento`, `revisor_periodico`, `revisor_projeto_fomento` | Specs não cobrem `Início` (`f_mes_ini`/`f_ano_ini`), `Comitê` (`MA`) nem `Fim` condicional (`f_status = Anterior`) | Tornar `Início` e `Comitê` obrigatórios e `Fim` obrigatório quando `Anterior` |
| **B2.5** | `orientacao_concluida.json` | `f_dsc_outra` está como obrigatório global (no Lattes é só Mestrado e Outra natureza); `F_COD_PROD` está opcional | Tornar `F_COD_PROD` obrigatório e `f_dsc_outra` condicional |
| **B2.6** | `topografia_circuito`, `artigo_aceito`, `redes_sociais`, `entrevistas_midia`, `curso_ministrado`, `cartas_mapas`, `software_sem_registro` | Faltam obrigatórios confirmados no `check()` (ex.: `f_inst_financ`, `f_finalidade`, `F_COD_PROD`, validação de ISSN em `artigo_aceito`) | Alinhar `obrigatorio: true` e validações prévias no robô |

---

## Prioridade 3 — Itens sem Spec, Legado e Estruturas Especiais

| ID | Alvo | Situação Atual | Ação Planejada (Fase 2) |
| --- | --- | --- | --- |
| **B3.1** | `orientacao_concluida` / `orientacao_andamento` + caderno de `anais` | Ainda usam o formulário legado em `static/index.html` | Migrar para o motor de specs (como já iniciado em `artigo`/`anais`/`apresentacao`) |
| **B3.2** | `assessoria_consultoria` | Item próprio no menu (`PKG_ASSESSORIA_CONSULTORIA.form`), sem arquivo dedicado em `itens/especificacao/` | Gerar spec próprio com `F_COD_PROD` (`Assessoria`, `Consultoria`) |
| **B3.3** | `areas_atuacao`, `linhas_de_pesquisa` | Sem spec: `areas_atuacao` é grid direto da árvore CNPq; `linhas_de_pesquisa` redireciona para `Atuação > Pesquisa e Desenvolvimento` | Documentar e suportar fluxo específico (grid de áreas e redirecionamento para `f_natur_ativ=2`) |
| **B3.4** | `premio`, `texto_inicial`, `outras_informacoes` | Conferir limites e layout (`premio`: `f_titulo` 200, `f_agencia` 100 opcional, sem Traduções; `texto_inicial`: 2x 4000 sem abas/visibilidade; `outras_informacoes`: 1x 2000 sem abas/visibilidade) | Garantir paridade exata de campos, limites e ausência de abas extras |

---

## Prioridade 4 — Wizards de Abertura, Hierarquias, Condicionais e Lupas (`static/app.js` + `extensao/autofill_core.js`)

1. **Wizards pré-formulário:**
   - `Artigos`: fluxo `findp` → `finfivip` (`fissn`, `fvolume`, `fpagini` obrigatórios) + tratamento de campos `disabled=true` em `F_CTR=FIV` e modo DOI.
   - `Livros/Capítulos`: fluxo `winLivrosCaps` em 2 passos (`prc_valida_issn` + `issnisbn`/`year`/`autoreditor`).
   - `Patentes/Registros` (`PP`, `PC`, `DI`, `MR`, `TC`): modal `infDadPat()` + seletor `escolhe_inst()` (12 órgãos) + validação de máscara INPI (`PC`, `DI`, `MR`, `TC`).
   - `Formação complementar`: wizard em 2 telas (`form` → `FORM2`), propagando `F_STATUS` para controlar `f_ano_fim` (`Conclusão` / `Interrupção` / `disabled`).
2. **Hierarquia em 3 níveis (`Atuação profissional`):**
   - `PKG_ATIV.inclui` (instituição + vínculo inicial) → hub `PKG_ATIV.cargos_vinculos` → `PKG_ATIV.vinculos` e `pkg_ativ.cargo` (9 naturezas `1,2,4,5,6,7,8,9,B`, com `Ensino (4)` trocando `Órgão` por `Nível` + `Curso`).
3. **Condicionais dinâmicos obrigatórios no motor de tela e robô:**
   - `Idiomas`: `Libras (LB)` remove `Lê` e `Escreve` (`veriLibra`).
   - `Participação em eventos`: `F_FORMA` popula `F_TPO`; `Ouvinte` esvazia `F_TPO` e dispensa `F_TPO` e `f_titulo`; `F_TPO` muda rótulo de `f_titulo`.
   - `Formação acadêmica (Doutorado)`: `f_tpo_doutorado` (`sanduíche` / `co-tutela` / `co-tutela/sanduíche`) muda rótulo de `f_inst` e insere blocos extras; `F_STATUS = incompleto` muda `Conclusão` para `Interrupção`.
   - `Inovação (f_sta_inovacao)`: respeitar defaults distintos (`Sim` em `PC` e `DI`; desmarcado obrigatório em `PP`; `Não` nos demais) e exibição/obrigatoriedade dinâmica de `f_txt_potencial`.
   - `Identificação`: `f_nome_social_r = Sim` (`f_nome_social`) e `f_pcd_r = Sim` (6 checkboxes `f_pcd`).
4. **Lupas e catálogos auxiliares:**
   - Reaproveitar `setorDP` (CNAE) e `areaDP` (Áreas CNPq) que já vêm completos no HTML do `PKG_MENU.menu`.
   - Prever tratamento assistido/cache para as lupas ainda sem banco próprio (`agencia()`, `periodico()`, `curso()`, `orgao()`, `dominio()`).
