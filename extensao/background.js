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
  // Pode haver várias abas do Lattes (login antigo, página inicial, currículo). Vale a primeira que estiver no currículo logado.
  const abas = (await chrome.tabs.query({ url: LATTES_PATTERNS })).filter((t) => (t.url || "").includes("wwws.cnpq.br"));
  abas.sort((a, b) => Number(!!b.active) - Number(!!a.active));
  for (const aba of abas) {
    const st = await verificarSeAbaLogada(aba.id);
    if (st.loggedIn) return { aba, logado: true };
  }
  const aba = await acharAbaLattes();
  return { aba, logado: false };
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

// ---- Aviso "alterações ainda não enviadas ao CNPq" (quadro de avisos do currículo) ----
// O Lattes guarda as edições na área de edição; só valem para o CNPq e a busca pública depois do envio definitivo.

// Roda NA página do Lattes: lê o quadro de avisos. {ok:false} = não achei o quadro (a aba não está no currículo).
function lerPendenciaNaPagina() {
  const janelas = (w, acc = []) => { try { acc.push(w); for (let i = 0; i < w.frames.length; i++) janelas(w.frames[i], acc); } catch (e) {} return acc; };
  let quadro = false;
  for (const w of janelas(window.top)) {
    try {
      const txt = (w.document.body && w.document.body.innerText) || "";
      if (/ainda não foram enviadas ao CNPq/i.test(txt)) return { ok: true, pendente: true };
      if (/Início dos avisos/i.test(txt)) quadro = true;
    } catch (e) {}
  }
  return quadro ? { ok: true, pendente: false } : { ok: false };
}

// Roda NA página do Lattes: clica no próprio aviso, que abre a tela de envio ao CNPq. Não confirma o envio.
function abrirTelaEnvioNaPagina() {
  const janelas = (w, acc = []) => { try { acc.push(w); for (let i = 0; i < w.frames.length; i++) janelas(w.frames[i], acc); } catch (e) {} return acc; };
  for (const w of janelas(window.top)) {
    try {
      const a = [...w.document.querySelectorAll("a")].find((x) => /ainda não foram enviadas ao CNPq/i.test(x.textContent || ""));
      if (a) { a.click(); return { ok: true }; }
    } catch (e) {}
  }
  return { ok: false };
}

// Roda NA página do Lattes: a tela de envio ao CNPq (pkg_publicar) está carregada num quadro?
function telaEnvioAbertaNaPagina() {
  const janelas = (w, acc = []) => { try { acc.push(w); for (let i = 0; i < w.frames.length; i++) janelas(w.frames[i], acc); } catch (e) {} return acc; };
  for (const w of janelas(window.top)) {
    try { if ([...w.document.querySelectorAll("iframe")].some((f) => /pkg_publicar/i.test(f.src || ""))) return { aberta: true }; } catch (e) {}
  }
  return { aberta: false };
}

// Espera a promessa, mas no máximo `ms`: um passo travado não pode deixar o LattesData sem resposta.
function comLimite(promessa, ms, padrao) {
  return Promise.race([promessa, new Promise((r) => setTimeout(() => r(padrao), ms))]);
}

async function pendenciaDaAba(tabId) {
  try {
    const out = await chrome.scripting.executeScript({ target: { tabId, allFrames: false }, world: "MAIN", func: lerPendenciaNaPagina });
    return (out && out[0] && out[0].result) || { ok: false };
  } catch (e) { return { ok: false }; }
}

async function abaDoCurriculo(base) {
  const { aba, logado } = await lattesLogado();
  if (!aba || !logado) {
    await abrirLoginLattes();
    await publicarResultado(base, { estado: "login", titulo: "Abri o Lattes: entre no seu currículo e tente de novo.", detalhes: [] });
    return null;
  }
  return aba;
}

const SEM_QUADRO = { estado: "indisponivel", titulo: "não achei o quadro de avisos: abra o seu currículo (página inicial do Lattes) e tente de novo.", detalhes: [] };

// Roda NA página do Lattes: pede ao próprio Lattes a "página para impressão" (modelo Completo, todas as seções), que é gerada na
// hora a partir do currículo atual. Só leitura (GET do formulário + POST que gera a página). Devolve o HTML já decodificado.
async function lerPaginaNaAba() {
  try {
    const a = document.querySelector('a[title*="Gerar arquivo"]');
    const m = a && (a.getAttribute("onclick") || "").match(/'([^']+)'/);
    if (!m) return { ok: false, erro: "não achei a opção de gerar a página no menu do currículo (abra o seu currículo)" };
    const form = new DOMParser().parseFromString(await (await fetch(m[1], { credentials: "include" })).text(), "text/html");
    const cod = form.querySelector("input[name=f_cod]");
    if (!cod) return { ok: false, erro: "o Lattes não devolveu o formulário (sessão expirada?)" };
    const c = new URLSearchParams();
    c.append("f_cod", cod.value); c.append("f_check", "DUMMY"); c.append("f_ctr", ""); c.append("f_fmt", "H"); c.append("f_tpo_arq", "0");
    form.querySelectorAll("input[name=f_check][type=checkbox]").forEach((x) => c.append("f_check", x.value)); // todas as seções
    c.append("f_tpo", "C"); c.append("f_est", "1"); c.append("f_idioma", "1"); c.append("f_padrao", "A");
    c.append("f_per_atu", "0"); c.append("f_ano_atu", ""); c.append("f_cit", "1"); c.append("f_per_prod", "0"); c.append("f_ano_prod", "");
    const r = await fetch("pkg_impcv.trata", { method: "POST", credentials: "include", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: c.toString() });
    if (!r.ok) return { ok: false, erro: "o Lattes respondeu " + r.status };
    const html = new TextDecoder("iso-8859-1").decode(await r.arrayBuffer()); // a página vem em ISO-8859-1
    const nome = document.getElementById("nmeLt");
    return { ok: true, html, nome: nome ? nome.textContent.trim() : "" };
  } catch (e) { return { ok: false, erro: String((e && e.message) || e) }; }
}

