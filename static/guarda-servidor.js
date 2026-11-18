"use strict";
// Avisa quando o servidor está rodando com código antigo (arquivos do projeto mudaram depois que ele iniciou).
// Sem isso, a tela nova conversa com o servidor velho e parece que a mudança "não pegou".
(function () {
  let aviso = null;
  async function checar() {
    try {
      const r = await fetch("/api/servidor/estado", { cache: "no-store" });
      if (!r.ok) return;
      const d = await r.json();
      if (d.desatualizado && !aviso) {
        aviso = document.createElement("div");
        aviso.setAttribute("role", "alert");
        aviso.style.cssText = "position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#92400e;color:#fff;padding:10px 16px;font:14px/1.4 system-ui,sans-serif;text-align:center";
        aviso.textContent = "O servidor está rodando com código antigo: as mudanças do projeto só valem depois de reiniciá-lo. Feche o \"python server.py\", rode de novo e atualize a página (Ctrl+F5).";
        document.body.appendChild(aviso);
      } else if (!d.desatualizado && aviso) {
        aviso.remove();
        aviso = null;
      }
    } catch (e) { /* sem rede ou sem sessão: tenta de novo no próximo ciclo */ }
  }
  setTimeout(checar, 2000);
  setInterval(checar, 60000);
  window.addEventListener("focus", checar);
})();
