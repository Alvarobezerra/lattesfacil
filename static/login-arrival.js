(() => {
  const arrival = new URL(location.href);
  if (arrival.searchParams.get('entrada') !== '1') return;
  arrival.searchParams.delete('entrada');
  history.replaceState(history.state, '', arrival);
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  };
  showArrival();
  function showArrival() {
    const dialog = el('dialog', 'arrival-dialog');
    dialog.setAttribute('aria-labelledby', 'arrivalTitle');
    const clip = el('video');
    clip.muted = true;
    clip.playsInline = true;
    clip.poster = '/media/boas-vindas.jpg';
    clip.src = '/media/boas-vindas.mp4' + '#t=0,2.7';
    const title = el('h2', '', 'Preparando seu espaço…');
    title.id = 'arrivalTitle';
    const skip = el('button', '', 'Pular animação');
    skip.type = 'button';
    const progress = el('progress');
    progress.max = 2.7;
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
      document.querySelector('main h1')?.setAttribute('tabindex', '-1');
      document.querySelector('main h1')?.focus({ preventScroll: true });
    }
    skip.addEventListener('click', finish);
    dialog.addEventListener('cancel', e => { e.preventDefault(); finish(); });
    clip.addEventListener('timeupdate', () => {
      progress.value = clip.currentTime;
      if (clip.currentTime >= progress.max - .05) finish();
    });
    clip.addEventListener('pause', () => { if (clip.currentTime >= progress.max - .05) finish(); });
    clip.addEventListener('error', finish, { once: true });
    clip.play().catch(finish);
  }

})();
