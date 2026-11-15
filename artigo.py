"""Leitura de artigos de periódico (PDF ou DOI) para 'Artigos completos publicados em periódicos' do Lattes."""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

import requests

from caderno import LATTES_AREAS, name_matches, normalize
from certificado import title_name
from extractor import _clean_line, to_citation_name

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", re.I)
DOI_ONLY_RE = re.compile(r"^\s*(?:doi:\s*|https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/\S+?)\s*[.,;]?\s*$", re.I)
LANGS = {"en": "Inglês", "pt": "Português", "es": "Espanhol", "fr": "Francês", "de": "Alemão", "it": "Italiano"}
USER_AGENT = "LattesFacil/1.0"


def new_artigo() -> dict[str, Any]:
    return {
        "tipo_producao": "artigo",
        "titulo": "", "ano": "", "idioma": "Português", "meio_divulgacao": "meio digital", "homepage": "",
        "doi": "", "periodico": "", "isbn_issn": "", "volume": "", "serie": "", "pagina_inicial": "", "pagina_final": "",
        "relevante": "não", "divulgacao_cientifica": "não",
        "autores": [], "palavras_chave": [], "area_conhecimento": "", "outras_informacoes": "",
        "visibilidade": "Público", "extraction_notes": [],
    }


def doi_only(text: str) -> str:
    """Se o texto colado é só um DOI (ou link doi.org), devolve o DOI; senão ''. """
    m = DOI_ONLY_RE.match(text or "")
    return m.group(1).rstrip(".,;)") if m else ""


def clean_doi(raw: str) -> str:
    return raw.strip().rstrip(".,;)")


def fetch_crossref(doi: str, timeout: int = 10) -> dict[str, Any] | None:
    """Metadados oficiais do DOI no Crossref (título, autores, periódico, ISSN, volume, páginas, ano)."""
    try:
        r = requests.get(
            "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"),
            timeout=timeout, headers={"User-Agent": USER_AGENT},
        )
        if r.ok:
            return r.json().get("message")
    except requests.RequestException:
        return None
    return None


def _crossref_year(msg: dict[str, Any]) -> str:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return ""


def _fix_case(name: str) -> str:
    """Corrige nomes TODO EM CAIXA ALTA ou todos em minúsculas; mantém os demais."""
    return title_name(name) if (name.isupper() or name.islower()) else name


def apply_crossref(rec: dict[str, Any], msg: dict[str, Any]) -> None:
    title = (msg.get("title") or [""])[0]
    if title:
        rec["titulo"] = _clean_line(re.sub(r"<[^>]+>", "", title))
    rec["ano"] = _crossref_year(msg) or rec["ano"]
    rec["periodico"] = (msg.get("container-title") or [""])[0] or rec["periodico"]
    issns = msg.get("ISSN") or []
    if issns:
        rec["isbn_issn"] = issns[0]
    rec["volume"] = str(msg.get("volume") or "")
    rec["serie"] = str(msg.get("issue") or "")
    page = str(msg.get("page") or msg.get("article-number") or "")
    if page:
        parts = re.split(r"\s*[-–]\s*", page)
        rec["pagina_inicial"] = parts[0]
        rec["pagina_final"] = parts[1] if len(parts) > 1 else ""
    lang = LANGS.get((msg.get("language") or "").lower())
    if lang:
        rec["idioma"] = lang
    authors = []
    for a in msg.get("author") or []:
        given, family = (a.get("given") or "").strip(), (a.get("family") or "").strip()
        nome = _clean_line(f"{_fix_case(given)} {_fix_case(family)}".strip()) or _clean_line(a.get("name") or "")
        if nome:
            authors.append({"nome": nome, "citacao": to_citation_name(nome)})
    if authors:
        rec["autores"] = authors
    if msg.get("URL"):
        rec["homepage"] = msg["URL"]


