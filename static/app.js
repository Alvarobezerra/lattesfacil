const FIELD_IDS = [
  "tipo_producao",
  "natureza",
  "instituicao_promotora",
  "local_evento",
  "periodico",
  "situacao_orientacao",
  "papel_orientacao",
  "tipo_mestrado",
  "nome_orientando",
  "instituicao_orient",
  "curso_orient",
  "titulo",
  "ano",
  "pais",
  "idioma",
  "meio_divulgacao",
  "homepage",
  "doi",
  "classificacao_evento",
  "nome_evento",
  "cidade_evento",
  "ano_evento",
  "titulo_anais",
  "pagina_inicial",
  "pagina_final",
  "volume",
  "fasciculo",
  "serie",
  "outras_informacoes",
  "isbn_issn",
  "editora",
  "cidade_editora",
  "area_conhecimento",
  "visibilidade",
];

const NATUREZAS = {
  anais: ["Resumo", "Resumo Expandido", "Completo"],
  apresentacao: ["Comunicação", "Conferência ou palestra", "Congresso", "Seminário", "Simpósio", "Outra"],
  artigo: null, // o formulário de artigo não tem natureza (fixa no Lattes)
  orientacao: [
    "Dissertação de mestrado",
    "Tese de doutorado",
    "Monografia de conclusão de curso de aperfeiçoamento/especialização",
    "Trabalho de conclusão de curso de graduação",
    "Iniciação Científica",
    "Supervisão de pós-doutorado",
    "Orientação de outra natureza",
  ],
};
const TIPO_INFO = {
  anais: {
    badge: "Trabalhos publicados em anais de eventos",
    guide: "Vá em <em>Produções → Trabalhos publicados em anais de eventos → Incluir novo item</em> para abrir o formulário.",
    bloco: "2. Evento e Publicação",
    issn: "ISBN / ISSN dos Anais",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["natureza", "titulo", "ano", "meio_divulgacao", "classificacao_evento", "nome_evento", "cidade_evento", "ano_evento", "titulo_anais", "pagina_inicial", "isbn_issn", "editora", "area_conhecimento"],
  },
  apresentacao: {
    badge: "Apresentação de trabalho e palestra",
    guide: "Vá em <em>Produções → Apresentação de trabalho e palestra → Incluir novo item</em> para abrir o formulário.",
    bloco: "2. Evento",
    issn: "ISBN / ISSN dos Anais",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["natureza", "titulo", "ano", "meio_divulgacao", "nome_evento", "instituicao_promotora", "cidade_evento", "area_conhecimento"],
  },
  artigo: {
    badge: "Artigos completos publicados em periódicos",
    guide: "Vá em <em>Produções → Artigos completos publicados em periódicos → Incluir novo item</em>, digite o DOI <strong>@DOI@</strong> na janela e confirme para abrir o formulário.",
    bloco: "2. Periódico",
    issn: "ISSN do periódico",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["titulo", "ano", "doi", "periodico", "isbn_issn", "volume", "pagina_inicial", "area_conhecimento"],
  },
  orientacao: {
    badge: "Orientações e supervisões",
    guide: "Vá em <em>Orientações → Orientações e supervisões concluídas (ou em andamento) → Incluir novo item</em> para abrir o formulário.",
    bloco: "2. Orientação",
    issn: "ISBN / ISSN dos Anais",
    ano: "Ano de término (em andamento: ano de início)",
    titulo: "Título do trabalho orientado",
    tracked: ["natureza", "titulo", "ano", "nome_orientando", "instituicao_orient", "curso_orient", "area_conhecimento"],
  },
};

function applyTipoProducao(tipo) {
  if (!TIPO_INFO[tipo]) tipo = "anais";
  $("tipo_producao").value = tipo;
  document.querySelectorAll("[data-tipos]").forEach((el) => {
    el.classList.toggle("type-hidden", !el.dataset.tipos.split(" ").includes(tipo));
  });
  const opcoes = NATUREZAS[tipo];
  if (opcoes) {
    const nat = $("natureza");
    const atual = nat.value;
    nat.innerHTML = "";
    opcoes.forEach((n) => {
      const o = document.createElement("option");
      o.value = n;
      o.textContent = n;
      nat.appendChild(o);
    });
    if (opcoes.includes(atual)) nat.value = atual;
  }
  const info = TIPO_INFO[tipo];
  $("tipoBadge").textContent = info.badge;
  $("blocoBTitulo").textContent = info.bloco;
  $("lblIsbn").textContent = info.issn;
  $("lblAno").childNodes[0].textContent = info.ano + " ";
  $("lblTitulo").childNodes[0].textContent = info.titulo + " ";
  $("guideStep2").innerHTML = info.guide.replace("@DOI@", ($("doi") && $("doi").value) || "do artigo");
}

let state = {
  autores: [],
  palavras_chave: [],
};

const $ = (id) => document.getElementById(id);

function showToast(msg) {
  const toast = $("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 2800);
}

function getFormData() {
  const data = {};
  FIELD_IDS.forEach((id) => {
    const el = $(id);
    if (el) data[id] = el.value.trim();
  });
  data.autores = [...state.autores];
  data.palavras_chave = [...state.palavras_chave];
  return data;
}

function setFormData(data, markEnrichedKeys = []) {
  applyTipoProducao(data.tipo_producao || "anais");
  FIELD_IDS.forEach((id) => {
    const el = $(id);
    if (!el || data[id] === undefined) return;
    el.value = data[id] || "";
    el.classList.remove("enriched-highlight");
    if (markEnrichedKeys.includes(id) && data[id]) {
      el.classList.add("enriched-highlight");
    }
  });
  if (Array.isArray(data.autores)) state.autores = data.autores;
  if (Array.isArray(data.palavras_chave)) state.palavras_chave = data.palavras_chave;
  applyTipoProducao($("tipo_producao").value); // atualiza o guia com o DOI já preenchido
  renderChips();
  updateCompleteness();
  updateBookmarklet();
}

function renderChips() {
  const authorsEl = $("authorsList");
  authorsEl.innerHTML = "";
  state.autores.forEach((a, idx) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    const num = document.createElement("strong");
    num.textContent = `${idx + 1}.`;
    const small = document.createElement("small");
    small.textContent = `(${a.citacao})`;
    const rm = document.createElement("button");
    rm.type = "button";
    rm.setAttribute("aria-label", "Remover");
    rm.textContent = "×";
    chip.append(num, ` ${a.nome} `, small, " ", rm);
    rm.onclick = () => {
      state.autores.splice(idx, 1);
      renderChips();
      updateCompleteness();
      updateBookmarklet();
    };
    authorsEl.appendChild(chip);
  });

  const kwEl = $("keywordsList");
  kwEl.innerHTML = "";
  state.palavras_chave.forEach((kw, idx) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    const rm = document.createElement("button");
    rm.type = "button";
    rm.setAttribute("aria-label", "Remover");
    rm.textContent = "×";
    chip.append(`${kw} `, rm);
    rm.onclick = () => {
      state.palavras_chave.splice(idx, 1);
      renderChips();
      updateCompleteness();
      updateBookmarklet();
    };
    kwEl.appendChild(chip);
  });
}

