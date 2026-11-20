"""Gera ferramentas/saida/ciclo_captura.js: roda a captura (fase 1) de vários itens em sequência no Lattes.
Uso: python ferramentas/gerar_ciclo_captura.py item1 item2 ...
No Lattes (aba do currículo, com auditoria_lattes.js, autofill_core.js e executor_preenchimento.js carregados):
  carregar /saida/ciclo_captura.js e olhar window.top.__ciclo (andamento/resultados)."""
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
    planos.append({"item": item, "variante": v["variante"], "url": v["url"], "lista": s.get("lista", ""), "pagina": v["url"].split("?")[0]})
js = "window.__planosCiclo = " + json.dumps(planos, ensure_ascii=False) + ";\n" + r"""
(async () => {
  const T = window.top; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
  T.__ciclo = { andamento: '', resultados: [] };
  for (const p of window.__planosCiclo) {
    T.__ciclo.andamento = p.item;
    try {
      T.__alvoF5 = { id: p.item, url: p.url, lista: p.lista };
      let ab = false;
      for (let t = 0; t < 2 && !ab; t++) ab = await T.__f5.abrirPorUrl(p.url, p.pagina);
      if (!ab) { T.__ciclo.resultados.push(p.item + ': formulário não abriu'); continue; }
      await sl(2500);
      const r = await T.__auditar({ item: p.item, variante: p.variante, variante_slug: p.item });
      T.__ciclo.resultados.push(p.item + ': ' + String(r).slice(0, 80) + ' | campos=' + ((T.__ultimaCaptura || {}).campos || []).length);
    } catch (e) { T.__ciclo.resultados.push(p.item + ': erro ' + e); }
  }
  T.__ciclo.andamento = 'FIM';
})();
"""
(RAIZ / "ferramentas" / "saida" / "ciclo_captura.js").write_text(js, encoding="utf-8")
print("planos:", [p["item"] for p in planos])
