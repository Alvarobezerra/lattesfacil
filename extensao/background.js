// Service worker: gerencia a conexão com o Lattes, fila pós-login e execução em 1 clique.
const LATTES_LOGIN_URL = "https://wwws.cnpq.br/cvlattesweb/pkg_login.prc_form";
const LATTES_PATTERNS = ["https://wwws.cnpq.br/*", "https://lattes.cnpq.br/*"];
const APP_PATTERNS = ["http://localhost/*", "http://127.0.0.1/*", "https://lattesfacil.onrender.com/*"];

// O CNPq mostra "erro de cookie" se pkg_login.prc_form for aberto sem estes cookies no domínio .cnpq.br.
async function prepararCookiesCnpq() {
  const base = { url: "https://wwws.cnpq.br/", domain: ".cnpq.br", path: "/", secure: true };
  try {
    await chrome.cookies.set({ ...base, name: "imp", value: "cnpqrestritos" });
    await chrome.cookies.set({ ...base, name: "idioma", value: "PT" });
  } catch (e) {
    console.warn("LattesData: não foi possível definir os cookies do CNPq", e);
  }
}

async function acharAbaLattes() {
  const abas = await chrome.tabs.query({ url: LATTES_PATTERNS });
  const cvAbas = abas.filter((t) => (t.url || "").includes("wwws.cnpq.br"));
  return cvAbas.find((t) => t.active) || cvAbas[0] || abas[0] || null;
}

async function verificarSeAbaLogada(tabId) {
  try {
    const res = await chrome.scripting.executeScript({
      target: { tabId },
      world: "MAIN",
      func: () => {
        try {
          const d = window.top.document;
          const el = d.getElementById("nmeLt") || d.querySelector(".dadosPrinc .nome");
          if (el && el.textContent.trim()) return { loggedIn: true, name: el.textContent.trim() };
          if (window.top.modalCV2 && typeof window.top.modalCV2.setarUrl === "function") {
            return { loggedIn: true, name: "" };
          }
          if (d.querySelector('[name="f_titulo"]')) return { loggedIn: true, name: "" };
        } catch (e) {}
        return { loggedIn: false, name: "" };
      }
    });
    return (res && res[0] && res[0].result) || { loggedIn: false, name: "" };
  } catch (e) {
    return { loggedIn: false, name: "" };
  }
}

