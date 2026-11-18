"""Autores citados no currículo (rotina de primeiro acesso): interpretação das linhas, gravação por usuário e busca da citação.
Uso: python tests/teste_autores_cv.py"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import autores_cv as A  # noqa: E402

falhas = 0


def checa(nome, cond, extra=""):
    global falhas
    print(("OK   " if cond else "FALHA ") + nome + (f" — {extra}" if extra and not cond else ""))
    falhas += 0 if cond else 1


linhas = [
    ["Nome", "Nome em citações bibliográficas"],  # cabeçalho
    ["1", "Ana Lúcia Fernandes Pereira", "PEREIRA, A. L. F."],
    ["2", "Virgínia Kelly Gonçalves Abreu", "ABREU, V. K. G.; ABREU, V. K."],
    ["3", "Tatiana de Oliveira Lemos"],  # sem citação
    ["SANTOS, A. A. B."],  # só citação
    ["Ana Lúcia Fernandes Pereira", "PEREIRA, A. L. F."],  # repetida
    ["", ""],
]
it = A.interpretar_linhas(linhas)
nomes = [x["nome"] for x in it]
checa("cabeçalho e linhas vazias não viram autor", "Nome" not in nomes and len(it) == 4, nomes)
checa("citação reconhecida e número da linha ignorado", next(x for x in it if x["nome"].startswith("Ana"))["citacao"] == "PEREIRA, A. L. F.")
checa("várias citações na mesma célula são mantidas", "ABREU, V. K. G." in next(x for x in it if x["nome"].startswith("Virg"))["citacao"])
checa("autor sem citação entra só com o nome", next(x for x in it if x["nome"].startswith("Tatiana"))["citacao"] == "")
checa("linha só com citação entra", any(x["nome"] == "" and x["citacao"] == "SANTOS, A. A. B." for x in it))

c = sqlite3.connect(":memory:")
A.criar_tabelas(c)
checa("antes da coleta: não coletado", A.estado(c, "Álvaro Antônio Bezerra dos Santos") == {"coletado": False, "total": 0, "coletado_em": "", "id_cv": ""})
r = A.salvar(c, "Álvaro Antônio Bezerra dos Santos", linhas, "K4298460T6")
checa("salva e conta os autores", r["total"] == 4 and A.estado(c, "alvaro antonio bezerra dos santos")["coletado"], r)
checa("é por usuário", not A.estado(c, "Aramys Silva dos Reis")["coletado"])
checa("coleta nova substitui a anterior", A.salvar(c, "Álvaro Antônio Bezerra dos Santos", [["Maria de Sousa Lima", "LIMA, M. S."]])["total"] == 1 and len(A.listar(c, "Álvaro Antônio Bezerra dos Santos")["autores"]) == 1)
A.salvar(c, "Aramys Silva dos Reis", linhas)
checa("citação conhecida por primeiro e último nome", A.citacao_de(c, "Aramys Silva dos Reis", "ANA LÚCIA PEREIRA") == "PEREIRA, A. L. F.")
checa("nome desconhecido não devolve citação", A.citacao_de(c, "Aramys Silva dos Reis", "João Nunes") == "")

print(f"{falhas} falha(s)")
sys.exit(1 if falhas else 0)
