"""Leitura de artigos de periódico (PDF ou DOI) para 'Artigos completos publicados em periódicos' do Lattes."""

from __future__ import annotations

import difflib
import re
import urllib.parse
from typing import Any

import requests

from caderno import LATTES_AREAS, name_matches, normalize
from certificado import title_name
from extractor import _clean_line, to_citation_name
from itens.leitura_comum import ano_de_publicacao, corrigir_doi_ocr, titulo_de_pagina, titulo_formatado, titulo_provavel

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
    assuntos = [re.sub(r"\s+", " ", str(s)).strip()[:50] for s in (msg.get("subject") or []) if str(s).strip()]
    if assuntos and not rec.get("palavras_chave"):
        rec["palavras_chave"] = assuntos[:5]  # assuntos do Crossref: melhor que adivinhar pelo título


def pdf_keywords(text: str) -> list[str]:
    """Palavras-chave do PDF: linha 'Keywords:' (+ a próxima só se for continuação da lista)."""
    lines = [ln.strip() for ln in text.splitlines()]
    for i, ln in enumerate(lines):
        m = re.match(r"(?i)^(?:keywords?|palavras[- ]chave|index terms)\s*[:\-–.]\s*(.*)$", ln)  # o OCR às vezes troca ":" por "."
        if not m:
            continue
        block = m.group(1)
        j = i + 1
        while j < len(lines) and j <= i + 2 and lines[j] and (block.rstrip().endswith((",", ";")) or lines[j][:1].islower()):
            block += " " + lines[j]
            j += 1
        block = _clean_line(block)[:300]
        block = re.sub(r"(?<=[a-zà-ú])\.(?=[A-ZÀ-Ú])", "; ", block)  # "Identidade,Mudança.Paradoxo.Teseu": ponto sem espaço separa palavras-chave
        palavras = [k.strip(" .;,-") for k in re.split(r"\s*[;•·,]\s*", block) if 2 < len(k.strip(" .;,-")) < 60][:8]
        return [_corrigir_ocr_palavra(k, text) for k in palavras]
    return []


