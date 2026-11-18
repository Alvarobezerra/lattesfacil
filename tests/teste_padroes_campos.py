"""Padrões por nome de campo (itens/padroes_campos.json) aplicados nas especificações geradas."""
import json, pathlib, sys
RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao, ids_especificados

falhas = 0
def ok(c, msg):
    global falhas
    print(("OK   " if c else "FALHA ") + msg)
    falhas += 0 if c else 1

padroes = {k.lower(): v for k, v in json.loads((RAIZ / "itens" / "padroes_campos.json").read_text(encoding="utf-8"))["campos"].items()}
n = 0
for i in ids_especificados():
    for v in especificacao(i)["variantes"]:
        for c in v["campos"]:
            if c["name"].lower() in padroes and c.get("origem_padrao") == "padrao_comum":
                n += 1
                if c.get("opcoes"):
                    if c["opcoes"].get(c["padrao"]) != padroes[c["name"].lower()]["codigo"]:
                        ok(False, f"{i}.{c['name']}: padrão {c['padrao']!r} não corresponde ao código")
                if not c.get("confira"):
                    ok(False, f"{i}.{c['name']} sem marca 'confira'")
            if c["name"].lower() == "f_tipo_privacidade":
                ok("padrao" not in c, f"{i}: privacidade sem padrão")
ok(n > 20, f"padrões comuns aplicados em {n} campos")
pe = {c["name"]: c for c in especificacao("participacao_evento")["variantes"][0]["campos"]}
ok(pe["f_pais"].get("origem") == "fixo" and "origem_padrao" not in pe["f_pais"], "curadoria não é sobreposta (f_pais de participacao_evento)")
ok(pe["F_FORMA"]["padrao"] == "Ouvinte", "padrão da curadoria preservado")
print("%d falha(s)" % falhas)
sys.exit(1 if falhas else 0)
