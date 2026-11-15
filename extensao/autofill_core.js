// GERADO por extensao/build.py a partir de static/app.js. Não edite.
window.__lfAutofill = async function (d) {
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var norm = function (t) { return String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim().toLowerCase(); };
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
      alert('LattesData: o currículo aberto no Lattes é de "' + (loggedName || 'titular não identificado') + '", mas o usuário selecionado no LattesData é "' + wanted + '".\n\nNada foi preenchido. Troque o usuário no LattesData ou entre no Lattes com a conta correta.');
      return;
    }
  }
  try { var tp = window.top.opener || window.opener; if (tp && d.__origem) tp.postMessage({ type: 'lattesfacil-status', online: !!loggedName, name: loggedName }, d.__origem); } catch (e) {}
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
    alert('LattesData: formulário não encontrado. Faça login no Lattes para abrir o painel principal e tente novamente.');
    return;
  }
  var report = [];
  var fire = function (el) { ['input', 'change'].forEach(function (t) { el.dispatchEvent(new Event(t, { bubbles: true })); }); };
  var visible = function (el) { return el.offsetParent !== null; };
  // Escolha automática em cadastros controlados: nome idêntico; senão, a opção mais parecida, só se for clara e única.
  var STOPW = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'a', 'o'];
  var toks = function (s) { return norm(s).replace(/[^a-z0-9 ]/g, ' ').split(' ').filter(function (t) { return t && STOPW.indexOf(t) < 0; }); };
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

  var want = d.tipo_producao || 'anais';
  var have = doc.querySelector('[name="f_titulo_periodico"]') ? 'artigo' : (doc.querySelector('[name="f_nme_orient"]') ? 'orientacao' : (doc.querySelector('[name="f_nme_evento"]') ? 'apresentacao' : 'anais'));
  var NOMES = { anais: 'um Trabalho em anais', apresentacao: 'uma Apresentação de trabalho', artigo: 'um Artigo em periódico', orientacao: 'uma Orientação' };
  var CAMINHOS = { anais: 'Produções > Trabalhos publicados em anais de eventos', apresentacao: 'Produções > Apresentação de trabalho e palestra', artigo: 'Produções > Artigos completos publicados em periódicos', orientacao: 'Orientações > Orientações e supervisões concluídas (ou em andamento)' };
  if (want !== have) {
    alert('LattesData: este registro é ' + NOMES[want] + ', mas o formulário aberto é de ' + NOMES[have] + '. Abra ' + CAMINHOS[want] + ' > Incluir novo item e execute de novo.');
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
    setRadio('F_RELEV', 'N');
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
      alert('LattesData: este registro é uma orientação ' + (andamento ? 'em andamento' : 'concluída') + ', mas o formulário aberto é de ' + (formAndamento ? 'em andamento' : 'concluídas') + '. Abra Orientações > Orientações e supervisões ' + (andamento ? 'em andamento' : 'concluídas') + ' > Incluir novo item.');
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
    setRadio('F_RELEV', 'N');
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
    setRadio('F_RELEV', 'N');
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
    try { btnSalvar.click(); return; } catch (e) {}
  }
  alert('LattesData: campos principais preenchidos. ' + (autoresPeloDoi ? 'Autores: do DOI; ' : (autores.length ? 'Autores: ' + okAut + '/' + autores.length + '; ' : '')) + 'palavras-chave: ' + okKw + '/' + kws.length + '; áreas: ' + okArea + '/' + areas.length + '.' +
    (report.length ? '\n\nAtenção:\n- ' + report.join('\n- ') : '') + '\n\nConfira tudo e clique no botão Salvar (destacado em verde) no Lattes.');
};
