"use strict";
(function () {
  const DRAFT_KEY = "lf-pesquisa-rascunho-v2";
  const form = document.getElementById("pesquisaForm");
  const nomeInput = document.getElementById("respondenteNome");
  const contextoInput = document.getElementById("respondenteContexto");
  const progText = document.getElementById("progText");
  const progFill = document.getElementById("progFill");
  const draftInfo = document.getElementById("draftInfo");
  const btnLimpar = document.getElementById("btnLimparRascunho");
  const btnEnviar = document.getElementById("btnEnviar");
  const statusBox = document.getElementById("statusBox");
  const q30LimitNote = document.getElementById("q30LimitNote");
  const qCards = Array.from(document.querySelectorAll(".q[data-qid]"));
  const blockLinks = Array.from(document.querySelectorAll(".block-nav a[data-block]"));

  if (!form) return;

  // Pré-preenche respondente pela URL (?respondente=... ou ?nome=...)
  try {
    const params = new URLSearchParams(location.search);
    const preNome = (params.get("respondente") || params.get("nome") || "").trim();
    if (preNome && nomeInput && !nomeInput.value) {
      nomeInput.value = preNome.slice(0, 120);
    }
  } catch (e) {}

  function statusMsg(texto, erro) {
    if (!statusBox) return;
    statusBox.textContent = texto;
    statusBox.className = "status-box " + (erro ? "err" : "ok");
  }

  function atualizarProgresso() {
    let respondidas = 0;
    const porBloco = {};

    qCards.forEach((card) => {
      const bloco = card.dataset.block || "";
      if (!porBloco[bloco]) porBloco[bloco] = { total: 0, feitas: 0 };
      porBloco[bloco].total += 1;

      const temMarcado = card.querySelectorAll("input:checked").length > 0;
      const temTexto = Array.from(card.querySelectorAll("textarea, input[type=text], select"))
        .some((el) => el.value.trim().length > 0);
      if (temMarcado || temTexto) {
        respondidas += 1;
        porBloco[bloco].feitas += 1;
      }
    });

    const total = qCards.length || 32;
    const pct = Math.round((respondidas * 100) / total);
    if (progText) progText.textContent = `${respondidas} de ${total} questões respondidas`;
    if (progFill) progFill.style.width = `${pct}%`;

    blockLinks.forEach((a) => {
      const b = a.dataset.block;
      if (b === "id") {
        const temId = (nomeInput && nomeInput.value.trim()) || (contextoInput && contextoInput.value.trim());
        a.classList.toggle("done", Boolean(temId));
        return;
      }
      const st = porBloco[b];
      a.classList.toggle("done", Boolean(st && st.feitas === st.total));
    });
  }

  function salvarRascunho() {
    try {
      const estado = {
        nome: nomeInput ? nomeInput.value : "",
        contexto: contextoInput ? contextoInput.value : "",
        checks: Array.from(form.querySelectorAll("input[type=checkbox], input[type=radio]"))
          .map((el) => ({ name: el.name, value: el.value, checked: el.checked })),
        textos: Array.from(form.querySelectorAll("textarea"))
          .map((el) => ({ name: el.name, value: el.value })),
      };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(estado));
      if (draftInfo) draftInfo.textContent = "Rascunho salvo neste navegador";
    } catch (e) {}
  }

  function restaurarRascunho() {
    try {
      const bruto = localStorage.getItem(DRAFT_KEY);
      if (!bruto) return;
      const estado = JSON.parse(bruto);
      if (estado.nome && nomeInput && !nomeInput.value) nomeInput.value = estado.nome;
      if (estado.contexto && contextoInput) contextoInput.value = estado.contexto;
      if (Array.isArray(estado.checks)) {
        estado.checks.forEach((c) => {
          const alvos = form.querySelectorAll(`input[name="${CSS.escape(c.name)}"]`);
          alvos.forEach((el) => {
            if (el.value === c.value) el.checked = Boolean(c.checked);
          });
        });
      }
      if (Array.isArray(estado.textos)) {
        estado.textos.forEach((t) => {
          const el = form.querySelector(`textarea[name="${CSS.escape(t.name)}"]`);
          if (el && typeof t.value === "string") el.value = t.value;
        });
      }
      if (draftInfo) draftInfo.textContent = "Rascunho restaurado";
    } catch (e) {}
  }

  // Limite gentil de até 3 opções na Q30
  const q30Checks = Array.from(form.querySelectorAll('input[name="q30"]'));
  q30Checks.forEach((chk) => {
    chk.addEventListener("change", () => {
      const marcados = q30Checks.filter((c) => c.checked);
      if (marcados.length > 3) {
        chk.checked = false;
        if (q30LimitNote) q30LimitNote.classList.add("show");
      } else if (q30LimitNote) {
        q30LimitNote.classList.toggle("show", marcados.length === 3);
      }
    });
  });

  form.addEventListener("input", () => {
    atualizarProgresso();
    salvarRascunho();
  });
  form.addEventListener("change", () => {
    atualizarProgresso();
    salvarRascunho();
  });

  if (btnLimpar) {
    btnLimpar.addEventListener("click", () => {
      try { localStorage.removeItem(DRAFT_KEY); } catch (e) {}
      form.reset();
      if (q30LimitNote) q30LimitNote.classList.remove("show");
      if (draftInfo) draftInfo.textContent = "Rascunho limpo";
      atualizarProgresso();
    });
  }

  function coletarRespostas() {
    const lista = [];
    const ctx = contextoInput ? contextoInput.value.trim() : "";
    if (ctx) {
      lista.push({
        pergunta: "Instituição, programa ou área de atuação",
        resposta: ctx,
      });
    }
    qCards.forEach((card, index) => {
      const titulo = (card.querySelector(".title")?.textContent || `Pergunta ${index + 1}`)
        .replace(/^Q\d+\s*/, "")
        .replace(/\s+/g, " ")
        .trim();
      const selecionados = Array.from(card.querySelectorAll("input:checked"))
        .map((inp) => inp.value || inp.closest("label")?.textContent.replace(/\s+/g, " ").trim() || "selecionado");
      const textos = Array.from(card.querySelectorAll("textarea, input[type=text], select"))
        .map((el) => el.value.trim())
        .filter(Boolean);
      const combinado = [...selecionados, ...textos].join("; ");
      if (combinado) {
        lista.push({ pergunta: titulo, resposta: combinado });
      }
    });
    return lista;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (statusBox) statusBox.className = "status-box";
    const respostas = coletarRespostas();
    if (respostas.length < 3) {
      statusMsg("Responda pelo menos três questões antes de enviar sua escuta.", true);
      return;
    }

    const respondente = (nomeInput && nomeInput.value.trim()) || "Pesquisador convidado";
    if (btnEnviar) {
      btnEnviar.disabled = true;
      btnEnviar.textContent = "Enviando respostas…";
    }

    try {
      const resp = await fetch("/api/pesquisa/pesquisador", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ respondente, respostas }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Não foi possível registrar suas respostas.");

      try { localStorage.removeItem(DRAFT_KEY); } catch (e) {}
      if (draftInfo) draftInfo.textContent = "Escuta enviada ✓";
      statusMsg(`Muito obrigado, ${respondente}! Recebemos ${respostas.length} resposta(s) para guiar a evolução do LattesData.`, false);
      form.querySelectorAll("input, textarea, select, button").forEach((el) => { el.disabled = true; });
    } catch (err) {
      statusMsg(err.message || "Falha ao enviar respostas.", true);
      if (btnEnviar) {
        btnEnviar.disabled = false;
        btnEnviar.textContent = "Enviar escuta completa";
      }
    }
  });

  restaurarRascunho();
  atualizarProgresso();

  // Formulário separado: Bloco 9 (Gestão Colaborativa de Projetos)
  const projForm = document.getElementById("projetosForm");
  if (projForm) {
    const PROJ_DRAFT_KEY = "lf-pesquisa-projetos-b9-v1";
    const projBtn = document.getElementById("btnEnviarProjetos");
    const projStatus = document.getElementById("projetosStatusBox");
    const projCards = Array.from(projForm.querySelectorAll(".q[data-proj-q]"));

    function projMsg(texto, erro) {
      if (!projStatus) return;
      projStatus.textContent = texto;
      projStatus.className = "status-box " + (erro ? "err" : "ok");
    }

    function salvarProjDraft() {
      try {
        const estado = {
          checks: Array.from(projForm.querySelectorAll("input[type=checkbox], input[type=radio]"))
            .map((el) => ({ name: el.name, value: el.value, checked: el.checked })),
          textos: Array.from(projForm.querySelectorAll("textarea"))
            .map((el) => ({ name: el.name, value: el.value })),
        };
        localStorage.setItem(PROJ_DRAFT_KEY, JSON.stringify(estado));
      } catch (e) {}
    }

    function restaurarProjDraft() {
      try {
        const bruto = localStorage.getItem(PROJ_DRAFT_KEY);
        if (!bruto) return;
        const estado = JSON.parse(bruto);
        if (Array.isArray(estado.checks)) {
          estado.checks.forEach((c) => {
            projForm.querySelectorAll(`input[name="${CSS.escape(c.name)}"]`).forEach((el) => {
              if (el.value === c.value) el.checked = Boolean(c.checked);
            });
          });
        }
        if (Array.isArray(estado.textos)) {
          estado.textos.forEach((t) => {
            const el = projForm.querySelector(`textarea[name="${CSS.escape(t.name)}"]`);
            if (el && typeof t.value === "string") el.value = t.value;
          });
        }
      } catch (e) {}
    }

    projForm.addEventListener("input", salvarProjDraft);
    projForm.addEventListener("change", salvarProjDraft);

    projForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (projStatus) projStatus.className = "status-box";
      const respostas = [];
      projCards.forEach((card, index) => {
        const titulo = (card.querySelector(".title")?.textContent || `Bloco 9 · Questão ${index + 1}`)
          .replace(/^\d+\s*/, "")
          .replace(/\s+/g, " ")
          .trim();
        const selecionados = Array.from(card.querySelectorAll("input:checked"))
          .map((inp) => inp.value || inp.closest("label")?.textContent.replace(/\s+/g, " ").trim() || "selecionado");
        const textos = Array.from(card.querySelectorAll("textarea, input[type=text]"))
          .map((el) => el.value.trim())
          .filter(Boolean);
        const combinado = [...selecionados, ...textos].join("; ");
        if (combinado) {
          respostas.push({ pergunta: `[Bloco 9 · Projetos] ${titulo}`, resposta: combinado });
        }
      });

      if (respostas.length === 0) {
        projMsg("Responda pelo menos uma questão do Bloco 9 antes de enviar.", true);
        return;
      }

      const baseNome = (nomeInput && nomeInput.value.trim()) || "Pesquisador convidado";
      const respondente = `${baseNome} · Bloco 9 (Projetos)`;
      if (projBtn) {
        projBtn.disabled = true;
        projBtn.textContent = "Enviando Bloco 9…";
      }

      try {
        const resp = await fetch("/api/pesquisa/pesquisador", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ respondente, respostas }),
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || "Não foi possível registrar suas respostas do Bloco 9.");
        try { localStorage.removeItem(PROJ_DRAFT_KEY); } catch (e) {}
        projMsg(`Obrigado, ${baseNome}! Recebemos ${respostas.length} resposta(s) do formulário separado de Gestão de Projetos.`, false);
        projForm.querySelectorAll("input, textarea, button").forEach((el) => { el.disabled = true; });
      } catch (err) {
        projMsg(err.message || "Falha ao enviar respostas do Bloco 9.", true);
        if (projBtn) {
          projBtn.disabled = false;
          projBtn.textContent = "Enviar formulário de Projetos (Bloco 9)";
        }
      }
    });

    restaurarProjDraft();
  }
})();