function updateCompleteness() {
  const tracked = TIPO_INFO[$("tipo_producao").value || "anais"].tracked;
  let filled = 0;
  tracked.forEach((id) => {
    const el = $(id);
    if (!el) return;
    if (el.value.trim()) {
      filled += 1;
      el.classList.remove("missing-highlight");
    } else {
      el.classList.add("missing-highlight");
    }
  });
  // orientações e artigos por DOI não têm grade de autores para preencher
  const contaAutores = !["orientacao", "artigo"].includes($("tipo_producao").value);
  if (contaAutores && state.autores.length > 0) filled += 1;
  if (state.palavras_chave.length > 0) filled += 1;

  const total = tracked.length + (contaAutores ? 2 : 1);
  const pct = Math.round((filled / total) * 100);
  $("progressFill").style.width = `${pct}%`;
  $("completenessText").textContent = `${filled} de ${total} campos principais preenchidos (${pct}%) — campos em amarelo estão pendentes.`;
}

// Script de preenchimento do formulário "Trabalhos publicados em anais de eventos" (pkg_trabalho.form).
// Nomes, valores e limites verificados no formulário real do Lattes em 15/11/2026.
// Regra: nunca clica em Salvar; o usuário confere e salva.
const AUTOFILL_TEMPLATE = String.raw`(async function () {
  var d = __DATA__;
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var norm = function (t) { return String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim().toLowerCase(); };
  function findDoc(w) {
    try { if (w.document.querySelector('[name="f_titulo"]') && (!w.frameElement || w.frameElement.offsetParent !== null)) return w.document; } catch (e) {}
    for (var i = 0; i < w.frames.length; i++) { var f = findDoc(w.frames[i]); if (f) return f; }
    return null;
  }
  var doc = findDoc(window);
  if (!doc) {
    alert('LattesFácil: formulário não encontrado. Abra Trabalhos publicados em anais de eventos > Incluir novo item e execute de novo.');
    return;
  }
  // Confere se o currículo aberto no Lattes é do usuário selecionado no LattesFácil antes de preencher qualquer coisa.
  var wanted = String(d.__usuario || '');
  var loggedName = '';
  try {
    var topDoc = window.top.document;
    var nameEl = topDoc.getElementById('nmeLt') || topDoc.querySelector('.dadosPrinc .nome');
    loggedName = nameEl ? nameEl.textContent.trim() : '';
  } catch (e) {}
  if (wanted) {
    var tok = function (s) { return norm(s).split(' ').filter(function (t) { return t && ['da', 'de', 'do', 'das', 'dos', 'e'].indexOf(t) < 0; }); };
    var wa = tok(wanted), lb = tok(loggedName);
    var same = wa.length > 0 && lb.length > 0 && wa[0] === lb[0] && wa[wa.length - 1] === lb[lb.length - 1] &&
      wa.every(function (t) { return lb.indexOf(t) >= 0; });
    if (!same) {
      alert('LattesFácil: o currículo aberto no Lattes é de "' + (loggedName || 'titular não identificado') + '", mas o usuário selecionado no LattesFácil é "' + wanted + '".\n\nNada foi preenchido. Troque o usuário no LattesFácil ou entre no Lattes com a conta correta.');
      return;
    }
  }
  try { var tp = window.top.opener || window.opener; if (tp && d.__origem) tp.postMessage({ type: 'lattesfacil-status', online: !!loggedName, name: loggedName }, d.__origem); } catch (e) {}
  var report = [];
  var fire = function (el) { ['input', 'change'].forEach(function (t) { el.dispatchEvent(new Event(t, { bubbles: true })); }); };
  var visible = function (el) { return el.offsetParent !== null; };

  function setVal(name, val) {
    if (!val) return;
    var el = doc.querySelector('[name="' + name + '"]');
    if (!el) { report.push('campo ausente: ' + name); return; }
    var v = String(val);
    if (el.maxLength > 0 && v.length > el.maxLength) { report.push(name + ' cortado em ' + el.maxLength + ' caracteres'); v = v.slice(0, el.maxLength); }
    el.value = v;
    fire(el);
  }
  function setRadio(name, value) {
    if (!value) return;
    var r = doc.querySelector('input[type="radio"][name="' + name + '"][value="' + value + '"]');
    if (!r) { report.push('opção ausente: ' + name + '=' + value); return; }
    r.checked = true; r.click();
  }
  function setSelect(name, value) {
    if (!value) return;
    var sel = doc.querySelector('select[name="' + name + '"]');
    if (!sel) { report.push('select ausente: ' + name); return; }
    sel.value = value; fire(sel);
    if (sel.value !== value) report.push('valor ausente em ' + name + ': ' + value);
  }
  function lookup(map, text, label) {
    var v = map[norm(text)];
    if (!v && text) report.push(label + ' sem correspondência: ' + text);
    return v;
  }

  var NATUREZA = { 'completo': '121', 'resumo': '122', 'resumo expandido': '123' };
  var TIPO_EVENTO = { 'internacional': 'I', 'nacional': 'N', 'regional': 'R', 'local': 'L' };
  var MEIO = { 'impresso': 'I', 'meio magnetico': 'M', 'meio digital': 'D', 'filme': 'F', 'hipertexto': 'H', 'outro': 'O', 'impresso e midia eletronica': 'V' };
  var PAIS = { 'brasil': 'BRA', 'portugal': 'POR' };
  var NAT_APRES = { 'comunicacao': '2J1', 'conferencia ou palestra': '2J2', 'congresso': '2J3', 'seminario': '2J4', 'simposio': '2J5', 'outra': '2J9' };
  var IDIOMA = { 'portugues': 'PT', 'ingles': 'EN', 'espanhol': 'ES', 'frances': 'FR', 'alemao': 'DE', 'italiano': 'IT' };

  var want = d.tipo_producao || 'anais';
  var have = doc.querySelector('[name="f_titulo_periodico"]') ? 'artigo' : (doc.querySelector('[name="f_nme_orient"]') ? 'orientacao' : (doc.querySelector('[name="f_nme_evento"]') ? 'apresentacao' : 'anais'));
  var NOMES = { anais: 'um Trabalho em anais', apresentacao: 'uma Apresentação de trabalho', artigo: 'um Artigo em periódico', orientacao: 'uma Orientação' };
  var CAMINHOS = { anais: 'Produções > Trabalhos publicados em anais de eventos', apresentacao: 'Produções > Apresentação de trabalho e palestra', artigo: 'Produções > Artigos completos publicados em periódicos', orientacao: 'Orientações > Orientações e supervisões concluídas (ou em andamento)' };
  if (want !== have) {
    alert('LattesFácil: este registro é ' + NOMES[want] + ', mas o formulário aberto é de ' + NOMES[have] + '. Abra ' + CAMINHOS[want] + ' > Incluir novo item e execute de novo.');
    return;
  }
  var isApres = want === 'apresentacao';
  if (want === 'artigo') {
    var winF = doc.defaultView;
    var msgs = [];
    try { winF.alert = function (m) { msgs.push(String(m)); }; } catch (e) {}
    var recuperou = false;
    var doiEl = doc.querySelector('[name="f_cod_doi"]');
    var tit0 = doc.querySelector('[name="f_titulo"]');
    if (d.doi && tit0 && tit0.value && doiEl && norm(doiEl.value) === norm(d.doi)) {
      recuperou = true; // o Lattes já recuperou os dados ao receber o DOI na janela inicial
    } else if (d.doi) {
      doiEl.value = d.doi; fire(doiEl);
      try { winF.call_doi(); } catch (e) { report.push('não consegui acionar a recuperação por DOI'); }
      var t0 = Date.now();
      while (Date.now() - t0 < 15000) {
        await sleep(500);
        var tt = doc.querySelector('[name="f_titulo"]');
        if ((tt && tt.value) || msgs.length) break;
      }
      msgs.forEach(function (m) { report.push('Lattes: ' + m); });
      var got = doc.querySelector('[name="f_titulo"]');
      recuperou = !!(got && got.value);
      if (!recuperou) report.push('o Lattes não recuperou os dados do DOI; usei os dados do LattesFácil');
    } else {
      report.push('sem DOI: escolha o periódico na lupa do Lattes');
    }
    if (!recuperou) {
      setVal('f_titulo', d.titulo); setVal('f_ano', d.ano);
      setSelect('F_IDIOMA', lookup(IDIOMA, d.idioma, 'idioma'));
      setSelect('f_meio', lookup(MEIO, d.meio_divulgacao, 'meio de divulgação'));
      setVal('f_issn', d.isbn_issn); setVal('f_volume', d.volume); setVal('f_serie', d.serie); setVal('f_pag_ini', d.pagina_inicial);
      if (d.periodico) report.push('periódico "' + d.periodico + '": escolha na lupa do Lattes (o campo é um cadastro controlado)');
    }
    var pf = doc.querySelector('[name="f_pag_fim"]');
    if (pf && !pf.value) setVal('f_pag_fim', d.pagina_final);
    setVal('f_homepage', d.homepage);
    setRadio('F_RELEV', 'N');
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', 'N');
    setVal('f_ref', d.outras_informacoes);
  } else if (want === 'orientacao') {
    var wnd = doc.defaultView;
    try { wnd.alert = function (m) { report.push('Lattes: ' + m); }; wnd.confirm = function () { return true; }; } catch (e) {}
    var topDoc2 = window.top.document;
    var normNome = function (t) { return norm(t).replace(/\s*\([a-z]{2}\)\s*$/, ''); };
    var normCurso = function (t) { return norm(t).replace(/\(\s*[0-9a-z]{8,}\s*\)\s*$/, '').trim(); };
    var waitFrame = async function (rx, ms) {
      var t1 = Date.now();
      while (Date.now() - t1 < ms) {
        var fr = [].slice.call(topDoc2.querySelectorAll('iframe')).filter(function (f) { return rx.test(f.src) && f.offsetParent !== null; })[0];
        if (fr && fr.contentDocument && fr.contentDocument.readyState === 'complete') return fr;
        await sleep(300);
      }
      return null;
    };
    var NAT_ORI = { 'dissertacao de mestrado': '41', 'tese de doutorado': '42', 'monografia de conclusao de curso de aperfeicoamento/especializacao': '43', 'trabalho de conclusao de curso de graduacao': '44', 'iniciacao cientifica': '45', 'supervisao de pos-doutorado': '46', 'orientacao de outra natureza': '49' };
    var andamento = d.situacao_orientacao === 'Em andamento';
    var primeiro = doc.querySelector('input[name="F_COD_PROD"]');
    var formAndamento = !!(primeiro && /^A/.test(primeiro.value));
    if (andamento !== formAndamento) {
      alert('LattesFácil: este registro é uma orientação ' + (andamento ? 'em andamento' : 'concluída') + ', mas o formulário aberto é de ' + (formAndamento ? 'em andamento' : 'concluídas') + '. Abra Orientações > Orientações e supervisões ' + (andamento ? 'em andamento' : 'concluídas') + ' > Incluir novo item.');
      return;
    }
    var cod = lookup(NAT_ORI, d.natureza, 'natureza');
    setRadio('F_COD_PROD', cod ? (andamento ? 'A' : '') + cod : '');
    await sleep(300);
    if (cod === '41' && d.tipo_mestrado) {
      try { wnd.atribui(d.tipo_mestrado === 'Profissional' ? '30#Profissional' : '29#Acadêmico'); } catch (e) { report.push('não consegui definir o tipo do mestrado'); }
    }
    if (cod === '41' || cod === '42') setRadio('f_tpo_orient', d.papel_orientacao === 'Coorientador' ? 'C' : 'O');
    setVal('f_titulo', d.titulo); setVal('f_ano', d.ano);
    setSelect('f_pais', lookup(PAIS, d.pais, 'país')); setSelect('F_IDIOMA', lookup(IDIOMA, d.idioma, 'idioma'));
    setVal('f_homepage', d.homepage); setRadio('F_RELEV', 'N'); setVal('f_nme_orient', d.nome_orientando);
    setRadio('F_BOLSA', 'N'); setVal('f_ref', d.outras_informacoes);
    // Instituição e curso são cadastros controlados do Lattes: buscamos e escolhemos o item de nome idêntico.
    if (cod && d.instituicao_orient) {
      wnd.sele_inst();
      var fi = await waitFrame(/prc_inst_form/, 8000);
      if (!fi) {
        report.push('a janela de instituições não abriu');
      } else {
        fi.contentDocument.querySelector('input[name="f_nome"]').value = d.instituicao_orient;
        try { fi.contentWindow.recuperaInstMacro(); } catch (e) {}
        await sleep(3500);
        var links = [].slice.call(fi.contentDocument.querySelectorAll('a')).filter(function (a) { return /seleciona\(/.test(a.getAttribute('href') || ''); });
        var achei = links.filter(function (a) { return normNome(a.textContent) === normNome(d.instituicao_orient); })[0];
        if (achei) { achei.click(); await sleep(1500); }
        else report.push('instituição "' + d.instituicao_orient + '" não encontrada no cadastro do Lattes' + (links.length ? ' (opções: ' + links.slice(0, 4).map(function (a) { return a.textContent.trim(); }).join('; ') + ')' : '') + '; escolha na lupa');
      }
      var instOk = !!((doc.querySelector('[name="f_cod_inst"]') || {}).value || (doc.querySelector('[name="f_cod_inst2"]') || {}).value);
      if (instOk && cod !== '46' && d.curso_orient) {
        wnd.curso();
        var fc = await waitFrame(/prc_curso_form/, 8000);
        if (!fc) {
          report.push('a janela de cursos não abriu');
        } else {
          var selc = fc.contentDocument.querySelector('select[name="f_curso"]');
          var opts2 = [].slice.call(selc.options);
          var alvo = normCurso(d.curso_orient);
          var oc = opts2.filter(function (o) { return normCurso(o.text) === alvo; })[0] || opts2.filter(function (o) { return alvo.length > 4 && normCurso(o.text).indexOf(alvo) >= 0; })[0];
          if (oc) { selc.value = oc.value; fc.contentWindow.selecionar(); await sleep(1500); }
          else report.push('curso "' + d.curso_orient + '" não encontrado para essa instituição e nível; escolha na lupa');
        }
      } else if (!instOk) {
        report.push('sem instituição escolhida não dá para escolher o curso');
      }
    }
  } else if (isApres) {
    setRadio('F_COD_PROD', lookup(NAT_APRES, d.natureza, 'natureza'));
    setVal('f_titulo', d.titulo);
    setVal('f_ano', d.ano);
    setSelect('f_pais', lookup(PAIS, d.pais, 'país'));
    setSelect('F_IDIOMA', lookup(IDIOMA, d.idioma, 'idioma'));
    setSelect('f_meio', lookup(MEIO, d.meio_divulgacao, 'meio de divulgação'));
    setVal('f_homepage', d.homepage);
    setRadio('F_RELEV', 'N');
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', 'N');
    setVal('f_nme_evento', d.nome_evento);
    setVal('f_inst', d.instituicao_promotora);
    setVal('f_local', d.local_evento);
    setVal('f_cidade', d.cidade_evento);
    setVal('f_ref', d.outras_informacoes);
  } else {
    setRadio('F_COD_PROD', lookup(NATUREZA, d.natureza, 'natureza'));
    setVal('f_cod_doi', d.doi);
    setVal('f_titulo', d.titulo);
    setVal('f_ano', d.ano);
    setSelect('f_pais', lookup(PAIS, d.pais, 'país'));
    setSelect('F_IDIOMA', lookup(IDIOMA, d.idioma, 'idioma'));
    setSelect('f_meio', lookup(MEIO, d.meio_divulgacao, 'meio de divulgação'));
    setVal('f_homepage', d.homepage);
    setRadio('F_RELEV', 'N');
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', 'N');
    setRadio('f_tipo_evento', lookup(TIPO_EVENTO, d.classificacao_evento, 'classificação do evento'));
    setVal('f_evento', d.nome_evento);
    setVal('f_cidade_evento', d.cidade_evento);
    setVal('f_ano_evento', d.ano_evento);
    setVal('f_titulo_pub', d.titulo_anais);
    setVal('f_volume', d.volume);
    setVal('f_fasciculo', d.fasciculo);
    setVal('f_serie', d.serie);
    setVal('f_pag_ini', d.pagina_inicial);
    setVal('f_pag_fim', d.pagina_final);
    setVal('f_isbn', String(d.isbn_issn || '').replace(/\D/g, ''));
    setVal('f_editora', d.editora);
    setVal('f_cidade_ed', d.cidade_editora);
    setVal('f_ref', d.outras_informacoes);
  }

  function gridLink(holderId, rx) {
    var holder = doc.getElementById(holderId);
    if (!holder) return null;
    return [].slice.call(holder.querySelectorAll('a')).filter(function (a) { return rx.test(a.textContent.trim()); })[0] || null;
  }
  function clickConfirm() {
    var c = [].slice.call(doc.querySelectorAll('a')).filter(function (a) { return /^confirmar$/i.test(a.textContent.trim()) && visible(a); });
    if (!c.length) return false;
    c[c.length - 1].click();
    return true;
  }

  var okAut = 0;
  var autores = d.autores || [];
  // Artigo recuperado por DOI: o Lattes importa os autores do DOI (não há grade para digitar) e liga o nome do
  // titular pelas "citações bibliográficas" do currículo.
  var autoresPeloDoi = want === 'artigo' && !gridLink('autorHolder', /^Incluir novo/);
  for (var i = 0; !autoresPeloDoi && i < autores.length; i++) {
    var link = gridLink('autorHolder', /^Incluir novo/);
    var nome = doc.getElementById('nomeAutor');
    var cita = doc.getElementById('nomeAutorComoCitado');
    if (!link) { report.push('grade de autores não encontrada'); break; }
    link.click(); await sleep(450);
    nome = doc.getElementById('nomeAutor'); cita = doc.getElementById('nomeAutorComoCitado');
    nome.value = String(autores[i].nome || '').slice(0, 60); cita.value = String(autores[i].citacao || '').slice(0, 60);
    fire(nome); fire(cita);
    if (clickConfirm()) okAut++; else report.push('não consegui confirmar o autor ' + autores[i].nome);
    await sleep(450);
  }

  var okKw = 0;
  var kws = d.palavras_chave || [];
  for (var k = 0; k < kws.length; k++) {
    var l2 = gridLink('palavraHolder', /^Incluir nova/);
    if (!l2) { report.push('grade de palavras-chave não encontrada'); break; }
    l2.click(); await sleep(450);
    var ins = [].slice.call(doc.querySelectorAll('input[type="text"]')).filter(function (x) { return !x.name && !x.id && visible(x) && x.maxLength === 50; });
    var inp = ins[ins.length - 1];
    if (!inp) { report.push('campo de palavra-chave não encontrado'); break; }
    inp.value = String(kws[k]).slice(0, 50); fire(inp);
    if (clickConfirm()) okKw++; else report.push('não consegui confirmar a palavra-chave ' + kws[k]);
    await sleep(450);
  }

  var okArea = 0;
  var areas = String(d.area_conhecimento || '').split(';').map(function (x) { return x.trim(); }).filter(Boolean);
  for (var m = 0; m < areas.length; m++) {
    var holder = doc.getElementById('areaHolder');
    if (!holder) { report.push('grade de áreas não encontrada'); break; }
    var ains = [].slice.call(holder.querySelectorAll('input[type="text"]')).filter(function (x) { return x.maxLength === 86; });
    var ainp = ains[ains.length - 1];
    if (!ainp) { report.push('campo de área não encontrado'); break; }
    ainp.focus(); ainp.value = areas[m];
    ['keydown', 'keypress', 'input', 'keyup'].forEach(function (t) { ainp.dispatchEvent(new KeyboardEvent(t, { bubbles: true, key: areas[m].slice(-1) })); });
    await sleep(1200);
    var box = ainp.parentElement.querySelector('.suggest-content');
    var opts = box ? [].slice.call(box.querySelectorAll('a')) : [];
    var hit = opts.filter(function (o) { return norm(o.textContent) === norm(areas[m]); })[0];
    if (hit) { hit.click(); okArea++; await sleep(600); }
    else { report.push('área sem correspondência exata no Lattes: ' + areas[m] + ' (escolha em Áreas)'); ainp.value = ''; }
  }

  var bodyTxt = '';
  try { bodyTxt = doc.body ? doc.body.innerText : ''; } catch (e) {}
  if (autoresPeloDoi) {
    report.push(/Nenhuma das op[cç][õo]es de formato do seu nome/i.test(bodyTxt)
      ? 'ATENÇÃO: o Lattes não reconheceu o nome do titular entre os autores do DOI. Confira o campo "Nome em citações bibliográficas" do currículo (o Lattes mostra a lista de autores do DOI na tela).'
      : 'autores importados do DOI pelo Lattes');
  }
  alert('LattesFácil: campos principais preenchidos. ' + (autoresPeloDoi ? 'Autores: do DOI; ' : (autores.length ? 'Autores: ' + okAut + '/' + autores.length + '; ' : '')) + 'palavras-chave: ' + okKw + '/' + kws.length + '; áreas: ' + okArea + '/' + areas.length + '.' +
    (report.length ? '\n\nAtenção:\n- ' + report.join('\n- ') : '') + '\n\nConfira tudo e clique em Salvar no Lattes.');
})();`;

