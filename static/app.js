// Segurança: identificadores aleatórios criptográficos e volta ao login quando a sessão acabar.
function randomId(bytes = 16) {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return [...arr].map((b) => b.toString(16).padStart(2, "0")).join("");
}
const _fetchOriginal = window.fetch.bind(window);
window.fetch = async (...args) => {
  const resp = await _fetchOriginal(...args);
  if (resp.status === 401) window.location.href = "/login";
  return resp;
};
document.addEventListener("submit", (e) => e.preventDefault());

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
  "relevante",
  "bolsa",
  "agencia_financiadora",
  "f_sta_divulgacao_cientifica",
  "f_inovacao",
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
    guide: "Na tela inicial do Lattes logado, o sistema <strong>abre sozinho</strong> o formulário de <em>Trabalhos publicados em anais de eventos</em>.",
    bloco: "2. Evento e Publicação",
    issn: "ISBN / ISSN dos Anais",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["natureza", "titulo", "ano", "meio_divulgacao", "classificacao_evento", "nome_evento", "cidade_evento", "ano_evento", "titulo_anais", "pagina_inicial", "isbn_issn", "editora", "area_conhecimento"],
  },
  apresentacao: {
    badge: "Apresentação de trabalho e palestra",
    guide: "Na tela inicial do Lattes logado, o sistema <strong>abre sozinho</strong> o formulário de <em>Apresentação de trabalho e palestra</em>.",
    bloco: "2. Evento",
    issn: "ISBN / ISSN dos Anais",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["natureza", "titulo", "ano", "meio_divulgacao", "nome_evento", "instituicao_promotora", "cidade_evento", "area_conhecimento"],
  },
  artigo: {
    badge: "Artigos completos publicados em periódicos",
    guide: "Na tela inicial do Lattes logado, o sistema <strong>abre sozinho</strong> o formulário de <em>Artigos completos em periódicos</em> já recuperando o DOI <strong>@DOI@</strong>.",
    bloco: "2. Periódico",
    issn: "ISSN do periódico",
    ano: "Ano de Publicação",
    titulo: "Título do Trabalho",
    tracked: ["titulo", "ano", "doi", "periodico", "isbn_issn", "volume", "pagina_inicial", "area_conhecimento"],
  },
  orientacao: {
    badge: "Orientações e supervisões",
    guide: "Na tela inicial do Lattes logado, o sistema <strong>abre sozinho</strong> o formulário de <em>Orientações e supervisões</em>.",
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
    if (!el) return;
    if (el.type === "checkbox") {
      data[id] = el.checked ? "S" : "N";
    } else {
      data[id] = el.value.trim();
    }
  });
  data.f_sta_divulgacao_cientifica = $("f_sta_divulgacao_cientifica") && $("f_sta_divulgacao_cientifica").checked ? "S" : "N";
  data.f_inovacao = $("f_inovacao") && $("f_inovacao").checked ? "S" : "N";
  data.autores = [...state.autores];
  data.palavras_chave = [...state.palavras_chave];
  return data;
}

function revelarPassos(modo) {
  // modo: "doc" | "manual" | "form". Os passos seguintes só aparecem depois da escolha do Passo 1.
  const up = $("stepUpload");
  if (modo === "doc" || modo === "manual") {
    up.classList.remove("hidden");
    up.classList.toggle("modo-manual", modo === "manual");
  }
  if (modo === "form") {
    $("stepRevisao").classList.remove("hidden");
    $("lattesForm").classList.remove("hidden");
  }
}

