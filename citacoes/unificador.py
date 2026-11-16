"""União das citações vindas de várias fontes, sem contar duas vezes, guardando a proveniência."""
from __future__ import annotations

import re
from typing import Any


def chave_titulo(titulo: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (titulo or "").lower())


def unificar(por_fonte: dict[str, list[dict[str, Any]]], autores_obra: set[str] | None = None) -> list[dict[str, Any]]:
    """por_fonte: {"openalex": [citante...], "opencitations": [...]} -> lista única com `fontes` e `autocitacao`."""
    autores_obra = autores_obra or set()
    por_doi: dict[str, dict[str, Any]] = {}
    por_tit: dict[str, dict[str, Any]] = {}
    unicos: list[dict[str, Any]] = []

    for fonte, lista in por_fonte.items():
        for c in lista:
            doi, tk = c.get("doi") or "", chave_titulo(c.get("titulo") or "")
            alvo = (por_doi.get(doi) if doi else None) or (por_tit.get(tk) if tk else None)
            if alvo is None:
                alvo = {"doi": doi, "titulo": "", "ano": None, "veiculo": "", "autores": [], "fontes": []}
                unicos.append(alvo)
            for campo in ("doi", "titulo", "ano", "veiculo"):
                if not alvo[campo] and c.get(campo):
                    alvo[campo] = c[campo]
            if not alvo["autores"] and c.get("autores"):
                alvo["autores"] = c["autores"]
            if fonte not in alvo["fontes"]:
                alvo["fontes"].append(fonte)
            if alvo["doi"]:
                por_doi[alvo["doi"]] = alvo
            tk = chave_titulo(alvo["titulo"])
            if tk:
                por_tit[tk] = alvo

    for alvo in unicos:
        ids = {a.get("id") for a in alvo["autores"] if a.get("id")}
        alvo["autocitacao"] = bool(ids & autores_obra)
    unicos.sort(key=lambda x: (x["ano"] or 0), reverse=True)
    return unicos