function buildLattesAutofillScript(data) {
  // "<" escapado para o JSON nunca fechar uma tag script caso o texto seja colado em HTML
  const usuario = $("ownerName") ? $("ownerName").value : "";
  const payload = JSON.stringify({ ...data, __usuario: usuario, __origem: location.origin }).replace(/</g, "\\u003c");
  return AUTOFILL_TEMPLATE.replace("__DATA__", () => payload);
}

function updateBookmarklet() {
  const script = buildLattesAutofillScript(getFormData());
  $("bookmarkletLink").href = "javascript:" + encodeURIComponent(script);
}

function showFileAdded(file) {
  const el = $("fileAdded");
  const mb = (file.size / 1048576).toFixed(1);
  el.textContent = `✅ ${file.name} (${mb} MB) adicionado`;
  el.classList.remove("hidden");
  showToast(`Arquivo adicionado: ${file.name}`);
}

// Entrada única de arquivos: PDF curto = um resumo; PDF longo = caderno de anais (busca pelo usuário selecionado).
// Envio em pedaços de 1 MB: em conexões lentas (ex.: túnel) uma requisição longa é derrubada, uma curta não.
const UPLOAD_CHUNK = 1024 * 1024;

async function uploadChunks(file, onProgress) {
  const id = Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
  const n = Math.max(1, Math.ceil(file.size / UPLOAD_CHUNK));
  for (let i = 0; i < n; i += 1) {
    const blob = file.slice(i * UPLOAD_CHUNK, (i + 1) * UPLOAD_CHUNK);
    let ok = false;
    let motivo = "";
    for (let tentativa = 1; tentativa <= 4 && !ok; tentativa += 1) {
      try {
        const r = await fetch(`/api/upload/chunk?id=${id}&i=${i}&n=${n}&name=${encodeURIComponent(file.name)}`, {
          method: "POST",
          headers: { "Content-Type": "application/octet-stream" },
          body: blob,
        });
        if (r.ok) ok = true;
        else motivo = `erro ${r.status}`;
      } catch (e) {
        motivo = "sem conexão";
      }
      if (!ok) await new Promise((res) => setTimeout(res, 800 * tentativa));
    }
    if (!ok) throw new Error(`Falha ao enviar o trecho ${i + 1} de ${n} (${motivo}). Tente de novo.`);
    if (onProgress) onProgress((i + 1) / n, Math.min((i + 1) * UPLOAD_CHUNK, file.size));
  }
  return id;
}