function setFormData(data, markEnrichedKeys = []) {
  revelarPassos("form");
  applyTipoProducao(data.tipo_producao || "anais");
  FIELD_IDS.forEach((id) => {
    const el = $(id);
    if (!el || data[id] === undefined) return;
    if (el.type === "checkbox") {
      el.checked = data[id] === "S" || data[id] === true;
    } else {
      el.value = data[id] || "";
    }
    el.classList.remove("enriched-highlight");
    if (markEnrichedKeys.includes(id) && data[id]) {
      el.classList.add("enriched-highlight");
    }
  });
  if ($("f_sta_divulgacao_cientifica")) {
    $("f_sta_divulgacao_cientifica").checked = data.f_sta_divulgacao_cientifica === "S" || data.divulgacao_cientifica === "S" || data.f_sta_divulgacao_cientifica === true;
  }
  if ($("f_inovacao")) {
    $("f_inovacao").checked = data.f_inovacao === "S" || data.inovacao === "S" || data.f_inovacao === true;
  }
  if (Array.isArray(data.autores)) state.autores = data.autores;
  if (Array.isArray(data.palavras_chave)) state.palavras_chave = data.palavras_chave;
  applyTipoProducao($("tipo_producao").value); // atualiza o guia com o DOI já preenchido
  renderChips();
  updateCompleteness();
  if (typeof updateComplianceUI === "function") updateComplianceUI();
  updateBookmarklet();
  updateStandardizedDossieName();
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
  // Silencia alert/confirm/prompt do Lattes em TODAS as janelas e quadros enquanto preenche: um alerta nativo (ex.: "DOI n\u00e3o encontrado.")
  // trava a p\u00e1gina e o preenchimento. As mensagens s\u00e3o guardadas e entram no relat\u00f3rio final; as fun\u00e7\u00f5es originais voltam no fim.
  try { if (window.top.__lfRestaurarAlertas) window.top.__lfRestaurarAlertas(); } catch (e) {}
  var lfAvisosLattes = [];
  var lfSilenciados = [];
  var lfSilenciar = function (w, prof) {
    if (prof > 6) return;
    try {
      if (!w.__lfSilencio) {
        lfSilenciados.push({ w: w, a: w.alert, c: w.confirm, p: w.prompt });
        w.alert = function (m) { lfAvisosLattes.push(String(m).replace(/\s+/g, ' ').slice(0, 300)); };
        w.confirm = function () { return true; };
        w.prompt = function () { return ''; };
        w.__lfSilencio = true;
      }
      for (var i = 0; i < w.frames.length; i++) lfSilenciar(w.frames[i], prof + 1);
    } catch (e) {}
  };
  var lfTimerAlertas = setInterval(function () { lfSilenciar(window.top, 0); }, 150);
  var lfRestaurar = function () {
    clearInterval(lfTimerAlertas);
    lfSilenciados.forEach(function (r) { try { r.w.alert = r.a; r.w.confirm = r.c; r.w.prompt = r.p; delete r.w.__lfSilencio; } catch (e) {} });
    lfSilenciados = [];
  };
  lfSilenciar(window.top, 0);
  try { window.top.__lfRestaurarAlertas = lfRestaurar; } catch (e) {}
  setTimeout(lfRestaurar, 600000);
  // O Lattes responde alguns alertas depois (consulta de DOI, validações assíncronas): mantém o silêncio por mais alguns segundos antes do aviso final.
  // Com d.__semAlerta (testes/automação) o relatório fica em window.top.__lfUltimoRelatorio e nenhum diálogo é aberto.
  var lfAlerta = async function (m) {
    await sleep(4000);
    lfRestaurar();
    if (d.__semAlerta) { try { window.top.__lfUltimoRelatorio = String(m); } catch (e) {} return; }
    alert(m);
  };
  function findDoc(w) {
    try { if (w.document.querySelector('[name="f_titulo"]') && (!w.frameElement || w.frameElement.offsetParent !== null)) return w.document; } catch (e) {}
    for (var i = 0; i < w.frames.length; i++) { var f = findDoc(w.frames[i]); if (f) return f; }
    return null;
  }
  function formTypeOf(dc) {
    if (!dc) return '';
    if (dc.querySelector('[name="f_titulo_periodico"]')) return 'artigo';
    if (dc.querySelector('[name="f_nme_orient"]')) return 'orientacao';
    if (dc.querySelector('[name="f_nme_evento"]')) return 'apresentacao';
    return 'anais';
  }
  function findCvCode(topDoc) {
    try {
      var el = topDoc.querySelector('[name="f_cod"]');
      if (el && el.value) return el.value.trim();
      var html = topDoc.documentElement ? topDoc.documentElement.innerHTML : '';
      var m = html.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i);
      if (m) return m[1];
    } catch (e) {}
    return '';
  }
  // Confere se o currículo aberto no Lattes é do usuário selecionado no LattesData antes de abrir ou preencher qualquer coisa.
  var wanted = String(d.__usuario || '');
  var loggedName = '';
  try {
    var topDoc = window.top.document;
    var nameEl = topDoc.getElementById('nmeLt') || topDoc.querySelector('.dadosPrinc .nome');
    loggedName = nameEl ? nameEl.textContent.trim() : '';
  } catch (e) {}
  if (wanted && loggedName) {
    var tok = function (s) { return norm(s).split(' ').filter(function (t) { return t && ['da', 'de', 'do', 'das', 'dos', 'e'].indexOf(t) < 0; }); };
    var wa = tok(wanted), lb = tok(loggedName);
    var same = wa.length > 0 && lb.length > 0 && wa[0] === lb[0] && wa[wa.length - 1] === lb[lb.length - 1] &&
      wa.every(function (t) { return lb.indexOf(t) >= 0; });
    if (!same) {
      lfAlerta('LattesData: o currículo aberto no Lattes é de "' + (loggedName || 'titular não identificado') + '", mas o usuário selecionado no LattesData é "' + wanted + '".\n\nNada foi preenchido. Troque o usuário no LattesData ou entre no Lattes com a conta correta.');
      return;
    }
  }
  try { var tp = window.top.opener || window.opener; if (tp && d.__origem) tp.postMessage({ type: 'lattesfacil-status', online: !!loggedName, name: loggedName }, d.__origem); } catch (e) {}
  var STOPW = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'a', 'o'];
  var toks = function (s) { return norm(s).replace(/[^a-z0-9 ]/g, ' ').split(' ').filter(function (t) { return t && STOPW.indexOf(t) < 0; }); };
  if (d.tipo_producao === 'generico') {
    var G = d.__generico || {};
    var pagina = String(G.url || '').split('?')[0].toLowerCase();
    // Formulários com subtipo no endereço (orientação concluída x em andamento, tipos de projeto): só reaproveita o aberto se for do mesmo subtipo.
    var mesmoSubtipo = function (src) {
      var m = /[?&](f_tipo|f_cod_tipo)=([^&]*)/i.exec(String(G.url || ''));
      if (!m) return true;
      var m2 = new RegExp('[?&]' + m[1] + '=([^&]*)', 'i').exec(src);
      return !!m2 && m2[1].toLowerCase() === m[2].toLowerCase();
    };
    var achaQuadro = function (w) {
      var lista = [];
      try { lista = [].slice.call(w.document.querySelectorAll('iframe')); } catch (e) {}
      for (var i = 0; i < lista.length; i++) {
        try {
          var cd = lista[i].contentDocument;
          if (cd && lista[i].offsetParent !== null && String(lista[i].src || '').toLowerCase().indexOf(pagina) >= 0 && cd.readyState === 'complete' && mesmoSubtipo(String(lista[i].src || ''))) return cd;
          var sub = lista[i].contentWindow && achaQuadro(lista[i].contentWindow);
          if (sub) return sub;
        } catch (e) {}
      }
      return null;
    };
    var gdoc = achaQuadro(window.top);
    if (!gdoc) {
      var cvG = findCvCode(window.top.document);
      var modalG = window.top.modalCV2;
      // Artigo aberto pelo periódico: o Lattes só abre o formulário depois de validar ISSN, nome e dados obrigatórios na janela "Informar dados".
      // Repete as mesmas verificações (os mesmos serviços do Lattes) e, se o Lattes recusaria, avisa em vez de abrir um formulário vazio.
      if (G.id === 'artigo' && /F_CTR=FIV/.test(String(G.url))) {
        var qsL = function (k) { var m = new RegExp('[?&]' + k + '=([^&]*)').exec(String(G.url)); return m ? unescape(m[1]) : ''; };
        var baseL = window.top.location.pathname.replace(/[^/]*$/, '');
        var postL = function (u, data) { try { var x = new XMLHttpRequest(); x.open('POST', baseL + u, false); x.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); x.send(data); return x.responseText.replace(/\s+/g, ' ').trim(); } catch (e) { return ''; } };
        var nomeP = qsL('F_TITULO_PERIODICO'), issnP = qsL('F_ISSN'), volP = qsL('F_VOLUME'), pagP = qsL('F_PAG_INI'), probsP = [];
        // Sem ISSN: faz a busca por nome do próprio Lattes (lista de periódicos cadastrados) e usa o ISSN só se houver um periódico de nome idêntico.
        if (!issnP && nomeP) {
          try {
            var cvQ = cvG;
            var nomeSemAc = nomeP.normalize('NFD').replace(/[̀-ͯ]/g, '');
            var linhasQ = [];
            // A busca por nome do Lattes só aceita UMA palavra (nome com espaço volta vazio): busca palavra por palavra, das mais longas
            // para as mais curtas (até 3), e filtra pelo nome idêntico, como o usuário faria na janela do Lattes.
            var palavrasQ = nomeSemAc.split(/\s+/).filter(function (w) { return w.length >= 3 && !/^(de|da|do|das|dos|the|of|and)$/i.test(w); })
              .sort(function (x, y) { return y.length - x.length; }).slice(0, 3);
            for (var pq = 0; pq < palavrasQ.length; pq++) {
              var xq = new XMLHttpRequest();
              xq.open('GET', baseL + 'pkg_artigo.find_periodico?p_str=' + encodeURIComponent(palavrasQ[pq]) + '&p_tipo=nome&p_cod=' + cvQ, false);
              xq.send();
              var reQ = /selecionar\('([^']*)','([^']*)'\)/g, mQ;
              while ((mQ = reQ.exec(xq.responseText))) { if (mQ[1]) linhasQ.push({ issn: mQ[1].replace('-', '').toUpperCase(), nome: mQ[2] }); }
              if (linhasQ.some(function (l) { return norm(l.nome) === norm(nomeSemAc); })) break;
            }
            var exatos = linhasQ.filter(function (l) { return norm(l.nome) === norm(nomeSemAc); });
            var issnsExatos = exatos.map(function (l) { return l.issn; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
            if (issnsExatos.length === 1) {
              issnP = issnsExatos[0];
              G.url = String(G.url).replace(/([?&]F_ISSN=)[^&]*/, '$1' + issnP);
            } else if (issnsExatos.length > 1) {
              probsP.push('há mais de um periódico com esse nome no cadastro do Lattes (' + issnsExatos.slice(0, 5).join(', ') + '); informe o ISSN');
            } else if (linhasQ.length) {
              var vistosQ = [];
              linhasQ.forEach(function (l) { var s = l.nome + ' (' + l.issn + ')'; if (vistosQ.indexOf(s) < 0) vistosQ.push(s); });
              probsP.push('nenhum periódico com nome idêntico no cadastro do Lattes; opções parecidas: ' + vistosQ.slice(0, 5).join('; ') + '; informe o ISSN do correto');
            } else {
              probsP.push('o periódico não consta no cadastro do Lattes pelo nome; informe o ISSN');
            }
          } catch (eq) { probsP.push('não consegui consultar o cadastro de periódicos do Lattes; informe o ISSN'); }
        }
        if (!nomeP) probsP.push('nome do periódico não informado');
        if (!issnP) { if (!probsP.length) probsP.push('ISSN não informado'); }
        else if (!/^\d{7}[\dXx]$/.test(issnP)) probsP.push('ISSN fora do formato 9999-999X');
        else if (postL('prc_valida_issn', 'f_issn=' + issnP) === 'INVALIDO') probsP.push('ISSN não consta no cadastro de periódicos do Lattes');
        else if (nomeP && postL('pkg_artigo.valida_nome_issn_periodico', 'f_nome=' + escape(nomeP.normalize('NFD').replace(/[̀-ͯ]/g, '')) + '&f_issn=' + issnP) === 'DIF') probsP.push('o nome do periódico não confere com o ISSN no cadastro do Lattes');
        if (!volP) probsP.push('volume não informado');
        if (!pagP) probsP.push('página inicial não informada');
        if (probsP.length) { lfAlerta('LattesData: o Lattes não abriria o formulário deste artigo: ' + probsP.join('; ') + '. Corrija no LattesData (periódico, ISSN, volume, página inicial) ou informe o DOI.'); return; }
      }
      // O Lattes só abre o formulário do artigo de forma confiável logo depois de carregar a lista de artigos (a lista prepara o estado no servidor;
      // sem ela alguns formulários abriam sem os dados do periódico). Carrega a lista antes, como o usuário faria pelo menu.
      var listaPrepG = { artigo: 'pkg_artigo.lista', anais: 'pkg_trabalho.lista', apresentacao: 'prc_tec_demais_lista?f_cod_tipo=2J&f_cod=', orientacao_concluida: 'pkg_orient.lista?f_tipo=C&f_cod=', orientacao_andamento: 'pkg_orient.lista?f_tipo=A&f_cod=' }[G.id];
      // A lista do item vem do spec (G.lista); o mapa fixo acima fica de reserva.
      if (G.lista && !listaPrepG) listaPrepG = String(G.lista).replace(/[?&]f_cod=<codigo_do_cv>/, '') + (String(G.lista).indexOf('?') < 0 ? '?f_cod=' : '&f_cod=');
      if (listaPrepG && cvG && modalG && typeof modalG.setarUrl === 'function') {
        modalG.setarUrl(listaPrepG + (listaPrepG.indexOf('?') < 0 ? '?f_cod=' : '') + cvG, true);
        await sleep(4000);
      }
      if (cvG && modalG && typeof modalG.setarUrl === 'function' && pagina) {
        modalG.setarUrl(String(G.url).replace('<codigo_do_cv>', cvG), true);
        var tG = Date.now();
        while (Date.now() - tG < 15000 && !gdoc) { await sleep(400); gdoc = achaQuadro(window.top); }
        // O formulário do artigo ainda se monta (e limpa campos) depois de "complete": espera mais antes de preencher (conferido em 21/11/2026).
        if (gdoc) await sleep((G.id === 'artigo' || G.id === 'anais' || G.id === 'apresentacao' || G.id === 'orientacao_concluida' || G.id === 'orientacao_andamento') ? 3500 : 600);
        // Artigo pelo periódico: o Lattes consulta serviços externos (Crossref) ao abrir e, quando falham, abre o formulário sem os dados
        // do periódico. Detecta e reabre (lista + formulário) até 2 vezes.
        if (gdoc && G.id === 'artigo' && /F_CTR=FIV/.test(String(G.url))) {
          for (var tentA = 0; tentA < 2; tentA++) {
            var tpA = gdoc.querySelector('[name="f_titulo_periodico"]');
            var autHA = gdoc.getElementById('autorHolder');
            var precisaAut = !!((G.grades || {}).autores || []).length;
            if (tpA && tpA.value && (!precisaAut || (autHA && autHA.querySelector('a')))) break;  // dados do periódico e, se há autores a incluir, a grade de autores montada
            gdoc = null;
            modalG.setarUrl('pkg_artigo.lista?f_cod=' + cvG, true);
            await sleep(4000);
            modalG.setarUrl(String(G.url).replace('<codigo_do_cv>', cvG), true);
            var tG2 = Date.now();
            while (Date.now() - tG2 < 15000 && !gdoc) { await sleep(400); gdoc = achaQuadro(window.top); }
            if (gdoc) await sleep(3500);
          }
          var tpB = gdoc ? gdoc.querySelector('[name="f_titulo_periodico"]') : null;
          if (gdoc && !(tpB && tpB.value)) lfAvisosLattes.push('O Lattes abriu o formulário sem os dados do periódico (serviço do Lattes instável); feche o formulário e execute de novo.');
          else if (gdoc && ((G.grades || {}).autores || []).length && !(gdoc.getElementById('autorHolder') && gdoc.getElementById('autorHolder').querySelector('a'))) lfAvisosLattes.push('O Lattes montou o formulário sem a grade de autores (serviço do Lattes instável); feche o formulário e execute de novo.');
        }
      }
    }
    if (!gdoc) { lfAlerta('LattesData: não consegui abrir o formulário "' + (G.item || '') + '". Abra: ' + (G.como_abrir || '') + ' e execute de novo. Se o Lattes voltou para a tela inicial (sessão expirada), entre de novo no currículo.'); return; }
    var rel = [];
    var fireG = function (el) { ['input', 'change'].forEach(function (t) { el.dispatchEvent(new Event(t, { bubbles: true })); }); };
    var ok = 0;
    var gw = gdoc.defaultView;
    // alert/confirm do formulário já são silenciados e coletados em lfAvisosLattes (todas as janelas); lá entram no relatório, com os avisos sem efeito filtrados.
    try { gw.confirm = function () { return true; }; } catch (e) {}
    // Cadastro controlado (instituição, agência, curso, periódico): se o Lattes oferecer sugestões ao digitar, escolhe a
    // de nome idêntico ou claramente parecido (melhor()); ambíguo ou sem correspondência: não escolhe e pede escolha manual.
    var gControladoRx = /^(f_inst|f_nme_inst|f_nme_agencia|f_curso|f_titulo_periodico|f_nme_periodico|f_orgao)$/i;
    var gControlado = async function (inp, alvo, rotulo) {
      inp.focus();
      ['keydown', 'keypress', 'input', 'keyup'].forEach(function (ev) { inp.dispatchEvent(new KeyboardEvent(ev, { bubbles: true, key: alvo.slice(-1) })); });
      var opts = [];
      for (var w = 0; w < 4 && !opts.length; w++) {
        await sleep(w ? 700 : 1000);
        var box = inp.parentElement && inp.parentElement.querySelector('.suggest-content');
        opts = box ? [].slice.call(box.querySelectorAll('a')) : [];
      }
      if (!opts.length) return; // campo livre ou sem sugestões: fica o texto digitado
      var hit = melhor(opts, alvo, function (o) { return o.textContent; });
      if (hit) { hit.click(); await sleep(500); }
      else { rel.push(rotulo + ': "' + alvo + '" sem correspondência única nas sugestões do Lattes — escolha manual'); }
    };
    // Instituição e curso desabilitados no formulário: o valor só entra pela lupa do Lattes (grava também o código oculto).
    // Abre a janela, pesquisa pelo texto do documento (nome completo, depois sigla/iniciais/nome sem prefixo) e escolhe o
    // resultado claro e único. Nunca digita em campo desabilitado; sem resultado, deixa a lupa aberta e avisa.
    var gTopDoc = window.top.document;
    var gFrame = async function (rx, ms) {
      var t1 = Date.now();
      while (Date.now() - t1 < ms) {
        var fr = [].slice.call(gTopDoc.querySelectorAll('iframe')).filter(function (f) { return rx.test(f.src) && f.offsetParent !== null; })[0];
        if (fr && fr.contentDocument && fr.contentDocument.readyState === 'complete' && !/^about:blank/.test(String(fr.contentDocument.location.href))) return fr;
        await sleep(300);
      }
      return null;
    };
    var gNormNome = function (t) { return norm(t).replace(/(\s*\([^)]*\))+\s*$/, ''); };  // ignora a sigla e a UF no fim do nome: "... do Maranhao (FAPEMA) (MA)"
    var gNormCurso = function (t) { return norm(t).replace(/\(\s*[0-9a-z]*[0-9][0-9a-z]*\s*\)\s*$/, '').replace(/^(programa de pos-graduacao|pos-graduacao|curso de)\s+(em\s+)?/, '').trim(); };
    var gVariacoes = function (nome) {
      var v = [nome];
      var sg = /\(([A-Za-z]{2,12})\)/.exec(nome);
      if (sg) v.push(sg[1]);
      var base = nome.replace(/\s*\([^)]*\)\s*/g, ' ').trim();
      var ini = base.split(/\s+/).filter(function (w) { return !/^(d[aeo]s?|e)$/i.test(w); }).map(function (w) { return w.charAt(0); }).join('').toUpperCase();
      if (ini.length >= 3 && ini.length <= 8) v.push(ini);
      var sem = base.replace(/^universidade\s+(federal|estadual|municipal)?\s*(d[aeo]s?\s+)?/i, '').trim();
      if (sem.length > 3) v.push(sem);
      var mu = /^universidade\s+(federal|estadual)\s+(?:d[aeo]s?\s+)?([a-zà-ÿ]{4,})$/i.exec(base);  // UFMA = UF + 2 primeiras letras do estado
      if (mu) v.push((/^f/i.test(mu[1]) ? 'UF' : 'UE') + mu[2].slice(0, 2).toUpperCase());
      // A busca da lupa só acha nomes por termos curtos: nomes longos (ex.: fundações de amparo) entram pelas palavras mais distintivas do nome;
      // a escolha continua exigindo o nome idêntico ou um resultado único e claro.
      base.split(/\s+/).filter(function (w) { return w.length >= 6 && !/^(universidade|fundacao|fundação|instituto|federal|estadual|ciencia|ciência)$/i.test(w); })
        .sort(function (x, y) { return y.length - x.length; }).slice(0, 3).forEach(function (w) { v.push(w); });
      return v.filter(function (x, i) { return x && v.indexOf(x) === i; });
    };
    // Pesquisa na lupa e espera o resultado de forma adaptativa (o resultado para de mudar) até o limite; mede o tempo.
    var gPesquisarLupa = async function (fi, termo, maxMs, rxHref) {
      var fnome = fi.contentDocument.querySelector('input[name="f_nome"]');
      if (!fnome || typeof fi.contentWindow.recuperaInstMacro !== 'function') return { links: [], ms: 0, erro: 'campo de busca da lupa não encontrado' };
      var lerLinks = function () { return [].slice.call(fi.contentDocument.querySelectorAll('a')).filter(function (a) { return (rxHref || /seleciona\(/).test(a.getAttribute('href') || ''); }); };
      var antes = lerLinks().map(function (a) { return a.textContent; }).join('|');
      fnome.value = termo;
      var t0 = Date.now();
      try { fi.contentWindow.recuperaInstMacro(); } catch (e) { return { links: [], ms: Date.now() - t0, erro: 'a busca da lupa falhou' }; }
      var ult = -1, estavel = 0, links = [];
      while (Date.now() - t0 < maxMs) {
        await sleep(300);
        links = lerLinks();
        var mudou = links.map(function (a) { return a.textContent; }).join('|') !== antes;
        if (mudou && links.length === ult) { if (++estavel >= 2) break; } else { estavel = 0; }
        ult = links.length;
      }
      return { links: links, ms: Date.now() - t0, erro: '' };
    };
    // Guarda o que a lupa devolveu (nome + argumentos do link) para o banco de instituições; o app envia ao servidor.
    var gRegLupa = function (termo, links, ms, origem, erro) {
      try {
        var tp = window.top;
        tp.__lfInstLote = tp.__lfInstLote || [];
        tp.__lfInstLote.push({ termo: termo, origem: origem, ms: ms, erro: erro || '', itens: links.slice(0, 300).map(function (a) {
          var m = /seleciona\(([^)]*)\)/.exec(a.getAttribute('href') || '');
          return { nome: a.textContent.trim().slice(0, 200), ref: m ? m[1].slice(0, 200) : '' };
        }) });
      } catch (e) {}
    };
    var gCodInst = function () { return !!((gdoc.querySelector('[name="f_cod_inst"]') || {}).value || (gdoc.querySelector('[name="f_cod_inst2"]') || {}).value); };
    var gLupaInst = async function (nome, rotulo) {
      if (typeof gw.sele_inst !== 'function') { rel.push(rotulo + ': a lupa de instituições não existe neste formulário; escolha manual'); return false; }
      gw.sele_inst();
      var fi = await gFrame(/prc_inst_form|pp_lista_inst/, 8000);
      if (!fi) { rel.push(rotulo + ': a janela de instituições não abriu; escolha na lupa'); return false; }
      var vistas = [];
      var tent = gVariacoes(nome);
      for (var ti = 0; ti < tent.length; ti++) {
        var pq = await gPesquisarLupa(fi, tent[ti], 3500);
        if (pq.erro) break;
        var links = pq.links;
        gRegLupa(tent[ti], links, pq.ms, 'uso');
        var achei = melhor(links, gNormNome(nome), function (a) { return gNormNome(a.textContent); });
        if (achei) { achei.click(); await sleep(1500); if (gCodInst()) return true; }
        links.forEach(function (a) { var x = a.textContent.trim(); if (vistas.indexOf(x) < 0) vistas.push(x); });
      }
      rel.push(rotulo + ': "' + nome + '" não identificada com segurança no cadastro do Lattes' + (vistas.length ? ' (opções: ' + vistas.slice(0, 4).join('; ') + ')' : '') + '; a janela da lupa ficou aberta para você escolher');
      return false;
    };
    // Agência financiadora: o Lattes não aceita o nome digitado ("Utilize o link para selecionar a agência"). O link chama agencia(), que marca
    // "Com bolsa? sim" e abre a lista (prc_agencia) com todas as agências; escolhe pela sigla ou pelo nome idêntico, só se for único.
    var gLupaAgencia = async function (nome, rotulo) {
      if (typeof gw.agencia !== 'function') { rel.push(rotulo + ': a lupa de agências não existe neste formulário; escolha manual'); return false; }
      gw.agencia();
      var fa = await gFrame(/prc_agencia/, 8000);
      var linksA = [];
      for (var ta = 0; ta < 10 && fa && !linksA.length; ta++) {
        linksA = [].slice.call(fa.contentDocument.querySelectorAll('a')).filter(function (a) { return /atribuir\(/.test(a.getAttribute('onclick') || ''); });
        if (!linksA.length) await sleep(500);
      }
      if (!linksA.length) { rel.push(rotulo + ': a lista de agências não abriu; escolha na lupa'); return false; }
      var alvoA = norm(nome);
      var semSigla = function (x) { return norm(x).replace(/^\([^)]*\)\s*/, ''); };
      var porSigla = linksA.filter(function (a) { var m = /^\(([^)]*)\)/.exec(a.textContent.trim()); return m && norm(m[1]) === alvoA; });
      var iguais = linksA.filter(function (a) { return semSigla(a.textContent) === alvoA; });
      var cand = porSigla.length === 1 ? porSigla : iguais.length === 1 ? iguais : linksA.filter(function (a) { return alvoA.length > 3 && norm(a.textContent).indexOf(alvoA) >= 0; });
      if (cand.length === 1) { cand[0].click(); await sleep(1500); return !!((gdoc.querySelector('[name="f_nme_agencia"]') || {}).value); }
      rel.push(rotulo + ': "' + nome + '" ' + (cand.length ? 'tem mais de uma agência parecida (' + cand.slice(0, 4).map(function (a) { return a.textContent.trim().slice(0, 50); }).join('; ') + ')' : 'não consta na lista de agências do Lattes') + '; a janela ficou aberta para você escolher');
      return false;
    };
    var gLupaCurso = async function (nome, rotulo) {
      if (!gCodInst()) { rel.push(rotulo + ': sem instituição escolhida não dá para escolher o curso; use a lupa'); return false; }
      if (typeof gw.curso !== 'function') { rel.push(rotulo + ': a lupa de cursos não existe neste formulário; escolha manual'); return false; }
      gw.curso();
      var fc = await gFrame(/prc_curso_form/, 8000);
      var selc = fc && fc.contentDocument.querySelector('select[name="f_curso"]');
      if (!selc) { rel.push(rotulo + ': a janela de cursos não abriu; escolha na lupa'); return false; }
      var opts2 = [].slice.call(selc.options).filter(function (o) { return o.value; });
      var alvoC = gNormCurso(nome);
      var nivel = (G.campos || []).map(function (x) { return norm(x.valor); }).join(' ');
      var dica = /doutor/.test(nivel) ? 'doutorado' : /mestr/.test(nivel) ? 'mestrado' : /especializ|aperfeicoamento/.test(nivel) ? 'especializacao' : /gradua/.test(nivel) ? 'graduacao' : '';
      var oc = opts2.filter(function (o) { return gNormCurso(o.text) === alvoC; })[0] || null;
      if (!oc) {
        var cand = alvoC.length > 4 ? opts2.filter(function (o) { return norm(o.text).indexOf(alvoC) >= 0; }) : [];
        if (cand.length > 1 && dica) { var porNivel = cand.filter(function (o) { return norm(o.text).indexOf(dica) >= 0; }); if (porNivel.length) cand = porNivel; }
        oc = cand.length === 1 ? cand[0] : (cand.length ? null : melhor(opts2, alvoC, function (o) { return gNormCurso(o.text); }));
        if (!oc && cand.length > 1) { rel.push(rotulo + ': "' + nome + '" tem mais de uma opção no Lattes (' + cand.slice(0, 4).map(function (o) { return o.text.trim(); }).join('; ') + '); a janela da lupa ficou aberta para você escolher'); return false; }
      }
      if (oc) { selc.value = oc.value; fc.contentWindow.selecionar(); await sleep(1500); return true; }
      rel.push(rotulo + ': "' + nome + '" não encontrado para essa instituição e nível; a janela da lupa ficou aberta para você escolher');
      return false;
    };
    // Órgão/Unidade (projetos): campo desabilitado; a lupa abre a hierarquia de órgãos da instituição já escolhida. Escolhe o nome
    // idêntico/claramente parecido entre os níveis visíveis; sem correspondência única, deixa a janela aberta para escolha manual.
    var gNormOrgao = function (t) { return norm(t).replace(/\s*-\s*[a-z]{2}\s*$/, '').replace(/\s*\([^)]*\)\s*/g, ' ').trim(); };
    var gLupaOrgao = async function (nome, rotulo) {
      if (!gCodInst()) { rel.push(rotulo + ': sem instituição escolhida não dá para escolher o órgão; use a lupa'); return false; }
      if (typeof gw.orgao !== 'function') { rel.push(rotulo + ': a lupa de órgãos não existe neste formulário; escolha manual'); return false; }
      gw.orgao();
      var fo = await gFrame(/orgao/i, 8000);
      if (!fo) { rel.push(rotulo + ': a janela de órgãos não abriu; escolha na lupa'); return false; }
      await sleep(600);
      var nomes = [].slice.call(fo.contentDocument.querySelectorAll('a')).filter(function (a) { return a.textContent.trim() && !/cadastrar/i.test(a.textContent); });
      var alvoO = gNormOrgao(nome);
      var achou = nomes.filter(function (a) { return gNormOrgao(a.textContent) === alvoO; })[0] || melhor(nomes, alvoO, function (a) { return gNormOrgao(a.textContent); });
      if (!achou) {
        // O Lattes costuma ter só o centro/campus (ex.: "Centro de Ciências Sociais, Saúde e Tecnologia (CCSST) - Imperatriz"), não a
        // coordenação do documento: se uma única opção contém a palavra distintiva do nome (a cidade, p.ex. "imperatriz"), usa-a e avisa.
        var parasO = alvoO.split(' ').filter(function (t) { return t.length >= 6 && !/^(centro|ciencias|campus|coordenacao|departamento|universidade|federal|curso|faculdade|instituto|programa)$/.test(t); });
        var porPalavra = nomes.filter(function (a) { var n2 = gNormOrgao(a.textContent); return parasO.some(function (t) { return n2.indexOf(t) >= 0; }); });
        if (porPalavra.length === 1) { achou = porPalavra[0]; rel.push(rotulo + ': escolhi "' + achou.textContent.trim() + '" por conter "' + parasO.filter(function (t) { return gNormOrgao(achou.textContent).indexOf(t) >= 0; })[0] + '" (o Lattes não tem "' + nome + '"); confira'); }
        else if (porPalavra.length > 1) { rel.push(rotulo + ': mais de um órgão parecido (' + porPalavra.slice(0, 4).map(function (a) { return a.textContent.trim(); }).join('; ') + '); a janela da lupa ficou aberta para você escolher'); return false; }
      }
      if (achou) { achou.click(); await sleep(1200); return true; }
      rel.push(rotulo + ': "' + nome + '" não está entre os órgãos visíveis da instituição no Lattes (a hierarquia pode exigir descer níveis ou cadastrar novo órgão); a janela da lupa ficou aberta para você escolher');
      return false;
    };
    // Coleta gradual do cadastro de instituições: só pesquisa na lupa (não preenche nada), com intervalo e teto vindos do app.
    var gColeta = async function (C) {
      var termos = (C.termos || []).slice(0, 25);
      var feitos = 0, erros = 0;
      var fim = function (o) { try { window.top.__lfInstFim = o; } catch (e) {} };
      if (typeof gw.sele_inst !== 'function') { fim({ ok: false, erro: 'a lupa de instituições não existe neste formulário', feitos: 0, total: termos.length }); return; }
      gw.sele_inst();
      var fi = await gFrame(/prc_inst_form|pp_lista_inst/, 8000);
      if (!fi) { fim({ ok: false, erro: 'a janela de instituições não abriu', feitos: 0, total: termos.length }); return; }
      for (var i = 0; i < termos.length; i++) {
        var pq = await gPesquisarLupa(fi, termos[i], 6000);
        if (pq.erro) { gRegLupa(termos[i], [], pq.ms, 'coleta', pq.erro); if (++erros >= 2) break; }
        else { gRegLupa(termos[i], pq.links, pq.ms, 'coleta'); feitos++; }
        if (i < termos.length - 1) await sleep(Math.max(2000, Number(C.intervalo_ms) || 4000));
      }
      fim({ ok: true, feitos: feitos, erros: erros, total: termos.length });
    };
    if (G.coleta) { await gColeta(G.coleta); return; }
    for (var gi = 0; gi < (G.campos || []).length; gi++) {
      var c = G.campos[gi];
      if (c.valor === '' || c.valor === undefined || c.valor === null || c.valor === false) {
        // campo cuja lista o Lattes monta a partir de outro (ex.: tipo da participação depende da forma): escolhe a opção mais próxima
        var selA = c.auto && c.tipo === 'select' ? gdoc.querySelector('select[name="' + c.name + '"]') : null;
        if (selA) {
          var opsA = [].slice.call(selA.options).filter(function (o) { return o.value; });
          for (var wA = 0; wA < 4 && !opsA.length; wA++) { await sleep(400); opsA = [].slice.call(selA.options).filter(function (o) { return o.value; }); }
          var refA = (G.campos || []).filter(function (x) { return x.name === c.auto_de; })[0];
          var escA = (refA && refA.valor && melhor(opsA, refA.valor, function (o) { return o.text; })) || opsA.filter(function (o) { return refA && refA.valor && norm(o.text).indexOf(norm(refA.valor)) >= 0; })[0] || opsA[0];
          if (escA) { selA.value = escA.value; fireG(selA); ok++; rel.push('"' + (c.rotulo || c.name) + '" escolhido automaticamente: ' + escA.text + ' (confira)'); }
          else if (opsA.length) rel.push('não consegui escolher: ' + (c.rotulo || c.name));
        }
        continue;
      }
      var alvo = [].slice.call(gdoc.querySelectorAll('[name="' + c.name + '"]'));
      if (!alvo.length) { rel.push('campo ausente no Lattes: ' + (c.rotulo || c.name)); continue; }
      if ((c.tipo === 'text' || !c.tipo) && /^(f_inst|f_curso|f_orgao)$/i.test(c.name) && alvo[0].disabled) {
        var okL = /^f_inst$/i.test(c.name) ? await gLupaInst(String(c.valor), c.rotulo || c.name) : /^f_orgao$/i.test(c.name) ? await gLupaOrgao(String(c.valor), c.rotulo || c.name) : await gLupaCurso(String(c.valor), c.rotulo || c.name);
        if (okL) ok++;
        continue;
      }
      if ((c.tipo === 'text' || !c.tipo) && /^f_nme_agencia$/i.test(c.name)) {
        if (c.valor && await gLupaAgencia(String(c.valor), c.rotulo || c.name)) ok++;
        continue;
      }
      if (c.tipo === 'radio') {
        var rd = alvo.filter(function (x) { return x.value === c.codigo || norm(x.value) === norm(c.valor); })[0];
        if (rd) { rd.checked = true; rd.click(); ok++; } else rel.push('opção não encontrada: ' + (c.rotulo || c.name) + ' = ' + c.valor);
      } else if (c.tipo === 'checkbox' && c.codigos && c.codigos.length) {
        var marcadosC = 0;
        c.codigos.forEach(function (cod) {
          var cb = alvo.filter(function (x) { return x.value === cod; })[0];
          if (cb) { if (!cb.checked) cb.click(); marcadosC++; } else rel.push('opção não encontrada: ' + (c.rotulo || c.name) + ' = ' + cod);
        });
        if (marcadosC) ok++;
      } else if (c.tipo === 'checkbox') {
        alvo[0].checked = true; fireG(alvo[0]); ok++;
      } else if (c.tipo === 'select') {
        var sel = alvo[0];
        var ops = [].slice.call(sel.options);
        var op = (c.codigo ? ops.filter(function (o) { return o.value === c.codigo; })[0] : null) || ops.filter(function (o) { return norm(o.text) === norm(c.valor); })[0] || melhor(ops, c.valor, function (o) { return o.text; });
        if (op) { sel.value = op.value; fireG(sel); ok++; } else rel.push('opção não encontrada ou ambígua: ' + (c.rotulo || c.name) + ' = ' + c.valor + ' — escolha manual');
      } else {
        var t = alvo[0];
        var v = String(c.valor);
        if (t.maxLength > 0 && v.length > t.maxLength) { rel.push((c.rotulo || c.name) + ' cortado em ' + t.maxLength + ' caracteres'); v = v.slice(0, t.maxLength); }
        t.value = v; fireG(t); ok++;
        if (c.controlado || gControladoRx.test(c.name)) await gControlado(t, v, c.rotulo || c.name);
      }
      await sleep(c.tipo === 'radio' ? 700 : 250);
    }
    // Grades (palavras-chave, áreas, setores, autores): descobertas pelo próprio formulário aberto (elementos "*Holder").
    var GR = G.grades || {};
    var gVis = function (e) { return e.offsetParent !== null; };
    var gHolder = function (rx) { return [].slice.call(gdoc.querySelectorAll('[id$="Holder"]')).filter(function (h) { return rx.test(h.id); })[0] || null; };
    var gLink = function (h, rx) { return h ? ([].slice.call(h.querySelectorAll('a')).filter(function (a) { return rx.test(a.textContent.trim()); })[0] || null) : null; };
    var gConfirmar = function () {
      var c = [].slice.call(gdoc.querySelectorAll('a')).filter(function (a) { return /^confirmar$/i.test(a.textContent.trim()) && gVis(a); });
      if (!c.length) return false;
      c[c.length - 1].click(); return true;
    };
    // Pop-up de inclusão (Palavra-chave, Autor...): o campo está acima do link Confirmar visível, fora das grades.
    var gCampoDoPopup = function () {
      var cs = [].slice.call(gdoc.querySelectorAll('a')).filter(function (a) { return /^confirmar$/i.test(a.textContent.trim()) && gVis(a); });
      var el = cs[cs.length - 1];
      for (var k = 0; el && k < 8; k++) {
        el = el.parentElement;
        if (!el) break;
        var f = [].slice.call(el.querySelectorAll('input[type="text"]')).filter(function (x) { return gVis(x) && !x.closest('[id$="Holder"]'); })[0];
        if (f) return f;
      }
      return null;
    };
    // Falhou no meio: fecha o pop-up para não deixar o formulário travado para as grades seguintes.
    var gCancelarPopup = function () {
      var c = [].slice.call(gdoc.querySelectorAll('a')).filter(function (a) { return /^cancelar$/i.test(a.textContent.trim()) && gVis(a); });
      if (c.length) { try { c[c.length - 1].click(); } catch (e) {} }
    };
    var gOk = {};
    var gTexto = async function (chave, rotuloGrade, rxHolder, rxNovo, campoVisivel) {
      var lista = GR[chave] || [];
      if (!lista.length) return;
      var h = gHolder(rxHolder);
      if (!h) { rel.push('grade "' + rotuloGrade + '" não encontrada no formulário aberto'); return; }
      gOk[chave] = 0;
      for (var i = 0; i < lista.length; i++) {
        if (norm(gHolder(rxHolder).textContent).indexOf(norm(String(lista[i]))) >= 0) { gOk[chave]++; continue; } // já está na lista (preenchimento repetido)
        var lk = gLink(gHolder(rxHolder), rxNovo);
        if (!lk) { rel.push('botão de incluir em "' + rotuloGrade + '" não encontrado'); break; }
        lk.click(); await sleep(450);
        // "Incluir nova" abre um pop-up ("Inclusão de palavra chave") FORA da grade; o campo dele fica acima do Confirmar visível.
        // O campo de dentro da grade é só a busca da lista: digitar nele deixava o pop-up vazio e o Lattes recusava.
        var inp = null;
        for (var tw = 0; !inp && tw < 8; tw++) { inp = gCampoDoPopup(); if (!inp) await sleep(300); }
        if (!inp) {
          var ins = [].slice.call(gHolder(rxHolder).querySelectorAll('input[type="text"]')).filter(gVis);
          inp = ins[ins.length - 1];
        }
        if (!inp) { rel.push('campo de "' + rotuloGrade + '" não apareceu'); gCancelarPopup(); break; }
        var v = String(lista[i]);
        if (inp.maxLength > 0 && v.length > inp.maxLength) { rel.push(rotuloGrade + ' cortado em ' + inp.maxLength + ' caracteres: ' + v); v = v.slice(0, inp.maxLength); }
        inp.value = v; fireG(inp);
        if (gConfirmar()) gOk[chave]++; else { rel.push('não consegui confirmar em "' + rotuloGrade + '": ' + v); gCancelarPopup(); }
        await sleep(450);
      }
    };
    var gSugestao = async function (chave, rotuloGrade, rxHolder) {
      var lista = GR[chave] || [];
      if (!lista.length) return;
      gOk[chave] = 0;
      for (var i = 0; i < lista.length; i++) {
        var h = gHolder(rxHolder);
        if (!h) { rel.push('grade "' + rotuloGrade + '" não encontrada no formulário aberto'); break; }
        if (norm(h.textContent).indexOf(norm(String(lista[i]))) >= 0) { gOk[chave]++; continue; } // já está na lista
        // O campo da grade vem com um texto de dica ("Digite, selecione ou inclua uma nova área..."): vazio ou dica = livre.
        var ins = [].slice.call(h.querySelectorAll('input[type="text"]')).filter(function (x) { return gVis(x) && (!x.value || /^digite/i.test(x.value)); });
        var inp = ins[ins.length - 1];
        if (!inp) { rel.push('campo de "' + rotuloGrade + '" não encontrado'); break; }
        var alvo = String(lista[i]);
        inp.focus(); inp.value = alvo;
        ['keydown', 'keypress', 'input', 'keyup'].forEach(function (t) { inp.dispatchEvent(new KeyboardEvent(t, { bubbles: true, key: alvo.slice(-1) })); });
        await sleep(1200);
        var box = inp.parentElement.querySelector('.suggest-content');
        var opts = box ? [].slice.call(box.querySelectorAll('a')) : [];
        if (!opts.length) { await sleep(1500); box = inp.parentElement.querySelector('.suggest-content'); opts = box ? [].slice.call(box.querySelectorAll('a')) : []; }
        var hit = melhor(opts, alvo, function (o) { return o.textContent; });
        if (hit) { hit.click(); gOk[chave]++; await sleep(600); }
        else { rel.push(rotuloGrade + ': sem correspondência exata no Lattes para "' + alvo + '" — escolha manual na aba'); inp.value = ''; }
      }
    };
    // Projetos: a coluna Coordenador da lista de pesquisadores vira um "sim/não" ao clicar na célula da linha do pesquisador.
    var gCoordenador = async function (nome, citacao) {
      var h = gHolder(/autor/i);
      if (!h) return false;
      var tk = toks(nome), ult = tk.length ? tk[tk.length - 1] : '';
      var linha = [].slice.call(h.querySelectorAll('tr')).filter(function (tr) {
        var tx = norm(tr.textContent || '');
        return /^\d/.test(tx) && ((citacao && tx.indexOf(norm(citacao)) >= 0) || (ult && tx.indexOf(ult) >= 0));
      })[0];
      if (!linha) { rel.push('Coordenador: linha de "' + nome + '" não encontrada na lista de pesquisadores; marque na aba Equipe'); return false; }
      var cel = [].slice.call(linha.querySelectorAll('.cell-wrapper')).filter(function (c) { return /^(n[aã]o|sim)$/i.test(c.textContent.trim()); })[0];
      if (!cel) { rel.push('Coordenador: coluna de "' + nome + '" não encontrada; marque na aba Equipe'); return false; }
      if (/^sim$/i.test(cel.textContent.trim())) return true;
      cel.click(); await sleep(450);
      var sl = linha.querySelector('select');
      if (!sl) { rel.push('Coordenador: o seletor de "' + nome + '" não abriu; marque na aba Equipe'); return false; }
      sl.value = 's'; fireG(sl); await sleep(600);
      return true;
    };
    var gAutores = async function () {
      var lista = GR.autores || [];
      if (!lista.length) return;
      if (/F_CTR=D(&|$)/.test(String(G.url || ''))) { rel.push('Autores: vêm do DOI (o Lattes os recupera sozinho e liga o seu nome pelas citações do currículo); confira a aba Autores'); return; }
      gOk.autores = 0;
      var digitados = 0;
      var tu = toks(d.__usuario || '');
      for (var i = 0; i < lista.length; i++) {
        var nomeA = String(lista[i].nome || '').trim();
        if (!nomeA) continue;
        var citJa = norm(String(lista[i].citacao || '')); if (citJa && norm((gHolder(/autor/i) || { textContent: '' }).textContent).indexOf(citJa) >= 0) { gOk.autores++; continue; } // já está na lista
        // O TITULAR precisa ser escolhido em "Listar todos" (o Lattes recusa o titular digitado à mão).
        var ta = toks(nomeA);
        if (tu.length && ta.length && tu[0] === ta[0] && tu[tu.length - 1] === ta[ta.length - 1]) {
          var lkTodos = gLink(gHolder(/autor/i), /^Listar todos/);
          if (lkTodos) {
            lkTodos.click();
            var escolhido = null, candL = [];
            for (var tt = 0; !escolhido && tt < 10; tt++) {
              await sleep(300);
              var cit = String(lista[i].citacao || '').trim();
              // A lista de "Listar todos" pode abrir no formulário ou numa janela/frame à parte: procura em todos os documentos acessíveis.
              var docsL = [gdoc, gTopDoc];
              [].slice.call(gTopDoc.querySelectorAll('iframe')).forEach(function (fr) { try { if (fr.contentDocument) docsL.push(fr.contentDocument); } catch (e) {} });
              [].slice.call(gdoc.querySelectorAll('iframe')).forEach(function (fr) { try { if (fr.contentDocument && docsL.indexOf(fr.contentDocument) < 0) docsL.push(fr.contentDocument); } catch (e) {} });
              candL = [];
              docsL.forEach(function (dc) { [].slice.call(dc.querySelectorAll('a')).forEach(function (x) { if (x.offsetParent !== null && x.textContent.trim().length > 3) candL.push(x); }); });
              escolhido = candL.filter(function (x) {
                var tx = x.textContent || '';
                if (cit && tx.indexOf('(' + cit + ')') >= 0) return true;
                var tk = toks(tx.split('(')[0]);
                return tk.length > 1 && (tk.join(' ') === ta.join(' ') || (tk[0] === ta[0] && tk[tk.length - 1] === ta[ta.length - 1] && Math.abs(tk.length - ta.length) <= 1));
              })[0];
            }
            if (escolhido) { escolhido.click(); gOk.autores++; await sleep(700); if (lista[i].coordenador) await gCoordenador(nomeA, cit); continue; }
            rel.push('titular não encontrado em "Listar todos": será digitado (o Lattes pode recusar) [' + candL.length + ' links visíveis; amostra: ' + candL.slice(0, 5).map(function (x) { return x.textContent.trim().slice(0, 25); }).join(' | ') + ']');
          }
        }
        digitados++;
        var lk = gLink(gHolder(/autor/i), /^Incluir novo/);
        if (!lk) { rel.push('grade de autores não encontrada (se o Lattes importou os autores, confira-os)'); break; }
        lk.click(); await sleep(450);
        var n1 = gdoc.getElementById('nomeAutor'), n2 = gdoc.getElementById('nomeAutorComoCitado');
        for (var t = 0; (!n1 || !n2) && t < 8; t++) { await sleep(300); n1 = gdoc.getElementById('nomeAutor'); n2 = gdoc.getElementById('nomeAutorComoCitado'); }
        if (!n1 || !n2) { rel.push('os campos do autor não apareceram'); break; }
        n1.value = nomeA.slice(0, 60); n2.value = String(lista[i].citacao || '').slice(0, 60); fireG(n1); fireG(n2);
        if (gConfirmar()) gOk.autores++; else { rel.push('não consegui confirmar o autor ' + nomeA); break; }
        await sleep(450);
        if (lista[i].coordenador) await gCoordenador(nomeA, String(lista[i].citacao || ''));
      }
      if (digitados) rel.push('Autores digitados à mão: confira (o titular deve ser escolhido em "Listar todos")');
    };
    await gTexto('palavras_chave', 'Palavras-chave', /palavra/i, /^Incluir nova/);
    await gSugestao('areas', 'Áreas', /^area/i);
    await gSugestao('setores', 'Setores', /setor/i);
    await gSugestao('instituicoes', 'Instituições', /^inst/i);
    // Depositante/Titular: pessoas e instituições têm cada uma a sua grade (titularPessoaHolder / titularInstHolder), com busca na lista do Lattes.
    // Documentos acessíveis (formulário, página do Lattes e frames): as janelas de inclusão podem estar em qualquer um deles.
    var gDocsTodos = function () {
      var out = [gdoc, gTopDoc];
      for (var q = 0; q < out.length && q < 16; q++) {
        [].slice.call(out[q].querySelectorAll('iframe')).forEach(function (fr) { try { if (fr.contentDocument && out.indexOf(fr.contentDocument) < 0) out.push(fr.contentDocument); } catch (e) {} });
      }
      return out;
    };
    var gDigitar = function (inp, v) {
      try { inp.focus(); } catch (e) {}
      inp.value = v; fireG(inp);
      ['keydown', 'keypress', 'input', 'keyup', 'change'].forEach(function (t) { try { inp.dispatchEvent(new Event(t, { bubbles: true })); } catch (e) {} });
    };
    // Janela "Seleção de Instituição" (Depositante/Titular): acha pelo texto visível, onde quer que ela esteja.
    var gDialogoInst = function () {
      var achado = null;
      gDocsTodos().forEach(function (dc) {
        try {
          if (!dc.body || !/Preencha o campo abaixo com Nome, Sigla/i.test(dc.body.innerText || '')) return;
          var cs = [].slice.call(dc.querySelectorAll('input[type="text"]')).filter(gVis);
          var inp = cs.filter(function (x) { return x.name === 'f_nome'; })[0] || cs[cs.length - 1];
          if (inp) achado = { dc: dc, inp: inp };
        } catch (e) {}
      });
      return achado;
    };
    var gTitularInst = async function (nome, lkIn, rotIn) {
      var rotT = rotIn || 'Depositante/Titular';
      var lk = lkIn || gLink(gHolder(/titularInst/i), /^Selecionar/i);
      if (!lk) { rel.push(rotT + ': link "Selecionar" das instituições não encontrado; escolha "' + nome + '" na aba'); return false; }
      lk.click();
      var dlg = null;
      for (var tf = 0; !dlg && tf < 30; tf++) { dlg = gDialogoInst(); if (!dlg) await sleep(300); }
      if (!dlg) { rel.push(rotT + ': a janela de instituições não abriu; escolha "' + nome + '" na aba'); return false; }
      var win = dlg.dc.defaultView;
      // Resultados da busca: links cujo nome termina com a UF/país entre parênteses, como o Lattes lista (ex.: "... do Maranhão (MA)").
      var lerRes = function () { var cur = gDialogoInst(); return [].slice.call((cur ? cur.dc : dlg.dc).querySelectorAll('a')).filter(function (a) { return gVis(a) && /[(]\s*[A-Za-z]{2,3}\s*[)]\s*$/.test(a.textContent.trim()); }); };
      var vistas = [];
      // A busca do Lattes acha melhor por sigla ou parte curta do nome: tenta as formas curtas antes do nome completo.
      var tent = gVariacoes(nome).sort(function (a, b) { var sa = /^[A-Z]{2,8}$/.test(a) ? 0 : 1, sb = /^[A-Z]{2,8}$/.test(b) ? 0 : 1; return sa - sb || a.length - b.length; });
      for (var ti = 0; ti < tent.length; ti++) {
        // O Lattes recarrega a janela a cada busca: o documento antigo fica obsoleto, então localiza a janela de novo a cada tentativa.
        dlg = gDialogoInst() || dlg; win = dlg.dc.defaultView;
        var antes = lerRes().map(function (a) { return a.textContent; }).join('|');
        gDigitar(dlg.inp, tent[ti]);
        if (typeof win.recuperaInstMacro === 'function') { try { win.recuperaInstMacro(); } catch (e) {} }
        else { try { dlg.inp.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 })); } catch (e) {} }
        var t0 = Date.now(), ult = -1, estavel = 0, links = [];
        while (Date.now() - t0 < 4500) {
          await sleep(300);
          links = lerRes();
          var mudou = links.map(function (a) { return a.textContent; }).join('|') !== antes;
          if (mudou && links.length === ult) { if (++estavel >= 2) break; } else { estavel = 0; }
          ult = links.length;
        }
        var achei = melhor(links, gNormNome(nome), function (a) { return gNormNome(a.textContent); });
        if (achei) { achei.click(); await sleep(1500); return true; }
        links.forEach(function (a) { var x = a.textContent.trim(); if (vistas.indexOf(x) < 0) vistas.push(x); });
      }
      rel.push(rotT + ': "' + nome + '" não identificada com segurança no cadastro do Lattes' + (vistas.length ? ' (opções: ' + vistas.slice(0, 4).join('; ') + ')' : ' [busca digitada: ' + tent.join(', ') + '; função de busca: ' + (typeof win.recuperaInstMacro) + ']') + '; a janela ficou aberta para você escolher');
      return false;
    };
    if ((GR.titulares_inst || []).length) {
      gOk.titulares_inst = 0;
      for (var ki = 0; ki < GR.titulares_inst.length; ki++) { if (await gTitularInst(GR.titulares_inst[ki])) gOk.titulares_inst++; else break; }
    }
    await gSugestao('titulares_pessoa', 'Depositante/Titular (pessoas)', /titularPessoa/i);
    // Situação do Depósito/Patente: "Incluir nova" abre uma janela com Descrição (lista) e Data (ddmmaaaa) e o botão Confirmar.
    var gJanelaSituacao = function () {
      var achado = null;
      gDocsTodos().forEach(function (dc) {
        try {
          [].slice.call(dc.querySelectorAll('select')).forEach(function (sl) {
            if (gVis(sl) && [].slice.call(sl.options).some(function (o) { return /aguardando negocia/i.test(o.text); })) achado = { dc: dc, sel: sl };
          });
        } catch (e) {}
      });
      return achado;
    };
    var gSituacao = async function (sit) {
      var jaAberta = gJanelaSituacao();
      if (!jaAberta) {
        var cand = [];
        gDocsTodos().forEach(function (dc) {
          [].slice.call(dc.querySelectorAll('a')).forEach(function (a) { if (/^incluir nov[oa]/i.test(a.textContent.trim()) && gVis(a) && !a.closest('[id$="Holder"]')) cand.push(a); });
        });
        if (!cand.length) { rel.push('Situação: link "Incluir nova" da aba Situação do Depósito/Patente não encontrado; inclua "' + sit.nome + ' ' + sit.data + '" na aba'); return false; }
        cand[0].click();
      }
      var jan = null;
      for (var tj = 0; !jan && tj < 20; tj++) { jan = gJanelaSituacao(); if (!jan) await sleep(300); }
      if (!jan) { rel.push('Situação: a janela "Situação do Depósito/Patente" não abriu; inclua "' + sit.nome + ' ' + sit.data + '" na aba'); return false; }
      var ops = [].slice.call(jan.sel.options);
      var alvoS = norm(sit.nome);
      var op = ops.filter(function (o) { return norm(o.text) === alvoS; })[0] || melhor(ops, sit.nome, function (o) { return o.text; });
      if (!op) { rel.push('Situação "' + sit.nome + '" não existe na lista do Lattes; escolha na janela'); return false; }
      jan.sel.value = op.value; fireG(jan.sel);
      var campoD = null, el2 = jan.sel;
      for (var kk = 0; !campoD && el2 && kk < 8; kk++) { el2 = el2.parentElement; if (el2) campoD = [].slice.call(el2.querySelectorAll('input[type="text"]')).filter(gVis)[0] || null; }
      if (!campoD) { rel.push('Situação: campo Data não encontrado; digite ' + sit.data + ' na janela'); return false; }
      var dig = String(sit.data || '').replace(/[^0-9]/g, '');
      gDigitar(campoD, campoD.maxLength >= 10 ? String(sit.data) : dig);
      await sleep(300);
      var conf = [].slice.call(jan.dc.querySelectorAll('a, button, input[type="button"], input[type="submit"]')).filter(function (x) { return gVis(x) && /^confirmar$/i.test((x.textContent || x.value || '').trim()); })[0];
      if (!conf) { rel.push('Situação: botão Confirmar não encontrado; confirme na janela'); return false; }
      conf.click();
      await sleep(800);
      if (gJanelaSituacao()) { rel.push('Situação "' + sit.nome + ' ' + sit.data + '": o Lattes não aceitou (a janela continua aberta); confira a data'); return false; }
      return true;
    };
    if ((GR.situacoes || []).length) {
      gOk.situacoes = 0;
      for (var si = 0; si < GR.situacoes.length; si++) { if (await gSituacao(GR.situacoes[si])) gOk.situacoes++; else break; }
    }
    await gAutores();
    // Projetos — Instituições envolvidas: campo com sugestões (f_instituicoes); sem correspondência única, usa o link "Selecionar" (lupa).
    var gLinkPerto = function (ref, rx) {
      var el2 = ref;
      for (var q = 0; el2 && q < 6; q++) {
        el2 = el2.parentElement;
        var a = el2 && [].slice.call(el2.querySelectorAll('a')).filter(function (x) { return rx.test(x.textContent.trim()) && gVis(x); })[0];
        if (a) return a;
      }
      return null;
    };
    if ((GR.instituicoes_envolvidas || []).length) {
      gOk.instituicoes_envolvidas = 0;
      for (var ie = 0; ie < GR.instituicoes_envolvidas.length; ie++) {
        var nmI = String(GR.instituicoes_envolvidas[ie]);
        var inpI = gdoc.getElementById('f_instituicoes');
        if (!inpI) { rel.push('Instituições envolvidas: campo não encontrado no formulário aberto'); break; }
        inpI.focus(); inpI.value = nmI;
        ['keydown', 'keypress', 'input', 'keyup'].forEach(function (t) { inpI.dispatchEvent(new KeyboardEvent(t, { bubbles: true, key: nmI.slice(-1) })); });
        await sleep(1200);
        var boxI = inpI.parentElement.querySelector('.suggest-content');
        var opI = boxI ? [].slice.call(boxI.querySelectorAll('a')) : [];
        var hitI = melhor(opI, nmI, function (o) { return o.textContent; });
        if (hitI) { hitI.click(); gOk.instituicoes_envolvidas++; await sleep(700); continue; }
        inpI.value = '';
        var lkSel = gLinkPerto(inpI, /^Selecionar/i);
        if (lkSel && await gTitularInst(nmI, lkSel, 'Instituições envolvidas')) { gOk.instituicoes_envolvidas++; await sleep(700); }
        else break;
      }
    }
    // Projetos — Instituição de financiamento: "Incluir novo item" abre a lupa de instituições e, ao escolher, a janela com
    // código do projeto (números), moeda, valor e natureza. Linha: instituição; código; moeda; valor; natureza.
    var gJanelaFinanc = function () {
      var achado = null;
      gDocsTodos().forEach(function (dc) { try { var i = dc.querySelector('input[name="f_cod_proj"]'); if (i && gVis(i)) achado = { dc: dc, cod: i }; } catch (e) {} });
      return achado;
    };
    var gSelPorTexto = function (sl, txt) {
      var ops = [].slice.call(sl.options).filter(function (o) { return o.value; });
      var alvoT = norm(txt);
      return ops.filter(function (o) { return norm(o.text) === alvoT; })[0] || melhor(ops, txt, function (o) { return o.text; });
    };
    if ((GR.financiamentos || []).length) {
      gOk.financiamentos = 0;
      for (var fi2 = 0; fi2 < GR.financiamentos.length; fi2++) {
        var pF = String(GR.financiamentos[fi2]).split(';').map(function (x) { return x.trim(); });
        var lkNovo = null;
        // O botão é uma imagem (img.botaoAdicionar) no rodapé da tabela cujo cabeçalho tem "Código do projeto"; só no formulário aberto
        // (a lista de projetos por baixo tem outro botão igual).
        var tabF = [].slice.call(gdoc.querySelectorAll('table')).filter(function (t) { return /c[oó]digo do projeto/i.test(t.textContent || '') && t.querySelector('img.botaoAdicionar'); })[0];
        if (tabF) lkNovo = tabF.querySelector('img.botaoAdicionar');
        if (!lkNovo) [].slice.call(gdoc.querySelectorAll('a, button, div, span')).forEach(function (a) { if (!lkNovo && gVis(a) && a.children.length < 3 && /^incluir novo item$/i.test((a.textContent || '').trim())) lkNovo = a; });
        if (!lkNovo) { rel.push('Financiamento: botão "Incluir novo item" não encontrado; inclua "' + pF[0] + '" na aba Equipe'); break; }
        if (!(await gTitularInst(pF[0], lkNovo, 'Financiamento'))) break;
        var jf = null;
        for (var tf2 = 0; !jf && tf2 < 20; tf2++) { jf = gJanelaFinanc(); if (!jf) await sleep(300); }
        if (!jf) { rel.push('Financiamento: a janela de dados do financiamento não abriu; preencha "' + pF[0] + '" na aba'); break; }
        var dcF = jf.dc;
        gDigitar(jf.cod, String(pF[1] || '').replace(/[^0-9]/g, '').slice(0, 20));
        var slM = dcF.querySelector('select[name="f_moeda"]'), slN = dcF.querySelector('select[name="f_natureza"]'), inV = dcF.querySelector('input[name="f_valor"]');
        var opM = slM && gSelPorTexto(slM, pF[2] || 'REAL');
        if (slM && opM) { slM.value = opM.value; fireG(slM); } else rel.push('Financiamento: moeda "' + (pF[2] || 'REAL') + '" não encontrada; escolha na janela');
        if (inV && pF[3]) gDigitar(inV, pF[3]);
        var opN = slN && pF[4] ? gSelPorTexto(slN, pF[4]) : null;
        if (slN && opN) { slN.value = opN.value; fireG(slN); } else if (pF[4]) rel.push('Financiamento: natureza "' + pF[4] + '" não encontrada; escolha na janela');
        await sleep(300);
        var cfF = [].slice.call(dcF.querySelectorAll('a, button, input[type="button"], input[type="submit"]')).filter(function (x) { return gVis(x) && /^confirmar$/i.test((x.textContent || x.value || '').trim()); })[0];
        if (!cfF) { rel.push('Financiamento: botão Confirmar não encontrado; confirme na janela'); break; }
        cfF.click();
        for (var fw = 0; fw < 20 && (fw === 0 || gJanelaFinanc()); fw++) await sleep(400);  // a janela leva alguns segundos para fechar
        if (gJanelaFinanc()) { rel.push('Financiamento "' + pF[0] + '": o Lattes não aceitou (a janela continua aberta); confira os campos'); break; }
        gOk.financiamentos++;
      }
    }
    // O Lattes pode recuperar dados do registro e trocar o que foi digitado (ex.: título): confere os campos de texto e reaplica.
    for (var gj = 0; gj < (G.campos || []).length; gj++) {
      var cj = G.campos[gj];
      if (!cj.valor || (cj.tipo !== 'text' && cj.tipo !== 'textarea') || /^(f_inst|f_curso|f_orgao|f_nme_agencia)$/i.test(cj.name)) continue;  // campos de lupa: o valor só entra pela janela de seleção
      var tj = gdoc.querySelector('[name="' + cj.name + '"]');
      var vj = String(cj.valor);
      if (tj && tj.maxLength > 0 && vj.length > tj.maxLength) vj = vj.slice(0, tj.maxLength);
      if (tj && !tj.disabled && tj.value !== vj) { tj.value = vj; fireG(tj); rel.push('"' + (cj.rotulo || cj.name) + '" tinha sido alterado pelo Lattes: reaplicado'); }
    }
    Object.keys(gOk).forEach(function (k) { ok += gOk[k]; rel.push(k.replace('_', '-') + ': ' + gOk[k] + '/' + ((GR[k] || []).length) + ' incluídos'); });
    (G.faltam || []).forEach(function (f) { rel.push('obrigatório sem valor: ' + f); });
    // Salvar automático (mesma regra do caminho dos itens antigos): só clica se nada precisa de conferência.
    var btnSalvarG = [].slice.call(gdoc.querySelectorAll('a, input[type="button"], input[type="submit"], button')).filter(function (el) {
      var act = (el.getAttribute('onclick') || '') + ' ' + (el.getAttribute('href') || '');
      return /pre_check|check\s*\(/i.test(act) || /^salvar$/i.test((el.textContent || el.value || '').trim());
    })[0];
    if (btnSalvarG) {
      try { btnSalvarG.style.outline = '3px solid #10b981'; btnSalvarG.style.boxShadow = '0 0 0 6px rgba(16,185,129,0.35)'; btnSalvarG.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
    }
    // No caminho manual do artigo (sem DOI) o Lattes dispara "DOI não encontrado." ao abrir o formulário: aviso sem efeito, não conta.
    var doiPreenchido = ((G.campos || []).filter(function (c) { return /^f_cod_doi$/i.test(c.name) && c.valor; }).length > 0);
    lfAvisosLattes.filter(function (m, i, v) { return v.indexOf(m) === i && !(/^DOI n[ãa]o encontrado/i.test(m) && /F_CTR=FIV/.test(String(G.url || ''))) && !(/^Informe o Digital Object Identifier/i.test(m) && !doiPreenchido); }).forEach(function (m) { rel.push('Aviso do Lattes: ' + m); });
    var criticosG = rel.filter(function (r) { return !/^Autores digitados à mão/i.test(r) && !/ incluídos$/.test(r); });
    if (d.__autoSalvar && btnSalvarG && !(G.faltam || []).length && criticosG.length === 0) {
      await sleep(600);
      try { window.top.sessionStorage.setItem('lfSalvou', String(Date.now())); } catch (e) {}
      if (d.__semAlerta) {
        // Automação: clica em Salvar e guarda a resposta do Lattes (as mensagens) sem abrir diálogo.
        var nAntes = lfAvisosLattes.length;
        try { btnSalvarG.click(); } catch (e) {}
        await sleep(7000);
        // O Lattes também responde com pop-ups próprios (HTML, não alert): "Não foi possível ... os seguintes problemas: ..." — lê em todas as janelas.
        var errosLattes = [];
        var varrerErros = function (w, prof) {
          if (prof > 6) return;
          try {
            var mErr = /N[ãa]o foi poss[ií]vel[\s\S]{0,400}/.exec(w.document.body.innerText || '');
            // ignora o texto de scripts do próprio Lattes que contêm a mesma frase (<br>, "for (", "saida"): só vale mensagem visível ao usuário
            if (mErr && !/<br>|for \(|saida|function/.test(mErr[0])) errosLattes.push(mErr[0].replace(/\s+/g, ' ').slice(0, 300));
            // Sucesso: o Lattes devolve um script ("A operação foi realizada com sucesso!") no quadro do formulário
            if (/realizada com sucesso/i.test(w.document.documentElement.innerHTML || '') && !errosLattes.some(function (x) { return /^Operação realizada com sucesso/.test(x); })) errosLattes.push('Operação realizada com sucesso (confirmado pelo Lattes)');
            for (var iw = 0; iw < w.frames.length; iw++) varrerErros(w.frames[iw], prof + 1);
          } catch (e) {}
        };
        varrerErros(window.top, 0);
        try { window.top.__lfUltimoRelatorio = 'Resposta do Lattes ao salvar: ' + ((lfAvisosLattes.slice(nAntes).concat(errosLattes)).join(' | ') || '(sem mensagem)'); } catch (e) {}
        lfRestaurar();
        return;
      }
      lfRestaurar();
      try { gdoc.defaultView.alert = window.top.alert.bind(window.top); } catch (e) {}
      try { btnSalvarG.click(); return; } catch (e) {}
    }
    lfAlerta('LattesData: ' + ok + ' campos preenchidos em "' + (G.item || '') + '".' + (rel.length ? '\n\nAtenção:\n- ' + rel.join('\n- ') : '') + '\n\nConfira tudo e clique em Salvar no Lattes.');
    return;
  }
  var want = d.tipo_producao || 'anais';
  var wantAndamento = want === 'orientacao' && norm(d.situacao_orient).indexOf('andamento') >= 0;
  var doc = findDoc(window);
  var precisaAbrir = !doc || formTypeOf(doc) !== want;
  if (!precisaAbrir && want === 'orientacao') {
    var r0 = doc.querySelector('input[type="radio"][name="F_COD_PROD"]');
    var jaAndamento = !!(r0 && /^A/.test(r0.value));
    if (wantAndamento !== jaAndamento) precisaAbrir = true;
  }
  if (precisaAbrir) {
    var cv = findCvCode(window.top.document);
    var modal = window.top.modalCV2;
    if (cv && modal && typeof modal.setarUrl === 'function') {
      var targetUrl = '';
      if (want === 'artigo') {
        var doiClean = String(d.doi || '').trim();
        targetUrl = 'PKG_ARTIGO.form?f_sta_divulgacao_cientifica=&F_COD_DOI=' + encodeURIComponent(doiClean) + '&F_CTR=' + (doiClean ? 'D' : 'I') + '&F_COD=' + cv + '&f_cod=' + cv;
      } else if (want === 'apresentacao') {
        targetUrl = 'prc_tec_apres?f_cod=' + cv;
      } else if (want === 'orientacao') {
        targetUrl = 'pkg_orient.form?f_cod=' + cv + '&f_tipo=' + (wantAndamento ? 'A' : 'C');
      } else {
        targetUrl = 'pkg_trabalho.form?f_cod=' + cv + '&F_STA_DIVULGACAO_CIENTIFICA=&f_seq_ev=';
      }
      modal.setarUrl(targetUrl, true);
      var tOpen = Date.now();
      doc = null;
      while (Date.now() - tOpen < 15000) {
        await sleep(350);
        var cand = findDoc(window);
        if (cand && cand.readyState === 'complete' && formTypeOf(cand) === want) {
          doc = cand;
          break;
        }
      }
      if (doc) await sleep(600);
    }
  }
  if (!doc) {
    lfAlerta('LattesData: formulário não encontrado. Faça login no Lattes para abrir o painel principal e tente novamente.');
    return;
  }
  var report = [];
  var fire = function (el) { ['input', 'change'].forEach(function (t) { el.dispatchEvent(new Event(t, { bubbles: true })); }); };
  var visible = function (el) { return el.offsetParent !== null; };
  // Escolha automática em cadastros controlados: nome idêntico; senão, a opção mais parecida, só se for clara e única.
  function melhor(itens, alvo, txt) {
    var a = norm(alvo);
    if (!a) return null;
    var ex = itens.filter(function (i) { return norm(txt(i)) === a; })[0];
    if (ex) return ex;
    var ta = toks(alvo);
    if (!ta.length) return null;
    var pts = itens.map(function (i) {
      var tb = toks(txt(i));
      var inter = ta.filter(function (t) { return tb.indexOf(t) >= 0; }).length;
      var uni = ta.length + tb.length - inter;
      return { i: i, s: uni ? inter / uni : 0 };
    }).sort(function (x, y) { return y.s - x.s; });
    if (pts.length && pts[0].s >= 0.75 && (pts.length < 2 || pts[1].s <= pts[0].s - 0.15)) return pts[0].i;
    return null;
  }
  async function esperaQuadro(rx, ms) {
    var t1 = Date.now();
    while (Date.now() - t1 < ms) {
      var fr = [].slice.call(window.top.document.querySelectorAll('iframe')).filter(function (f) { return rx.test(f.src) && f.offsetParent !== null; })[0];
      if (fr && fr.contentDocument && fr.contentDocument.readyState === 'complete') return fr;
      await sleep(300);
    }
    return null;
  }

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
  function setRadioIfExists(name, value) {
    if (!value) return;
    var r = doc.querySelector('input[type="radio"][name="' + name + '"][value="' + value + '"]');
    if (r) { r.checked = true; r.click(); }
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

  var divCient = (d.f_sta_divulgacao_cientifica === 'S' || d.divulgacao_cientifica === 'S') ? 'S' : 'N';
  var inovVal = (d.f_inovacao === 'S' || d.inovacao === 'S') ? 'S' : 'N';
  var relevVal = /^(s|sim)$/i.test(String(d.relevante || '').trim()) ? 'S' : 'N';

  var want = d.tipo_producao || 'anais';
  var have = doc.querySelector('[name="f_titulo_periodico"]') ? 'artigo' : (doc.querySelector('[name="f_nme_orient"]') ? 'orientacao' : (doc.querySelector('[name="f_nme_evento"]') ? 'apresentacao' : 'anais'));
  var NOMES = { anais: 'um Trabalho em anais', apresentacao: 'uma Apresentação de trabalho', artigo: 'um Artigo em periódico', orientacao: 'uma Orientação' };
  var CAMINHOS = { anais: 'Produções > Trabalhos publicados em anais de eventos', apresentacao: 'Produções > Apresentação de trabalho e palestra', artigo: 'Produções > Artigos completos publicados em periódicos', orientacao: 'Orientações > Orientações e supervisões concluídas (ou em andamento)' };
  if (want !== have) {
    lfAlerta('LattesData: este registro é ' + NOMES[want] + ', mas o formulário aberto é de ' + NOMES[have] + '. Abra ' + CAMINHOS[want] + ' > Incluir novo item e execute de novo.');
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
      if (!recuperou) report.push('o Lattes não recuperou os dados do DOI; usei os dados do LattesData');
    } else {
      report.push('sem DOI: escolha o periódico na lupa do Lattes');
    }
    if (!recuperou) {
      setVal('f_titulo', d.titulo); setVal('f_ano', d.ano);
      setSelect('F_IDIOMA', lookup(IDIOMA, d.idioma, 'idioma'));
      setSelect('f_meio', lookup(MEIO, d.meio_divulgacao, 'meio de divulgação'));
      setVal('f_issn', d.isbn_issn); setVal('f_volume', d.volume); setVal('f_serie', d.serie); setVal('f_pag_ini', d.pagina_inicial);
      if (d.periodico) {
        // Melhor esforço: o DOM da lupa de periódicos não está documentado; qualquer falha vira aviso, nunca erro.
        var perOk = false;
        try {
          var lupa = [].slice.call(doc.querySelectorAll('a, img, input[type="button"]')).filter(function (x) {
            var h = (x.getAttribute('href') || '') + ' ' + (x.getAttribute('onclick') || '');
            return /periodico/i.test(h) && visible(x);
          })[0];
          if (lupa) {
            lupa.click();
            var fp = await esperaQuadro(/periodico/i, 8000);
            if (fp) {
              var fd = fp.contentDocument;
              var campo = [].slice.call(fd.querySelectorAll('input[type="text"]')).filter(function (x) { return visible(x); })[0];
              if (campo) {
                campo.value = d.isbn_issn || d.periodico; fire(campo);
                var busca = [].slice.call(fd.querySelectorAll('a, input[type="button"], input[type="submit"], button')).filter(function (x) { return /pesquis|busc|consult|localiz/i.test(x.textContent + ' ' + (x.value || '') + ' ' + (x.getAttribute('onclick') || '')); })[0];
                if (busca) busca.click();
                await sleep(3500);
                var cands = [].slice.call(fd.querySelectorAll('a')).filter(function (a) { return /selecion|retorn|escolh/i.test((a.getAttribute('href') || '') + ' ' + (a.getAttribute('onclick') || '')); });
                var pa = melhor(cands, d.periodico, function (a) { return a.textContent; }) || (d.isbn_issn && cands.length === 1 ? cands[0] : null);
                if (pa) { pa.click(); await sleep(1500); perOk = !!(doc.querySelector('[name="f_titulo_periodico"]') || {}).value; }
              }
            }
          }
        } catch (e) {}
        if (!perOk) report.push('periódico "' + d.periodico + '": não consegui escolher sozinho; escolha na lupa do Lattes (cadastro controlado)');
      }
    }
    var pf = doc.querySelector('[name="f_pag_fim"]');
    if (pf && !pf.value) setVal('f_pag_fim', d.pagina_final);
    setVal('f_homepage', d.homepage);
    setRadio('F_RELEV', relevVal);
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', divCient);
    setRadioIfExists('f_sta_inovacao', inovVal);
    setRadioIfExists('f_inovacao', inovVal);
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
      lfAlerta('LattesData: este registro é uma orientação ' + (andamento ? 'em andamento' : 'concluída') + ', mas o formulário aberto é de ' + (formAndamento ? 'em andamento' : 'concluídas') + '. Abra Orientações > Orientações e supervisões ' + (andamento ? 'em andamento' : 'concluídas') + ' > Incluir novo item.');
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
    setVal('f_homepage', d.homepage); setRadio('F_RELEV', relevVal); setVal('f_nme_orient', d.nome_orientando);
    var comBolsa = /^(s|sim)$/i.test(String(d.bolsa || '').trim());
    setRadio('F_BOLSA', comBolsa ? 'S' : 'N'); setVal('f_ref', d.outras_informacoes);
    if (comBolsa && d.agencia_financiadora) {
      if (doc.querySelector('[name="f_nme_agencia"]')) { setVal('f_nme_agencia', d.agencia_financiadora); report.push('agência financiadora "' + d.agencia_financiadora + '" digitada: confirme na lupa do Lattes'); }
      else report.push('não achei o campo da agência financiadora; informe na lupa');
    }
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
        var achei = melhor(links, normNome(d.instituicao_orient), function (a) { return normNome(a.textContent); });
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
          var oc = opts2.filter(function (o) { return normCurso(o.text) === alvo; })[0] || opts2.filter(function (o) { return alvo.length > 4 && normCurso(o.text).indexOf(alvo) >= 0; })[0] || melhor(opts2, alvo, function (o) { return normCurso(o.text); });
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
    setRadio('F_RELEV', relevVal);
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', divCient);
    setRadioIfExists('f_sta_inovacao', inovVal);
    setRadioIfExists('f_inovacao', inovVal);
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
    setRadio('F_RELEV', relevVal);
    setRadio('F_STA_DIVULGACAO_CIENTIFICA', divCient);
    setRadioIfExists('f_sta_inovacao', inovVal);
    setRadioIfExists('f_inovacao', inovVal);
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
  // Lista curta dos campos visíveis, para diagnosticar quando o Lattes muda a tela (vai no relatório do painel).
  function camposVisiveis() {
    return [].slice.call(doc.querySelectorAll('input, select, textarea')).filter(function (x) { return visible(x) && x.type !== 'hidden'; })
      .slice(0, 14).map(function (x) { return (x.id || x.name || x.type) + (x.value ? '=' + String(x.value).slice(0, 18) : ''); }).join(', ');
  }
  // Autores: primeiro procura no histórico do currículo ("Listar todos"), que traz o nome JÁ no formato que o Lattes
  // reconhece (o do titular vem em azul). Só se não achar é que inclui um autor novo, digitando.
  function mesmoNome(a, b) {
    var x = toks(a), y = toks(b);
    return x.length > 1 && y.length > 1 && x[0] === y[0] && x[x.length - 1] === y[y.length - 1] &&
      x.every(function (t) { return y.indexOf(t) >= 0; });
  }
  function ehAzul(a) { return /00f|0,\s*0,\s*255/i.test(a.getAttribute('style') || ''); }
  function fecharListaAutores(item) {
    var el = item;
    while (el && el !== doc.body) {
      var c = el.querySelector && el.querySelector('a.tool.close');
      if (c) { c.click(); return true; }
      el = el.parentElement;
    }
    return false;
  }
  async function autorDoHistorico(autor, titular) {
    var lk = gridLink('autorHolder', /^Listar todos/);
    if (!lk) return 'sem-botao';
    lk.click();
    var itens = [];
    for (var t = 0; t < 16 && !itens.length; t++) { await sleep(300); itens = [].slice.call(doc.querySelectorAll('li > a.label')); }
    if (!itens.length) return 'lista-vazia';
    var alvo = null, ambiguo = false;
    if (titular) alvo = itens.filter(ehAzul)[0] || null;
    if (!alvo) {
      var nomeDe = function (a) { return a.textContent.replace(/\s*\([^()]*\)\s*$/, ''); };
      var exatos = itens.filter(function (a) { return norm(nomeDe(a)) === norm(autor.nome); });
      var parecidos = itens.filter(function (a) { return mesmoNome(autor.nome, nomeDe(a)); });
      if (exatos.length === 1) alvo = exatos[0];
      else if (!exatos.length && parecidos.length === 1) alvo = parecidos[0];
      else if (exatos.length > 1 || parecidos.length > 1) ambiguo = true;
    }
    if (!alvo) { fecharListaAutores(itens[0]); await sleep(300); return ambiguo ? 'ambiguo' : 'nao-achou'; }
    var m = alvo.textContent.match(/\(([^()]*)\)\s*$/);
    var cit = m ? m[1] : '';
    alvo.click();
    var holder = doc.getElementById('autorHolder');
    for (var u = 0; u < 12; u++) {
      await sleep(250);
      if (!cit || (holder && holder.innerText.indexOf(cit) >= 0)) { return 'ok'; }
    }
    return 'sem-confirmacao';
  }

  var logadoNome = '';
  try { var ne = window.top.document.getElementById('nmeLt') || window.top.document.querySelector('.dadosPrinc .nome'); logadoNome = ne ? ne.textContent.trim() : ''; } catch (e) {}
  var okHist = 0, titularNaLista = false;

  for (var i = 0; !autoresPeloDoi && i < autores.length; i++) {
    var nomeAut = String(autores[i].nome || '').trim();
    if (!nomeAut) { report.push('autor ' + (i + 1) + ' sem nome no certificado: ignorado'); continue; }
    var ehTit = !!logadoNome && mesmoNome(logadoNome, nomeAut);
    var hist = await autorDoHistorico(autores[i], ehTit);
    if (hist === 'ok') { okAut++; okHist++; if (ehTit) titularNaLista = true; await sleep(450); continue; }
    if (hist === 'ambiguo') report.push('há mais de um autor parecido com "' + nomeAut + '" no histórico: incluí como novo (confira)');
    else if (hist === 'sem-confirmacao') report.push('selecionei "' + nomeAut + '" no histórico, mas a grade não confirmou. Confira os autores');
    if (hist === 'sem-confirmacao') { continue; }
    if (ehTit) report.push('ATENÇÃO: não achei o titular (azul) no histórico de autores; vou incluí-lo digitando e o Lattes pode recusar');
    var link = gridLink('autorHolder', /^Incluir novo/);
    if (!link) { report.push('grade de autores não encontrada'); break; }
    link.click(); await sleep(450);
    var nome = doc.getElementById('nomeAutor'), cita = doc.getElementById('nomeAutorComoCitado');
    for (var tentaCampos = 0; (!nome || !cita) && tentaCampos < 8; tentaCampos++) {
      await sleep(300); nome = doc.getElementById('nomeAutor'); cita = doc.getElementById('nomeAutorComoCitado');
    }
    if (!nome || !cita) { report.push('os campos do autor não apareceram. Campos visíveis: ' + camposVisiveis()); break; }
    nome.value = nomeAut.slice(0, 60); cita.value = String(autores[i].citacao || '').slice(0, 60);
    fire(nome); fire(cita);
    if (clickConfirm()) { okAut++; if (ehTit) titularNaLista = true; }
    else { report.push('não consegui confirmar o autor ' + nomeAut + '. Campos visíveis: ' + camposVisiveis()); break; } // para: repetir só faria o Lattes piscar
    await sleep(450);
  }

  if (want !== 'orientacao' && !autoresPeloDoi && logadoNome && !titularNaLista) {
    report.push('ATENÇÃO: o titular (' + logadoNome + ') não ficou na lista de autores: o Lattes vai recusar ao salvar. Escolha-o em "Listar todos" (aparece em azul).');
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
    if (!opts.length) { await sleep(1500); box = ainp.parentElement.querySelector('.suggest-content'); opts = box ? [].slice.call(box.querySelectorAll('a')) : []; }
    var hit = melhor(opts, areas[m], function (o) { return o.textContent; });
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
  lfRestaurar();
  try { if (doc.defaultView && window.top && window.top.alert) doc.defaultView.alert = window.top.alert.bind(window.top); } catch (e) {}
  var btnSalvar = [].slice.call(doc.querySelectorAll('a, input[type="button"], input[type="submit"], button')).filter(function (el) {
    var act = (el.getAttribute('onclick') || '') + ' ' + (el.getAttribute('href') || '');
    return /pre_check|check\s*\(/i.test(act) || /^salvar$/i.test((el.textContent || el.value || '').trim());
  })[0];
  if (btnSalvar) {
    try {
      btnSalvar.style.outline = '3px solid #10b981';
      btnSalvar.style.boxShadow = '0 0 0 6px rgba(16,185,129,0.35)';
      btnSalvar.style.borderRadius = '6px';
      btnSalvar.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (e) {}
  }
  var avisosCriticos = report.filter(function (r) { return !/^autores importados do DOI/i.test(r); });
  if (d.__autoSalvar && btnSalvar && avisosCriticos.length === 0) {
    await sleep(600);
    try { window.top.sessionStorage.setItem('lfSalvou', String(Date.now())); } catch (e) {}
    try { btnSalvar.click(); return; } catch (e) {}
  }
  lfAlerta('LattesData: campos principais preenchidos. ' + (autoresPeloDoi ? 'Autores: do DOI; ' : (autores.length ? 'Autores: ' + okAut + '/' + autores.length + '; ' : '')) + 'palavras-chave: ' + okKw + '/' + kws.length + '; áreas: ' + okArea + '/' + areas.length + '.' +
    (report.length ? '\n\nAtenção:\n- ' + report.join('\n- ') : '') + '\n\nConfira tudo e clique no botão Salvar (destacado em verde) no Lattes.');
})();`;

function sanitizeDataPayload(raw) {
  const d = { ...raw };
  const ASPAS = /["'“”‘’`«»]/g;
  const TRAVES = /[—–]/g;
  const cleanStr = (s) => (s ? String(s).replace(ASPAS, "").replace(TRAVES, "-").replace(/\s+/g, " ").trim() : "");
  
  [
    "titulo",
    "titulo_anais",
    "titulo_en",
    "nome_evento",
    "cidade_evento",
    "local_evento",
    "instituicao_promotora",
    "editora",
    "cidade_editora",
    "periodico",
    "nome_orientando",
    "instituicao_orient",
    "curso_orient"
  ].forEach((k) => {
    if (d[k] && typeof d[k] === "string") d[k] = cleanStr(d[k]);
  });
  if (d.isbn_issn) {
    d.isbn_issn = String(d.isbn_issn).replace(/\D/g, "");
  }
  if (d.doi) {
    let doi = String(d.doi).trim().replace(/^(https?:\/\/)?(dx\.)?doi\.org\//i, "").replace(/^doi:\s*/i, "").trim();
    const m = doi.match(/\b(10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+)/);
    if (m) doi = m[1].replace(/\.$/, "");
    d.doi = doi;
  }
  return d;
}

function evaluateCompliance(data) {
  const alerts = [];
  const tipo = data.tipo_producao || "anais";
  const titulo = (data.titulo || "").trim();
  const doi = (data.doi || "").trim();
  const pagIni = (data.pagina_inicial || "").trim();
  const vol = (data.volume || "").trim();
  const isbn = (data.isbn_issn || "").trim();

  // 1. Regra de Artigo sem DOI (Portaria CNPq 2.664/2026 e CAPES Sucupira)
  if (tipo === "artigo") {
    if (!doi) {
      alerts.push({
        campo: "doi",
        nivel: "critico",
        mensagem: "Artigo sem DOI cadastrado. Conforme a Portaria CNPq 2.664/2026 e CAPES Sucupira, artigos sem DOI não são importados pelo Sucupira, gerando inconsistência e perda de pontuação do PPG."
      });
    } else if (!doi.startsWith("10.") || !doi.includes("/")) {
      alerts.push({
        campo: "doi",
        nivel: "critico",
        mensagem: `DOI '${doi}' fora do padrão Lattes (deve iniciar com '10.' e conter barra '/', sem prefixos URL).`
      });
    } else {
      alerts.push({
        campo: "doi",
        nivel: "sucesso",
        mensagem: `DOI em conformidade com o padrão CNPq (10.xxxx): ${doi}`
      });
    }
  } else if (doi) {
    if (doi.startsWith("10.") && doi.includes("/")) {
      alerts.push({
        campo: "doi",
        nivel: "sucesso",
        mensagem: `DOI em conformidade com o padrão CNPq: ${doi}`
      });
    } else {
      alerts.push({
        campo: "doi",
        nivel: "aviso",
        mensagem: `DOI '${doi}' fora do formato oficial do Lattes (esperado 10.xxxx).`
      });
    }
  }

  // 2. Regra de aspas e travessões no título
  if (titulo) {
    const hasAspas = /["'“”‘’`«»]/.test(titulo);
    const hasTraves = /[—–]/.test(titulo);
    if (hasAspas || hasTraves) {
      const motivos = [];
      if (hasAspas) motivos.push("aspas");
      if (hasTraves) motivos.push("travessões (—, –)");
      alerts.push({
        campo: "titulo",
        nivel: "aviso",
        mensagem: `O título contém ${motivos.join(" e ")}, que o Lattes converte para '?'. Use a sanitização automática para evitar corrupção de caracteres.`
      });
    } else {
      alerts.push({
        campo: "titulo",
        nivel: "sucesso",
        mensagem: "Título em conformidade, sem aspas ou caracteres conflitantes com o Lattes."
      });
    }
  } else {
    alerts.push({
      campo: "titulo",
      nivel: "critico",
      mensagem: "Título não informado. Campo obrigatório no Lattes."
    });
  }

  // 3. Regra de Página Inicial e Volume (CAPES Sucupira)
  if (tipo === "artigo" || tipo === "anais") {
    if (!pagIni) {
      alerts.push({
        campo: "pagina_inicial",
        nivel: "aviso",
        mensagem: "Página inicial não informada. Importante para conferência nos relatórios Sucupira/CAPES."
      });
    } else {
      alerts.push({
        campo: "pagina_inicial",
        nivel: "sucesso",
        mensagem: `Página inicial (${pagIni}) registrada.`
      });
    }

    if (!vol) {
      alerts.push({
        campo: "volume",
        nivel: "aviso",
        mensagem: "Volume não informado. Recomendado para citação bibliográfica completa."
      });
    } else {
      alerts.push({
        campo: "volume",
        nivel: "sucesso",
        mensagem: `Volume (${vol}) registrado.`
      });
    }
  }

  // 4. Regra de ISBN / ISSN (somente dígitos no Lattes)
  if (isbn) {
    if (/\D/.test(isbn)) {
      alerts.push({
        campo: "isbn_issn",
        nivel: "aviso",
        mensagem: `ISBN/ISSN '${isbn}' contém caracteres não numéricos (como hífens). O campo f_isbn do Lattes exige apenas dígitos.`
      });
    } else {
      alerts.push({
        campo: "isbn_issn",
        nivel: "sucesso",
        mensagem: `ISBN/ISSN formatado com dígitos (${isbn}), em conformidade com o Lattes.`
      });
    }
  }

  // 5. Preenchimento Duplo (Protocolo 3V)
  if (data.f_sta_divulgacao_cientifica === "S") {
    alerts.push({
      campo: "f_sta_divulgacao_cientifica",
      nivel: "sucesso",
      mensagem: "Preenchimento Duplo Ativo: Configurado para replicação na aba Educação e Popularização de C&T."
    });
  }
  if (data.f_inovacao === "S") {
    alerts.push({
      campo: "f_inovacao",
      nivel: "sucesso",
      mensagem: "Preenchimento Duplo Ativo: Configurado para replicação na aba Atividade de Inovação Tecnológica."
    });
  }

  return alerts;
}

function updateComplianceUI() {
  const data = getFormData();
  const alerts = evaluateCompliance(data);
  const pill = $("compliancePill");
  const miniPill = $("compliancePillMini");
  const card = $("complianceCard");
  const container = $("complianceAlerts");

  const hasCritico = alerts.some((a) => a.nivel === "critico");
  const hasAviso = alerts.some((a) => a.nivel === "aviso");

  let statusLevel = "sucesso";
  let statusText = "🛡️ Conformidade CNPq: Conforme";
  if (hasCritico) {
    statusLevel = "critico";
    statusText = "🚨 Conformidade CNPq: Risco Crítico";
  } else if (hasAviso) {
    statusLevel = "aviso";
    statusText = "⚠️ Conformidade CNPq: Atenção (Pendências)";
  }

  if (pill) {
    pill.className = `compliance-pill ${statusLevel}`;
    pill.textContent = statusText;
  }
  if (miniPill) {
    miniPill.className = `compliance-pill-mini ${statusLevel}`;
    miniPill.textContent = hasCritico ? "🚨 CNPq: Crítico" : (hasAviso ? "⚠️ CNPq: Ajustes" : "🛡️ CNPq: Conforme");
  }
  if (card) {
    card.classList.remove("has-critico", "has-aviso", "is-ok");
    if (hasCritico) card.classList.add("has-critico");
    else if (hasAviso) card.classList.add("has-aviso");
    else card.classList.add("is-ok");
  }

  if (container) {
    container.innerHTML = "";
    alerts.forEach((alt) => {
      const item = document.createElement("div");
      item.className = `compliance-alert-item ${alt.nivel}`;
      const icon = alt.nivel === "critico" ? "🚨" : (alt.nivel === "aviso" ? "⚠️" : "✅");
      const badge = document.createElement("span");
      badge.className = "compliance-badge-level";
      badge.textContent = alt.nivel;
      
      const textSpan = document.createElement("span");
      textSpan.textContent = ` ${icon} ${alt.mensagem}`;
      
      item.appendChild(badge);
      item.appendChild(textSpan);
      container.appendChild(item);
    });
  }
}

function buildLattesAutofillScript(data) {
  // "<" escapado para o JSON nunca fechar uma tag script caso o texto seja colado em HTML
  const usuario = $("ownerName") ? $("ownerName").value : "";
  const autoSalvar = !!($("autoSaveLattes") && $("autoSaveLattes").checked);
  const sanitized = aplicarCitacaoTitular(sanitizeDataPayload(data));
  const payload = JSON.stringify({ ...sanitized, __usuario: usuario, __origem: location.origin, __autoSalvar: autoSalvar }).replace(/</g, "\\u003c");
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
  const id = randomId(16);
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
  currentUploadedFile = file;
  currentUploadId = uploadId;
  $("cadernoResults").innerHTML = "";
  aplicarResposta(json, { uploadId, nomeArquivo: file.name });
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
  aplicarResposta(json, { texto: text, nomeArquivo: "o texto colado" });
}


// ==========================================================================
// Reconhecimento da evidência: "Entendi: X" / "Qual destes?" / escolhedor guiado
// ==========================================================================
let classCtx = { uploadId: null, texto: null, json: null };
let catalogoItens = null;
let chooserGrupo = "";
const TIPO_DO_ITEM = {};
const SINONIMOS = {
  anais: "resumo congresso poster pôster publicado anais caderno de resumos",
  apresentacao: "palestra poster pôster comunicação oral apresentei apresentação",
  participacao_evento: "ouvinte participante congresso simpósio jornada semana",
  organizacao_evento: "comissão organizadora organizei coordenei evento",
  artigo: "revista periódico doi publicado journal",
  artigo_aceito: "aceite aceito carta submissão",
  livro_capitulo: "livro capítulo isbn editora",
  orientacao_concluida: "tcc monografia ic iniciação científica mestrado doutorado coorientação orientei",
  orientacao_andamento: "tcc ic iniciação científica orientando atual em andamento",
  banca: "banca examinadora examinador defesa qualificação avaliador",
  curso_ministrado: "minicurso oficina aula ministrei docente instrutor",
  formacao_complementar: "curso capacitação extensão aperfeiçoamento atualização certificado de curso aluno",
  formacao_academica: "diploma graduação especialização mestrado doutorado titulação histórico",
  atuacao_profissional: "vínculo cargo trabalho emprego servidor monitoria contrato",
  revisor_periodico: "parecerista reviewer peer review revisor revista",
  corpo_editorial: "editor editorial conselho revista",
  patente: "inpi invenção carta patente depósito",
  software_registro: "programa de computador software registro inpi",
  premio: "prêmio menção honrosa melhor trabalho homenagem título",
  projeto: "pesquisa extensão ensino bolsa edital fapema cnpq equipe",
  idioma: "inglês espanhol proficiência toefl ielts cambridge",
  licenca: "maternidade paternidade adoção licença",
  relatorio_tecnico: "parecer relatório consultoria assessoria laudo",
};
const normTxt = (t) => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const confRotulo = (c) => (c >= 0.75 ? "Confiança alta" : c >= 0.5 ? "Confiança média" : "Confiança baixa");

function el(tag, cls, texto) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (texto !== undefined) e.textContent = texto;
  return e;
}

async function garantirCatalogo() {
  if (catalogoItens) return catalogoItens;
  try {
    const r = await fetch("/api/itens");
    catalogoItens = (await r.json()).itens || [];
  } catch (e) {
    catalogoItens = [];
  }
  return catalogoItens;
}

function aplicarResposta(json, ctx) {
  const statusEl = $("extractStatus");
  classCtx = { uploadId: ctx.uploadId || null, texto: ctx.texto || null, json };
  const cls = json.classificacao || { decisao: "escolher", candidatos: [] };
  if (json.generico) {
    genOcultar();
    mostrarGenerico(json.generico);
    statusEl.textContent = `Li ${ctx.nomeArquivo}. Revise o formulário abaixo e envie ao Lattes.`;
  } else if (json.extracted) {
    genOcultar();
    setFormData(json.extracted);
    const notes = (json.extracted.extraction_notes || []).join(" ");
    statusEl.textContent = `Li ${ctx.nomeArquivo}. ${notes || "Revise e clique em Buscar Dados Faltantes se necessário."}`;
    if (notes.includes("ATENÇÃO")) showToast("Atenção: o usuário selecionado não consta neste documento.");
  } else {
    statusEl.textContent = `Li ${ctx.nomeArquivo}, mas ainda não preenchi nada: ${cls.motivo_decisao || "escolha abaixo o que ele comprova"}.`;
  }
  statusEl.classList.remove("hidden");
  renderClassPanel(cls, json);
}

async function renderClassPanel(cls, json) {
  const itens = await garantirCatalogo();
  const painel = $("classPanel");
  const head = $("classHead");
  const cards = $("classCards");
  const rel = $("classRel");
  head.innerHTML = "";
  cards.innerHTML = "";
  rel.textContent = "";
  painel.classList.remove("hidden", "ok", "duvida", "escolher");
  $("classChooser").classList.add("hidden");
  const cands = cls.candidatos || [];
  const top = cands[0];

  if (cls.decisao === "avancar" && top) {
    painel.classList.add(top.implementado && json.extracted ? "ok" : "duvida");
    head.appendChild(el("strong", "", top.implementado && json.extracted ? `✅ Entendi: ${top.item}` : `Reconheci: ${top.item}`));
    head.appendChild(el("p", "", `Porque: ${top.motivos.join("; ")}.` + (top.implementado ? "" : " O preenchimento automático deste tipo ainda não está pronto.")));
    cands.slice(1).filter((c) => c.confianca >= 0.55).slice(0, 2).forEach((c) => {
      const b = el("button", "btn btn-sm btn-ghost", `Ou seria: ${c.item}`);
      b.type = "button";
      b.onclick = () => escolherItem(c.id);
      cards.appendChild(b);
    });
    const tambem = (cls.tambem_pode_gerar || [])[0];
    if (tambem) {
      const alvo = itens.find((i) => i.id === tambem.id);
      rel.textContent = `Este documento também comprova: ${alvo ? alvo.item : tambem.id} (${tambem.motivo}). Registre depois de concluir este.`;
    }
  } else if (cls.decisao === "confirmar" && cands.length) {
    painel.classList.add("duvida");
    head.appendChild(el("strong", "", "Encontrei mais de uma possibilidade. Qual descreve melhor este documento?"));
    cands.slice(0, 3).forEach((c) => {
      const card = el("div", "class-card");
      card.appendChild(el("h4", "", c.item));
      card.appendChild(el("span", "conf-pill", confRotulo(c.confianca)));
      const ul = el("ul");
      c.motivos.forEach((m) => ul.appendChild(el("li", "", m)));
      card.appendChild(ul);
      const b = el("button", "btn btn-sm btn-primary", c.implementado ? "Usar este" : "Reconhecido (em breve)");
      b.type = "button";
      b.onclick = () => escolherItem(c.id);
      card.appendChild(b);
      cards.appendChild(card);
    });
  } else {
    painel.classList.add("escolher");
    head.appendChild(el("strong", "", "Não consegui identificar o documento."));
    head.appendChild(el("p", "", `${cls.motivo_decisao || "Nada nele aponta claramente para um item"}. Escolha abaixo o que ele comprova.`));
    abrirChooser();
  }
}

function abrirChooser() {
  $("classPanel").classList.remove("hidden");
  $("classChooser").classList.remove("hidden");
  renderChooser();
  $("chooserBusca").focus();
}

async function renderChooser() {
  const itens = await garantirCatalogo();
  const q = normTxt($("chooserBusca").value).trim();
  const grupos = [...new Set(itens.map((i) => i.grupo))];
  const gBox = $("chooserGrupos");
  gBox.innerHTML = "";
  ["", ...grupos].forEach((g) => {
    const b = el("button", g === chooserGrupo ? "ativo" : "", g || "Todos");
    b.type = "button";
    b.onclick = () => {
      chooserGrupo = g;
      renderChooser();
    };
    gBox.appendChild(b);
  });
  const lista = $("chooserLista");
  lista.innerHTML = "";
  const sugerido = classCtx.json && classCtx.json.classificacao && (classCtx.json.classificacao.candidatos || []).map((c) => c.id);
  const filtrados = itens
    .filter((i) => !chooserGrupo || i.grupo === chooserGrupo)
    .filter((i) => !q || normTxt([i.item, i.secao, i.grupo, i.exemplo, SINONIMOS[i.id] || ""].join(" ")).includes(q))
    .sort((a, b) => (sugerido && sugerido.includes(b.id) ? 1 : 0) - (sugerido && sugerido.includes(a.id) ? 1 : 0));
  if (!filtrados.length) {
    lista.appendChild(el("p", "hint", "Nada encontrado. Tente outra palavra (ex.: certificado, declaração, ata) ou escolha um grupo acima."));
    return;
  }
  filtrados.forEach((i) => {
    const b = el("button", "chooser-item");
    b.type = "button";
    const txt = el("span");
    txt.appendChild(document.createTextNode(i.item));
    txt.appendChild(el("small", "", `${i.secao} · ${i.grupo}${i.exemplo ? " · ex.: " + i.exemplo : ""}`));
    b.appendChild(txt);
    b.appendChild(el("span", i.implementado ? "badge-pronto" : "badge-breve", i.implementado ? "pronto" : "em breve"));
    b.onclick = () => escolherItem(i.id);
    lista.appendChild(b);
  });
}

function enviarFeedback(sugerido, escolhido, cls) {
  fetch("/api/classificacao/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sugerido, escolhido, decisao: (cls && cls.decisao) || "", confianca: (cls && cls.candidatos && cls.candidatos[0] && cls.candidatos[0].confianca) || 0 }),
  }).catch(() => {});
}

async function escolherItem(itemId) {
  const itens = await garantirCatalogo();
  const alvo = itens.find((i) => i.id === itemId);
  if (!alvo) return;
  const cls = classCtx.json && classCtx.json.classificacao;
  const sugerido = (cls && cls.candidatos && cls.candidatos[0] && cls.candidatos[0].id) || "nenhum";
  if (cls && itemId !== sugerido) enviarFeedback(sugerido, itemId, cls); // aprende com a correção (só os ids)
  const head = $("classHead");
  const statusEl = $("extractStatus");
  if (!alvo.implementado) {
    head.innerHTML = "";
    head.appendChild(el("strong", "", `Escolhido: ${alvo.item}`));
    head.appendChild(el("p", "", "O mapeamento deste formulário do Lattes já existe, mas o preenchimento automático ainda não está pronto. Seu documento continua guardado nesta sessão por 30 minutos."));
    $("classPanel").classList.remove("ok", "escolher");
    $("classPanel").classList.add("duvida");
    $("classCards").innerHTML = "";
    return;
  }
  if (!classCtx.uploadId && !classCtx.texto && TIPO_DO_ITEM[itemId]) {
    // sem documento: abre o formulário em branco do tipo escolhido (formulários fixos do app)
    setFormData({ tipo_producao: TIPO_DO_ITEM[itemId] || "anais", situacao_orientacao: itemId === "orientacao_andamento" ? "Em andamento" : "Concluída" });
    statusEl.textContent = `Formulário em branco de: ${alvo.item}. Preencha os campos ou envie um documento.`;
    statusEl.classList.remove("hidden");
    $("classPanel").classList.add("hidden");
    return;
  }
  const corpo = { item: itemId, usuario: $("ownerName").value };
  if (classCtx.uploadId) corpo.id = classCtx.uploadId;
  else corpo.texto = classCtx.texto || " "; // sem documento: formulário em branco do item por especificação
  const r = await fetch("/api/classificacao/interpretar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  const json = await r.json();
  if (r.status === 410) {
    showToast("O arquivo venceu no servidor. Envie de novo.");
    return;
  }
  if (!r.ok || !json.extracted) {
    showToast(json.error || "Não consegui ler o documento como esse item.");
    return;
  }
  let notes = "";
  if (json.generico) {
    mostrarGenerico(json.generico);
  } else {
    genOcultar();
    setFormData(json.extracted);
    notes = (json.extracted.extraction_notes || []).join(" ");
  }
  statusEl.textContent = `Lido como: ${alvo.item}. ${notes}`;
  statusEl.classList.remove("hidden");
  if (notes.includes("ATENÇÃO")) showToast("Atenção: o usuário selecionado não consta neste documento.");
  $("classHead").innerHTML = "";
  $("classHead").appendChild(el("strong", "", `✅ Usando: ${alvo.item}`));
  $("classCards").innerHTML = "";
  $("classRel").textContent = "";
  $("classChooser").classList.add("hidden");
  $("classPanel").classList.remove("duvida", "escolher");
  $("classPanel").classList.add("ok");
}

$("btnOutroTipo").onclick = abrirChooser;
$("intentDoc").onclick = () => { revelarPassos("doc"); $("stepUpload").scrollIntoView({ behavior: "smooth", block: "start" }); };
$("btnEscolherManual").onclick = () => {
  revelarPassos("manual");
  classCtx = { uploadId: null, texto: null, json: null };
  const painel = $("classPanel");
  painel.classList.remove("ok", "duvida");
  painel.classList.add("escolher");
  $("classHead").innerHTML = "";
  $("classHead").appendChild(el("strong", "", "O que você quer registrar?"));
  $("classHead").appendChild(el("p", "", "Escolha o tipo e abrimos o formulário. Se tiver o documento depois, é só enviar."));
  $("classCards").innerHTML = "";
  $("classRel").textContent = "";
  abrirChooser();
};
$("chooserBusca").addEventListener("input", renderChooser);

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

// O número ao lado de "Registros" soma os registros salvos e os envios ao Lattes.
function atualizarContadorRegistros() {
  const el = $("recordsCount");
  if (el) el.textContent = (window.__nRegistros || 0) + (window.__nEnvios || 0);
}

async function loadRecords() {
  const resp = await fetch("/api/records");
  const json = await resp.json();
  const records = json.records || [];
  window.__nRegistros = records.length;
  atualizarContadorRegistros();
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
      voltarCadastro();
      abrirRegistroAntigo(rec.data);
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

// Registros no formato antigo (caderno de resumos, histórico): anais e artigo abrem no formulário gerado pelo spec; os demais, no formulário antigo.
async function abrirRegistroAntigo(data) {
  const tp = (data && data.tipo_producao) || "anais"; // sem tipo, o formulário antigo também assumia anais
  if (data && (tp === "anais" || tp === "artigo" || tp === "apresentacao" || tp === "orientacao")) {
    try {
      const r = await (await fetch("/api/itens/abrir-registro", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ data, item: tp }) })).json();
      if (r.generico) { mostrarGenerico(r.generico); return true; }
    } catch (e) { /* cai no formulário antigo */ }
  }
  setFormData(data);
  return false;
}

function loadCadernoRecord(r) {
  abrirRegistroAntigo(r.record);
  const notes = (r.record.extraction_notes || []).join(" ");
  const st = $("extractStatus");
  st.textContent = `Resumo da pág. ${r.page_label || r.pdf_page} carregado. ${notes}`;
  st.classList.remove("hidden");
  showToast("Resumo carregado no formulário!");
  ($("formGenerico") && !$("formGenerico").classList.contains("hidden") ? $("formGenerico") : $("lattesForm")).scrollIntoView({ behavior: "smooth" });
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
// Usuário em teste: define quem está logado no LattesData (dono dos registros, autor buscado no caderno
// e titular esperado no Lattes). Guardado só neste navegador.
function applyUser(name, { persist = true } = {}) {
  $("ownerName").value = name;
  try { $("citacaoNome").value = localStorage.getItem("lf-citacao:" + name) || ""; } catch (e) {}
  $("searchUser").textContent = name;
  $("guideUser").textContent = name;
  if (persist) {
    try { localStorage.setItem("lf-usuario", name); } catch (e) {}
  }
  $("cadernoResults").innerHTML = "";
  updateBookmarklet();
}
$("citacaoNome").addEventListener("input", () => {
  try { localStorage.setItem("lf-citacao:" + $("ownerName").value, $("citacaoNome").value.trim()); } catch (e) {}
  updateBookmarklet();
});

// O Lattes só aceita o cadastro se o nome em citações de UM autor for igual a um dos nomes cadastrados no currículo
// do titular. Se o usuário informou o dele, ele vale para o autor que é o titular.
function aplicarCitacaoTitular(d) {
  const cit = $("citacaoNome") ? $("citacaoNome").value.trim() : "";
  if (!cit || !d || !Array.isArray(d.autores)) return d;
  const t = nameTokens($("ownerName").value);
  const autores = d.autores.map((a) => {
    const b = nameTokens(a && a.nome);
    const ehTitular = t.length > 0 && b.length > 0 && t[0] === b[0] && t[t.length - 1] === b[b.length - 1];
    return ehTitular ? { ...a, citacao: cit } : a;
  });
  return { ...d, autores };
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

$("btnLoadSample").onclick = async () => {
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
  try {
    const resp = await fetch("/exemplos/2024-SEMICresumo.pdf");
    if (resp.ok) {
      currentUploadedFile = await resp.blob();
      currentUploadId = "sample";
    }
  } catch (e) {}
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
  updateStandardizedDossieName();
};

$("btnAddKeyword").onclick = () => {
  const val = $("newKeywordInput").value.trim();
  if (!val) return;
  state.palavras_chave.push(val);
  $("newKeywordInput").value = "";
  renderChips();
  updateCompleteness();
  updateBookmarklet();
  updateStandardizedDossieName();
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
      updateStandardizedDossieName();
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
    // Canal 1: aba aberta pelo LattesData (window.opener). Canal 2: aviso ao servidor, funciona com qualquer aba.
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
  alert(n ? 'LattesData conectado. Currículo aberto: ' + n : 'LattesData conectado, mas ainda não há currículo aberto. Faça login no Lattes; o status atualiza sozinho.');
})();`;

function getSid() {
  // Identifica este navegador junto ao servidor, para o aviso do conector chegar só a esta página.
  try {
    let s = localStorage.getItem("lf-sid2");
    if (!s) {
      s = randomId(16);
      localStorage.setItem("lf-sid2", s);
    }
    return s;
  } catch (e) {
    window.__lfSidMem = window.__lfSidMem || randomId(16);
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
  card.className = `lattes-pop state-${state}${card.classList.contains("hidden") ? " hidden" : ""}`;
  $("lcTitle").textContent = title;
  $("lcDetail").textContent = detail;
  const pill = $("lattesPill");
  pill.className = `lattes-pill state-${state}`;
  $("lattesPillText").textContent = { on: "Lattes conectado", mismatch: "Lattes: outro usuário", wait: "Lattes: aguardando", off: "Lattes desconectado" }[state];
}

function openLattesTab() {
  // Sem "noopener": a aba do Lattes precisa de window.opener para o conector avisar o status.
  window.open(LATTES_URL, "lattesfacil_lattes");
  lattesState.opened = true;
  renderLattesStatus();
}

window.addEventListener("message", (e) => {
  if (e.origin !== LATTES_ORIGIN && e.origin !== location.origin) return; // sinais do Lattes ou da extensão LattesData
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
function togglePopLattes(abrir) {
  const pop = $("lattesConnect"), pill = $("lattesPill");
  const open = abrir === undefined ? pop.classList.contains("hidden") : abrir;
  pop.classList.toggle("hidden", !open);
  pill.setAttribute("aria-expanded", String(open));
}
$("lattesPill").onclick = (e) => { e.stopPropagation(); togglePopLattes(); };
document.addEventListener("click", (e) => { if (!e.target.closest(".lattes-wrap")) togglePopLattes(false); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") togglePopLattes(false); });
$("ownerName").addEventListener("change", renderLattesStatus);

// Menu do usuário (avatar): troca de usuário em teste e saída.
function atualizarAvatar() {
  const partes = nameTokens($("ownerName").value);
  const ini = partes.length ? (partes[0][0] + (partes.length > 1 ? partes[partes.length - 1][0] : "")).toUpperCase() : "?";
  $("avatarIni").textContent = ini;
}
function toggleUserMenu(abrir) {
  const menu = $("userMenu"), btn = $("avatarBtn");
  const open = abrir === undefined ? menu.classList.contains("hidden") : abrir;
  menu.classList.toggle("hidden", !open);
  btn.setAttribute("aria-expanded", String(open));
}
$("avatarBtn").onclick = (e) => { e.stopPropagation(); toggleUserMenu(); };
document.addEventListener("click", (e) => { if (!e.target.closest(".user-wrap")) toggleUserMenu(false); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") toggleUserMenu(false); });
$("ownerName").addEventListener("change", atualizarAvatar);
atualizarAvatar();
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

// Resultado do envio ao Lattes, que fica na tela (o aviso rápido some). Só textContent: o texto vem de outra página.
function mostrarResultadoLattes(m) {
  const box = $("lattesResultado");
  if (!box || !m) return;
  // Sem "estado" = resposta imediata da extensão (ainda em andamento); com estado = resultado final do preenchimento.
  const VISUAL = { removido: "ok", ausente: "atencao", login: "atencao", divergente: "erro", "nao-suportado": "atencao" };
  const estado = ["ok", "atencao", "erro"].includes(m.estado) ? m.estado : (VISUAL[m.estado] || (m.ok ? "andando" : "erro"));
  const cores = { andando: ["#f0f9ff", "#bae6fd", "#0369a1", "⏳"], ok: ["#ecfdf5", "#6ee7b7", "#047857", "✅"], atencao: ["#fffbeb", "#fcd34d", "#92400e", "⚠️"], erro: ["#fef2f2", "#fca5a5", "#b91c1c", "❌"] }[estado];
  box.style.cssText = `margin-top:12px;padding:12px 14px;border-radius:10px;border:1px solid ${cores[1]};background:${cores[0]};color:${cores[2]};`;
  box.textContent = "";
  const t = document.createElement("strong");
  t.textContent = `${cores[3]} Lattes: ${String(m.message || "").slice(0, 300)}`;
  box.appendChild(t);
  const det = Array.isArray(m.detalhes) ? m.detalhes.slice(0, 8) : [];
  if (det.length) {
    const ul = document.createElement("ul");
    ul.style.cssText = "margin:6px 0 0;padding-left:18px;font-size:0.9rem";
    det.forEach((x) => { const li = document.createElement("li"); li.textContent = String(x).slice(0, 300); ul.appendChild(li); });
    box.appendChild(ul);
  }
  if (["ok", "atencao", "erro"].includes(m.estado) || m.estado === "removido") {
    const ver = document.createElement("button");
    ver.type = "button";
    ver.className = "btn btn-sm btn-secondary";
    ver.style.marginTop = "8px";
    ver.textContent = "📚 Ver em Registros";
    ver.onclick = () => {
      mostrarRegistros();
    };
    box.appendChild(ver);
  }
  box.classList.remove("hidden");
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------- Envios ao Lattes: registro, verificação e remoção ----------
const TIPO_ROTULO = { apresentacao: "Apresentação de trabalho", anais: "Trabalho em anais", artigo: "Artigo", orientacao: "Orientação", orientacao_concluida: "Orientação concluída", orientacao_andamento: "Orientação em andamento", generico: "Outro item" };
const STATUS_ENVIO = {
  enviando: ["⏳ Enviando", "#0369a1"],
  salvo: ["✅ Salvo no Lattes", "#047857"],
  preenchido: ["📝 Preenchido (falta salvar)", "#92400e"],
  atencao: ["⚠️ Conferir no Lattes", "#92400e"],
  erro: ["❌ Erro", "#b91c1c"],
  removendo: ["⏳ Removendo…", "#0369a1"],
  removido: ["🗑️ Removido do Lattes", "#475569"],
  falha_remocao: ["❌ Falha ao remover", "#b91c1c"],
};
const LIMITE_REMOCAO_MS = 120000; // depois disso, "Removendo…" sem resposta volta a oferecer as ações
const REMOCAO_SUPORTADA = new Set(["apresentacao"]); // tipos com leitura de lista e Excluir mapeados no Lattes
// os demais itens com lista mapeada (itens/listas_lattes.json) vêm do servidor
fetch("/api/itens/listas").then((r) => (r.ok ? r.json() : null)).then((j) => {
  if (j && Array.isArray(j.itens)) { j.itens.forEach((i) => REMOCAO_SUPORTADA.add(i)); if (typeof renderEnvios === "function") try { renderEnvios(); } catch (e) {} }
}).catch(() => {});
let enviosCache = [];

function fmtDataHora(iso) {
  const d = new Date(iso);
  return isNaN(d) ? "" : d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

async function carregarEnvios() {
  const lista = $("enviosLista");
  if (!lista) return;
  try {
    const r = await fetch("/api/lattes/envios?owner=" + encodeURIComponent($("ownerName").value), { cache: "no-store" });
    const j = await r.json();
    enviosCache = Array.isArray(j.envios) ? j.envios : [];
  } catch (e) {
    return;
  }
  window.__nEnvios = enviosCache.length;
  atualizarContadorRegistros();
  renderEnvios();
}

async function criarEnvio(dados) {
  try {
    const r = await fetch("/api/lattes/envios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ owner: $("ownerName").value, titulo: dados.titulo, tipo: dados.tipo_producao === "orientacao" && dados.situacao_orientacao === "Em andamento" ? "orientacao_andamento" : dados.tipo_producao, ano: dados.ano }),
    });
    const j = await r.json();
    return j.id || "";
  } catch (e) {
    return "";
  }
}

async function atualizarEnvio(id, status, mensagem, seq) {
  try {
    await fetch("/api/lattes/envios/" + encodeURIComponent(id), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, mensagem: mensagem || "", lattes_seq: seq || "" }),
    });
  } catch (e) {}
  await carregarEnvios();
}

// Resultado final vindo da extensão (preenchimento, verificação ou remoção) -> atualiza o registro.
function processarResultadoEnvio(m) {
  if (!m || !m.envioId || !m.estado) return; // resposta imediata (sem estado) não muda nada
  const ev = m.evento || "preenchimento";
  const msg = String(m.message || "");
  const seq = String(m.seq || "");
  if (ev === "preenchimento") {
    const status = m.estado === "ok" ? (seq ? "salvo" : "preenchido") : m.estado === "atencao" ? "atencao" : "erro";
    atualizarEnvio(m.envioId, status, msg, seq);
  } else if (ev === "verificacao") {
    if (m.estado === "ok") atualizarEnvio(m.envioId, "salvo", msg, seq);
    else if (m.estado === "ausente") atualizarEnvio(m.envioId, "atencao", msg, "");
    else carregarEnvios();
  } else if (ev === "remocao") {
    if (m.estado === "removido" || m.estado === "ausente") atualizarEnvio(m.envioId, "removido", msg, seq);
    else if (m.estado === "login") atualizarEnvio(m.envioId, "salvo", msg, ""); // não chegou a remover: volta ao estado anterior
    else atualizarEnvio(m.envioId, "falha_remocao", msg, seq);
  }
}

// ---------- Aviso "alterações ainda não enviadas ao CNPq" ----------
// Edições no Lattes só valem para o CNPq e a busca pública depois do envio definitivo. A extensão lê o quadro de avisos
// e, quando o usuário confirma aqui, abre a tela de envio do Lattes; o clique final em Enviar é do usuário.
const PEND_ROTULO = {
  abrindo: ["⏳ Procurando o aviso no Lattes…", "#475569"],
  pendente: ["⚠️ Há alterações pendentes de envio ao CNPq", "#b45309"],
  aguardando_envio: ["⏳ Tela de envio aberta no Lattes: falta você clicar em Enviar", "#b45309"],
  em_dia: ["✅ Nenhuma alteração pendente (o CNPq tem a versão atual)", "#047857"],
  login: ["🔐 Entre no Lattes e verifique de novo", "#475569"],
  indisponivel: ["ℹ️ Abra o seu currículo no Lattes e verifique de novo", "#475569"],
  erro: ["❌ Não consegui concluir", "#b91c1c"],
};

function extensaoCv() {
  if (!window.__lattesExtAtiva) { showToast("Instale a extensão LattesData para falar com o Lattes."); return false; }
  if (versaoMenor(window.__lattesExtVersao, "0.6.0")) { showToast("Atualize a extensão LattesData (versão 0.6.0 ou mais nova) para usar esta função."); return false; }
  return true;
}

function atualizarCartaoPendencia(m) {
  const txt = $("cvPendTexto"), env = $("btnCvEnviar");
  if (!txt) return;
  const [rotulo, cor] = PEND_ROTULO[m.estado] || [m.estado, "#475569"];
  txt.textContent = rotulo + (m.message ? " — " + m.message : "");
  txt.style.color = cor;
  if (env && m.estado !== "abrindo") env.classList.toggle("hidden", !["pendente", "aguardando_envio"].includes(m.estado));
}

function verificarPendenciaCv() {
  if (!extensaoCv()) return;
  const txt = $("cvPendTexto");
  if (txt) { txt.textContent = "Verificando o quadro de avisos do Lattes…"; txt.style.color = "#475569"; }
  window.postMessage({ type: "lattesdata-ext-cv-status" }, location.origin);
}

function enviarCurriculoAoCnpq() {
  if (!extensaoCv()) return;
  const ok = window.confirm(
    "Enviar o currículo ao CNPq?\n\n" +
    "• Vou abrir a tela de envio na aba do Lattes; o clique final em Enviar é seu.\n" +
    "• Depois do envio, as suas alterações passam a valer para o CNPq e para a busca pública, substituindo a versão anterior.\n" +
    "• Se quiser guardar a versão atual antes, importe o XML em \"Meu currículo\" primeiro.\n\n" +
    "Abrir a tela de envio agora?");
  if (!ok) return;
  window.postMessage({ type: "lattesdata-ext-cv-publish" }, location.origin);
}

document.addEventListener("DOMContentLoaded", () => {
  const v = $("btnCvVerificar"), e = $("btnCvEnviar");
  if (v) v.onclick = verificarPendenciaCv;
  if (e) e.onclick = enviarCurriculoAoCnpq;
});

function pedirVerificacao(e) {
  if (!window.__lattesExtAtiva) { showToast("Instale a extensão LattesData para verificar no Lattes."); return; }
  window.postMessage({ type: "lattesdata-ext-verify", envioId: e.id, tipo: e.tipo, titulo: e.titulo, seq: e.lattes_seq || "" }, location.origin);
  showToast("Verificando no Lattes…");
}

async function pedirRemocao(e) {
  if (!window.__lattesExtAtiva) { showToast("Instale a extensão LattesData para remover do Lattes."); return; }
  const ok = window.confirm(
    "Remover do Lattes?\n\n“" + e.titulo + "”\n\nIsto EXCLUI o item do seu Currículo Lattes e não pode ser desfeito pelo LattesData. Continuar?"
  );
  if (!ok) return;
  await atualizarEnvio(e.id, "removendo", "Removendo no Lattes…", "");
  window.postMessage({ type: "lattesdata-ext-remove", envioId: e.id, tipo: e.tipo, titulo: e.titulo, seq: e.lattes_seq || "" }, location.origin);
  showToast("Pedido de remoção enviado ao Lattes. Acompanhe o painel na aba do Lattes.");
}

async function tirarDaLista(e) {
  try { await fetch("/api/lattes/envios/" + encodeURIComponent(e.id), { method: "DELETE" }); } catch (err) {}
  carregarEnvios();
}

function renderEnvios() {
  const lista = $("enviosLista");
  if (!lista) return;
  lista.textContent = "";
  if (!enviosCache.length) {
    const p = document.createElement("p");
    p.className = "hint";
    p.textContent = "Nenhum envio registrado para este usuário ainda. Os próximos envios ao Lattes aparecem aqui.";
    lista.appendChild(p);
    return;
  }
  enviosCache.forEach((e) => {
    // "Removendo…" sem resposta da extensão por mais de 2 min (aba do Lattes recarregada, extensão reiniciada...) não pode prender o
    // cartão: devolve Verificar, Remover de novo e Tirar da lista.
    const parado = e.status === "removendo" && Date.now() - new Date(e.atualizado_em || e.enviado_em).getTime() > LIMITE_REMOCAO_MS;
    const [rotulo, cor] = parado ? ["⚠️ Remoção sem resposta", "#92400e"] : (STATUS_ENVIO[e.status] || [e.status, "#475569"]);
    const box = document.createElement("div");
    box.style.cssText = "border:1px solid #e2e8f0;border-left:5px solid " + cor + ";border-radius:10px;padding:10px 12px;margin:8px 0;background:#fff";
    const tit = document.createElement("strong");
    tit.textContent = e.titulo;
    box.appendChild(tit);
    const meta = document.createElement("div");
    meta.className = "hint";
    meta.style.margin = "2px 0 4px";
    meta.textContent = [TIPO_ROTULO[e.tipo] || e.tipo, e.ano, "enviado em " + fmtDataHora(e.enviado_em), e.lattes_seq ? "item nº " + e.lattes_seq + " no Lattes" : ""].filter(Boolean).join(" • ");
    box.appendChild(meta);
    const st = document.createElement("div");
    st.style.cssText = "font-weight:600;color:" + cor;
    st.textContent = rotulo + (parado ? " — a extensão não respondeu em 2 minutos. Use Verificar no Lattes para ver se o item saiu, ou tente remover de novo." : (e.mensagem ? " — " + e.mensagem : ""));
    box.appendChild(st);
    const XML_ROTULO = {
      confirmado: "✅ Confirmado pelo XML do Lattes",
      ausente: "⚠️ Não consta no XML importado (confira se o XML é posterior ao envio)",
      xml_anterior: "ℹ️ O XML importado é anterior a este envio; importe um novo para confirmar",
      remocao_confirmada: "✅ Remoção confirmada pelo XML",
      ainda_presente: "⚠️ Ainda consta no XML importado",
    };
    if (e.xml_status && XML_ROTULO[e.xml_status]) {
      const x = document.createElement("div");
      x.className = "hint";
      x.style.marginTop = "2px";
      x.textContent = XML_ROTULO[e.xml_status] + (e.xml_verificado_em ? " (" + fmtDataHora(e.xml_verificado_em) + ")" : "");
      box.appendChild(x);
    }

    const acoes = document.createElement("div");
    acoes.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;margin-top:8px";
    const btn = (txt, fn, classe) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "btn btn-sm " + (classe || "btn-secondary");
      b.textContent = txt;
      b.onclick = fn;
      acoes.appendChild(b);
    };
    const suportado = REMOCAO_SUPORTADA.has(e.tipo);
    if (e.status !== "removido" && suportado) btn("🔎 Verificar no Lattes", () => pedirVerificacao(e));
    if ((["salvo", "atencao", "falha_remocao"].includes(e.status) || parado) && suportado) btn(parado ? "🗑️ Tentar remover de novo" : "🗑️ Remover do Lattes", () => pedirRemocao(e), "btn-accent");
    if (e.status !== "removido" && !suportado) {
      const nota = document.createElement("span");
      nota.className = "hint";
      nota.textContent = "Verificação e remoção automáticas ainda não existem para este tipo: confira ou remova direto no Lattes.";
      acoes.appendChild(nota);
    }
    if (e.status !== "removendo" || parado) btn("Tirar da lista", () => tirarDaLista(e));
    box.appendChild(acoes);
    lista.appendChild(box);
  });
}

if ($("btnAtualizarEnvios")) $("btnAtualizarEnvios").onclick = carregarEnvios;
setInterval(() => { if (enviosCache.some((x) => x.status === "removendo")) renderEnvios(); }, 15000); // o cartão sai de "Removendo…" sozinho
$("ownerName").addEventListener("change", carregarEnvios);
carregarEnvios();

async function dispararEnvioExtensao() {
  const data = getFormData();
  if (!data.titulo) {
    showToast("Carregue ou preencha ao menos o título antes de enviar ao Lattes.");
    return false;
  }
  const usuario = $("ownerName") ? $("ownerName").value : "";
  const autoSalvar = !!($("autoSaveLattes") && $("autoSaveLattes").checked);
  const dados = { ...aplicarCitacaoTitular(sanitizeDataPayload(data)), __usuario: usuario, __origem: location.origin, __autoSalvar: autoSalvar };
  const btnExt = $("btnEnviarExtensao");
  const btnOpen = $("btnOpenLattes");
  if (btnExt) btnExt.disabled = true;
  if (btnOpen) btnOpen.disabled = true;
  const envioId = await criarEnvio(dados); // registra o envio; o resultado dele chega depois da extensão
  if (envioId) dados.__envioId = envioId;
  carregarEnvios();
  window.postMessage({ type: "lattesdata-ext-fill", data: dados }, location.origin);
  return true;
}

// ---------- Extensão LattesData: avisar quando não está instalada ou está desatualizada ----------
const EXT_VERSAO_MINIMA = "0.9.7"; // sobe junto com extensao/manifest.json quando a extensão muda de forma incompatível

function versaoMenor(a, b) {
  const x = String(a || "0").split(".").map((n) => parseInt(n, 10) || 0);
  const y = String(b || "0").split(".").map((n) => parseInt(n, 10) || 0);
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) < (y[i] || 0);
  }
  return false;
}

let extAvisoDispensado = false;
try { extAvisoDispensado = sessionStorage.getItem("lf-ext-aviso") === "1"; } catch (e) {}

function mostrarAvisoExtensao(titulo, texto) {
  const box = $("extAviso");
  if (!box || extAvisoDispensado) return;
  $("extAvisoTitulo").textContent = titulo;
  $("extAvisoTexto").textContent = texto;
  box.classList.remove("hidden");
  box.style.display = "block";
}

function esconderAvisoExtensao() {
  const box = $("extAviso");
  if (!box) return;
  box.classList.add("hidden");
  box.style.display = "none";
}

// Chamada depois que a extensão respondeu (ou deixou de responder) ao ping.
function avaliarExtensao() {
  if (!window.__lattesExtAtiva) {
    mostrarAvisoExtensao(
      "🧩 Instale a extensão LattesData para enviar ao Lattes com 1 clique",
      "Sem ela o envio e o registro automáticos não funcionam. A instalação leva 1 minuto e é feita uma única vez, no Chrome ou no Edge."
    );
    return;
  }
  if (versaoMenor(window.__lattesExtVersao, EXT_VERSAO_MINIMA)) {
    mostrarAvisoExtensao(
      "🔄 A extensão LattesData está desatualizada (versão " + (window.__lattesExtVersao || "?") + ")",
      "Baixe a versão atual, substitua a pasta e clique em recarregar a extensão em chrome://extensions. Precisa da versão " + EXT_VERSAO_MINIMA + " ou mais nova."
    );
    return;
  }
  esconderAvisoExtensao();
}

if ($("btnExtAvisoInstalar")) $("btnExtAvisoInstalar").onclick = () => abrirModalExtensao();
if ($("btnExtAvisoDispensar")) {
  $("btnExtAvisoDispensar").onclick = () => {
    extAvisoDispensado = true;
    try { sessionStorage.setItem("lf-ext-aviso", "1"); } catch (e) {}
    esconderAvisoExtensao();
  };
}
// A extensão responde em milissegundos; se em 2 s não respondeu, considera ausente (e reavalia ao reconectar).
window.setTimeout(avaliarExtensao, 2000);

function fecharModalAtivador() {
  const modal = $("ativadorModal");
  if (modal) modal.classList.add("hidden");
}

function abrirModalExtensao() {
  const modal = $("ativadorModal");
  if (!modal) {
    openLattesTab();
    $("lattesGuide").classList.remove("hidden");
    return;
  }
  modal.classList.remove("hidden");
}

if ($("btnCloseAtivadorModal")) {
  $("btnCloseAtivadorModal").onclick = fecharModalAtivador;
}
if ($("ativadorModal")) {
  $("ativadorModal").onclick = (e) => {
    if (e.target === $("ativadorModal")) fecharModalAtivador();
  };
}
if ($("btnModalManualLattes")) {
  $("btnModalManualLattes").onclick = async () => {
    fecharModalAtivador();
    openLattesTab();
    try { await navigator.clipboard.writeText(buildLattesAutofillScript(getFormData())); } catch (e) {}
    $("lattesGuide").classList.remove("hidden");
    showToast("Lattes aberto e script copiado! Faça login e cole no Console (F12) ou use o Favorito.");
    $("lattesGuide").scrollIntoView({ behavior: "smooth", block: "center" });
  };
}

// Enviar ao Lattes: com a extensão instalada é 1 clique (ela abre o login, espera você entrar e preenche).
// Sem a extensão, mostra como instalar (uma única vez).
$("btnOpenLattes").onclick = () => {
  const data = getFormData();
  if (!data.titulo) {
    showToast("⚠️ Carregue um comprovante no Passo 2 ou preencha o campo Título antes de enviar ao Lattes.");
    const titEl = $("titulo");
    if (titEl) {
      titEl.scrollIntoView({ behavior: "smooth", block: "center" });
      titEl.focus();
    }
    return;
  }
  if (window.__lattesExtAtiva && !versaoMenor(window.__lattesExtVersao, EXT_VERSAO_MINIMA)) {
    dispararEnvioExtensao();
    return;
  }
  abrirModalExtensao();
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

// "Registros" é uma aba própria: #registros mostra só o painel de registros; sem o hash, volta o Cadastrar.
function aplicarVista() {
  const emRegistros = location.hash === "#registros";
  document.body.classList.toggle("view-registros", emRegistros);
  $("historyPanel").classList.toggle("hidden", !emRegistros);
  const b = $("btnToggleHistory");
  if (emRegistros) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
  const cad = document.querySelector('.topnav a[href="/"]');
  if (cad) { if (emRegistros) cad.removeAttribute("aria-current"); else cad.setAttribute("aria-current", "page"); }
  if (emRegistros) { loadRecords(); carregarEnvios(); window.scrollTo(0, 0); }
}
function mostrarRegistros() { if (location.hash === "#registros") aplicarVista(); else location.hash = "#registros"; }
function voltarCadastro() { history.pushState(null, "", location.pathname + location.search); aplicarVista(); }
window.addEventListener("hashchange", aplicarVista);
$("btnToggleHistory").onclick = mostrarRegistros;
$("btnCloseHistory").onclick = voltarCadastro;
document.querySelector('.topnav a[href="/"]').addEventListener("click", (e) => { if (location.hash === "#registros") { e.preventDefault(); voltarCadastro(); } });
aplicarVista();

// Modal de Avaliação & Diagnóstico Lattes (Lattes Shield) & Radar Online
const auditModal = $("auditModal");
const KNOWN_ORCIDS = {
  "Aramys Silva dos Reis": "0000-0003-4999-6382",
};

let radarObrasCache = [];

function carregarObraNoForm(obra) {
  if (auditModal) auditModal.classList.add("hidden");
  const tipo = "artigo";
  $("tipo_producao").value = tipo;
  applyTipoProducao(tipo);

  if ($("titulo")) $("titulo").value = obra.titulo || "";
  if ($("doi")) $("doi").value = obra.doi || "";
  if ($("ano")) $("ano").value = obra.ano || "";
  if ($("periodico")) $("periodico").value = obra.veiculo || "";
  if ($("idioma")) $("idioma").value = "Português";
  if ($("pais")) $("pais").value = "Brasil";
  if ($("meio_divulgacao")) $("meio_divulgacao").value = "meio digital";

  if (Array.isArray(obra.autores) && obra.autores.length > 0) {
    const skip = new Set(["da", "de", "do", "das", "dos", "e"]);
    state.autores = obra.autores.map((nomeStr) => {
      const trimmed = String(nomeStr).trim();
      const parts = trimmed.split(/\s+/);
      const cit = parts.length > 1
        ? `${parts[parts.length - 1].toUpperCase()}, ${parts.slice(0, -1).filter((p) => !skip.has(p.toLowerCase())).map((p) => p[0].toUpperCase() + ".").join(" ")}`
        : trimmed.toUpperCase();
      return { nome: trimmed, citacao: cit };
    });
  } else {
    state.autores = [];
  }

  renderChips();
  updateCompleteness();
  updateBookmarklet();
  showToast(`✨ Obra resgatada pelo Radar carregada no formulário!`);
  const form = $("lattesForm");
  if (form) form.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function carregarRadarObras(force = false) {
  const container = $("auditRadarItems");
  if (!container) return;
  const user = $("ownerName") ? $("ownerName").value.trim() : "Aramys Silva dos Reis";
  const orcid = KNOWN_ORCIDS[user] || "";

  if (container.dataset.loadedUser === user && !force && radarObrasCache.length > 0) {
    return;
  }

  container.innerHTML = `
    <div style="text-align: center; padding: 14px; color: #475569;">
      <span style="display:inline-block; margin-right:6px;">⏳</span>
      Varrendo OpenAlex & CrossRef em busca de produções reais de <strong>${user}</strong>...
    </div>
  `;
  const badge = $("auditRadarBadge");
  if (badge) badge.textContent = "Buscando...";

  try {
    const params = new URLSearchParams({ autor: user });
    if (orcid) params.set("orcid", orcid);
    const resp = await fetch(`/api/radar?${params.toString()}`);
    if (!resp.ok) throw new Error("Falha na resposta do servidor");
    const json = await resp.json();
    const obras = json.obras || [];
    radarObrasCache = obras;
    container.dataset.loadedUser = user;

    if (obras.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 12px; color: #64748b;">
          Nenhuma obra recente localizada nas APIs para este autor.
        </div>
      `;
      if (badge) badge.textContent = "0 Encontradas";
      return;
    }

    if (badge) badge.textContent = `+${obras.length * 10} Pontos (${obras.length} Obras)`;
    container.innerHTML = "";

    obras.forEach((obra) => {
      const itemEl = document.createElement("div");
      itemEl.className = "radar-item";

      const infoDiv = document.createElement("div");
      infoDiv.style.flex = "1";
      infoDiv.style.minWidth = "0";

      const titleStrong = document.createElement("strong");
      titleStrong.textContent = (obra.veiculo ? "Artigo: " : "Trabalho: ");
      infoDiv.appendChild(titleStrong);

      const titleSpan = document.createElement("span");
      titleSpan.textContent = obra.titulo;
      infoDiv.appendChild(titleSpan);

      const metaSpan = document.createElement("span");
      metaSpan.className = "radar-meta";
      const metaParts = [];
      if (obra.ano) metaParts.push(`Ano: ${obra.ano}`);
      if (obra.veiculo) metaParts.push(obra.veiculo);
      if (obra.doi) metaParts.push(`DOI: ${obra.doi}`);
      if (obra.autores && obra.autores.length > 0) {
        metaParts.push(`Autores: ${obra.autores.slice(0, 3).join(", ")}${obra.autores.length > 3 ? " et al." : ""}`);
      }
      metaSpan.textContent = metaParts.join(" • ");
      infoDiv.appendChild(metaSpan);

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-sm btn-accent";
      btn.textContent = "📥 Carregar no Form";
      btn.onclick = () => carregarObraNoForm(obra);

      itemEl.appendChild(infoDiv);
      itemEl.appendChild(btn);
      container.appendChild(itemEl);
    });
  } catch (err) {
    console.error("Falha ao buscar obras do radar:", err);
    container.innerHTML = `
      <div style="text-align: center; padding: 12px; color: #dc2626;">
        ⚠️ Erro ao consultar bases online. Clique em "Escanear Obras" para tentar novamente.
      </div>
    `;
    if (badge) badge.textContent = "Erro na Busca";
  }
}

