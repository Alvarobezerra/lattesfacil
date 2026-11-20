# Relatório Final — Rastreio Independente da Plataforma Lattes (Antigravity)

**Data:** 2026-11-20  
**Escopo:** 100% das seções do menu do Currículo Lattes (`Dados gerais`, `Formação`, `Atuação`, `Projetos` [auditado via capturas], `Produções Bibliográficas/Técnicas/Artísticas`, `Patentes e Registros`, `Eventos`, `Orientações`, `Bancas` e `Citações`) — **63 formulários/subformulários** documentados com JSONs brutos em `docs/auditoria-antigravity/capturas/` e evidências visuais em `browser_evidence/58f005e7-da4d-4c7c-bfba-20fb50aa8d8d/`.

> **Isolamento garantido:** Nenhum arquivo de código ou arquivo do Claude fora de `docs/auditoria-antigravity/` foi alterado. Todos os testes de salvamento/exclusão deixaram o CV limpo.

---

## 1. Mapa de Comportamentos de Abertura (Wizards e Modais)
Para espelhar a Plataforma Lattes como um espelho no `lattesdata`, o preenchimento deve respeitar **5 padrões distintos de abertura**:
1. **Auto-abertura quando vazio (0 itens):** a maioria das listas (`pkg_texto`, `prc_bib_*`, `prc_tec_*`, `pkg_arte_nova`, `pkg_revisor`, `pkg_banca_*`, `CP`, `CR`, `pkg_orient`) abre o formulário automaticamente quando não há registros; se já houver itens, exige clicar em `Incluir novo item`.
2. **Abertura direta (sem lista):** `prc_ident`, `prc_endereco`, `pkg_resume.form`, `prc_outras_inf`, `prc_area_atuacao` e `prc_indicadores` (`f_base=1,2,3,4,99`).
3. **Modal de DOI / Periódico em 2 passos (`findp` -> `finfivip`):** `Artigos completos publicados em periódicos` (`PKG_ARTIGO.form`) — aceita DOI direto ou exige buscar periódico + preencher `ISSN`, `Volume` e `Página inicial`, abrindo `F_CTR=FIV` com `f_titulo_periodico`, `f_jcr`, `f_issn`, `f_volume`, `f_serie` e `f_pag_ini` já preenchidos e `disabled=true`.
4. **Wizard de 2 passos (`winLivrosCaps`):** `Livros e capítulos` — passo 1 exige `Tipo` (`Livro`/`Capitulo`) + `DOI/ISBN` válido via `prc_valida_issn`; passo 2 exige `ISBN` + `Ano` + `Autor/Editor`.
5. **Modal de Instituição + Registro (`infDadPat()`):** `Patente (PP)`, `Software Registrado (PC)`, `Desenho Industrial (DI)`, `Marca Registrada (MR)`, `Topografia (TC)` — exige `escolhe_inst()` (12 órgãos) + `f_cod_reg` (com validação de máscara INPI em `PC`, `DI`, `MR`, `TC`).
6. **Seletor de Nível/Natureza prévio:** `Formação acadêmica` (10 níveis), `Pós-doutorado/Livre-docência` (2 níveis), `Formação complementar` (wizard 2 telas `form` -> `FORM2`), `Atuação profissional > Atividades` (9 naturezas `f_natur_ativ`).

---