// Roda DENTRO da página do Lattes (mundo MAIN). Executa o preenchimento, captura os alert() do script em vez de
// deixá-los piscar/bloquear, mostra um painel fixo com o resultado e devolve o resumo para o LattesData.
async function rodarComFeedback(d) {
  const top = window.top;
  const doc = top.document;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  try { top.sessionStorage.removeItem("lfSalvou"); } catch (e) {}

  function painel(estado, titulo, detalhes) {
    let p = doc.getElementById("lattesdata-painel");
    if (!p) {
      p = doc.createElement("div");
      p.id = "lattesdata-painel";
      p.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;max-width:400px;font:14px/1.45 system-ui,sans-serif;" +
        "color:#0f172a;background:#fff;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.3);border-left:6px solid #0369a1;padding:12px 14px";
      doc.body.appendChild(p);
    }
    p.style.borderLeftColor = { andando: "#0369a1", ok: "#059669", atencao: "#d97706", erro: "#dc2626" }[estado] || "#0369a1";
    p.textContent = "";
    const h = doc.createElement("strong");
    h.textContent = "LattesData — " + titulo;
    p.appendChild(h);
    if (detalhes && detalhes.length) {
      const ul = doc.createElement("ul");
      ul.style.cssText = "margin:6px 0 0;padding-left:18px";
      detalhes.forEach((t) => { const li = doc.createElement("li"); li.textContent = t; ul.appendChild(li); });
      p.appendChild(ul);
    }
    if (estado !== "andando") {
      const x = doc.createElement("button");
      x.textContent = "Fechar";
      x.style.cssText = "margin-top:8px;border:0;background:#e2e8f0;border-radius:6px;padding:4px 10px;cursor:pointer";
      x.onclick = () => p.remove();
      p.appendChild(x);
    }
  }

  function formAberto(w) {
    try { const el = w.document.querySelector('[name="f_titulo"]'); if (el && (!w.frameElement || w.frameElement.offsetParent !== null)) return true; } catch (e) {}
    for (let i = 0; i < w.frames.length; i++) { try { if (formAberto(w.frames[i])) return true; } catch (e) {} }
    return false;
  }

  // Avisos que o Lattes desenha na própria página (caixa "Atenção"), em qualquer quadro acessível.
  function avisosNaPagina(w, acc, prof) {
    if (prof > 4) return acc;
    try {
      const txt = (w.document.body && w.document.body.innerText) || "";
      const re = /(N[aã]o foi poss[ií]vel[^\r\n]*)|(O seu nome dever[aá][^\r\n]*)|(Informe [^\r\n]{3,80})/gi;
      let m;
      while ((m = re.exec(txt)) && acc.length < 6) {
        const linha = m[0].replace(/\s+/g, " ").trim().slice(0, 220);
        if (!acc.includes(linha)) acc.push(linha);
      }
    } catch (e) {}
    try { for (let i = 0; i < w.frames.length; i++) avisosNaPagina(w.frames[i], acc, prof + 1); } catch (e) {}
    return acc;
  }

  const msgs = [];
  const alertOriginal = top.alert;
  top.alert = (m) => { msgs.push(String(m)); };
  let erro = "";
  painel("andando", "aguardando o Lattes terminar de carregar…", ["Não feche esta aba até terminar."]);
  // Logo depois do login (1º envio) o painel do currículo já aparece, mas o Lattes ainda está montando a página: o
  // modalCV2 (que abre os formulários) e o código do currículo podem não existir ainda. Espera ficarem prontos.
  const prontoLattes = () => {
    try {
      const html = (doc.documentElement && doc.documentElement.innerHTML) || "";
      return doc.readyState === "complete" && !!top.modalCV2 && typeof top.modalCV2.setarUrl === "function" && /[?&]f_cod=[A-Za-z0-9]{6,20}/i.test(html);
    } catch (e) { return false; }
  };
  for (let i = 0; i < 60 && !prontoLattes(); i++) await sleep(500);
  const prontoMs = prontoLattes();
  if (!prontoMs) {
    top.alert = alertOriginal;
    const r = { estado: "erro", titulo: "o Lattes não terminou de carregar o currículo (30 s). Recarregue a página do Lattes e envie de novo.", detalhes: [] };
    painel(r.estado, r.titulo, r.detalhes);
    return r;
  }
  await sleep(800); // folga para os menus do Lattes terminarem de se montar
  painel("andando", "preenchendo o formulário no Lattes…", ["Não feche esta aba até terminar."]);
  try {
    await window.__lfAutofill(d);
  } catch (e) {
    erro = String((e && e.message) || e);
  }

  let res;
  const NL = String.fromCharCode(10);
  const linhas = () => msgs.join(NL).split(NL).map((t) => t.trim()).filter(Boolean);
  const texto = () => msgs.join(NL);
  if (erro) {
    res = { estado: "erro", titulo: "o preenchimento falhou", detalhes: [erro] };
  } else if (/curr[ií]culo aberto no Lattes [ée] de/i.test(texto())) {
    res = { estado: "erro", titulo: "currículo de outra pessoa — nada foi preenchido", detalhes: linhas() };
  } else if (/n[aã]o consegui abrir|formul[aá]rio n[aã]o encontrado/i.test(texto())) {
    res = { estado: "erro", titulo: "não consegui abrir o formulário", detalhes: linhas() };
  } else if (!msgs.length && d.__autoSalvar) {
    // O script clicou em Salvar e não avisa nada: espera o Lattes responder e confere.
    await sleep(4000);
    const aviso = /erro|obrigat|inv[aá]lid|n[aã]o foi poss|preench|ausente|j[aá] existe/i.test(texto());
    if (aviso) res = { estado: "atencao", titulo: "o Lattes avisou algo ao salvar — confira", detalhes: linhas() };
    else if (formAberto(window)) res = { estado: "atencao", titulo: "cliquei em Salvar, mas o formulário continua aberto — confira", detalhes: linhas() };
    else res = { estado: "ok", titulo: "salvo: o formulário fechou após Salvar. Confira o item no seu currículo.", detalhes: linhas() };
  } else {
    const d2 = linhas().filter((t) => !/^LattesData:/i.test(t) && !/^Confira tudo/i.test(t) && !/^Aten[cç][aã]o:?$/i.test(t));
    const resumo = (linhas().find((t) => /^LattesData:/i.test(t)) || "Campos preenchidos.").replace(/^LattesData:\s*/i, "");
    res = { estado: /Aten[cç][aã]o/i.test(texto()) ? "atencao" : "ok", titulo: "preenchido — falta você salvar. " + resumo, detalhes: d2 };
  }
  top.alert = alertOriginal;
  await sleep(1200); // dá tempo ao Lattes de desenhar a caixa de aviso, se houver
  const noLattes = avisosNaPagina(window.top, [], 0).filter((x) => !res.detalhes.includes(x));
  if (noLattes.length) {
    res.detalhes = res.detalhes.concat(noLattes.map((x) => "Lattes: " + x));
    if (res.estado === "ok") { res.estado = "atencao"; res.titulo = "o Lattes mostrou um aviso — o item pode NÃO ter sido salvo"; }
  }
  if (res.estado !== "ok" && Array.isArray(d.autores) && d.autores.length) {
    res.detalhes.push("Autores enviados: " + d.autores.slice(0, 6).map((a) => String(a.nome || "?") + " [" + String(a.citacao || "sem citação") + "]").join("; "));
  }
  painel(res.estado, res.titulo, res.detalhes.slice(0, 9));
  return res;
}

