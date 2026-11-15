"""Módulo de Radar de Coautorias / Obras Online via APIs OpenAlex e CrossRef.

Permite localizar produções científicas vinculadas a um pesquisador pelo seu nome
e/ou ORCID, normalizando e desduplicando os registros para exibição e carregamento
no LattesFácil.
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any

import requests

logger = logging.getLogger(__name__)

USER_AGENT = "LattesFacilRadar/1.0 (https://lattesfacil.org; mailto:suporte@lattesfacil.org)"
DEFAULT_TIMEOUT = 10


def normalize_doi(doi: str | None) -> str:
    """Extrai e normaliza o identificador DOI puro (ex: 10.xxxx/...)."""
    if not doi:
        return ""
    clean = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi.strip(), flags=re.IGNORECASE)
    clean = clean.strip().rstrip(".,;)")
    return clean.lower()


def clean_doi_display(doi: str | None) -> str:
    """Devolve o DOI sem protocolo para exibição/preenchimento de campo."""
    if not doi:
        return ""
    clean = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi.strip(), flags=re.IGNORECASE)
    return clean.strip().rstrip(".,;)")


def normalize_title(title: str | None) -> str:
    """Gera chave alfanumérica normalizada do título para detecção de duplicatas."""
    if not title:
        return ""
    clean = re.sub(r"<[^>]+>", "", title)
    return re.sub(r"[^a-z0-9]", "", clean.lower())


def clean_text(text: str | None) -> str:
    """Remove quebras de linha extras e tags HTML de títulos ou nomes."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return " ".join(clean.split())


def _buscar_openalex(nome_autor: str, orcid: str | None, max_results: int, timeout: int) -> list[dict[str, Any]]:
    """Consulta a API do OpenAlex filtrando por ORCID ou por busca textual."""
    obras: list[dict[str, Any]] = []
    headers = {"User-Agent": USER_AGENT}

    clean_orcid = ""
    if orcid:
        clean_orcid = re.sub(r"^https?://orcid\.org/", "", orcid.strip())
        clean_orcid = clean_orcid.strip()

    if clean_orcid:
        url = f"https://api.openalex.org/works?filter=author.orcid:{clean_orcid}&per_page={max_results}"
    elif nome_autor and nome_autor.strip():
        encoded = urllib.parse.quote(nome_autor.strip())
        url = f"https://api.openalex.org/works?search={encoded}&per_page={max_results}"
    else:
        return obras

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            for w in data.get("results", []):
                raw_title = w.get("title") or ""
                if not raw_title:
                    continue
                doi_raw = w.get("doi") or ""
                ano_val = w.get("publication_year")
                ano = str(ano_val) if ano_val else ""

                loc = w.get("primary_location") or {}
                source = (loc.get("source") or {}) if isinstance(loc, dict) else {}
                veiculo = source.get("display_name") or ""

                autores = []
                for a in w.get("authorships", []):
                    autor_obj = a.get("author") or {}
                    dname = autor_obj.get("display_name") or ""
                    if dname:
                        autores.append(clean_text(dname))

                obras.append({
                    "titulo": clean_text(raw_title),
                    "doi": clean_doi_display(doi_raw),
                    "ano": ano,
                    "veiculo": clean_text(veiculo),
                    "autores": autores,
                })
    except requests.RequestException as exc:
        logger.warning("Falha na consulta ao OpenAlex: %s", exc)
    except Exception as exc:
        logger.warning("Erro inesperado ao processar OpenAlex: %s", exc)

    return obras


def _buscar_crossref(nome_autor: str, max_results: int, timeout: int) -> list[dict[str, Any]]:
    """Consulta a API do CrossRef buscando pelo nome do autor."""
    obras: list[dict[str, Any]] = []
    if not nome_autor or not nome_autor.strip():
        return obras

    headers = {"User-Agent": USER_AGENT}
    encoded = urllib.parse.quote(nome_autor.strip())
    url = f"https://api.crossref.org/works?query.author={encoded}&rows={max_results}"

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            items = (data.get("message") or {}).get("items", [])
            for item in items:
                raw_titles = item.get("title") or []
                raw_title = raw_titles[0] if isinstance(raw_titles, list) and raw_titles else (raw_titles if isinstance(raw_titles, str) else "")
                if not raw_title:
                    continue

                doi_raw = item.get("DOI") or ""

                # Ano de publicação
                ano = ""
                for date_field in ("published-print", "published-online", "issued", "created"):
                    parts = (item.get(date_field) or {}).get("date-parts")
                    if parts and parts[0] and parts[0][0]:
                        ano = str(parts[0][0])
                        break

                containers = item.get("container-title") or []
                veiculo = containers[0] if isinstance(containers, list) and containers else (containers if isinstance(containers, str) else "")

                autores = []
                for a in item.get("author", []):
                    given = (a.get("given") or "").strip()
                    family = (a.get("family") or "").strip()
                    name = f"{given} {family}".strip() if (given or family) else (a.get("name") or "").strip()
                    if name:
                        autores.append(clean_text(name))

                obras.append({
                    "titulo": clean_text(raw_title),
                    "doi": clean_doi_display(doi_raw),
                    "ano": ano,
                    "veiculo": clean_text(veiculo),
                    "autores": autores,
                })
    except requests.RequestException as exc:
        logger.warning("Falha na consulta ao CrossRef: %s", exc)
    except Exception as exc:
        logger.warning("Erro inesperado ao processar CrossRef: %s", exc)

    return obras


def buscar_obras_radar(nome_autor: str, orcid: str | None = None, max_results: int = 10) -> list[dict[str, Any]]:
    """Busca obras acadêmicas via OpenAlex e CrossRef, desduplicando por DOI e título.

    Args:
        nome_autor: Nome do autor/pesquisador.
        orcid: ORCID do autor (opcional, ex: '0000-0003-4999-6382').
        max_results: Número máximo de obras a retornar após desduplicação.

    Returns:
        Lista de obras no formato:
        [{"titulo": ..., "doi": ..., "ano": ..., "veiculo": ..., "autores": [...]}, ...]
    """
    candidatas: list[dict[str, Any]] = []

    # 1. Consulta OpenAlex
    openalex_res = _buscar_openalex(nome_autor, orcid, max_results=max_results, timeout=DEFAULT_TIMEOUT)
    candidatas.extend(openalex_res)

    # 2. Consulta CrossRef
    crossref_res = _buscar_crossref(nome_autor, max_results=max_results, timeout=DEFAULT_TIMEOUT)
    candidatas.extend(crossref_res)

    # 3. Normalização e desduplicação
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    obras_unicas: list[dict[str, Any]] = []

    for obra in candidatas:
        norm_doi = normalize_doi(obra.get("doi"))
        norm_title = normalize_title(obra.get("titulo"))

        # Desduplica por DOI
        if norm_doi:
            if norm_doi in seen_dois:
                continue
            seen_dois.add(norm_doi)

        # Desduplica por similaridade de título (chave normalizada)
        if norm_title:
            if norm_title in seen_titles:
                continue
            seen_titles.add(norm_title)

        obras_unicas.append({
            "titulo": obra["titulo"],
            "doi": obra["doi"],
            "ano": obra["ano"],
            "veiculo": obra["veiculo"],
            "autores": obra["autores"],
        })

        if len(obras_unicas) >= max_results:
            break

    return obras_unicas
