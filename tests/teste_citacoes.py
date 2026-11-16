"""Testes offline do unificador e do serviço de citações (sem rede).

Uso:  python tests/teste_citacoes.py
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from citacoes import servico  # noqa: E402
from citacoes.unificador import unificar  # noqa: E402

falhas = []


def checa(nome, ok):
    print("OK   " if ok else "FALHA", nome)
    if not ok:
        falhas.append(nome)


oa = [
    {"doi": "10.1/a", "titulo": "Estudo A", "ano": 2024, "veiculo": "Rev X", "autores": [{"id": "A1", "nome": "Eu"}]},
    {"doi": "", "titulo": "Estudo: B!", "ano": 2023, "veiculo": "", "autores": []},
]
oc = [
    {"doi": "10.1/a", "titulo": "", "ano": 2024, "veiculo": "", "autores": []},
    {"doi": "10.1/c", "titulo": "", "ano": 2022, "veiculo": "", "autores": []},
]
u = unificar({"openalex": oa, "opencitations": oc}, {"A1"})
checa("une por DOI sem duplicar (3 únicas)", len(u) == 3)
a = next(c for c in u if c["doi"] == "10.1/a")
checa("guarda proveniência das duas fontes", sorted(a["fontes"]) == ["openalex", "opencitations"])
checa("marca autocitação por autor em comum", a["autocitacao"] is True)
checa("preenche título vindo só de uma fonte", a["titulo"] == "Estudo A")
checa("ordena do ano mais recente", [c["ano"] for c in u] == [2024, 2023, 2022])

obra = {"openalex_id": "W1", "doi": "10.1/z", "titulo": "Z", "ano": 2020, "veiculo": "", "autores": [], "cited_by_count": 5}
with mock.patch.object(servico.fontes, "openalex_obra_por_doi", return_value=obra), \
        mock.patch.object(servico.fontes, "openalex_citantes", return_value=oa), \
        mock.patch.object(servico.fontes, "opencitations_citantes", return_value=oc), \
        mock.patch.object(servico.fontes, "crossref_contagem", return_value=4):
    r = servico.citacoes_do_pesquisador(dois=["https://doi.org/10.1234/z", "nao-e-doi"])
checa("serviço ignora DOI inválido e normaliza URL", r["resumo"]["obras"] == 1)
checa("resumo soma citações únicas", r["resumo"]["citacoes_unicas"] == 3)
checa("contagem por fonte exposta", r["obras"][0]["contagem_fontes"] == {"openalex": 5, "opencitations": 2, "crossref": 4})

sys.exit(1 if falhas else 0)
