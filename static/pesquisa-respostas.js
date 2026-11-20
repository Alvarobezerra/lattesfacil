"use strict";
(function () {
  const app = document.getElementById("app");
  const filtro = document.getElementById("filtroBusca");
  const resumo = document.getElementById("resumoContagem");
  let todas = [];

  function el(tag, props, ...kids) {
    const node = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => {
      if (k === "class") node.className = v;
      else node.setAttribute(k, v);
    });
    kids.flat().forEach((c) => {
      if (c != null) node.append(c instanceof Node ? c : document.createTextNode(String(c)));
    });
    return node;
  }

  function formatarData(iso) {
    const d = new Date(iso);
    return isNaN(d.getTime()) ? String(iso || "") : d.toLocaleString("pt-BR");
  }

  function renderizar() {
    if (!app) return;
    const q = (filtro && filtro.value ? filtro.value : "").trim().toLowerCase();
    const filtradas = !q
      ? todas
      : todas.filter((item) => {
          if ((item.respondente || "").toLowerCase().includes(q)) return true;
          return (item.respostas || []).some((a) =>
            (a.pergunta || "").toLowerCase().includes(q) || (a.resposta || "").toLowerCase().includes(q)
          );
        });

    if (resumo) {
      resumo.textContent = `${filtradas.length} de ${todas.length} submiss${todas.length === 1 ? "ão" : "ões"}`;
    }

    if (!todas.length) {
      app.className = "card";
      app.replaceChildren(el("p", { class: "muted" }, "Ainda não há respostas registradas."));
      return;
    }

    if (!filtradas.length) {
      app.className = "card";
      app.replaceChildren(el("p", { class: "muted" }, "Nenhuma resposta corresponde ao filtro digitado."));
      return;
    }

    app.className = "";
    app.replaceChildren(
      ...filtradas.map((item) => {
        const lista = Array.isArray(item.respostas) ? item.respostas : [];
        const cab = el(
          "div",
          { class: "card-head" },
          el("div", {}, el("strong", {}, item.respondente || "Pesquisador convidado"), el("p", { class: "muted" }, formatarData(item.criado_em))),
          el("span", { class: "pill" }, `${lista.length} resposta${lista.length === 1 ? "" : "s"}`)
        );
        const blocos = lista.map((a) =>
          el("div", { class: "answer" }, el("div", { class: "question" }, a.pergunta || ""), el("div", { class: "resp" }, a.resposta || ""))
        );
        return el("article", { class: "card" }, cab, ...blocos);
      })
    );
  }

  async function carregar() {
    try {
      const r = await fetch("/api/pesquisa/pesquisadores");
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || "Acesso negado.");
      todas = Array.isArray(d.respostas) ? d.respostas : [];
      renderizar();
    } catch (e) {
      if (resumo) resumo.textContent = "Erro ao carregar";
      if (app) {
        app.className = "card";
        app.replaceChildren(el("p", { class: "error" }, e.message || "Falha ao carregar respostas."));
      }
    }
  }

  if (filtro) filtro.addEventListener("input", renderizar);
  carregar();
})();