if ($("btnOpenAuditModal") && auditModal) {
  $("btnOpenAuditModal").onclick = () => {
    const user = $("ownerName") ? $("ownerName").value : "Aramys Silva dos Reis";
    if ($("auditModalUser")) $("auditModalUser").textContent = user;
    auditModal.classList.remove("hidden");
    carregarRadarObras();
  };
  if ($("btnCloseAuditModal")) {
    $("btnCloseAuditModal").onclick = () => auditModal.classList.add("hidden");
  }
  auditModal.onclick = (e) => {
    if (e.target === auditModal) auditModal.classList.add("hidden");
  };
}

function escCit(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function buscarCitacoes() {
  const out = $("citacoesResultado");
  const orcid = ($("citOrcid").value || "").trim();
  const dois = ($("citDois").value || "").trim();
  if (!orcid && !dois) { out.textContent = "Informe um ORCID ou ao menos um DOI."; return; }
  out.textContent = "Consultando as bases…";
  const qs = new URLSearchParams();
  if (orcid) qs.set("orcid", orcid);
  if (dois) qs.set("doi", dois);
  try {
    const r = await fetch(`/api/citacoes?${qs}`);
    const d = await r.json();
    if (!d.ok) { out.textContent = d.error || "Falha na consulta."; return; }
    const s = d.resumo;
    const anos = Object.entries(s.por_ano).map(([a, n]) => `${escCit(a)}: ${n}`).join(" · ");
    let html = `<p><strong>${s.citacoes_unicas}</strong> citações únicas em ${s.obras} obra(s) (${s.autocitacoes} autocitações). ${anos ? "Por ano — " + anos : ""}</p>`;
    html += d.obras.map((o) => {
      const f = o.contagem_fontes;
      const lista = o.citantes.slice(0, 15).map((c) =>
        `<li>${escCit(c.titulo || c.doi || "(sem título)")} ${c.ano ? "(" + escCit(c.ano) + ")" : ""}` +
        `${c.doi ? ` — <a href="https://doi.org/${encodeURIComponent(c.doi).replace(/%2F/g, "/")}" target="_blank" rel="noopener">DOI</a>` : ""}` +
        ` <small>[${c.fontes.map(escCit).join(", ")}${c.autocitacao ? ", autocitação" : ""}]</small></li>`).join("");
      return `<details><summary><strong>${escCit(o.titulo || o.doi)}</strong> — ${o.total_unico}${o.truncado ? "+" : ""} únicas ` +
        `<small>(OpenAlex ${f.openalex}, OpenCitations ${f.opencitations}, Crossref ${f.crossref ?? "—"}${o.truncado ? "; lista parcial, total estimado " + o.total_estimado : ""})</small></summary><ul>${lista}</ul></details>`;
    }).join("");
    out.innerHTML = html;
  } catch (e) {
    out.textContent = "Erro de rede ao consultar citações.";
  }
}
if ($("btnBuscarCitacoes")) $("btnBuscarCitacoes").onclick = buscarCitacoes;

if ($("btnScanRadar")) {
  $("btnScanRadar").onclick = () => carregarRadarObras(true);
}

if ($("btnLoadRadarItem")) {
  $("btnLoadRadarItem").onclick = () => {
    carregarObraNoForm({
      titulo: "IMPORTÂNCIA DO FARMACÊUTICO NO CUIDADO AO PACIENTE HIPERTENSO: UMA REVISÃO DE LITERATURA",
      doi: "10.29327/2239332.2.2-13",
      ano: "2023",
      veiculo: "Revista Científica de Saúde",
      autores: ["Aramys Silva dos Reis"]
    });
  };
}

updateCompleteness();
updateBookmarklet();
loadRecords();
// (updateStandardizedDossieName() é chamada logo depois de STOP_WORDS_SET, abaixo: antes dava erro de inicialização)

// ==========================================================================
// Dossiê Acadêmico & Padronizador de Comprovantes (CAPES / CNPq)
// ==========================================================================

let currentUploadedFile = null;
let currentUploadId = null;
let currentStandardFileName = "2024_ARTIGO_REIS_TITULO.pdf";

const STOP_WORDS_SET = new Set([
  "DE", "DO", "DA", "DOS", "DAS", "E", "EM", "NO", "NA", "NOS", "NAS",
  "PARA", "POR", "COM", "UM", "UMA", "UNS", "UMAS", "O", "A", "OS", "AS",
  "AO", "AOS", "SOBRE", "ENTRE", "SEM", "SOB", "THE", "OF", "AND", "IN", "ON", "AT", "TO", "FOR"
]);

const PARENTESCO_SET = new Set(["JUNIOR", "FILHO", "NETO", "SOBRINHO", "SEGUNDO", "TERCEIRO"]);

updateStandardizedDossieName();

function cleanAscii(str) {
  return String(str || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase()
    .replace(/[^A-Z0-9\s\-_]/g, " ")
    .trim();
}

function generateStandardName(data) {
  // Ano
  const anoMatch = String(data.ano || data.ano_evento || "").match(/\b(19\d\d|20\d\d)\b/);
  const ano = anoMatch ? anoMatch[1] : "SEM-ANO";

  // Tipo
  const mapaTipos = {
    artigo: "ARTIGO",
    periodico: "ARTIGO",
    anais: "ANAIS",
    resumo: "ANAIS",
    apresentacao: "APRESENTACAO",
    palestra: "APRESENTACAO",
    conferencia: "APRESENTACAO",
    orientacao: "ORIENTACAO",
    certificado: "CERTIFICADO",
    livro: "LIVRO",
    capitulo: "CAPITULO",
    patente: "PATENTE",
    relatorio: "RELATORIO",
  };
  const tipoBruto = (data.tipo_producao || data.tipo || data.natureza || "").toLowerCase();
  let tipo = "PRODUCAO";
  for (const [k, v] of Object.entries(mapaTipos)) {
    if (tipoBruto.includes(k)) {
      tipo = v;
      break;
    }
  }
  if (tipo === "PRODUCAO") {
    if (data.doi || data.periodico) tipo = "ARTIGO";
    else if (data.nome_evento || data.titulo_anais) tipo = "ANAIS";
    else if (data.nome_orientando || data.instituicao_orient) tipo = "ORIENTACAO";
  }

  // Primeiro autor
  let autor = "AUTOR";
  if (Array.isArray(state.autores) && state.autores.length > 0) {
    const a0 = state.autores[0];
    const raw = typeof a0 === "object" ? (a0.citacao?.split(",")[0] || a0.nome || "") : String(a0);
    const tokens = cleanAscii(raw).split(/\s+/).filter(Boolean);
    if (tokens.length > 0) {
      const last = tokens[tokens.length - 1];
      if (PARENTESCO_SET.has(last) && tokens.length > 1) {
        autor = `${tokens[tokens.length - 2]}-${last}`;
      } else {
        autor = last;
      }
    }
  } else if ($("ownerName") && $("ownerName").value) {
    const tokens = cleanAscii($("ownerName").value).split(/\s+/).filter(Boolean);
    if (tokens.length > 0) autor = tokens[tokens.length - 1];
  }

  // Slug título
  const limpoTitulo = cleanAscii(data.titulo || "DOCUMENTO");
  const words = limpoTitulo.split(/\s+/).filter(Boolean);
  let relevantes = words.filter((w) => !STOP_WORDS_SET.has(w));
  if (relevantes.length === 0) relevantes = words;

  const selected = [];
  let curLen = 0;
  for (const w of relevantes.slice(0, 5)) {
    const add = w.length + (selected.length ? 1 : 0);
    if (curLen + add > 40 && selected.length) break;
    selected.push(w);
    curLen += add;
  }
  const slug = (selected.join("-") || "DOCUMENTO").replace(/-+/g, "-");

  const base = `${ano}_${tipo}_${autor}_${slug}`
    .replace(/[^A-Z0-9_\-]/g, "")
    .replace(/_{2,}/g, "_")
    .replace(/-{2,}/g, "-");
  return `${base}.pdf`;
}

function updateStandardizedDossieName() {
  const data = getFormData();
  currentStandardFileName = generateStandardName(data);
  const el = $("standardFileName");
  if (el) {
    el.textContent = currentStandardFileName;
  }
}

async function downloadStandardizedFile() {
  const data = getFormData();
  const nome = currentStandardFileName || generateStandardName(data);

  // 1. Se temos o blob/arquivo carregado na memória do navegador
  if (currentUploadedFile) {
    const url = URL.createObjectURL(currentUploadedFile);
    const a = document.createElement("a");
    a.href = url;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast(`📥 Comprovante padronizado baixado: ${nome}`);
    return;
  }

  // 2. Se temos o uploadId registrado no servidor
  if (currentUploadId) {
    const downloadUrl = `/api/dossie/download?id=${encodeURIComponent(currentUploadId)}&nome=${encodeURIComponent(nome)}`;
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast(`📥 Baixando comprovante do servidor: ${nome}`);
    return;
  }

  // 3. Se foi carregado exemplo ou formulário manual sem arquivo, tenta obter o exemplo do SEMIC ou gera stub
  try {
    const resp = await fetch("/exemplos/2024-SEMICresumo.pdf");
    if (resp.ok) {
      currentUploadedFile = await resp.blob();
      const url = URL.createObjectURL(currentUploadedFile);
      const a = document.createElement("a");
      a.href = url;
      a.download = nome;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      showToast(`📥 Comprovante de exemplo baixado padronizado: ${nome}`);
      return;
    }
  } catch (err) {}

  // Fallback: gera stub PDF descritivo
  const stubText = `%PDF-1.4\n% Dossiê Acadêmico CAPES / CNPq\n% Arquivo: ${nome}\n% Título: ${data.titulo || "Sem título"}\n% Autor: ${state.autores?.[0]?.nome || "Autor"}\n% Ano: ${data.ano || "2024"}\n`;
  const blob = new Blob([stubText], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast(`📥 Comprovante padronizado baixado: ${nome}`);
}

const dossieModal = $("dossieModal");

async function renderDossieTree() {
  const preview = $("dossieTreePreview");
  if (!preview) return;
  preview.innerHTML = "Carregando estrutura do dossiê...";

  try {
    const rResp = await fetch("/api/records");
    const rData = await rResp.json();
    const records = rData.records || [];

    const lote = [];
    const atual = getFormData();
    if (atual.titulo || atual.ano) {
      lote.push({ dados: atual, nome_original: "producao_atual.pdf" });
    }
    records.forEach((r, idx) => {
      lote.push({ dados: r.data, nome_original: `registro_${idx + 1}.pdf` });
    });

    const res = await fetch("/api/dossie/padronizar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lote }),
    });
    const org = await res.json();

    if (!org.anos || Object.keys(org.anos).length === 0) {
      preview.innerHTML = `<span class="tree-meta">Nenhum comprovante cadastrado ainda. Envie um arquivo no Passo 2.</span>`;
      return;
    }

    let html = "";
    for (const [ano, itens] of Object.entries(org.anos)) {
      html += `<div class="tree-folder">📁 ${ano}/ <span class="tree-meta">(${itens.length} arquivo${itens.length > 1 ? "s" : ""})</span></div>`;
      itens.forEach((it, i) => {
        const isLast = i === itens.length - 1;
        const prefix = isLast ? "└──" : "├──";
        html += `<div class="tree-file">&nbsp;&nbsp;${prefix} 📄 <strong>${it.nome_padronizado}</strong> <span class="tree-meta">(${it.tipo})</span></div>`;
      });
    }
    preview.innerHTML = html;
    window.__lastDossieMd = org.relatorio_markdown || "";
    window.__lastDossieLote = lote;
  } catch (e) {
    preview.innerHTML = `<span style="color:#f87171;">Erro ao carregar estrutura: ${e.message}</span>`;
  }
}

if ($("btnOpenDossieModal") && dossieModal) {
  $("btnOpenDossieModal").onclick = () => {
    dossieModal.classList.remove("hidden");
    renderDossieTree();
  };
  if ($("btnCloseDossieModal")) {
    $("btnCloseDossieModal").onclick = () => dossieModal.classList.add("hidden");
  }
  dossieModal.onclick = (e) => {
    if (e.target === dossieModal) dossieModal.classList.add("hidden");
  };
}

if ($("btnDownloadStandardized")) {
  $("btnDownloadStandardized").onclick = downloadStandardizedFile;
}
if ($("btnDownloadStandardizedPasso3")) {
  $("btnDownloadStandardizedPasso3").onclick = downloadStandardizedFile;
}
if ($("btnCopyStandardName")) {
  $("btnCopyStandardName").onclick = async () => {
    await navigator.clipboard.writeText(currentStandardFileName);
    showToast(`📋 Nome copiado: ${currentStandardFileName}`);
  };
}

if ($("btnCopyDossieMd")) {
  $("btnCopyDossieMd").onclick = async () => {
    if (window.__lastDossieMd) {
      await navigator.clipboard.writeText(window.__lastDossieMd);
      showToast("📋 Relatório do dossiê em Markdown copiado!");
    } else {
      showToast("Abra a árvore do dossiê primeiro.");
    }
  };
}

if ($("btnDownloadDossieZip")) {
  $("btnDownloadDossieZip").onclick = async () => {
    showToast("📦 Gerando pacote ZIP do dossiê acadêmico...");
    try {
      const lote = window.__lastDossieLote || [{ dados: getFormData() }];
      const resp = await fetch("/api/dossie/zip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lote }),
      });
      if (resp.ok) {
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "dossie_academico_capes.zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        showToast("📦 Pacote ZIP baixado com sucesso!");
      } else {
        showToast("Erro ao gerar ZIP do dossiê.");
      }
    } catch (e) {
      showToast("Falha na geração do ZIP.");
    }
  };
}

// ==========================================================================
// Protocolo 3V - Conformidade CNPq Ativa & Preenchimento Duplo
// ==========================================================================
if ($("btnSanitizeForm")) {
  $("btnSanitizeForm").onclick = () => {
    const raw = getFormData();
    const sanitized = sanitizeDataPayload(raw);
    setFormData(sanitized);
    updateComplianceUI();
    showToast("✨ Metadados sanitizados com sucesso! Aspas e travessões removidos, DOI e ISBN formatados.");
  };
}

const lattesFormEl = $("lattesForm");
if (lattesFormEl) {
  lattesFormEl.addEventListener("input", () => {
    updateComplianceUI();
    updateCompleteness();
    updateBookmarklet();
  });
  lattesFormEl.addEventListener("change", () => {
    updateComplianceUI();
    updateCompleteness();
    updateBookmarklet();
  });
}

updateComplianceUI();

// Extensão LattesData: se instalada, o botão "Enviar ao Lattes" abre o formulário no Lattes, aguarda login se necessário e preenche tudo sem colar script.
(function iniciarExtensao() {
  const btn = $("btnEnviarExtensao");
  const btnOpen = $("btnOpenLattes");
  const extBox = $("extInstallBox");
  const autoSaveChk = $("autoSaveLattes");
  if (autoSaveChk) {
    autoSaveChk.addEventListener("change", () => updateBookmarklet());
  }
  window.addEventListener("message", (e) => {
    if (e.source !== window || e.origin !== location.origin) return;
    const m = e.data;
    if (!m) return;
    if (m.type === "lattesdata-ext-pong") {
      window.__lattesExtAtiva = true;
      window.__lattesExtVersao = String(m.version || "");
      avaliarExtensao();
      if (btn) btn.classList.remove("hidden");
      if (btnOpen) btnOpen.textContent = "🚀 Enviar e Cadastrar no Lattes (1-Clique)";
      if (extBox) extBox.classList.add("ext-active");
      const badge = $("extStatusBadge");
      if (badge) badge.textContent = "✅ Extensão 1-Clique Ativa";
    }
    if (m.type === "lattesdata-ext-result" && m.evento === "pendencia") {
      atualizarCartaoPendencia(m);
      return;
    }
    if (m.type === "lattesdata-ext-result" && m.evento === "leitura") return; // progresso da leitura ao vivo: tratado na página Meu currículo
    if (m.type === "lattesdata-ext-result") {
      if (btn) btn.disabled = false;
      if (btnOpen) btnOpen.disabled = false;
      showToast(m.message || (m.ok ? "Enviado ao Lattes." : "A extensão não conseguiu preencher."));
      mostrarResultadoLattes(m);
      processarResultadoEnvio(m);
    }
  });
  if (btn) {
    btn.onclick = () => dispararEnvioExtensao();
  }
  window.postMessage({ type: "lattesdata-ext-ping" }, location.origin);
})();

// ---------- Formulário genérico (itens descritos por especificação: itens/especificacao/<id>.json) ----------
const GEN = { spec: null, variante: null, valores: {}, item: "" };

function genOcultar() {
  const f = $("formGenerico");
  if (f) f.classList.add("hidden");
}

async function mostrarGenerico(g) {
  let spec = null;
  try { spec = await (await fetch(`/api/itens/${encodeURIComponent(g.item)}/spec`)).json(); } catch (e) {}
  if (!spec || !spec.variantes) { showToast("Não consegui carregar o formulário deste item."); return; }
  const variante = spec.variantes.find((v) => v.variante === g.variante) || spec.variantes[0];
  GEN.spec = spec; GEN.variante = variante; GEN.valores = { ...g.valores }; GEN.item = g.item;
  revelarPassos("form");
  $("lattesForm").classList.add("hidden");
  $("formGenerico").classList.remove("hidden");
  $("genTitulo").textContent = spec.item;
  $("genComo").textContent = "No Lattes: " + (spec.como_abrir || "");
  const av = $("genAvisos");
  av.innerHTML = "";
  if (spec.variantes.length > 1) {
    const wv = el("div", "field");
    const lv = el("label", "", "Tipo de formulário do Lattes");
    lv.htmlFor = "genVariante";
    wv.appendChild(lv);
    const sv = document.createElement("select");
    sv.id = "genVariante";
    spec.variantes.forEach((v) => { const op = document.createElement("option"); op.value = v.variante; op.textContent = v.rotulo || v.variante; sv.appendChild(op); });
    sv.value = variante.variante;
    sv.addEventListener("change", () => genTrocarVariante(sv.value));
    wv.appendChild(sv);
    av.appendChild(wv);
    av.appendChild(el("p", "hint", g.motivo_variante
      ? "Tipo escolhido pelo documento: " + g.motivo_variante + ". Confira."
      : "Não consegui identificar o tipo pelo documento: escolha o tipo de formulário acima."));
  }
  (g.notas || []).forEach((n) => av.appendChild(el("p", "hint", "• " + n)));
  if (["anais", "artigo"].includes(g.item)) {
    // Mesma busca de dados faltantes do formulário antigo (Crossref e OpenAlex), agora sobre o formulário do spec.
    const bt = el("button", "btn btn-secondary btn-sm", "🔎 Buscar dados faltantes (Crossref, OpenAlex)");
    bt.type = "button";
    bt.id = "btnGenEnriquecer";
    const st = el("p", "hint", "");
    bt.onclick = async () => {
      st.textContent = "Consultando Crossref e OpenAlex...";
      const valores = {};
      GEN.variante.campos.forEach((c) => { const e = $("gen_" + c.name); if (e) valores[c.name] = e.value.trim(); });
      try {
        const r = await (await fetch("/api/itens/enriquecer", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ item: g.item, valores }) })).json();
        const chaves = Object.keys(r.valores || {});
        chaves.forEach((n) => { const e = $("gen_" + n); if (e) { e.value = r.valores[n]; e.dispatchEvent(new Event("input", { bubbles: true })); } });
        st.textContent = chaves.length ? `Campos completados (${chaves.length}) via ${(r.fontes || []).join(", ")}: confira.` : "Nenhum dado adicional encontrado nas bases externas.";
        genAtualizar();
      } catch (e) { st.textContent = "Não consegui consultar as bases externas."; }
    };
    av.append(bt, st);
  }
  genDesenhar();
}

