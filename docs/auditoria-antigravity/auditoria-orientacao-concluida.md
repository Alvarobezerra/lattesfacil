# Auditoria Independente (Ao Vivo): Orientações e Supervisões Concluídas (`orientacao_concluida`)

**Data:** 2026-11-20  
**Captura ao vivo:** [capturas/orientacao_concluida.json](capturas/orientacao_concluida.json)  
**URL no Lattes:** `pkg_orient.form?f_tipo=C` (`PKG_ORIENT` / `PKG_ORIENT.FORM`)  
**Evidência visual:** `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/final_step_150.png`

---

## 1. Status no `lattesdata`
- Existe spec gerada em `itens/especificacao/orientacao_concluida.json` com os 18 campos do formulário real, **porém** na interface principal (`static/index.html`) o item ainda usa o **formulário legado** (`data-tipos="orientacao"`).

## 2. Comportamento Condicional e Lupas (Lattes ao vivo)
- **Natureza (`F_COD_PROD`):** 7 níveis (`Dissertação de mestrado`, `Tese de doutorado`, `Monografia de conclusão de curso de aperfeiçoamento/especialização`, `Trabalho de conclusão de curso de graduação`, `Iniciação Científica`, `Supervisão de pós-doutorado`, `Orientação de outra natureza`), cada um com `onclick="testa_nivel(0..6);"`.
  - Alternar `F_COD_PROD` **não oculta nem desabilita** elementos no DOM, mas controla handlers: em `Supervisão de pós-doutorado` (índice 5), `f_tpo_orient` (`test_ori()`) **bloqueia** a marcação de `Orientador principal`/`coorientador`, enquanto em `Dissertação de mestrado` (índice 0) permite marcar normalmente.
- **Campos `input-lupa` (preenchimento indireto):**
  - `f_dsc_outra` (`readOnly=true`, `maxlength=100`, lupa `dominio()`): usado para Tipo de mestrado (Acadêmico/Profissional) e Orientação de outra natureza.
  - `f_inst` (`disabled=true`, `maxlength=75`, lupa `sele_inst()`): instituição sempre bloqueada para digitação direta.
  - `f_curso` (`disabled=true`, `maxlength=50`, lupa `curso()`): curso sempre bloqueado para digitação direta.
  - `f_nme_agencia` (`maxlength=75`, lupa `agencia()`): `F_BOLSA` (`agnull(0/1)`) não oculta nem desabilita o campo, atuando no controle de valor.
  - `f_nme_orient` (`maxlength=60`): possui ícone auxiliar da **CAPES** (`capesdados()`) para importação em Mestrado/Doutorado.

## 3. Divergências entre `static/index.html`, Spec e Lattes Real
1. **Ausentes no formulário legado (`static/index.html`):**
   - `f_titulo_en` (`Title`, max 400) e `f_ref_en` (`Other information`, max 3800).
   - Lista `tabelasetor` / `setorHolder` (Tabela CNAE, ação "Listar todos").
   - Suporte a `Orientação de outra natureza` no campo Tipo (`f_dsc_outra` via `dominio()`; no HTML atual `#tipo_mestrado` só tem `Acadêmico`/`Profissional`).
   - `pais` e `idioma` como `<input type="text">` livre em vez de `<select>` (244 países / 152 idiomas).
   - `maxlength` ausentes em `titulo` (400), `homepage` (250), `instituicao_orient` (75), `curso_orient` (50) e `agencia_financiadora` (75).
2. **Atenção na spec (`itens/especificacao/orientacao_concluida.json`):**
   - `f_dsc_outra` está marcado como `obrigatorio: true` na spec, mas no Lattes é condicional ("apenas para dissertação de mestrado e orientação de outra natureza").
   - `F_COD_PROD` está como `obrigatorio: false` na spec, embora seja o nível obrigatório da orientação.

## 4. Regras de Salvamento e Exclusão (Validadas ao Vivo)
1. **Salvamento em branco (`pre_check()`):**
   - `alert`: `"Por favor informe os seguintes campos obrigatórios:\n\nNatureza\nTítulo do trabalho orientado\nAno de término da orientação\nNome do orientando\nInstituição"`
2. **Salvamento mínimo (`Iniciação Científica`):**
   - `Curso` (`f_curso`), `Tipo` (`f_dsc_outra`) e `Tipo de orientação` (`f_tpo_orient`) **não** são obrigatórios para Iniciação Científica.
   - Sem `Instituição`, bloqueia com: `"Por favor informe os seguintes campos obrigatórios:\n\nInstituição"`.
   - Preenchendo `Instituição` via lupa `sele_inst()` (`prc_inst_form`), o salvamento concluiu e listou o item em `pkg_orient.lista?f_tipo=C`.
3. **Regra de exclusão (`pkg_orient.lista`):**
   - Botão `Excluir` aciona `onclick="excluir('...');"` com diálogo `confirm("Deseja excluir o item selecionado?")`.
   - Ao confirmar, recarrega a lista limpa (`browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/step_188.png`).
