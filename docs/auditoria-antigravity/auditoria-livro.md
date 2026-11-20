# Auditoria Independente (Ao Vivo): Livro Publicado / Organizado (`PKG_LVR_CAP.FORM_LVR`)

**Data:** 2026-11-20  
**Captura ao vivo:** [capturas/livro.json](capturas/livro.json)  
**Evidência visual:** `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/final_step_283.png`

---

## 1. Fluxo de Abertura (Wizard `winLivrosCaps`)
- Ao clicar em **Incluir novo item**, abre o modal `PKG_LVR_CAP.INFORMAR_DADOS_LVR_CAP`:
  1. **Passo 1:** Escolher `Tipo de Produção` (`Livro` ou `Capitulo`) e informar **DOI ou ISBN** (`#doiissn`, max 60). Clicar em **Confirmar** com `#doiissn` vazio **não faz nada**; ISBN inválido dispara `"O ISSN informado é inválido."` via `prc_valida_issn` e fecha o modal.
  2. **Passo 2** (quando ISBN é válido): pede `ISBN` (`issnisbn`), `Ano` (`year`) e `Autor/Editor` (`autoreditor`). Só abre `PKG_LVR_CAP.FORM_LVR` quando todos estão preenchidos, já pré-carregando `f_ano` e `f_isbn`.

## 2. Regras de Salvamento e Comportamento Condicional
- **Obrigatórios ao salvar (`check()`):**
  - `Tipo` (`F_COD_PROD`: `Livro publicado` ou `Organização de obra publicada`)
  - `Título do livro` (`f_titulo`, max 400)
  - `Ano` (`f_ano`, max 4)
  - `ISBN` (`f_isbn`, max 13 — validado por dígito verificador!)
  - `Edição` (`f_edicao`, max 3 — **`Número da edição/revisão` é obrigatório!**)
  - `Autores`: `"O seu nome deverá ser incluído na lista de autores."`
- **Comportamento condicional:**
  - `f_sub_prod` (`Natureza`, max 20) é `disabled=true` e preenchido via lupa `dominio()`.
  - Trocar `F_COD_PROD` não altera visibilidade no DOM, mas aciona `onclick="apaga();"` limpando `f_sub_prod`.
  - `f_cidade_ed` tem limite curto de **30 caracteres**.
