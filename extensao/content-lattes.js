// Roda automaticamente nas páginas do Currículo Lattes (https://wwws.cnpq.br/*).
// 1) Informa ao NautiScience se o currículo está aberto e de quem é (sem precisar de F12/conector manual).
// 2) Se houver um envio na fila aguardando o login do usuário, retoma o cadastro assim que o login concluir.
(function () {
  if (window !== window.top) return;

  function obterNomeTitular() {
    try {
      const el = document.getElementById("nmeLt") || document.querySelector(".dadosPrinc .nome");
      return el ? el.textContent.trim() : "";
    } catch (e) {
      return "";
    }
  }

  function temPainelLattes() {
    try {
      if (obterNomeTitular()) return true;
      const html = document.documentElement ? document.documentElement.innerHTML : "";
      return /[?&]f_cod=[A-Za-z0-9]{6,20}/i.test(html) && /modalCV2/i.test(html);
    } catch (e) {
      return false;
    }
  }

  function mostrarAvisoFilaLogin(titulo) {
    if (document.getElementById("lattesdata-login-banner")) return;
    const bar = document.createElement("div");
    bar.id = "lattesdata-login-banner";
    bar.style.cssText = [
      "position:fixed",
      "top:0",
      "left:0",
      "right:0",
      "z-index:2147483647",
      "background:linear-gradient(90deg,#0b192c,#0369a1)",
      "color:#fff",
      "padding:12px 20px",
      "font:600 14px/1.4 system-ui,-apple-system,sans-serif",
      "text-align:center",
      "box-shadow:0 4px 16px rgba(0,0,0,0.3)",
      "border-bottom:2px solid #38bdf8"
    ].join(";");
    const nomeObra = titulo ? ` ("${String(titulo).slice(0, 70)}")` : "";
    bar.textContent = `🚀 NautiScience: Faça seu login no Lattes. Assim que entrar, o cadastro${nomeObra} será aberto e preenchido automaticamente!`;
    document.body.appendChild(bar);
  }

  // Mostra de novo o último resultado do preenchimento quando a página foi recarregada (o painel antigo some junto).
  function mostrarUltimoResultado() {
    chrome.storage.local.get("ultimoResultadoLattes", (res) => {
      const r = res && res.ultimoResultadoLattes;
      if (!r || r.exibido || Date.now() - (r.ts || 0) > 120000) return;
      if (document.getElementById("lattesdata-painel")) return;
      chrome.storage.local.set({ ultimoResultadoLattes: { ...r, exibido: true } });
      const p = document.createElement("div");
      p.id = "lattesdata-painel";
      p.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;max-width:400px;font:14px/1.45 system-ui,sans-serif;" +
        "color:#0f172a;background:#fff;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.3);padding:12px 14px;border-left:6px solid " +
        ({ ok: "#059669", removido: "#059669", atencao: "#d97706", ausente: "#d97706", login: "#d97706", erro: "#dc2626", divergente: "#dc2626" }[r.estado] || "#0369a1");
      const h = document.createElement("strong");
      h.textContent = "NautiScience — " + String(r.titulo || "");
      p.appendChild(h);
      if (Array.isArray(r.detalhes) && r.detalhes.length) {
        const ul = document.createElement("ul");
        ul.style.cssText = "margin:6px 0 0;padding-left:18px";
        r.detalhes.slice(0, 8).forEach((x) => { const li = document.createElement("li"); li.textContent = String(x); ul.appendChild(li); });
        p.appendChild(ul);
      }
      const x = document.createElement("button");
      x.textContent = "Fechar";
      x.style.cssText = "margin-top:8px;border:0;background:#e2e8f0;border-radius:6px;padding:4px 10px;cursor:pointer";
      x.onclick = () => p.remove();
      p.appendChild(x);
      (document.body || document.documentElement).appendChild(p);
    });
  }

  function checarEstado() {
    mostrarUltimoResultado();
    const nome = obterNomeTitular();
    const logado = temPainelLattes();
    chrome.runtime.sendMessage({ type: "lattes-heartbeat", online: logado, name: nome });

    if (logado) {
      const faixa = document.getElementById("lattesdata-login-banner");
      if (faixa) faixa.remove();
    }
    chrome.storage.local.get("pendingLattesFill", (res) => {
      const item = res && res.pendingLattesFill;
      if (!item || !item.data) {
        const faixa = document.getElementById("lattesdata-login-banner");
        if (faixa) faixa.remove();
        return;
      }
      if (Date.now() - (item.ts || 0) > 15 * 60 * 1000) {
        chrome.storage.local.remove("pendingLattesFill");
        return;
      }
      if (logado) {
        chrome.runtime.sendMessage({ type: "lattes-ready-for-pending" });
      } else {
        mostrarAvisoFilaLogin(item.data.titulo);
      }
    });
  }

  checarEstado();
  setInterval(checarEstado, 4000);
})();