function genTrocarVariante(nome) {
  const nova = GEN.spec.variantes.find((v) => v.variante === nome);
  if (!nova || nova === GEN.variante) return;
  GEN.variante.campos.forEach((c) => {
    const e = $("gen_" + c.name);
    if (e) GEN.valores[c.name] = e.type === "checkbox" ? (e.checked ? "S" : "") : e.value.trim();
  });
  const gr = genGrades();
  (GEN.variante.grades || []).forEach((x) => { GEN.valores["grade:" + x.chave] = gr[x.chave] || []; });
  GEN.variante = nova;
  genDesenhar();
}

function genDesenhar() {
  const variante = GEN.variante;
  const box = $("genCampos");
  box.innerHTML = "";
  const abas = {};
  variante.campos.forEach((c) => { if (!c.oculto || c.mostrar_quando) (abas[c.aba || "Dados"] = abas[c.aba || "Dados"] || []).push(c); });
  Object.keys(abas).forEach((aba) => {
    const det = document.createElement("details");
    det.open = abas[aba].some((c) => c.obrigatorio || GEN.valores[c.name]);
    det.appendChild(el("summary", "", aba));
    const grid = el("div", "field-grid");
    abas[aba].forEach((c) => grid.appendChild(genCampo(c)));
    det.appendChild(grid);
    box.appendChild(det);
  });
  const todasGrades = variante.grades || [];
  const tabulares = todasGrades.filter((g) => g.colunas);
  const grades = todasGrades.filter((g) => !g.colunas);
  if (grades.length) {
    const det = document.createElement("details");
    det.open = genExigeTitular() || grades.some((gr) => (GEN.valores["grade:" + gr.chave] || []).length);
    det.appendChild(el("summary", "", "Listas (autores, palavras-chave, áreas, setores)"));
    const grid = el("div", "field-grid");
    grades.forEach((gr) => {
      const wrap = el("div", "field");
      const lab = el("label", "", gr.rotulo);
      lab.htmlFor = "gengrade_" + gr.chave;
      wrap.appendChild(lab);
      const ta = document.createElement("textarea");
      ta.rows = 3; ta.id = "gengrade_" + gr.chave; ta.dataset.grade = gr.chave; ta.placeholder = gr.dica || "";
      const ini = GEN.valores["grade:" + gr.chave] || [];
      ta.value = ini.map((x) => (x && typeof x === "object" ? [x.nome, (gr.chave === "autores" && citacaoConhecida(x.nome)) || x.citacao, x.coordenador ? "coordenador" : ""].filter(Boolean).join("; ") : x)).join("\n");
      wrap.appendChild(ta);
      if (gr.chave === "areas" || gr.chave === "setores") genSeletorGrade(gr, ta, wrap);
      if (genExigeTitular() && /^titulares_/.test(gr.chave)) {
        ta.addEventListener("input", genAtualizar);
        if (gr.chave === "titulares_pessoa") wrap.insertBefore(el("p", "hint", "Quem é o depositante/titular desta patente? Informe a pessoa e/ou a instituição (obrigatório no Lattes). O que veio do documento está só como sugestão: confira."), lab);
      }
      grid.appendChild(wrap);
    });
    det.appendChild(grid);
    box.appendChild(det);
  }
  tabulares.forEach((gr) => {
    const det = document.createElement("details");
    det.open = true;
    det.appendChild(el("summary", "", gr.rotulo));
    det.appendChild(genGradeTabular(gr));
    box.appendChild(det);
  });
  (variante.abas_informativas || []).forEach((ai) => {
    const det = document.createElement("details");
    det.open = true;
    det.appendChild(el("summary", "", ai.aba));
    const tb = el("table", "grid-tab");
    const tr = document.createElement("tr");
    (ai.colunas || []).forEach((c) => tr.appendChild(el("th", "", c)));
    const th = document.createElement("thead"); th.appendChild(tr); tb.appendChild(th);
    tb.appendChild(el("caption", "hint", "Nenhum registro (vínculo feito no Lattes)"));
    det.appendChild(tb);
    det.appendChild(el("p", "hint", ai.nota));
    box.appendChild(det);
  });
  genAtualizar();
}

