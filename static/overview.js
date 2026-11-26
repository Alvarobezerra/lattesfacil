/* Visão geral: atividade persistida e trajetória da versão do próprio pesquisador. */
(() => {
  const $ = id => document.getElementById(id);
  const { owner, sameOwner, json } = window.LattesUI;
  const D = window.CurriculumData;
  const fmt = n => Number(n).toLocaleString('pt-BR');
  const date = value => { const d = new Date(value); return Number.isNaN(+d) ? 'Data não informada' : d.toLocaleDateString('pt-BR'); };
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const empty = (id, message) => $(id).replaceChildren(el('p', 'empty', message));
  const link = (text, href) => { const a = el('a', '', text); a.href = href; return a; };
  function notice(id, text) { $(id).replaceChildren(el('p', 'notice error', text)); }
  const tabs = [$('tabRotina'), $('tabTrajetoria')];
  function showTab(focus = false) {
    const active = location.hash === '#trajetoria' ? 1 : 0;
    tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(active === i)); tab.tabIndex = active === i ? 0 : -1; $(tab.getAttribute('aria-controls')).hidden = active !== i; });
    if (focus) tabs[active].focus();
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => { history.replaceState(null, '', i ? '#trajetoria' : '#rotina'); showTab(); });
    tab.addEventListener('keydown', e => { if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return; e.preventDefault(); const n = e.key === 'Home' ? 0 : e.key === 'End' ? 1 : 1 - i; history.replaceState(null, '', n ? '#trajetoria' : '#rotina'); showTab(true); });
  });
  window.addEventListener('hashchange', () => showTab()); showTab();

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const arrival = new URL(location.href);
  if (arrival.searchParams.get('entrada') === '1') {
    arrival.searchParams.delete('entrada');
    history.replaceState(history.state, '', arrival);
    if (!reduced.matches) showArrival();
  }

  function showArrival() {
    const dialog = el('dialog', 'arrival-dialog');
    dialog.setAttribute('aria-labelledby', 'arrivalTitle');
    const clip = el('video');
    clip.muted = true;
    clip.playsInline = true;
    const clipStart = 2;
    const duration = 2.6;
    clip.src = '/media/boas-vindas.mp4#t=2,4.6';
    clip.setAttribute('aria-hidden', 'true');
    const title = el('h2', '', 'Preparando seu espaço…');
    title.id = 'arrivalTitle';
    const skip = el('button', '', 'Pular animação');
    skip.type = 'button';
    const progress = el('progress');
    progress.max = duration;
    progress.value = 0;
    progress.setAttribute('aria-label', 'Progresso da animação');
    const controls = el('div', 'arrival-controls');
    controls.append(title, progress, skip);
    dialog.append(clip, controls);
    document.body.append(dialog);
    dialog.showModal();
    const deadline = setTimeout(finish, 3000);
    function finish() {
      if (!dialog.open) return;
      clearTimeout(deadline);
      clip.pause();
      dialog.close();
      dialog.remove();
      document.querySelector('.welcome h1').setAttribute('tabindex', '-1');
      document.querySelector('.welcome h1').focus({ preventScroll: true });
    }
    skip.addEventListener('click', finish);
    dialog.addEventListener('cancel', e => { e.preventDefault(); finish(); });
    clip.addEventListener('timeupdate', () => {
      progress.value = Math.max(0, clip.currentTime - clipStart);
      if (clip.currentTime >= clipStart + duration - .05) finish();
    });
    clip.addEventListener('pause', () => { if (clip.currentTime >= clipStart + duration - .05) finish(); });
    clip.addEventListener('error', finish, { once: true });
    clip.play().catch(finish);
  }

  async function routine() {
    try {
      const activeOwner = owner || (window.LattesUI && window.LattesUI.owner) || 'Aramys Silva dos Reis';
      const d = await json('/api/rotina?usuario=' + encodeURIComponent(activeOwner));
      $('savedCount').textContent = fmt(d.registros_salvos);
      $('confirmedCount').textContent = fmt(d.envios_confirmados);
      $('attentionCount').textContent = fmt(d.envios_atencao);
      const labels = { salvo: 'Salvo no Lattes', preenchido: 'Preenchido, confirme no Lattes', atencao: 'Conferir no Lattes', erro: 'Falha no envio', removido: 'Removido', removendo: 'Remoção em andamento', enviando: 'Envio em andamento', falha_remocao: 'Falha na remoção' };
      const pending = $('routinePending');
      if (d.envios_atencao) {
        $('nextStep').dataset.state = 'pending';
        $('nextTitle').textContent = d.envios_atencao === 1 ? '1 envio para conferir' : `${fmt(d.envios_atencao)} envios para conferir`;
        $('nextText').textContent = 'Veja o que precisa de atenção nos seus envios ao Lattes.';
        $('nextAction').textContent = 'Conferir envios';
        $('nextAction').href = '/#registros';
        pending.replaceChildren(...(d.pendencias || []).map(r => {
          const item = el('li', 'data-row'), body = el('div');
          const status = r.xml_status === 'ausente' ? 'Ausente na cópia importada'
            : r.xml_status === 'ainda_presente' ? 'Ainda consta na cópia importada' : labels[r.status] || r.status;
          body.append(el('strong', '', r.titulo || 'Envio sem título'), el('small', '', status));
          item.append(body);
          return item;
        }));
        pending.hidden = !pending.childElementCount;
      } else {
        $('nextStep').dataset.state = 'clear';
        $('nextTitle').textContent = '✓ Sem pendências';
        $('nextText').textContent = d.registros_salvos
          ? 'Adicione uma produção ou retome um registro salvo abaixo.'
          : 'Adicione uma produção para começar a registrar suas atividades.';
        $('nextAction').textContent = '+ Adicionar produção';
        $('nextAction').href = '/';
      }
      $('nextAction').hidden = false;
      $('routineRecords').replaceChildren(...d.registros.map(r => {
        const row = el('div', 'data-row'), text = el('div');
        const title = r.titulo || 'Registro sem título';
        const resume = link('Retomar ›', `/?retomar=${encodeURIComponent(r.id)}`);
        resume.setAttribute('aria-label', 'Retomar ' + title);
        text.append(el('strong', '', title), el('small', '', 'Salvo em ' + date(r.criado_em)));
        row.append(text, resume);
        return row;
      }));
      if (!d.registros.length) empty('routineRecords', 'Você ainda não tem registros salvos. Comece por Adicionar produção.');
      $('routineActivity').replaceChildren(...d.atividade.map(r => {
        const row = el('div', 'data-row'), text = el('div'); text.append(el('strong', '', r.titulo || 'Envio sem título'), el('small', '', date(r.enviado_em)));
        const confirmed = ['salvo', 'preenchido', 'atencao'].includes(r.status) && r.xml_status === 'confirmado';
        let label = confirmed ? 'Confirmado no currículo' : labels[r.status] || r.status;
        if (r.xml_status === 'ausente') label = 'Ausente na cópia importada';
        row.append(text, el('span', 'badge' + (confirmed ? ' success' : ['erro','atencao'].includes(r.status) || r.xml_status === 'ausente' ? ' warning' : ''), label)); return row;
      }));
      if (!d.atividade.length) empty('routineActivity', 'Nenhum envio ao Lattes registrado para este perfil.');
    } catch (e) {
      notice('routineNotice', e.message);
      $('nextTitle').textContent = 'Seus registros estão temporariamente indisponíveis'; $('nextText').textContent = 'Você pode continuar a atualização ou tentar novamente ao recarregar esta página.';
      empty('routineRecords', 'Não foi possível consultar os registros.'); empty('routineActivity', 'Não foi possível consultar a atividade.');
    }
  }

  let curriculum = null, dashboard = null;
  const groups = [
    ['Pesquisa e produção', 'Artigos, livros, capítulos e trabalhos científicos.', new Set(['artigo','artigo_aceito','livro','capitulo','trabalho_evento','texto_jornal','outra_producao_bibliografica'])],
    ['Formação de pessoas', 'Orientações, bancas e atividades de ensino.', new Set(['orientacao_concluida','orientacao_andamento','banca','curso_ministrado'])],
    ['Inovação e aplicação', 'Projetos, patentes e soluções desenvolvidas.', new Set(['projeto','patente','software','produto_tecnologico','trabalho_tecnico','registro_propriedade','outra_producao_tecnica'])],
    ['Comunidade e sociedade', 'Eventos, divulgação e produção cultural.', new Set(['apresentacao','organizacao_evento','participacao_evento','producao_artistica','premio'])]
  ];
  function drawChart(counts, start, end, unit) {
    const svg = $('trajectoryChart');
    svg.replaceChildren();
    const namespace = 'http://www.w3.org/2000/svg';
    function add(tag, attrs, text) {
      const node = document.createElementNS(namespace, tag);
      Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
      if (text != null) node.textContent = String(text);
      svg.append(node);
      return node;
    }
    if (!counts.size) {
      svg.setAttribute('aria-label', 'Sem ' + unit + ' com ano informado neste período.');
      add('text', { x: 350, y: 110, 'text-anchor': 'middle', class: 'chart-axis', 'font-size': 24 }, 'Sem ' + unit + ' neste período.');
      return;
    }
    const years = Array.from({ length: end - start + 1 }, (_, i) => start + i);
    const max = Math.max(...counts.values(), 1);
    const width = 656 / years.length, base = 190;
    const barWidth = Math.min(64, width * .7);
    const labelStep = Math.ceil(years.length / 8);
    svg.setAttribute('aria-label', years.map(year => year + ': ' + (counts.get(year) || 0) + ' ' + unit).join(', '));
    add('line', { x1: 22, x2: 678, y1: base, y2: base, class: 'chart-baseline' });
    years.forEach((year, i) => {
      const n = counts.get(year) || 0;
      const height = 143 * n / max;
      const center = 22 + (i + .5) * width;
      if (n) {
        const bar = add('rect', { x: center - barWidth / 2, y: base - height, width: barWidth, height, rx: 5, class: n === max ? 'chart-bar peak' : 'chart-bar' });
        const tooltip = document.createElementNS(namespace, 'title');
        tooltip.textContent = year + ': ' + n + ' ' + unit;
        bar.append(tooltip);
      }
      if (years.length <= 10) add('text', { x: center, y: base - height - 8, 'text-anchor': 'middle', class: 'chart-value', 'font-size': 23 }, n);
      if (i === years.length - 1 || (i % labelStep === 0 && i <= years.length - 1 - labelStep)) {
        add('text', { x: center, y: 219, 'text-anchor': 'middle', class: 'chart-axis', 'font-size': years.length <= 5 ? 23 : 19 }, year);
      }
    });
  }

  let fallback = null;
  function renderTrajectoryFallback(ab, ownerName) {
    const period = Number($('trajectoryPeriod').value), year = new Date().getFullYear();
    const prod = ab.producao || {}, cit = ab.citacoes || {}, leg = ab.legado || {}, alc = ab.alcance || {};
    const totalProd = prod.total || 0;
    const totalCit = cit.total || 0;
    const hIndex = cit.h || 0;
    const periodicals = alc.periodicos || 0;
    const metrics = [
      [totalProd, 'Obras indexadas'],
      [totalCit, 'Citações acompanhadas'],
      [hIndex ? `h-${hIndex}` : '—', 'Índice de impacto'],
      [periodicals, 'Periódicos citantes']
    ];
    $('trajectoryMetrics').replaceChildren(...metrics.map(([n, label]) => {
      const box = el('article', 'panel');
      box.append(el('span', 'label', label), el('b', 'value', n == null ? '—' : (typeof n === 'number' ? fmt(n) : n)), el('span', 'note', 'Bases abertas (OpenAlex & citação)'));
      return box;
    }));

    const dims = Array.isArray(ab.dimensoes) && ab.dimensoes.length ? ab.dimensoes : [
      { id: 'conhecimento', nome: 'Geração de conhecimento', descricao: 'Artigos, livros, capítulos e trabalhos científicos.', total: totalProd },
      { id: 'formacao', nome: 'Formação de pessoas', descricao: 'Orientações, bancas e atividades de ensino.', total: leg.pessoas_orientadas || 0 },
      { id: 'impacto', nome: 'Inovação e aplicação', descricao: 'Projetos, patentes e soluções desenvolvidas.', total: leg.projetos || 0 },
      { id: 'comunidade', nome: 'Comunidade e sociedade', descricao: 'Eventos, divulgação e produção cultural.', total: leg.eventos_registrados || 0 },
    ];
    $('trajectoryDimensions').replaceChildren(...dims.map(d => {
      const row = el('div', 'data-row'), body = el('div');
      body.append(el('strong', '', d.nome), el('small', '', d.descricao || ''));
      row.append(body, el('span', 'badge', fmt(d.total || 0) + ' registros'));
      return row;
    }));

    const series = (prod.serie || []).slice(period ? -period : 0);
    const counts = new Map(series.map(item => [Number(item.ano), Number(item.valor) || 0]));
    $('trajectoryChartTitle').textContent = 'Obras indexadas por ano';
    $('trajectoryChartSummary').textContent = fmt(totalProd) + ' obras nas bases abertas';
    drawChart(counts, Math.min(...counts.keys()), Math.max(...counts.keys()), 'obras');
    $('trajectoryChartNote').textContent = `${year} é um ano em andamento. Citações e produção unificadas via OpenAlex e CrossRef.`;

    const topObras = ab.obras_mais_citadas || [];
    const milestones = topObras.slice(0, 3);
    $('trajectoryMilestones').replaceChildren(...milestones.map(o => {
      const li = el('li');
      li.append(el('b', '', `${o.ano || '—'} · Artigo (${fmt(o.total || 0)} citações)`), el('p', '', o.titulo || 'Sem título informado'));
      return li;
    }));
    if (!milestones.length) empty('trajectoryMilestones', 'Ainda não há marcos registrados para este perfil.');

    $('trajectorySource').textContent = `Fonte: Bases abertas de citação (OpenAlex / ORCID) · ${ownerName}`;
    $('trajectoryNotice').replaceChildren(
      el('p', 'notice info', 'Exibindo trajetória pelas publicações e citações das bases abertas. '),
      link('Importar currículo completo (XML/Lattes ao vivo)', '/meu-curriculo.html#importar')
    );
  }

  function renderTrajectory() {
    if (!curriculum) return;
    const period = Number($('trajectoryPeriod').value), year = new Date().getFullYear();
    const items = curriculum.itens.filter(i => !period || (Number(i.ano) >= year - 4 && Number(i.ano) <= year));
    const summary = D.summary(items);
    // A contagem integral vem do servidor, que conhece também o nome de citação.
    const authors = period ? null : dashboard.legado?.coautores_unicos;
    const metrics = [[summary.productions,'Produções registradas'],[summary.orientations,'Orientações concluídas'],[summary.projects,'Projetos registrados'],[authors,'Coautores identificados']];
    $('trajectoryMetrics').replaceChildren(...metrics.map(([n,label]) => { const box = el('article','panel'); box.append(el('span','label',label),el('b','value',n == null ? '—' : fmt(n)),el('span','note',n == null ? 'Consulte todo o período' : period ? 'No período selecionado' : 'Na versão importada')); return box; }));
    $('trajectoryDimensions').replaceChildren(...groups.map(([name,desc,cats]) => { const row = el('div','data-row'), body = el('div'); body.append(el('strong','',name),el('small','',desc)); row.append(body,el('span','badge',fmt(items.filter(i => cats.has(i.categoria)).length)+' registros')); return row; }));
    const counts = new Map();
    for (const item of items) {
      const itemYear = Number(item.ano);
      if (item.categoria === 'artigo' && Number.isInteger(itemYear) && itemYear >= 1900 && itemYear <= 2100) {
        counts.set(itemYear, (counts.get(itemYear) || 0) + 1);
      }
    }
    const start = period ? year - period + 1 : Math.min(...counts.keys());
    const end = period ? year : Math.max(...counts.keys());
    const articleTotal = curriculum.itens.filter(item => item.categoria === 'artigo').length;
    $('trajectoryChartSummary').textContent = (counts.size ? start + '–' + end + ' · ' : '') + fmt(articleTotal) + ' artigos na versão importada';
    drawChart(counts, start, end, 'artigos');
    $('trajectoryChartNote').textContent = counts.has(year)
      ? year + ' é um ano em andamento. O gráfico reúne artigos com ano informado.'
      : 'O gráfico reúne artigos com ano informado.';
    const names = { orientacao_concluida: 'Orientação concluída', projeto: 'Projeto registrado', patente: 'Patente registrada', premio: 'Prêmio ou título', artigo: 'Artigo publicado' };
    const candidates = items.filter(item => Number(item.ano) && Object.hasOwn(names, item.categoria))
      .sort((a, b) => Number(b.ano) - Number(a.ano));
    const categories = ['premio', 'projeto', 'patente', 'orientacao_concluida'];
    const featured = categories.map(category => candidates.find(item => item.categoria === category)).filter(Boolean);
    const milestones = [...featured, ...candidates.filter(item => !featured.includes(item))]
      .slice(0, 3).sort((a, b) => Number(b.ano) - Number(a.ano));
    $('trajectoryMilestones').replaceChildren(...milestones.map(item => {
      const milestone = el('li');
      milestone.append(el('time', '', item.ano), el('b', '', item.titulo || 'Sem título informado'), el('p', 'muted', names[item.categoria]));
      return milestone;
    }));
    if (!milestones.length) empty('trajectoryMilestones','Ainda não há marcos com ano informado neste período.');
  }
  async function trajectory() {
    try {
      const activeOwner = owner || window.LattesUI?.owner || 'Aramys Silva dos Reis';
      const { snapshots } = await json('/api/curriculo/snapshots');
      const own = (snapshots || []).filter(s => sameOwner(s.nome));
      const selected = window.LattesUI.storage.get('lf-cv-selection:' + activeOwner);
      const snapshot = own.find(s => s.id === selected) || own[0];
      if (snapshot) {
        [curriculum, dashboard] = await Promise.all([
          json('/api/curriculo?snapshot=' + encodeURIComponent(snapshot.id)),
          json('/api/curriculo/dashboard?snapshot=' + encodeURIComponent(snapshot.id))
        ]);
        $('trajectorySource').textContent = `Fonte: ${snapshot.fonte === 'pagina' ? 'leitura do Lattes' : 'XML importado'} · Versão guardada em ${date(snapshot.carregado_em)} · ${curriculum.nome}`;
        const summary = dashboard.perfil?.resumo;
        if (summary) {
          const details = el('details', 'detail-fold');
          details.append(el('summary', '', 'Resumo do pesquisador'), el('p', 'muted', summary));
          $('trajectoryProfile').replaceChildren(details);
        }
        for (const opportunity of dashboard.oportunidades || []) {
          if (!['/auditoria.html', '/meu-curriculo.html', '/painel.html', '/painel.html#secEdi'].includes(opportunity.href)) continue;
          const item = el('div', 'opportunity');
          item.append(el('strong', '', opportunity.titulo), el('p', '', opportunity.descricao), link(opportunity.acao, opportunity.href));
          $('trajectoryProfile').append(item);
        }
        renderTrajectory();
      } else {
        const ab = await json('/api/abertura?usuario=' + encodeURIComponent(activeOwner));
        fallback = { data: ab, owner: activeOwner };
        renderTrajectoryFallback(ab, activeOwner);
      }
    } catch (e) { notice('trajectoryNotice', e.message); $('trajectorySource').textContent = 'Dados indisponíveis; nenhum indicador foi estimado.'; }
  }
  $('trajectoryPeriod').addEventListener('change', () => {
    if (curriculum) renderTrajectory();
    else if (fallback) renderTrajectoryFallback(fallback.data, fallback.owner);
  });
  if (new URLSearchParams(location.search).get('primeiro_acesso') === '1') {
    const welcomeNotice = el('p', 'notice info', 'Boas-vindas ao NautiScience! Seu perfil foi configurado. Sincronize seu Currículo Lattes para acompanhar sua trajetória completa.');
    $('routineNotice').prepend(welcomeNotice);
  }
  routine(); trajectory();
})();
