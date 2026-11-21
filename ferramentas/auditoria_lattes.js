/* Auditoria de um formulário REAL do Lattes (fase 1 da metodologia: docs/metodologia-validacao-formularios.md).
 *
 * Como usar: com o formulário do item ABERTO no Chrome (em branco, sem salvar), execute este arquivo na página do
 * currículo (ele guarda as funções em window.top) e depois, para cada variante:
 *     await window.top.__auditar({ item: 'projeto', variante: 'Projeto de extensão', variante_slug: 'projeto_de_extensao' })
 * O resultado é enviado ao receptor local (python ferramentas/receptor_captura.py, porta 8798) e gravado em
 * docs/campos-lattes/ref/<item>/<variante_slug>.json. Só LÊ e alterna controles; nunca clica em Salvar.
 * Não grava URLs nem códigos do currículo. O envio usa pedidos de imagem em partes (a página do Lattes bloqueia fetch).
 */
function enviarCaptura(obj) {
  return new Promise((resolve) => {
    const s = encodeURIComponent(JSON.stringify(obj));
    const TAM = 1500, n = Math.ceil(s.length / TAM), chave = Date.now().toString(36);
    let recebidas = 0, falhas = 0;
    const fim = () => { if (recebidas + falhas === n) resolve('enviado em ' + n + ' partes (ok=' + recebidas + ', falhas=' + falhas + ')'); };
    for (let i = 0; i < n; i++) { const im = new Image(); im.onload = () => { recebidas++; fim(); }; im.onerror = () => { falhas++; fim(); }; im.src = 'http://127.0.0.1:8798/p?k=' + chave + '&i=' + i + '&t=' + n + '&d=' + s.slice(i * TAM, (i + 1) * TAM); }
    setTimeout(() => resolve('tempo esgotado (ok=' + recebidas + ', falhas=' + falhas + ' de ' + n + ')'), 20000);
  });
}

