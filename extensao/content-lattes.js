// Roda automaticamente nas páginas do Currículo Lattes (https://wwws.cnpq.br/*).
// 1) Informa ao LattesData se o currículo está aberto e de quem é (sem precisar de F12/conector manual).
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
    bar.textContent = `🚀 LattesData: Faça seu login no Lattes. Assim que entrar, o cadastro${nomeObra} será aberto e preenchido automaticamente!`;
    document.body.appendChild(bar);
  }

  function checarEstado() {
    const nome = obterNomeTitular();
    const logado = temPainelLattes();
    chrome.runtime.sendMessage({ type: "lattes-heartbeat", online: logado, name: nome });

    chrome.storage.local.get("pendingLattesFill", (res) => {
      const item = res && res.pendingLattesFill;
      if (!item || !item.data) return;
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
