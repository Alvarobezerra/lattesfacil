"""Gera ferramentas/saida/ciclo_matriz.js: roda a matriz de valores (fases 4 e 5) de vários itens em sequência no Lattes real.
Uso: python ferramentas/gerar_ciclo_matriz.py item1 item2 ...   (antes: python ferramentas/gerar_casos.py <item>)
Resultado em window.top.__cicloM (andamento, resultados por item, rótulos conferidos no formulário aberto)."""
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
js = "window.__planosMatriz = " + json.dumps(planos, ensure_ascii=False) + ";\n" + r"""
(async () => {
  const T = window.top; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
  const car = (n) => new Promise((r) => { const s = document.createElement('script'); s.src = 'http://127.0.0.1:8798/' + n + '?' + Date.now(); s.onload = r; s.onerror = r; document.head.appendChild(s); });
  T.__cicloM = { andamento: '', resultados: [] };
  for (const p of window.__planosMatriz) {
    T.__cicloM.andamento = p.item;
    try {
      await car('saida/casos_' + p.item + '.js');
      T.__alvoF5 = { id: p.item, url: p.url, lista: p.lista };
      let ab = false;
      for (let t = 0; t < 2 && !ab; t++) ab = await T.__f5.abrirPorUrl(p.url, p.pagina);
      if (!ab) { T.__cicloM.resultados.push(p.item + ': formulário não abriu'); continue; }
      await sl(2000);
      let rot = '';
      try { const w = T.__f5.formulario(); const e = w.document.querySelector('[name="f_sta_inovacao"]'); if (e) rot = (e.closest('td') || e.parentElement).textContent.replace(/\s+/g, ' ').trim().slice(0, 90); } catch (e) { /* sem campo */ }
      const slug = Object.keys(window.__casos)[0];
      await T.__f5.rodar(slug, { item: p.item, variante: p.variante }, { lentos: true });
      const res = T.__ultimoF5.resultados;
      T.__cicloM.resultados.push(p.item + ': ' + JSON.stringify(T.__ultimoF5.resumo) + ' | nao-OK: ' + res.filter((x) => x.status !== 'OK').map((x) => x.id + '=' + x.status + ' ' + (x.detalhe || '').slice(0, 60)).join(' ; ') + (rot ? ' | rotulo potencial: ' + rot : ''));
    } catch (e) { T.__cicloM.resultados.push(p.item + ': erro ' + e); }
  }
  T.__cicloM.andamento = 'FIM';
})();
"""
(RAIZ / "ferramentas" / "saida" / "ciclo_matriz.js").write_text(js, encoding="utf-8")
print("planos:", [p["item"] for p in planos])
