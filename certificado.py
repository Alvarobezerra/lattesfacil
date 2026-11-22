"""Leitura de certificados de apresentação de trabalho (evidência para 'Apresentação de trabalho' no Lattes)."""

from __future__ import annotations

import re
from typing import Any

from caderno import LATTES_AREAS, PARTICLES, name_matches, normalize
from extractor import _clean_line, to_citation_name

EVENT_WORDS = "Congresso|Simpósio|Simposio|Seminário|Seminario|Encontro|Jornada|Fórum|Forum|Colóquio|Conferência|Workshop|Reunião|Semana"
NATUREZA_POR_EVENTO = [
    ("congresso", "Congresso"), ("simposio", "Simpósio"), ("seminario", "Seminário"),
    ("conferencia", "Conferência ou palestra"), ("palestra", "Conferência ou palestra"),
]
MESES = {m: i + 1 for i, m in enumerate(
    ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"])}


def is_certificate(text: str) -> bool:
    """Certificados começam com 'Certificamos que...' / 'Certificado'; resumos não."""
    head = normalize(text[:600])
    return bool(re.search(r"\bcertific(amos|a-se|ado|amos que)\b", head)) and "palavras-chave" not in head


def new_apresentacao() -> dict[str, Any]:
    return {
        "tipo_producao": "apresentacao",
        "natureza": "Comunicação",
        "titulo": "", "ano": "", "pais": "Brasil", "idioma": "Português", "meio_divulgacao": "meio digital",
        "homepage": "", "relevante": "não", "divulgacao_cientifica": "não",
        "nome_evento": "", "instituicao_promotora": "", "local_evento": "", "cidade_evento": "", "ano_evento": "",
        "autores": [], "palavras_chave": [], "area_conhecimento": "", "outras_informacoes": "",
        "visibilidade": "Público", "extraction_notes": [],
    }


def title_name(name: str) -> str:
    """'ANA KARLLA DOS SANTOS' -> 'Ana Karlla dos Santos'."""
    words = []
    for w in _clean_line(name).split():
        words.append(w.lower() if w.lower() in PARTICLES else w.capitalize())
    return " ".join(words)


def sentence_title(raw: str) -> str:
    """Título em CAIXA ALTA -> caixa de sentença; '(ATTALEA SPECIOSA)' vira '(Attalea speciosa)'."""
    raw = _clean_line(raw)
    if not raw.isupper():
        return raw
    out = raw.lower()
    out = out[:1].upper() + out[1:]

    def binomial(m: re.Match) -> str:
        genus, species = m.group(1).split()
        return f"({genus.capitalize()} {species})"

    return re.sub(r"\(([a-zà-ÿ]{4,} [a-zà-ÿ]{4,})\)", binomial, out)


def _split_names(chunk: str) -> list[str]:
    chunk = _clean_line(chunk)
    parts = re.split(r"\s*,\s*|\s+e\s+(?=[A-ZÀ-Ý][A-Za-zÀ-ÿ])", chunk)
    return [p.strip(" .;") for p in parts if p.strip(" .;")]


def parse_certificado(text: str, usuario: str = "") -> dict[str, Any]:
    flat = _clean_line(text)
    rec = new_apresentacao()
    notes: list[str] = rec["extraction_notes"]

    m = re.search(r"intitulad[oa]\s+['\"“”]([^'\"“”]{3,300})['\"“”]", flat, re.I) or \
        re.search(r"intitulad[oa]\s+(.+?)\s+(?:foi\s+(?:aprovad|apresentad|selecionad)|fo[ir]|apresentad[oa]\s+(?:no|na|em))", flat, re.I)
    if m:
        rec["titulo"] = sentence_title(m.group(1))
        if re.search(r"\([A-ZÀ-Ý]{4,} [A-ZÀ-Ý]{4,}\)", m.group(1)):
            notes.append("Nome científico no título foi escrito como 'Gênero espécie'; confira.")

    m = re.search(rf"\b(?:no|na|do|da|em)\s+((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;]*?\([A-Z0-9]{{2,12}}\))", flat)
    if not m:
        m = re.search(rf"\b(?:no|na|do|da|em)\s+((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;.]{{5,140}})", flat)
    if m:
        rec["nome_evento"] = re.sub(r"\s+em\s+(?:19|20)\d{2}\b.*$", "", _clean_line(m.group(1)), flags=re.I).strip(" ,.")[:255]
        ev = normalize(rec["nome_evento"])
        for key, nat in NATUREZA_POR_EVENTO:
            if key in ev:
                rec["natureza"] = nat
                break
    else:
        notes.append("Nome do evento não identificado no certificado.")

    m = re.search(r"realizad[oa]\s+(?:pel[ao]s?|por)\s+(.+?)(?:,\s*no per[ií]odo|\s+no per[ií]odo|,\s*em\s)", flat, re.I)
    if m:
        promotora = _clean_line(m.group(1))
        j = re.search(r"juntamente com\s+(?:a|o|as|os)\s+(.+)$", promotora, re.I)
        rec["instituicao_promotora"] = (j.group(1) if j else promotora)[:255]

    m = re.search(
        r"per[ií]odo de\s+(\d{1,2})(?:\s+de\s+([a-zçã]+))?\s+a\s+(\d{1,2})\s+de\s+([a-zçã]+)\s+de\s+(\d{4})", flat, re.I)
    if m:
        rec["ano"] = rec["ano_evento"] = m.group(5)
        ini_mes = m.group(2) or m.group(4)
        rec["periodo"] = f"{m.group(1)} de {ini_mes} a {m.group(3)} de {m.group(4)} de {m.group(5)}"
    else:
        y = re.findall(r"\b(20[0-3]\d|199\d)\b", flat)
        if y:
            rec["ano"] = rec["ano_evento"] = y[-1]
        else:
            notes.append("Ano do evento não identificado.")

    m = re.search(r"\bem\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat)
    if m:
        rec["cidade_evento"] = f"{m.group(1).strip()} - {m.group(2)}"
    else:
        m_br = re.search(r"\bem\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*Brasil\b", flat, re.I)
        if m_br:
            rec["cidade_evento"] = m_br.group(1).strip()
        else:
            notes.append("Cidade do evento não identificada.")

    # Papéis e autores
    ori = re.search(r"orientador(?:a)?\s+(.+?)(?:,\s*(?:apresentad)|\s+apresentad)", flat, re.I)
    apr = re.search(r"apresentad[oa]\s+por\s+(.+?)\s+e\s+(?:co-?autoria|coautores?)", flat, re.I) or \
        re.search(r"apresentad[oa]\s+por\s+(.+?)(?:\s+no formato|\.|$)", flat, re.I) or \
        re.search(r"(?:certificamos|declaramos)\s+que\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{4,80}?)\s+(?:participou\b[^.]{0,120}?\be\s+)?(?:apresentou|proferiu)\b", flat, re.I)
    coa = re.search(r"co-?autoria\s+de\s+(.+?)\s+no formato", flat, re.I)
    orientador = title_name(ori.group(1)) if ori else ""
    apresentador = title_name(apr.group(1)) if apr else ""
    coautores = [title_name(n) for n in _split_names(coa.group(1))] if coa else []
    aut = re.search(r"de\s+autoria\s+de\s+(.+?)(?:,\s*foi\s+apresentad|\s+foi\s+apresentad)", flat, re.I)
    if aut and not apresentador and not coautores:
        nomes_aut = [title_name(n) for n in _split_names(aut.group(1))]
        if nomes_aut:
            apresentador, coautores = nomes_aut[0], nomes_aut[1:]

    ordem = [(apresentador, "apresentador")] + [(c, "coautor") for c in coautores] + [(orientador, "orientador")]
    for nome, papel in ordem:
        if nome:
            rec["autores"].append({"nome": nome, "citacao": to_citation_name(nome), "papel": papel})
    if rec["autores"]:
        notes.append("Ordem de autoria assumida: apresentador, coautores e orientador; ajuste se o seu currículo usa outra.")
    else:
        notes.append("Autores não identificados no certificado.")

    # O certificado precisa ser do usuário selecionado
    if usuario:
        achou = next((a for a in rec["autores"] if name_matches(usuario, a["nome"])), None)
        if achou:
            notes.insert(0, f"{usuario} consta neste certificado como {achou['papel']}.")
            rec["papel_usuario"] = achou["papel"]
            # usa a grafia do currículo (o certificado pode omitir partículas, ex.: "Aramys Silva Reis")
            achou["nome"] = usuario
            achou["citacao"] = to_citation_name(usuario)
        else:
            notes.insert(0, f"ATENÇÃO: {usuario} não aparece entre os autores deste certificado. Confira se é o arquivo certo.")

    forma = re.search(r"no formato de\s+(.+?)(?:\.|$)", flat, re.I)
    url = re.search(r"https?://\S+", flat)
    cod = re.search(r"C[óo]digo:\s*([A-Za-z0-9-]+)", flat)
    extra = []
    if forma:
        extra.append(f"Forma de apresentação: {_clean_line(forma.group(1))}.")
    if rec.get("periodo"):
        extra.append(f"Período do evento: {rec['periodo']}.")
    if cod:
        extra.append(f"Certificado código {cod.group(1)}" + (f", validação em {url.group(0).rstrip('.,;')}" if url else "") + ".")
    rec["outras_informacoes"] = " ".join(extra)

    hay = normalize(rec["titulo"])
    areas = [lattes for term, lattes in LATTES_AREAS if re.search(r"\b" + term + r"\b", hay)]
    if areas:
        rec["area_conhecimento"] = "; ".join(areas[:3])
    else:
        notes.append("Áreas e palavras-chave não constam no certificado; preencha no formulário.")
    return rec