function progressText(file) {
  return (frac, bytes) => {
    $("extractStatus").textContent = `Enviando "${file.name}": ${Math.round(frac * 100)}% (${(bytes / 1048576).toFixed(1)} de ${(file.size / 1048576).toFixed(1)} MB)...`;
  };
}

async function uploadEvidenceFile(file) {
  const statusEl = $("extractStatus");
  if (!/\.(pdf|txt)$/i.test(file.name)) {
    $("fileAdded").textContent = "❌ Envie um arquivo PDF.";
    $("fileAdded").classList.remove("hidden");
    showToast("Formato não aceito: envie um PDF.");
    return;
  }
  showFileAdded(file);
  statusEl.textContent = `Enviando "${file.name}"...`;
  statusEl.classList.remove("hidden");

  let json;
  let uploadId;
  try {
    uploadId = await uploadChunks(file, progressText(file));
    statusEl.textContent = `Lendo "${file.name}"...`;
    const resp = await fetch("/api/upload/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: uploadId, usuario: $("ownerName").value }),
    });
    json = await resp.json();
    if (!resp.ok) {
      statusEl.textContent = json.error || "Erro na extração.";
      return;
    }
  } catch (e) {
    statusEl.textContent = (e && e.message) || "Falha de conexão ao enviar o arquivo.";
    return;
  }
  if (json.caderno) {
    // PDF com várias páginas: é um caderno de resumos, então procuramos os trabalhos do usuário selecionado.
    cadernoFile = file;
    cadernoUploadId = uploadId;
    statusEl.textContent = `Arquivo com ${json.page_count} páginas: tratado como caderno de resumos. Procurando os resumos de ${$("ownerName").value}...`;
    searchCaderno();
    return;
  }
  cadernoFile = null;
  cadernoUploadId = null;
  $("cadernoResults").innerHTML = "";
  setFormData(json.extracted);
  const notes = (json.extracted.extraction_notes || []).join(" ");
  const kind = { apresentacao: "Certificado", artigo: "Artigo", orientacao: "Documento de orientação" }[json.extracted.tipo_producao] || "Resumo";
  statusEl.textContent = `${kind} lido de "${file.name}". ${notes || "Revise e clique em Buscar Dados Faltantes se necessário."}`;
  if (notes.includes("ATENÇÃO")) showToast("Atenção: o usuário selecionado não consta neste documento.");
}

