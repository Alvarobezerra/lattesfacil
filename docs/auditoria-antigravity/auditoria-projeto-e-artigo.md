# Auditoria Cruzada: Projetos e Artigo Completo em Periódico

**Data:** 2026-11-20  
**Fontes comparadas (somente leitura):**
- Capturas reais do Lattes: `docs/campos-lattes/ref/projeto/*.json`, `docs/campos-lattes/ref/projeto_f5/*.json`, `docs/campos-lattes/ref/diag/obrigatorios_extensao.json`, `docs/campos-lattes/ref/artigo/artigo_periodico.json`, `docs/campos-lattes/ref/artigo_doi/artigo_periodico_doi.json`
- Especificações do app: `itens/especificacao/projeto.json`, `itens/especificacao/artigo.json`, `docs/campos-lattes/catalogos/paises-244.json`
- Formulário legado e autofill: `static/index.html` (linhas 225–540), `extensao/autofill_core.js` (linhas 770–1010)

---

## 1. Artigo Completo em Periódico (`artigo`)

### 1.1 Correções sobre o diagnóstico em `docs/validacao/STATUS.md`
O `STATUS.md` apontou que o formulário do `lattesdata` (`static/index.html`) não possuía diversos campos do artigo e que exibia "Fascículo" indevidamente. **A inspeção direta de `static/index.html` mostra um cenário diferente:**

| Campo do Lattes (`artigo_periodico.json`) | Situação real em `static/index.html` | Oportunidade de melhoria |
| --- | --- | --- |
| `F_IDIOMA` (select, 152 opções) | **Existe** (`#idioma`, linha 294), mas como `<input type="text">` livre | Trocar para `<select>` com o catálogo de 152 idiomas para evitar erro de digitação |
| `f_homepage` (`maxlength=250`) | **Existe** (`#homepage`, linha 299) | Adicionar `maxlength="250"` |
| `F_RELEV` (radio Sim/Não) | **Existe** (`#relevante`, linha 534) | Paridade OK |
| `f_ref` (`maxlength=3950`) | **Existe** (`#outras_informacoes`, linha 506, `maxlength="3950"`) | Paridade OK |
| Lista Palavras-chave | **Existe** (`#keywordsList`, linha 497) | Paridade OK |
| Lista Áreas do conhecimento | **Existe** (`#area_conhecimento`, linha 512) | Paridade OK |
| `f_tipo_privacidade` (visibilidade) | **Existe** (`#visibilidade`, linha 516: Público/Privado) | Verificar vínculo no `autofill_core.js` (não há referência a `f_tipo_privacidade` no autofill) |
| Fascículo (`#fasciculo`, linha 469) | **Oculto para artigo** (`data-tipos="anais"`) | Não é exibido para `artigo` |

### 1.2 Campos realmente ausentes em `static/index.html` (para `artigo`)
1. `F_STA_DIVULGACAO_CIENTIFICA` ("Produção para educação e popularização de C&T?", radio `S`/`N`) — **Importante:** `extensao/autofill_core.js` (linha 846) já lê `d.f_sta_divulgacao_cientifica || d.divulgacao_cientifica`, mas não existe campo correspondente no `static/index.html`.
2. `f_titulo_en` ("Title", text `maxlength=400`).
3. `f_ref_en` ("Other information", textarea `maxlength=3800`).
4. `f_jcr` ("Fator de Impacto (JCR)", somente leitura / visível após busca por DOI).
5. Lista `tabelasetor` / `setorHolder` ("Setor de aplicação da Tabela CNAE", link "Listar todos").

### 1.3 Divergências de domínio e limites (`static/index.html` vs Lattes real)
- **`meio_divulgacao` (`f_meio`):**
  - `static/index.html` oferece **7 opções**: `meio digital`, `Impresso`, `hipertexto`, `impresso e mídia eletrônica`, `meio magnético`, `filme`, `outro`.
  - Lattes real (`f_meio`) aceita apenas **3 opções válidas**: `I` (Impresso), `D` (meio digital) e `V` (Impresso e mídia eletrônica). As outras 4 opções falham no mapeamento do autofill para `artigo`.