// Áreas e Setores: igual ao Lattes, com "Listar todos" para escolher na própria plataforma (o preenchimento no Lattes usa o nome exato).
const GEN_CATALOGOS = {};
const semAcentoGrade = (t) => String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const linhasDaGrade = (ta) => ta.value.split("\n").map((x) => x.trim()).filter(Boolean);

function genSeletorGrade(gr, ta, wrap) {
  const barra = el("div", "");
  barra.style.cssText = "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:4px";
  const btn = el("button", "btn btn-secondary btn-sm", "Listar todos");
  btn.type = "button";
  const estado = el("span", "hint", "");
  const atualizar = () => {
    const n = linhasDaGrade(ta).length;
    estado.textContent = n ? n + " escolhida(s)" : "Nenhuma escolhida. Use Listar todos para escolher, se quiser incluir.";
  };
  ta.addEventListener("input", atualizar);
  btn.onclick = () => genAbrirListaTodos(gr, ta, atualizar);
  barra.append(btn, estado);
  wrap.appendChild(barra);
  atualizar();
}

async function genAbrirListaTodos(gr, ta, aoMudar) {
  const tipo = gr.chave === "areas" ? "areas" : "setores";
  if (!GEN_CATALOGOS[tipo]) {
    try { GEN_CATALOGOS[tipo] = (await (await fetch("/api/catalogos/" + tipo)).json()).itens || []; } catch (e) { GEN_CATALOGOS[tipo] = []; }
  }
  const itens = GEN_CATALOGOS[tipo];
  if (!itens.length) { showToast("Não consegui carregar a lista. Digite os nomes, um por linha."); return; }
  const fundo = el("div", "audit-modal-backdrop");
  fundo.setAttribute("role", "dialog");
  fundo.setAttribute("aria-modal", "true");
  const cartao = el("div", "audit-modal-card");
  const cab = el("div", "audit-modal-header");
  const titulo = el("h2", "audit-modal-title", (tipo === "areas" ? "Áreas do conhecimento" : "Setores de atividade") + " — Listar todos");
  const fechar = el("button", "btn-close", "✕");
  fechar.type = "button";
  fechar.setAttribute("aria-label", "Fechar");
  cab.append(titulo, fechar);
  const corpo = el("div", "audit-modal-body");
  const busca = document.createElement("input");
  busca.type = "text";
  busca.placeholder = "Filtrar por nome (ex.: farmacologia)";
  busca.style.cssText = "width:100%;margin-bottom:8px";
  const lista = el("div", "");
  lista.style.cssText = "max-height:50vh;overflow:auto;border:1px solid #e2e8f0;border-radius:8px";
  const rodape = el("div", "hint", "");
  const concluir = el("button", "btn btn-primary btn-sm", "Concluir");
  concluir.type = "button";
  const noPalavra = (nome) => linhasDaGrade(ta).some((l) => semAcentoGrade(l) === semAcentoGrade(nome));
  const desenhar = () => {
    const q = semAcentoGrade(busca.value).trim();
    const vistos = itens.filter((i) => !q || semAcentoGrade(i.caminho).includes(q)).slice(0, 400);
    lista.replaceChildren(...vistos.map((i) => {
      const linha = el("label", "");
      linha.style.cssText = "display:flex;gap:8px;align-items:flex-start;padding:5px 10px;cursor:pointer;padding-left:" + (10 + (q ? 0 : i.nivel * 16)) + "px";
      const cx = document.createElement("input");
      cx.type = "checkbox";
      cx.checked = noPalavra(i.nome);
      cx.onchange = () => {
        const atuais = linhasDaGrade(ta).filter((l) => semAcentoGrade(l) !== semAcentoGrade(i.nome));
        if (cx.checked) atuais.push(i.nome);
        ta.value = atuais.join("\n");
        ta.dispatchEvent(new Event("input", { bubbles: true }));
        aoMudar();
        rodape.textContent = linhasDaGrade(ta).length + " escolhida(s)";
        desenhar();
      };
      const txt = el("span", "", "");
      txt.append(el("b", "", i.nome));
      if (q && i.caminho !== i.nome) txt.append(el("span", "hint", "  " + i.caminho));
      linha.append(cx, txt);
      return linha;
    }));
    if (itens.filter((i) => !q || semAcentoGrade(i.caminho).includes(q)).length > 400) lista.append(el("div", "hint", "Mostrando os 400 primeiros: refine o filtro."));
    rodape.textContent = linhasDaGrade(ta).length + " escolhida(s)";
  };
  const sair = () => { document.removeEventListener("keydown", tecla); fundo.remove(); };
  const tecla = (e) => { if (e.key === "Escape") sair(); };
  fechar.onclick = sair;
  concluir.onclick = sair;
  fundo.addEventListener("click", (e) => { if (e.target === fundo) sair(); });
  document.addEventListener("keydown", tecla);
  busca.addEventListener("input", desenhar);
  corpo.append(busca, lista, el("div", "", ""), rodape, concluir);
  cartao.append(cab, corpo);
  fundo.appendChild(cartao);
  document.body.appendChild(fundo);
  desenhar();
  busca.focus();
}

