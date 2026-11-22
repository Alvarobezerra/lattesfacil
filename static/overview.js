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
      if (!owner) throw new Error('Selecione seu perfil na tela de login para consultar seus registros.');
      const d = await json('/api/rotina?usuario=' + encodeURIComponent(owner));
      $('savedCount').textContent = fmt(d.registros_salvos);
      $('confirmedCount').textContent = fmt(d.envios_confirmados);
      $('attentionCount').textContent = fmt(d.envios_atencao);
      if (d.envios_atencao) {
        $('nextTitle').textContent = 'Confira os envios que precisam de atenção';
        $('nextText').textContent = 'O histórico mostra o resultado de cada envio e permite verificar o item no Lattes.';
        $('nextAction').textContent = 'Conferir envios'; $('nextAction').href = '/#registros';
      } else {
        $('nextTitle').textContent = d.registros_salvos ? 'Continue mantendo seu Lattes em dia' : 'Registre sua primeira conquista';
        $('nextText').textContent = 'Envie um artigo, certificado ou declaração. Você revisa os dados antes de preencher no Lattes.';
      }
      $('routineRecords').replaceChildren(...d.registros.map(r => {
        const row = el('div', 'data-row'), text = el('div'); text.append(el('strong', '', r.titulo || 'Registro sem título'), el('small', '', 'Salvo em ' + date(r.criado_em))); row.append(text, link('Abrir histórico', '/#registros')); return row;
      }));
      if (!d.registros.length) empty('routineRecords', 'Você ainda não tem registros salvos. Comece por Adicionar produção.');
      const labels = { salvo: 'Salvo no Lattes', preenchido: 'Preenchido, confirme no Lattes', atencao: 'Conferir no Lattes', erro: 'Falha no envio', removido: 'Removido', removendo: 'Remoção em andamento', enviando: 'Envio em andamento' };
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
  function drawChart(items, period) {
    const svg = $('trajectoryChart'); svg.replaceChildren();
    const counts = new Map();
    items.filter(i => D.production.has(i.categoria)).forEach(i => { const year = Number(i.ano); if (year >= 1900 && year <= 2100) counts.set(year, (counts.get(year) || 0) + 1); });
    const current = new Date().getFullYear();
    if (!counts.size) { const t = document.createElementNS('http://www.w3.org/2000/svg', 'text'); t.setAttribute('x', '24'); t.setAttribute('y', '100'); t.setAttribute('fill', '#546580'); t.textContent = 'Sem produções com ano informado neste período.'; svg.append(t); return; }
    const start = period ? current - 4 : Math.min(...counts.keys()), end = period ? current : Math.max(...counts.keys());
    const years = Array.from({ length: end - start + 1 }, (_, i) => start + i);
    const max = Math.max(...counts.values(), 1), width = 650 / years.length, base = 195;
    const add = (tag, attrs, text) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([k,v]) => e.setAttribute(k, v)); if (text != null) e.textContent = String(text); svg.append(e); return e; };
    [0, .5, 1].forEach(part => { const y = base - 160 * part; add('line', { x1:35, x2:690, y1:y, y2:y, stroke:'#dbe4ee' }); add('text', { x:0, y:y+4, fill:'#546580', 'font-size':12 }, Math.round(max*part)); });
    years.forEach((year, i) => { const n = counts.get(year) || 0, height = 160*n/max, x = 35+i*width;
      const rect = add('rect', { x:x+width*.18, y:base-height, width:width*.64, height, rx:3, fill:'#00a3c4', opacity:year === current ? .65 : 1 });
      const title = document.createElementNS('http://www.w3.org/2000/svg','title'); title.textContent = `${year}: ${n} produções`; rect.append(title);
      if (years.length <= 12) add('text',{ x:x+width/2, y:base-height-7, 'text-anchor':'middle', fill:'#0b192c', 'font-size':12 }, n);
      if (i % Math.ceil(years.length/10) === 0 || i === years.length-1) add('text',{ x:x+width/2, y:218, 'text-anchor':'middle', fill:'#546580', 'font-size':12 }, year);
    });
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
    drawChart(items, period);
    $('trajectoryChartNote').textContent = `${year} é um ano em andamento. Itens sem ano não aparecem no gráfico.`;
    const milestones = items.filter(i => Number(i.ano) && ['orientacao_concluida','projeto','patente','premio','artigo'].includes(i.categoria)).sort((a,b) => Number(b.ano)-Number(a.ano)).slice(0,3);
    const names = { orientacao_concluida:'Orientação concluída', projeto:'Projeto registrado', patente:'Patente registrada', premio:'Prêmio ou título', artigo:'Artigo publicado' };
    $('trajectoryMilestones').replaceChildren(...milestones.map(i => { const li = el('li'); li.append(el('b','',`${i.ano} · ${names[i.categoria]}`),el('p','',i.titulo || 'Sem título informado')); return li; }));
    if (!milestones.length) empty('trajectoryMilestones','Ainda não há marcos com ano informado neste período.');
  }
  async function trajectory() {
    try {
      if (!owner) throw new Error('Selecione seu perfil no login.');
      const { snapshots } = await json('/api/curriculo/snapshots');
      const own = snapshots.filter(s => sameOwner(s.nome));
      const selected = window.LattesUI.storage.get('lf-cv-selection:' + owner);
      const snapshot = own.find(s => s.id === selected) || own[0];
      if (!snapshot) {
        notice('trajectoryNotice', 'Importe seu currículo ou leia o Lattes ao vivo para visualizar sua trajetória.');
        $('trajectoryNotice').append(link('Importar meu currículo', '/meu-curriculo.html#importar'));
        $('trajectorySource').textContent = 'Nenhuma versão encontrada para este perfil.';
        ['trajectoryDimensions','trajectoryMilestones'].forEach(id => empty(id,'Os dados aparecerão após a importação.'));
        return;
      }
      [curriculum,dashboard] = await Promise.all([json('/api/curriculo?snapshot='+encodeURIComponent(snapshot.id)),json('/api/curriculo/dashboard?snapshot='+encodeURIComponent(snapshot.id))]);
      if (!sameOwner(curriculum.nome) || !sameOwner(dashboard.nome)) throw new Error('A versão consultada pertence a outro perfil. Selecione seu currículo.');
      $('trajectorySource').textContent = `Fonte: ${snapshot.fonte === 'pagina' ? 'leitura do Lattes' : 'XML importado'} · Versão guardada em ${date(snapshot.carregado_em)} · ${curriculum.nome}`;
      const summary = dashboard.perfil?.resumo;
      if (summary) { const details = el('details','detail-fold'); details.append(el('summary','','Resumo do pesquisador'),el('p','muted',summary)); $('trajectoryProfile').replaceChildren(details); }
      for (const opportunity of dashboard.oportunidades || []) {
        if (!['/auditoria.html', '/meu-curriculo.html', '/painel.html', '/painel.html#secEdi'].includes(opportunity.href)) continue;
        const item = el('div', 'opportunity');
        item.append(el('strong', '', opportunity.titulo), el('p', '', opportunity.descricao), link(opportunity.acao, opportunity.href));
        $('trajectoryProfile').append(item);
      }
      renderTrajectory();
    } catch (e) { notice('trajectoryNotice', e.message); $('trajectorySource').textContent = 'Dados indisponíveis; nenhum indicador foi estimado.'; }
  }
  $('trajectoryPeriod').addEventListener('change',renderTrajectory);
  routine(); trajectory();
})();
