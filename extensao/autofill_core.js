// GERADO por extensao/build.py a partir de static/app.js. Não edite.
window.__lfAutofill = async function (d) {
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
};
