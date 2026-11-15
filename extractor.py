"""Extraction and metadata enrichment helpers for Lattes abstracts (Resumos)."""

from __future__ import annotations

import re
import urllib.parse
from collections import Counter
from typing import Any

import pymupdf
import requests


AREA_KEYWORDS = [
    ("Ciências Biológicas", ["ciências biológicas", "ciencias biologicas", "biologia", "biology", "immunology", "microbiology", "parasitology", "physiology", "biochemistry", "pharmacology", "neuroscience", "genetics", "bioquímica", "farmacologia", "enzimas", "peroxidação"]),
    ("Ciências da Saúde", ["ciências da saúde", "ciencias da saude", "medicina", "medicine", "cancer", "clinical", "enfermagem", "farmácia", "odontologia", "saúde pública"]),
    ("Ciências Agrárias", ["ciências agrárias", "ciencias agrarias", "agronomia", "zootecnia", "veterinária", "florestal"]),
    ("Ciências Exatas e da Terra", ["ciências exatas", "matemática", "física", "química", "computação", "estatística"]),
    ("Engenharias", ["engenharia", "engenharias", "automação", "materiais"]),
    ("Ciências Humanas", ["ciências humanas", "educação", "pedagogia", "psicologia", "história", "sociologia"]),
    ("Ciências Sociais Aplicadas", ["ciências sociais aplicadas", "direito", "administração", "economia", "contabilidade"]),
    ("Linguística, Letras e Artes", ["linguística", "letras", "artes", "literatura"]),
]


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> dict[str, Any]:
    """Extract plain text and basic PDF metadata from raw PDF bytes."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pages_text: list[str] = []
    for page in doc:
        pages_text.append(page.get_text("text"))
    full_text = "\n".join(pages_text).strip()
    meta = doc.metadata or {}
    return {
        "text": full_text,
        "page_count": len(doc),
        "pdf_title": (meta.get("title") or "").strip(),
        "pdf_author": (meta.get("author") or "").strip(),
    }


def to_citation_name(full_name: str) -> str:
    """Convert 'Aramys Silva Dos Reis' into Lattes-style 'REIS, A. S.'."""
    cleaned = re.sub(r"[\d¹²³⁴⁵⁶⁷⁸⁹⁰*†‡]+$", "", full_name).strip()
    parts = [p for p in cleaned.split() if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].upper()
    ignore = {"da", "de", "do", "das", "dos", "e"}
    surname = parts[-1].upper()
    initials = [f"{p[0].upper()}." for p in parts[:-1] if p.lower() not in ignore]
    return f"{surname}, {' '.join(initials)}".strip()


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def new_record() -> dict[str, Any]:
    """Registro vazio com os campos de 'Trabalhos em anais de eventos' do Lattes."""
    return {
        "natureza": "Resumo",
        "titulo": "",
        "ano": "",
        "pais": "Brasil",
        "idioma": "Português",
        "meio_divulgacao": "meio digital",
        "homepage": "",
        "doi": "",
        "relevante": "não",
        "divulgacao_cientifica": "não",
        "classificacao_evento": "Local",
        "nome_evento": "",
        "cidade_evento": "",
        "ano_evento": "",
        "titulo_anais": "",
        "volume": "",
        "fasciculo": "",
        "serie": "",
        "pagina_inicial": "",
        "pagina_final": "",
        "isbn_issn": "",
        "editora": "",
        "cidade_editora": "",
        "autores": [],
        "palavras_chave": [],
        "area_conhecimento": "",
        "outras_informacoes": "",
        "visibilidade": "Público",
        "extraction_notes": [],
    }


def parse_evidence_text(text: str, filename: str = "") -> dict[str, Any]:
    """Parse extracted text from a PDF/document into Lattes 'Trabalhos em anais de eventos' fields."""
    raw_lines = [_clean_line(ln) for ln in text.splitlines()]
    lines = [ln for ln in raw_lines if ln]

    result = new_record()

    # Detect DOI
    doi_match = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b", text)
    if doi_match:
        result["doi"] = doi_match.group(1).rstrip(".,;)")

    # Detect ISBN / ISSN
    isbn_match = re.search(r"ISBN[:\s]*([0-9Xx\-]{10,17})", text, re.IGNORECASE)
    if isbn_match:
        result["isbn_issn"] = isbn_match.group(1).strip()
    else:
        issn_match = re.search(r"ISSN[:\s]*(\d{4}-?\d{3}[\dXx])", text, re.IGNORECASE)
        if issn_match:
            result["isbn_issn"] = issn_match.group(1).strip()

    # Detect Natureza
    lower_text = text.lower()
    if "resumo expandido" in lower_text or "extended abstract" in lower_text:
        result["natureza"] = "Resumo Expandido"

    # Detect standalone page number (e.g., line "193" or "p. 193")
    for ln in lines[:4] + lines[-4:]:
        if re.fullmatch(r"\d{1,3}", ln):
            result["pagina_inicial"] = ln
            result["pagina_final"] = ln
            break
        m_pages = re.search(r"(?:p\.?|pp\.?|páginas?)\s*(\d{1,4})(?:\s*[-–]\s*(\d{1,4}))?", ln, re.IGNORECASE)
        if m_pages:
            result["pagina_inicial"] = m_pages.group(1)
            result["pagina_final"] = m_pages.group(2) or m_pages.group(1)
            break

    # Detect Year (20xx)
    year_re = r"\b(20[0-3]\d|199\d)\b"
    years = re.findall(year_re, "\n".join(lines[:15])) or re.findall(year_re, text)
    if years:
        result["ano"] = Counter(years).most_common(1)[0][0]
        result["ano_evento"] = result["ano"]

    # Detect Palavras-chave / Keywords
    kw_match = re.search(
        r"(?:Palavras-?chave|Keywords|Descritores)\s*:\s*(.+?)(?:\n\n|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if kw_match:
        kw_block = " ".join(ln.strip() for ln in kw_match.group(1).splitlines()[:3] if ln.strip() and not ln.strip().isupper())
        kws = [k.strip(" .;,-") for k in re.split(r"[.;,•/]+", kw_block) if k.strip(" .;,-")]
        result["palavras_chave"] = kws[:6]

    # Detect Event name
    event_patterns = [
        r"((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:Seminário|Congresso|Simpósio|Encontro|Jornada|Fórum|Colóquio|Conferência|Workshop)[^\n]{5,140})",
        r"((?:Seminário|Congresso|Simpósio|Encontro|Jornada|Fórum|Conferência|Workshop)\s+(?:Nacional|Internacional|Regional|Brasileiro|de)[^\n]{5,140})",
    ]
    for pat in event_patterns:
        m_ev = re.search(pat, text, re.IGNORECASE)
        if m_ev:
            ev_name = _clean_line(m_ev.group(1))
            result["nome_evento"] = ev_name
            ev_lower = ev_name.lower()
            if "internacional" in ev_lower:
                result["classificacao_evento"] = "Internacional"
            elif "nacional" in ev_lower or "brasileir" in ev_lower:
                result["classificacao_evento"] = "Nacional"
            elif "regional" in ev_lower or "nordeste" in ev_lower or "sudeste" in ev_lower:
                result["classificacao_evento"] = "Regional"
            else:
                result["classificacao_evento"] = "Local"
            break

    # Detect Area of Knowledge
    for area_name, triggers in AREA_KEYWORDS:
        if any(re.search(r"\b" + re.escape(t) + r"\b", lower_text) for t in triggers):
            result["area_conhecimento"] = area_name
            break

    # Detect Title & Authors around "RESUMO" / "INTRODUÇÃO"
    resumo_idx = None
    for idx, ln in enumerate(lines):
        if re.fullmatch(r"(?:RESUMO|ABSTRACT)", ln, re.IGNORECASE):
            resumo_idx = idx
            break

    header_slice = lines[:resumo_idx] if resumo_idx is not None else lines[:12]
    # Filter out obvious page numbers, area footers, or short noise
    filtered_header: list[str] = []
    for ln in header_slice:
        if re.fullmatch(r"\d{1,4}", ln):
            continue
        if any(ln.lower() == a.lower() for a, _ in AREA_KEYWORDS):
            continue
        if result["nome_evento"] and ln in result["nome_evento"]:
            continue
        filtered_header.append(ln)

    # Heuristic: Authors are lines with superscripts (¹, ², *, etc.) or 2-5 capitalized words right before RESUMO
    authors: list[dict[str, str]] = []
    title_lines: list[str] = []
    for ln in filtered_header:
        has_sup = bool(re.search(r"[¹²³⁴⁵⁶⁷⁸⁹⁰*†]\s*$", ln))
        is_uppercase_title = ln.isupper() and len(ln) > 12
        word_count = len(ln.split())
        looks_like_person = (
            not is_uppercase_title
            and 2 <= word_count <= 6
            and all(w[0].isupper() or w.lower() in {"da", "de", "do", "das", "dos", "e"} for w in ln.split() if w)
            and not ln.endswith(":")
        )
        if has_sup or (resumo_idx is not None and looks_like_person and title_lines):
            clean_author = re.sub(r"[\d¹²³⁴⁵⁶⁷⁸⁹⁰*†‡]+$", "", ln).strip(" ,;")
            if clean_author:
                authors.append({"nome": clean_author, "citacao": to_citation_name(clean_author)})
        else:
            if not authors:
                title_lines.append(ln)

    if title_lines:
        raw_title = " ".join(title_lines)
        # Format ALL CAPS title into clean sentence case if needed, preserving acronyms
        if raw_title.isupper():
            raw_title = raw_title[0].upper() + raw_title[1:].lower()
        result["titulo"] = _clean_line(raw_title)

    result["autores"] = authors

    if not result["ano"]:
        result["extraction_notes"].append("Ano não encontrado no documento; use 'Buscar Dados Faltantes'.")
    if not result["isbn_issn"]:
        result["extraction_notes"].append("ISBN/ISSN dos anais não encontrado no documento.")
    if not result["cidade_evento"]:
        result["extraction_notes"].append("Cidade do evento não identificada no documento.")

    return result


def enrich_missing_fields(record: dict[str, Any]) -> dict[str, Any]:
    """Search external academic/web sources (Crossref, OpenAlex, DuckDuckGo) for missing fields."""
    suggestions: dict[str, Any] = {}
    sources: list[str] = []

    doi = (record.get("doi") or "").strip()
    titulo = (record.get("titulo") or "").strip()
    nome_evento = (record.get("nome_evento") or "").strip()

    # 1. Crossref by DOI
    if doi:
        try:
            resp = requests.get(
                f"https://api.crossref.org/works/{urllib.parse.quote(doi)}",
                timeout=8,
                headers={"User-Agent": "LattesFacil/1.0 (mailto:contato@lattesfacil.local)"},
            )
            if resp.ok:
                msg = resp.json().get("message", {})
                if not record.get("titulo") and msg.get("title"):
                    suggestions["titulo"] = msg["title"][0]
                if not record.get("ano"):
                    issued = msg.get("issued", {}).get("date-parts", [[None]])[0]
                    if issued and issued[0]:
                        suggestions["ano"] = str(issued[0])
                        suggestions["ano_evento"] = str(issued[0])
                if not record.get("titulo_anais") and msg.get("container-title"):
                    suggestions["titulo_anais"] = msg["container-title"][0]
                if not record.get("editora") and msg.get("publisher"):
                    suggestions["editora"] = msg["publisher"]
                if not record.get("isbn_issn"):
                    isbns = msg.get("ISBN") or msg.get("ISSN") or []
                    if isbns:
                        suggestions["isbn_issn"] = isbns[0]
                if not record.get("pagina_inicial") and msg.get("page"):
                    pages = str(msg["page"]).split("-")
                    suggestions["pagina_inicial"] = pages[0].strip()
                    suggestions["pagina_final"] = pages[-1].strip()
                sources.append("Crossref API")
        except Exception:
            pass

    # 2. OpenAlex search by title (if still missing key fields)
    if titulo and (not record.get("ano") or not record.get("doi") or not record.get("titulo_anais")):
        try:
            resp = requests.get(
                "https://api.openalex.org/works",
                params={"search": titulo, "per-page": 1},
                timeout=8,
            )
            if resp.ok:
                results = resp.json().get("results", [])
                if results:
                    w = results[0]
                    title_oa = (w.get("title") or "").lower()
                    if titulo[:25].lower() in title_oa or title_oa[:25] in titulo.lower():
                        if not record.get("ano") and w.get("publication_year"):
                            suggestions["ano"] = str(w["publication_year"])
                        if not record.get("doi") and w.get("doi"):
                            suggestions["doi"] = w["doi"].replace("https://doi.org/", "")
                        loc = w.get("primary_location") or {}
                        src = loc.get("source") or {}
                        if not record.get("titulo_anais") and src.get("display_name"):
                            suggestions["titulo_anais"] = src["display_name"]
                        if not record.get("isbn_issn") and src.get("issn_l"):
                            suggestions["isbn_issn"] = src["issn_l"]
                        sources.append("OpenAlex")
        except Exception:
            pass

    # 3. Web search fallback (DuckDuckGo HTML) for event proceedings (ISBN, ano, editora, cidade)
    query_term = nome_evento or titulo
    if query_term and (not record.get("isbn_issn") or not record.get("ano") or not record.get("editora")):
        try:
            q = f"{query_term} anais ISBN"
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": q},
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if resp.ok:
                html_text = re.sub(r"<[^>]+>", " ", resp.text)
                html_text = re.sub(r"\s+", " ", html_text)
                if not record.get("isbn_issn"):
                    m_isbn = re.search(r"\b(97[89][- ]?\d{2}[- ]?\d{4,6}[- ]?\d{2,4}[- ]?\d)\b", html_text)
                    if m_isbn:
                        suggestions["isbn_issn"] = m_isbn.group(1).replace(" ", "-")
                if not record.get("ano"):
                    m_yr = re.search(r"\b(202[0-6])\b", html_text)
                    if m_yr:
                        suggestions["ano"] = m_yr.group(1)
                        suggestions["ano_evento"] = m_yr.group(1)
                if not record.get("editora"):
                    m_ed = re.search(r"\b(EDUFMA|Editora\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç\s]{2,30})\b", html_text)
                    if m_ed:
                        suggestions["editora"] = m_ed.group(1).strip()
                if suggestions:
                    sources.append("Busca Web (Anais)")
        except Exception:
            pass

    return {
        "suggestions": suggestions,
        "sources": sources,
    }
