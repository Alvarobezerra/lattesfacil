"""Fase 3 da metodologia: gera uma página de teste que renderiza o formulário do app (funções REAIS de static/app.js)
e o compara, estado a estado, com a captura do Lattes real (docs/campos-lattes/ref/<item>/*.json).

Uso:  python ferramentas/gerar_harness_tela.py projeto <pasta_saida>
Depois sirva a pasta (python -m http.server) e abra harness.html: o resultado fica em window.__resultado
(lista de divergências por variante) e no <pre id="saida">.
"""
import json
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUNCOES = ["el", "genCampo", "genGradeTabular", "genVisivel", "genAplicarCondicionais", "genDesenhar", "genColetar", "genAtualizar"]


def extrair(src, nome):
    m = re.search(r"^(?:async )?function " + re.escape(nome) + r"\(", src, re.M)
    if not m:
        m2 = re.search(r"^const " + re.escape(nome) + r" = ", src, re.M)
        if not m2:
            raise SystemExit(f"função {nome} não encontrada em app.js")
        fim = src.index("\n", m2.start())
        return src[m2.start():fim]
    ini = m.start()
    fim = src.index("\n}\n", ini) + 3
    return src[ini:fim]


def main(item, saida):
    saida = pathlib.Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
    funcs = "\n".join(extrair(app, n) for n in FUNCOES)
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    refs = {}
    for p in sorted((RAIZ / "docs" / "campos-lattes" / "ref" / item).glob("*.json")):
        if p.name != "excecoes.json":
            refs[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    dados = {"spec": spec, "refs": refs}
    (saida / "dados.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    shutil.copy(RAIZ / "static" / "styles.css", saida / "styles.css")
    html = (RAIZ / "ferramentas" / "harness_tela_modelo.html").read_text(encoding="utf-8").replace("/*__FUNCOES_DO_APP__*/", funcs)
    (saida / "harness.html").write_text(html, encoding="utf-8")
    print("harness gerado em", saida, "com", len(refs), "capturas")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