async function auditar(meta) {
  const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
  // Frame do formulário = o que tem mais campos nomeados.
  let melhor = null, mx = 0;
  const alvo = String(window.top.__paginaAlvo || '').toLowerCase();  // prefere o quadro da página aberta (sobras de outros formulários podem ter mais campos)
  const varrer = (w) => { try { const n = w.document.querySelectorAll('input[name],select[name],textarea[name]').length; const src = (w.frameElement && w.frameElement.src || '').toLowerCase(); const peso = alvo && src.indexOf(alvo) >= 0 && n > 0 ? n + 100000 : n; if (peso > mx) { mx = peso; melhor = w; } } catch (e) { /* outro domínio */ } for (let i = 0; i < w.length; i++) varrer(w[i]); };
  varrer(window.top);
  const w = melhor; const d = w.document;
  w.alert = () => {}; w.confirm = () => true;

  const visivel = (e) => { const cs = w.getComputedStyle(e), r = e.getBoundingClientRect(); return e.offsetParent !== null && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  const limpo = (t) => String(t || '').replace(/\s+/g, ' ').trim().slice(0, 140);
  const textosPerto = (e, sentido, max) => {
    const tw = d.createTreeWalker(d.body, NodeFilter.SHOW_TEXT); tw.currentNode = e; const out = [];
    for (let n = sentido < 0 ? tw.previousNode() : tw.nextNode(), k = 0; n && k < 14 && out.length < max; n = sentido < 0 ? tw.previousNode() : tw.nextNode(), k++) {
      const t = limpo(n.textContent); if (t && !n.parentElement.closest('script,style,option,select,textarea')) out.push(t);
    }
    return out;
  };
  const rotuloDe = (e) => { const l = e.id && d.querySelector('label[for="' + e.id + '"]'); return l ? limpo(l.textContent) : (textosPerto(e, -1, 1)[0] || ''); };
  // Texto de uma opção: "Sim ○ Não ○" (texto ANTES do radio) ou "☐ Texto" (texto DEPOIS da caixa).
  // Texto de uma opção de radio: o texto mais PRÓXIMO do botão (geometria), seja antes ("Sim ○") ou depois ("○ Sim").
  const noTexto = (e, sentido) => {
    const tw = d.createTreeWalker(d.body, NodeFilter.SHOW_TEXT); tw.currentNode = e;
    for (let n = sentido < 0 ? tw.previousNode() : tw.nextNode(), k = 0; n && k < 14; n = sentido < 0 ? tw.previousNode() : tw.nextNode(), k++) {
      if (limpo(n.textContent) && !n.parentElement.closest('script,style,option,select,textarea')) return n;
    }
    return null;
  };
  const distTexto = (n, x, sentido) => {
    if (!n) return Infinity;
    const r = d.createRange(); r.selectNodeContents(n); const rt = r.getBoundingClientRect(), rx = x.getBoundingClientRect();
    const dx = sentido < 0 ? rx.left - rt.right : rt.left - rx.right;
    const dy = Math.abs((rt.top + rt.bottom) / 2 - (rx.top + rx.bottom) / 2);
    return Math.abs(dx) + dy * 3;
  };
  const textoOpcao = (x) => {
    const a = textosPerto(x, -1, 1)[0] || '', p = textosPerto(x, 1, 1)[0] || '';
    if (x.type === 'radio') { const na = noTexto(x, -1), np = noTexto(x, 1); return distTexto(na, x, -1) <= distTexto(np, x, 1) ? a : p; }
    return p.length <= 60 ? p : a;
  };

  // Espera a página terminar de montar (o Lattes esconde/mostra campos ao carregar): conjunto de campos visíveis estável.
  const nomes0 = () => [...d.querySelectorAll('input,select,textarea')].filter((e) => e.type !== 'hidden' && e.name && visivel(e)).map((e) => e.name + (e.checked ? '*' : '')).join('|');
  for (let est = 0, ult = '', k = 0; est < 3 && k < 30; k++) { await dormir(300); const a = nomes0(); est = a === ult ? est + 1 : 0; ult = a; }

  const todos = [...d.querySelectorAll('input,select,textarea')].filter((e) => e.type !== 'hidden' && e.name);
  const grupos = new Map();
  todos.forEach((e) => { if (!grupos.has(e.name)) grupos.set(e.name, []); grupos.get(e.name).push(e); });
  const campos = [];
  const rotulosDeOpcao = new Set();
  grupos.forEach((els, name) => {
    const e0 = els[0]; const escolha = e0.type === 'radio' || e0.type === 'checkbox';
    const c = { name, tipo: e0.type === 'select-one' ? 'select' : e0.type === 'select-multiple' ? 'select_multiplo' : e0.tagName === 'TEXTAREA' ? 'textarea' : e0.type === 'radio' ? 'radio' : e0.type === 'checkbox' ? (els.length > 1 ? 'grupo_marcacao' : 'marcacao') : e0.type, desabilitado: els.every((x) => x.disabled), somente_leitura: els.every((x) => x.readOnly), visivel_inicial: els.some(visivel) };
    if (!escolha) c.rotulo = rotuloDe(e0);
    if (e0.maxLength > 0 && e0.maxLength < 100000) c.maxlength = e0.maxLength;
    if (e0.tagName === 'SELECT') { c.total_opcoes = e0.options.length; c.opcoes = [...e0.options].slice(0, 80).map((o) => ({ valor: o.value, texto: limpo(o.text) })); }
    if (escolha) { let anterior = null; c.opcoes = els.map((x) => { let t = textoOpcao(x); if (x.type === 'radio' && anterior !== null && t === anterior) { t = textosPerto(x, 1, 1)[0] || t; } anterior = t; rotulosDeOpcao.add(t); return { valor: x.value, texto: t, visivel: visivel(x), marcado_inicial: x.checked }; }); }
    campos.push(c);
  });
  // Pergunta de radios/grupos: primeiro texto antes do grupo que NÃO seja rótulo de opção (de qualquer grupo).
  campos.forEach((c) => {
    if (!c.opcoes || c.tipo === 'select') return;
    const els = grupos.get(c.name); const prim = els.find(visivel) || els[0];
    c.pergunta = textosPerto(prim, -1, 8).find((t) => !rotulosDeOpcao.has(t)) || '';
  });

  const nomesVisiveis = () => new Set([...grupos.entries()].filter(([, els]) => els.some(visivel)).map(([n]) => n));
  // Campos habilitados (visíveis e sem 'disabled'): o Lattes deixa alguns visíveis porém bloqueados até outro campo ser escolhido.
  const nomesHabilitados = () => new Set([...grupos.entries()].filter(([, els]) => els.some((x) => visivel(x) && !x.disabled)).map(([n]) => n));
  const diff0 = (a, b) => ({ aparecem: [...b].filter((x) => !a.has(x)).sort(), somem: [...a].filter((x) => !b.has(x)).sort() });
  const diff = (a, b) => diff0(a, b);
  const mudancas = (antesV, antesH) => { const dv = diff0(antesV, nomesVisiveis()), dh = diff0(antesH, nomesHabilitados());
    return { aparecem: dv.aparecem, somem: dv.somem, habilitam: dh.aparecem.filter((x) => !dv.aparecem.includes(x)), desabilitam: dh.somem.filter((x) => !dv.somem.includes(x)) }; };
  const estados = [];
  const habilitacoes = [];  // por opção de gatilho: campos que passam a ficar habilitados/desabilitados em relação ao estado inicial
  const baseH = nomesHabilitados(), baseV = nomesVisiveis();
  const regHab = (name, valor, texto) => { const h = nomesHabilitados(), v = nomesVisiveis(); const hab = [...h].filter((x) => !baseH.has(x) && baseV.has(x) && v.has(x)).sort(), des = [...baseH].filter((x) => !h.has(x) && v.has(x)).sort(); if (hab.length || des.length) habilitacoes.push({ gatilho: name, valor, texto, habilitam: hab, desabilitam: des }); };
  for (const [name, els] of grupos) {
    const e0 = els[0];
    if (e0.disabled || !els.some(visivel)) continue;
    if (e0.tagName === 'SELECT') {
      if (e0.options.length > 14) continue;
      const original = e0.value;
      for (const o of [...e0.options]) {
        if (o.value === original) continue;
        const antes = nomesVisiveis(), antesH = nomesHabilitados(); e0.value = o.value; e0.dispatchEvent(new Event('change', { bubbles: true })); await dormir(500);
        const dif = mudancas(antes, antesH); if (dif.aparecem.length || dif.somem.length || dif.habilitam.length || dif.desabilitam.length) estados.push({ gatilho: name, valor: o.value, texto: limpo(o.text), ...dif });
        regHab(name, o.value, limpo(o.text));
        e0.value = original; e0.dispatchEvent(new Event('change', { bubbles: true })); await dormir(250);
      }
    } else if (e0.type === 'radio') {
      const original = els.find((x) => x.checked);
      for (const r of els.filter((x) => visivel(x) && !x.checked)) {
        const antes = nomesVisiveis(), antesH = nomesHabilitados(); r.click(); await dormir(500);
        const dif = mudancas(antes, antesH); if (dif.aparecem.length || dif.somem.length || dif.habilitam.length || dif.desabilitam.length) estados.push({ gatilho: name, valor: r.value, texto: textoOpcao(r), ...dif });
        regHab(name, r.value, textoOpcao(r));
        if (original) { original.click(); await dormir(250); }
      }
    } else if (e0.type === 'checkbox') {
      for (const cb of els.filter((x) => visivel(x))) {
        const antes = nomesVisiveis(); const marcado = cb.checked; cb.click(); await dormir(500);
        const dif = diff(antes, nomesVisiveis()); if (dif.aparecem.length || dif.somem.length) estados.push({ gatilho: name, valor: cb.value, texto: textoOpcao(cb), marcando: !marcado, ...dif });
        if (cb.checked !== marcado) { cb.click(); await dormir(250); }
      }
    }
  }

  // Habilitações: o Lattes deixa campos (inclusive de outras abas) bloqueados até um radio/seleção ser escolhido. Independe de visibilidade (abas).
  const habilitadosTodos = () => new Set([...grupos.entries()].filter(([, els]) => els.some((x) => !x.disabled)).map(([n]) => n));
  const baseTodos = habilitadosTodos();
  for (const [name, els] of grupos) {
    const e0 = els[0];
    if (els.every((x) => x.disabled)) continue;
    const opcoesGat = e0.tagName === 'SELECT' ? (e0.options.length <= 14 ? [...e0.options].map((o) => ({ valor: o.value, texto: limpo(o.text) })) : []) : e0.type === 'radio' ? els.map((x) => ({ valor: x.value, texto: textoOpcao(x) })) : [];
    for (const op of opcoesGat) {
      if (e0.tagName === 'SELECT') { e0.value = op.valor; e0.dispatchEvent(new Event('change', { bubbles: true })); }
      else { const r = els.find((x) => x.value === op.valor); if (!r) continue; r.click(); }
      await dormir(450);
      const h = habilitadosTodos();
      const hab = [...h].filter((x) => !baseTodos.has(x) && x !== name).sort(), des = [...baseTodos].filter((x) => !h.has(x) && x !== name).sort();
      if (hab.length || des.length) habilitacoes.push({ gatilho: name, valor: op.valor, texto: op.texto, habilitam: hab, desabilitam: des });
    }
    // volta ao estado inicial deste gatilho
    const ini = e0.tagName === 'SELECT' ? null : els.find((x) => x.defaultChecked);
    if (ini) { ini.click(); await dormir(250); }
  }

  // Aceitação: o Lattes recusa (desmarca/limpa) certos valores enquanto outro campo não for escolhido, ou quando o valor não consta de um cadastro.
  // Testa se cada campo "pega"; para os que não pegam, procura qual opção de outro radio/seleção os libera (dependência) ou marca como controlado.
  const aceitacao = [];
  const gatilhosAcc = [...grupos.entries()].filter(([, els]) => (els[0].type === 'radio' || (els[0].tagName === 'SELECT' && els[0].options.length <= 14)) && !els.every((x) => x.disabled));
  const escolher = async (els, valor) => { const e0 = els[0]; if (e0.tagName === 'SELECT') { e0.value = valor; e0.dispatchEvent(new Event('change', { bubbles: true })); } else { const r = els.find((x) => x.value === valor); if (r) r.click(); } await dormir(400); };
  const valorAtual = (els) => { const e0 = els[0]; return e0.tagName === 'SELECT' ? e0.value : (els.find((x) => x.checked) || {}).value; };
  const pega = async (name, els) => {
    const e0 = els[0];
    if (e0.disabled || e0.readOnly || ['hidden', 'file', 'button', 'submit', 'checkbox'].includes(e0.type)) return null;
    if (e0.type === 'radio') {
      const alvo = els.find((x) => !x.checked && !x.disabled); if (!alvo) return null;
      const ant = els.find((x) => x.checked); alvo.click(); await dormir(400); const ok = alvo.checked;
      if (ant) { ant.click(); await dormir(250); } else if (ok) { alvo.checked = false; }
      return ok;
    }
    if (e0.tagName === 'SELECT') return null;
    // só 'input'/'keyup': change e blur disparam pesquisas do Lattes (ex.: a lupa do nome do orientando abre o currículo da pessoa e tira a página do lugar)
    const ant = e0.value; e0.value = 'ZZ'; e0.dispatchEvent(new Event('input', { bubbles: true })); e0.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'Z' })); await dormir(500);
    const ok = e0.value === 'ZZ'; e0.value = ant; e0.dispatchEvent(new Event('input', { bubbles: true })); return ok;
  };
  for (const [name, els] of grupos) {
    if (/^(nomeautor|nometitular|f_nome|f_tipo_privacidade)/i.test(name)) continue;
    let ok = null; try { ok = await pega(name, els); } catch (e) { ok = null; }
    if (ok !== false) continue;
    const deps = [];
    for (const [gname, gels] of gatilhosAcc) {
      if (gname === name) continue;
      const ini = valorAtual(gels);
      const opcoes = gels[0].tagName === 'SELECT' ? [...gels[0].options].map((o) => ({ valor: o.value, texto: limpo(o.text) })) : gels.map((x) => ({ valor: x.value, texto: textoOpcao(x) }));
      const valores = [];
      for (const op of opcoes) {
        if (op.valor === ini) continue;
        await escolher(gels, op.valor);
        let ok2 = null; try { ok2 = await pega(name, els); } catch (e) { ok2 = null; }
        if (ok2 === true) valores.push({ valor: op.valor, texto: op.texto });
      }
      if (ini !== undefined && ini !== null) await escolher(gels, ini);
      if (valores.length) deps.push({ gatilho: gname, valores });
    }
    aceitacao.push({ campo: name, pega_no_estado_inicial: false, depende: deps, controlado_ou_recusa: deps.length === 0 });
  }

  // Listas (grades): tabelas e *Holder, com colunas e links; e botões "Incluir novo item".
  const listas = [];
  d.querySelectorAll('table[id],[id$=Holder]').forEach((t) => {
    const cab = [...t.querySelectorAll('th')].map((x) => limpo(x.textContent)).filter(Boolean);
    const cel = cab.length ? cab : [...(t.rows && t.rows[0] ? t.rows[0].cells : [])].map((x) => limpo(x.textContent)).filter(Boolean);
    const links = [...t.querySelectorAll('a')].map((a) => limpo(a.textContent)).filter((x) => x && x.length < 40);
    listas.push({ id: t.id, colunas: cel, links: [...new Set(links)], visivel: visivel(t) });
  });
  const botoes = [...d.querySelectorAll('a,button,div,span')].filter((x) => x.children.length < 3 && /^incluir novo item$/i.test(limpo(x.textContent)) && visivel(x)).map((x) => ({ texto: limpo(x.textContent), antes: (textosPerto(x, -1, 1)[0] || '') }));
  const abas = [...d.querySelectorAll('#abas a, .abas a')].map((a) => ({ texto: limpo(a.textContent), titulo: limpo(a.getAttribute('title')) }));

  const saida = { item: meta.item, variante: meta.variante, variante_slug: meta.variante_slug, capturado_em: new Date().toISOString().slice(0, 10), abas, campos, estados, habilitacoes, aceitacao, listas, botoes_incluir: botoes, observacoes: meta.observacoes || [] };
  window.top.__ultimaCaptura = saida;
  const envio = await enviarCaptura(saida);
  return envio + ' | campos=' + campos.length + ' estados=' + estados.length + ' listas=' + listas.length;
}
window.top.__auditar = auditar; window.top.__enviarCaptura = enviarCaptura;
