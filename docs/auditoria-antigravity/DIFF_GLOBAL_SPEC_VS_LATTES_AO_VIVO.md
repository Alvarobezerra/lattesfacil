# Diff Global: Capturas ao Vivo (62 JSONs) × `itens/especificacao/`

**Data:** 2026-11-20  
**Escopo:** Execução da **Etapa 1** de [PLANO_CONTRALIDACAO_E_ESCALA.md](PLANO_CONTRALIDACAO_E_ESCALA.md) (Pilares 1 e 2), cruzando `docs/auditoria-antigravity/capturas/*.json` contra `itens/especificacao/*.json`.

---

## 1. Achado Crítico — Divergência das "80 Opções" (País e Idioma)
No `docs/validacao/STATUS.md`, o Claude anotou `"80 opções reais"` para país/idioma em Artigo, Anais e Apresentação. A inspeção direta dos specs gerados confirma que o corte foi parar em `itens/especificacao/`:

| Spec | Campo | No Spec (`itens/especificacao/`) | No Lattes ao Vivo (DOM real) |
| --- | --- | --- | --- |
| `artigo.json` | `F_IDIOMA` | **80** opções inline (`catalogo: None`) | **152** idiomas |
| `anais.json` | `f_pais` | **80** opções inline (`catalogo: None`) | **244** países |
| `anais.json` | `F_IDIOMA` | **80** opções inline (`catalogo: None`) | **152** idiomas |
| `apresentacao.json` | `f_pais` | **80** opções inline (`catalogo: None`) | **244** países |
| `apresentacao.json` | `F_IDIOMA` | **80** opções inline (`catalogo: None`) | **152** idiomas |
| `projeto.json` | `f_pais_inst` | `catalogos/paises-244.json` (**244**) | **79** países (+1 vazia = 80) |

> **Diagnóstico:** Os dois lados estão invertidos em relação ao Lattes real — `artigo`/`anais`/`apresentacao` deveriam usar os catálogos completos (`244` países e `152` idiomas), enquanto `f_pais_inst` em `projeto.json` deveria ser restrito aos `79` países aceitos pelo formulário de Projetos.

---

## 2. Divergências Estruturais e de `maxlength`
1. **Itens sem arquivo correspondente em `itens/especificacao/`:**
   - `assessoria_consultoria` (no Lattes é item próprio do menu: `PKG_ASSESSORIA_CONSULTORIA.form` com `F_COD_PROD`: `Assessoria` / `Consultoria`).
   - `areas_atuacao` (`prc_area_atuacao` — grid direto na árvore de 9 Grandes Áreas).
   - `linhas_de_pesquisa` (`pkg_linhapesq.lista` — sem formulário próprio, redireciona para `Atuação > Pesquisa e Desenvolvimento`).
   - `trabalhos_anais_eventos` usa o nome `anais.json` no spec (e `anais.json` está com 80 países/idiomas).
2. **`maxlength` incorretos em `livro_capitulo.json`:**
   - `f_titulo` (Livro): spec = `255` vs ao vivo = **`400`**.
   - `f_ref_en` (Livro e Capítulo): spec = `3900` vs ao vivo = **`3800`** (risco de truncamento/rejeição no Lattes).
3. **`idioma.json`:** os 4 pares checkbox+radio de modalidade (`FC_LE`/`F_LE`, `FC_CONVERSA`/`F_CONVERSA`, `FC_ESCREVE`/`F_ESCREVE`, `FC_COMPR`/`F_COMPR`) não aparecem como campos nomeados individuais compatíveis com o comportamento dinâmico de `Libras` (`veriLibra`).

---

## 3. Principais Lacunas de Obrigatoriedade (`obrigatorio` no Spec × `check()` ao Vivo)
O teste ao vivo de salvamento em branco revelou dezenas de campos obrigatórios que estão com `obrigatorio: false` (ou ausentes) nos specs atuais:

| Item | Obrigatórios no Spec | Obrigatórios Reais (`check()` ao vivo) | Principais Faltantes no Spec |
| --- | --- | --- | --- |
| `licenca.json` | **0** | **4** | `f_tipo_licenca`, `f_dta_inicio`, `f_dta_fim`, `f_dta_nasc_adoc` |
| `patente.json` | **1** | **9** | `Depositante/Titular`, `f_sta_inovacao`, `f_titulo`, `f_natureza`, `f_tipo`, `f_inst`, `f_cod_reg`, `Data de depósito`, `inventores` |
| `cultivar_protegida.json` | **3** | **5** | `f_inst`, `f_cod_reg`, `f_dta_dep`, `melhoristas` |
| `cultivar_registrada.json` | **2** | **6** | `f_ano`, `f_inst`, `f_cod_reg`, `f_dta_dep`, `inventores` |
| `comite_assessoramento.json` | **2** | **3 (+1 cond.)** | `f_comite`, `Início` (e `Fim` se `Anterior`) |
| `corpo_editorial.json` | **1** | **2 (+1 cond.)** | `Início` (e `Fim` se `Anterior`) |
| `revisor_periodico.json` | **1** | **2 (+1 cond.)** | `Início` (e `Fim` se `Anterior`) |
| `revisor_projeto_fomento.json` | **1** | **2 (+1 cond.)** | `Início` (e `Fim` se `Anterior`) |
| `artigo_aceito.json` | **4** | **5** | Validação de **ISSN válido** |
| `entrevistas_midia` / `redes_sociais` / `curso_ministrado` / `cartas_mapas` | **3** | **6–7** | `F_COD_PROD` (`Natureza`/`Nível`), `participantes`/`autores` |
| `topografia_circuito.json` | **5** | **7** | `f_inst_financ`, `f_finalidade`, `inventores` (+ `f_txt_potencial` se `Sim`) |

---

## 4. Próximo Passo (Etapa 2 do Plano)
Consolidar essas correções no backlog de Fase 2 (para `itens/gerar_specs.py`, `itens/curadoria.json`, `static/app.js` e `extensao/autofill_core.js`) e seguir para a **Etapa 3 (Validação F4/F5/F7 por Famílias)** assim que formos iniciar a implantação.