## 2. Principais Regras Condicionais Descobertas ao Vivo
- **Identificação (`PRC_IDENT`):** `f_nome_social_r = Sim` revela `tr#NomeSocial` (`f_nome_social`, max 60); `f_pcd_r = Sim` revela `tr#listaPCD` (6 checkboxes `f_pcd`).
- **Idiomas (`PKG_IDIOMA`):** selecionar `Libras (LB)` (`veriLibra(this)`) remove `Lê` e `Escreve`, mantendo apenas `Expressa-se` e `Compreende`.
- **Licença (`PKG_LICENCA`):** default de visibilidade é **`Privado`** (único no Lattes); `f_tipo_licenca` muda rótulo entre `Data de nascimento` (`M`/`P`) e `Data de adoção` (`A`).
- **Formação acadêmica (`Doutorado`):** `f_tpo_doutorado` (`sanduíche` / `co-tutela` / `co-tutela/sanduíche`) muda rótulo de `f_inst` e insere blocos extras (`f_inst_dout*`, `f_orient_dout*`, `f_meses_sw*`); `F_STATUS = incompleto` muda `Conclusão (ano)` para `Interrupção (ano)`.
- **Formação complementar (`FORM2`):** `Status` da Tela 1 controla `f_ano_fim` na Tela 2 (`Conclusão`, `Interrupção`, ou `disabled` em `em andamento`).
- **Atuação profissional (`PKG_ATIV`):** `Outro (especifique)` habilita digitação livre em `f_vinc`; `f_status = Anterior` revela e exige `f_mes_fim` / `f_ano_fim` (o mesmo ocorre em `PKG_REVISOR` `MB`, `MA`, `RV`, `RA`); em Atividades, `Ensino (4)` troca `Órgão/Unidade` por `Nível` (`401..409`) + `Curso`.
- **Inovação (`f_sta_inovacao`):** presente em `Produtos`, `Processos`, `Software s/ registro`, `Patente`, `Software c/ registro`, `Cultivares`, `Desenho Industrial`, `Marca`, `Topografia`. Quando `Sim`, exibe e exige `f_txt_potencial` (max 400). *Atenção aos defaults:* em `PC` e `DI` inicia marcado em `Sim`; em `PP` inicia desmarcado e exige escolha; nos demais inicia em `Não`.
- **Participação em eventos (`PKG_EVENTO`):** `F_FORMA` (`montaTipoApres`) popula `F_TPO` dinamicamente; `Ouvinte` esvazia `F_TPO` e dispensa `F_TPO` e `f_titulo`; `F_TPO` reescreve o rótulo de `f_titulo`.
- **Orientações (`PKG_ORIENT`):** `Em andamento` tem apenas **6** opções de Natureza (sem TCC de graduação) e exige `Curso` no salvamento em branco; `Concluída` tem **7** opções e permite salvar `Iniciação Científica` sem `Curso`; `Supervisão de pós-doutorado` bloqueia marcação de `f_tpo_orient`.

---

## 3. Oportunidades de Melhoria Prioritárias para o `lattesdata` (Fase 2)
1. **Migrar os 4 itens legados** (`artigo`, `anais`, `apresentacao`, `orientacao`) de `static/index.html` para o motor de specs — resolve ausência de `F_STA_DIVULGACAO_CIENTIFICA`, `f_titulo_en`, `f_ref_en`, `tabelasetor` (CNAE), `maxlength` curtos (ex.: `cidade_evento`/`cidade_editora` = 30 em `anais`, `f_local` = 30 em `texto`), domínio incompatível de `f_meio` em `artigo` (3 opções reais vs 7 no HTML), e TCC inexistente em `orientacao_andamento`.
2. **Corrigir catálogo de países em Projetos (`f_pais_inst`):** `projeto.json` usa 244 países, mas o Lattes aceita apenas **79** em Projetos (165 causariam falha).
3. **Preservar espaços à direita nos `<select>` legados do Lattes:** `f_sub_tipo` em `Prefácio` (`"31 "`, `"32 "`, `"33 "`) e `f_sub_prod` em `Bancas de trabalho` (`"34 "`, `"35 "`).
4. **Espelhar regras de exclusão e validações:** fluxo `confirm("Deseja excluir o item selecionado?")` validado em `pkg_orient.lista`, e mensagens de obrigatoriedade documentadas por variante em cada JSON de `capturas/`.

---

## 4. Índice dos Arquivos Gerados
- **Auditorias comparativas:** `auditoria-projeto-e-artigo.md`, `auditoria-anais.md`, `auditoria-apresentacao.md`, `auditoria-orientacao-concluida.md`, `auditoria-orientacao-andamento.md`, `auditoria-livro.md`, `auditoria-capitulo-e-texto.md`, `auditoria-artigo-aceito-e-partitura.md`, `auditoria-demais-bibliograficas.md`, `auditoria-tecnica-lote1.md`, `auditoria-tecnica-lote2.md`, `auditoria-tecnica-lote3.md`.
- **Capturas JSON ao vivo (`capturas/`):** 62 arquivos JSON cobrindo todas as seções e formulários da Plataforma Lattes.
