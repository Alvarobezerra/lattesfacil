// Service worker: gerencia a conexão com o Lattes, fila pós-login e execução em 1 clique.
importScripts("listas_lattes.js"); // self.LISTAS_POR_ITEM (gerado por build.py)
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
      // Só mensagens reais do Lattes. Fora: rótulos fixos dos formulários (ex.: "Informe o Digital Object Identifier (DOI®) do artigo...") e texto de
      // script do Lattes que contém a mesma frase (aparece no texto da página com <br>, aspas e ponto e vírgula).
      const re = /(N[aã]o foi poss[ií]vel[^\r\n]*)|(O seu nome dever[aá][^\r\n]*)/gi;
      let m;
      while ((m = re.exec(txt)) && acc.length < 6) {
        const linha = m[0].replace(/\s+/g, " ").trim().slice(0, 220);
        if (/<br>|";|function|saida|\\n/.test(linha)) continue;
        if (!acc.includes(linha)) acc.push(linha);
      }
    } catch (e) {}
    try { for (let i = 0; i < w.frames.length; i++) avisosNaPagina(w.frames[i], acc, prof + 1); } catch (e) {}
    return acc;
  }

  const msgs = [];
  // O Lattes deixa na página a caixa "Atenção" de tentativas anteriores (inclusive o texto "Não foi possível atualizar...").
  // Guarda o que já estava lá ANTES de preencher para só acusar avisos novos, e não dar um item salvo como "pode não ter sido salvo".
  let avisosAntes = [];
  try { avisosAntes = avisosNaPagina(window.top, [], 0); } catch (e) {}
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
  const noLattes = avisosNaPagina(window.top, [], 0).filter((x) => !res.detalhes.includes(x) && !avisosAntes.includes(x));
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
  const antesSeqs = data.__autoSalvar && !data.__alterar ? await fotografarLista(tabId, data) : null;
  if (data.__alterar && data.__generico) {
    // ALTERAÇÃO: o endereço do formulário vem da lista do próprio Lattes (nunca do app), pelo nº do item escolhido.
    const l = await lerLista(tabId, tipoDaLista(data));
    const it = l.ok ? l.itens.find((x) => x.seq === String(data.__alterar.seq)) : null;
    if (!it) return publicarResultado({ envioId: "", evento: "preenchimento" }, { estado: "erro", titulo: "o item nº " + data.__alterar.seq + " não está na lista do Lattes: nada foi alterado.", detalhes: [l.erro || ""] });
    data.__generico.url = it.url;
  }
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
  if (data.__autoSalvar && data.__alterar && res.estado !== "erro") {
    await aguardarAbaCarregada(tabId);
    await esperar(1500);
    const l = await lerLista(tabId, tipoDaLista(data));
    const ainda = l.ok && l.itens.some((x) => x.seq === String(data.__alterar.seq));
    res = ainda
      ? { estado: "ok", titulo: "alteração salva: o item nº " + data.__alterar.seq + " continua na lista do currículo.", detalhes: res.detalhes || [], seq: String(data.__alterar.seq) }
      : { ...res, estado: "atencao", titulo: "cliquei em Salvar, mas o item nº " + data.__alterar.seq + " não está mais na lista. Confira no currículo.", detalhes: res.detalhes || [] };
  } else if (data.__autoSalvar && res.estado !== "erro") {
    const c = await confirmarNaLista(tabId, data, antesSeqs);
    if (c.achou) {
      res = { estado: "ok", titulo: "salvo e confirmado no currículo (item nº " + c.seq + ").", detalhes: res.detalhes || [], seq: c.seq };
    } else if (c.consultou) {
      res = { ...res, estado: "atencao", titulo: "cliquei em Salvar, mas o item não apareceu na lista do Lattes. Confira no currículo.", detalhes: res.detalhes || [] };
    }
  }
  enviarLoteInstituicoes(await lerLoteInstituicoes(tabId)); // o que a lupa devolveu durante o preenchimento alimenta o banco
  // Guarda o resultado: a página recarregada o mostra de novo (ver content-lattes.js).
  return publicarResultado({ envioId: data.__envioId || "", evento: "preenchimento" }, res);
}