// Pedido do LattesData: lê o currículo atual direto do Lattes (sem depender do XML, que pode estar defasado).
async function lerCvAoVivo() {
  const base = { envioId: "", evento: "leitura" };
  const aba = await abaDoCurriculo(base);
  if (!aba) return;
  await publicarResultado(base, { estado: "lendo", titulo: "Lendo o seu currículo no Lattes…", detalhes: [] });
  let r = null;
  try {
    const out = await comLimite(chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", func: lerPaginaNaAba }), 60000, null);
    r = out && out[0] && out[0].result;
  } catch (e) { r = { ok: false, erro: String((e && e.message) || e) }; }
  if (!r) r = { ok: false, erro: "o Lattes demorou demais para responder" };
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) if (a.id) chrome.tabs.sendMessage(a.id, { type: "lattes-live", ok: !!r.ok, html: r.html || "", nome: r.nome || "", erro: r.erro || "" }).catch(() => {});
  } catch (e) {}
}

// Pedido do LattesData: o currículo tem alterações pendentes de envio ao CNPq? Só lê.
async function statusCv() {
  const base = { envioId: "", evento: "pendencia" };
  const aba = await abaDoCurriculo(base);
  if (!aba) return;
  const p = await pendenciaDaAba(aba.id);
  if (!p.ok) return publicarResultado(base, SEM_QUADRO);
  if (p.pendente) return publicarResultado(base, { estado: "pendente", titulo: "O currículo tem alterações que ainda não foram enviadas ao CNPq.", detalhes: ["Se você acabou de enviar, recarregue a aba do Lattes (F5) e verifique de novo."] });
  return publicarResultado(base, { estado: "em_dia", titulo: "Nenhuma alteração pendente: o CNPq já tem a versão atual do currículo.", detalhes: [] });
}

// Pedido do LattesData (confirmado pelo usuário lá): abre a tela de envio ao CNPq. O clique final em Enviar é do usuário.
async function enviarCv() {
  const base = { envioId: "", evento: "pendencia" };
  const aba = await abaDoCurriculo(base);
  if (!aba) return;
  // Feedback imediato: o LattesData sempre recebe um sinal, mesmo que um passo seguinte demore ou falhe.
  await publicarResultado(base, { estado: "abrindo", titulo: "Procurando o aviso no Lattes…", detalhes: [] });
  // Foco na aba do Lattes é conveniência: se falhar (janela fechada, SO sem foco), o resto continua.
  try { await chrome.tabs.update(aba.id, { active: true }); await chrome.windows.update(aba.windowId, { focused: true }); } catch (e) {}
  const p = await comLimite(pendenciaDaAba(aba.id), 8000, { ok: false });
  if (!p.ok) return publicarResultado(base, SEM_QUADRO);
  if (!p.pendente) return publicarResultado(base, { estado: "em_dia", titulo: "Nenhuma alteração pendente: não há nada a enviar ao CNPq.", detalhes: [] });
  const abriu = await comLimite(
    chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", func: abrirTelaEnvioNaPagina }).then((o) => o && o[0] && o[0].result, () => null),
    8000, null);
  if (!abriu || !abriu.ok) return publicarResultado(base, { estado: "erro", titulo: "não consegui abrir a tela de envio. Use o ícone Enviar, no canto superior direito do Lattes.", detalhes: [] });
  let visivel = false; // confirma que a tela abriu de fato (o Lattes a carrega num quadro)
  for (let i = 0; i < 8 && !visivel; i++) {
    await esperar(1000);
    const t = await comLimite(chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", func: telaEnvioAbertaNaPagina }).then((o) => o && o[0] && o[0].result, () => null), 4000, null);
    visivel = !!(t && t.aberta);
  }
  if (!visivel) return publicarResultado(base, { estado: "erro", titulo: "cliquei no aviso, mas não vi a tela de envio abrir. Confira a aba do Lattes ou use o ícone Enviar.", detalhes: [] });
  await publicarResultado(base, { estado: "aguardando_envio", titulo: "Abri a tela de envio ao CNPq na aba do Lattes. Confira e clique em Enviar nela: o último clique é seu.", detalhes: [] });
  for (let i = 0; i < 36; i++) { // acompanha por ~3 min; depois disso o botão Verificar refaz a checagem
    await esperar(5000);
    const q = await pendenciaDaAba(aba.id);
    if (q.ok && !q.pendente) return publicarResultado(base, { estado: "em_dia", titulo: "O Lattes não mostra mais alterações pendentes: o currículo foi enviado ao CNPq.", detalhes: [] });
  }
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

  if (msg.type === "cv-status") {
    statusCv().catch(() => {});
    sendResponse({ ok: true, message: "Verificando o quadro de avisos do Lattes…" });
    return;
  }

  if (msg.type === "cv-live") {
    lerCvAoVivo().catch(() => {});
    sendResponse({ ok: true, message: "Lendo o currículo no Lattes…" });
    return;
  }

  if (msg.type === "cv-publish") {
    enviarCv().catch(() => {});
    sendResponse({ ok: true, message: "Abrindo a tela de envio ao CNPq…" });
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
