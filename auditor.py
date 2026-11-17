"""Auditor de conformidade do currículo (Lattes Audit): lê o XML já interpretado e lista pendências por risco.

A classificação Leve/Grave/Gravíssima é uma HEURÍSTICA do LattesFácil inspirada na Portaria CNPq 2.664/2026; não
reproduz o texto da norma e não substitui a análise do CNPq. Nada é corrigido automaticamente: só se aponta.
"""
from __future__ import annotations

import datetime
import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any

from lattes_xml import _chave_titulo, formatar_doi

RISCOS = ("Gravíssimo", "Grave", "Leve")
CATEGORIAS_COM_DOI = {"artigo"}
CATEGORIAS_ISSN = {"artigo", "artigo_aceito"}


def issn_valido(issn: str) -> bool:
    s = re.sub(r"[^0-9Xx]", "", issn or "").upper()
    if len(s) != 8 or not re.fullmatch(r"\d{7}[\dX]", s):
        return False
    soma = sum(int(c) * (8 - i) for i, c in enumerate(s[:7]))
    dv = (11 - soma % 11) % 11
    return s[7] == ("X" if dv == 10 else str(dv))


def isbn_valido(isbn: str) -> bool:
    s = re.sub(r"[^0-9Xx]", "", isbn or "").upper()
    if len(s) == 13 and s.isdigit():
        soma = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s[:12]))
        return (10 - soma % 10) % 10 == int(s[12])
    if len(s) == 10 and re.fullmatch(r"\d{9}[\dX]", s):
        soma = sum((10 - i) * int(c) for i, c in enumerate(s[:9])) + (10 if s[9] == "X" else int(s[9]))
        return soma % 11 == 0
    return False


def _p(risco: str, codigo: str, msg: str, item: dict[str, Any] | None = None, como_corrigir: str = "") -> dict[str, Any]:
    return {"risco": risco, "codigo": codigo, "mensagem": msg, "como_corrigir": como_corrigir,
            "item": ({"categoria": item["categoria"], "titulo": item.get("titulo", ""), "ano": item.get("ano", "")} if item else None)}


def _mesma_pessoa(nome: str, outro: str) -> bool:
    a, b = _chave_titulo(nome), _chave_titulo(outro)
    return bool(a and b) and SequenceMatcher(None, a, b).ratio() >= 0.8


def auditar(curriculo: dict[str, Any], hoje: datetime.date | None = None) -> dict[str, Any]:
    hoje = hoje or datetime.date.today()
    achados: list[dict[str, Any]] = []
    itens = curriculo["itens"]

    for it in itens:
        cat, ano = it["categoria"], it.get("ano", "")
        if ano and int(ano) > hoje.year:
            achados.append(_p("Gravíssimo", "ano_futuro", f"Ano {ano} é posterior ao atual; só cabe em 'aceito para publicação'.", it,
                              "Corrija o ano ou mova para 'Artigos aceitos para publicação'."))
        if not ano:
            achados.append(_p("Leve", "sem_ano", "Item sem ano.", it, "Informe o ano no formulário do item."))
        if cat in CATEGORIAS_COM_DOI:
            if not it.get("doi"):
                achados.append(_p("Leve", "sem_doi", "Artigo sem DOI.", it, "Informe o DOI (botão de recuperação do Lattes) se o artigo tiver."))
            elif not formatar_doi(it["doi"]) or it["doi"].lower().startswith(("http", "doi:")):
                achados.append(_p("Grave", "doi_formato", f"DOI fora do formato aceito: {it['doi']}", it,
                                  "Use só o identificador, começando em 10. (sem URL ou 'doi:')."))
        if cat in CATEGORIAS_ISSN:
            if not it.get("issn"):
                achados.append(_p("Leve", "sem_issn", "Artigo sem ISSN do periódico.", it, "Informe o ISSN do periódico."))
            elif not issn_valido(it["issn"]):
                achados.append(_p("Grave", "issn_invalido", f"ISSN inválido (dígito verificador): {it['issn']}", it, "Confira o ISSN no site da revista."))
        if cat in ("livro", "capitulo"):
            if it.get("isbn") and not isbn_valido(it["isbn"]):
                achados.append(_p("Grave", "isbn_invalido", f"ISBN inválido (dígito verificador): {it['isbn']}", it, "Confira o ISBN na ficha catalográfica."))
            elif not it.get("isbn"):
                achados.append(_p("Leve", "sem_isbn", "Livro/capítulo sem ISBN.", it, "Informe o ISBN de 13 dígitos."))
        if cat == "artigo" and not it.get("veiculo"):
            achados.append(_p("Leve", "sem_periodico", "Artigo sem título do periódico.", it))
        if cat == "trabalho_evento" and not it.get("veiculo"):
            achados.append(_p("Leve", "sem_evento", "Trabalho em evento sem o nome do evento.", it))

    # duplicidades dentro do próprio currículo: a falha mais cobrada em auditorias
    por_chave: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for it in itens:
        if it.get("titulo") and it["categoria"] not in ("atuacao_profissional", "formacao_academica"):
            por_chave[(it["categoria"], _chave_titulo(it["titulo"]))].append(it)
    for lista in por_chave.values():
        if len(lista) > 1:
            achados.append(_p("Gravíssimo", "duplicado", f"{len(lista)} registros com o mesmo título e tipo.", lista[0],
                              "Mantenha um só registro; duplicar produção infla a pontuação."))
    dois = defaultdict(list)
    for it in itens:
        d = formatar_doi(it.get("doi", ""))
        if d:
            dois[d].append(it)
    for d, lista in dois.items():
        if len(lista) > 1 and not any(a["codigo"] == "duplicado" and a["item"]["titulo"] == lista[0].get("titulo") for a in achados):
            achados.append(_p("Gravíssimo", "doi_repetido", f"O DOI {d} aparece em {len(lista)} registros.", lista[0], "Remova o registro repetido."))

    # nome do pesquisador nas listas de autores: variações incoerentes
    nome = curriculo.get("nome", "")
    if nome:
        variantes = defaultdict(int)
        for it in itens:
            for a in it.get("autores", []):
                if _mesma_pessoa(nome, a):
                    variantes[a.strip()] += 1
        if len(variantes) > 1:
            achados.append(_p("Leve", "nome_inconsistente", "O seu nome aparece grafado de formas diferentes na lista de autores: " +
                              "; ".join(sorted(variantes)) + ".", None, "Padronize a grafia (e o 'nome em citações bibliográficas')."))
        sem_voce = [it for it in itens if it.get("autores") and not any(_mesma_pessoa(nome, a) for a in it["autores"])]
        for it in sem_voce[:20]:
            achados.append(_p("Grave", "autor_ausente", "O seu nome não consta entre os autores deste item.", it,
                              "Confira se a produção é sua ou se o nome foi digitado diferente."))

    # vínculos profissionais sem término há muito tempo
    for it in itens:
        if it["categoria"] == "atuacao_profissional" and it.get("ano") and not it.get("ano_fim") and hoje.year - int(it["ano"]) >= 15:
            achados.append(_p("Leve", "vinculo_sem_fim", f"Vínculo iniciado em {it['ano']} sem data de término.", it,
                              "Se terminou, informe o fim; se segue vigente, confirme a atualização."))

    achados.sort(key=lambda a: RISCOS.index(a["risco"]))
    cont = {r: sum(1 for a in achados if a["risco"] == r) for r in RISCOS}
    return {"resumo": cont, "total": len(achados), "pendencias": achados,
            "aviso": "Classificação de risco é heurística do LattesFácil; consulte a Portaria CNPq 2.664/2026 e o seu setor de pesquisa."}