function genGrades() {
  const out = {};
  ((GEN.variante && GEN.variante.grades) || []).forEach((gr) => {
    const e = $("gengrade_" + gr.chave);
    if (!e) return;
    const linhas = e.value.split("\n").map((l) => l.trim()).filter(Boolean);
    if (gr.chave === "situacoes") {
      const sit = linhas.map((l) => { const [nome, ...r] = l.split(";"); return { nome: nome.trim(), data: r.join(";").trim() }; });
      if (sit.length) out[gr.chave] = sit;
      return;
    }
    if (gr.chave === "autores") {
      let autores = linhas.map((l) => {
        const [nome, ...r] = l.split(";");
        const partes = r.map((x) => x.trim());
        const coordenador = partes.some((x) => /^coordenador(a)?$/i.test(x));
        const a = { nome: nome.trim(), citacao: partes.filter((x) => !/^coordenador(a)?$/i.test(x)).join(";").trim() };
        if (coordenador) a.coordenador = true;
        return a;
      });
      // O Lattes recusa salvar se o titular não está entre os autores: garante o titular (com o nome em citações).
      const dono = $("ownerName") ? $("ownerName").value.trim() : "";
      const cit = $("citacaoNome") ? $("citacaoNome").value.trim() : "";
      const t = nameTokens(dono);
      const ehTitular = (a) => { const b = nameTokens(a.nome); return t.length > 0 && b.length > 0 && t[0] === b[0] && t[t.length - 1] === b[b.length - 1]; };
      if (dono && !autores.some(ehTitular)) autores = [{ nome: dono, citacao: cit }, ...autores];
      else if (cit) autores = autores.map((a) => (ehTitular(a) ? { ...a, citacao: cit } : a));
      if (autores.length) out[gr.chave] = autores;
      return;
    }
    if (!linhas.length) return;
    out[gr.chave] = linhas;
  });
  return out;
}

