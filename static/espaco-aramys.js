// LattesData - Espaço de Co-construção Aramys

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSugestoes();
  initReferencias();
  initQuestionario();
});

/* ==========================================================================
   1. NAVEGAÇÃO POR ABAS
   ========================================================================== */
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });
}

/* ==========================================================================
   2. SUGESTÕES DE MELHORIAS & UPLOAD DE ARQUIVOS DE APOIO
   ========================================================================== */
function initSugestoes() {
  const form = document.getElementById("formSugestao");
  const alertBox = document.getElementById("sugestaoAlert");
  const submitBtn = document.getElementById("btnEnviarSugestao");
  const fileInput = document.getElementById("sugestaoArquivo");
  const filePill = document.getElementById("sugestaoFilePill");
  const fileNameSpan = document.getElementById("sugestaoFileName");
  const removeFileBtn = document.getElementById("removeSugestaoFile");
  const feed = document.getElementById("sugestoesFeed");
  const countBadge = document.getElementById("badgeSugestoesCount");

  // Drag and drop / file change
  if (fileInput) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        fileNameSpan.textContent = `${file.name} (${formatBytes(file.size)})`;
        filePill.classList.add("show");
      } else {
        filePill.classList.remove("show");
      }
    });
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.value = "";
      filePill.classList.remove("show");
    });
  }

  // Carregar lista de sugestões existentes
  async function carregarSugestoes() {
    try {
      const res = await fetch("/api/aramys/sugestoes");
      if (!res.ok) return;
      const data = await res.json();
      renderSugestoes(data.sugestoes || []);
    } catch (err) {
      console.warn("Erro ao buscar sugestões:", err);
    }
  }

  function renderSugestoes(itens) {
    if (countBadge) {
      countBadge.textContent = itens.length;
    }
    if (!itens || itens.length === 0) {
      feed.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">💡</div>
          <p>Nenhuma sugestão registrada ainda.<br>Envie a primeira sugestão pelo formulário ao lado!</p>
        </div>
      `;
      return;
    }

    feed.innerHTML = itens
      .map((item) => {
        const dataFmt = item.criado_em ? formatDataHora(item.criado_em) : "";
        const prioridadeClass = getPrioridadeClass(item.prioridade);
        const fileLink = item.tem_arquivo
          ? `<a class="feed-file-link" href="/api/pesquisa/colaborador/arquivo?id=${item.id}" target="_blank">
               📎 ${escapeHtml(item.arquivo_nome || "Arquivo anexo")}
             </a>`
          : `<span style="color:#94a3b8;font-size:11.5px">Sem anexo</span>`;

        return `
          <div class="feed-item">
            <div class="feed-head">
              <span class="badge ${prioridadeClass}">${escapeHtml(item.prioridade || "Normal")}</span>
              <span class="badge badge-teal">${escapeHtml(item.tipo || "Geral")}</span>
              <span class="feed-date">${dataFmt}</span>
            </div>
            ${item.titulo ? `<div class="feed-title">${escapeHtml(item.titulo)}</div>` : ""}
            <div class="feed-body">${escapeHtml(item.texto || "")}</div>
            <div class="feed-footer">
              ${fileLink}
              <span style="font-size:11px;color:#10b981;font-weight:700">✓ Registrado no roadmap</span>
            </div>
          </div>
        `;
      })
      .join("");
  }

  // Envio de formulário
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.className = "alert-box";
      alertBox.textContent = "";

      const formData = new FormData(form);
      submitBtn.disabled = true;
      submitBtn.textContent = "Gravando contribuição…";

      try {
        const res = await fetch("/api/aramys/sugestao", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Erro ao salvar sugestão.");

        alertBox.className = "alert-box alert-success show";
        alertBox.innerHTML = "✓ <strong>Sugestão enviada com sucesso!</strong> A equipe já recebeu seus apontamentos e arquivo.";
        form.reset();
        filePill.classList.remove("show");
        carregarSugestoes();
      } catch (err) {
        alertBox.className = "alert-box alert-error show";
        alertBox.textContent = err.message || "Falha na comunicação com o servidor.";
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Encaminhar Sugestão de Melhoria";
      }
    });
  }

  carregarSugestoes();
}

/* ==========================================================================
   3. BASE DE REFERÊNCIA DE CURRÍCULOS LATTES
   ========================================================================== */
function initReferencias() {
  const dropzone = document.getElementById("refDropzone");
  const fileInput = document.getElementById("refFileInput");
  const alertBox = document.getElementById("refAlert");
  const tableBody = document.getElementById("refTableBody");
  const countBadge = document.getElementById("badgeRefTotal");
  const countHeader = document.getElementById("refCountHeader");
  const btnUpload = document.getElementById("btnRefUpload");
  const uploadProg = document.getElementById("refUploadProgress");

  async function carregarReferencias() {
    try {
      const res = await fetch("/api/referencias");
      if (res.ok) {
        const data = await res.json();
        renderTabela(data.arquivos || []);
      }
      carregarCiclo();
    } catch (err) {
      console.warn("Erro ao buscar currículos de referência:", err);
    }
  }

  async function carregarCiclo() {
    try {
      const res = await fetch("/api/referencias/ciclo");
      if (!res.ok) return;
      const data = await res.json();
      renderCiclo(data);
    } catch (err) {
      console.warn("Erro ao carregar dados do ciclo:", err);
    }
  }

  function renderCiclo(ciclo) {
    const textoProg = document.getElementById("cicloProgressoTexto");
    const bar = document.getElementById("cicloProgressBar");
    const grid = document.getElementById("cicloGridItens");

    if (textoProg) {
      textoProg.textContent = `Progresso: ${ciclo.concluidos} de ${ciclo.total_alvos} (${ciclo.percentual}%)`;
    }
    if (bar) {
      bar.style.width = `${ciclo.percentual}%`;
    }
    if (grid && ciclo.itens) {
      grid.innerHTML = ciclo.itens
        .map((it) => {
          const statusBadge = it.presente
            ? `<span class="badge badge-mint">✓ ${it.paginas ? it.paginas + " pág." : "Na base"}</span>`
            : (it.link_lattes
                ? `<a href="${it.link_lattes}" target="_blank" class="badge badge-blue" style="text-decoration:none">Abrir Lattes ↗</a>`
                : `<span class="badge" style="background:#f1f5f9;color:#64748b">Pendente</span>`);

          return `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#fff;border:1px solid #e2e8f0;border-radius:8px">
              <span>${it.num}. <strong>${escapeHtml(it.nome)}</strong></span>
              ${statusBadge}
            </div>
          `;
        })
        .join("");
    }
  }

  function renderTabela(arquivos) {
    if (countBadge) countBadge.textContent = arquivos.length;
    if (countHeader) countHeader.textContent = `${arquivos.length} currículos cadastrados`;

    if (!arquivos || arquivos.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" class="empty-state">
            <div class="empty-state-icon">📚</div>
            <p>Nenhum currículo de referência encontrado na base.<br>Faça o upload do primeiro arquivo acima.</p>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = arquivos
      .map((item) => {
        const isXml = item.extensao === ".xml";
        const icon = isXml ? '<span class="ref-icon xml">&lt;/&gt;</span>' : '<span class="ref-icon">PDF</span>';
        const dataFmt = item.modificado_em ? formatDataHora(item.modificado_em) : "-";

        return `
          <tr>
            <td>
              <div class="ref-file-name">
                ${icon}
                <span>${escapeHtml(item.nome)}</span>
              </div>
            </td>
            <td><span class="badge badge-teal">${item.tamanho_formatado}</span></td>
            <td><span style="color:#64748b;font-size:12px">${dataFmt}</span></td>
            <td style="text-align:right">
              <a class="btn btn-secondary btn-sm" href="/api/referencias/download/${encodeURIComponent(item.nome)}" target="_blank" download>
                Baixar / Abrir ↗
              </a>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Upload de arquivos
  async function enviarArquivos(files) {
    if (!files || files.length === 0) return;
    alertBox.className = "alert-box";
    alertBox.textContent = "";

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("arquivo", files[i]);
    }

    if (btnUpload) {
      btnUpload.disabled = true;
      btnUpload.textContent = `Enviando ${files.length} arquivo(s)…`;
    }
    if (uploadProg) uploadProg.textContent = "Processando upload e registrando na base de referência…";

    try {
      const res = await fetch("/api/referencias/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Erro ao salvar currículos.");

      alertBox.className = "alert-box alert-success show";
      alertBox.innerHTML = `✓ <strong>Sucesso!</strong> ${escapeHtml(data.mensagem || "Currículos adicionados à base de referência.")}`;
      carregarReferencias();
    } catch (err) {
      alertBox.className = "alert-box alert-error show";
      alertBox.textContent = err.message || "Erro no envio.";
    } finally {
      if (btnUpload) {
        btnUpload.disabled = false;
        btnUpload.textContent = "Selecionar Currículos";
      }
      if (uploadProg) uploadProg.textContent = "";
      if (fileInput) fileInput.value = "";
    }
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      enviarArquivos(fileInput.files);
    });
  }

  if (dropzone) {
    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      if (e.dataTransfer && e.dataTransfer.files) {
        enviarArquivos(e.dataTransfer.files);
      }
    });
  }

  carregarReferencias();
}

