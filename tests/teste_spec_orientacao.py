"""Regressão das orientações (conferidas no Lattes real em 21/11/2026): spec, dependência do tipo de orientação, lupa da agência e leitor."""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
falhas = 0


def checa(nome, ok, detalhe=""):
    global falhas
    print(("OK   " if ok else "FALHA ") + nome + ("" if ok else f" -> {detalhe}"))
    if not ok:
        falhas += 1


from ferramentas.valida_paridade import comparar  # noqa: E402
from itens.leitores import de_registro_antigo, ler  # noqa: E402

for item in ("orientacao_concluida", "orientacao_andamento"):
    spec = json.loads((RAIZ / "itens" / "especificacao" / f"{item}.json").read_text(encoding="utf-8"))
    v = spec["variantes"][0]
    c = {x["name"].lower(): x for x in v["campos"]}
    checa(f"{item}: natureza com 7 opções e país/idioma com 80", len(c["f_cod_prod"]["opcoes"]) == 7 and len(c["f_pais"]["opcoes"]) == 80 and len(c["f_idioma"]["opcoes"]) == 80)
    checa(f"{item}: tipo de orientação exige mestrado ou doutorado", c["f_tpo_orient"].get("exige_antes", {}).get("name") == "F_COD_PROD" and len(c["f_tpo_orient"]["exige_antes"]["valores"]) == 2, c["f_tpo_orient"].get("exige_antes"))
    checa(f"{item}: agência é campo de lupa", c["f_nme_agencia"].get("lupa") is True)
    ref_dir = RAIZ / "docs" / "campos-lattes" / "ref" / item
    ref = json.loads((ref_dir / f"{item}.json").read_text(encoding="utf-8"))
    exc = json.loads((ref_dir / "excecoes.json").read_text(encoding="utf-8")).get(item, [])
    pend = [d for d in comparar(v, ref) if (d["categoria"], d["campo"].lower()) not in {(e["categoria"], e["campo"].lower()) for e in exc}]
    checa(f"{item}: paridade com a captura real (exceções justificadas)", not pend, pend)

r = ler("orientacao_concluida", "Declaramos que Fulano orientou como orientador principal o trabalho de conclusão de curso de Lucas Ferreira Andrade, do curso de Saúde e Tecnologia, intitulado \"Atividade antioxidante\", defendido e aprovado em 2023.", "Fulano")["valores"]
checa("leitor: aluno e curso certos, sem tipo de orientação para TCC", r.get("f_nme_orient") == "Lucas Ferreira Andrade" and r.get("f_curso") == "Saúde e Tecnologia" and not r.get("f_tpo_orient"), r)
checa("registro antigo em andamento vai para o formulário certo", de_registro_antigo("orientacao", {"situacao_orientacao": "Em andamento", "natureza": "Tese de doutorado"})["variante"] == "Orientação em andamento")
ext = (RAIZ / "extensao" / "autofill_core.js").read_text(encoding="utf-8")
checa("extensão: lupa da agência e subtipo do formulário", "gLupaAgencia" in ext and "mesmoSubtipo" in ext)
print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