// ===== Banco de instituições: o que a lupa do Lattes devolve (uso e coleta gradual) vai para o LattesData =====
// O script do formulário guarda cada consulta da lupa em window.top.__lfInstLote; aqui se lê (e zera) e se repassa às abas do app,
// que gravam no servidor com a sessão do usuário. Nada do currículo vai junto: só nome e argumentos do link da instituição.
async function lerLoteInstituicoes(tabId) {
  try {
    const r = await chrome.scripting.executeScript({
      target: { tabId },
      world: "MAIN",
      func: () => { try { const l = window.top.__lfInstLote || []; window.top.__lfInstLote = []; return l; } catch (e) { return []; } }
    });
    return (r && r[0] && r[0].result) || [];
  } catch (e) { return []; }
}

async function enviarLoteInstituicoes(lote, fim) {
  if ((!lote || !lote.length) && !fim) return;
  (lote || []).forEach((q) => { q.lote_id = String(q.lote_id || crypto.randomUUID().replace(/-/g, "")); }); // o mesmo id em todas as abas do app: o servidor descarta repetidos
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) if (a.id) chrome.tabs.sendMessage(a.id, { type: "lattes-inst-lote", lote: lote || [], fim: fim || null }).catch(() => {});
  } catch (e) {}
}

// Roda NA página do Lattes: espera o painel pronto e executa o modo "coleta" do script de preenchimento (só pesquisa na lupa).
async function rodarColeta(d) {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const top = window.top;
  const msgs = [];
  const alertOriginal = top.alert;
  top.alert = (m) => { msgs.push(String(m)); };
  try {
    top.__lfInstFim = null;
    top.__lfInstLote = [];
    const pronto = () => { try { const h = top.document.documentElement.innerHTML || ""; return top.document.readyState === "complete" && !!top.modalCV2 && typeof top.modalCV2.setarUrl === "function" && /[?&]f_cod=[A-Za-z0-9]{6,20}/i.test(h); } catch (e) { return false; } };
    for (let i = 0; i < 60 && !pronto(); i++) await sleep(500);
    if (!pronto()) return { ok: false, erro: "o Lattes não terminou de carregar o currículo" };
    await sleep(800);
    await window.__lfAutofill(d);
    const fim = top.__lfInstFim;
    if (fim) return fim;
    return { ok: false, erro: msgs.join(" ").slice(0, 300) || "a coleta não chegou ao fim" };
  } catch (e) {
    return { ok: false, erro: String((e && e.message) || e).slice(0, 300) };
  } finally {
    top.alert = alertOriginal;
  }
}

