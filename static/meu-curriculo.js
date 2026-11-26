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
  let itens = [], snapshots = [], pagina = 1, grupo = '', carga = 0, snapshotAtual = '';
  const PAGE_SIZE = 6;
  const SECOES = [
    ['formacao', 'Formação', ['formacao_academica', 'formacao_complementar']],
    ['atuacao', 'Atuação', ['atuacao_profissional', 'curso_ministrado']],
    ['publicacoes', 'Publicações', ['artigo', 'artigo_aceito', 'livro', 'capitulo', 'trabalho_evento', 'texto_jornal', 'outra_producao_bibliografica']],
    ['orientacoes', 'Orientações', ['orientacao_concluida', 'orientacao_andamento']],
    ['projetos', 'Projetos', ['projeto']],
    ['patentes', 'Patentes', ['patente']],
    ['bancas', 'Bancas', ['banca']],
    ['premios', 'Prêmios', ['premio']],
  ];
  const categoriasDasSecoes = new Set(SECOES.flatMap(([, , categorias]) => categorias));

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

  function detalhesItem(item) {
    const details = el('details', { class: 'item-detail' }, el('summary', {}, 'Ver detalhes'));
    const dl = el('dl');
    [['Título', item.titulo], ['Categoria', rot(item.categoria)], ['Ano', item.ano], ['Veículo', item.veiculo], ['Instituição', item.instituicao], ['Autores', (item.autores || []).join('; ')], ['DOI', item.doi], ['ISSN', item.issn], ['ISBN', item.isbn]].forEach(([key, value]) => {
      if (value) dl.append(el('dt', {}, key), el('dd', {}, String(value)));
    });
    details.append(dl);
    return details;
  }

  function desenharLeitura(nome, resumo, data) {
    $('cvName').textContent = nome || 'Meu currículo';
    const partesDoNome = (nome || '').trim().split(/\s+/);
    const primeira = partesDoNome[0][0] || '';
    const ultima = partesDoNome.length > 1 ? partesDoNome.at(-1)[0] : '';
    $('cvInitials').textContent = (primeira + ultima).toUpperCase();
    $('cvSummary').textContent = resumo || 'Esta versão não traz um resumo.';
    $('cvUpdated').textContent = data ? 'Currículo Lattes · Atualizado em ' + data : 'Versão do Currículo Lattes';
    const outros = itens.filter(item => !categoriasDasSecoes.has(item.categoria));
    const secoes = SECOES.map(([id, titulo, categorias]) => [id, titulo, itens.filter(item => categorias.includes(item.categoria))]);
    if (outros.length) secoes.push(['outros', 'Outros registros', outros]);
    // Publicações abre primeiro na leitura. O índice mantém a ordem das seções do currículo.
    const secoesOrdenadas = [...secoes].sort(([idA], [idB]) => Number(idB === 'publicacoes') - Number(idA === 'publicacoes'));
    const links = new Map();
    const paineis = secoesOrdenadas.map(([id, titulo, registros]) => {
      const section = el('details', { id: 'cv-' + id, class: 'panel cv-section', open: id === 'publicacoes' });
      section.append(el('summary', {}, el('strong', {}, titulo), el('span', {}, registros.length)));
      const link = el('a', { href: '#' + section.id }, titulo, el('span', {}, registros.length));
      links.set(id, link);
      if (id === 'publicacoes') link.setAttribute('aria-current', 'location');
      link.addEventListener('click', event => {
        event.preventDefault();
        section.open = true;
        links.forEach(a => a.removeAttribute('aria-current'));
        link.setAttribute('aria-current', 'location');
        section.querySelector('summary').focus({ preventScroll: true });
        section.scrollIntoView({ block: 'nearest' });
      });
      const resultado = el('div');
      if (id === 'publicacoes') {
        const search = el('input', { type: 'search', placeholder: 'Título, periódico, autor ou DOI' });
        const total = el('p', { class: 'muted', hidden: true });
        total.setAttribute('role', 'status');
        section.append(el('label', { class: 'cv-search' }, 'Buscar em publicações', search), total);
        search.addEventListener('input', () => {
          const query = search.value.trim();
          const filtrados = D.filter(registros, { query });
          total.hidden = !query;
          total.textContent = filtrados.length + (filtrados.length === 1 ? ' publicação encontrada' : ' publicações encontradas');
          desenharPorAno(resultado, filtrados, Boolean(query));
        });
      }
      section.append(resultado);
      desenharPorAno(resultado, registros, false);
      if (!registros.length && resumo && (id === 'formacao' || id === 'atuacao')) {
        resultado.replaceChildren(el('p', { class: 'muted' }, 'Esta versão traz o resumo do perfil acima. Os registros detalhados desta seção não estão disponíveis.'));
      }
      return section;
    });
    $('cvIndex').replaceChildren(...secoes.map(([id]) => links.get(id)));
    $('cvSections').replaceChildren(...paineis);
    $('cvProfile').hidden = $('cvReading').hidden = $('curriculumTable').hidden = false;
  }

  function desenharPorAno(destino, registros, expandirTodos) {
    const anos = new Map();
    for (const item of registros) {
      const ano = String(item.ano || '');
      if (!anos.has(ano)) anos.set(ano, []);
      anos.get(ano).push(item);
    }
    const grupos = [...anos].sort(([a], [b]) => b.localeCompare(a, 'pt-BR', { numeric: true }));
    destino.replaceChildren(...grupos.map(([ano, items], index) => el('details', { class: 'cv-year', open: expandirTodos || index === 0 },
      el('summary', {}, el('strong', {}, ano || 'Ano não informado'), el('span', {}, items.length + (items.length === 1 ? ' registro' : ' registros'))),
      items.map(item => el('article', { class: 'cv-entry' }, el('h3', {}, item.titulo || 'Título não informado'),
        el('p', { class: 'muted' }, item.veiculo || item.instituicao || rot(item.categoria)), detalhesItem(item))))));
    if (!registros.length) destino.append(el('p', { class: 'empty' }, 'Nenhum registro disponível nesta seção.'));
  }

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
      const details = detalhesItem(i);
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
    carga++;
    snapshotAtual = '';
    itens = []; $('secDash').hidden = $('secItens').hidden = $('secComp').hidden = true;
    $('cvProfile').hidden = $('cvReading').hidden = $('curriculumTable').hidden = true;
    if ($('bDiagIA')) $('bDiagIA').hidden = true;
    if ($('secDiagnosticoIA')) $('secDiagnosticoIA').hidden = true;
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
    snapshotAtual = snap;
    if ($('bDiagIA')) $('bDiagIA').hidden = false;
    if ($('secDiagnosticoIA')) $('secDiagnosticoIA').hidden = true;
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
    desenharLeitura(it.nome, it.perfil?.resumo || d.perfil?.resumo, dt || it.atualizacao_iso?.slice(0, 10).split('-').reverse().join('/'));
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
    try { await json("/api/curriculo/snapshots/" + encodeURIComponent(id), { method: "DELETE" }); status("Versão apagada.", false); UI.storage.set('lf-cv-selection:' + UI.owner, ''); limparCurriculo(); await carregarTudo(await listarVersoes()); }
    catch (e) { status(e.message, true); }
  };
  ['fCat','fAno','fSituacao'].forEach(id => $(id).addEventListener('change', () => { pagina = 1; desenharItens(); }));
  $('fBusca').addEventListener('input', () => { pagina = 1; desenharItens(); });
  $('prevItems').addEventListener('click', () => { pagina--; desenharItens(); });
  $('nextItems').addEventListener('click', () => { pagina++; desenharItens(); });
  function renderizarDiagnosticoIA(res) {
    const sec = $('secDiagnosticoIA');
    const body = $('iaDiagBody');
    const meta = $('iaDiagMeta');
    const av = res.avaliacao || {};
    const u = res.usage || {};
    const cacheTxt = res.cached ? ' · resultado em cache ($0)' : ` · custo acumulado da sessão: ~$${Number(u.estimated_usd || 0).toFixed(4)}`;
    meta.textContent = `Modelo: ${res.model || 'Gemini'} · ${res.total_itens_analisados || 0} de ${res.total_itens_curriculo || 0} itens analisados${cacheTxt}`;

    const blocos = [];
    blocos.push(el('div', { class: 'cv-ai-score' }, `Nota geral de organização Lattes/CAPES: ${av.nota_geral ?? '—'}/100`));
    if (av.resumo_executivo) blocos.push(el('p', {}, av.resumo_executivo));

    if ((av.pontos_fortes || []).length) {
      blocos.push(el('div', { class: 'cv-ai-block' },
        el('h3', {}, 'Pontos fortes da trajetória'),
        el('ul', { class: 'cv-ai-list' }, av.pontos_fortes.map(p => el('li', {}, p)))));
    }

    const errados = av.itens_secao_errada || [];
    blocos.push(el('div', { class: 'cv-ai-block' },
      el('h3', {}, `Itens possivelmente na seção errada (${errados.length})`),
      errados.length
        ? tabela(['Item', 'Seção atual', 'Sugestão Lattes', 'Motivo'], errados.map(x => [x.titulo, rot(x.secao_atual), rot(x.secao_sugerida), x.motivo]))
        : el('p', { class: 'muted' }, 'Nenhum item com suspeita de seção incorreta encontrado.')));

    const dups = av.duplicatas_semanticas || [];
    if (dups.length) {
      blocos.push(el('div', { class: 'cv-ai-block' },
        el('h3', {}, `Possíveis duplicatas semânticas (${dups.length})`),
        el('ul', { class: 'cv-ai-list' }, dups.map(d => el('li', {}, el('strong', {}, d.item_a), ' ↔ ', el('strong', {}, d.item_b), ' — ', d.motivo)))));
    }

    const lacunas = av.lacunas_estrategicas || [];
    if (lacunas.length) {
      blocos.push(el('div', { class: 'cv-ai-block' },
        el('h3', {}, 'Lacunas e prioridades estratégicas'),
        el('ul', { class: 'cv-ai-list' }, lacunas.map(l => el('li', {},
          el('span', { class: 'cv-ai-prio ' + (l.prioridade || 'media') }, l.prioridade || 'média'),
          el('strong', {}, l.tema + ': '),
          l.acao)))));
    }

    if (av.sugestao_texto_inicial) {
      const ta = el('textarea', { class: 'cv-ai-textarea', readOnly: true, value: av.sugestao_texto_inicial });
      const btnCopiar = el('button', { class: 'button', type: 'button', style: 'margin-top:6px' }, '📋 Copiar sugestão de resumo inicial');
      btnCopiar.onclick = async () => {
        try { await navigator.clipboard.writeText(av.sugestao_texto_inicial); btnCopiar.textContent = '✅ Copiado!'; setTimeout(() => { btnCopiar.textContent = '📋 Copiar sugestão de resumo inicial'; }, 2000); }
        catch (_) { status('Não foi possível copiar automaticamente; selecione e copie o texto acima.', true); }
      };
      blocos.push(el('div', { class: 'cv-ai-block' },
        el('h3', {}, 'Sugestão de Texto Inicial para o Lattes (padrão CNPq)'),
        el('p', { class: 'muted' }, 'Revise antes de colar em Dados gerais › Texto inicial do currículo:'),
        ta,
        btnCopiar));
    }

    body.replaceChildren(...blocos);
    sec.hidden = false;
    sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function executarDiagnosticoIA(force) {
    if (!snapshotAtual) return status('Importe ou selecione uma versão do currículo primeiro.', true);
    const btn = $('bDiagIA');
    const btnRef = $('bDiagIARefazer');
    if (btn) btn.disabled = true;
    if (btnRef) btnRef.disabled = true;
    status('Consultando Gemini para diagnóstico qualitativo do currículo…', false);
    try {
      const res = await json('/api/ia/avaliar-curriculo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ snapshot: snapshotAtual, force: !!force }),
      });
      renderizarDiagnosticoIA(res);
      status(res.cached ? 'Diagnóstico carregado do cache local ($0).' : 'Diagnóstico IA concluído.', false);
    } catch (e) {
      status(e.message, true);
    } finally {
      if (btn) btn.disabled = false;
      if (btnRef) btnRef.disabled = false;
    }
  }

  if ($('bDiagIA')) $('bDiagIA').onclick = () => executarDiagnosticoIA(false);
  if ($('bDiagIARefazer')) $('bDiagIARefazer').onclick = () => executarDiagnosticoIA(true);
  if ($('bDiagIAFechar')) $('bDiagIAFechar').onclick = () => { $('secDiagnosticoIA').hidden = true; };

  function revealHash() {
    if (location.hash === '#importar') $('importar').open = true;
    if (location.hash === '#coautorias') { $('curriculumAnalysis').open = true; if (!$('secDash').hidden) $('tCoa').scrollIntoView({ block: 'center' }); }
  }
  document.querySelectorAll('a[href="#importar"]').forEach(a => a.addEventListener('click', () => { $('importar').open = true; }));
  window.addEventListener('hashchange', revealHash); revealHash();
  if (UI.owner) listarVersoes().then(id => carregarTudo(id)).then(revealHash).catch(e => status(e.message, true));
  else status('Selecione seu perfil na tela de login para consultar seu currículo.', true);
})();
