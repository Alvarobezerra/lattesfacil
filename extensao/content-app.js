// Roda nas páginas do LattesData (local e Render). Faz a ponte entre a página e a extensão.
window.addEventListener("message", (e) => {
  if (e.source !== window || e.origin !== location.origin) return;
  const m = e.data;
  if (!m || typeof m !== "object") return;
  if (m.type === "lattesdata-ext-ping") {
    window.postMessage({ type: "lattesdata-ext-pong", version: chrome.runtime.getManifest().version }, location.origin);
  } else if (m.type === "lattesdata-ext-remove" || m.type === "lattesdata-ext-verify") {
    chrome.runtime.sendMessage({
      type: m.type === "lattesdata-ext-remove" ? "remove" : "verify",
      envioId: String(m.envioId || "").slice(0, 16),
      tipo: String(m.tipo || "").slice(0, 30),
      titulo: String(m.titulo || "").slice(0, 400),
      seq: String(m.seq || "").replace(/\D/g, "").slice(0, 12)
    }, () => { void chrome.runtime.lastError; });
  } else if (m.type === "lattesdata-ext-fill") {
    chrome.runtime.sendMessage({ type: "fill", data: m.data }, (resp) => {
      const err = chrome.runtime.lastError;
      window.postMessage(
        {
          type: "lattesdata-ext-result",
          ok: !err && !!(resp && resp.ok),
          queued: !!(resp && resp.queued),
          message: err ? err.message : (resp && resp.message) || ""
        },
        location.origin
      );
    });
  }
});

// Recebe atualizações automáticas de status da aba do Lattes via background service worker.
chrome.runtime.onMessage.addListener((msg) => {
  if (msg && msg.type === "lattes-result") {
    window.postMessage({
      type: "lattesdata-ext-result",
      ok: msg.estado === "ok",
      estado: String(msg.estado || ""),
      envioId: String(msg.envioId || ""),
      evento: String(msg.evento || ""),
      seq: String(msg.seq || ""),
      message: String(msg.titulo || ""),
      detalhes: Array.isArray(msg.detalhes) ? msg.detalhes.map((x) => String(x).slice(0, 300)).slice(0, 8) : []
    }, location.origin);
    return;
  }
  if (msg && msg.type === "lattes-status") {
    window.postMessage({ type: "lattesfacil-status", online: !!msg.online, name: msg.name || "" }, location.origin);
  }
});

// Anuncia presença assim que o script carrega.
window.postMessage({ type: "lattesdata-ext-pong", version: chrome.runtime.getManifest().version }, location.origin);
