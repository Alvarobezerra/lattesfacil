"use strict";
(function () {
  const $ = (id) => document.getElementById(id);
  const NS = "http://www.w3.org/2000/svg";
  const ROTULO = {
    artigo: "Artigos publicados", artigo_aceito: "Artigos aceitos", trabalho_evento: "Trabalhos em eventos", apresentacao: "Apresentações de trabalho",
    livro: "Livros", capitulo: "Capítulos de livro", texto_jornal: "Textos em jornal/revista", curso_ministrado: "Cursos ministrados",
    formacao_complementar: "Formação complementar", patente: "Patentes", software: "Softwares", trabalho_tecnico: "Trabalhos técnicos",
    produto_tecnologico: "Produtos/processos", banca: "Bancas", orientacao_concluida: "Orientações concluídas", orientacao_andamento: "Orientações em andamento",
    projeto: "Projetos", participacao_evento: "Participação em eventos", organizacao_evento: "Organização de eventos", premio: "Prêmios e títulos",
    atuacao_profissional: "Atuação profissional", formacao_academica: "Formação acadêmica", outra_producao_bibliografica: "Outra produção bibliográfica",
    outra_producao_tecnica: "Outra produção técnica", producao_artistica: "Produção artística/cultural",
    registro_propriedade: "Marcas, cultivares e desenhos", demais_trabalhos: "Demais trabalhos",
  };
  const rot = (c) => ROTULO[c] || c;
  const UI = window.LattesUI, D = window.CurriculumData;
  let itens = [], snapshots = [], pagina = 1, grupo = '', carga = 0;
  const PAGE_SIZE = 6;

  // texto sempre via textContent: nada vindo do XML entra como HTML
  function el(tag, props, ...filhos) {
    const e = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => (k === "class" ? (e.className = v) : (e[k] = v)));
    filhos.flat().forEach((f) => e.append(f instanceof Node ? f : document.createTextNode(f == null ? "" : String(f))));
    return e;
  }
  function tabela(cab, linhas) {
    const t = el("table", { class: "tab" }, el("thead", {}, el("tr", {}, cab.map((c) => el("th", {}, c)))));
    t.append(el("tbody", {}, linhas.map((l) => el("tr", {}, l.map((c) => el("td", {}, c))))));
    return t;
  }
  function status(texto, erro) { const s = $("sStatus"); s.textContent = texto; s.className = erro ? "erro" : "ok"; }
  async function json(url, opts) {
    const r = await fetch(url, opts);
    if (r.status === 401) { location.assign('/login'); throw new Error('Sessão expirada.'); }
    let d = {};
    try { d = await r.json(); } catch (e) { /* corpo não-JSON */ }
    if (!r.ok) { const e = new Error(d.error || "Falha (" + r.status + ")"); e.dados = d; throw e; }
    return d;
  }
  const dataHora = (iso) => { const d = new Date(iso); return isNaN(d) ? "" : d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }); };

  function grafico(anos) {
    if (!anos.length) return el("p", { class: "dica" }, "Sem itens com ano.");
    const W = 760, H = 220, base = 190, esq = 28, max = Math.max(...anos.map((a) => a.total), 1);
    const larg = Math.min(34, (W - esq) / anos.length);
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("class", "graf"); svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Itens do currículo por ano");
    const add = (nome, attrs, txt) => { const n = document.createElementNS(NS, nome); Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v)); if (txt != null) n.textContent = txt; svg.append(n); return n; };
    add("text", { x: 0, y: 14 }, String(max));
    anos.forEach((a, i) => {
      const x = esq + i * larg, h = (a.total / max) * (base - 20), hp = (a.producao / max) * (base - 20);
      const r = add("rect", { x: x + 2, y: base - h, width: Math.max(larg - 4, 2), height: h });
      const t = document.createElementNS(NS, "title"); t.textContent = a.ano + ": " + a.total + " itens (" + a.producao + " de produção)"; r.append(t);
      add("rect", { x: x + 2, y: base - hp, width: Math.max(larg - 4, 2), height: hp, class: "prod" });
      if (anos.length <= 24 || i % 2 === 0) add("text", { x: x + larg / 2, y: base + 14, "text-anchor": "middle" }, String(a.ano).slice(-2));
    });
    return svg;
  }

  function desenharItens() {
    const lista = D.filter(itens, { category: $('fCat').value, query: $('fBusca').value, year: $('fAno').value, situation: $('fSituacao').value, selectedGroup: grupo });
    const pages = Math.max(1, Math.ceil(lista.length / PAGE_SIZE)); pagina = Math.max(1, Math.min(pagina, pages));
    const start = (pagina - 1) * PAGE_SIZE, shown = lista.slice(start, start + PAGE_SIZE);
    $('nItens').textContent = lista.length ? `${start + 1}–${start + shown.length} de ${lista.length} registros (${itens.length} na versão)` : 'Nenhum registro corresponde aos filtros.';
    $('pageItems').textContent = `${pagina} / ${pages}`; $('prevItems').disabled = pagina === 1; $('nextItems').disabled = pagina === pages;
    const rows = shown.map(i => {
      const details = el('details', { class: 'item-detail' }, el('summary', {}, 'Ver detalhes'));
      const dl = el('dl');
      [['Título', i.titulo], ['Categoria', rot(i.categoria)], ['Ano', i.ano], ['Veículo', i.veiculo], ['Instituição', i.instituicao], ['Autores', (i.autores || []).join('; ')], ['DOI', i.doi], ['ISSN', i.issn], ['ISBN', i.isbn]].forEach(([key, value]) => {
        if (value) dl.append(el('dt', {}, key), el('dd', {}, String(value)));
      });
      details.append(dl);
      const title = el('div', {}, el('strong', {}, i.titulo || 'Título não informado'), el('div', { class: 'record-subtitle' }, i.veiculo || rot(i.categoria)));
      const situation = D.needsAttention(i) ? el('span', { class: 'badge warning' }, 'DOI não informado') : el('span', { class: 'badge' }, 'Na versão importada');
      return [title, rot(i.categoria), i.ano || '—', situation, details];
    });
    $('tItens').replaceChildren(lista.length ? tabela(['Registro', 'Tipo', 'Ano', 'Situação', 'Ação'], rows) : el('p', { class: 'empty' }, 'Experimente outra busca ou categoria.'));
    $('categoryTabs').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.group === grupo)));
  }

  function desenharGrupos() {
    const groups = [['', 'Todos'], ['producoes', 'Produções'], ['orientacoes', 'Orientações'], ['projetos', 'Projetos'], ['outros', 'Outros registros']];
    $('categoryTabs').replaceChildren(...groups.map(([id, label]) => {
      const count = id ? itens.filter(i => D.group(i) === id).length : itens.length;
      const b = el('button', { type: 'button' }, `${label} (${count})`); b.dataset.group = id; b.setAttribute('aria-pressed', String(grupo === id));
      b.addEventListener('click', () => { grupo = id; pagina = 1; $('fCat').value = ''; desenharItens(); }); return b;
    }));
  }

  function limparCurriculo() {
    itens = []; $('secDash').hidden = $('secItens').hidden = $('secComp').hidden = true;
    $('curriculumEmpty').hidden = false; $('snapshotLabel').textContent = 'Nenhuma versão selecionada';
  }

  function mostrarComparacao(c) {
    const caixa = $("rComp");
    const bloco = (titulo, lista, cls) => el("div", {}, el("h3", { style: "margin:8px 0 4px;font-size:1rem", class: cls }, titulo + " (" + lista.length + ")"),
      lista.length ? tabela(["Categoria", "Título", "Ano"], lista.map((i) => [rot(i.categoria), i.titulo || i.doi, i.ano || ""])) : el("p", { class: "dica" }, "Nenhum."));
    caixa.replaceChildren(el("p", { class: "dica" }, "Total: " + c.total_antes + " → " + c.total_depois + ". Um título editado no Lattes aparece como saiu + entrou."),
      bloco("Entraram", c.adicionados, "mais"), bloco("Saíram", c.removidos, "menos"));
    $("secComp").hidden = false;
  }

  async function carregarTudo(snap) {
    if (!snap) { limparCurriculo(); return; }
    const ticket = ++carga;
    const q = "?snapshot=" + encodeURIComponent(snap);
    const [d, it] = await Promise.all([json('/api/curriculo/dashboard' + q), json('/api/curriculo' + q)]);
    if (ticket !== carga) return;
    if (!UI.sameOwner(d.nome) || !UI.sameOwner(it.nome)) { limparCurriculo(); throw new Error('Esta versão pertence a outro perfil. Entre com o pesquisador correspondente para consultá-la.'); }
    UI.storage.set('lf-cv-selection:' + UI.owner, snap);
    $('curriculumEmpty').hidden = true;
    $("secDash").hidden = false; $("secItens").hidden = false;
    const version = snapshots.find(s => s.id === snap);
    $('snapshotLabel').textContent = `${d.fonte === 'pagina' ? 'Leitura do Lattes' : 'Currículo importado'}${version ? ' · Versão guardada em ' + dataHora(version.carregado_em) : ''}`;
    $("tNome").textContent = d.nome || "Currículo";
    const dt = (d.atualizacao || "").replace(/^(\d{2})(\d{2})(\d{4})$/, "$1/$2/$3");
    $("tMeta").textContent = "Lattes " + (d.id_lattes || "—") + " · " + (d.fonte === "pagina" ? "leitura ao vivo (currículo de " + (dt || "—") + ")" : "XML exportado, atualizado em " + (dt || "—")) +
      (d.perfil && d.perfil.areas && d.perfil.areas.length ? " · áreas: " + d.perfil.areas.slice(0, 4).join("; ") : "");
    const k = (n, t) => el("div", { class: "kpi" }, el("b", {}, n), el("span", {}, t));
    $("kpis").replaceChildren(k(d.total_itens, "itens no total"), k(d.ultimos_5_anos, "nos últimos 5 anos"), k(d.artigos.total, "artigos publicados"),
      k(d.artigos.sem_doi, "artigos sem DOI"), k(d.orientacoes.concluidas + d.orientacoes.em_andamento, "orientações"), k(d.bancas, "bancas"));
    const nc = Object.entries(d.nao_classificados || {});
    $("avisoNaoClass").replaceChildren(nc.length ? el("p", { class: "aviso" }, "O XML traz itens que o NautiScience ainda não classifica: " +
      nc.map(([t, n]) => t + " (" + n + ")").join(", ") + ". Eles não entram nos totais.") : "");
    $("grafAno").replaceChildren(grafico(d.por_ano));
    $("tCat").replaceChildren(tabela(["Categoria", "Itens"], Object.entries(d.por_categoria).map(([c, n]) => [rot(c), n])));
    $("tPer").replaceChildren(d.periodicos_top.length ? tabela(["Periódico", "Artigos"], d.periodicos_top) : el("p", { class: "dica" }, "—"));
    $("tCoa").replaceChildren(d.coautores_top.length ? tabela(["Coautor", "Itens"], d.coautores_top) : el("p", { class: "dica" }, "—"));
    itens = it.itens;
    const cats = [...new Set(itens.map((i) => i.categoria))].sort((a, b) => rot(a).localeCompare(rot(b)));
    $("fCat").replaceChildren(el("option", { value: "" }, "Todas as categorias"), cats.map((c) => el("option", { value: c }, rot(c))));
    $('fAno').replaceChildren(el('option', { value: '' }, 'Todos os anos'), [...new Set(itens.map(i => String(i.ano || '')).filter(Boolean))].sort().reverse().map(year => el('option', { value: year }, year)));
    pagina = 1; desenharGrupos(); desenharItens();
    try { const comparison = await json('/api/curriculo/comparar?para=' + encodeURIComponent(d.snapshot_id)); if (ticket === carga) mostrarComparacao(comparison); } catch (e) { if (ticket === carga) $('secComp').hidden = true; }
  }

  async function listarVersoes(escolher) {
    const data = await json("/api/curriculo/snapshots");
    snapshots = data.snapshots.filter(s => UI.sameOwner(s.nome));
    const sel = $("selVersao");
    sel.replaceChildren(el("option", { value: "" }, snapshots.length ? "Escolha uma versão guardada…" : "Nenhuma versão guardada"),
      ...snapshots.map((s) => el("option", { value: s.id }, (s.nome || s.id_lattes) + " — " + (s.fonte === "pagina" ? "lido ao vivo" : "XML") + " em " + dataHora(s.carregado_em) + " (" + s.total + " itens)")));
    const saved = escolher || UI.storage.get('lf-cv-selection:' + UI.owner);
    sel.value = snapshots.some(s => s.id === saved) ? saved : snapshots[0]?.id || '';
    $('bExcluir').disabled = !sel.value;
    return sel.value;
  }

  // Leitura em tempo real: a extensão busca a página do Lattes logado e devolve o HTML; o servidor interpreta e guarda uma versão.
  let extensaoAtiva = false;
  function resumoCarga(d) {
    const partes = [d.novo_snapshot ? "Nova versão guardada." : "Nada mudou desde a última leitura."];
    if (d.comparacao) partes.push("Desde a versão anterior: +" + d.comparacao.adicionados + " / −" + d.comparacao.removidos + " itens.");
    const e = d.envios_conciliados || {}, n = Object.values(e).reduce((a, b) => a + b, 0);
    if (n) partes.push("Envios conferidos: " + Object.entries(e).map(([k, v]) => v + " " + k.replace(/_/g, " ")).join(", ") + ".");
    return partes.join(" ");
  }
  window.addEventListener("message", async (ev) => {
    if (ev.source !== window || ev.origin !== location.origin || !ev.data) return;
    const m = ev.data;
    if (m.type === "lattesdata-ext-pong") extensaoAtiva = true;
    else if (m.type === "lattesdata-ext-result" && m.evento === "leitura") status(m.message || "", !["lendo", "ok"].includes(m.estado));
    else if (m.type === "lattesdata-ext-live") {
      if (!m.ok) return status("Não consegui ler o Lattes: " + (m.erro || "erro desconhecido"), true);
      try {
        status("Interpretando a página recebida…", false);
        const d = await json("/api/curriculo/pagina", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ html: m.html, nome: m.nome }) });
        status(resumoCarga(d), false);
        await listarVersoes(d.snapshot_id); await carregarTudo(d.snapshot_id);
      } catch (e) { status(e.message, true); }
    }
  });
  $("bAoVivo").onclick = () => {
    if (!extensaoAtiva) return status("A extensão NautiScience não respondeu. Instale ou atualize (versão 0.7.0 ou mais nova) e recarregue esta página.", true);
    status("Pedindo ao Lattes…", false);
    window.postMessage({ type: "lattesdata-ext-cv-live" }, location.origin);
  };
  window.postMessage({ type: "lattesdata-ext-ping" }, location.origin);

  $("bXml").onclick = async () => {
    const arq = $("fXml").files[0];
    if (!arq) return status("Escolha o arquivo XML ou ZIP.", true);
    const f = new FormData(); f.append("arquivo", arq);
    try {
      const d = await json("/api/lattes-xml", { method: "POST", body: f });
      const partes = [d.novo_snapshot ? "Nova versão guardada." : "Este XML já estava guardado (nada mudou)."];
      if (d.comparacao) partes.push("Desde a versão anterior: +" + d.comparacao.adicionados + " / −" + d.comparacao.removidos + " itens.");
      const e = d.envios_conciliados || {}, n = Object.values(e).reduce((a, b) => a + b, 0);
      if (n) partes.push("Envios conferidos pelo XML: " + Object.entries(e).map(([k, v]) => v + " " + k.replace(/_/g, " ")).join(", ") + ".");
      status(partes.join(" "), false);
      await listarVersoes(d.snapshot_id); await carregarTudo(d.snapshot_id);
    } catch (e) { status(e.message, true); }
  };
  $("selVersao").onchange = async () => {
    const id = $("selVersao").value; if (!id) return;
    try { await json("/api/curriculo/ativar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ snapshot: id }) }); await carregarTudo(id); status("", false); }
    catch (e) { status(e.message, true); }
  };
  $("bExcluir").onclick = async () => {
    const id = $("selVersao").value; if (!id) return status("Escolha a versão que quer apagar.", true);
    if (!window.confirm("Apagar esta versão guardada? Isso não afeta o seu currículo no Lattes.")) return;
    try { await json("/api/curriculo/snapshots/" + encodeURIComponent(id), { method: "DELETE" }); status("Versão apagada.", false); ++carga; UI.storage.set('lf-cv-selection:' + UI.owner, ''); limparCurriculo(); await carregarTudo(await listarVersoes()); }
    catch (e) { status(e.message, true); }
  };
  ['fCat','fAno','fSituacao'].forEach(id => $(id).addEventListener('change', () => { pagina = 1; desenharItens(); }));
  $('fBusca').addEventListener('input', () => { pagina = 1; desenharItens(); });
  $('prevItems').addEventListener('click', () => { pagina--; desenharItens(); });
  $('nextItems').addEventListener('click', () => { pagina++; desenharItens(); });
  function revealHash() {
    if (location.hash === '#importar') $('importar').open = true;
    if (location.hash === '#coautorias') { $('curriculumAnalysis').open = true; if (!$('secDash').hidden) $('tCoa').scrollIntoView({ block: 'center' }); }
  }
  document.querySelectorAll('a[href="#importar"]').forEach(a => a.addEventListener('click', () => { $('importar').open = true; }));
  window.addEventListener('hashchange', revealHash); revealHash();
  if (UI.owner) listarVersoes().then(id => carregarTudo(id)).then(revealHash).catch(e => status(e.message, true));
  else status('Selecione seu perfil na tela de login para consultar seu currículo.', true);
})();