/* ==========================================================================
   4. FORMULÁRIO PARA AVALIAÇÃO DE PERFIL
   ========================================================================== */
function initQuestionario() {
  const DRAFT_KEY = "lf-aramys-escuta-v2";
  const form = document.getElementById("formPerfilPesquisador");
  const alertBox = document.getElementById("perfilAlert");
  const submitBtn = document.getElementById("btnSalvarPerfil");
  const parte1Btn = document.getElementById("btnSalvarParte1");
  const statusBanner = document.getElementById("perfilStatusBanner");
  const savedDetailsBox = document.getElementById("perfilSavedDetails");
  const badgePerfil = document.getElementById("badgePerfilStatus");
  const progText = document.getElementById("aramysProgText");
  const progFill = document.getElementById("aramysProgFill");
  const draftInfo = document.getElementById("aramysDraftInfo");
  const btnLimparRascunho = document.getElementById("btnAramysLimparRascunho");
  const q30LimitNote = document.getElementById("aramysQ30LimitNote");
  const qCards = form ? Array.from(form.querySelectorAll(".q-card")) : [];
  const qCardsP1 = form ? Array.from(form.querySelectorAll(".q-card[data-p1]")) : [];
  const qCardsCont = form ? Array.from(form.querySelectorAll(".q-card[data-qid]")) : [];
  const blockLinks = Array.from(document.querySelectorAll(".ar-block-pills a[data-block]"));

  function cardRespondido(card) {
    const temMarcado = card.querySelectorAll("input:checked").length > 0;
    const temTexto = Array.from(card.querySelectorAll("textarea, input[type=text], select"))
      .some((el) => el.value.trim().length > 0);
    return temMarcado || temTexto;
  }

  function atualizarProgresso() {
    if (!qCardsCont.length) return;
    let respCont = 0;
    const porBloco = {};

    qCardsCont.forEach((card) => {
      const bloco = card.dataset.block || "";
      if (!porBloco[bloco]) porBloco[bloco] = { total: 0, feitas: 0 };
      porBloco[bloco].total += 1;

      if (cardRespondido(card)) {
        respCont += 1;
        porBloco[bloco].feitas += 1;
      }
    });

    const respP1 = qCardsP1.filter(cardRespondido).length;
    const total = qCardsCont.length;
    const pct = Math.round((respCont * 100) / total);
    if (progText) {
      progText.textContent = `${respCont} de ${total} questões da continuação respondidas` +
        (qCardsP1.length ? ` · ${respP1}/${qCardsP1.length} iniciais` : "");
    }
    if (progFill) progFill.style.width = `${pct}%`;

    blockLinks.forEach((a) => {
      const st = porBloco[a.dataset.block];
      a.classList.toggle("done", Boolean(st && st.feitas === st.total));
    });
  }

  function salvarRascunho() {
    if (!form) return;
    try {
      const estado = {
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
    if (!form) return;
    try {
      const bruto = localStorage.getItem(DRAFT_KEY);
      if (!bruto) return;
      const estado = JSON.parse(bruto);
      if (Array.isArray(estado.checks)) {
        estado.checks.forEach((c) => {
          form.querySelectorAll(`input[name="${CSS.escape(c.name)}"]`).forEach((el) => {
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

  function renderizarRespostasSalvas(respostas) {
    if (!savedDetailsBox) return;
    savedDetailsBox.replaceChildren();
    if (!Array.isArray(respostas) || !respostas.length) return;

    const details = document.createElement("details");
    details.className = "ar-saved-details";
    const summary = document.createElement("summary");
    summary.textContent = `Ver último envio registrado (${respostas.length} resposta${respostas.length === 1 ? "" : "s"})`;
    details.appendChild(summary);

    const list = document.createElement("div");
    list.className = "ar-saved-list";
    respostas.forEach((item) => {
      const row = document.createElement("div");
      row.className = "ar-saved-item";
      const q = document.createElement("b");
      q.textContent = item.pergunta || "";
      const a = document.createElement("span");
      a.textContent = item.resposta || "";
      row.append(q, a);
      list.appendChild(row);
    });
    details.appendChild(list);
    savedDetailsBox.appendChild(details);
  }

  // Carregar respostas prévias se existirem
  async function verificarRespostasPrevias() {
    try {
      const res = await fetch("/api/pesquisa/aramys");
      if (!res.ok) return;
      const data = await res.json();
      if (data.respondido) {
        if (badgePerfil) {
          badgePerfil.textContent = "Respondido ✓";
          badgePerfil.style.background = "#e2f7f1";
          badgePerfil.style.color = "#0d6b5e";
        }
        if (statusBanner) {
          const dataFmt = data.criado_em ? formatDataHora(data.criado_em) : "";
          statusBanner.className = "alert-box alert-success show";
          statusBanner.replaceChildren();
          const strong = document.createElement("strong");
          strong.textContent = `✓ Escuta já registrada por Aramys em ${dataFmt}. `;
          statusBanner.append(
            strong,
            document.createTextNode("Você pode atualizar ou completar suas respostas a qualquer momento enviando o formulário novamente.")
          );
        }
        renderizarRespostasSalvas(data.respostas);
      }
    } catch (err) {
      console.warn("Erro ao checar perfil prévio:", err);
    }
  }

  if (form) {
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

    if (btnLimparRascunho) {
      btnLimparRascunho.addEventListener("click", () => {
        try { localStorage.removeItem(DRAFT_KEY); } catch (e) {}
        form.reset();
        if (q30LimitNote) q30LimitNote.classList.remove("show");
        if (draftInfo) draftInfo.textContent = "Rascunho limpo";
        atualizarProgresso();
      });
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.className = "alert-box";
      alertBox.textContent = "";

      const respostas = coletarRespostasDoFormulario();
      if (respostas.length === 0) {
        alertBox.className = "alert-box alert-error show";
        alertBox.textContent = "Por favor, responda a pelo menos uma das questões antes de enviar.";
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Salvando avaliação…";
      }
      if (parte1Btn) {
        parte1Btn.disabled = true;
        parte1Btn.textContent = "Salvando…";
      }

      try {
        const payload = {
          respondente: "Prof. Dr. Aramys Silva dos Reis",
          respostas: respostas,
        };

        const res = await fetch("/api/pesquisa/pesquisador", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Erro ao gravar respostas.");

        try { localStorage.removeItem(DRAFT_KEY); } catch (err) {}
        if (draftInfo) draftInfo.textContent = "Respostas enviadas ✓";
        alertBox.className = "alert-box alert-success show";
        alertBox.replaceChildren();
        const okStrong = document.createElement("strong");
        okStrong.textContent = `✓ Avaliação completa salva com sucesso (${respostas.length} resposta${respostas.length === 1 ? "" : "s"})! `;
        alertBox.append(okStrong, document.createTextNode("Suas diretrizes estão salvas e balizando as próximas entregas do LattesData."));
        verificarRespostasPrevias();
      } catch (err) {
        alertBox.className = "alert-box alert-error show";
        alertBox.textContent = err.message || "Falha ao enviar avaliação.";
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Enviar Avaliação Completa (Parte 1 + Continuação)";
        }
        if (parte1Btn) {
          parte1Btn.disabled = false;
          parte1Btn.textContent = "Salvar Avaliação de Perfil";
        }
      }
    });
  }

  function coletarRespostasDoFormulario() {
    const itens = [];

    qCards.forEach((card, idx) => {
      const titulo = (card.querySelector(".q-title")?.textContent || `Questão ${idx + 1}`)
        .replace(/^\d+\s*/, "")
        .replace(/\s+/g, " ")
        .trim();
      const selecionados = Array.from(card.querySelectorAll("input:checked")).map((el) => {
        return el.value || el.closest("label")?.textContent.replace(/\s+/g, " ").trim() || "selecionado";
      });
      const textos = Array.from(card.querySelectorAll("textarea, input[type=text]"))
        .map((el) => el.value.trim())
        .filter(Boolean);

      const todas = [...selecionados, ...textos];
      if (todas.length > 0) {
        itens.push({
          pergunta: titulo,
          resposta: todas.join("; "),
        });
      }
    });

    return itens;
  }

  restaurarRascunho();
  atualizarProgresso();
  verificarRespostasPrevias();
}

/* ==========================================================================
   UTILITÁRIOS
   ========================================================================== */
function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function formatDataHora(isoString) {
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function getPrioridadeClass(prioridade) {
  const p = (prioridade || "").toLowerCase();
  if (p.includes("crítica") || p.includes("alta")) return "badge-rose";
  if (p.includes("média") || p.includes("desejável")) return "badge-amber";
  if (p.includes("futura")) return "badge-blue";
  return "badge-mint";
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
