"""Extraction and metadata enrichment helpers for Lattes abstracts (Resumos)."""

from __future__ import annotations

import collections
import difflib
import hashlib
import logging
import re
import threading
import unicodedata
import urllib.parse
from collections import Counter
from typing import Any

import pymupdf
import requests

from ocr_texto import corrigir_espacos, qualidade_texto, restaurar_acentos


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


# Ligaduras que alguns PDFs (SEI, Word) gravam como um só caractere e quebram as buscas por palavra.
_log = logging.getLogger("lattesfacil.ocr")
_OCR_ENGINE: Any = None
_OCR_LOCK = threading.Lock()
_OCR_CACHE: "collections.OrderedDict[str, str]" = collections.OrderedDict()  # sha1 da imagem -> texto lido


def _ocr_engine() -> Any:
    """Uma única instância do RapidOCR por processo (carregar o modelo a cada arquivo é caro)."""
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        from rapidocr_onnxruntime import RapidOCR
        _OCR_ENGINE = RapidOCR()
    return _OCR_ENGINE


def ocr_imagem(png_ou_bytes: bytes) -> str:
    """OCR de uma imagem; devolve o texto com uma linha por trecho reconhecido (preserva as quebras)."""
    chave = hashlib.sha1(png_ou_bytes).hexdigest() if isinstance(png_ou_bytes, (bytes, bytearray)) else None
    if chave and chave in _OCR_CACHE:  # mesma imagem de página já lida (reenvio, junção de arquivos): não refaz o OCR
        _OCR_CACHE.move_to_end(chave)
        return _OCR_CACHE[chave]
    with _OCR_LOCK:  # a sessão onnx compartilhada não deve ser usada por duas requisições ao mesmo tempo
        res, _ = _ocr_engine()(png_ou_bytes)
    texto = restaurar_acentos(corrigir_espacos("\n".join(_juntar_rotulo_e_valor(res or []))))
    if chave:
        _OCR_CACHE[chave] = texto
        while len(_OCR_CACHE) > 300:
            _OCR_CACHE.popitem(last=False)
    return texto


def aquecer_ocr() -> None:
    """Carrega o modelo de OCR em segundo plano (a primeira leitura depois de ligar o servidor gastava ~9 s só nisso)."""
    def _carregar():
        try:
            with _OCR_LOCK:
                _ocr_engine()
        except Exception:
            pass
    threading.Thread(target=_carregar, daemon=True).start()


