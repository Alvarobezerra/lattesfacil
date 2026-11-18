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
  const PUBLIC_PROFILES = {
    "Álvaro Antônio Bezerra dos Santos": {
      id: "0174461068626535", atualizado: "17/11/2026",
      resumo: "Farmacêutico, perito criminal e estudante de Direito, com experiência em farmácia hospitalar, segurança de medicamentos, assistência farmacêutica e saúde pública.",
      areas: ["Farmácia hospitalar", "Farmácia clínica", "Perícia criminal", "Saúde pública"],
      destaques: ["Perito criminal", "Farmacêutico hospitalar", "Programa de computador registrado"]
    },
    "Aramys Silva dos Reis": {
      id: "1040580590566490", atualizado: "23/08/2026",
      resumo: "Professor Associado da UFMA, doutor em Ciências pela USP, coordenador de pesquisas em saúde, inovação e produtos naturais, com atuação em orientação e divulgação científica.",
      areas: ["Pesquisa em saúde", "Produtos naturais", "Inovação", "Orientação", "Divulgação científica"],
      destaques: ["Professor Associado I", "Coordenador do PPGST", "Patentes e projetos de inovação"]
    }
  };
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

  function proximoPasso() {
    const title = $("nextTitle"), text = $("nextText"), action = $("nextAction"), icon = document.querySelector("#nextStep .ns-icon");
    if (!title || !text || !action) return;
    let cfg = { icon: "→", title: "Envie seu primeiro documento", text: "Comece por um artigo, certificado ou resumo em PDF.", label: "Enviar documento", href: "/" };
    if (!orcid) cfg = { icon: "◎", title: "Conecte seu ORCID", text: "Assim calculamos sua produção e mostramos quem cita você.", label: "Informar ORCID", href: "#ids" };
    else if (!dados) cfg = { icon: "…", title: "Preparando seu painel", text: "Estamos verificando seus dados e seus documentos.", label: "Aguarde", href: "#nextStep" };
    else if (dados.pendente || dados.atualizando) cfg = { icon: "↻", title: "Atualizando seus indicadores", text: "Você já pode explorar o painel enquanto verificamos novidades.", label: "Ver currículo", href: "/meu-curriculo.html" };
    else if (dados.envios && dados.envios.total) cfg = { icon: "✓", title: "Continue mantendo seu Lattes em dia", text: `${fmt(dados.envios.total)} documento${dados.envios.total === 1 ? " já foi" : "s já foram"} registrado${dados.envios.total === 1 ? "" : "s"}.`, label: "Enviar outro", href: "/" };
    title.textContent = cfg.title; text.textContent = cfg.text; action.textContent = cfg.label; action.href = cfg.href;
    if (icon) icon.textContent = cfg.icon;
  }

  function renderMomento() {
    const box = $("moment");
    if (!box) return;
    if (!dados) {
      box.replaceChildren(el("article", { class: "card moment-main" }, el("div", { class: "eyebrow" }, "Seu momento"), el("h2", {}, "Sua trajetória começa pelo que você já construiu."), el("p", {}, "Assim que os dados forem carregados, vamos transformar seus registros em uma visão clara da sua jornada.")));
      return;
    }
    const p = dados.producao || {}, c = dados.citacoes || {}, e = dados.envios || {};
    const total = Number(p.total || 0), ano = Number(p.no_ano || 0), cit = Number(c.total || 0);
    let frase = total ? `Você já tem ${fmt(total)} ${total === 1 ? "produção registrada" : "produções registradas"} para contar sua trajetória.` : "Sua trajetória está pronta para começar a ser organizada.";
    if (ano) frase += ` Neste ano, ${fmt(ano)} ${ano === 1 ? "item já apareceu" : "itens já apareceram"} no seu percurso.`;
    box.replaceChildren(
      el("article", { class: "card moment-main" }, el("div", { class: "eyebrow" }, "Seu momento"), el("h2", {}, "O que você construiu importa."), el("p", {}, frase)),
      el("article", { class: "card moment-stat" }, el("div", { class: "ms-label" }, "Produção"), el("div", { class: "ms-value" }, fmt(total)), el("div", { class: "ms-help" }, "obras encontradas")),
      el("article", { class: "card moment-stat" }, el("div", { class: "ms-label" }, "Citações"), el("div", { class: "ms-value" }, fmt(cit)), el("div", { class: "ms-help" }, "impacto acompanhado")),
      el("article", { class: "card moment-stat" }, el("div", { class: "ms-label" }, "Registros"), el("div", { class: "ms-value" }, fmt(e.total || 0)), el("div", { class: "ms-help" }, "no LattesData")),
    );
  }

  function mostrarPerfilPublico() {
    const p = PUBLIC_PROFILES[usuario], box = $("latProfile");
    if (!p || !box) return;
    box.hidden = false;
    $("latMeta").textContent = `Lattes ${p.id} · perfil público · atualizado em ${p.atualizado}`;
    $("latSummary").textContent = p.resumo;
    $("latAreas").replaceChildren(...p.areas.map((a) => el("span", { class: "lat-area" }, a)));
    $("latK").replaceChildren(...p.destaques.map((d) => el("div", { class: "profile-highlight" }, "✓ ", d)));
    $("latGraf").replaceChildren();
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
    proximoPasso(); renderMomento();
  }
  async function carregar() {
    // Última foto guardada neste navegador: a tela abre instantaneamente e a verificação segue por trás.
    if (!dados && orcid) {
      try { const snap = JSON.parse(store.get(CHAVE_SNAP + orcid) || "null"); if (snap && snap.ok) { dados = snap; dados.atualizando = true; mostrar(); } } catch (e) {}
    }
    if (!dados) { $("status").textContent = "Carregando seus indicadores…"; proximoPasso(); renderMomento(); }
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

  // ---- Seu Lattes: dashboard do currículo já importado (XML ou leitura ao vivo), para mostrar o acesso aos dados.
  const ROT = { artigo: "Artigos publicados", artigo_aceito: "Artigos aceitos", trabalho_evento: "Trabalhos em eventos", apresentacao: "Apresentações",
    livro: "Livros", capitulo: "Capítulos de livro", texto_jornal: "Textos em jornal/revista", curso_ministrado: "Cursos ministrados",
    formacao_complementar: "Formação complementar", patente: "Patentes", software: "Softwares", trabalho_tecnico: "Trabalhos técnicos",
    produto_tecnologico: "Produtos/processos", banca: "Bancas", orientacao_concluida: "Orientações concluídas", orientacao_andamento: "Orientações em andamento",
    projeto: "Projetos", participacao_evento: "Participação em eventos", organizacao_evento: "Organização de eventos", premio: "Prêmios e títulos",
    atuacao_profissional: "Atuação profissional", formacao_academica: "Formação acadêmica", outra_producao_bibliografica: "Outra produção bibliográfica",
    outra_producao_tecnica: "Outra produção técnica", producao_artistica: "Produção artística/cultural", registro_propriedade: "Marcas, cultivares e desenhos",
    demais_trabalhos: "Demais trabalhos" };
  const norm = (t) => (t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().split(/\s+/).filter(Boolean);
  const CHAVE_LAT = "lf-lattes:" + usuario;

  function desenharLattes(d) {
    $("latMeta").textContent = "Lattes " + (d.id_lattes || "—") + " · " + (d.fonte === "pagina" ? "leitura ao vivo" : "XML exportado") +
      (d.atualizacao ? " · atualizado em " + d.atualizacao.replace(/^(\d{2})(\d{2})(\d{4})$/, "$1/$2/$3") : "");
    const k = (n, t) => el("div", {}, el("b", {}, fmt(n)), t);
    const perfil = d.perfil || {};
    const resumo = String(perfil.resumo || "").trim();
    const profileBox = $("latProfile");
    if (profileBox) {
      if (resumo || (perfil.areas || []).length) {
        profileBox.hidden = false;
        $("latSummary").textContent = resumo ? (resumo.length > 520 ? resumo.slice(0, 517).replace(/\s+\S*$/, "") + "…" : resumo) : "Seu currículo já foi importado. Explore as áreas e os registros que compõem sua trajetória.";
        $("latAreas").replaceChildren(...(perfil.areas || []).slice(0, 8).map((a) => el("span", { class: "lat-area" }, a)));
      } else profileBox.hidden = true;
    }
    $("latK").replaceChildren(k(d.total_itens, "itens no Lattes"), k(d.ultimos_5_anos, "nos últimos 5 anos"), k(d.artigos.total, "artigos"),
      k(d.artigos.sem_doi, "artigos sem DOI"), k(d.orientacoes.concluidas + d.orientacoes.em_andamento, "orientações"), k(d.bancas, "bancas"));
    const anos = (d.por_ano || []).slice(-15), svg = $("latGraf");
    svg.replaceChildren();
    const add = (nome, attrs, txt) => { const n = document.createElementNS(NS, nome); Object.entries(attrs).forEach(([a, v]) => n.setAttribute(a, v)); if (txt != null) n.textContent = txt; svg.append(n); return n; };
    if (anos.length) {
      const W = 700, base = 130, max = Math.max(...anos.map((a) => a.total), 1), larg = W / anos.length;
      anos.forEach((a, i) => {
        const h = (a.total / max) * 105, hp = (a.producao / max) * 105, x = i * larg;
        const r = add("rect", { x: x + 3, y: base - h, width: Math.max(larg - 6, 2), height: h, opacity: ".35" });
        r.append(Object.assign(document.createElementNS(NS, "title"), { textContent: a.ano + ": " + a.total + " itens (" + a.producao + " de produção)" }));
        add("rect", { x: x + 3, y: base - hp, width: Math.max(larg - 6, 2), height: hp, class: "p" });
        add("text", { x: x + larg / 2, y: base + 14, "text-anchor": "middle" }, String(a.ano).slice(-2));
      });
    }
    const cats = Object.entries(d.por_categoria || {}).slice(0, 6);
    $("latCat").replaceChildren(...cats.map(([c, n]) => el("div", { class: "row" }, el("div", { class: "s" }, ROT[c] || c), el("div", { class: "q" }, fmt(n)))));
  }

  async function carregarLattes() {
    mostrarPerfilPublico();
    try { const snap = JSON.parse(store.get(CHAVE_LAT) || "null"); if (snap) desenharLattes(snap); } catch (e) {}
    try {
      let sid = "";
      try {
        const { snapshots } = await (await fetch("/api/curriculo/snapshots")).json();
        const meu = norm(usuario);
        const achou = (snapshots || []).find((s) => { const n = norm(s.nome); return n.length && meu.length && n[0] === meu[0] && n[n.length - 1] === meu[meu.length - 1]; });
        sid = achou ? achou.id : "";
      } catch (e) {}
      const r = await fetch("/api/curriculo/dashboard" + (sid ? "?snapshot=" + encodeURIComponent(sid) : ""));
      if (!r.ok) {
        if (!store.get(CHAVE_LAT)) {
          $("latMeta").replaceChildren("Ainda não há currículo Lattes importado. ", el("a", { href: "/meu-curriculo.html" }, "Importe seu XML ou leia ao vivo"), " para ver sua produção e registros aqui.");
          $("latK").replaceChildren(); $("latGraf").replaceChildren(); $("latCat").replaceChildren();
          const ns = $("nextStep"); if (ns && orcid) { $("nextTitle").textContent = "Importe seu currículo Lattes"; $("nextText").textContent = "Veja sua produção completa, pendências e evolução por categoria."; $("nextAction").textContent = "Importar currículo"; $("nextAction").href = "/meu-curriculo.html"; }
        }
        return;
      }
      const d = await r.json();
      store.set(CHAVE_LAT, JSON.stringify(d));
      desenharLattes(d);
    } catch (e) {}
  }

  document.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".seg button").forEach((x) => x.classList.remove("on")); b.classList.add("on");
    janela = +b.dataset.n; if (dados) desenhar();
  }));
  carregar();
  carregarLattes();
})();