async function avisarResultado(res) {
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) {
      if (a.id) chrome.tabs.sendMessage(a.id, { type: "lattes-result", ...res }).catch(() => {});
    }
  } catch (e) {}
}

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

async function aguardarAbaCarregada(tabId, ms = 25000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    try {
      const tab = await chrome.tabs.get(tabId);
      if (tab && tab.status === "complete") return true;
    } catch (e) { return false; }
    await esperar(400);
  }
  return false;
}

// O script marca (sessionStorage da aba, que sobrevive à recarga) quando clica em Salvar: nesse caso NÃO se repete,
// para não gravar o mesmo item duas vezes.
async function jaClicouSalvar(tabId) {
  try {
    const r = await chrome.scripting.executeScript({
      target: { tabId },
      world: "MAIN",
      func: () => { try { const v = Number(window.top.sessionStorage.getItem("lfSalvou") || 0); return v > 0 && Date.now() - v < 90000; } catch (e) { return false; } }
    });
    return !!(r && r[0] && r[0].result);
  } catch (e) { return false; }
}

async function executarAutofillNaAba(tabId, data) {
  let res = null;
  let ultimoErro = "";
  // Logo após o login o Lattes ainda costuma recarregar a página (redirecionamentos): o script some junto e a
  // execução volta sem resultado. Se isso ocorrer ANTES de Salvar, espera a página assentar e tenta de novo.
  for (let tentativa = 1; tentativa <= 3 && !res; tentativa++) {
    try {
      await chrome.scripting.executeScript({ target: { tabId }, world: "MAIN", files: ["autofill_core.js"] });
      const out = await chrome.scripting.executeScript({ target: { tabId }, world: "MAIN", args: [data], func: rodarComFeedback });
      const r = out && out[0] && out[0].result;
      if (r) { res = r; break; }
    } catch (e) {
      ultimoErro = String((e && e.message) || e);
    }
    await aguardarAbaCarregada(tabId);
    await esperar(1200);
    if (await jaClicouSalvar(tabId)) {
      res = {
        estado: "atencao",
        titulo: "o Lattes recarregou a página depois de Salvar. Confira no currículo se o item foi gravado.",
        detalhes: []
      };
    }
  }
  if (!res) {
    res = {
      estado: "erro",
      titulo: "a página do Lattes continuou recarregando e não consegui preencher. Envie de novo.",
      detalhes: ultimoErro ? [ultimoErro] : []
    };
  }
  // Com Salvar automático, confirma de verdade olhando a lista do currículo (e guarda o nº do item para remover depois).
  if (data.__autoSalvar && res.estado !== "erro") {
    const c = await confirmarNaLista(tabId, data);
    if (c.achou) {
      res = { estado: "ok", titulo: "salvo e confirmado no currículo (item nº " + c.seq + ").", detalhes: res.detalhes || [], seq: c.seq };
    } else if (c.consultou) {
      res = { ...res, estado: "atencao", titulo: "cliquei em Salvar, mas o item não apareceu na lista do Lattes. Confira no currículo.", detalhes: res.detalhes || [] };
    }
  }
  // Guarda o resultado: a página recarregada o mostra de novo (ver content-lattes.js).
  return publicarResultado({ envioId: data.__envioId || "", evento: "preenchimento" }, res);
}