def _juntar_rotulo_e_valor(res: list) -> list[str]:
    """Linhas do OCR; em tabelas ("Curso:" | "Psicologia") o RapidOCR entrega rótulos e valores em ordem de coluna, longe um do outro.
    Quando uma caixa termina em ':' (rótulo), cola nela a caixa mais próxima À DIREITA na mesma linha visual. Só rótulos são mexidos:
    texto corrido e colunas de artigo continuam na ordem original."""
    itens = []
    for r in res:
        if len(r) > 1 and r[1] and r[1].strip():
            xs, ys = [p[0] for p in r[0]], [p[1] for p in r[0]]
            itens.append({"t": r[1].strip(), "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys), "usado": False})
    for it in itens:
        if it["usado"] or not re.search(r"[:;]$", it["t"]) or len(it["t"]) > 45:
            continue
        melhor = None
        for o in itens:
            if o is it or o["usado"] or o["x0"] < it["x1"] - 4:
                continue
            sobre = min(it["y1"], o["y1"]) - max(it["y0"], o["y0"])
            if sobre < 0.5 * min(it["y1"] - it["y0"], o["y1"] - o["y0"]):
                continue  # não está na mesma linha visual
            gap = o["x0"] - it["x1"]
            if gap <= 6 * max(it["y1"] - it["y0"], 1) and (melhor is None or gap < melhor[0]):
                melhor = (gap, o)
        if melhor and not re.search(r"[:;]$", melhor[1]["t"]):  # o vizinho é valor, não outro rótulo
            it["t"] = it["t"] + " " + melhor[1]["t"]
            melhor[1]["usado"] = True
    return [it["t"] for it in itens if not it["usado"]]


LACUNA_RE = re.compile(r"carga hor[aá]ria\s+(?:de\s+)?(?:horas|h\b|hs\b)|realizad[oa]\s+de\s+a\s|\bno dia\s*[,.]|\bnos dias\s*[,.]|\bperíodo de\s+a\s", re.I)


def _chave_linha(linha: str) -> str:
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", linha).encode("ascii", "ignore").decode().lower())


def mesclar_linhas(base: str, extra: str) -> str:
    """Acrescenta a `base` as linhas de `extra` que não aparecem nela (comparação sem acentos/espaços, tolerante a erro de OCR)."""
    base_linhas = [_chave_linha(ln) for ln in base.splitlines() if ln.strip()]
    base_junta = "".join(base_linhas)
    novas = []
    for ln in extra.splitlines():
        k = _chave_linha(ln)
        if len(k) < 12 or k in base_junta:
            continue
        if any(difflib.SequenceMatcher(None, k, b).ratio() >= 0.8 for b in base_linhas if abs(len(b) - len(k)) <= max(8, len(k) // 3)):
            continue
        novas.append(ln)
    return base + ("\n" + "\n".join(novas) if novas else "")


def ocr_pagina(page: Any) -> str:
    """OCR da página em duas resoluções e união das linhas.

    O RapidOCR perde linhas inteiras de forma diferente conforme a resolução (ex.: a frase com o período do curso sumia a 200 dpi e
    aparecia a 100 dpi). Uma segunda leitura em resolução menor, mais barata, recupera essas linhas.
    """
    alta = ocr_imagem(page.get_pixmap(dpi=200).tobytes("png"))
    try:
        baixa = ocr_imagem(page.get_pixmap(dpi=100).tobytes("png"))
    except Exception:
        return alta
    return mesclar_linhas(alta, baixa)


LIGADURAS = {"\u019f": "ti", "\u01a9": "tt", "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
             "\u01ab": "tt", "\u0183": "ti"}


def corrigir_ligaduras(texto: str) -> str:
    for k, v in LIGADURAS.items():
        texto = texto.replace(k, v)
    return texto


def corrigir_ocr_certificados(texto: str) -> str:
    """Corrige falhas e ruídos típicos de OCR em fontes cursivas/caligráficas e certificados."""
    t = re.sub(r'\b[I1l]{2}\b(?=\s*(?:Jornada|Congresso|Simp[oó]sio|Semin[aá]rio|Encontro|brn|prn|odont))', 'II', texto, flags=re.I)
    t = re.sub(r'\b[I1l]{3}\b(?=\s*(?:Jornada|Congresso|Simp[oó]sio|Semin[aá]rio|Encontro|brn|prn|odont))', 'III', t, flags=re.I)
    t = re.sub(r'\b[I1l]\b(?=\s*(?:Jornada|Congresso|Simp[oó]sio|Semin[aá]rio|Encontro|brn|prn|odont))', 'I', t, flags=re.I)
    # Corrige 'brn ada', 'prn ada', 'brnada', 'prnada' -> Jornada
    t = re.sub(r'\b(?:brn\s*ada|prn\s*ada|brnada|prnada|ornada)\b', 'Jornada', t, flags=re.I)
    # Corrige Odontoligica / Odontolbgica -> Odontológica
    t = re.sub(r'\bodontol[iobg]+ica\b', 'Odontológica', t, flags=re.I)
    # Corrige Mhssoes / Mssoes / dad Missoes -> das Missões
    t = re.sub(r'\b(?:dad|das)\s+M[hs\d]+[oó0]+es\b', 'das Missões', t, flags=re.I)
    # Corrige carga horária: TOhoras, T0horas, 1Ohoras -> 10 horas
    t = re.sub(r'carga\s+hor[aá]ria\s+de\s+[T1I][0O]\s*horas?', 'carga horária de 10 horas', t, flags=re.I)
    return t


def _pagina_escaneada_mal_lida(page: Any, texto: str) -> bool:
    """Página que é basicamente uma imagem (escaneada) cuja camada de texto tem muitas palavras fora do vocabulário."""
    try:
        area = page.rect.width * page.rect.height
        cobre = any(page.get_image_rects(img[0]) and max(r.width * r.height for r in page.get_image_rects(img[0])) >= 0.7 * area
                    for img in page.get_images())
    except Exception:
        return False
    return cobre and len(texto) > 300 and qualidade_texto(texto) < 0.45


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> dict[str, Any]:
    """Extract plain text and basic PDF metadata from raw PDF bytes."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pages_text: list[str] = []
    for i, page in enumerate(doc):
        texto_pag = page.get_text("text")
        # texto nativo com lacunas ("carga horária de   horas/aula, realizado de   a  "): os valores destacados estão em objetos que não
        # entram no texto (anotações/campos). O OCR da página enxerga o que está desenhado e completa o texto.
        if LACUNA_RE.search(texto_pag) and len(doc) <= 15:
            try:
                texto_pag = texto_pag + "\n" + ocr_pagina(page)  # sem dedupe: a linha do OCR com o valor é quase igual à nativa em branco
            except Exception as exc:  # sem OCR segue com o texto nativo
                _log.warning("OCR de página com lacunas falhou: %s", type(exc).__name__)
        elif _pagina_escaneada_mal_lida(page, texto_pag) and len(doc) <= 15:
            # escaneado com camada de texto de OCR ruim: o nosso OCR vem primeiro (os leitores usam a 1ª ocorrência) e o nativo fica de reserva
            try:
                texto_pag = ocr_pagina(page) + "\n" + texto_pag
            except Exception as exc:
                _log.warning("OCR de escaneado mal lido falhou: %s", type(exc).__name__)
        pages_text.append(texto_pag)
    full_text = corrigir_ligaduras("\n".join(pages_text).strip())

    # Fallback automático de OCR para PDFs escaneados, com texto insuficiente ou com apenas metadados/nomes
    texto_limpo = re.sub(r"(?i)powered by tcpdf[^\n]*", "", full_text).strip()
    media_por_pag = len(texto_limpo) / max(len(doc), 1)
    ocr_erro = ""
    if (len(texto_limpo) < 200 or media_por_pag < 90) and len(doc) <= 15:
        try:
            ocr_pages = [ocr_pagina(page) for page in doc]
            ocr_pages = [t for t in ocr_pages if t]
            if ocr_pages:
                ocr_full = corrigir_ligaduras(corrigir_ocr_certificados("\n".join(ocr_pages).strip()))
                if len(ocr_full) > len(texto_limpo):
                    full_text = f"{ocr_full}\n{texto_limpo}" if texto_limpo else ocr_full
        except Exception as exc:  # sem OCR o arquivo segue com o texto nativo, mas o motivo fica registrado
            ocr_erro = f"{type(exc).__name__}: {exc}"[:200]
            _log.warning("OCR falhou: %s", ocr_erro)

    meta = doc.metadata or {}
    return {
        "text": full_text,
        "page_count": len(doc),
        "pdf_title": (meta.get("title") or "").strip(),
        "pdf_author": (meta.get("author") or "").strip(),
        "ocr_erro": ocr_erro,
    }


def extract_text_from_image_bytes(image_bytes: bytes, filename: str = "") -> dict[str, Any]:
    """Extrai texto de arquivos de imagem (PNG, JPG, JPEG, WEBP, BMP, TIFF) via OCR (RapidOCR)."""
    full_text, ocr_erro = "", ""
    try:
        full_text = corrigir_ligaduras(corrigir_ocr_certificados(ocr_imagem(image_bytes).strip()))
    except Exception as exc:
        ocr_erro = f"{type(exc).__name__}: {exc}"[:200]
        _log.warning("OCR de imagem falhou: %s", ocr_erro)

    return {
        "text": full_text,
        "page_count": 1,
        "pdf_title": "",
        "pdf_author": "",
        "ocr_erro": ocr_erro,
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
        kw_block = " ".join(ln.strip() for ln in kw_match.group(1).splitlines()[:3]
                            if ln.strip() and not ln.strip().isupper() and not ln.strip().isdigit())
        kws = [k.strip(" .;,-") for k in re.split(r"[.;,•/]+", kw_block)
               if k.strip(" .;,-") and not re.fullmatch(r"\d+", k.strip(" .;,-"))]
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
        if re.fullmatch(r"(?:RESUMO|ABSTRACT)(?:\s+(?:EXPANDIDO|SIMPLES|ESTENDIDO))?", ln, re.IGNORECASE):
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
        if result["nome_evento"] and ln.lower() in result["nome_evento"].lower():
            continue
        # Faixa de cabeçalho dos anais (selo "COMPROVANTE", título dos anais, volume/ISSN, tipo do trabalho): não é título.
        if re.search(r"(?i)^comprovante\b|\bissn\b|\bvolume\s+\d|^anais d[eo]\b|^trabalho (?:completo|resumido|expandido)\b|publicado em anais", ln):
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
        # Autores numerados em texto simples ("Fulano de Tal 1, Beltrano 2"): vários por linha, afiliação pelo número.
        if title_lines and not authors and not has_sup and re.search(r"[A-Za-zÀ-ÿ.]\s*\d\s*(?:[,;]|$)", ln) and not re.match(r"\d", ln):
            for parte in re.split(r"(?<=\d)\s*[,;]\s*", ln):
                nome = re.sub(r"[\d¹²³⁴⁵⁶⁷⁸⁹⁰*†‡]+$", "", parte).strip(" ,;")
                if nome:
                    authors.append({"nome": nome, "citacao": to_citation_name(nome)})
            continue
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

    # Áreas específicas (as que o autocompletar do Lattes aceita) a partir do título e das palavras-chave.
    # "Ciências Biológicas" e afins são grandes áreas e não são aceitas pelo campo.
    from caderno import LATTES_AREAS, normalize
    hay = normalize(" ".join([result["titulo"]] + result["palavras_chave"]))
    especificas = [lat for term, lat in LATTES_AREAS if re.search(r"\b" + term + r"\b", hay)]
    if especificas:
        result["area_conhecimento"] = "; ".join(especificas[:3])

    # O ano costuma estar só no nome do arquivo (ex.: 2024-SEMICresumo.pdf), pois o resumo traz apenas a folha do caderno.
    if not result["ano"]:
        m_fn = re.match(r"\s*(20[0-3]\d|199\d)(?!\d)", filename or "")
        if m_fn:
            result["ano"] = result["ano_evento"] = m_fn.group(1)
            result["extraction_notes"].append(f"Ano {m_fn.group(1)} deduzido do nome do arquivo; confira.")
    if not result["ano"]:
        result["extraction_notes"].append("Ano não encontrado no documento; use 'Buscar Dados Faltantes'.")
    if not result["isbn_issn"]:
        result["extraction_notes"].append("ISBN/ISSN dos anais não encontrado no documento.")
    if not result["cidade_evento"]:
        result["extraction_notes"].append("Cidade do evento não identificada no documento.")
    if not result["nome_evento"]:
        result["extraction_notes"].append("Nome do evento não consta nesta página (resumo avulso de caderno); envie também a capa/ficha do caderno ou preencha.")

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
