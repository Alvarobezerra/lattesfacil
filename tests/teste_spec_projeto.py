"""Regressão das regras do formulário de projeto confirmadas no Lattes real (validação de 18-20/11/2026):
radios Sim/Não corretos, grupos de marcação, condicionais, obrigatórios (Ano fim só se concluído; instituição e órgão sempre),
listas da aba Equipe e do financiamento, e o cálculo de 'obrigatórios que faltam' do servidor."""
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


spec = json.loads((RAIZ / "itens" / "especificacao" / "projeto.json").read_text(encoding="utf-8"))
por_nome = {v["variante"]: v for v in spec["variantes"]}
checa("5 variantes de projeto", len(por_nome) == 5, list(por_nome))

for nome, v in por_nome.items():
    c = {x["name"].lower(): x for x in v["campos"]}
    checa(f"{nome}: radio de inovação Sim=S / Não=N", c["f_sta_inovacao"]["opcoes"] == {"Sim": "S", "Não": "N"}, c["f_sta_inovacao"].get("opcoes"))
    checa(f"{nome}: instituição e órgão obrigatórios", c["f_inst"]["obrigatorio"] and c["f_orgao"]["obrigatorio"])
    checa(f"{nome}: Ano fim só obrigatório se concluído", not c["f_ano_fim"]["obrigatorio"] and c["f_ano_fim"].get("obrigatorio_quando", {}).get("valor") == "Concluído", c["f_ano_fim"])
    chaves = {g["chave"] for g in v["grades"]}
    checa(f"{nome}: listas Pesquisadores, Instituições envolvidas e Financiamento", {"autores", "instituicoes_envolvidas", "financiamentos"} <= chaves, chaves)
    fin = next(g for g in v["grades"] if g["chave"] == "financiamentos")
    checa(f"{nome}: financiamento com 5 colunas do Lattes", [x["rotulo"] for x in fin["colunas"]] == ["Instituição", "Código do projeto", "Moeda", "Valor financiado", "Natureza"])
    checa(f"{nome}: abas Produção C&T e Orientações informativas", [a["aba"] for a in v.get("abas_informativas", [])] == ["Produção C & T", "Orientações"])

ens = por_nome["Projeto de ensino"]
ce = {x["name"].lower(): x for x in ens["campos"]}
for g in ("f_tpo_cooperacao", "f_tpo_acao_inov", "f_tematica"):
    checa(f"Ensino: {g} é grupo de marcação com rótulo do Lattes", ce[g]["tipo"] == "checkbox" and len(ce[g]["opcoes"]) > 1 and not ce[g]["rotulo"].startswith("f_"), ce[g]["rotulo"])
checa("Ensino: 'Especifique' só com temática Outra", ce["f_especifique"].get("mostrar_quando") == {"name": "f_tematica", "valor": "Outra"})
checa("Ensino: f_tpo_pesq_emp oculto", ce["f_tpo_pesq_emp"].get("oculto") is True)

ext = por_nome["Projeto de extensão"]
cx = {x["name"].lower(): x for x in ext["campos"]}
for n in ("f_cnpj_empresa", "f_txt_email_institucional", "f_txt_setor"):
    checa(f"Extensão: {n} condicional à cooperação com empresa", cx[n].get("mostrar_quando", {}).get("name") == "f_tpo_pesq_emp")
checa("Extensão: potencial de inovação condicional à inovação", cx["f_txt_potencial"].get("mostrar_quando", {}).get("name") == "f_sta_inovacao")

# servidor: obrigatórios que faltam (campos condicionais não contam; Ano fim só se concluído)
from itens.leitores import ler  # noqa: E402

texto = ("Art. 1º Homologar o Projeto de Extensão intitulado Ciência na Rede: descomplicando a ciência, coordenado pelo Professor Aramys Silva dos Reis, "
         "da Coordenação do Curso de Medicina, vinculada ao Centro de Ciências de Imperatriz (CCIm), da Universidade Federal do Maranhão. São Luís, 28 de janeiro de 2025.")
r = ler("projeto", texto, "")
faltam = r["faltam_obrigatorios"]
checa("leitor: 'Ano fim' não é cobrado em projeto em andamento", "Ano fim" not in faltam, faltam)
checa("leitor: campos de empresa/potencial não são cobrados sem gatilho", not any(x in faltam for x in ("CNPJ da empresa", "Setor", "E-mail Institucional")), faltam)
checa("leitor: coordenador do documento vira pesquisador coordenador", r["valores"].get("grade:autores", [{}])[0].get("coordenador") is True, r["valores"].get("grade:autores"))
checa("leitor: órgão sugerido é o centro citado", "Imperatriz" in r["valores"].get("f_orgao", ""), r["valores"].get("f_orgao"))

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
