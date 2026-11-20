"""O detector de avisos da extensão (background.js) só pode acusar mensagens reais do Lattes: rótulos fixos do formulário (ex.: "Informe o Digital
Object Identifier (DOI®)...") e texto de script da página já causaram falso "o item pode NÃO ter sido salvo" (21/11/2026)."""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
src = (RAIZ / "extensao" / "background.js").read_text(encoding="utf-8")
falhas = 0


def checa(nome, ok):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome)
    if not ok:
        falhas += 1


m = re.search(r"const re = (/.+?/gi);", src)
checa("detector de avisos encontrado", bool(m))
rx = re.compile(m.group(1)[1:-3], re.I) if m else None
checa("não acusa o rótulo 'Informe o Digital Object Identifier'", bool(rx) and not rx.search("Informe o Digital Object Identifier (DOI®) do artigo e clique no botão"))
checa("ainda acusa 'Não foi possível atualizar as informações'", bool(rx) and bool(rx.search("Não foi possível atualizar as informações porque ocorreram os seguintes problemas:")))
checa("ignora texto de script (<br>, aspas e ponto e vírgula)", '<br>|";|function|saida' in src and ".test(linha)) continue" in src)
checa("versão da extensão foi atualizada", '"version": "0.9.7"' in (RAIZ / "extensao" / "manifest.json").read_text(encoding="utf-8"))
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
