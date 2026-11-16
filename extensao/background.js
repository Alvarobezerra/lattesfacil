// Service worker: gerencia a conexão com o Lattes, fila pós-login e execução em 1 clique.
const LATTES_LOGIN_URL = "https://wwws.cnpq.br/cvlattesweb/pkg_cv_estr.inicio";
const LATTES_PATTERNS = ["https://wwws.cnpq.br/*", "https://lattes.cnpq.br/*"];
const APP_PATTERNS = ["http://localhost/*", "http://127.0.0.1/*", "https://*.onrender.com/*"];

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

async function executarAutofillNaAba(tabId, data) {
  await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    files: ["autofill_core.js"]
  });
  await chrome.scripting.executeScript({
    target: { tabId },
    world: "MAIN",
    args: [data],
    func: (d) => window.__lfAutofill(d)
  });
}

async function preencher(data) {
  const aba = await acharAbaLattes();
  if (!aba) {
    await chrome.storage.local.set({ pendingLattesFill: { data, ts: Date.now() } });
    await chrome.tabs.create({ url: LATTES_LOGIN_URL, active: true });
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
      await chrome.tabs.update(aba.id, { url: LATTES_LOGIN_URL });
    }
    return {
      ok: true,
      queued: true,
      message: "🔐 Aguardando seu login na aba do Lattes — o cadastro iniciará sozinho assim que o currículo abrir!"
    };
  }

  await chrome.storage.local.remove("pendingLattesFill");
  await executarAutofillNaAba(aba.id, data);
  return {
    ok: true,
    queued: false,
    message: "🚀 Abrindo formulário no Lattes e preenchendo automaticamente!"
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
