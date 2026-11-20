"""Gera ferramentas/saida/ciclo_salvar.js: salvamento de teste (fase 7) de vários itens em sequência no Lattes real e conferência na lista.
Uso: python ferramentas/gerar_ciclo_salvar.py item1 item2 ...   (antes: python ferramentas/gerar_payload_generico.py <item>)
Resultado em window.top.__cicloS: por item, resposta do Lattes ao salvar (mensagem do relatório) e linhas da lista com o prefixo ZZ-TESTE.
NUNCA use com títulos sem o prefixo ZZ-TESTE-LATTESFACIL."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402

planos = []
for item in sys.argv[1:]:
    s = especificacao(item)
    v = s["variantes"][0]
    planos.append({"item": item, "url": v["url"], "lista": s.get("lista", ""), "pagina": v["url"].split("?")[0]})
js = "window.__planosSalvar = " + json.dumps(planos, ensure_ascii=False) + ";\n" + r"""
(async () => {
  const T = window.top; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
  const car = (n) => new Promise((r) => { const s = document.createElement('script'); s.src = 'http://127.0.0.1:8798/' + n + '?' + Date.now(); s.onload = r; s.onerror = r; document.head.appendChild(s); });
  const cv = (T.document.querySelector('[name="f_cod"]') || {}).value || ((T.document.documentElement.innerHTML.match(/[?&]f_cod=([A-Za-z0-9]{6,20})/i) || [])[1]) || '';
  T.__cicloS = { andamento: '', resultados: [] };
  const limpa = (t) => String(t).replace(/\s+/g, ' ').replace(/[?=&;]/g, ' ').slice(0, 900);
  for (const p of window.__planosSalvar) {
    T.__cicloS.andamento = p.item;
    try {
      await car('saida/payload_' + p.item + '.js');
      T.__alvoF5 = { id: p.item, url: p.url, lista: p.lista };
      let ab = false;
      for (let t = 0; t < 2 && !ab; t++) ab = await T.__f5.abrirPorUrl(p.url, p.pagina);
      if (!ab) { T.__cicloS.resultados.push(p.item + ': formulário não abriu'); continue; }
      T.__lfUltimoRelatorio = '';
      await window.__lfAutofill(window.__payloadTeste);
      await sl(14000);
      const rel = limpa(T.__lfUltimoRelatorio);
      // lista: o item de teste deve aparecer
      let lista = '';
      const lu = (p.lista || '').replace('<codigo_do_cv>', cv);
      if (lu) {
        T.modalCV1.setarUrl(lu + (lu.indexOf('f_cod=') < 0 ? (lu.indexOf('?') < 0 ? '?f_cod=' : '&f_cod=') + cv : ''), true);
        await sl(5500);
        const v = (w, d) => { if (d > 5) return; try { if (/lista/i.test(w.location.pathname)) { const t = w.document.body.innerText; if (/ZZ-TESTE/.test(t)) lista += limpa(t.slice(t.indexOf('ZZ-TESTE') - 5, t.indexOf('ZZ-TESTE') + 120)) + ' | '; } } catch (e) { /* outro domínio */ } for (let i = 0; i < w.length; i++) v(w[i], d + 1); };
        v(T, 0);
      }
      T.__cicloS.resultados.push(p.item + ': ' + rel + ' || LISTA: ' + (lista || 'não encontrado'));
    } catch (e) { T.__cicloS.resultados.push(p.item + ': erro ' + e); }
  }
  T.__cicloS.andamento = 'FIM';
})();
"""
(RAIZ / "ferramentas" / "saida" / "ciclo_salvar.js").write_text(js, encoding="utf-8")
print("planos:", [p["item"] for p in planos])
