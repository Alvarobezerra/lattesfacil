// Guia de instalação: detecta a extensão (ping/pong com o content script) e copia o endereço de extensões.
(function () {
  const estado = document.getElementById("estado"), txt = document.getElementById("estadoTxt");
  const edge = /Edg\//.test(navigator.userAgent);
  const endereco = edge ? "edge://extensions" : "chrome://extensions";
  document.getElementById("enderecoExt").textContent = endereco;
  document.querySelectorAll(".tela .url").forEach((u) => { if (u.textContent.trim().endsWith("://extensions")) u.textContent = endereco; });

  let achou = false;
  window.addEventListener("message", (ev) => {
    if (ev.source !== window || ev.origin !== location.origin || !ev.data || ev.data.type !== "lattesdata-ext-pong") return;
    achou = true;
    estado.className = "estado ok";
    txt.textContent = "Extensão instalada e ativa neste computador" + (ev.data.version ? " (versão " + ev.data.version + ")" : "") + ". Não precisa fazer mais nada.";
  });
  window.postMessage({ type: "lattesdata-ext-ping" }, location.origin);
  setTimeout(() => {
    if (achou) return;
    estado.className = "estado no";
    txt.textContent = "Extensão ainda não detectada neste computador. Siga os passos abaixo e, no fim, aperte F5.";
  }, 1800);

  document.getElementById("btnCopia").addEventListener("click", async (e) => {
    const b = e.currentTarget;
    try { await navigator.clipboard.writeText(endereco); b.textContent = "Copiado! Cole na barra do navegador"; }
    catch (err) { b.textContent = "Selecione e copie o texto ao lado"; }
    setTimeout(() => { b.textContent = "Copiar endereço"; }, 3500);
  });
})();
