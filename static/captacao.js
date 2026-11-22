"use strict";
// Gerenciador da captação de instituições: monitora o banco local e o desempenho das consultas à lupa do Lattes.
(function () {
  const $ = (id) => document.getElementById(id);
  const URL_FORM_LUPA = "PKG_BANCA_TRAB.form?f_cod=<codigo_do_cv>"; // formulário (spec de bancas) que traz a lupa de instituições
  const VERSAO_MIN_EXT = [0, 9, 5];
  const estado = { lattesOnline: false, ext: "", cfg: null, rodando: false };

  // texto sempre via textContent: nada vindo do Lattes entra como HTML
  function el(tag, props, ...filhos) {
    const e = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => (k === "class" ? (e.className = v) : (e[k] = v)));
    filhos.flat().forEach((f) => e.append(f instanceof Node ? f : document.createTextNode(f == null ? "" : String(f))));
    return e;
  }
  async function json(url, opts) {
    const r = await fetch(url, opts);
    let d = {};
    try { d = await r.json(); } catch (e) { /* corpo não-JSON */ }
    if (!r.ok) throw new Error(d.error || "Falha (" + r.status + ")");
    return d;
  }
  const post = (acao, corpo) => json("/api/instituicoes/" + acao, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo || {}) });
  function msg(id, texto, erro) { const s = $(id); s.textContent = texto; s.className = erro ? "erro" : "ok"; }
  function numero(rotulo, valor, dica) { return el("div", { class: "num" }, el("b", {}, valor), el("span", {}, rotulo + (dica ? " — " + dica : ""))); }
  function tabela(cab, linhas) {
    const t = el("table", { class: "tab" }, el("thead", {}, el("tr", {}, cab.map((c) => el("th", {}, c)))));
    t.append(el("tbody", {}, linhas.map((l) => el("tr", {}, l.map((c) => el("td", {}, c))))));
    return t;
  }
  function versaoOk(v) {
    const p = String(v || "").split(".").map((x) => parseInt(x, 10) || 0);
    for (let i = 0; i < 3; i++) { if ((p[i] || 0) > VERSAO_MIN_EXT[i]) return true; if ((p[i] || 0) < VERSAO_MIN_EXT[i]) return false; }
    return true;
  }

  function atualizarConexao() {
    $("connLattes").classList.toggle("on", estado.lattesOnline);
    $("connTxt").textContent = estado.lattesOnline ? "Lattes: conectado" : "Lattes: sem sinal";
    const extOk = !!estado.ext && versaoOk(estado.ext);
    $("connExt").classList.toggle("on", extOk);
    $("extTxt").textContent = !estado.ext ? "Extensão: não detectada" : extOk ? "Extensão " + estado.ext : "Extensão " + estado.ext + " — atualize para 0.9.5 ou mais";
    const falta = [];
    if (!extOk) falta.push("instalar/atualizar a extensão NautiScience");
    if (!estado.lattesOnline) falta.push("abrir o Lattes e entrar no currículo (o selo \"Lattes\" da tela principal deve ficar conectado)");
    $("avisoConexao").textContent = falta.length ? "Para consultar a lupa é preciso " + falta.join(" e ") + ". Sem isso a captação fica parada e o preenchimento usa só o banco local." : "";
    $("bExecutar").disabled = estado.rodando || !extOk || !estado.lattesOnline || !(estado.cfg && estado.cfg.ativa);
  }

  function desenhar(d) {
    estado.cfg = d.config;
    $("cAtiva").checked = !!d.config.ativa;
    $("cDia").value = d.config.limite_dia; $("cLote").value = d.config.limite_lote; $("cInt").value = Math.round(d.config.intervalo_ms / 1000);
    const b = d.banco;
    $("gBanco").replaceChildren(
      numero("instituições no banco", b.total), numero("com código do Lattes", b.com_codigo, b.total ? Math.round((100 * b.com_codigo) / b.total) + "%" : ""),
      numero("confirmadas por usuários", b.por_origem.confirmada || 0), numero("coletadas na lupa", b.por_origem.coletada || 0),
      numero("da semente", b.por_origem.semente || 0), numero("textos confirmados", b.aliases));
    $("gHoje").replaceChildren(numero("coleta hoje", d.hoje.coleta + " / " + d.config.limite_dia), numero("restante hoje", d.hoje.restante), numero("consultas de uso hoje", d.hoje.uso));
    $("tPref").replaceChildren(tabela(["Prefixo", "Situação", "Resultados", "Novas", "Aprofundamentos", "Última"], d.prefixos.map((p) => [
      p.termo, el("span", { class: "tag t-" + p.estado }, p.estado), p.tentativas ? p.resultados : "—", p.tentativas ? p.novas : "—",
      p.aprofundamentos ? p.aprofundamentos_feitos + " de " + p.aprofundamentos : "—", p.ultimo_em ? p.ultimo_em.replace("T", " ").slice(0, 16) : "—"])));
    const dp = d.desempenho;
    $("gDesemp").replaceChildren(numero("consultas no total", dp.consultas_total), numero("tempo médio", dp.ms_medio ? (dp.ms_medio / 1000).toFixed(1) + " s" : "—", "por consulta"),
      numero("resultados por consulta", dp.resultados_medio || "—"), numero("taxa de novidade", dp.taxa_novidade ? Math.round(dp.taxa_novidade * 100) + "%" : "—", "últimas 50"),
      numero("limite da lupa", dp.cap_detectado || "não detectado", dp.cap_detectado ? "resultados por busca" : "precisa de mais consultas"),
      numero("fila", (d.fila.pendente || 0) + " pendentes", (d.fila.saturado || 0) + " saturados, " + (d.fila.feito || 0) + " feitos"));
    const max = Math.max(1, ...d.por_dia.map((x) => x.coleta + x.uso));
    $("bDias").replaceChildren(...d.por_dia.map((x) => {
      const w = el("div", { title: x.dia + ": " + x.coleta + " coleta, " + x.uso + " uso, " + x.novas + " novas" });
      w.style.height = Math.round((100 * (x.coleta + x.uso)) / max) + "%";
      if (!x.coleta) w.className = "uso";
      return w;
    }));
    $("eDias").replaceChildren(...d.por_dia.map((x) => el("span", {}, x.dia.slice(8))));
    $("tErros").replaceChildren(dp.erros_recentes.length ? tabela(["Quando", "Termo", "Erro"], dp.erros_recentes.map((x) => [x.quando.replace("T", " ").slice(0, 16), x.termo, x.erro])) : el("p", { class: "dica" }, "Nenhum erro recente."));
    $("amostras").replaceChildren(...(d.amostras_ref.length ? d.amostras_ref.map((a) => el("div", {}, el("code", {}, a.join("  |  ")))) : [document.createTextNode("Ainda sem amostras: aparecem depois da primeira consulta à lupa. Elas mostram o formato real do link, que define como o código da instituição é lido.")]));
    atualizarConexao();
  }

  async function carregar() {
    try { desenhar(await json("/api/instituicoes/gerenciador")); } catch (e) { msg("sCtl", e.message, true); }
  }

  $("bSalvar").onclick = async () => {
    try {
      const r = await post("config", { ativa: $("cAtiva").checked ? 1 : 0, limite_dia: $("cDia").value, limite_lote: $("cLote").value, intervalo_ms: Number($("cInt").value) * 1000 });
      msg("sCtl", "Configuração salva (com os tetos: " + r.config.limite_dia + "/dia, " + r.config.limite_lote + "/lote, " + r.config.intervalo_ms / 1000 + " s).");
      carregar();
    } catch (e) { msg("sCtl", e.message, true); }
  };
  $("bExecutar").onclick = async () => {
    try {
      const l = await json("/api/instituicoes/proximo-lote");
      if (!l.termos.length) { msg("sCtl", "Nada a coletar agora: " + (l.motivo || "fila vazia") + ".", true); return; }
      estado.rodando = true; atualizarConexao();
      msg("sCtl", "Coletando " + l.termos.length + " termo(s): " + l.termos.join(", ") + "… não feche a aba do Lattes.");
      window.postMessage({ type: "lattesdata-ext-inst-coleta", termos: l.termos, intervalo_ms: l.intervalo_ms, url: URL_FORM_LUPA }, location.origin);
    } catch (e) { msg("sCtl", e.message, true); }
  };
  $("bBusca").onclick = async () => {
    const q = $("qBusca").value.trim();
    if (!q) return;
    try {
      const r = await json("/api/instituicoes/buscar?q=" + encodeURIComponent(q));
      $("rBusca").replaceChildren(r.candidatas.length ? tabela(["Nome", "Sigla", "Código Lattes", "Origem", "Pontos"], r.candidatas.map((c) => [c.nome, c.sigla || "—", c.codigo || "— (confirmar na lupa)", c.origem, c.pontos])) : el("p", { class: "dica" }, "Nada no banco para esse texto."));
    } catch (e) { $("rBusca").replaceChildren(el("p", { class: "erro" }, e.message)); }
  };
  $("bCsv").onclick = async () => {
    const f = $("fCsv").files[0];
    if (!f) { msg("sCsv", "Escolha um arquivo CSV.", true); return; }
    try {
      const r = await post("importar", { csv: await f.text() });
      msg("sCsv", r.lidas + " linhas lidas, " + r.novas + " instituições novas."); carregar();
    } catch (e) { msg("sCsv", e.message, true); }
  };

  window.addEventListener("message", (e) => {
    const m = e.data;
    if (!m) return;
    if (m.type === "lattesfacil-status" && (e.origin === location.origin || /\.cnpq\.br$/.test(new URL(e.origin).hostname))) { estado.lattesOnline = !!m.online; atualizarConexao(); return; }
    if (e.source !== window || e.origin !== location.origin) return;
    if (m.type === "lattesdata-ext-pong") { estado.ext = String(m.version || ""); atualizarConexao(); }
    else if (m.type === "lattesdata-ext-inst-coleta-resp" && !m.ok) { estado.rodando = false; msg("sCtl", m.message || "A extensão não iniciou a coleta.", true); atualizarConexao(); }
  });
  window.addEventListener("lf-inst-lote", (ev) => {
    const fim = ev.detail && ev.detail.fim;
    if (fim) {
      estado.rodando = false;
      msg("sCtl", fim.ok ? "Lote concluído: " + fim.feitos + " de " + fim.total + " consultas" + (fim.erros ? " (" + fim.erros + " com erro)" : "") + ". Feche o formulário de bancas aberto no Lattes." : "A coleta parou: " + (fim.erro || "motivo não informado") + ".", !fim.ok);
    }
    carregar();
  });

  window.postMessage({ type: "lattesdata-ext-ping" }, location.origin);
  carregar();
  setInterval(carregar, 30000);
})();
