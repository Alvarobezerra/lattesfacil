"""Segmentação de cadernos de resumos (vários trabalhos num único PDF) e busca por pesquisador."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

import pymupdf

from extractor import (
    AREA_KEYWORDS,
    _clean_line,
    new_record,
    to_citation_name,
)

LOWER_WORDS = {"of", "the", "and", "in", "on", "for", "with", "to", "a", "an", "by", "at", "from", "as", "or",
               "de", "da", "do", "das", "dos", "e", "em", "na", "no", "para", "com", "por", "um", "uma"}
PT_STOP = {"de", "da", "do", "que", "para", "com", "uma", "os", "as", "dos", "em", "foi", "são", "ao", "pelo", "pela"}
EN_STOP = {"the", "of", "and", "was", "were", "with", "that", "this", "for", "in", "is", "by", "to", "from", "are"}
KW_RE = re.compile(r"^(?:Keywords?|Palavras-?chave)\s*:\s*(?:(?:Keywords?|Palavras-?chave)\s*:\s*)?", re.IGNORECASE)
# Termos do eixo/título em inglês -> nome exato da área no autocompletar do Lattes (conferidos no formulário real)
LATTES_AREAS = [
    ("immunology", "Imunologia"), ("microbiology", "Microbiologia"), ("parasitology", "Parasitologia"),
    ("pharmacology", "Farmacologia"), ("physiology", "Fisiologia"), ("biochemistry", "Bioquímica"),
    ("genetics", "Genética"), ("cell biology", "Citologia e Biologia Celular"), ("molecular biology", "Biologia Molecular"),
    ("endocrinology", "Endocrinologia"), ("nutrition", "Nutrição"), ("toxicology", "Toxicologia"),
    ("biophysics", "Biofísica"), ("morphology", "Morfologia"), ("ecology", "Ecologia"),
    ("zoology", "Zoologia"), ("botany", "Botânica"),
    # Equivalentes em português (o texto é normalizado, sem acento)
    ("(?:imunologia|imunologic\\w*)", "Imunologia"), ("(?:microbiologia|microbian\\w*)", "Microbiologia"),
    ("(?:parasitologia|parasit\\w*)", "Parasitologia"), ("(?:farmacologia|farmacologic\\w*)", "Farmacologia"),
    ("fisiologia", "Fisiologia"), ("(?:bioquimica|antioxidante\\w*|oxidativo)", "Bioquímica"),
    ("(?:genetica|genomic\\w*)", "Genética"), ("(?:toxicologia|toxicidade)", "Toxicologia"),
    ("(?:extrato\\w*|fitoterap\\w*|planta\\w* medicina\\w*)", "Farmacognosia"),
    ("(?:nutricao|nutricional|farinha|dieta)", "Nutrição"), ("botanica", "Botânica"),
]
AFFIL_RE =re.compile(r"^1\s+\S")
AXIS_RE = re.compile(r"^(\d{1,2})\.\s+(\S.*)$")
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9'’\-]*")


def normalize(text: str) -> str:
    """Minúsculas, sem acentos, espaços colapsados — para comparar nomes."""
    base = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", base).strip().lower()


PARTICLES = {"da", "de", "do", "das", "dos", "e"}


def name_tokens(name: str) -> list[str]:
    """Partes significativas do nome, sem acento/ponto/partículas. Aceita 'Sobrenome, Nome'."""
    name = name.strip()
    if "," in name:
        surname, _, given = name.partition(",")
        name = f"{given} {surname}"
    flat = normalize(name.replace(".", " "))
    return [t for t in re.split(r"[\s\-]+", flat) if t and t not in PARTICLES]


def _tok_eq(q: str, a: str) -> bool:
    """Igualdade de partes de nome, tolerando iniciais ('s' casa com 'silva')."""
    return q == a or (len(q) == 1 and a.startswith(q)) or (len(a) == 1 and q.startswith(a))


def name_matches(query: str, author: str) -> bool:
    """True quando o nome buscado (completo ou abreviado) corresponde ao nome do autor."""
    q = name_tokens(query)
    a = name_tokens(author)
    if not q or not a:
        return False
    if len(q) == 1:
        return q[0] in a
    # primeiro e último nomes precisam bater; as partes do meio podem estar abreviadas ou ausentes no autor
    if not (_tok_eq(q[0], a[0]) and _tok_eq(q[-1], a[-1])):
        return False
    return all(any(_tok_eq(t, x) for x in a) for t in q)


def smart_title(title: str, body: str = "") -> str:
    """Converte título em CAIXA ALTA para caixa de sentença, preservando siglas e nomes próprios que o resumo escreve assim."""
    if not title.isupper():
        return title
    variants: dict[str, Counter] = {}
    for w in WORD_RE.findall(body):
        variants.setdefault(w.lower(), Counter())[w] += 1
    out: list[str] = []
    for i, tok in enumerate(title.split(" ")):
        m = re.match(r"^([^\w]*)(.*?)([^\w]*)$", tok)
        pre, core, suf = m.group(1), m.group(2), m.group(3)
        seen = variants.get(core.lower(), Counter())
        if any(ch.isdigit() for ch in core):
            word = core
        elif len(core) > 1 and seen.get(core):
            word = core  # sigla que aparece em maiúsculas no resumo
        elif seen and seen.most_common(1)[0][1] > seen.get(core.lower(), 0):
            word = seen.most_common(1)[0][0]
        else:
            word = core.lower()
        if i > 0 and core.lower() in LOWER_WORDS:
            word = core.lower()
        out.append(pre + word + suf)
    result = " ".join(out)
    return result[:1].upper() + result[1:]


def parse_authors(block: str) -> list[dict[str, str]]:
    """Divide a linha de autores ('Nome1, Nome Sobrenome1,2, ...') em nomes limpos."""
    block = _clean_line(block)
    names: list[str] = []
    if re.search(r"[A-Za-zÀ-ÿ]\s*\d", block):
        for m in re.finditer(r"\s*([^\d,]+?)\s*\d+(?:\s*,\s*\d+)*\s*(?:,|$)", block):
            names.append(m.group(1).strip(" ,;"))
    else:
        names = [n.strip(" ,;") for n in re.split(r",|;| e ", block) if n.strip(" ,;")]
    authors = []
    for n in names:
        if len(n.split()) >= 1 and n:
            nice = " ".join(w.capitalize() if w.islower() or w.isupper() else w for w in n.split())
            nice = re.sub(r"\b(Da|De|Do|Das|Dos|E)\b", lambda m: m.group(1).lower(), nice)
            authors.append({"nome": nice, "citacao": to_citation_name(nice)})
    return authors


AUTHORS_FULL = re.compile(r"^(?:\s*[^\d,]+?\s*\d+(?:\s*,\s*\d+)*\s*(?:,|$))+$")


def _author_start(lines: list[str], limit: int, strict: bool = False) -> int | None:
    """Índice da primeira linha do bloco de autores (antes da afiliação).

    Modo estrito: o bloco inteiro até 'limit' deve ser 'Nome1, Nome Sobrenome2,3, ...' (vale para caixa alta
    ou baixa). Fora do modo estrito, cai na heurística antiga (linha com nome capitalizado e número colado).
    """
    for i in range(1, limit):
        # a primeira linha do bloco já traz um número de afiliação colado ao nome ("Silva1,"); linhas de
        # título sem número ficam de fora em vez de serem engolidas pelo primeiro autor
        if re.search(r"[A-Za-zÀ-ÿ]\d+(?:\s*,\s*\d+)*\s*(?:,|$)", lines[i]) and AUTHORS_FULL.match(" ".join(lines[i:limit])):
            return i
    if strict:
        return None
    for i in range(limit):
        ln = lines[i]
        if re.match(r"^[A-ZÀ-Ý][a-zà-ÿ]+", ln) and re.search(r"[a-zà-ÿ]\d+(?:\s*,\s*\d+)*\s*(?:,|$)", ln):
            return i
    return limit


def _language(text: str) -> str:
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    pt = sum(w in PT_STOP for w in words)
    en = sum(w in EN_STOP for w in words)
    return "Inglês" if en > pt else "Português"


def parse_abstract_page(text: str, pdf_index: int) -> dict[str, Any] | None:
    """Interpreta uma página de caderno (um resumo por página). Retorna None se não for resumo."""
    raw = [_clean_line(ln) for ln in text.splitlines()]
    lines = [ln for ln in raw if ln]
    kw_idx = next((i for i, ln in enumerate(lines) if KW_RE.match(ln)), None)
    if kw_idx is None or not lines:
        return None

    page_label = ""
    if re.fullmatch(r"\d{1,4}", lines[0]):
        page_label = lines.pop(0)
        kw_idx -= 1
    # A linha de afiliação ("1 Universidade...") vem depois dos autores; um título pode começar com "1 ..."
    # (ex.: "TYPE 1 IN THE"), então só aceitamos a candidata cujo bloco anterior seja uma lista de autores.
    affil_idx = None
    a_start = None
    for cand in [i for i in range(kw_idx) if AFFIL_RE.match(lines[i])]:
        found = _author_start(lines, cand, strict=True)
        if found is not None:
            affil_idx, a_start = cand, found
            break
    if a_start is None:
        a_start = _author_start(lines, kw_idx, strict=True)
        if a_start is None:
            first = next((i for i in range(kw_idx) if AFFIL_RE.match(lines[i])), None)
            affil_idx = first
            a_start = _author_start(lines, first if first is not None else kw_idx)
    head_end = affil_idx if affil_idx is not None else kw_idx
    if a_start == 0 or a_start is None or a_start >= head_end:
        return None

    title_raw = re.sub(r"(?<=\w)-\s+(?=[A-Za-zÀ-ÿ])", "-", " ".join(lines[:a_start]))
    authors = parse_authors(" ".join(lines[a_start:head_end]))
    affiliations = " ".join(lines[head_end:kw_idx]) if affil_idx is not None else ""

    # palavras-chave: podem quebrar linha até a linha do eixo temático
    kw_lines = [lines[kw_idx]]
    j = kw_idx + 1
    while j < len(lines) and not AXIS_RE.match(lines[j]) and j < kw_idx + 3:
        kw_lines.append(lines[j])
        j += 1
    kw_text = KW_RE.sub("", " ".join(kw_lines)).strip()
    keywords = [k.strip(" .;,-") for k in re.split(r"[.;,•]+\s*", kw_text) if k.strip(" .;,-")]

    axis = ""
    body_start = j
    if j < len(lines) and AXIS_RE.match(lines[j]):
        axis = lines[j]
        body_start = j + 1
    body = " ".join(lines[body_start:])

    return {
        "pdf_page": pdf_index + 1,
        "page_label": page_label,
        "titulo": smart_title(_clean_line(title_raw), body + " " + kw_text),
        "autores": authors,
        "afiliacoes": affiliations,
        "palavras_chave": keywords[:6],
        "eixo": axis,
        "idioma": _language(body),
        "resumo_trecho": body[:300],
    }


def parse_front_matter(front_text: str) -> dict[str, str]:
    """Extrai dados gerais do caderno (evento, ISSN, ano, anais) das primeiras páginas."""
    flat = _clean_line(front_text)
    info: dict[str, str] = {}
    m = re.search(r"ISSN\s*(\d{4}-\d{3}[\dXx])", flat)
    if m:
        info["isbn_issn"] = m.group(1)
    m = re.search(r"Volume\s+\d+\s*\((\d{4})\)", flat)
    if m:
        info["ano"] = m.group(1)
    m = re.search(r"\|\s*(10\.\d{4,9}/\S+)", flat)
    if m:
        info["doi"] = m.group(1)
    m = re.search(r"OPEN ACCESS\s+(.+?)\s+(?:Investiga|Volume)", flat)
    if m:
        info["titulo_anais"] = m.group(1).strip()
    m = re.search(r"\(([A-Za-z0-9]{3,12})\)\s+realizou\s+(?:a|o)\s+(.+?)\s+de\s+\d", flat)
    if m:
        sigla, ev = m.group(1), m.group(2).strip()
        info["nome_evento"] = f"{ev} da {sigla}"
    m = re.search(r",\s*em\s+([A-ZÀ-Ý][^,./]{2,40}?)\s*/\s*([A-Z]{2})\b", flat)
    if m:
        info["cidade_evento"] = f"{m.group(1).strip()} - {m.group(2)}"
    # Editora: "ALIES (Associação ... Saúde), Lisbon, Portugal"
    m = re.search(r"\b([A-Z]{3,10})\s*\(([^)]{10,160})\),\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ ]{2,30}),\s*(Portugal|Brasil|Brazil)\b", flat)
    if m:
        sigla, nome, cidade, pais = m.group(1), _clean_line(m.group(2)), m.group(3).strip(), m.group(4)
        info["editora"] = f"{sigla} - {nome}"[:100]
        info["cidade_editora"] = {"Lisbon": "Lisboa"}.get(cidade, cidade)[:30]
        info["pais"] = "Brasil" if pais in ("Brasil", "Brazil") else "Portugal"
    return info


def scan_caderno(pdf_bytes: bytes, pesquisador: str = "") -> dict[str, Any]:
    """Segmenta o caderno em resumos; se 'pesquisador' for dado, devolve só os que o incluem como autor."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        front = "\n".join(doc[i].get_text("text") for i in range(min(3, len(doc))))
        meta = parse_front_matter(front)
        abstracts: list[dict[str, Any]] = []
        for i, page in enumerate(doc):
            item = parse_abstract_page(page.get_text("text"), i)
            if item:
                abstracts.append(item)
        abstracts.sort(key=lambda a: a["pdf_page"])
        total = len(abstracts)
        pesquisador = pesquisador.strip()
        if pesquisador:
            abstracts = [a for a in abstracts if any(name_matches(pesquisador, au["nome"]) for au in a["autores"])]
        return {"meta": meta, "total_resumos": total, "paginas_pdf": len(doc), "resumos": abstracts}
    finally:
        doc.close()


