"""Fontes de citação (OpenAlex, OpenCitations, Crossref). Cada função falha em silêncio: devolve vazio e registra aviso."""
from __future__ import annotations

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 15
USER_AGENT = "LattesFacilCitacoes/1.0 (mailto:suporte@lattesfacil.org)"
OPENALEX = "https://api.openalex.org"
SELECT_OBRA = "id,doi,title,publication_year,cited_by_count,authorships,primary_location"


def limpar_doi(doi: str | None) -> str:
    if not doi:
        return ""
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.I)
    return d.strip().rstrip(".,;)").lower()


def _oa_params(extra: dict[str, Any]) -> dict[str, Any]:
    params = dict(extra)
    chave = os.environ.get("OPENALEX_API_KEY", "").strip()
    if chave:
        params["api_key"] = chave
    else:
        params["mailto"] = "suporte@lattesfacil.org"
    return params


def _get(url: str, params: dict[str, Any] | None = None) -> Any | None:
    try:
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        logger.warning("%s -> HTTP %s", url, r.status_code)
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Falha em %s: %s", url, exc)
    return None


def _obra_oa(w: dict[str, Any]) -> dict[str, Any]:
    loc = w.get("primary_location") or {}
    fonte = (loc.get("source") or {}) if isinstance(loc, dict) else {}
    autores = []
    for a in w.get("authorships") or []:
        au = a.get("author") or {}
        autores.append({"id": (au.get("id") or "").rsplit("/", 1)[-1], "nome": au.get("display_name") or ""})
    return {
        "openalex_id": (w.get("id") or "").rsplit("/", 1)[-1],
        "doi": limpar_doi(w.get("doi")),
        "titulo": " ".join((w.get("title") or "").split()),
        "ano": w.get("publication_year") or None,
        "veiculo": fonte.get("display_name") or "",
        "autores": autores,
        "cited_by_count": w.get("cited_by_count") or 0,
    }


def openalex_obras_por_orcid(orcid: str, limite: int = 25) -> list[dict[str, Any]]:
    dados = _get(f"{OPENALEX}/works", _oa_params({
        "filter": f"author.orcid:{orcid}", "per_page": min(limite, 100),
        "sort": "cited_by_count:desc", "select": SELECT_OBRA,
    }))
    return [_obra_oa(w) for w in (dados or {}).get("results", [])][:limite]


def openalex_obra_por_doi(doi: str) -> dict[str, Any] | None:
    w = _get(f"{OPENALEX}/works/doi:{doi}", _oa_params({"select": SELECT_OBRA}))
    return _obra_oa(w) if isinstance(w, dict) and w.get("id") else None


def openalex_citantes(openalex_id: str, limite: int = 200) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = "*"
    while cursor and len(out) < limite:
        dados = _get(f"{OPENALEX}/works", _oa_params({
            "filter": f"cites:{openalex_id}", "per_page": min(200, limite - len(out)),
            "cursor": cursor, "select": SELECT_OBRA,
        }))
        if not dados:
            break
        out.extend(_obra_oa(w) for w in dados.get("results", []))
        cursor = (dados.get("meta") or {}).get("next_cursor")
    return out[:limite]


def opencitations_citantes(doi: str, limite: int = 200) -> list[dict[str, Any]]:
    """Pares DOI→DOI abertos. Só traz DOI e data; o título é completado por outras fontes."""
    dados = _get(f"https://api.opencitations.net/index/v2/citations/doi:{doi}")
    out: list[dict[str, Any]] = []
    for item in dados or []:
        ids = (item.get("citing") or "").split()
        d = next((limpar_doi(i[4:]) for i in ids if i.startswith("doi:")), "")
        if d:
            criacao = (item.get("creation") or "")[:4]
            out.append({"doi": d, "titulo": "", "ano": int(criacao) if criacao.isdigit() else None,
                        "veiculo": "", "autores": [], "openalex_id": ""})
        if len(out) >= limite:
            break
    return out


def crossref_contagem(doi: str) -> int | None:
    dados = _get(f"https://api.crossref.org/works/{doi}")
    try:
        return int(dados["message"]["is-referenced-by-count"])
    except (TypeError, KeyError, ValueError):
        return None
