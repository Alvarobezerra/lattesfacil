"""Sugestão de variante do formulário (livro/capítulo, projeto, formação acadêmica, pós-doutorado).

Uso: python tests/teste_variantes.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from itens import especificacao  # noqa: E402
from itens.variantes import rotulo_variante, spec_com_rotulos, sugerir_variante  # noqa: E402

CASOS = [
    ("livro_capitulo", "Capítulo 3 do livro Saúde Coletiva, ISBN 978-85-0000-000-0", "Capítulo de livro"),
    ("livro_capitulo", "Livro publicado pela Editora X, 2ª edição, ISBN 978-85-0000-000-0", "Livro"),
    ("formacao_academica", "Certificamos a conclusão do curso de Mestrado Profissional em Ensino de Ciências", "Mestrado profissional"),
    ("formacao_academica", "Diploma de Mestre em Educação pela UFMA", "Mestrado"),
    ("formacao_academica", "Diploma de Doutor em Física, programa de Doutorado em Física", "Doutorado"),
    ("formacao_academica", "Certificado de Especialização lato sensu em Gestão Pública", "Especialização"),
    ("formacao_academica", "Diploma de Bacharel em Enfermagem, curso de Graduação", "Graduação"),
    ("formacao_academica", "Programa de Residência Médica em Pediatria", "Especialização - Residência médica"),
    ("pos_doutorado", "Estágio de Pós-Doutorado na Universidade de Lisboa", "Pós-doutorado"),
    ("pos_doutorado", "Título de Livre-Docência em Clínica Médica", "Livre-docência"),
    ("projeto", "Projeto de extensão: Saúde na escola, coordenado por Ana Lima", "Projeto de extensão"),
    ("projeto", "Projeto de pesquisa sobre biodiversidade do cerrado", "Projetos de pesquisa"),
]
falhas = 0

for item, texto, esperado in CASOS:
    s = sugerir_variante(item, texto)
    spec = especificacao(item)
    v = next((x for x in spec["variantes"] if x["variante"] == s["variante"]), None)
    rot = rotulo_variante(item, v) if v else None
    ok = rot == esperado and bool(s["motivo"])
    falhas += not ok
    print(("OK   " if ok else "FALHA"), item, "->", rot, "| esperado:", esperado)

# doutorado não pode ser confundido com pós-doutorado na formação acadêmica
s = sugerir_variante("formacao_academica", "Estágio de pós-doutorado")
ok = s["variante"] is None
falhas += not ok
print(("OK   " if ok else "FALHA"), "pós-doutorado não vira Doutorado em formacao_academica")

# sem pista: não escolhe sozinho, mas devolve as opções para o usuário
s = sugerir_variante("livro_capitulo", "")
ok = s["variante"] is None and len(s["opcoes"]) == 2
falhas += not ok
print(("OK   " if ok else "FALHA"), "sem texto: sem sugestão e com opções")

# item de formulário único e item sem especificação não quebram
ok = sugerir_variante("premio", "Prêmio X")["variante"] is not None and sugerir_variante("inexistente", "x")["variante"] is None
falhas += not ok
print(("OK   " if ok else "FALHA"), "item único e item inexistente")

# rótulos legíveis para a tela, com as 10 variantes de formação distintas
sp = spec_com_rotulos("formacao_academica")
rots = [v["rotulo"] for v in sp["variantes"]]
ok = len(set(rots)) == 10 and "Doutorado" in rots and not any(r.startswith("Formul") for r in rots)
falhas += not ok
print(("OK   " if ok else "FALHA"), "rótulos das 10 variantes de formação:", rots)

print("%d falha(s)" % falhas)
sys.exit(1 if falhas else 0)