def abstract_to_record(item: dict[str, Any], meta: dict[str, str]) -> dict[str, Any]:
    """Combina resumo + dados do caderno num registro compatível com o formulário Lattes."""
    rec = new_record()
    rec.update(
        {
            "titulo": item["titulo"],
            "autores": item["autores"],
            "palavras_chave": item["palavras_chave"],
            "idioma": item["idioma"],
            "pagina_inicial": item["page_label"],
            "pagina_final": item["page_label"],
            "ano": meta.get("ano", ""),
            "ano_evento": meta.get("ano", ""),
            "nome_evento": meta.get("nome_evento", ""),
            "cidade_evento": meta.get("cidade_evento", ""),
            "titulo_anais": meta.get("titulo_anais", ""),
            "isbn_issn": meta.get("isbn_issn", ""),
            "pais": meta.get("pais", "Brasil"),
            "editora": meta.get("editora", ""),
            "cidade_editora": meta.get("cidade_editora", ""),
        }
    )
    if meta.get("doi"):
        # O DOI do caderno identifica o volume, não o resumo: vai como link do trabalho, não no campo DOI.
        rec["homepage"] = "https://doi.org/" + meta["doi"]
        rec["extraction_notes"].append("Home page = DOI do volume do caderno (não é DOI individual do resumo); apague se preferir.")
    if meta.get("pais") == "Portugal":
        rec["extraction_notes"].append("País da publicação = Portugal (sede da editora); confirme.")
    if meta.get("nome_evento"):
        low = meta["nome_evento"].lower()
        rec["classificacao_evento"] = (
            "Internacional" if "internacional" in low else "Regional" if "regional" in low else "Nacional"
        )
    hay = normalize(item["titulo"] + " " + " ".join(item["palavras_chave"]) + " " + item["eixo"])
    areas = [lattes for term, lattes in LATTES_AREAS if re.search(r"\b" + term + r"\b", hay)]
    if areas:
        rec["area_conhecimento"] = "; ".join(areas[:3])
    else:
        for area, triggers in AREA_KEYWORDS:  # só dica de grande área; o Lattes exige área específica
            if any(re.search(r"\b" + re.escape(normalize(t)) + r"\b", hay) for t in triggers):
                rec["area_conhecimento"] = area
                rec["extraction_notes"].append(f"Grande área sugerida ({area}); no Lattes escolha uma área específica.")
                break
    if item["eixo"]:
        rec["outras_informacoes"] = "Eixo temático: " + re.sub(r"^\d+\.\s*", "", item["eixo"])
    if not rec["editora"]:
        rec["extraction_notes"].append("Editora e cidade da editora não constam no caderno; use 'Buscar Dados Faltantes'.")
    if not rec["doi"]:
        rec["extraction_notes"].append("DOI individual do resumo não consta no caderno.")
    return rec
