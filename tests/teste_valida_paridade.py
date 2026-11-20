"""Autoteste do comparador da fase 2 (ferramentas/valida_paridade.py): uma captura derivada do próprio spec deve dar
zero divergência; capturas alteradas de propósito devem ser acusadas na categoria certa."""
import copy
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
import valida_paridade as vp  # noqa: E402

falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


def captura_do_spec(var):
    """Monta uma 'captura' fiel ao que o spec descreve (referência sintética só para o autoteste)."""
    campos = []
    for c in var["campos"]:
        t = vp.tipo_spec(c)
        r = {"name": c["name"], "tipo": t, "desabilitado": c["name"].lower() in ("f_inst", "f_orgao"), "somente_leitura": False,
             "visivel_inicial": not c.get("oculto") and not c.get("mostrar_quando")}
        if c.get("maxlength"):
            r["maxlength"] = c["maxlength"]
        if t in ("radio", "grupo_marcacao", "marcacao"):
            r["pergunta"] = c.get("rotulo", "")
            r["opcoes"] = [{"valor": v, "texto": k, "visivel": True, "marcado_inicial": False} for k, v in (c.get("opcoes") or {}).items()]
        elif t == "select":
            r["rotulo"] = c.get("rotulo", "")
            r["total_opcoes"] = len(c.get("opcoes") or {})
            r["opcoes"] = [{"valor": v, "texto": k} for k, v in (c.get("opcoes") or {}).items()]
        else:
            r["rotulo"] = c.get("rotulo", "")
        campos.append(r)
    estados = [{"gatilho": c["mostrar_quando"]["name"], "valor": "x", "texto": "", "aparecem": [c["name"]], "somem": []}
               for c in var["campos"] if c.get("mostrar_quando")]
    return {"item": "projeto", "variante": var["variante"], "variante_slug": vp.slug(var["variante"]), "campos": campos, "estados": estados,
            "listas": [], "botoes_incluir": []}


spec = json.loads((RAIZ / "itens" / "especificacao" / "projeto.json").read_text(encoding="utf-8"))
ens = next(v for v in spec["variantes"] if "ensino" in v["variante"].lower())

ref = captura_do_spec(ens)
div = vp.comparar(ens, ref)
checa("captura fiel ao spec: zero divergência", not div, div[:3])

r2 = copy.deepcopy(ref)
r2["campos"].append({"name": "f_campo_novo", "tipo": "text", "rotulo": "Novo", "visivel_inicial": True, "desabilitado": False, "somente_leitura": False})
checa("campo a mais no Lattes -> ausente_no_spec", any(d["categoria"] == "ausente_no_spec" and d["campo"] == "f_campo_novo" for d in vp.comparar(ens, r2)))

r3 = copy.deepcopy(ref)
t = next(c for c in r3["campos"] if c["name"] == "f_tematica")
t["tipo"] = "marcacao"
checa("grupo desenhado como marcação única -> tipo_diferente", any(d["categoria"] == "tipo_diferente" for d in vp.comparar(ens, r3)))

r4 = copy.deepcopy(ref)
rd = next(c for c in r4["campos"] if c["name"] == "f_sta_inovacao")
rd["opcoes"][0]["valor"] = "X"
checa("opção com valor diferente -> opcoes_diferentes", any(d["categoria"] == "opcoes_diferentes" for d in vp.comparar(ens, r4)))

r5 = copy.deepcopy(ref)
next(c for c in r5["campos"] if c["name"] == "f_titulo")["maxlength"] = 200
checa("maxlength diferente -> maxlength_diferente", any(d["categoria"] == "maxlength_diferente" for d in vp.comparar(ens, r5)))

r6 = copy.deepcopy(ref)
next(c for c in r6["campos"] if c["name"] == "f_titulo")["rotulo"] = "Título do projeto"
checa("rótulo diferente -> rotulo_diferente", any(d["categoria"] == "rotulo_diferente" for d in vp.comparar(ens, r6)))

r7 = copy.deepcopy(ref)
r7["estados"].append({"gatilho": "f_sta_inovacao", "valor": "S", "texto": "Sim", "aparecem": ["f_titulo_en"], "somem": []})
checa("campo que aparece por gatilho sem condicional -> condicional_ausente", any(d["categoria"] == "condicional_ausente" for d in vp.comparar(ens, r7)))

r8 = copy.deepcopy(ref)
r8["botoes_incluir"] = [{"texto": "Incluir novo item", "antes": "Instituição de financiamento"}]
r8["listas"] = [{"id": "autorHolder", "colunas": ["Pesquisadores"], "links": [], "visivel": True}]
spec_sem = copy.deepcopy(ens)
spec_sem["grades"] = []
spec_sem.pop("abas_informativas", None)
cats = {d["categoria"] for d in vp.comparar(spec_sem, r8)}
checa("listas do Lattes sem equivalente -> lista_ausente", "lista_ausente" in cats, cats)

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