// Lista com colunas, como as do Lattes (ex.: Instituição de financiamento). Guarda as linhas num textarea oculto
// (gengrade_<chave>), uma por linha e colunas separadas por ";", que o restante do fluxo já sabe ler.
function genGradeTabular(gr) {
  const wrap = el("div", "field");
  const ta = document.createElement("textarea");
  ta.id = "gengrade_" + gr.chave; ta.dataset.grade = gr.chave; ta.hidden = true;
  const ini = GEN.valores["grade:" + gr.chave] || [];
  ta.value = ini.map((x) => (typeof x === "string" ? x : "")).filter(Boolean).join("\n");
  const tb = el("table", "grid-tab");
  const cab = document.createElement("tr");
  gr.colunas.forEach((c) => cab.appendChild(el("th", "", c.rotulo)));
  cab.appendChild(el("th", "", ""));
  const th = document.createElement("thead"); th.appendChild(cab); tb.appendChild(th);
  const corpo = document.createElement("tbody"); tb.appendChild(corpo);
  const sync = () => {
    // Só entra a linha com a primeira coluna (instituição) preenchida; a moeda-padrão sozinha não conta.
    ta.value = [...corpo.rows].map((tr) => [...tr.querySelectorAll("input,select")].map((i) => i.value.trim().replace(/;/g, ","))).filter((c) => c[0]).map((c) => c.join("; ")).join("\n");
    genAtualizar();
  };
  const novaLinha = (vals) => {
    const tr = document.createElement("tr");
    gr.colunas.forEach((c, i) => {
      const td = document.createElement("td");
      let inp;
      if (c.opcoes) {
        inp = document.createElement("select");
        ["", ...c.opcoes].forEach((o) => { const op = document.createElement("option"); op.value = o; op.textContent = o || "—"; inp.appendChild(op); });
        inp.value = (vals && vals[i]) || c.padrao || "";
      } else {
        inp = document.createElement("input");
        inp.type = "text"; inp.value = (vals && vals[i]) || "";
        if (c.maxlength) inp.maxLength = c.maxlength;
        if (c.dica) inp.placeholder = c.dica;
        if (c.numerico) { inp.inputMode = "numeric"; inp.addEventListener("input", () => { inp.value = inp.value.replace(/\D/g, ""); }); }
        if (c.valor) inp.addEventListener("input", () => { inp.value = inp.value.replace(/[^0-9.,]/g, ""); });
      }
      inp.setAttribute("aria-label", c.rotulo);
      inp.addEventListener("input", sync); inp.addEventListener("change", sync);
      td.appendChild(inp); tr.appendChild(td);
    });
    const tdx = document.createElement("td");
    const bx = el("button", "btn btn-secondary btn-sm", "Excluir"); bx.type = "button";
    bx.onclick = () => { tr.remove(); sync(); };
    tdx.appendChild(bx); tr.appendChild(tdx);
    corpo.appendChild(tr);
  };
  ta.value.split("\n").filter(Boolean).forEach((l) => novaLinha(l.split(";").map((x) => x.trim())));
  wrap.append(ta, tb);
  const add = el("button", "btn btn-secondary btn-sm", "Incluir novo item"); add.type = "button";
  add.onclick = () => novaLinha(null);
  wrap.appendChild(add);
  if (gr.dica) wrap.appendChild(el("p", "hint", gr.dica));
  return wrap;
}

