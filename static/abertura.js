// Tela de abertura: indicadores reais vindos de /api/abertura. Todo texto externo entra por textContent (nunca innerHTML).
(function () {
  const $ = (id) => document.getElementById(id);
  const KNOWN_ORCIDS = { "Aramys Silva dos Reis": "0000-0003-4999-6382" };
  const NS = "http://www.w3.org/2000/svg";
  const TIPOS = { artigo: "Artigos", anais: "Trabalhos em anais", apresentacao: "Apresentações", orientacao: "Orientações",
    orientacao_concluida: "Orientações concluídas", orientacao_andamento: "Orientações em andamento" };
  const fmt = (n) => (n || 0).toLocaleString("pt-BR");
  const store = {
    get(k) { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };

  function el(tag, props, ...kids) {
    const e = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => (k === "class" ? (e.className = v) : e.setAttribute(k, v)));
    kids.flat().forEach((c) => c != null && e.append(c));
    return e;
  }
  const empty = (box, msg) => box.replaceChildren(el("p", { class: "empty" }, msg));
  const doiUrl = (d) => (d ? `https://doi.org/${encodeURIComponent(d).replace(/%2F/gi, "/")}` : "");

  // Escolha feita na tela de login (cookie lf_user, de vida curta): vira o usuário ativo e o cookie é apagado.
  const NOMES_LOGIN = { alvaro: "Álvaro Antônio Bezerra dos Santos", aramys: "Aramys Silva dos Reis" };
  try {
    const m = document.cookie.match(/(?:^|;\s*)lf_user=([a-z]+)/);
    if (m && NOMES_LOGIN[m[1]]) store.set("lf-usuario", NOMES_LOGIN[m[1]]);
    if (m) document.cookie = "lf_user=; Path=/; Max-Age=0";
  } catch (e) {}

  const usuario = store.get("lf-usuario") || "Álvaro Antônio Bezerra dos Santos";
  let orcid = store.get("lf-orcid:" + usuario) || KNOWN_ORCIDS[usuario] || "";
  let dados = null, atual = "prod", janela = 5;

  const iniciais = usuario.split(/\s+/).filter((p) => p.length > 2).map((p) => p[0]).slice(0, 2).join("").toUpperCase() || "?";
  $("av").textContent = $("av2").textContent = iniciais;
  $("nome").textContent = usuario.split(/\s+/)[0];

  function formOrcid(msg) {
    const input = el("input", { type: "text", placeholder: "0000-0000-0000-0000", "aria-label": "ORCID", maxlength: "19" });
    const f = el("form", { class: "orcid" }, input, el("button", { class: "btn btn-p", type: "submit" }, "Ver meus indicadores"));
    f.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const v = input.value.trim().toUpperCase();
      if (!/^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/.test(v)) { input.setCustomValidity("Formato 0000-0000-0000-0000"); input.reportValidity(); return; }
      input.setCustomValidity("");
      store.set("lf-orcid:" + usuario, v); orcid = v; dados = null; tentativas = 0; carregar();
    });
    $("banner").replaceChildren(el("div", { class: "banner" }, msg, f));
  }

  function kpi(id, rotulo, valor, delta, sub, flat) {
    const b = el("button", { class: "card kpi" + (id === atual ? " on" : ""), type: "button", "data-k": id },
      el("div", { class: "lb" }, rotulo), el("div", { class: "v" }, valor),
      el("div", { class: "d" + (flat ? " flat" : "") }, delta), el("div", { class: "sub" }, sub));
    b.addEventListener("click", () => { atual = id; renderKpis(); desenhar(); });
    return b;
  }

  function variacao(no, ant, ano) {
    const d = no - ant;
    return d === 0 ? ["sem variação em " + ano, true] : [(d > 0 ? "▲ +" + d : "▼ " + Math.abs(d)) + " em " + ano + " (parcial)", d < 0];
  }

  function renderKpis() {
    const p = dados.producao, c = dados.citacoes, e = dados.eventos, a = dados.alcance, ano = dados.ano_atual;
    const [dp, fp] = variacao(p.no_ano, p.ano_anterior, ano);
    const serie = c.serie, noAno = c.no_ano;
    $("kpis").replaceChildren(
      kpi("prod", "Produção", fmt(p.total), dp, "obras indexadas (OpenAlex)", fp),
      kpi("cit", "Citações", fmt(c.total), noAno ? "▲ " + fmt(noAno) + " em " + ano : "—", `h ${c.h} · i10 ${c.i10} · sem autocit. ${fmt(c.sem_autocitacao)}`, !noAno),
      kpi("ev", "Eventos", fmt(e.total), e.total ? "enviados ao LattesData" : "nenhum envio ainda", `${fmt(e.orientacoes)} orientações enviadas`, true),
      kpi("imp", "Alcance", fmt(a.periodicos), "periódicos que citam", `${fmt(a.citantes_unicos)} trabalhos citantes`, true),
    );
    void serie;
  }

  function desenhar() {
    const cfg = {
      prod: ["Produção por ano", "#00a3c4", dados.producao.serie, () => [["Total", fmt(dados.producao.total)], ["Neste ano", dados.producao.no_ano],
        ["Melhor ano", dados.producao.melhor_ano ? `${dados.producao.melhor_ano[0]} (${dados.producao.melhor_ano[1]})` : "—"], ["Fonte", "OpenAlex"]]],
      cit: ["Citações por ano", "#10b981", dados.citacoes.serie, () => [["Total", fmt(dados.citacoes.total)], ["Sem autocitação", fmt(dados.citacoes.sem_autocitacao)],
        ["Índice h", dados.citacoes.h], ["Obras analisadas", `${dados.citacoes.obras_consideradas} de ${dados.citacoes.obras_indexadas}`]]],
      ev: ["Eventos por ano (envios ao LattesData)", "#38bdf8", dados.eventos.serie, () => [["Total", fmt(dados.eventos.total)], ["Orientações", fmt(dados.eventos.orientacoes)],
        ["Envios no total", fmt(dados.envios.total)], ["Fonte", "seus envios"]]],
      imp: ["Periódicos que mais citam você", "#1b365d", null, () => [["Periódicos", fmt(dados.alcance.periodicos)], ["Trabalhos citantes", fmt(dados.alcance.citantes_unicos)],
        ["Autocitações", fmt(dados.citacoes.autocitacoes)], ["Fonte", "OpenAlex + OC"]]],
    }[atual];
    $("chart-title").textContent = cfg[0];
    $("foot").replaceChildren(...cfg[3]().map(([k, v]) => el("div", {}, k, el("b", {}, String(v)))));
    const svg = $("chart"); svg.replaceChildren();
    const add = (tag, attrs, text) => { const n = document.createElementNS(NS, tag); Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v)); if (text != null) n.textContent = text; svg.appendChild(n); return n; };
    let rotulos, valores;
    if (cfg[2]) { const s = janela ? cfg[2].slice(-janela) : cfg[2]; rotulos = s.map((x) => String(x.ano)); valores = s.map((x) => x.valor); }
    else { const t = dados.alcance.top_periodicos; rotulos = t.map((x) => x.nome.length > 14 ? x.nome.slice(0, 13) + "…" : x.nome); valores = t.map((x) => x.citacoes); }
    $("src").textContent = "";
    if (!valores.length || valores.every((v) => !v)) { add("text", { x: 350, y: 105, "text-anchor": "middle", "font-size": 14, fill: "var(--muted)" }, "Sem dados para mostrar ainda"); return; }
    const W = 700, H = 210, pl = 34, pb = 24, pt = 10, max = Math.max(...valores) * 1.15, bw = (W - pl) / valores.length;
    for (let i = 0; i <= 3; i++) { const y = pt + (H - pb - pt) * i / 3;
      add("line", { x1: pl, x2: W, y1: y, y2: y, stroke: "var(--border)" }); add("text", { x: 0, y: y + 4, "font-size": 10, fill: "var(--muted)" }, String(Math.round(max * (1 - i / 3)))); }
    valores.forEach((v, i) => {
      const bh = (H - pb - pt) * v / max, x = pl + i * bw + bw * .18, w = bw * .64;
      const parcial = cfg[2] && Number(rotulos[i]) === dados.ano_atual;
      const r = add("rect", { x, y: H - pb - bh, width: w, height: bh, rx: 4, fill: cfg[1], opacity: parcial ? .55 : 1 }); r.appendChild(Object.assign(document.createElementNS(NS, "title"), { textContent: `${rotulos[i]}: ${v}${parcial ? " (ano em andamento)" : ""}` }));
      add("text", { x: x + w / 2, y: H - 8, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)" }, rotulos[i]);
    });
    $("src").append("Barra clara = ano em andamento. Citações unificadas de ", el("b", {}, "OpenAlex"), ", ", el("b", {}, "OpenCitations"), " e ", el("b", {}, "Crossref"), ".");
  }

  function renderFeed() {
    const lista = dados.citantes_recentes;
    if (!lista.length) { empty($("feed"), orcid ? "Nenhuma citação encontrada ainda." : "Informe seu ORCID para ver quem cita você."); return; }
    $("feed").replaceChildren(...lista.map((c) => {
      const t = el("div", { class: "t" }, el("b", {}, "Citado em: "), c.titulo || "(título não informado)");
      if (c.autocitacao) t.append(el("span", { class: "conf" }, "autocitação"));
      t.append(el("span", { class: "conf" }, c.fontes.length + (c.fontes.length > 1 ? " fontes" : " fonte")));
      const meta = [c.veiculo, c.ano].filter(Boolean).join(" · ");
      const body = el("div", { class: "b" }, t, el("div", { class: "m" }, (meta ? meta + " · " : "") + "cita: " + c.obra));
      if (c.doi) body.append(el("div", { class: "acts" }, el("a", { href: doiUrl(c.doi), target: "_blank", rel: "noopener noreferrer" }, "Ver artigo citante")));
      return el("article", { class: "post", style: "--c:#10b981" }, el("div", { class: "ico" }, "❝"), body);
    }));
  }

  function renderSide() {
    const top = dados.obras_mais_citadas;
    top.length ? $("top").replaceChildren(...top.map((o) => el("div", { class: "row" },
      el("div", {}, el("div", { class: "n" }, o.titulo || "(sem título)"), el("div", { class: "s" }, [o.veiculo, o.ano].filter(Boolean).join(" · "))),
      el("div", { class: "q" }, fmt(o.total))))) : empty($("top"), "Sem obras com citações.");
    const v = dados.alcance.top_periodicos;
    v.length ? $("vei").replaceChildren(...v.map((x) => el("div", { class: "row" }, el("div", { class: "n" }, x.nome), el("div", { class: "q" }, String(x.citacoes))))) : empty($("vei"), "Sem dados de periódicos.");
    const e = dados.envios;
    if (!e.total) { empty($("env"), "Você ainda não enviou documentos. Envie um certificado ou artigo para começar."); return; }
    $("env").replaceChildren(el("div", { class: "row" }, el("div", { class: "n" }, "Total de registros"), el("div", { class: "q" }, fmt(e.total))),
      ...Object.entries(e.por_tipo).map(([k, n]) => el("div", { class: "row" }, el("div", { class: "s" }, TIPOS[k] || k), el("div", { class: "q" }, String(n)))));
  }

  let tentativas = 0;
  const CHAVE_SNAP = "lf-abertura:" + usuario + ":";
  function mostrar() {
    const ids = [];
    if (dados.orcid) ids.push(el("span", { class: "pill" }, "ORCID " + dados.orcid));
    ids.push(el("span", { class: "pill neutral" }, "Perfil privado"));
    $("ids").replaceChildren(...ids);
    $("status").textContent = "Atualizado em " + dados.consultado_em + (dados.atualizando ? " · verificando novidades…" : "");
    const avisos = dados.avisos || [];
    if (!orcid) formOrcid("Informe seu ORCID para calcular produção e citações. Seus envios já aparecem abaixo.");
    else if (avisos.length) $("banner").replaceChildren(el("div", { class: "banner" }, avisos.join(" ")));
    else $("banner").replaceChildren();
    renderKpis(); desenhar(); renderFeed(); renderSide();
  }
  async function carregar() {
    // Última foto guardada neste navegador: a tela abre instantaneamente e a verificação segue por trás.
    if (!dados && orcid) {
      try { const snap = JSON.parse(store.get(CHAVE_SNAP + orcid) || "null"); if (snap && snap.ok) { dados = snap; dados.atualizando = true; mostrar(); } } catch (e) {}
    }
    if (!dados) $("status").textContent = "Carregando seus indicadores…";
    const qs = new URLSearchParams({ usuario });
    if (orcid) qs.set("orcid", orcid);
    let novo;
    try {
      const r = await fetch("/api/abertura?" + qs);
      if (r.status === 401) { location.href = "/login"; return; }
      novo = await r.json();
      if (!novo.ok) throw new Error(novo.error || "Falha");
    } catch (e) {
      if (!dados) $("banner").replaceChildren(el("div", { class: "banner" }, "Não foi possível carregar os indicadores agora. " + (e.message || "")));
      else { dados.atualizando = false; $("status").textContent = "Atualizado em " + dados.consultado_em + " · sem conexão para atualizar"; }
      return;
    }
    if (novo.pendente && dados && dados.producao) novo = dados; // ainda calculando: mantém o que já está na tela
    dados = novo;
    if (!dados.pendente && orcid) store.set(CHAVE_SNAP + orcid, JSON.stringify(dados));
    mostrar();
    // Servidor ainda calculando/atualizando: confere de novo em instantes.
    if ((dados.pendente || dados.atualizando) && tentativas++ < 12) setTimeout(carregar, 5000);
  }

  document.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".seg button").forEach((x) => x.classList.remove("on")); b.classList.add("on");
    janela = +b.dataset.n; if (dados) desenhar();
  }));
  carregar();
})();