let coletando = false;
async function coletarInstituicoes(msg) {
  if (coletando) return { ok: false, message: "Já existe uma coleta em andamento." };
  const aba = await acharAbaLattes();
  if (!aba) return { ok: false, message: "Abra o Lattes e faça o login para coletar instituições." };
  const st = await verificarSeAbaLogada(aba.id);
  if (!st.loggedIn) return { ok: false, message: "A aba do Lattes não está com o currículo aberto (login)." };
  coletando = true;
  (async () => {
    let fim = { ok: false, erro: "coleta interrompida" };
    try {
      const d = {
        tipo_producao: "generico", __usuario: String(msg.usuario || "").slice(0, 120),
        __generico: { url: String(msg.url || ""), item: "coleta de instituições", campos: [], grades: {}, faltam: [],
                      coleta: { termos: (msg.termos || []).map((t) => String(t).slice(0, 120)).slice(0, 25), intervalo_ms: Number(msg.intervalo_ms) || 4000 } }
      };
      await chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", files: ["autofill_core.js"] });
      const out = await comLimite(chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", args: [d], func: rodarColeta }), 25 * 60 * 1000, null);
      if (out && out[0] && out[0].result) fim = out[0].result;
    } catch (e) {
      fim = { ok: false, erro: String((e && e.message) || e).slice(0, 300) };
    } finally {
      coletando = false;
    }
    await enviarLoteInstituicoes(await lerLoteInstituicoes(aba.id), fim);
  })();
  return { ok: true, message: "Coleta iniciada na aba do Lattes. Não feche a aba até terminar." };
}


// ===== Itens já cadastrados: ler a lista do Lattes, confirmar o que foi salvo, verificar e remover =====
// Mapeado no Lattes real (somente leitura): a lista de cada tipo é uma página HTML cujas linhas trazem o f_seq do
// item; abrir o item é prc_tec_apres?f_cod=<cv>&f_seq=<seq>, e o botão Excluir chama del() (confirm + envio).
// Cada item do Lattes com lista mapeada (itens/listas_lattes.json): a lista e, por linha, o formulário do item (onclick).
const LISTAS_LATTES = {};
for (const [id, caminho] of Object.entries(self.LISTAS_POR_ITEM || {})) {
  LISTAS_LATTES[id] = { lista: caminho + (caminho.includes("?") ? "&" : "?") + "f_cod=", rotulo: id };
}

function normTitulo(s) {
  return String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}
function mesmoTitulo(a, b) {
  const x = normTitulo(a), y = normTitulo(b);
  if (!x || !y) return false;
  if (x === y) return true;
  const n = Math.min(x.length, y.length);
  // Itens genéricos: o texto da lista pode ser só parte do campo do formulário (ou o contrário).
  return (n >= 40 && (x.startsWith(y) || y.startsWith(x))) || (n >= 10 && (x.includes(y) || y.includes(x)));
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
    const itens = [...doc.querySelectorAll("tr[onclick*='setarUrl']")].map((tr) => {
      const oc = tr.getAttribute("onclick") || "";
      const mu = oc.match(/setarUrl\(\s*['"]([^'"]+)['"]/);
      const url = mu ? mu[1] : "";
      // nº do item: f_seq, f_seq_ativ... (ou o 1º parâmetro numérico que não seja o código do currículo)
      const ms = url.match(/[?&]f_seq[a-z_]*=(\d+)/i) || url.match(/[?&](?!f_cod=|f_tipo|f_cod_tipo)[a-z_]+=(\d+)/i);
      const tds = [...tr.querySelectorAll("td")].map((td) => td.textContent.replace(/\s+/g, " ").trim());
      // Colunas conferidas no Lattes real: Título, Tipo, Ano, Visibilidade (na tela há antes uma coluna de numeração).
      const o = /^\d+$/.test(tds[0] || "") ? 1 : 0;
      return { seq: ms ? ms[1] : "", titulo: tds[o] || "", tipo: tds[o + 1] || "", ano: tds[o + 2] || "", url, linha: tds.join(" | ") };
    }).filter((i) => i.seq && i.url);
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

// Listas como as de orientações não trazem o título na 1ª coluna (vem o orientando, a natureza...): o título vale se
// aparecer em qualquer coluna da linha.
function casaItem(i, titulo) {
  if (mesmoTitulo(i.titulo, titulo)) return true;
  const t = normTitulo(titulo);
  return t.length >= 10 && normTitulo(i.linha || "").includes(t);
}

// Procura o item na lista: por seq (se conhecido) ou pelo título (o de maior seq = o mais recente).
function acharItem(itens, titulo, seq) {
  if (seq) {
    return itens.find((i) => i.seq === String(seq)) || null;
  }
  const iguais = itens.filter((i) => casaItem(i, titulo));
  iguais.sort((a, b) => Number(b.seq) - Number(a.seq));
  return iguais[0] || null;
}

// Id do item para a lista: "apresentação" (legado) vem em tipo_producao; os genéricos, em __generico.item.
function tipoDaLista(data) {
  if (data.tipo_producao === "orientacao" && data.situacao_orientacao === "Em andamento") return "orientacao_andamento";
  return data.tipo_producao === "generico" ? ((data.__generico || {}).id || "") : data.tipo_producao;
}

// Antes de preencher: guarda os nºs que a lista já tem, para reconhecer depois o item novo (vale para qualquer título).
async function fotografarLista(tabId, data) {
  const tipo = tipoDaLista(data);
  if (!LISTAS_LATTES[tipo]) return null;
  const l = await lerLista(tabId, tipo);
  return l.ok ? l.itens.map((i) => i.seq) : null;
}

// Depois de Salvar: confirma de verdade, olhando a lista do currículo, se o item está lá.
async function confirmarNaLista(tabId, data, antesSeqs) {
  const tipo = tipoDaLista(data);
  if (!LISTAS_LATTES[tipo]) return { consultou: false };
  await aguardarAbaCarregada(tabId);
  for (let i = 0; i < 4; i++) {
    const l = await lerLista(tabId, tipo);
    if (l.ok) {
      let it = null;
      if (Array.isArray(antesSeqs)) {
        const novos = l.itens.filter((x) => !antesSeqs.includes(x.seq));
        if (novos.length === 1) it = novos[0];
        else if (novos.length > 1) it = acharItem(novos, data.titulo, "");
      }
      if (!it) it = acharItem(l.itens, data.titulo, "");
      if (it) return { consultou: true, achou: true, seq: it.seq };
    }
    await esperar(2000);
  }
  return { consultou: true, achou: false };
}

// Roda NA página do Lattes: abre o item pelo formulário da linha da lista, confere que é ele e aciona o Excluir do Lattes.
async function abrirEExcluirNaPagina(itemPath, seq, titulo) {
  const top = window.top;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const norm = (s) => String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const bate = (a, b) => { const x = norm(a), y = norm(b); if (!x || !y) return false; if (x === y) return true; const n = Math.min(x.length, y.length); return (n >= 40 && (x.startsWith(y) || y.startsWith(x))) || (n >= 10 && (x.includes(y) || y.includes(x))); };
  if (!top.modalCV2 || typeof top.modalCV2.setarUrl !== "function") return { ok: false, erro: "o Lattes ainda não está pronto (modalCV2)" };
  const janelas = (w, acc = []) => { try { acc.push(w); for (let i = 0; i < w.frames.length; i++) janelas(w.frames[i], acc); } catch (e) {} return acc; };
  top.modalCV2.setarUrl(itemPath, true);
  let alvo = null;
  for (let i = 0; i < 40 && !alvo; i++) {
    await sleep(400);
    for (const w of janelas(top)) {
      try {
        if (w.document.readyState !== "complete" || typeof w.del !== "function") continue;
        // o formulário certo traz o nº do item num campo f_seq*; sem esse campo, vale o que a linha da lista abriu
        const campo = [...w.document.querySelectorAll("input")].find((x) => /^f_seq/i.test(x.name || "") && String(x.value) === String(seq));
        if (campo || (!w.document.querySelector('[name^="f_seq"]') && w.document.querySelector("form"))) { alvo = { w }; break; }
      } catch (e) {}
    }
  }
  if (!alvo) return { ok: false, erro: "não consegui abrir o item no Lattes" };
  // Conferência de identidade: se o formulário tem algum campo de texto com o título (ou o nome) do item, ele precisa bater.
  const textos = [...alvo.w.document.querySelectorAll('input[type="text"],textarea')].map((x) => x.value).filter((v) => v && v.length >= 6);
  if (textos.length && !textos.some((v) => bate(v, titulo))) {
    return { ok: false, divergente: true, erro: "o item aberto não confere com o registrado (" + String(textos[0]).slice(0, 80) + "). Nada foi excluído." };
  }
  alvo.w.confirm = () => true; // a confirmação foi dada no LattesData, antes de chegar aqui
  setTimeout(() => alvo.w.del(), 50); // adia: o Lattes recarrega a página ao excluir e a caixa nativa travaria a automação
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

// Pedido do LattesData: listar os itens já cadastrados de um tipo (para o usuário escolher qual ALTERAR).
async function avisarLista(res) {
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) if (a.id) chrome.tabs.sendMessage(a.id, { type: "lattes-lista", ...res }).catch(() => {});
  } catch (e) {}
}

async function listarItens(msg) {
  const tipo = String(msg.tipo || "");
  if (!LISTAS_LATTES[tipo]) return avisarLista({ ok: false, tipo, erro: "este tipo não tem lista mapeada no Lattes." });
  const { aba, logado } = await lattesLogado();
  if (!aba || !logado) {
    await abrirLoginLattes();
    return avisarLista({ ok: false, tipo, login: true, erro: "Abri o Lattes: entre no seu currículo e peça a lista de novo." });
  }
  const l = await lerLista(aba.id, tipo);
  return avisarLista({
    ok: !!l.ok, tipo, erro: l.erro || "",
    itens: (l.itens || []).map((i) => ({ seq: i.seq, titulo: i.titulo, tipo: i.tipo, ano: i.ano }))
  });
}

// Rotina de primeiro acesso: lê "Autores citados no currículo" (menu lateral, pkg_dic_autor.lista) e devolve as linhas da tabela.
// Roda NA página do Lattes (mundo MAIN). A tabela ainda não foi mapeada célula a célula: devolve os textos de cada linha e o servidor interpreta.
async function lerAutoresNaPagina() {
  const html = (window.top.document.documentElement && window.top.document.documentElement.innerHTML) || "";
  const m = html.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i);
  if (!m) return { ok: false, erro: "código do currículo não encontrado na página" };
  try {
    const r = await fetch("/cvlattesweb/pkg_dic_autor.lista?f_cod=" + m[1], { credentials: "include" });
    if (!r.ok) return { ok: false, erro: "HTTP " + r.status };
    const buf = await r.arrayBuffer();
    const cs = (((r.headers.get("content-type") || "").match(/charset=([^;]+)/i) || [])[1] || "iso-8859-1").trim();
    let texto;
    try { texto = new TextDecoder(cs).decode(buf); } catch (e) { texto = new TextDecoder("iso-8859-1").decode(buf); }
    const doc = new DOMParser().parseFromString(texto, "text/html");
    const linhas = [...doc.querySelectorAll("tr")].map((tr) => [...tr.querySelectorAll("td, th")].map((td) => td.textContent.replace(/\s+/g, " ").trim())).filter((c) => c.some((x) => x));
    return { ok: true, cv: m[1], linhas: linhas.slice(0, 5000), amostra: linhas.slice(0, 3).map((c) => c.join(" | ").slice(0, 160)), texto: linhas.length ? "" : (doc.body ? doc.body.textContent.replace(/\s+/g, " ").trim().slice(0, 200) : "") };
  } catch (e) {
    return { ok: false, erro: String((e && e.message) || e) };
  }
}

async function avisarAutores(res) {
  try {
    const abas = await chrome.tabs.query({ url: APP_PATTERNS });
    for (const a of abas) if (a.id) chrome.tabs.sendMessage(a.id, { type: "lattes-autores", ...res }).catch(() => {});
  } catch (e) {}
}

async function coletarAutores() {
  const { aba, logado } = await lattesLogado();
  if (!aba || !logado) {
    await abrirLoginLattes();
    return avisarAutores({ ok: false, login: true, erro: "Abri o Lattes: entre no seu currículo e a coleta dos autores recomeça sozinha." });
  }
  try {
    const out = await chrome.scripting.executeScript({ target: { tabId: aba.id }, world: "MAIN", func: lerAutoresNaPagina });
    const r = (out && out[0] && out[0].result) || { ok: false, erro: "sem resposta da página" };
    return avisarAutores(r);
  } catch (e) {
    return avisarAutores({ ok: false, erro: String((e && e.message) || e).slice(0, 300) });
  }
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
  if (!casaItem(it, msg.titulo)) {
    return publicarResultado(base, { estado: "divergente", titulo: "o item nº " + it.seq + " do Lattes tem outro título. Nada foi excluído.", detalhes: [it.titulo.slice(0, 120)] });
  }
  let ac = null;
  try {
    const out = await chrome.scripting.executeScript({
      target: { tabId: aba.id }, world: "MAIN",
      args: [it.url, it.seq, msg.titulo], func: abrirEExcluirNaPagina
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

  if (msg.type === "inst-coleta") {
    coletarInstituicoes(msg).then(sendResponse, (e) => sendResponse({ ok: false, message: String((e && e.message) || e) }));
    return true;
  }

  if (msg.type === "autores-coleta") {
    coletarAutores().catch(() => {});
    sendResponse({ ok: true, message: "Lendo os autores citados no seu currículo…" });
    return;
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

  if (msg.type === "list") {
    listarItens(msg).catch(() => {});
    sendResponse({ ok: true, message: "Lendo a lista no Lattes…" });
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
