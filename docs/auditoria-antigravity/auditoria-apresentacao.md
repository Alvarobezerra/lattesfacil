# Auditoria Independente (Ao Vivo): Apresentação de Trabalho e Palestra (`apresentacao`)

**Data:** 2026-11-20  
**Captura ao vivo:** [capturas/apresentacao_trabalho.json](capturas/apresentacao_trabalho.json)  
**URL no Lattes:** `prc_tec_apres` (`GN_TEC` / `PRC_TEC_APRES`)  
**Evidência visual:** `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/final_step_124.png`

---

## 1. Status no `lattesdata`
- **Não há spec** em `itens/especificacao/` para `apresentacao` — o item usa o formulário legado em `static/index.html` (linhas 225–540) com opções dinâmicas de `natureza` injetadas por `static/app.js` (linha 59) e autofill em `extensao/autofill_core.js` (linhas 922–939).

## 2. Paridade de Natureza e Comportamento Condicional
- **Natureza (`F_COD_PROD`):** 6 opções no Lattes real (`Comunicação`, `Conferência ou palestra`, `Congresso`, `Seminário`, `Simpósio`, `Outra`) — **`static/app.js` (linha 59) já espelha todas as 6 opções** dinamicamente no `#natureza`.
- **Teste condicional:** Alternar `F_COD_PROD` no Lattes ao vivo **não altera** a visibilidade nem habilitação de nenhum campo do DOM (`html_length` constante em `18132` bytes).
- **Visibilidade:** Widget `.ms-dd.ms-pr` (default `Público`, opções `Público` / `Privado`).

## 3. Campos do Lattes AUSENTES em `static/index.html`
1. `F_STA_DIVULGACAO_CIENTIFICA` ("É uma produção para educação e popularização de CeT?", radio `sim`/`não`, default `não`) — `autofill_core.js` (linha 931) já tenta preencher, mas o campo não existe no HTML.
2. `f_titulo_en` ("Title", text `maxlength=400`).
3. `f_ref_en` ("Other information", textarea `maxlength=3800`).
4. Lista `tabelasetor` / `setorHolder` ("Setor de aplicação da Tabela CNAE", ação "Listar todos").

## 4. Divergências de Limites (`maxlength`) e Tipos em `static/index.html`
| Campo | `static/index.html` | Lattes real (`prc_tec_apres`) | Observação |
| --- | --- | --- | --- |
| `titulo` (`f_titulo`) | sem `maxlength` | `maxlength=400` | Falta limite no HTML |
| `homepage` (`f_homepage`) | sem `maxlength` | `maxlength=250` | Falta limite no HTML |
| `nome_evento` (`f_nme_evento`) | sem `maxlength` | `maxlength=255` | Falta limite no HTML |
| `instituicao_promotora` (`f_inst`) | `maxlength=255` | `maxlength=255` | Paridade OK |
| `local_evento` (`f_local`) | `maxlength=255` | `maxlength=255` | Paridade OK |
| `cidade_evento` (`f_cidade`) | sem `maxlength` | `maxlength=255` | Diferente de `anais` (que é 30), aqui é 255 |
| `pais` (`f_pais`) | `<input type="text">` | `<select>` (244 países, default `BRA`) | Risco de erro de digitação |
| `idioma` (`F_IDIOMA`) | `<input type="text">` | `<select>` (152 idiomas, default `PT`) | Risco de erro de digitação |
| `meio_divulgacao` (`f_meio`) | 7 opções (sem vazia) | 7 opções + vazia `""` (`I,M,D,F,H,O,V`) | Domínio compatível |