def pdf_keywords(text: str) -> list[str]:
    """Palavras-chave do PDF: linha 'Keywords:' (+ a próxima só se for continuação da lista)."""
    lines = [ln.strip() for ln in text.splitlines()]
    for i, ln in enumerate(lines):
        m = re.match(r"(?i)^(?:keywords?|palavras[- ]chave|index terms)\s*[:\-–]\s*(.*)$", ln)
        if not m:
            continue
        block = m.group(1)
        j = i + 1
        while j < len(lines) and j <= i + 2 and lines[j] and (block.rstrip().endswith((",", ";")) or lines[j][:1].islower()):
            block += " " + lines[j]
            j += 1
        block = _clean_line(block)[:300]
        return [k.strip(" .;,-") for k in re.split(r"\s*[;•·,]\s*", block) if 2 < len(k.strip(" .;,-")) < 60][:8]
    return []


def is_article(text: str) -> bool:
    """Heurística: tem DOI e sinais de artigo (resumo/abstract + palavras-chave ou 'Received/Accepted')."""
    head = text[:6000]
    if not DOI_RE.search(head):
        return False
    low = normalize(head)
    sinais = sum(bool(re.search(p, low)) for p in (
        r"\babstract\b|\bresumo\b", r"keywords?|palavras[- ]chave", r"received|accepted|recebido|aceito",
        r"\bjournal\b|\brevista\b|\bperiodico\b", r"\bintroduction\b|\bintroducao\b"))
    return sinais >= 2


def parse_artigo(text: str, usuario: str = "", doi: str = "") -> dict[str, Any]:
    """Monta o registro do artigo. Dados do Crossref (via DOI) têm prioridade; o PDF completa palavras-chave e lacunas."""
    rec = new_artigo()
    notes: list[str] = rec["extraction_notes"]
    doi = clean_doi(doi or (DOI_RE.search(text[:8000]).group(1) if DOI_RE.search(text[:8000]) else ""))
    rec["doi"] = doi
    msg = fetch_crossref(doi) if doi else None
    if msg:
        apply_crossref(rec, msg)
        notes.append("Dados do artigo conferidos no Crossref pelo DOI; o Lattes também os recupera sozinho ao informar o DOI.")
        notes.append("No Lattes os autores vêm do DOI e o seu nome é ligado pelas 'citações bibliográficas' do currículo; se não casar, o Lattes avisa.")
    elif doi:
        notes.append("Não consegui consultar o DOI no Crossref (sem internet ou DOI inexistente); revise os campos.")
    else:
        notes.append("DOI não encontrado: sem ele o periódico precisa ser escolhido manualmente no Lattes (lupa do periódico).")

    if text.strip() and not doi_only(text):
        rec["palavras_chave"] = pdf_keywords(text)
        if not rec["titulo"]:
            lines = [_clean_line(ln) for ln in text.splitlines() if _clean_line(ln)]
            head: list[str] = []
            for ln in lines[:8]:
                if re.match(r"(?i)^(abstract|resumo|keywords?|palavras)", ln) or (head and re.search(r"\d\s*,|\w\d\b", ln)):
                    break
                head.append(ln)
            rec["titulo"] = " ".join(head[:3])
            notes.append("Título tirado do PDF sem DOI; confira.")
        if not rec["ano"]:
            years = re.findall(r"\b(19[89]\d|20[0-3]\d)\b", text[:3000])
            if years:
                rec["ano"] = years[0]
    if not rec["palavras_chave"]:
        notes.append("Palavras-chave não encontradas; preencha no formulário.")

    if rec["autores"] and usuario:
        achou = next((i for i, a in enumerate(rec["autores"]) if name_matches(usuario, a["nome"])), None)
        if achou is None:
            notes.insert(0, f"ATENÇÃO: {usuario} não aparece entre os autores deste artigo. Confira se é o artigo certo.")
        else:
            pos = achou + 1
            notes.insert(0, f"{usuario} é o autor {pos} de {len(rec['autores'])} neste artigo.")
            rec["autores"][achou]["nome"] = usuario  # grafia do currículo
            rec["autores"][achou]["citacao"] = to_citation_name(usuario)
    elif not rec["autores"]:
        notes.append("Autores não obtidos; adicione no formulário.")

    hay = normalize(rec["titulo"] + " " + " ".join(rec["palavras_chave"]))
    areas = [lat for term, lat in LATTES_AREAS if re.search(r"\b" + term + r"\b", hay)]
    if areas:
        rec["area_conhecimento"] = "; ".join(areas[:3])
    else:
        notes.append("Área do conhecimento não identificada; preencha no formulário.")
    return rec