// ===== Itens já cadastrados: ler a lista do Lattes, confirmar o que foi salvo, verificar e remover =====
// Mapeado no Lattes real (somente leitura): a lista de cada tipo é uma página HTML cujas linhas trazem o f_seq do
// item; abrir o item é prc_tec_apres?f_cod=<cv>&f_seq=<seq>, e o botão Excluir chama del() (confirm + envio).
const LISTAS_LATTES = {
  apresentacao: {
    lista: "prc_tec_demais_lista?f_cod_tipo=2J&f_cod=",
    item: (cv, seq) => "prc_tec_apres?f_cod=" + cv + "&f_seq=" + seq,
    rotulo: "Apresentação de trabalho e palestra"
  }
};

function normTitulo(s) {
  return String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}
function mesmoTitulo(a, b) {
  const x = normTitulo(a), y = normTitulo(b);
  if (!x || !y) return false;
  if (x === y) return true;
  const n = Math.min(x.length, y.length);
  return n >= 40 && (x.startsWith(y) || y.startsWith(x));
}

// Roda NA página do Lattes (mundo MAIN): lê a lista do tipo e devolve os itens (seq, título, tipo, ano).
async function lerListaNaPagina(listaPath) {
  const html = (window.top.document.documentElement && window.top.document.documentElement.innerHTML) || "";
  const m = html.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i);
  if (!m) return { ok: false, erro: "código do currículo não encontrado na página" };
  try {
    const r = await fetch("/cvlattesweb/" + listaPath + m[1], { credentials: "include" });
    if (!r.ok) return { ok: false, erro: "HTTP " + r.status };
    // O Lattes responde em ISO-8859-1: decodificar como UTF-8 troca os acentos por "�" e o título nunca casa.
    const buf = await r.arrayBuffer();
    const cs = (((r.headers.get("content-type") || "").match(/charset=([^;]+)/i) || [])[1] || "iso-8859-1").trim();
    let texto;
    try { texto = new TextDecoder(cs).decode(buf); } catch (e) { texto = new TextDecoder("iso-8859-1").decode(buf); }
    const doc = new DOMParser().parseFromString(texto, "text/html");
    const itens = [...doc.querySelectorAll("tr[onclick*='f_seq']")].map((tr) => {
      const mm = (tr.getAttribute("onclick") || "").match(/f_seq=(\d+)/);
      const tds = [...tr.querySelectorAll("td")].map((td) => td.textContent.replace(/\s+/g, " ").trim());
      // Na página devolvida pelo servidor as colunas são Título, Tipo, Ano, Visibilidade (conferido no Lattes real);
      // na tela renderizada há antes uma coluna de numeração. Aceita as duas formas.
      const o = /^\d+$/.test(tds[0] || "") ? 1 : 0;
      return { seq: mm ? mm[1] : "", titulo: tds[o] || "", tipo: tds[o + 1] || "", ano: tds[o + 2] || "" };
    }).filter((i) => i.seq);
    return { ok: true, cv: m[1], itens };
  } catch (e) {
    return { ok: false, erro: String((e && e.message) || e) };
  }
}

