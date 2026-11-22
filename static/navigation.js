// Menu único das páginas internas. Executado antes dos scripts de cada página.
(() => {
  const header = document.querySelector('header') || document.querySelector('body > nav');
  if (!header) return;
  const main = !!document.getElementById('lattesPill');
  const container = header.querySelector('.topbar-inner, .top-in') || header;
  header.classList.add('site-header');
  container.classList.add('site-header-inner');
  let nav = header.querySelector('nav');
  if (!nav) {
    nav = document.createElement('nav');
    container.append(nav);
  }
  nav.className = 'topnav site-navigation';
  nav.setAttribute('aria-label', 'Principal');
  const items = [
    ['Início', '/abertura.html'],
    ['Espaço Aramys', '/espaco-aramys.html'],
    ['Atualizar Lattes', '/'],
    ['Registros', '/#registros', 'btnToggleHistory'],
    ['Avaliação', '/#avaliacao'],
    ['Gestão de projetos', '/projetos.html'],
    ['Buscador de Editais', '/editais.html'],
    ['Extensão', '/instalar-extensao.html'],
  ];
  nav.replaceChildren(...items.map(([label, href, id]) => {
    const el = document.createElement(main && id ? 'button' : 'a');
    el.className = 'nav-link';
    el.textContent = label;
    if (el.tagName === 'BUTTON') { el.type = 'button'; el.id = id; }
    else el.href = href;
    if (main && id === 'btnToggleHistory') {
      const count = document.createElement('span');
      count.className = 'nav-count'; count.id = 'recordsCount'; count.textContent = '0';
      el.append(' ', count);
    }
    if (location.pathname === href) el.setAttribute('aria-current', 'page');
    return el;
  }));
  if (main) return;
  // A conexão usa a mesma sessão do cadastro, sem presumir login pelo cache.
  const status = document.createElement('a');
  status.className = 'site-lattes-status';
  status.href = '/';
  status.setAttribute('aria-live', 'polite');
  status.textContent = 'Lattes desconectado';
  container.append(status);
  async function refresh() {
    try {
      const sid = localStorage.getItem('lf-sid2');
      if (!sid) return;
      const response = await fetch('/api/lattes/status?sid=' + encodeURIComponent(sid), {cache: 'no-store'});
      if (!response.ok) throw new Error('status');
      const data = await response.json();
      const connected = data.seen && data.online && data.age <= 45;
      status.textContent = connected ? 'Lattes conectado' : 'Lattes desconectado';
      status.classList.toggle('connected', !!connected);
      status.title = connected ? String(data.name || '') : 'Abra Atualizar Lattes para conectar';
    } catch (_) {
      status.textContent = 'Lattes desconectado';
      status.classList.remove('connected');
    }
  }
  refresh();
  setInterval(refresh, 4000);
})();
