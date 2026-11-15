"""Gera autofill_core.js a partir do AUTOFILL_TEMPLATE de static/app.js (fonte única do preenchimento).
Uso: python extensao/build.py   (rode de novo sempre que o template do app.js mudar)."""
import re, pathlib
raiz = pathlib.Path(__file__).resolve().parent.parent
src = (raiz / "static" / "app.js").read_text(encoding="utf-8")
m = re.search(r"const AUTOFILL_TEMPLATE = String\.raw`(.*?)`;\n", src, re.S)
if not m:
    raise SystemExit("AUTOFILL_TEMPLATE não encontrado em static/app.js")
t = m.group(1)
cab = "(async function () {\n  var d = __DATA__;"
if not t.startswith(cab) or not t.rstrip().endswith("})();"):
    raise SystemExit("Formato do template mudou; ajuste build.py")
corpo = t[len(cab):].rstrip()[: -len("})();")]
saida = "// GERADO por extensao/build.py a partir de static/app.js. Não edite.\nwindow.__lfAutofill = async function (d) {" + corpo + "};\n"
(pathlib.Path(__file__).parent / "autofill_core.js").write_text(saida, encoding="utf-8")
print("autofill_core.js gerado,", len(saida), "bytes")