async function extractFromRawText(text) {
  const statusEl = $("extractStatus");
  statusEl.textContent = "Analisando texto...";
  statusEl.classList.remove("hidden");

  const resp = await fetch("/api/extract", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, usuario: $("ownerName").value }),
  });
  const json = await resp.json();
  if (!resp.ok) {
    statusEl.textContent = json.error || "Erro na extração.";
    return;
  }
  setFormData(json.extracted);
  const n2 = (json.extracted.extraction_notes || []).join(" ");
  statusEl.textContent = `Dados extraídos do texto. ${n2 || "Use 'Buscar Dados Faltantes' para completar informações."}`;
  if (n2.includes("ATENÇÃO")) showToast("Atenção: o usuário selecionado não consta neste documento.");
}

async function enrichMissing() {
  const statusEl = $("enrichStatus");
  statusEl.textContent = "Consultando Crossref, OpenAlex e anais na web...";
  statusEl.classList.remove("hidden");

  const current = getFormData();
  const resp = await fetch("/api/enrich", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(current),
  });
  const json = await resp.json();
  const suggestions = json.suggestions || {};
  const keys = Object.keys(suggestions);

  if (keys.length === 0) {
    statusEl.textContent = "Nenhum dado adicional encontrado automaticamente nas bases externas.";
    return;
  }

  const merged = { ...current, ...suggestions };
  setFormData(merged, keys);
  statusEl.textContent = `Campos completados automaticamente (${keys.join(", ")}) via ${(json.sources || []).join(", ")}.`;
}

async function loadRecords() {
  const resp = await fetch("/api/records");
  const json = await resp.json();
  const records = json.records || [];
  $("recordsCount").textContent = records.length;
  const list = $("recordsList");
  list.innerHTML = "";
  if (records.length === 0) {
    list.innerHTML = `<p class="hint">Nenhum registro salvo ainda.</p>`;
    return;
  }
  records.forEach((rec) => {
    const item = document.createElement("div");
    item.className = "record-item";
    const info = document.createElement("div");
    const h4 = document.createElement("h4");
    h4.textContent = rec.titulo;
    const meta = document.createElement("div");
    meta.className = "record-meta";
    const who = document.createElement("strong");
    who.textContent = rec.owner;
    meta.append("Por ", who, ` • ${rec.data.ano || "s/ano"} • ${rec.data.nome_evento || "Evento não informado"}`);
    info.append(h4, meta);
    const btns = document.createElement("div");
    btns.style.cssText = "display:flex;gap:6px;";
    const btnLoad = document.createElement("button");
    btnLoad.type = "button";
    btnLoad.className = "btn btn-sm btn-primary";
    btnLoad.textContent = "Carregar";
    const btnDel = document.createElement("button");
    btnDel.type = "button";
    btnDel.className = "btn btn-sm btn-secondary";
    btnDel.textContent = "Excluir";
    btns.append(btnLoad, btnDel);
    item.append(info, btns);
    btnLoad.onclick = () => {
      setFormData(rec.data);
      $("historyPanel").classList.add("hidden");
      showToast("Registro carregado no formulário!");
    };
    btnDel.onclick = async () => {
      await fetch(`/api/records/${encodeURIComponent(rec.id)}`, { method: "DELETE" });
      loadRecords();
      showToast("Registro removido.");
    };
    list.appendChild(item);
  });
}

