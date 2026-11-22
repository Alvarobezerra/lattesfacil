// Roda nas páginas do NautiScience (local e Render). Faz a ponte entre a página e a extensão.
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
  } else if (m.type === "lattesdata-ext-list") {
    chrome.runtime.sendMessage({ type: "list", tipo: String(m.tipo || "").replace(/[^a-z_]/g, "").slice(0, 40) }, () => { void chrome.runtime.lastError; });
  } else if (m.type === "lattesdata-ext-autores") {
    chrome.runtime.sendMessage({ type: "autores-coleta" }, () => { void chrome.runtime.lastError; });
  } else if (m.type === "lattesdata-ext-cv-live") {
    chrome.runtime.sendMessage({ type: "cv-live" }, () => { void chrome.runtime.lastError; });
  } else if (m.type === "lattesdata-ext-cv-status" || m.type === "lattesdata-ext-cv-publish") {
    chrome.runtime.sendMessage({ type: m.type === "lattesdata-ext-cv-status" ? "cv-status" : "cv-publish" }, () => { void chrome.runtime.lastError; });
  } else if (m.type === "lattesdata-ext-inst-coleta") {
    chrome.runtime.sendMessage({
      type: "inst-coleta",
      termos: Array.isArray(m.termos) ? m.termos.map((t) => String(t).slice(0, 120)).slice(0, 25) : [],
      intervalo_ms: Math.max(2000, Math.min(60000, Number(m.intervalo_ms) || 4000)),
      url: String(m.url || "").slice(0, 200),
      usuario: String(m.usuario || "").slice(0, 120)
    }, (resp) => {
      const err = chrome.runtime.lastError;
      window.postMessage({ type: "lattesdata-ext-inst-coleta-resp", ok: !err && !!(resp && resp.ok), message: err ? err.message : (resp && resp.message) || "" }, location.origin);
    });
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
  if (msg && msg.type === "lattes-lista") { // itens já cadastrados de um tipo (para alterar)
    window.postMessage({
      type: "lattesdata-ext-lista", ok: !!msg.ok, tipoItem: String(msg.tipo || "").slice(0, 40), login: !!msg.login, erro: String(msg.erro || "").slice(0, 300),
      itens: Array.isArray(msg.itens) ? msg.itens.slice(0, 500).map((i) => ({ seq: String(i.seq || "").replace(/\D/g, "").slice(0, 12), titulo: String(i.titulo || "").slice(0, 300), tipo: String(i.tipo || "").slice(0, 80), ano: String(i.ano || "").slice(0, 8) })) : []
    }, location.origin);
    return;
  }
  if (msg && msg.type === "lattes-autores") { // autores citados no currículo (rotina de primeiro acesso)
    window.postMessage({
      type: "lattesdata-ext-autores-resp", ok: !!msg.ok, login: !!msg.login, erro: String(msg.erro || "").slice(0, 300), cv: String(msg.cv || "").replace(/[^A-Za-z0-9]/g, "").slice(0, 20),
      linhas: (Array.isArray(msg.linhas) ? msg.linhas : []).slice(0, 5000).map((l) => (Array.isArray(l) ? l : [l]).slice(0, 8).map((c) => String(c || "").slice(0, 200))),
      amostra: (Array.isArray(msg.amostra) ? msg.amostra : []).slice(0, 3).map((x) => String(x).slice(0, 160)), texto: String(msg.texto || "").slice(0, 200)
    }, location.origin);
    return;
  }
  if (msg && msg.type === "lattes-live") { // leitura em tempo real do currículo (HTML da página para impressão)
    window.postMessage({ type: "lattesdata-ext-live", ok: !!msg.ok, html: String(msg.html || ""), nome: String(msg.nome || "").slice(0, 200), erro: String(msg.erro || "").slice(0, 300) }, location.origin);
    return;
  }
  if (msg && msg.type === "lattes-inst-lote") { // consultas da lupa (uso e coleta) para o banco de instituições
    const lote = (Array.isArray(msg.lote) ? msg.lote : []).slice(0, 40).map((q) => ({
      lote_id: String(q.lote_id || "").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 40), termo: String(q.termo || "").slice(0, 120), origem: q.origem === "coleta" ? "coleta" : "uso", ms: Math.max(0, Number(q.ms) || 0), erro: String(q.erro || "").slice(0, 200),
      itens: (Array.isArray(q.itens) ? q.itens : []).slice(0, 300).map((i) => ({ nome: String(i.nome || "").slice(0, 200), ref: String(i.ref || "").slice(0, 200) }))
    }));
    const fim = msg.fim ? { ok: !!msg.fim.ok, feitos: Number(msg.fim.feitos) || 0, erros: Number(msg.fim.erros) || 0, total: Number(msg.fim.total) || 0, erro: String(msg.fim.erro || "").slice(0, 300) } : null;
    window.postMessage({ type: "lattesdata-ext-inst-lote", lote, fim }, location.origin);
    return;
  }
  if (msg && msg.type === "lattes-status") {
    window.postMessage({ type: "lattesfacil-status", online: !!msg.online, name: msg.name || "" }, location.origin);
  }
});

// Anuncia presença assim que o script carrega.
window.postMessage({ type: "lattesdata-ext-pong", version: chrome.runtime.getManifest().version }, location.origin);
