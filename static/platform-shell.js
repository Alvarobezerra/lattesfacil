/* Identidade e navegação das telas de consulta. Não altera a sessão do Lattes. */
(() => {
  const names = { alvaro: 'Álvaro Antônio Bezerra dos Santos', aramys: 'Aramys Silva dos Reis' };
  const storage = { get(key) { try { return localStorage.getItem(key) || ''; } catch (_) { return ''; } }, set(key, value) { try { localStorage.setItem(key, value); } catch (_) {} } };
  const cookie = document.cookie.match(/(?:^|;\s*)lf_user=([a-z]+)/);
  if (cookie && names[cookie[1]]) { storage.set('lf-usuario', names[cookie[1]]); document.cookie = 'lf_user=; Path=/; Max-Age=0'; }
  const owner = storage.get('lf-usuario');
  const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().replace(/\s+/g, ' ').toLowerCase();
  const sameOwner = name => !!owner && normalize(name) === normalize(owner);
  async function json(url, options) {
    const response = await fetch(url, options);
    if (response.status === 401) { location.assign('/login'); throw new Error('Sessão expirada.'); }
    let data;
    try { data = await response.json(); }
    catch (_) {
      if (url.startsWith('/api/rotina?') && response.status === 404) {
        throw new Error('Reinicie o servidor do NautiScience e recarregue a página para consultar os registros.');
      }
      throw new Error('O servidor não retornou os dados esperados. Recarregue a página e tente novamente.');
    }
    if (!response.ok) { const error = new Error(data.error || 'Não foi possível carregar os dados.'); error.dados = data; throw error; }
    return data;
  }
  window.LattesUI = { owner, storage, sameOwner, json, normalize };
  const initials = owner.split(/\s+/).filter(p => p.length > 2).slice(0, 2).map(p => p[0]).join('') || '?';
  document.querySelectorAll('[data-user-name]').forEach(e => e.textContent = owner.split(' ')[0] || 'pesquisador');
  document.querySelectorAll('[data-user-full]').forEach(e => e.textContent = owner || 'Selecione seu perfil no login');
  document.querySelectorAll('[data-user-initials]').forEach(e => e.textContent = initials);
  const sidebar = document.getElementById('platformSidebar');
  const items = [
    ["Visão geral","/abertura.html","M3 10l9-7 9 7v10H3z M9 20v-7h6v7"],
    ["Espaço Aramys","/espaco-aramys.html","M4 21v-2a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"],
    ["Meu currículo","/meu-curriculo.html","M6 3h8l4 4v14H6z M14 3v5h4 M9 12h6m-6 4h6"],
    ["Atualizar Lattes","/","M20 10a8 8 0 0 0-14-4L3 9m0-5v5h5 M4 14a8 8 0 0 0 14 4l3-3m0 5v-5h-5"],
    ["Registros","/#registros","M12 7v5l3 2 M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"],
    ["Avaliação","/#avaliacao","M5 4h14v16H5z M8 12l3 3 5-6"],
    ["Gestor de Projetos","/projetos.html","M12 3l9 5-9 5-9-5Z M3 12l9 5 9-5 M3 16l9 5 9-5"],
    ["Buscador de Editais","/editais.html","M4 10v5h4l9 4V6L8 10z M8 15l2 5 M20 9l2-2m-2 8 2 2"],
    ["Extensão","/instalar-extensao.html","M8 3h8v5h5v8h-5v5H8v-5H3V8h5z"],
  ];
  const brand = document.createElement('a');
  brand.className = 'platform-brand';
  brand.href = '/abertura.html';
  brand.setAttribute('aria-label', 'NautiScience - Início');

  const symbol = document.createElement('img');
  symbol.className = 'platform-brand-symbol';
  symbol.src = '/img/nautiscience/symbol-darkmode.png';
  symbol.alt = '';

  const wordmark = document.createElement('img');
  wordmark.className = 'platform-brand-text';
  wordmark.src = '/img/nautiscience/wordmark-darkmode.png';
  wordmark.alt = 'NAUTISCIENCE';

  brand.append(symbol, wordmark);
  const label = document.createElement('p'); label.className = 'sidebar-label'; label.textContent = 'ESPAÇO PESSOAL';
  const nav = document.createElement('nav'); nav.setAttribute('aria-label', 'Principal');
  const updatePage = !!document.getElementById('lattesPill');
  if (updatePage) nav.classList.add('topnav');
  const svgNS = 'http://www.w3.org/2000/svg';
  items.forEach(([text, href, path]) => {
    const a = document.createElement('a');
    a.href = href;
    const icon = document.createElementNS(svgNS, 'svg');
    icon.setAttribute('viewBox', '0 0 24 24');
    icon.setAttribute('aria-hidden', 'true');
    const shape = document.createElementNS(svgNS, 'path');
    shape.setAttribute('d', path);
    icon.append(shape);
    a.append(icon, text);
    if (updatePage && href === '/#registros') {
      a.id = 'btnToggleHistory';
      const count = document.createElement('span');
      count.id = 'recordsCount'; count.textContent = '0';
      a.append(count);
    }
    if (location.pathname + location.hash === href ||
        (location.pathname === href && href !== '/')) a.setAttribute('aria-current', 'page');
    nav.append(a);
  });
  const footer = document.createElement('div'); footer.className = 'sidebar-bottom';
  const logout = document.createElement('a');
  logout.href = '/logout';
  logout.textContent = 'Sair';
  footer.append(logout);
  const person = document.createElement('div'); person.className = 'sidebar-person'; const avatar = document.createElement('span'); avatar.className = 'platform-avatar'; avatar.textContent = initials; const name = document.createElement('span'); name.textContent = owner || 'Perfil não identificado'; person.append(avatar, name); footer.append(person);
  sidebar.replaceChildren(brand, label, nav, footer);
  const toggle = document.getElementById('sidebarToggle');
  toggle.addEventListener('click', () => { const open = toggle.getAttribute('aria-expanded') !== 'true'; toggle.setAttribute('aria-expanded', String(open)); document.body.classList.toggle('sidebar-open', open); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { document.body.classList.remove('sidebar-open'); toggle.setAttribute('aria-expanded', 'false'); } });
  const status = document.getElementById('platformConnection');
  if (!status) return;
  async function refresh() {
    let connected = false;
    try { const sid = storage.get('lf-sid2'); if (sid) { const d = await json('/api/lattes/status?sid=' + encodeURIComponent(sid)); connected = !!(d.seen && d.online && d.age <= 45); } } catch (_) {}
    status.textContent = connected ? 'Lattes conectado' : 'Lattes desconectado'; status.classList.toggle('connected', connected);
  }
  refresh(); setInterval(() => { if (!document.hidden) refresh(); }, 15000);
})();