let cadernoFile = null;
let cadernoUploadId = null;

function loadCadernoRecord(r) {
  setFormData(r.record);
  const notes = (r.record.extraction_notes || []).join(" ");
  const st = $("extractStatus");
  st.textContent = `Resumo da pág. ${r.page_label || r.pdf_page} carregado. ${notes}`;
  st.classList.remove("hidden");
  showToast("Resumo carregado no formulário!");
  $("lattesForm").scrollIntoView({ behavior: "smooth" });
}

async function saveAllCaderno(resultados) {
  const owner = $("ownerName").value.trim() || "Convidado";
  let ok = 0;
  for (const r of resultados) {
    const resp = await fetch("/api/records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ owner, data: r.record }),
    });
    if (resp.ok) ok += 1;
  }
  showToast(`${ok} de ${resultados.length} resumo(s) salvos na lista compartilhada.`);
  loadRecords();
}

function cadernoDetail(r) {
  const rec = r.record;
  const card = document.createElement("div");
  card.className = "caderno-detail";
  const h4 = document.createElement("h4");
  h4.textContent = r.titulo;
  card.appendChild(h4);
  const rows = [
    ["Autores", (rec.autores || []).map((a) => `${a.nome} (${a.citacao})`).join("; ")],
    ["Palavras-chave", (rec.palavras_chave || []).join("; ")],
    ["Página", `${r.page_label || "?"} (PDF ${r.pdf_page})`],
    ["Evento", [rec.nome_evento, rec.cidade_evento, rec.ano_evento].filter(Boolean).join(" · ")],
    ["Anais", [rec.titulo_anais, rec.isbn_issn].filter(Boolean).join(" · ")],
    ["Idioma", rec.idioma],
    ["Área", rec.area_conhecimento || "não identificada"],
  ];
  const dl = document.createElement("dl");
  rows.forEach(([k, v]) => {
    const dt = document.createElement("dt");
    dt.textContent = k;
    const dd = document.createElement("dd");
    dd.textContent = v || "—";
    dl.append(dt, dd);
  });
  card.appendChild(dl);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn btn-sm btn-primary";
  btn.textContent = "Carregar no formulário";
  btn.onclick = () => loadCadernoRecord(r);
  card.appendChild(btn);
  return card;
}

function renderCadernoResults(json) {
  const box = $("cadernoResults");
  box.innerHTML = "";
  const resultados = json.resultados || [];
  const head = document.createElement("p");
  head.className = "hint";
  head.textContent = resultados.length
    ? `${resultados.length} resumo(s) encontrado(s) entre ${json.total_resumos} resumos do caderno (${json.paginas_pdf} páginas).`
    : `Nenhum resumo encontrado para esse nome entre ${json.total_resumos} resumos do caderno. Confira a grafia do nome.`;
  box.appendChild(head);
  if (!resultados.length) return;

  const tabs = document.createElement("div");
  tabs.className = "tabs";
  tabs.setAttribute("role", "tablist");
  const panel = document.createElement("div");
  panel.className = "tab-panel";
  panel.setAttribute("role", "tabpanel");

  const showAll = () => {
    panel.innerHTML = "";
    const bar = document.createElement("div");
    bar.className = "row-end";
    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "btn btn-sm btn-secondary";
    saveBtn.textContent = `💾 Salvar todos (${resultados.length})`;
    saveBtn.onclick = () => saveAllCaderno(resultados);
    bar.appendChild(saveBtn);
    panel.appendChild(bar);
    resultados.forEach((r, i) => {
      const item = document.createElement("div");
      item.className = "record-item";
      const info = document.createElement("div");
      const h4 = document.createElement("h4");
      h4.textContent = r.titulo;
      const meta = document.createElement("div");
      meta.className = "record-meta";
      meta.textContent = `Pág. ${r.page_label || "?"} (PDF ${r.pdf_page}) • ${r.autores.join(", ")}`;
      info.append(h4, meta);
      const open = document.createElement("button");
      open.type = "button";
      open.className = "btn btn-sm btn-primary";
      open.textContent = "Ver aba";
      open.onclick = () => select(i + 1);
      item.append(info, open);
      panel.appendChild(item);
    });
  };

  const buttons = [];
  const select = (idx) => {
    buttons.forEach((b, i) => {
      b.classList.toggle("active", i === idx);
      b.setAttribute("aria-selected", i === idx ? "true" : "false");
    });
    if (idx === 0) showAll();
    else {
      panel.innerHTML = "";
      panel.appendChild(cadernoDetail(resultados[idx - 1]));
    }
  };

  const labels = [`Todos (${resultados.length})`, ...resultados.map((r, i) => `Resumo ${i + 1} · pág. ${r.page_label || r.pdf_page}`)];
  labels.forEach((text, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "tab-btn";
    b.setAttribute("role", "tab");
    b.textContent = text;
    b.onclick = () => select(i);
    buttons.push(b);
    tabs.appendChild(b);
  });
  box.append(tabs, panel);
  select(resultados.length === 1 ? 1 : 0);
}

async function searchCaderno() {
  const statusEl = $("extractStatus");
  const nome = $("ownerName").value.trim();
  if (!cadernoFile || !nome) return;
  statusEl.textContent = `Procurando os resumos de "${nome}" em "${cadernoFile.name}"...`;
  statusEl.classList.remove("hidden");
  const buscar = () =>
    fetch("/api/caderno", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: cadernoUploadId, pesquisador: nome }),
    });
  try {
    if (!cadernoUploadId) cadernoUploadId = await uploadChunks(cadernoFile, progressText(cadernoFile));
    let resp = await buscar();
    if (resp.status === 410) {
      // o servidor já descartou o arquivo (30 min): reenvia uma vez
      cadernoUploadId = await uploadChunks(cadernoFile, progressText(cadernoFile));
      statusEl.textContent = `Procurando os resumos de "${nome}"...`;
      resp = await buscar();
    }
    const json = await resp.json();
    if (!resp.ok) {
      statusEl.textContent = json.error || "Erro ao ler o caderno.";
      return;
    }
    statusEl.textContent = `Caderno lido: ${json.meta.nome_evento || "evento não identificado"} ${json.meta.ano || ""}.`;
    renderCadernoResults(json);
  } catch (e) {
    statusEl.textContent = (e && e.message) || "Falha de conexão ao ler o caderno.";
  }
}

$("doi").addEventListener("input", () => {
  if ($("tipo_producao").value === "artigo") applyTipoProducao("artigo");
});
$("tipo_producao").addEventListener("change", () => {
  applyTipoProducao($("tipo_producao").value);
  updateCompleteness();
  updateBookmarklet();
});

