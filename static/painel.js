"use strict";
(function () {
  const $ = (id) => document.getElementById(id);
  let barema = null;

  // texto sempre via textContent: nada vindo de documentos ou do XML entra como HTML
  function el(tag, props, ...filhos) {
    const e = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => (k === "class" ? (e.className = v) : (e[k] = v)));
    filhos.flat().forEach((f) => e.append(f instanceof Node ? f : document.createTextNode(f == null ? "" : String(f))));
    return e;
  }
  function tabela(cab, linhas) {
    const t = el("table", { class: "tab" }, el("thead", {}, el("tr", {}, cab.map((c) => el("th", {}, c)))));
    t.append(el("tbody", {}, linhas.map((l) => el("tr", {}, l.map((c) => el("td", {}, c))))));
    return t;
  }
  function msg(id, texto, erro) { const s = $(id); s.textContent = texto; s.className = erro ? "erro" : "ok"; }
  async function json(url, opts) {
    const r = await fetch(url, opts);
    let d = {};
    try { d = await r.json(); } catch (e) { /* corpo não-JSON */ }
    if (!r.ok) { const e = new Error(d.error || "Falha (" + r.status + ")"); e.dados = d; throw e; }
    return d;
  }
  function form(campos, arquivos) {
    const f = new FormData();
    Object.entries(campos || {}).forEach(([k, v]) => f.append(k, v));
    (arquivos || []).forEach((a) => f.append("arquivo", a));
    return f;
  }
  function baixar(blob, nome) {
    const a = el("a", { href: URL.createObjectURL(blob), download: nome });
    document.body.append(a); a.click(); a.remove();
  }
  async function baixarDe(url, f, nome) {
    const r = await fetch(url, { method: "POST", body: f });
    if (!r.ok) { let d = {}; try { d = await r.json(); } catch (e) { /* vazio */ } throw new Error(d.error || "Falha (" + r.status + ")"); }
    baixar(await r.blob(), nome);
  }

  // 1. XML
  $("bXml").onclick = async () => {
    const arq = $("fXml").files[0];
    if (!arq) return msg("sXml", "Escolha o arquivo XML ou ZIP.", true);
    try {
      const d = await json("/api/lattes-xml", { method: "POST", body: form({}, [arq]) });
      const cats = Object.entries(d.por_categoria).map(([k, v]) => k + ": " + v).join(" · ");
      msg("sXml", "Carregado: " + d.nome + " — " + d.total_itens + " itens (" + cats + ")", false);
    } catch (e) { msg("sXml", e.message, true); }
  };

  // 2. lote
  const pegaLote = () => Array.from($("fLote").files);
  $("bLote").onclick = async () => {
    const arqs = pegaLote();
    if (!arqs.length) return msg("sLote", "Escolha PDFs ou um ZIP.", true);
    msg("sLote", "Analisando " + arqs.length + " arquivo(s)…", false);
    try {
      const d = await json("/api/lote", { method: "POST", body: form({ usuario: $("usuLote").value }, arqs) });
      const resumo = Object.entries(d.por_status).map(([k, v]) => k + ": " + v).join(" · ");
      msg("sLote", d.total + " documento(s) — " + resumo, false);
      const linhas = d.arquivos.map((a) => [a.arquivo, a.item_nome || a.mensagem || "—", a.confianca != null ? Math.round(a.confianca * 100) + "%" : "",
        a.caminho_sugerido || "", (a.possivel_duplicata || []).map((x) => "Já consta: " + x.titulo + " (" + x.motivo + ")").join("; "), (a.faltam_obrigatorios || []).join(", ")]);
      const alvo = $("rLote"); alvo.replaceChildren(tabela(["Arquivo", "Item do Lattes", "Confiança", "Pasta/nome sugerido", "Duplicata?", "Falta preencher"], linhas));
      if (d.ignorados.length) alvo.append(el("p", { class: "dica" }, "Ignorados: " + d.ignorados.map((i) => i.arquivo + " (" + i.motivo + ")").join("; ")));
    } catch (e) { msg("sLote", e.message, true); }
  };
  $("bLoteZip").onclick = async () => {
    const arqs = pegaLote();
    if (!arqs.length) return msg("sLote", "Escolha PDFs ou um ZIP.", true);
    try { await baixarDe("/api/lote", form({ usuario: $("usuLote").value, saida: "zip" }, arqs), "comprovantes-organizados.zip"); msg("sLote", "ZIP gerado.", false); }
    catch (e) { msg("sLote", e.message, true); }
  };

  // 3. auditoria
  $("bAud").onclick = async () => {
    try {
      const d = await json("/api/auditoria");
      msg("sAud", d.total + " pendência(s): " + Object.entries(d.resumo).map(([k, v]) => k + " " + v).join(" · "), d.total > 0 && d.resumo["Gravíssimo"] > 0);
      const linhas = d.pendencias.map((p) => [el("span", { class: "tag r-" + p.risco }, p.risco), p.mensagem + (p.item ? " — " + (p.item.titulo || p.item.categoria) + (p.item.ano ? " (" + p.item.ano + ")" : "") : ""), p.como_corrigir]);
      $("rAud").replaceChildren(linhas.length ? tabela(["Risco", "Pendência", "Como corrigir"], linhas) : el("p", { class: "ok" }, "Nenhuma pendência encontrada."), el("p", { class: "dica" }, d.aviso));
    } catch (e) { msg("sAud", e.message, true); }
  };

  // 4. EditalScore
  const ano = () => ($("aEdital").value ? Number($("aEdital").value) : undefined);
  $("bBarema").onclick = async () => {
    try {
      barema = await json("/api/edital/barema", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ texto: $("tBarema").value, nome: $("nEdital").value || "Edital" }) });
      const linhas = barema.blocos.flatMap((b) => b.itens.map((i) => [b.nome + (b.teto ? " (máx. " + b.teto + ")" : ""), i.descricao, i.categorias.join(", ") || "— sem categoria —", i.pontos_unitarios, i.teto == null ? "" : i.teto, i.janela_anos ? i.janela_anos + " anos" : "", i.qualis]));
      $("rBarema").replaceChildren(
        el("p", { class: "dica" }, "Teto global: " + (barema.teto_global == null ? "não encontrado" : barema.teto_global) + ". Confira antes de calcular."),
        tabela(["Bloco", "Item", "Categorias do Lattes", "Pontos", "Teto do item", "Janela", "Qualis"], linhas),
        ...barema.avisos.map((a) => el("p", { class: "erro" }, a)));
    } catch (e) { $("rBarema").replaceChildren(el("p", { class: "erro" }, e.message)); }
  };
  $("bCalc").onclick = async () => {
    if (!barema) return $("rCalc").replaceChildren(el("p", { class: "erro" }, "Leia o barema primeiro."));
    try {
      const d = await json("/api/edital/calcular", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ barema, ano: ano() }) });
      const linhas = d.blocos.flatMap((b) => b.itens.map((i) => [i.descricao, i.quantidade, i.pontos, i.teto == null ? "" : i.teto, i.status.replaceAll("_", " ")]));
      $("rCalc").replaceChildren(
        el("div", { class: "grande" }, d.total + (d.teto_global ? " / " + d.teto_global : "") + " pontos"),
        tabela(["Item", "Qtd. no currículo", "Pontos", "Teto", "Situação"], linhas),
        ...(d.lacunas.length ? [el("h3", {}, "Onde focar"), tabela(["Item", "Situação", "Dica"], d.lacunas.map((l) => [l.item, l.situacao, l.dica]))] : []),
        el("p", { class: "dica" }, d.aviso));
    } catch (e) { $("rCalc").replaceChildren(el("p", { class: "erro" }, e.message)); }
  };
  $("bSim").onclick = async () => {
    if (!barema) return msg("rSim", "Leia o barema primeiro.", true);
    const extras = Array.from({ length: Math.min(Number($("qSim").value) || 1, 20) }, () => ({ categoria: $("cSim").value }));
    try {
      const d = await json("/api/edital/simular", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ barema, ano: ano(), extras }) });
      msg("rSim", d.antes + " → " + d.depois + " pontos (" + (d.diferenca >= 0 ? "+" : "") + d.diferenca + ")", false);
    } catch (e) { msg("rSim", e.message, true); }
  };

  // dossiê: o usuário liga cada PDF a um item do edital
  $("bDossieLista").onclick = () => {
    const arqs = Array.from($("fDossie").files);
    if (!arqs.length) return;
    const itensBarema = barema ? barema.blocos.flatMap((b) => b.itens.map((i) => i)) : [];
    const linhas = arqs.map((a, n) => {
      const sel = el("select", { id: "ds" + n });
      sel.append(el("option", { value: "" }, "— não incluir —"));
      itensBarema.forEach((i) => sel.append(el("option", { value: i.id }, i.id + " " + i.descricao.slice(0, 60))));
      return [a.name, sel];
    });
    const btn = el("button", { class: "btn btn-primary", type: "button" }, "Gerar dossiê PDF");
    btn.onclick = async () => {
      const mapa = {}; const escolhidos = [];
      arqs.forEach((a, n) => { const v = $("ds" + n).value; if (v) { mapa[a.name] = { item: v, descricao: itensBarema.find((i) => i.id === v).descricao }; escolhidos.push(a); } });
      if (!escolhidos.length) return;
      try { await baixarDe("/api/edital/dossie", form({ candidato: $("nCand").value, edital: $("nEdital").value, itens: JSON.stringify(mapa) }, escolhidos), "dossie-comprobatorio.pdf"); }
      catch (e) { $("rDossie").append(el("p", { class: "erro" }, e.message)); }
    };
    $("rDossie").replaceChildren(itensBarema.length ? tabela(["Arquivo", "Item do edital"], linhas) : el("p", { class: "erro" }, "Leia o barema antes de ligar os arquivos aos itens."), btn);
  };
})();
