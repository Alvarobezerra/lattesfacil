/* Fase 5 da metodologia: executa os casos da matriz (ferramentas/saida/casos_<item>.js) no formulário REAL do Lattes
 * usando o autofill de verdade (extensao/autofill_core.js) e lê cada campo de volta para comparar com o esperado.
 *
 * Pré-requisitos (na aba do currículo, formulário em branco aberto): carregar por <script src> do receptor local
 *   autofill_core.js, casos_<item>.js e este arquivo. Depois:
 *     const r = await window.top.__f5.rodar('projeto_de_extensao', { item: 'projeto', variante: 'Projeto de extensão' })
 * NUNCA clica em Salvar. Resultado enviado ao receptor (docs/campos-lattes/ref/<item>_f5/<variante>.json).
 */
(function () {
  const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
  const norm = (t) => String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();

  function formulario() {
    let melhor = null, mx = 0;
    const varrer = (w) => { try { const n = w.document.querySelectorAll('input[name],select[name],textarea[name]').length; if (n > mx) { mx = n; melhor = w; } } catch (e) { /* outro domínio */ } for (let i = 0; i < w.length; i++) varrer(w[i]); };
    varrer(window.top);
    return melhor;
  }
  // O envio dos resultados usa __enviarCaptura (auditoria_lattes.js): carrega sozinho se ainda não estiver na página.
  if (!window.top.__enviarCaptura) { const sc = document.createElement('script'); sc.src = 'http://127.0.0.1:8798/auditoria_lattes.js?' + Date.now(); document.head.appendChild(sc); }
  // Silencia alert/confirm/prompt de todas as janelas do Lattes enquanto o executor roda (a abertura dos formulários também dispara alertas).
  window.top.__alertasLattes = window.top.__alertasLattes || [];
  const silenciarTudo = (w, prof) => { if (prof > 6) return; try { if (!w.__lfSil) { w.alert = (m) => { window.top.__alertasLattes.push(String(m).replace(/\s+/g, ' ').slice(0, 200)); }; w.confirm = () => true; w.prompt = () => ''; w.__lfSil = true; } for (let i = 0; i < w.frames.length; i++) silenciarTudo(w.frames[i], prof + 1); } catch (e) { /* outro domínio */ } };
  if (!window.top.__lfSilTimer) window.top.__lfSilTimer = setInterval(() => silenciarTudo(window.top, 0), 150);
  const lista = (d, name) => [...d.querySelectorAll('[name="' + name + '"]')].filter((e) => e.value !== 'DUMMY');

  function ler(d, name, tipo) {
    const els = lista(d, name);
    if (!els.length) return { existe: false };
    const e0 = els[0];
    if (e0.type === 'radio') { const c = els.find((x) => x.checked); return { existe: true, valor: c ? c.value : '' }; }
    if (e0.type === 'checkbox') return { existe: true, conjunto: els.filter((x) => x.checked).map((x) => x.value).sort() };
    if (e0.tagName === 'SELECT') return { existe: true, valor: e0.value, texto: (e0.options[e0.selectedIndex] || {}).text || '' };
    return { existe: true, valor: e0.value };
  }

  function limpar(d, name) {
    lista(d, name).forEach((e) => {
      if (e.type === 'checkbox') { if (e.checked) e.click(); }
      else if (e.type === 'radio') { /* radios não se desmarcam; o caso seguinte define o valor */ }
      else if (e.tagName === 'SELECT') { e.value = ''; e.dispatchEvent(new Event('change', { bubbles: true })); }
      else { e.value = ''; e.dispatchEvent(new Event('input', { bubbles: true })); }
    });
  }

  async function autofill(campos) {
    const msgs = [];
    const alertaOriginal = window.alert;
    window.alert = (m) => { msgs.push(String(m)); };
    try {
      await window.__lfAutofill({
        tipo_producao: 'generico', __usuario: '', __origem: '', __autoSalvar: false, __semAlerta: true,
        __generico: { id: (window.__alvoF5 || {}).id || 'projeto', item: 'Teste de validação', como_abrir: '', url: (window.__alvoF5 || {}).url || 'PKG_PROJETO.form', campos, faltam: [], grades: {} },
      });
    } finally { window.alert = alertaOriginal; }
    return msgs.join(' | ').replace(/\s+/g, ' ').slice(0, 400);
  }

  function comparar(caso, lido) {
    const e = caso.esperado;
    if (!lido.existe) return ['campo_ausente', ''];
    if (e.modo === 'texto') {
      if (lido.valor === e.valor) return ['OK', ''];
      if (e.registrar_apenas) return ['registrado', 'lido=' + lido.valor];
      return ['divergente', 'esperado=' + e.valor.slice(0, 60) + ' lido=' + String(lido.valor).slice(0, 60)];
    }
    if (e.modo === 'valor') return lido.valor === e.valor ? ['OK', ''] : ['divergente', 'esperado=' + e.valor + ' lido=' + lido.valor];
    if (e.modo === 'conjunto') {
      const a = [...e.valores].sort().join(','), b = (lido.conjunto || []).join(',');
      return a === b ? ['OK', ''] : ['divergente', 'esperado=' + a + ' lido=' + b];
    }
    if (e.modo === 'lupa') return norm(lido.valor).includes(e.contem) ? ['OK', ''] : ['exige_acao_manual', 'lido=' + lido.valor];
    return ['indefinido', ''];
  }

  async function rodar(slug, meta, opcoes) {
    opcoes = opcoes || {};
    const w = formulario(); const d = w.document;
    const casos = (window.__casos[slug] || []).filter((c) => (opcoes.lentos ? true : !c.lento));
    casos.sort((a, b) => (a.lento ? 1 : 0) - (b.lento ? 1 : 0));
    const resultados = [];
    for (const caso of casos) {
      window.top.__f5caso = { slug, id: caso.id, desde: Date.now() };  // rastreio: qual caso está rodando (para achar travas)
      const t0 = Date.now();
      let status, detalhe = '', aviso = '', lido = null;
      try {
        const gatInicial = {};
        (caso.pre || []).forEach((p) => { const e = lista(d, p.name); if (e[0] && e[0].type === 'radio') { const c = e.find((x) => x.checked); gatInicial[p.name] = c ? c.value : ''; } });
        limpar(d, caso.campo);
        let campos = (caso.pre || []).concat([caso.alvo]);
        if ((caso.campo === 'f_orgao' || caso.campo === 'f_curso') && !((d.querySelector('[name="f_inst"]') || {}).value)) campos = [{ name: 'f_inst', rotulo: 'Instituição', tipo: 'text', valor: 'Universidade Federal do Maranhão', codigo: '', codigos: [], auto: false }].concat(campos);
        aviso = await autofill(campos);
        await dormir(200);
        lido = ler(d, caso.campo, caso.tipo);
        [status, detalhe] = comparar(caso, lido);
        // volta os gatilhos ao estado inicial
        for (const p of (caso.pre || [])) {
          const e = lista(d, p.name);
          if (!e.length) continue;
          if (e[0].type === 'radio' && gatInicial[p.name]) { const r = e.find((x) => x.value === gatInicial[p.name]); if (r && !r.checked) r.click(); }
          if (e[0].type === 'checkbox') e.filter((x) => x.checked).forEach((x) => x.click());
        }
        await dormir(150);
      } catch (err) { status = 'erro'; detalhe = String(err && err.message || err); }
      resultados.push({ id: caso.id, campo: caso.campo, status, detalhe, aviso: /Atenção/.test(aviso) ? aviso.replace(/^.*?Atenção:/, 'Atenção:').slice(0, 220) : '', ms: Date.now() - t0 });
    }
    const resumo = {};
    resultados.forEach((r) => { resumo[r.status] = (resumo[r.status] || 0) + 1; });
    const saida = { item: (meta.item || 'projeto') + '_f5', variante_slug: slug, variante: meta.variante, executado_em: new Date().toISOString(), resumo, resultados };
    window.top.__ultimoF5 = saida;
    const envio = await window.top.__enviarCaptura(saida);
    return JSON.stringify(resumo) + ' | ' + envio;
  }
  // Listas da aba Equipe (projeto): pesquisadores (com coordenador), instituições envolvidas e financiamento. Preenche com o autofill
  // real e confere o que ficou nas tabelas do formulário. Nunca salva.
  async function listas(meta) {
    const w = formulario(); const d = w.document;
    const grades = {
      autores: [{ nome: 'ZZ-TESTE Pesquisador Coordenador', citacao: 'COORDENADOR, Z. T.', coordenador: true }, { nome: 'ZZ-TESTE Pesquisador Dois', citacao: 'DOIS, Z. T.' }],
      instituicoes_envolvidas: ['Universidade Federal do Maranhão'],
      // Cadastro único no Lattes. (O CNPq tem dois cadastros de mesmo nome, DF e RJ: escolha manual é o comportamento correto.)
      financiamentos: [(meta.financiadora || 'Fundação de Amparo à Pesquisa e ao Desenvolvimento Científico e Tecnológico do Maranhão') + '; 123456; REAL; 1500,00; Bolsa'],
    };
    const msgs = [];
    const alertaOriginal = window.alert; window.alert = (m) => { msgs.push(String(m)); };
    try {
      window.top.__lfUltimoRelatorio = '';
      await window.__lfAutofill({ tipo_producao: 'generico', __usuario: '', __origem: '', __autoSalvar: false, __semAlerta: true, __generico: { id: 'projeto', item: 'Teste de listas', como_abrir: '', url: 'PKG_PROJETO.form', campos: [], faltam: [], grades } });
    } finally { window.alert = alertaOriginal; }
    for (let k = 0; k < 15 && !window.top.__lfUltimoRelatorio; k++) await dormir(1000);
    msgs.push(String(window.top.__lfUltimoRelatorio || ''));
    await dormir(1500);
    const dd = () => { try { return formulario().document; } catch (e) { return d; } };  // relê o formulário depois do preenchimento (o frame pode ter sido trocado)
    const txt = (id) => { const e = dd().getElementById(id); return e ? e.textContent.replace(/\s+/g, ' ').trim() : ''; };
    const linhasAutor = [...(dd().getElementById('autorHolder') || { querySelectorAll: () => [] }).querySelectorAll('tr')].map((tr) => tr.textContent.replace(/\s+/g, ' ').trim());
    const coord = linhasAutor.find((l) => /COORDENADOR, Z\. T\./i.test(l)) || '', dois = linhasAutor.find((l) => /DOIS, Z\. T\./i.test(l)) || '';
    const resultados = [
      { id: 'autores#presentes', status: coord && dois ? 'OK' : 'divergente', detalhe: coord && dois ? '' : 'linhas=' + linhasAutor.join(' // ').slice(0, 200) },
      { id: 'autores#coordenador_sim', status: /sim\s*$/i.test(coord.trim()) || /\bsim\b/i.test(coord) ? 'OK' : 'divergente', detalhe: 'linha=' + coord.slice(0, 120) },
      { id: 'autores#segundo_nao_coordenador', status: /n[ãa]o/i.test(dois) ? 'OK' : 'divergente', detalhe: 'linha=' + dois.slice(0, 120) },
      { id: 'instituicoes_envolvidas#uma', status: /maranh/i.test(txt('titularInstHolder') + ' ' + txt('f_instituicoes')) ? 'OK' : 'divergente', detalhe: txt('titularInstHolder').slice(0, 160) },
      { id: 'financiamento#linha', status: /123456/.test(txt('grid2')) && /bolsa/i.test(txt('grid2')) ? 'OK' : 'divergente', detalhe: txt('grid2').slice(0, 200) },
    ];
    resultados.forEach((r) => { r.aviso = ''; r.ms = 0; r.campo = r.id.split('#')[0]; });
    const resumo = {}; resultados.forEach((r) => { resumo[r.status] = (resumo[r.status] || 0) + 1; });
    const saida = { item: (meta.item || 'projeto') + '_f5', variante_slug: meta.slug || 'listas', variante: meta.variante || 'listas', executado_em: new Date().toISOString(), resumo, resultados, avisos_autofill: msgs.join(' | ').replace(/\s+/g, ' ').slice(0, 900) };
    window.top.__ultimoF5 = saida;
    return JSON.stringify(resumo) + ' | ' + await window.top.__enviarCaptura(saida);
  }

  // Abre o formulário de cada variante pela URL (como o próprio autofill faz) e roda a matriz. Segue em segundo plano:
  //   window.top.__f5.rodarTodas([{ slug, variante, tipo: 'E' }, ...], { item: 'projeto' });  depois consultar window.top.__f5todas
  async function abrirPorTipo(tipo) {
    const topo = window.top;
    const cv = (topo.document.querySelector('[name="f_cod"]') || {}).value || ((topo.document.documentElement.innerHTML.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i) || [])[1]) || '';
    topo.modalCV2.setarUrl('PKG_PROJETO.form?f_tpo_cooperacao=X&f_tpo_acao_inov=X&f_tematica=X&F_sta_inovacao=&f_cod_tipo=' + tipo + '&f_cod=' + cv, true);
    for (let k = 0; k < 50; k++) {
      await dormir(400);
      const w = formulario();
      try { if (w && w.frameElement && w.document.querySelector('[name=f_titulo]') && w.frameElement.src.indexOf('f_cod_tipo=' + tipo) >= 0 && w.document.readyState === 'complete') { await dormir(1500); return true; } } catch (e) { /* aguarda */ }
    }
    return false;
  }
  // Abre um formulário por endereço completo (artigo: caminhos manual e por DOI). A espera extra evita que o Lattes limpe campos depois de "complete".
  async function abrirPorUrl(url, pagina) {
    const topo = window.top;
    const cv = (topo.document.querySelector('[name="f_cod"]') || {}).value || ((topo.document.documentElement.innerHTML.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i) || [])[1]) || '';
    window.__alvoF5 = { id: (window.__alvoF5 || {}).id || 'projeto', url };
    const listaDe = { artigo: 'pkg_artigo.lista?f_cod=' + cv, anais: 'pkg_trabalho.lista?f_cod=' + cv, orientacao_concluida: 'pkg_orient.lista?f_tipo=C&f_cod=' + cv, orientacao_andamento: 'pkg_orient.lista?f_tipo=A&f_cod=' + cv, apresentacao: 'prc_tec_demais_lista?f_cod_tipo=2J&f_cod=' + cv }[window.__alvoF5.id];
    if (listaDe) { topo.modalCV2.setarUrl(listaDe, true); await dormir(4000); }  // como o robô: a lista prepara o estado do servidor
    topo.modalCV2.setarUrl(url.replace('<codigo_do_cv>', cv), true);
    await dormir(1500);
    for (let k = 0; k < 50; k++) {
      await dormir(400);
      const w = formulario();
      try { if (w && w.frameElement && w.document.querySelector('[name=f_titulo]') && w.frameElement.src.toLowerCase().indexOf(pagina.toLowerCase()) >= 0 && w.document.readyState === 'complete') { await dormir(3500); return true; } } catch (e) { /* aguarda */ }
    }
    return false;
  }
  async function rodarTodas(lista, meta, opcoes) {
    window.top.__f5todas = { iniciado: new Date().toISOString(), concluidas: [], andamento: '' };
    for (const v of lista) {
      window.top.__f5todas.andamento = v.slug;
      const abriu = v.url ? await abrirPorUrl(v.url, v.pagina || 'pkg_artigo.form') : await abrirPorTipo(v.tipo);
      if (!abriu) { window.top.__f5todas.concluidas.push({ slug: v.slug, erro: 'formulário não abriu' }); continue; }
      const r = await rodar(v.slug, { item: (meta || {}).item || 'projeto', variante: v.variante }, opcoes);
      window.top.__f5todas.concluidas.push({ slug: v.slug, resumo: r, falhas: window.top.__ultimoF5.resultados.filter((x) => x.status !== 'OK').map((x) => x.id + ' => ' + x.status + (x.detalhe ? ' (' + x.detalhe + ')' : '')) });
    }
    window.top.__f5todas.andamento = 'FIM'; window.top.__f5todas.fim = new Date().toISOString();
  }
  window.top.__f5 = { rodar, ler, formulario, rodarTodas, abrirPorTipo, abrirPorUrl, listas };
})();
