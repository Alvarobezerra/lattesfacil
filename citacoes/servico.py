"""Orquestra as fontes por obra e devolve o resumo do pesquisador."""
from __future__ import annotations

import re
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from . import fontes
from .unificador import unificar

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
TTL = 3600
_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_lock = threading.Lock()


def _citacoes_da_obra(obra: dict[str, Any], max_citantes: int) -> dict[str, Any]:
    chave = obra.get("doi") or obra.get("openalex_id") or ""
    agora = time.time()
    with _lock:
        hit = _cache.get(chave)
        if hit and agora - hit[0] < TTL:
            return hit[1]

    por_fonte: dict[str, list[dict[str, Any]]] = {}
    if obra.get("openalex_id"):
        por_fonte["openalex"] = fontes.openalex_citantes(obra["openalex_id"], max_citantes)
    if obra.get("doi"):
        por_fonte["opencitations"] = fontes.opencitations_citantes(obra["doi"], max_citantes)
    crossref = fontes.crossref_contagem(obra["doi"]) if obra.get("doi") else None

    ids_autores = {a["id"] for a in obra.get("autores", []) if a.get("id")}
    citantes = unificar(por_fonte, ids_autores)
    res = {
        "titulo": obra.get("titulo", ""), "doi": obra.get("doi", ""), "ano": obra.get("ano"),
        "veiculo": obra.get("veiculo", ""),
        "contagem_fontes": {
            "openalex": obra.get("cited_by_count", 0),
            "opencitations": len(por_fonte.get("opencitations", [])),
            "crossref": crossref,
        },
        "total_unico": len(citantes),
        "total_estimado": max([obra.get("cited_by_count", 0), crossref or 0, len(citantes)]),
        "autocitacoes": sum(1 for c in citantes if c["autocitacao"]),
        "truncado": any(len(v) >= max_citantes for v in por_fonte.values()),
        "citantes": [{k: v for k, v in c.items() if k != "autores"} for c in citantes],
    }
    with _lock:
        _cache[chave] = (agora, res)
    return res


def citacoes_do_pesquisador(orcid: str | None = None, dois: list[str] | None = None,
                            max_obras: int = 25, max_citantes: int = 200) -> dict[str, Any]:
    obras: list[dict[str, Any]] = []
    if orcid:
        obras.extend(fontes.openalex_obras_por_orcid(orcid, max_obras))
    vistos = {o["doi"] for o in obras if o.get("doi")}
    for d in dois or []:
        d = fontes.limpar_doi(d)
        if DOI_RE.match(d) and d not in vistos and len(obras) < max_obras:
            o = fontes.openalex_obra_por_doi(d) or {"doi": d, "titulo": "", "ano": None, "autores": [],
                                                    "openalex_id": "", "veiculo": "", "cited_by_count": 0}
            obras.append(o)
            vistos.add(d)

    with ThreadPoolExecutor(max_workers=4) as pool:
        resultados = list(pool.map(lambda o: _citacoes_da_obra(o, max_citantes), obras))

    por_ano: Counter[int] = Counter()
    total = auto = 0
    for r in resultados:
        total += r["total_unico"]
        auto += r["autocitacoes"]
        por_ano.update(c["ano"] for c in r["citantes"] if c["ano"])
    resultados.sort(key=lambda r: r["total_unico"], reverse=True)
    return {
        "obras": resultados,
        "resumo": {"obras": len(resultados), "citacoes_unicas": total, "autocitacoes": auto,
                   "sem_autocitacao": total - auto, "por_ano": dict(sorted(por_ano.items())),
                   "consultado_em": time.strftime("%Y-%m-%d %H:%M")},
    }
