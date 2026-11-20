# Auditoria Independente (Ao Vivo): Produção Técnica — Lote 3 (2A, 2B, 2C)

**Data:** 2026-11-20  
**Capturas:** [cartas_mapas.json](capturas/cartas_mapas.json) · [curso_ministrado.json](capturas/curso_ministrado.json) · [material_didatico.json](capturas/material_didatico.json)

---

## Destaques
1. **Cartas, mapas ou similares (`PRC_TEC_CARTA`):**
   - `F_COD_PROD`: `Aerofotograma`, `Carta`, `Fotograma`, `Mapa`, `Outro` (obrigatório).
   - Detalhamento: `f_tema`, `f_tecnica`, `f_finalidade`, `f_area`, `f_inst` (todos max 255).
2. **Curso de curta duração ministrado (`PRC_TEC_CURSO`):**
   - `F_COD_PROD`: `Extensão`, `Aperfeiçoamento`, `Especialização`, `Outro` (obrigatório como `Nível do curso`).
   - **Sem `f_homepage`**; inclui `f_participacao` (`Docente`, `Organizador`, `Outra`), `f_duracao` (max 5), `f_unidade` (`horas`, `dias`, `semanas`), `f_inst`, `f_local`, `f_cidade`.
3. **Desenvolvimento de material didático ou instrucional (`PRC_TEC_DESEN`):**
   - `f_natureza` é texto livre obrigatório (`maxlength=100`); `f_homepage` tem botão `mostrarPreviaVideo()`.