// Event Listeners
// Usuário em teste: define quem está logado no LattesFácil (dono dos registros, autor buscado no caderno
// e titular esperado no Lattes). Guardado só neste navegador.
function applyUser(name, { persist = true } = {}) {
  $("ownerName").value = name;
  $("searchUser").textContent = name;
  $("guideUser").textContent = name;
  if (persist) {
    try { localStorage.setItem("lf-usuario", name); } catch (e) {}
  }
  $("cadernoResults").innerHTML = "";
  updateBookmarklet();
}
let initialUser = $("ownerName").options[0].value;
try {
  const savedUser = localStorage.getItem("lf-usuario");
  if (savedUser && [...$("ownerName").options].some((o) => o.value === savedUser)) initialUser = savedUser;
} catch (e) {}
applyUser(initialUser, { persist: false });
$("ownerName").addEventListener("change", () => {
  applyUser($("ownerName").value);
  showToast(`Usuário em teste: ${$("ownerName").value}`);
  if (cadernoFile) {
    $("extractStatus").textContent = `Procurando os resumos de ${$("ownerName").value} em "${cadernoFile.name}"...`;
    searchCaderno();
  }
});
$("btnPickFile").onclick = () => $("fileInput").click();
$("dropZone").onclick = (e) => {
  if (e.target.id !== "btnPickFile") $("fileInput").click();
};
$("fileInput").onchange = (e) => {
  if (e.target.files[0]) uploadEvidenceFile(e.target.files[0]);
};
$("dropZone").ondragover = (e) => {
  e.preventDefault();
  $("dropZone").classList.add("dragover");
};
$("dropZone").ondragleave = () => $("dropZone").classList.remove("dragover");
$("dropZone").ondrop = (e) => {
  e.preventDefault();
  $("dropZone").classList.remove("dragover");
  if (e.dataTransfer.files[0]) uploadEvidenceFile(e.dataTransfer.files[0]);
};

$("btnExtractText").onclick = () => {
  const txt = $("rawTextInput").value.trim();
  if (txt) extractFromRawText(txt);
};

$("btnLoadSample").onclick = () => {
  const sampleText = `XXXVI SEMINÁRIO DE INICIAÇÃO CIENTÍFICA E XVI SEMINÁRIO DE INICIAÇÃO AO DESENVOLVIMENTO TECNOLÓGICO E INOVAÇÃO
POTENCIAL DO MESOCARPO DE BABAÇU COMO INIBIDOR DA PEROXIDAÇÃO LIPÍDICA E DE ENZIMAS PRÓ-OXIDANTES
Aramys Silva Dos Reis¹
Caroline Chavier Pereira Santana²
RESUMO
Introdução: A progressão de algumas doenças está associada ao estresse oxidativo...
Palavras-chave: Babaçu. Peroxidação lipídica. In silico.
CIÊNCIAS BIOLÓGICAS
193`;
  $("rawTextInput").value = sampleText;
  extractFromRawText(sampleText);
};

$("btnEnrich").onclick = enrichMissing;

$("btnAddAuthor").onclick = () => {
  const val = $("newAuthorInput").value.trim();
  if (!val) return;
  const parts = val.split(/\s+/);
  const skip = new Set(["da", "de", "do", "das", "dos", "e"]);
  const cit = parts.length > 1
    ? `${parts[parts.length - 1].toUpperCase()}, ${parts.slice(0, -1).filter((p) => !skip.has(p.toLowerCase())).map((p) => p[0].toUpperCase() + ".").join(" ")}`
    : val.toUpperCase();
  state.autores.push({ nome: val, citacao: cit });
  $("newAuthorInput").value = "";
  renderChips();
  updateCompleteness();
  updateBookmarklet();
};

$("btnAddKeyword").onclick = () => {
  const val = $("newKeywordInput").value.trim();
  if (!val) return;
  state.palavras_chave.push(val);
  $("newKeywordInput").value = "";
  renderChips();
  updateCompleteness();
  updateBookmarklet();
};

document.querySelectorAll(".copy-btn").forEach((btn) => {
  btn.onclick = async () => {
    const target = $(btn.dataset.copy);
    if (!target || !target.value) return;
    await navigator.clipboard.writeText(target.value);
    showToast("Campo copiado!");
  };
});

FIELD_IDS.forEach((id) => {
  const el = $(id);
  if (el) {
    el.addEventListener("input", () => {
      updateCompleteness();
      updateBookmarklet();
    });
  }
});

$("btnSaveRecord").onclick = async () => {
  const owner = $("ownerName").value.trim() || "Convidado";
  const data = getFormData();
  const resp = await fetch("/api/records", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ owner, data }),
  });
  if (resp.ok) {
    showToast("Registro salvo na lista compartilhada!");
    loadRecords();
  }
};

const LATTES_URL = "https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form";
const LATTES_ORIGIN = "https://wwws.cnpq.br";
const LATTES_STALE_MS = 45000; // sem sinal do conector por esse tempo = estado incerto

// A nossa página não consegue ler a sessão do Lattes (sites diferentes). Quem informa o estado é o "conector",
// um script curto que roda na aba do Lattes e avisa esta página por postMessage a cada 15 s.
const CONNECTOR_TEMPLATE = String.raw`(function () {
  var ORIGIN = '__ORIGEM__';
  var SID = '__SID__';
  function nameOf() {
    try {
      var d = window.top.document;
      var e = d.getElementById('nmeLt') || d.querySelector('.dadosPrinc .nome');
      return e ? e.textContent.trim() : '';
    } catch (err) { return ''; }
  }
  function send(online, name) {
    // Canal 1: aba aberta pelo LattesFácil (window.opener). Canal 2: aviso ao servidor, funciona com qualquer aba.
    try { var t = window.top.opener || window.opener; if (t) t.postMessage({ type: 'lattesfacil-status', online: online, name: name }, ORIGIN); } catch (err) {}
    try {
      var img = new Image();
      img.src = ORIGIN + '/api/lattes/ping?sid=' + SID + '&online=' + (online ? 1 : 0) + '&name=' + encodeURIComponent(name || '') + '&t=' + Date.now();
    } catch (err) {}
  }
  if (window.__lfTimer) clearInterval(window.__lfTimer);
  var n = nameOf();
  send(!!n, n);
  window.__lfTimer = setInterval(function () { var x = nameOf(); send(!!x, x); }, 15000);
  window.addEventListener('pagehide', function () { send(false, ''); });
  alert(n ? 'LattesFácil conectado. Currículo aberto: ' + n : 'LattesFácil conectado, mas ainda não há currículo aberto. Faça login no Lattes; o status atualiza sozinho.');
})();`;

function getSid() {
  // Identifica este navegador junto ao servidor, para o aviso do conector chegar só a esta página.
  try {
    let s = localStorage.getItem("lf-sid");
    if (!s) {
      s = Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
      localStorage.setItem("lf-sid", s);
    }
    return s;
  } catch (e) {
    window.__lfSidMem = window.__lfSidMem || Math.random().toString(36).slice(2, 14);
    return window.__lfSidMem;
  }
}

function buildConnectorScript() {
  return CONNECTOR_TEMPLATE.replace("__ORIGEM__", () => location.origin).replace("__SID__", () => getSid());
}

const lattesState = { opened: false, online: false, name: "", last: 0 };