function genCampo(c) {
  const wrap = el("div", "field");
  const lab = el("label", "", c.rotulo + (c.obrigatorio ? " *" : ""));
  lab.htmlFor = "gen_" + c.name;
  wrap.appendChild(lab);
  let inp;
  const ops = c.opcoes ? Object.keys(c.opcoes) : null;
  if (c.mostrar_quando) { wrap.dataset.mostrarQuando = c.mostrar_quando.name; wrap.dataset.mostrarValor = c.mostrar_quando.valor; }
  if (c.tipo === "radio" && ops) {
    // Igual ao Lattes: grupo de radios (Sim/Não). O valor fica num campo oculto (id gen_<name>) para o restante do fluxo ler como antes.
    inp = document.createElement("input");
    inp.type = "hidden";
    inp.id = "gen_" + c.name;
    inp.dataset.name = c.name;
    inp.value = GEN.valores[c.name] || c.padrao || "";
    const grupo = el("div", "radio-group");
    grupo.setAttribute("role", "radiogroup");
    ops.forEach((o) => {
      const rl = el("label", "radio-opt");
      const r = document.createElement("input");
      r.type = "radio"; r.name = "genr_" + c.name; r.value = o; r.checked = inp.value === o;
      r.addEventListener("change", () => { inp.value = o; genAtualizar(); });
      rl.append(r, " " + o);
      grupo.appendChild(rl);
    });
    lab.removeAttribute("for");
    if (c.confira && !GEN.valores[c.name] && c.padrao) { lab.textContent += " (padrão — confira)"; grupo.title = "Valor-padrão sugerido pelo LattesFácil: confira antes de enviar."; }
    wrap.append(inp, grupo);
    if (c.dica) wrap.appendChild(el("div", "hint", c.dica));
    return wrap;
  }
  if (c.tipo === "checkbox" && ops && ops.length > 1) {
    // Grupo de caixas de marcação (várias opções), como no Lattes. O valor fica num campo oculto: opções marcadas separadas por "|".
    inp = document.createElement("input");
    inp.type = "hidden";
    inp.id = "gen_" + c.name;
    inp.dataset.name = c.name;
    const marcados = String(GEN.valores[c.name] || c.padrao || "").split("|").map((x) => x.trim()).filter(Boolean);
    inp.value = marcados.join("|");
    const grupo = el("div", "check-group");
    ops.forEach((o) => {
      const rl = el("label", "check-opt");
      const cb = document.createElement("input");
      cb.type = "checkbox"; cb.value = o; cb.checked = marcados.includes(o);
      cb.addEventListener("change", () => {
        inp.value = [...grupo.querySelectorAll("input:checked")].map((x) => x.value).join("|");
        genAtualizar();
      });
      rl.append(cb, " " + o);
      grupo.appendChild(rl);
    });
    lab.removeAttribute("for");
    wrap.append(inp, grupo);
    if (c.dica) wrap.appendChild(el("div", "hint", c.dica));
    return wrap;
  }
  if (c.tipo === "textarea") {
    inp = document.createElement("textarea");
    inp.rows = 3;
    if (c.maxlength) inp.maxLength = c.maxlength;
  } else if (ops && (c.tipo === "select" || c.tipo === "radio")) {
    inp = document.createElement("select");
    ["", ...ops].forEach((o) => { const op = document.createElement("option"); op.value = o; op.textContent = o || "—"; inp.appendChild(op); });
  } else if (c.tipo === "checkbox") {
    inp = document.createElement("input");
    inp.type = "checkbox";
  } else {
    inp = document.createElement("input");
    inp.type = "text";
    if (c.maxlength) inp.maxLength = c.maxlength;
  }
  inp.id = "gen_" + c.name;
  inp.dataset.name = c.name;
  const v = GEN.valores[c.name] || c.padrao;
  if (inp.type === "checkbox") inp.checked = !!v;
  else inp.value = v || "";
  if (c.confira && !GEN.valores[c.name] && c.padrao) {
    lab.textContent += " (padrão — confira)";
    inp.title = "Valor-padrão sugerido pelo LattesFácil: confira antes de enviar.";
  }
  inp.addEventListener("input", genAtualizar);
  inp.addEventListener("change", genAtualizar);
  wrap.appendChild(inp);
  if (c.dica) wrap.appendChild(el("div", "hint", c.dica));
  if (c.name === "f_inst" && inp.type === "text") genAssistirInstituicao(inp, wrap);
  return wrap;
}

// Campo condicional do Lattes (ex.: CNPJ só aparece com cooperação "Sim"): visível só quando o gatilho tem o valor esperado.
function genVisivel(c) {
  if (!c.mostrar_quando) return true;
  const g = $("gen_" + c.mostrar_quando.name);
  return !!g && (g.value === c.mostrar_quando.valor || g.value.split("|").includes(c.mostrar_quando.valor));
}
function genAplicarCondicionais() {
  if (!GEN.variante) return;
  GEN.variante.campos.forEach((c) => {
    const e = $("gen_" + c.name);
    if (c.exige_antes && e) {
      // O Lattes recusa o valor enquanto outro campo não for escolhido (ex.: tipo de orientação só com mestrado/doutorado): campo bloqueado até lá.
      const g = $("gen_" + c.exige_antes.name);
      const libera = !!g && c.exige_antes.valores.includes(g.value);
      e.disabled = !libera;
      if (!libera && e.value) { e.value = ""; document.querySelectorAll('input[name="genr_' + c.name + '"]').forEach((r) => { r.checked = false; }); }  // o Lattes recusa o valor sem o pré-requisito
      document.querySelectorAll('input[name="genr_' + c.name + '"]').forEach((r) => { r.disabled = !libera; });
      if (!libera) e.title = "Disponível quando " + c.exige_antes.name + " for: " + c.exige_antes.valores.join(" ou ");
    }
    if (!c.mostrar_quando) return;
    if (e && e.closest(".field")) e.closest(".field").style.display = genVisivel(c) ? "" : "none";
  });
}

// Instituição é cadastro controlado do Lattes (campo desabilitado; só a lupa grava o código). Na revisão, consulta o banco local
// (confirmações anteriores, semente e o que a lupa já devolveu) e deixa o usuário escolher/confirmar o nome exato antes de enviar.
// Sem resultado no banco, avisa que o preenchimento dependerá da lupa e, portanto, da conexão com o Lattes.
function genAssistirInstituicao(inp, wrap) {
  const dica = el("div", "hint");
  dica.setAttribute("aria-live", "polite");
  wrap.appendChild(dica);
  let tmr = null;
  let ultimo = "";
  const escolher = async (cand, texto) => {
    inp.value = cand.nome;
    inp.dispatchEvent(new Event("input", { bubbles: true }));
    if (texto) {
      try {
        await fetch("/api/instituicoes/confirmar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ texto, id: cand.id, usuario: $("ownerName") ? $("ownerName").value : "" }) });
      } catch (e) { /* a escolha vale mesmo sem gravar a confirmação */ }
    }
    ultimo = "";
    consultar();
  };
  const botao = (rotulo, fn) => { const b = el("button", "btn btn-secondary btn-sm", rotulo); b.type = "button"; b.style.marginRight = "6px"; b.style.marginTop = "4px"; b.onclick = fn; return b; };
  const consultar = async () => {
    const q = inp.value.trim();
    if (q === ultimo) return;
    ultimo = q;
    dica.replaceChildren();
    if (q.length < 3) return;
    let r;
    try { r = await (await fetch("/api/instituicoes/buscar?q=" + encodeURIComponent(q))).json(); } catch (e) { return; }
    if (inp.value.trim() !== q || !r || !Array.isArray(r.candidatas)) return;
    const cands = r.candidatas;
    if (r.confirmada && cands[0]) {
      dica.append("✔ Confirmada antes: " + cands[0].nome + (cands[0].codigo ? " (código " + cands[0].codigo + ")" : ""));
      if (cands[0].nome !== q) dica.append(" ", botao("Usar este nome", () => escolher(cands[0], "")));
      return;
    }
    if (!cands.length) {
      dica.append("Não está no banco local de instituições. " + (lattesState.online
        ? "No envio, o LattesData procura na lupa do Lattes e escolhe se o resultado for claro."
        : "Conecte-se ao Lattes: o preenchimento precisa da lupa para registrar esta instituição."));
      return;
    }
    dica.append(r.claro ? "No banco: " : "Possíveis no banco: ");
    (r.claro ? cands.slice(0, 1) : cands.slice(0, 4)).forEach((cd) => dica.append(botao(cd.nome + (cd.sigla ? " (" + cd.sigla + ")" : "") + (cd.codigo ? "" : " · sem código"), () => escolher(cd, q))));
    if (!lattesState.online && cands.some((cd) => !cd.codigo)) dica.append(el("div", "", "Alguma opção ainda não tem código do Lattes: conecte-se ao Lattes para a lupa confirmá-la no envio."));
  };
  inp.addEventListener("input", () => { clearTimeout(tmr); tmr = setTimeout(consultar, 500); });
  setTimeout(consultar, 0);
}

function genColetar() {
  const campos = [];
  const faltam = [];
  GEN.variante.campos.forEach((c) => {
    const e = $("gen_" + c.name);
    if (!e || !genVisivel(c)) return;
    const valor = e.type === "checkbox" ? (e.checked ? "S" : "") : e.value.trim();
    const obrigatorio = c.obrigatorio || (c.obrigatorio_quando && ($("gen_" + c.obrigatorio_quando.name) || {}).value === c.obrigatorio_quando.valor);
    if (obrigatorio && !valor && !c.automatico) faltam.push(c.rotulo);
    if (c.tipo === "checkbox" && c.opcoes && Object.keys(c.opcoes).length > 1) {
      const partes = valor.split("|").filter(Boolean);
      campos.push({ name: c.name, rotulo: c.rotulo, tipo: c.tipo, valor: partes.join("; "), codigo: "", codigos: partes.map((p) => c.opcoes[p]).filter(Boolean), auto: false, auto_de: "" });
      return;
    }
    campos.push({ name: c.name, rotulo: c.rotulo, tipo: c.tipo, valor, codigo: c.opcoes && c.opcoes[valor] ? c.opcoes[valor] : "", auto: !!c.automatico, auto_de: c.auto_de || "" });
  });
  if (genExigeTitular() && !genTitularInformado()) faltam.push(GEN_ROTULO_TITULAR);
  // Projetos: o Lattes exige a equipe com um (e só um) coordenador.
  if (GEN.spec && GEN.spec.id === "projeto") {
    const ta = $("gengrade_autores");
    const nCoord = ta ? ta.value.split("\n").filter((l) => /;\s*coordenador(a)?\s*$/i.test(l.trim())).length : 0;
    if (nCoord === 0) faltam.push("Coordenador da equipe (marque um pesquisador com \"coordenador\")");
    if (nCoord > 1) faltam.push("Apenas um coordenador na equipe");
  }
  return { campos, faltam };
}

// Patente: o Lattes exige o depositante/titular e o documento nem sempre o traz certo; a plataforma sempre pergunta e não envia sem resposta.
const GEN_ROTULO_TITULAR = "Depositante/Titular (pessoa ou instituição)";
const genExigeTitular = () => !!(GEN.spec && GEN.spec.id === "patente");
const genTitularInformado = () => ["titulares_pessoa", "titulares_inst"].some((k) => { const e = $("gengrade_" + k); return e && e.value.trim(); });

function genAtualizar() {
  if (!GEN.variante) return;
  genAplicarCondicionais();
  const { faltam } = genColetar();
  GEN.variante.campos.forEach((c) => {
    const e = $("gen_" + c.name);
    if (e) e.classList.toggle("missing-highlight", c.obrigatorio && faltam.includes(c.rotulo));
  });
  if (genExigeTitular()) ["titulares_pessoa", "titulares_inst"].forEach((k) => { const e = $("gengrade_" + k); if (e) e.classList.toggle("missing-highlight", faltam.includes(GEN_ROTULO_TITULAR)); });
  $("btnGenEnviar").title = faltam.length ? "Faltam obrigatórios: " + faltam.join(", ") : "";
  let b = $("genFaltam");
  if (!b) { b = el("p", "hint"); b.id = "genFaltam"; $("genAvisos").appendChild(b); }
  b.textContent = faltam.length ? "Obrigatórios do Lattes ainda vazios: " + faltam.join(", ") + "." : "Todos os campos obrigatórios estão preenchidos.";
}

// Campo que melhor identifica o item no Lattes (usado para reconhecer o registro na lista do currículo).
const GEN_CAMPOS_TITULO = ["f_titulo", "titulo", "f_nme_evento", "f_curso", "f_nme_agencia", "f_nme_projeto", "f_cod_reg", "f_inst"];

function genTitulo(campos) {
  for (const n of GEN_CAMPOS_TITULO) {
    const c = campos.find((x) => x.name === n && x.valor);
    if (c) return c.valor;
  }
  const c = campos.find((x) => x.valor && x.tipo === "text");
  return c ? c.valor : "";
}

// Formulários de registro (patente, software, marca...) abrem com a instituição e o nº do registro no endereço.
// O mapeamento traz um nº de exemplo: troca pelos valores reais do formulário.
function genUrlDaVariante(campos) {
  let url = GEN.variante.url || "";
  const val = (n) => ((campos.find((c) => c.name === n) || {}).valor || "").trim();
  if (GEN.spec.id === "artigo") {
    // O Lattes abre o artigo por dois caminhos (conferido na lista do Lattes em 20/11/2026): pelo DOI (dados e autores vêm do DOI) ou
    // pelo periódico informado à mão (ISSN, título, volume, edição e página inicial vão no endereço).
    const doi = val("f_cod_doi");
    if (doi) return "PKG_ARTIGO.form?f_sta_divulgacao_cientifica=&F_COD_DOI=" + encodeURIComponent(doi) + "&F_CTR=D&F_COD=<codigo_do_cv>";
    return "PKG_ARTIGO.form?f_sta_divulgacao_cientifica=&F_ORIGEM_WS=F&F_TITULO_PERIODICO=" + escape(val("f_titulo_periodico")) +
      "&F_ISSN=" + val("f_issn").replace(/-/g, "") + "&F_VOLUME=" + escape(val("f_volume")) + "&F_SERIE=" + escape(val("f_serie")) +
      "&F_PAG_INI=" + escape(val("f_pag_ini")) + "&F_CTR=FIV&F_COD=<codigo_do_cv>";
  }
  const reg = val("f_cod_reg").replace(/\s+/g, "");
  const inst = val("f_inst");
  if (/[?&]f_cod_reg=/i.test(url)) url = url.replace(/([?&]f_cod_reg=)[^&]*/i, "$1" + encodeURIComponent(reg));
  if (/[?&]f_inst=/i.test(url) && inst) {
    const completo = /^INPI$/i.test(inst) ? "INPI - Instituto Nacional da Propriedade Industrial" : inst;
    url = url.replace(/([?&]f_inst=)[^&]*/i, "$1" + encodeURIComponent(completo));
  }
  return url;
}

function genPayload() {
  const { campos, faltam } = genColetar();
  const usuario = $("ownerName") ? $("ownerName").value : "";
  const ano = (campos.find((x) => /^f_?ano/i.test(x.name) && x.valor) || {}).valor || "";
  return {
    tipo_producao: "generico", __usuario: usuario, __origem: location.origin,
    __autoSalvar: !!($("autoSaveLattes") && $("autoSaveLattes").checked),
    titulo: genTitulo(campos), ano,
    __generico: { id: GEN.spec.id, item: GEN.spec.item, como_abrir: GEN.spec.como_abrir, lista: GEN.spec.lista || "", url: genUrlDaVariante(campos), campos, faltam, grades: genGrades() },
    ...(GEN.alterarSeq ? { __alterar: { seq: GEN.alterarSeq } } : {}),
  };
}

// ---- Incluir ou ALTERAR: lista os itens do Lattes do tipo e deixa escolher qual alterar
(function genModoAlterar() {
  const btn = $("btnGenEnviar");
  if (!btn || !btn.parentNode) return;
  const caixa = el("div", "hint");
  caixa.id = "genModoBox";
  caixa.style.cssText = "margin:8px 0;display:flex;flex-wrap:wrap;gap:8px;align-items:center";
  const modo = document.createElement("select");
  modo.id = "genModo";
  modo.innerHTML = '<option value="novo">Incluir como novo item</option><option value="alterar">Alterar um item já cadastrado…</option>';
  const itens = document.createElement("select");
  itens.id = "genItemAlterar";
  itens.style.display = "none";
  const aviso = el("span", "hint");
  aviso.id = "genModoAviso";
  caixa.append(modo, itens, aviso);
  btn.parentNode.insertBefore(caixa, btn);
  const redefinir = () => { GEN.alterarSeq = ""; btn.textContent = btn.dataset.rotuloOriginal || btn.textContent; };
  modo.onchange = () => {
    GEN.alterarSeq = "";
    itens.style.display = modo.value === "alterar" ? "" : "none";
    aviso.textContent = "";
    if (modo.value === "alterar") {
      aviso.textContent = "Lendo a lista no Lattes…";
      window.postMessage({ type: "lattesdata-ext-list", tipo: GEN.spec && GEN.spec.id }, location.origin);
    } else redefinir();
  };
  itens.onchange = () => {
    GEN.alterarSeq = itens.value || "";
    aviso.textContent = GEN.alterarSeq ? "Só os campos preenchidos acima serão trocados no item nº " + GEN.alterarSeq + "; os vazios ficam como estão." : "";
  };
  window.addEventListener("message", (e) => {
    const m = e.data;
    if (e.source !== window || !m || m.type !== "lattesdata-ext-lista" || !GEN.spec || m.tipoItem !== GEN.spec.id) return;
    itens.innerHTML = "";
    if (!m.ok) { aviso.textContent = m.erro || "Não consegui ler a lista do Lattes."; return; }
    if (!m.itens.length) { aviso.textContent = "Não há itens cadastrados deste tipo no Lattes."; return; }
    const o0 = document.createElement("option"); o0.value = ""; o0.textContent = "Escolha o item…"; itens.appendChild(o0);
    m.itens.forEach((i) => { const o = document.createElement("option"); o.value = i.seq; o.textContent = (i.titulo || "(sem título)").slice(0, 90) + (i.ano ? " — " + i.ano : "") + " · nº " + i.seq; itens.appendChild(o); });
    aviso.textContent = m.itens.length + " item(ns) no Lattes.";
  });
})();

$("btnGenEnviar").onclick = () => {
  const btn = $("btnGenEnviar");
  btn.disabled = true;
  const dados = genPayload();
  // registra o envio (tipo = id do item) para a verificação e a remoção automáticas encontrarem o registro depois
  const envio = dados.__alterar ? Promise.resolve("") : fetch("/api/lattes/envios", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ owner: $("ownerName") ? $("ownerName").value : "", titulo: dados.titulo, tipo: dados.__generico.id, ano: dados.ano }),
  }).then((r) => r.json()).then((j) => j.id || "").catch(() => "");
  envio.then((id) => {
    if (id) dados.__envioId = id;
    try { carregarEnvios(); } catch (e) {}
    window.postMessage({ type: "lattesdata-ext-fill", data: dados }, location.origin);
  });
  setTimeout(() => { btn.disabled = false; }, 4000);
};
$("btnGenCopiar").onclick = async () => {
  const payload = JSON.stringify(genPayload()).replace(/</g, "\\u003c");
  try {
    await navigator.clipboard.writeText(AUTOFILL_TEMPLATE.replace("__DATA__", () => payload));
    showToast("Script copiado. Cole no Console (F12) da aba do Lattes já logada.");
  } catch (e) {
    showToast("Não foi possível copiar automaticamente.");
  }
};

// Rotina de primeiro acesso: ler os "Autores citados no currículo" já cadastrados no Lattes do usuário e guardá-los no servidor.
// Depois eles completam o nome em citações dos inventores/coautores sem digitar de novo.
const AUTORES_CV = { owner: "", autores: [], coletado: false, total: 0, coletando: false };

function citacaoConhecida(nome) {
  const t = nameTokens(nome);
  if (t.length < 2) return "";
  const a = AUTORES_CV.autores.find((x) => { const u = nameTokens(x.nome); return x.citacao && u.length >= 2 && u[0] === t[0] && u[u.length - 1] === t[t.length - 1]; });
  return a ? a.citacao : "";
}

(function iniciarRotinaAutores() {
  const dono = () => ($("ownerName") ? $("ownerName").value.trim() : "");
  let cartao = null;
  const mostrar = (titulo, texto, botao) => {
    if (!cartao) {
      cartao = document.createElement("div");
      cartao.id = "cartaoAutores";
      cartao.style.cssText = "position:fixed;left:16px;bottom:16px;max-width:360px;z-index:60;background:var(--surface,#fff);color:var(--text,#1c2430);border:1px solid var(--border,#d6dde6);border-left:4px solid #2563eb;border-radius:10px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.18);font-size:14px";
      document.body.appendChild(cartao);
    }
    cartao.replaceChildren();
    const h = document.createElement("strong"); h.textContent = titulo; cartao.appendChild(h);
    const p = document.createElement("p"); p.style.cssText = "margin:6px 0 8px"; p.textContent = texto; cartao.appendChild(p);
    const linha = document.createElement("div"); linha.style.cssText = "display:flex;gap:8px;flex-wrap:wrap";
    if (botao) { const b = document.createElement("button"); b.type = "button"; b.className = "btn btn-primary btn-sm"; b.textContent = botao.rotulo; b.onclick = botao.acao; linha.appendChild(b); }
    const f = document.createElement("button"); f.type = "button"; f.className = "btn btn-secondary btn-sm"; f.textContent = "Fechar"; f.onclick = () => { cartao.remove(); cartao = null; };
    linha.appendChild(f);
    cartao.appendChild(linha);
  };
  const esconder = () => { if (cartao) { cartao.remove(); cartao = null; } };

  async function carregar() {
    const o = dono();
    if (!o) return null;
    try {
      const j = await (await fetch("/api/autores?owner=" + encodeURIComponent(o))).json();
      AUTORES_CV.owner = o; AUTORES_CV.autores = j.autores || []; AUTORES_CV.coletado = !!j.coletado; AUTORES_CV.total = j.total || 0;
      return j;
    } catch (e) { return null; }
  }

  function iniciarLeitura(manual) {
    if (!window.__lattesExtAtiva) { if (manual) showToast("Instale a extensão LattesData para ler os autores do Lattes."); return; }
    if (AUTORES_CV.coletando) return;
    AUTORES_CV.coletando = true;
    mostrar("Primeiro acesso: lendo seus autores", "Estou lendo, no seu Lattes, os autores citados no currículo. Se o Lattes abrir pedindo login, entre no seu currículo: a leitura continua sozinha.");
    window.postMessage({ type: "lattesdata-ext-autores" }, location.origin);
    try { sessionStorage.setItem("lfAutores:" + dono(), String(Date.now())); } catch (e) {}
  }

  window.addEventListener("message", async (e) => {
    const m = e.data;
    if (e.source !== window || e.origin !== location.origin || !m || m.type !== "lattesdata-ext-autores-resp") return;
    AUTORES_CV.coletando = false;
    if (m.login) { mostrar("Entre no seu currículo Lattes", m.erro || "Faça o login no Lattes e clique em Tentar de novo.", { rotulo: "Tentar de novo", acao: () => iniciarLeitura(true) }); return; }
    if (!m.ok) { mostrar("Não consegui ler seus autores", (m.erro || "Erro desconhecido.") + " Você pode tentar de novo.", { rotulo: "Tentar de novo", acao: () => iniciarLeitura(true) }); return; }
    try {
      const r = await (await fetch("/api/autores/salvar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ owner: dono(), linhas: m.linhas, cv: m.cv }) })).json();
      await carregar();
      if (r.total > 0) { mostrar("Autores guardados", r.total + " autores do seu currículo foram guardados e passam a completar os nomes em citações nos formulários."); setTimeout(esconder, 6000); }
      else mostrar("A lista veio sem autores reconhecidos", "O Lattes respondeu, mas não consegui identificar autores nela (" + m.linhas.length + " linhas lidas). Amostra: " + ((m.amostra || []).join(" // ") || m.texto || "vazia") + ". Me envie essa amostra para eu ajustar a leitura.", { rotulo: "Tentar de novo", acao: () => iniciarLeitura(true) });
    } catch (err) { mostrar("Não consegui guardar os autores", "Falha ao falar com o servidor. Tente de novo.", { rotulo: "Tentar de novo", acao: () => iniciarLeitura(true) }); }
  });

  async function verificar() {
    const j = await carregar();
    if (!j) return;
    if (j.coletado) { esconder(); return; }
    // ainda não coletou: espera a extensão aparecer e inicia uma vez por sessão (o botão permite repetir)
    let tent = 0;
    const tenta = () => {
      if (window.__lattesExtAtiva) {
        let feito = ""; try { feito = sessionStorage.getItem("lfAutores:" + dono()) || ""; } catch (e) {}
        if (!feito) iniciarLeitura(false);
        else mostrar("Autores do seu Lattes ainda não lidos", "No primeiro acesso o LattesData lê os autores já cadastrados no seu currículo.", { rotulo: "Ler agora", acao: () => iniciarLeitura(true) });
      } else if (++tent < 20) setTimeout(tenta, 500);
      else mostrar("Autores do seu Lattes ainda não lidos", "Instale a extensão LattesData para ler os autores já cadastrados no seu currículo.");
    };
    tenta();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { setTimeout(verificar, 1500); });
  else setTimeout(verificar, 1500);
  if ($("ownerName")) $("ownerName").addEventListener("change", () => { esconder(); AUTORES_CV.coletando = false; verificar(); });
})();
