"""Caderno de resumos (PDF longo): reconhece como caderno, acha os resumos do pesquisador e abre cada um no formulário do spec (anais)."""
import pathlib
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


import server  # noqa: E402
from itens.leitores import de_registro_antigo  # noqa: E402

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("amostras", RAIZ / "tests" / "teste_amostras_sinteticas.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
PESQUISADORA, _caderno = mod.PESQUISADORA, mod._caderno
with tempfile.TemporaryDirectory() as d:
    pdf = pathlib.Path(d) / "caderno.pdf"
    mod._escrever(_caderno(), pdf)
    dados = pdf.read_bytes()
ex = server.process_extract("caderno.pdf", dados, PESQUISADORA)
checa("PDF longo reconhecido como caderno", ex.get("caderno") is True and ex.get("page_count") == 14, ex.get("page_count"))
res, status = server.run_caderno(dados, "caderno.pdf", PESQUISADORA)
rs = res.get("resultados", [])
checa("acha os 14 resumos do pesquisador", status == 200 and len(rs) == 14, (status, len(rs)))
if rs:
    rec = rs[0]["record"]
    g = de_registro_antigo(rec.get("tipo_producao") or "anais", rec)
    v = g["valores"]
    checa("resumo abre no formulário de anais do spec", g["item"] == "anais" and "efeito exemplar" in v.get("f_titulo", "").lower(), v.get("f_titulo"))
    checa("autores e palavras-chave chegam à lista", any("Pinheiro" in a["nome"] for a in v.get("grade:autores", [])) and v.get("grade:palavras_chave"), v.get("grade:autores"))
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