function nameTokens(s) {
  const skip = new Set(["da", "de", "do", "das", "dos", "e"]);
  return String(s || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .split(/\s+/)
    .filter((t) => t && !skip.has(t));
}

function sameLattesUser(wanted, logged) {
  const a = nameTokens(wanted);
  const b = nameTokens(logged);
  return a.length > 0 && b.length > 0 && a[0] === b[0] && a[a.length - 1] === b[b.length - 1] && a.every((t) => b.includes(t));
}

function renderLattesStatus() {
  const wanted = $("ownerName").value;
  const age = Date.now() - lattesState.last;
  let state = "off";
  let title = "Lattes: desconectado";
  let detail = "Nenhum sinal do Lattes ainda. Clique em Entrar no Lattes, faça o login e conecte.";
  if (lattesState.opened && !lattesState.last) {
    state = "wait";
    title = "Lattes: aguardando conexão";
    detail = "Aba do Lattes aberta. Faça o login lá e, no Console (F12) ou pelo favorito, rode o conector.";
  } else if (lattesState.last && age > LATTES_STALE_MS) {
    state = "wait";
    title = "Lattes: sem sinal";
    detail = "O conector parou de responder (aba fechada ou recarregada). Reconecte para confirmar.";
  } else if (lattesState.last && lattesState.online) {
    if (sameLattesUser(wanted, lattesState.name)) {
      state = "on";
      title = `Lattes: conectado como ${lattesState.name}`;
      detail = "Currículo confere com o usuário selecionado. Pode preencher.";
    } else {
      state = "mismatch";
      title = `Lattes: aberto como ${lattesState.name}`;
      detail = `Diferente do usuário selecionado (${wanted}). Troque o usuário aqui ou entre no Lattes com a conta correta.`;
    }
  } else if (lattesState.last && !lattesState.online) {
    state = "off";
    title = "Lattes: sem login";
    detail = "A aba do Lattes não tem currículo aberto. Faça o login (Login Único CNPq) nessa aba.";
  }
  const card = $("lattesConnect");
  card.className = `card lattes-connect state-${state}`;
  $("lcTitle").textContent = title;
  $("lcDetail").textContent = detail;
  const pill = $("lattesPill");
  pill.className = `lattes-pill state-${state}`;
  pill.textContent = { on: "● Lattes ON", mismatch: "● Lattes: outro usuário", wait: "● Lattes: aguardando", off: "● Lattes OFF" }[state];
}

function openLattesTab() {
  // Sem "noopener": a aba do Lattes precisa de window.opener para o conector avisar o status.
  window.open(LATTES_URL, "lattesfacil_lattes");
  lattesState.opened = true;
  renderLattesStatus();
}

window.addEventListener("message", (e) => {
  if (e.origin !== LATTES_ORIGIN) return; // só aceita sinais vindos do próprio Lattes
  const m = e.data;
  if (!m || m.type !== "lattesfacil-status") return;
  lattesState.opened = true;
  lattesState.online = !!m.online;
  lattesState.name = String(m.name || "").slice(0, 120);
  lattesState.last = Date.now();
  renderLattesStatus();
});

$("btnLoginLattes").onclick = async () => {
  openLattesTab();
  try {
    await navigator.clipboard.writeText(buildConnectorScript());
    showToast("Lattes aberto e conector copiado. Faça o login e cole o conector no Console (F12).");
  } catch (e) {
    showToast("Lattes aberto. Use 'Copiar conector' para copiar manualmente.");
  }
};
$("btnCopyConnector").onclick = async () => {
  try {
    await navigator.clipboard.writeText(buildConnectorScript());
    showToast("Conector copiado! Cole no Console (F12) da aba do Lattes.");
  } catch (e) {
    showToast("Não foi possível copiar automaticamente.");
  }
};
$("connectorLink").href = "javascript:" + encodeURIComponent(buildConnectorScript());
$("lattesPill").onclick = () => $("lattesConnect").scrollIntoView({ behavior: "smooth", block: "center" });
$("ownerName").addEventListener("change", renderLattesStatus);
setInterval(renderLattesStatus, 5000);

async function pollLattesStatus() {
  // Consulta o aviso que o conector deixou no servidor (funciona mesmo se a aba do Lattes não foi aberta por aqui).
  try {
    const r = await fetch("/api/lattes/status?sid=" + encodeURIComponent(getSid()), { cache: "no-store" });
    const j = await r.json();
    if (!j.seen) return;
    const when = Date.now() - j.age * 1000;
    if (when < lattesState.last) return; // já temos um sinal mais novo
    lattesState.opened = true;
    lattesState.online = !!j.online;
    lattesState.name = String(j.name || "");
    lattesState.last = when;
    renderLattesStatus();
  } catch (e) {}
}
setInterval(pollLattesStatus, 4000);
pollLattesStatus();

renderLattesStatus();

$("btnOpenLattes").onclick = async () => {
  const data = getFormData();
  if (!data.titulo) {
    showToast("Carregue ou preencha ao menos o título antes de enviar ao Lattes.");
    return;
  }
  // Abre a aba primeiro (dentro do clique) para o navegador não bloquear o pop-up.
  openLattesTab();
  $("lattesGuide").classList.remove("hidden");
  try {
    await navigator.clipboard.writeText(buildLattesAutofillScript(data));
    showToast("Lattes aberto em nova aba e script copiado! Siga o passo a passo.");
  } catch (e) {
    showToast("Lattes aberto. Use o botão 'Copiar Script' para copiar manualmente.");
  }
  $("lattesGuide").scrollIntoView({ behavior: "smooth", block: "center" });
};

$("btnCopyLattesScript").onclick = async () => {
  const script = buildLattesAutofillScript(getFormData());
  await navigator.clipboard.writeText(script);
  showToast("Script copiado! Cole no Console (F12) com o formulário do Lattes aberto.");
};

$("btnExportJson").onclick = () => {
  const blob = new Blob([JSON.stringify(getFormData(), null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "lattes-resumo.json";
  a.click();
};

$("btnToggleHistory").onclick = () => {
  $("historyPanel").classList.toggle("hidden");
  loadRecords();
};
$("btnCloseHistory").onclick = () => $("historyPanel").classList.add("hidden");

// Modal de Avaliação & Diagnóstico Lattes (Lattes Shield)
const auditModal = $("auditModal");
if ($("btnOpenAuditModal") && auditModal) {
  $("btnOpenAuditModal").onclick = () => {
    const user = $("ownerName") ? $("ownerName").value : "Aramys Silva dos Reis";
    if ($("auditModalUser")) $("auditModalUser").textContent = user;
    auditModal.classList.remove("hidden");
  };
  if ($("btnCloseAuditModal")) {
    $("btnCloseAuditModal").onclick = () => auditModal.classList.add("hidden");
  }
  auditModal.onclick = (e) => {
    if (e.target === auditModal) auditModal.classList.add("hidden");
  };
}

if ($("btnLoadRadarItem")) {
  $("btnLoadRadarItem").onclick = () => {
    if (auditModal) auditModal.classList.add("hidden");
    $("tipo_producao").value = "artigo";
    applyTipoProducao("artigo");
    if ($("titulo")) $("titulo").value = "IMPORTÂNCIA DO FARMACÊUTICO NO CUIDADO AO PACIENTE HIPERTENSO: UMA REVISÃO DE LITERATURA";
    if ($("doi")) $("doi").value = "10.29327/2239332.2.2-13";
    if ($("ano")) $("ano").value = "2023";
    if ($("idioma")) $("idioma").value = "Português";
    if ($("pais")) $("pais").value = "Brasil";
    if ($("meio_divulgacao")) $("meio_divulgacao").value = "meio digital";
    autores = ["Reis, Aramys Silva dos"];
    renderAutores();
    updateCompleteness();
    updateBookmarklet();
    showToast("✨ Artigo resgatado pelo Radar carregado no formulário! Clique em 'Buscar Dados Faltantes' para enriquecer.");
    const form = $("lattesForm");
    if (form) form.scrollIntoView({ behavior: "smooth", block: "start" });
  };
}

updateCompleteness();
updateBookmarklet();
loadRecords();