def _corrigir_ocr_palavra(kw: str, text: str) -> str:
    """Palavra-chave de uma palavra só com letra trocada pelo OCR ("ldennldade"): troca pela palavra parecida que aparece no corpo do texto."""
    if " " in kw or len(kw) < 6:
        return kw
    vocab = {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{6,}", text)}
    if kw.lower() in vocab:
        return kw
    perto = difflib.get_close_matches(kw.lower(), vocab, n=1, cutoff=0.75)
    if not perto:
        return kw
    return perto[0].capitalize() if kw[:1].isupper() else perto[0]


def is_article(text: str) -> bool:
    """Heurística: tem DOI e sinais de artigo (resumo/abstract + palavras-chave ou 'Received/Accepted')."""
    head = text[:6000]
    if not DOI_RE.search(head):
        return False
    low = normalize(head)
    sinais = sum(bool(re.search(p, low)) for p in (
        r"\babstract\b|\bresumo\b", r"keywords?|palavras[- ]chave", r"received|accepted|recebido|aceito",
        r"\bjournal\b|\brevista\b|\bperiodico\b", r"\bintroduction\b|\bintroducao\b",
        r"certificado de publicacao|declaracao de publicacao|publicaram no|publicou o artigo|artigo intitulado"))
    return sinais >= 2


# Rótulos de volume/edição/páginas tolerando OCR: "Voume13", "lssue2" (l no lugar de I), sem espaço entre rótulo e número.
_VOL = r"(?:Vo[l1I]?ume|Vol\.?|v\.)\s*(\d+)"
_EDICAO = r"(?:[Il1]ssue|No\.|n\.|N[uú]mero|Fasc[ií]culo)\s*(\d+)"
_PAGINAS = r"(?:pp?\.|p[aá]ginas?|pages?)\s*([0-9A-Za-z]+)\s*[-–]\s*([0-9A-Za-z]+)"


def _nome_periodico(linha: str) -> str:
    """Nome da revista lido da linha: separa palavras coladas pelo OCR ("interferenceJoumal") e conserta "Journal" mal lido."""
    nome = _clean_line(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", linha)).strip(" ,.;")
    palavras = nome.split()
    if palavras:
        ultima = palavras[-1]
        for certo in ("Journal", "Review", "Revista"):
            minimo = 0.6 if certo == "Journal" and ultima[:2].lower() == "jo" else 0.75  # "Joumaf", "Joumal": OCR troca letras do fim
            if ultima.lower() != certo.lower() and difflib.SequenceMatcher(None, ultima.lower(), certo.lower()).ratio() >= minimo:
                palavras[-1] = certo
                break
    return " ".join(palavras)


def dados_bibliograficos(text: str) -> dict[str, str]:
    """Periódico, volume, número, páginas e ISSN lidos da citação do PDF.

    Aceita 'Revista X, Volume 12, Issue 3, pp. 101-110, 2025. ISSN 0000-0000' e também o nome da revista numa linha e
    'Volume 11, Issue 2 (2025), Page 1856-1871' na seguinte."""
    flat = text[:6000]
    out: dict[str, str] = {}
    m = re.search(r"^[ \t]*([^\n]{4,140}?),\s*" + _VOL, flat, re.M | re.I)
    if m:
        out["periodico"] = _nome_periodico(m.group(1))
    else:  # nome da revista na linha de cima do "Volume N, Issue N"
        linhas = flat.splitlines()
        for k, ln in enumerate(linhas):
            if k and re.match(r"^\s*" + _VOL, ln, re.I) and re.search(_EDICAO + r"|" + _PAGINAS, ln, re.I):
                anterior = _clean_line(linhas[k - 1])
                if 4 <= len(anterior) <= 90 and not re.search(r"\d{3,}|https?://|doi", anterior, re.I):
                    out["periodico"] = _nome_periodico(anterior)
                break
    m = re.search(_VOL, flat, re.I)
    if m:
        out["volume"] = m.group(1)
    m = re.search(_EDICAO, flat, re.I)
    if m:
        out["serie"] = m.group(1)
    m = re.search(_PAGINAS, flat, re.I)
    if m:
        out["pagina_inicial"], out["pagina_final"] = m.group(1), m.group(2)
    m = re.search(r"ISSN[:\s]*([0-9]{4}-[0-9]{3}[0-9Xx])", flat, re.I)
    if m:
        out["isbn_issn"] = m.group(1).upper()
    return out


CABECALHO_RE = re.compile(
    r"(?i)(?<!\w)(issn|e-issn|volume|issue|pages?|p[aá]ginas|doi\.org|https?://|original research article|artigo original)(?!\w)|^comprovante(?!\w)")


def parse_artigo(text: str, usuario: str = "", doi: str = "") -> dict[str, Any]:
    """Monta o registro do artigo. Dados do Crossref (via DOI) têm prioridade; o PDF completa palavras-chave e lacunas."""
    rec = new_artigo()
    notes: list[str] = rec["extraction_notes"]
    text = corrigir_doi_ocr(text)  # DOI quebrado na troca de linha, com espaço depois da barra ou com prefixo estragado pelo OCR
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
            # Faixa de cabeçalho do periódico (selo "COMPROVANTE", nome da revista, volume/ISSN/DOI, tipo do artigo)
            # vem antes do título: começa depois da última linha de metadados dentro das primeiras linhas.
            ultima_meta = max((i for i, ln in enumerate(lines[:8]) if CABECALHO_RE.search(ln)), default=-1)
            if ultima_meta >= 0 and ultima_meta + 1 < len(lines):
                lines = lines[ultima_meta + 1:]
            head: list[str] = []
            for ln in lines[:8]:
                if re.match(r"(?i)^(abstract|resumo|keywords?|palavras)", ln) or (head and re.search(r"\d\s*,|\w\d\b", ln)):
                    break
                head.append(ln)
            pagina = titulo_de_pagina(text)  # página de artigo na web: título depois de "ARTIGO DE REVISÃO"/"Published..."
            rec["titulo"] = titulo_formatado(pagina) if pagina else " ".join(head[:3])
            if len(rec["titulo"].split()) < 4:  # primeira linha era a faixa/logo da revista ("Interference"): procura a linha com cara de título
                rec["titulo"] = titulo_provavel(text) or rec["titulo"]
            # título que só aparece depois do "RESUMO/ABSTRACT" é frase do resumo, não título (página sem a folha de rosto)
            m_res = re.search(r"(?im)^\s*(resumo|abstract)\b", text)
            chave = rec["titulo"][:40]
            if m_res and chave and text.find(chave) > m_res.start():
                rec["titulo"] = ""
                notes.append("O título do artigo não aparece neste documento (só o resumo); preencha o título no formulário.")
            else:
                notes.append("Título tirado do PDF sem DOI; confira.")
        if not rec["ano"]:
            rec["ano"] = ano_de_publicacao(text[:3000])  # ignora faixas de anos e Qualis ("2017-2020")
    if text.strip() and not doi_only(text):
        achados = dados_bibliograficos(text)
        preenchidos = [k for k, v in achados.items() if v and not rec.get(k)]
        for k in preenchidos:
            rec[k] = achados[k]
        if not rec["isbn_issn"] and rec["doi"]:  # DOIs de revistas (Atena, SciELO...) trazem o ISSN logo depois da barra
            m_issn = re.match(r"10\.\d{4,9}/(\d{4}-\d{3}[\dXx])(?![\d-])", rec["doi"])
            if m_issn:
                rec["isbn_issn"] = m_issn.group(1).upper()
                notes.append("ISSN deduzido do DOI; confira.")
        if preenchidos:
            notes.append("Periódico, volume e páginas lidos da citação do documento; confira com a primeira página do artigo.")
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