async function lerLista(tabId, tipo) {
  const cfg = LISTAS_LATTES[tipo];
  if (!cfg) return { ok: false, naoSuportado: true, erro: "tipo sem leitura de lista" };
  try {
    const out = await chrome.scripting.executeScript({ target: { tabId }, world: "MAIN", args: [cfg.lista], func: lerListaNaPagina });
    return (out && out[0] && out[0].result) || { ok: false, erro: "sem resposta da página" };
  } catch (e) {
    return { ok: false, erro: String((e && e.message) || e) };
  }
}

// Procura o item na lista: por seq (se conhecido) ou pelo título (o de maior seq = o mais recente).
function acharItem(itens, titulo, seq) {
  if (seq) {
    return itens.find((i) => i.seq === String(seq)) || null;
  }
  const iguais = itens.filter((i) => mesmoTitulo(i.titulo, titulo));
  iguais.sort((a, b) => Number(b.seq) - Number(a.seq));
  return iguais[0] || null;
}

// Depois de Salvar: confirma de verdade, olhando a lista do currículo, se o item está lá.
async function confirmarNaLista(tabId, data) {
  if (!LISTAS_LATTES[data.tipo_producao]) return { consultou: false };
  await aguardarAbaCarregada(tabId);
  for (let i = 0; i < 4; i++) {
    const l = await lerLista(tabId, data.tipo_producao);
    if (l.ok) {
      const it = acharItem(l.itens, data.titulo, "");
      if (it) return { consultou: true, achou: true, seq: it.seq };
    }
    await esperar(2000);
  }
  return { consultou: true, achou: false };
}

// Roda NA página do Lattes: abre o item pelo f_seq, confere o título e aciona o Excluir do próprio Lattes.
async function abrirEExcluirNaPagina(itemPath, seq, titulo) {
  const top = window.top;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const norm = (s) => String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const bate = (a, b) => { const x = norm(a), y = norm(b); if (!x || !y) return false; if (x === y) return true; const n = Math.min(x.length, y.length); return n >= 40 && (x.startsWith(y) || y.startsWith(x)); };
  if (!top.modalCV2 || typeof top.modalCV2.setarUrl !== "function") return { ok: false, erro: "o Lattes ainda não está pronto (modalCV2)" };
  const janelas = (w, acc = []) => { try { acc.push(w); for (let i = 0; i < w.frames.length; i++) janelas(w.frames[i], acc); } catch (e) {} return acc; };
  top.modalCV2.setarUrl(itemPath, true);
  let alvo = null;
  for (let i = 0; i < 40 && !alvo; i++) {
    await sleep(400);
    for (const w of janelas(top)) {
      try {
        const f = w.document.querySelector('[name="f_seq"]');
        const t = w.document.querySelector('[name="f_titulo"]');
        if (f && t && w.document.readyState === "complete" && String(f.value) === String(seq)) { alvo = { w, titulo: t.value }; break; }
      } catch (e) {}
    }
  }
  if (!alvo) return { ok: false, erro: "não consegui abrir o item no Lattes" };
  if (!bate(alvo.titulo, titulo)) return { ok: false, divergente: true, erro: "o título do item aberto não confere com o registrado (" + String(alvo.titulo).slice(0, 80) + "). Nada foi excluído." };
  if (typeof alvo.w.del !== "function") return { ok: false, erro: "botão Excluir não encontrado no formulário" };
  alvo.w.confirm = () => true; // a confirmação foi dada no LattesData, antes de chegar aqui
  alvo.w.del();
  return { ok: true, acionado: true };
}

async function lattesLogado() {
  const aba = await acharAbaLattes();
  if (!aba) return { aba: null, logado: false };
  const st = await verificarSeAbaLogada(aba.id);
  return { aba, logado: !!st.loggedIn };
}