- **`maxlength` ausentes em `static/index.html`:**
  - `titulo`: sem limite no HTML (Lattes: `400`)
  - `doi`: sem limite no HTML (Lattes: `250`)
  - `homepage`: sem limite no HTML (Lattes: `250`)
  - `isbn_issn`: sem limite no HTML (Lattes: `10`)
  - `pagina_inicial` / `pagina_final`: sem limite no HTML (Lattes: `15`, aceita número de artigo eletrônico)
- **`itens/especificacao/artigo.json` já existe e está alinhado ao Lattes:**
  - A spec gerada em `itens/especificacao/artigo.json` cobre os 19 campos do `artigo_periodico.json` (incluindo `F_STA_DIVULGACAO_CIENTIFICA`, `f_titulo_en`, `f_ref_en`, `f_jcr` e `maxlength` corretos). Migrar `artigo` do formulário legado em `static/index.html` para o motor de specs resolverá quase todas as lacunas acima de uma só vez.

### 1.4 Diferença de comportamento: Abertura Manual vs Abertura com DOI
Comparando `artigo_periodico.json` (manual) com `artigo_periodico_doi.json` (com DOI):
- Quando aberto **via DOI**, **6 campos** vêm `desabilitado: true`: `f_cod_doi`, `f_ano`, `f_issn`, `f_volume`, `f_serie` e `f_pag_ini`.
- O campo `f_jcr` muda de `visivel_inicial: false` (manual) para `visivel_inicial: true` (DOI), mantendo `desabilitado: true`.
- `f_titulo_periodico` é sempre `desabilitado: true` nos dois modos (preenchido pelo DOI ou pela lupa `periodico()`).

---

## 2. Projetos (`projeto` — 5 variantes)

### 2.1 Cobertura estrutural (`itens/especificacao/projeto.json` vs `docs/campos-lattes/ref/projeto/*.json`)
- Todas as 5 variantes (`Projetos de pesquisa`, `Projeto de extensão`, `Projeto de ensino`, `Projeto de desenvolvimento tecnológico`, `Outros tipos de projetos`) têm paridade de campos e `maxlength` entre a spec e a captura real.
- Diferenças de contagem em `F_TPO_NATUREZA` (6 vs 5), `F_TPO_SITUACAO` (4 vs 3) e `f_uf` (28 vs 27) são apenas a opção vazia inicial `""` presente no `<select>` do Lattes.

### 2.2 Pontos de atenção e oportunidades de melhoria
1. **Catálogo de países em `f_pais_inst` (Risco de erro no preenchimento):**
   - `itens/especificacao/projeto.json` referencia `catalogos/paises-244.json` (**244 países**).
   - O `<select name="f_pais_inst">` real no formulário de Projetos do Lattes possui apenas **79 países** (+ opção vazia = 80).
   - Todos os 79 países existem em `paises-244.json`, mas **165 países** do catálogo não existem em `f_pais_inst`. Se o usuário selecionar um desses 165 países no `lattesdata`, o autofill não conseguirá selecionar no Lattes.
   - *Sugestão para fase 2:* Criar um subcatálogo específico (ex.: `paises-79.json`) ou filtrar as opções exibidas no `lattesdata` para `f_pais_inst` de Projeto.
2. **Campos `grupo_marcacao` em `Projeto de ensino`:**
   - `f_tematica` (12 opções), `f_tpo_acao_inov` (7 opções) e `f_tpo_cooperacao` (3 opções) são capturados como `grupo_marcacao` e representados como `checkbox` na spec.
   - Atenção ao texto exato no Lattes em `f_tpo_acao_inov`: `"Mestado Profissional"` (sem "r", typo original do Lattes) com valor `"MP"`. O preenchimento deve sempre priorizar o `valor` (`"MP"`).
3. **Campos condicionais/somente leitura ligados a popups:**
   - `f_inst` e `f_orgao`: `desabilitado: true` (preenchidos pela lupa `pp_lista_inst`).
   - `f_txt_nme_empresa`: `somente_leitura: true` e `visivel_inicial: false` (habilitado quando há cooperação com empresa; ainda sem tratamento específico no `autofill_core.js`).
   - Regras de validação levantadas em `obrigatorios_extensao.json`: `F_ANO_FIM` só pode ser preenchido se situação for `Concluído` (`C`); quando há potencial de inovação, a descrição é obrigatória; equipe exige 1 responsável e exatamente 1 coordenador.
