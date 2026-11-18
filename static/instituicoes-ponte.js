"use strict";
// Ponte do banco de instituições: a extensão devolve o que a lupa do Lattes retornou (uso e coleta); aqui vai ao servidor
// com a sessão do usuário. Cada consulta traz um lote_id: se várias abas do app receberem a mesma mensagem, o servidor
// grava uma vez só. Incluída em todas as páginas que possam estar abertas durante o preenchimento.
(function () {
  window.addEventListener("message", async (e) => {
    if (e.source !== window || e.origin !== location.origin) return;
    const m = e.data;
    if (!m || m.type !== "lattesdata-ext-inst-lote") return;
    const lote = Array.isArray(m.lote) ? m.lote : [];
    for (const q of lote) {
      try {
        await fetch("/api/instituicoes/registrar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(q) });
      } catch (err) { /* sem rede: a consulta se perde; não afeta o preenchimento */ }
    }
    window.dispatchEvent(new CustomEvent("lf-inst-lote", { detail: { fim: m.fim || null, n: lote.length } }));
  });
})();