async function abrirLoginLattes() {
  await prepararCookiesCnpq();
  const nova = await chrome.tabs.create({ url: LATTES_LOGIN_URL, active: true });
  if (nova && nova.windowId) chrome.windows.update(nova.windowId, { focused: true }).catch(() => {});
}

async function publicarResultado(base, res) {
  const completo = { ...res, envioId: base.envioId || "", evento: base.evento };
  try { await chrome.storage.local.set({ ultimoResultadoLattes: { ...completo, ts: Date.now(), exibido: false } }); } catch (e) {}
  await avisarResultado(completo);
  return completo;
}

// Pedido do LattesData: conferir no Lattes se o item (por título) existe e qual é o seq.
async function verificarEnvio(msg) {
  const base = { envioId: msg.envioId, evento: "verificacao" };
  if (!LISTAS_LATTES[msg.tipo]) return publicarResultado(base, { estado: "atencao", titulo: "a verificação automática ainda não existe para este tipo de item.", detalhes: [] });
  const { aba, logado } = await lattesLogado();
  if (!aba || !logado) {
    await abrirLoginLattes();
    return publicarResultado(base, { estado: "login", titulo: "Abri o Lattes: entre no seu currículo e clique em Verificar de novo.", detalhes: [] });
  }
  const l = await lerLista(aba.id, msg.tipo);
  if (!l.ok) return publicarResultado(base, { estado: "erro", titulo: "não consegui ler a lista do Lattes", detalhes: [l.erro || ""] });
  const it = acharItem(l.itens, msg.titulo, "");
  if (!it) return publicarResultado(base, { estado: "ausente", titulo: "o item NÃO está na lista do Lattes.", detalhes: [] });
  return publicarResultado(base, { estado: "ok", titulo: "confirmado: o item está no seu currículo (nº " + it.seq + ").", detalhes: [], seq: it.seq });
}

// Pedido do LattesData: remover o item do Lattes (a confirmação do usuário já foi dada na tela do LattesData).
async function removerEnvio(msg) {
  const base = { envioId: msg.envioId, evento: "remocao" };
  const cfg = LISTAS_LATTES[msg.tipo];
  if (!cfg) return publicarResultado(base, { estado: "nao-suportado", titulo: "a remoção automática ainda não existe para este tipo. Remova direto no Lattes.", detalhes: [] });
  const { aba, logado } = await lattesLogado();
  if (!aba || !logado) {
    await abrirLoginLattes();
    return publicarResultado(base, { estado: "login", titulo: "Abri o Lattes: entre no seu currículo e clique em Remover de novo.", detalhes: [] });
  }
  await chrome.tabs.update(aba.id, { active: true });
  await chrome.windows.update(aba.windowId, { focused: true });
  const antes = await lerLista(aba.id, msg.tipo);
  if (!antes.ok) return publicarResultado(base, { estado: "erro", titulo: "não consegui ler a lista do Lattes antes de remover", detalhes: [antes.erro || ""] });
  const it = acharItem(antes.itens, msg.titulo, msg.seq);
  if (!it) return publicarResultado(base, { estado: "ausente", titulo: "o item já não está na lista do Lattes (talvez já tenha sido removido).", detalhes: [] });
  if (!mesmoTitulo(it.titulo, msg.titulo)) {
    return publicarResultado(base, { estado: "divergente", titulo: "o item nº " + it.seq + " do Lattes tem outro título. Nada foi excluído.", detalhes: [it.titulo.slice(0, 120)] });
  }
  let ac = null;
  try {
    const out = await chrome.scripting.executeScript({
      target: { tabId: aba.id }, world: "MAIN",
      args: [cfg.item(antes.cv, it.seq), it.seq, msg.titulo], func: abrirEExcluirNaPagina
    });
    ac = out && out[0] && out[0].result;
  } catch (e) { /* o Lattes recarrega a página ao excluir: o script some junto; a conferência abaixo decide */ }
  if (ac && !ac.ok) return publicarResultado(base, { estado: ac.divergente ? "divergente" : "erro", titulo: ac.erro || "não consegui acionar o Excluir", detalhes: [] });
  await aguardarAbaCarregada(aba.id);
  await esperar(1500);
  for (let i = 0; i < 4; i++) {
    const depois = await lerLista(aba.id, msg.tipo);
    if (depois.ok && !depois.itens.some((x) => x.seq === it.seq)) {
      return publicarResultado(base, { estado: "removido", titulo: "removido do Lattes (o item nº " + it.seq + " saiu da lista).", detalhes: [], seq: it.seq });
    }
    await esperar(2000);
  }
  return publicarResultado(base, { estado: "erro", titulo: "acionei o Excluir, mas o item continua na lista do Lattes. Confira no currículo.", detalhes: [], seq: it.seq });
}

