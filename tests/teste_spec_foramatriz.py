"""Regressão dos itens fora da matriz que dependem de lupas (conferido no Lattes real em 21/11/2026): formação acadêmica (instituição do doutorado
sanduíche/co-tutela) e atuação profissional (instituição e vínculo). Complementa teste_spec_fora_matriz.py (paridade dos demais itens)."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from ferramentas.valida_paridade import carregar_excecoes, comparar, slug  # noqa: E402

falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


spec = json.loads((RAIZ / "itens" / "especificacao" / "formacao_academica.json").read_text(encoding="utf-8"))
checa("formação acadêmica: 10 formulários", len(spec["variantes"]) == 10, len(spec["variantes"]))
for v in spec["variantes"]:
    ref = next((json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "docs" / "campos-lattes" / "ref" / "formacao_academica").glob("*.json"))
                if p.name != "excecoes.json" and json.loads(p.read_text(encoding="utf-8")).get("variante_slug") == slug(v["variante"])), None)
    checa(f"formação / {v['variante']}: captura real arquivada", ref is not None)
    if ref is None:
        continue
    just = {(x["categoria"], x["campo"].lower()) for x in carregar_excecoes("formacao_academica").get(ref["variante_slug"], [])}
    pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in just]
    checa(f"formação / {v['variante']}: paridade com a captura real, 0 pendentes", not pend, pend)
    for c in v["campos"]:
        if c["name"].lower().startswith("f_inst_dout"):
            checa(f"formação / {v['variante']} / {c['name']}: marcado como lupa de instituição e condicional (ou oculto fora do doutorado)", c.get("lupa_instituicao") and (c.get("mostrar_quando") or c.get("oculto")), c)

at = json.loads((RAIZ / "itens" / "especificacao" / "atuacao_profissional.json").read_text(encoding="utf-8"))["variantes"][0]
ca = {c["name"].lower(): c for c in at["campos"]}
checa("atuação: vínculo e vínculo empregatício só depois da instituição (checkVinc limpa sem ela)", ca["f_vinc"].get("exige_antes", {}).get("name") == "f_inst" and ca["f_stavinc"].get("exige_antes", {}).get("name") == "f_inst")

app = (RAIZ / "static" / "app.js").read_text(encoding="utf-8")
nucleo = (RAIZ / "extensao" / "autofill_core.js").read_text(encoding="utf-8")
for nome, texto in (("app.js", app), ("autofill_core.js (extensão)", nucleo)):
    checa(f"robô ({nome}): lupas sele_inst(2/3/4) do doutorado", "f_inst_dout_sw: [3" in texto and "f_inst_dout_ct: [4" in texto and "f_inst_dout: [2" in texto)
    checa(f"robô ({nome}): lupa de vínculo chama sele() e 'Outro' libera a digitação", "gLupaVinc" in texto and "gw.sele('Outro')" in texto)
    checa(f"robô ({nome}): sele_inst(1) quando a função pede o nível", "gw.sele_inst(1)" in texto)

casos = (RAIZ / "ferramentas" / "gerar_casos.py").read_text(encoding="utf-8")
checa("gerador de casos: vínculo (4 fixos + Outro) e instituições do doutorado entram na matriz", '"Celetista"' in casos and '"f_inst_dout_ct"' in casos)
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
