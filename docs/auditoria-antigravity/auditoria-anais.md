# Auditoria Independente (Ao Vivo): Trabalhos Publicados em Anais de Eventos (`anais`)

**Data:** 2026-11-20  
**Captura ao vivo:** [capturas/trabalhos_anais_eventos.json](capturas/trabalhos_anais_eventos.json)  
**URL no Lattes:** `pkg_trabalho.form` (`GN_TRABALHO` / `PKG_TRABALHO.FORM`)  
**Evidência visual:** `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/final_step_93.png`

---

## 1. Status no `lattesdata`
- **Não há spec** em `itens/especificacao/` para `anais` — o item depende 100% do formulário legado em `static/index.html` (linhas 225–540) e do mapeamento direto em `extensao/autofill_core.js` (linhas 940–966).

## 2. Comportamento e Campos Condicionais (Lattes ao vivo)
- **Sem modal prévio de DOI:** a seção **D.O.I** (`f_cod_doi`, max 250) aparece diretamente no topo do formulário, com `onclick="seta_doi(this.value);"`, `onblur="call_doi();"` e `onfocus="focusDoi()"`.
- **Natureza (`F_COD_PROD`):** `Completo`, `Resumo`, `Resumo Expandido` — testado ao vivo alternando as 3 opções: **nenhum campo muda de visibilidade** no DOM.
- **Educação e Popularização de C&T (`F_STA_DIVULGACAO_CIENTIFICA`):** `sim` / `não` (default `não`) — também não altera visibilidade de outros campos.
- **Visibilidade:** usa widget customizado `.ms-dd` (default `Público`, opções `Público` / `Privado`).

## 3. Campos do Lattes AUSENTES em `static/index.html`
1. `F_STA_DIVULGACAO_CIENTIFICA` ("É uma produção para educação e popularização de CeT?", radio `sim`/`não`) — `autofill_core.js` (linha 949) já tenta preencher, mas não existe no HTML.
2. `f_titulo_en` ("Title", text `maxlength=400`).
3. `f_ref_en` ("Other information", textarea `maxlength=3800`).
4. Lista `tabelasetor` / `setorHolder` ("Setor de aplicação da Tabela CNAE", ação "Listar todos").

## 4. Divergências de Limites (`maxlength`) e Tipos em `static/index.html`
| Campo | `static/index.html` | Lattes real (`pkg_trabalho.form`) | Impacto / Risco |
| --- | --- | --- | --- |
| `titulo` (`f_titulo`) | sem `maxlength` | `maxlength=400` | Truncamento ou rejeição no Lattes |
| `doi` (`f_cod_doi`) | sem `maxlength` | `maxlength=250` | Baixo, mas convém espelhar |
| `homepage` (`f_homepage`) | sem `maxlength` | `maxlength=250` | URLs longas podem falhar |
| `nome_evento` (`f_evento`) | sem `maxlength` | `maxlength=255` | Títulos longos de eventos |
| `cidade_evento` (`f_cidade_evento`) | sem `maxlength` | **`maxlength=30`** | **Alto risco:** cidades + UF/país passam de 30 chars |
| `titulo_anais` (`f_titulo_pub`) | sem `maxlength` | `maxlength=255` | Títulos longos de anais |
| `editora` (`f_editora`) | sem `maxlength` | `maxlength=100` | Nomes compostos de editoras |
| `cidade_editora` (`f_cidade_ed`) | sem `maxlength` | **`maxlength=30`** | **Alto risco:** limite curto de 30 chars |
| `isbn_issn` (`f_isbn`) | sem `maxlength` | `maxlength=13` | Autofill já remove não-dígitos |
| `pagina_inicial` / `pagina_final` | sem `maxlength` | `maxlength=15` | Aceita número de artigo eletrônico |
| `pais` (`f_pais`) | `<input type="text">` | `<select>` (244 países, default `BRA`) | Erro de digitação impede lookup |
| `idioma` (`F_IDIOMA`) | `<input type="text">` | `<select>` (152 idiomas, default `PT`) | Erro de digitação impede lookup |
| `meio_divulgacao` (`f_meio`) | 7 opções (sem vazia) | 7 opções + vazia `""` (`I,M,D,F,H,O,V`) | Domínio compatível para `anais` |

## 5. Listas e Limites de Sugestão (Modais)
- `tabelaAutor` / `autorHolder`: input suggest `maxlength=60`, ações `Listar todos` e `Incluir novo`.
- `tabelapalavra` / `palavraHolder`: input suggest `maxlength=50`, ações `Listar todos` e `Incluir nova`.
- `tabelaarea` / `areaHolder`: input suggest `maxlength=86`, ações `Listar todos` e `Incluir nova`.
- `tabelasetor` / `setorHolder`: input suggest sem `maxlength`, ação apenas `Listar todos` (catálogo fechado CNAE).