async function preencher(data) {
  const aba = await acharAbaLattes();
  if (!aba) {
    await chrome.storage.local.set({ pendingLattesFill: { data, ts: Date.now() } });
    await prepararCookiesCnpq();
    const nova = await chrome.tabs.create({ url: LATTES_LOGIN_URL, active: true });
    if (nova && nova.windowId) chrome.windows.update(nova.windowId, { focused: true }).catch(() => {});
    return {
      ok: true,
      queued: true,
      message: "🔐 Abri o Lattes! Faça o login (1ª vez) — assim que entrar, o formulário será aberto e preenchido automaticamente."
    };
  }

  await chrome.tabs.update(aba.id, { active: true });
  await chrome.windows.update(aba.windowId, { focused: true });

  const status = await verificarSeAbaLogada(aba.id);
  if (!status.loggedIn) {
    await chrome.storage.local.set({ pendingLattesFill: { data, ts: Date.now() } });
    if (!(aba.url || "").includes("wwws.cnpq.br/cvlattesweb")) {
      await prepararCookiesCnpq();
      await chrome.tabs.update(aba.id, { url: LATTES_LOGIN_URL });
    }
    return {
      ok: true,
      queued: true,
      message: "🔐 Aguardando seu login na aba do Lattes — o cadastro iniciará sozinho assim que o currículo abrir!"
    };
  }

  await chrome.storage.local.remove("pendingLattesFill");
  executarAutofillNaAba(aba.id, data); // o resultado chega depois, pelo painel e pelo aviso ao LattesData
  return {
    ok: true,
    queued: false,
    message: "🚀 Preenchendo no Lattes… acompanhe o painel na aba do Lattes."
  };
}

async function avisarAbasApp(online, name) {
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) {
      if (a.id) {
        chrome.tabs.sendMessage(a.id, { type: "lattes-status", online, name }).catch(() => {});
      }
    }
  } catch (e) {}
}

let executandoFila = false;

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg) return;

  if (msg.type === "fill") {
    preencher(msg.data).then(sendResponse, (e) =>
      sendResponse({ ok: false, message: String((e && e.message) || e) })
    );
    return true;
  }

  if (msg.type === "remove") {
    removerEnvio(msg).catch(() => {});
    sendResponse({ ok: true, message: "Removendo no Lattes… acompanhe o painel na aba do Lattes." });
    return;
  }

  if (msg.type === "verify") {
    verificarEnvio(msg).catch(() => {});
    sendResponse({ ok: true, message: "Verificando no Lattes…" });
    return;
  }

  if (msg.type === "lattes-heartbeat") {
    avisarAbasApp(!!msg.online, msg.name || "");
    return;
  }

  if (msg.type === "lattes-ready-for-pending" && sender && sender.tab && sender.tab.id) {
    if (executandoFila) return;
    executandoFila = true;
    chrome.storage.local.get("pendingLattesFill", async (res) => {
      try {
        const item = res && res.pendingLattesFill;
        if (item && item.data && Date.now() - (item.ts || 0) < 15 * 60 * 1000) {
          await chrome.storage.local.remove("pendingLattesFill");
          await executarAutofillNaAba(sender.tab.id, item.data);
        }
      } catch (e) {
        console.error("Erro ao retomar fila pós-login:", e);
      } finally {
        executandoFila = false;
      }
    });
  }
});
