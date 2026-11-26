"""Auxiliares de leitura compartilhados pelos leitores: valor por rótulo, pares de datas e datas que não são do documento.

Surgiram do controle positivo (leitura visual das imagens × saída do sistema, 25/11/2026): os mesmos tipos de erro aparecem
em vários documentos, então ficam aqui em vez de remendos por caso.
"""
from __future__ import annotations

import difflib
import re
import unicodedata

MESES = {"janeiro": "01", "fevereiro": "02", "marco": "03", "abril": "04", "maio": "05", "junho": "06", "julho": "07",
         "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"}
Data = tuple[str, str, str]  # (dia, mês 'MM', ano)


def _n(t: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower().split())


# Leis, portarias, decretos etc.: o ano/data que vem junto é da norma, não do fato que o documento comprova
# (ex.: "Lei nº 11.788, de 25 de setembro de 2008", "Portaria nº 195 Data da Portaria: 22/03/2018 D.O.U ...").
_NORMA = re.compile(
    r"(?<![A-Za-zÀ-ÿ])(?:lei|decreto|portaria|resolu[çc][ãa]o|instru[çc][ãa]o normativa|medida provis[óo]ria|d\.o\.u\.?|di[áa]rio oficial)(?![A-Za-zÀ-ÿ])"
    r"(?:\s+(?:complementar|federal|estadual|reitoria|mec|normativa|presidencial|ministerial|interministerial))?\s*(?:n[º°o.]*\s*)?[\d./-]*"
    r"(?:[^;\n]{0,45}?(?:data da portaria\s*:?\s*)?(?:de\s+\d{1,2}\s+de\s+[A-Za-zçÇãÃéÉ]+\s+de\s+\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}))?",
    re.I)


def sem_referencias_legais(flat: str) -> str:
    """Troca por espaço as citações de normas, que trazem datas alheias ao documento."""
    flat = _NORMA.sub(" ", flat)
    # ato numerado com ano ("Parecer nº 64/2004", "nº 12/2010"): o ano é do ato, não do documento
    return re.sub(r"(?i)(?:parecer|nota t[ée]cnica|ato|ofício|oficio|instru[çc][ãa]o|parecer cne/ceb)?\s*n[º°o]\.?\s*\d{1,5}\s*/\s*(?:19|20)\d{2}", " ", flat)


def _data(m_dia: str, mes: str, ano: str) -> Data | None:
    mm = MESES.get(_n(mes)) if not mes.isdigit() else mes.zfill(2)
    if not mm or not 1 <= int(mm) <= 12:
        return None
    return (m_dia.zfill(2), mm, ano)


_DATA_RX = r"(\d{1,2})(?:\s*(?:º|°))?(?:\s+de\s+([A-Za-zçÇãÃéÉ]+)\s+de\s+|/(\d{1,2})/)(\d{4})"
_SEP = (r"(?:\s*(?:,|;|\be\b|\ba\b|à|at[eé]|-|–))*\s*"
        r"(?:(?:t[eé]rmino|encerramento|fim|final)(?:\s+d[oae]\s+\w+)?\s*(?:em\s*)?:?\s*)?")


def par_de_datas(flat: str) -> tuple[Data, Data] | None:
    """Início e fim de um período escrito com datas completas.

    Aceita "no período de 15 de março de 2024 a 22 de fevereiro de 2025", "de 01/07/2024 a 31/12/2024",
    "início em 01/07/2024 e término em 31/12/2024", "INÍCIO ESTÁGIO: 01/07/2024 ENCERRAMENTO DO ESTÁGIO: 31/12/2024".
    """
    t = sem_referencias_legais(flat)
    pat = (rf"(?:per[ií]odo\s+de|de|desde|in[ií]cio(?:\s+d[oae]\s+\w+)?(?:\s+(?:est[aá]gio|vig[eê]ncia|contrato|v[ií]nculo|curso|atividades?))?(?:\s+em)?\s*:?|a partir de)\s*{_DATA_RX}"
           rf"{_SEP}{_DATA_RX}")
    m = re.search(pat, t, re.I)
    if not m:
        return None
    g = m.groups()
    ini = _data(g[0], g[1] or g[2], g[3])
    fim = _data(g[4], g[5] or g[6], g[7])
    return (ini, fim) if ini and fim else None


def valor_do_rotulo(texto: str, rotulos: tuple[str, ...] | list[str]) -> str:
    """Valor de um campo rotulado ('CURSO: X'), com o valor na mesma linha ou na seguinte.

    O texto extraído de PDF costuma separar rótulo e valor em linhas diferentes; a linha seguinte só vale se não for ela mesma
    outro rótulo (termina em ':' ou é 'PALAVRA(S) EM CAIXA ALTA:' no começo).
    """
    linhas = [ln.strip() for ln in texto.splitlines()]
    for rot in rotulos:
        rx = re.compile(r"^\W*([^:;]{2,45})\s*[:;]\s*(.*)$")
        alvo = re.sub(r"[^a-z0-9]", "", _n(rot))
        for i, ln in enumerate(linhas):
            m = rx.match(ln)
            if not m:
                continue
            # rótulo igual ou muito parecido (OCR: "Curse", "Matrlcula", "Perlodo")
            cand = re.sub(r"[^a-z0-9]", "", _n(m.group(1)))
            if not cand or (cand != alvo and (len(alvo) < 5 or difflib.SequenceMatcher(None, cand, alvo).ratio() < 0.82)):
                continue
            val = m.group(2).strip()
            if val and not _parece_rotulo(val):
                return val
            if not val:
                for prox in linhas[i + 1:i + 3]:
                    if prox and not _parece_rotulo(prox):
                        return prox
                    if prox:
                        break
    return ""


def _parece_rotulo(linha: str) -> bool:
    """Linha que é só outro rótulo ('AUTORIZAÇÃO:', 'RECONHECIMENTO: RENOVAÇÃO: Conclusão em:')."""
    if re.fullmatch(r"[A-ZÀ-Ý][A-Za-zÀ-ÿ/ ]{2,40}:", linha.strip()):
        return True
    if re.match(r"(?i)\W*(autoriza[çc][ãa]o|reconhecimento|renova[çc][ãa]o|portaria|decreto|resolu[çc][ãa]o)\b", linha):
        return True  # linha de ato legal do curso, não o valor do rótulo anterior
    return bool(re.match(r"^[A-ZÀ-Ý][A-ZÀ-Ý/ ]{3,30}:\s", linha)) and linha.count(":") >= 2


def valor_na_secao(texto: str, secao: tuple[str, ...] | list[str], rotulo: str, alcance: int = 12) -> str:
    """Valor de `rotulo` na primeira ocorrência depois do cabeçalho de seção ('CONCEDENTE' ... 'RAZÃO SOCIAL: X')."""
    linhas = texto.splitlines()
    for i, ln in enumerate(linhas):
        if any(re.match(rf"^\W*{re.escape(s)}\W*$", ln.strip(), re.I) for s in secao):
            val = valor_do_rotulo("\n".join(linhas[i + 1:i + 1 + alcance]), (rotulo,))
            if val:
                return val
    return ""


# ---------------------------------------------------------------- páginas de web/livro (capturas de tela, capítulos)
_LIXO_PAGINA = re.compile(
    r"planned intervention|skip to|cookie|scanned with|camscanner|^(?:in[ií]cio|home)\s*/|orcid|https?:|^\W*(?:open|menu|login|entrar)\W*$|"
    r"^version\s*v?\d|^published\b|^journal article|^\d{1,3}$", re.I)
_CUE_TITULO = re.compile(
    r"^\W*(?:artigo|article)\s*(?:de\s*)?(?:te[óo]rico|revis[ãa]o|original|cient[ií]fico|review|research)\W*$|^published\b|^journal article|^cap[ií]tulo\s*\d+\W*(?:[-–:]\W*)?$", re.I)
_INGLES = re.compile(r"\b(?:of|and|the|on|in|for|with|among|between|from)\b", re.I)


def _parece_nome(linha: str) -> bool:
    """'Alexandre Ribeiro Borges': 2 a 6 palavras iniciadas por maiúscula e com minúsculas (título em CAIXA ALTA não é nome)."""
    ps = linha.split()
    if len(ps) == 1:  # OCR sem espaços: 'MarceladeMariaPereiraTeixeira'
        return len(linha) >= 14 and len(re.findall(r"[a-zà-ÿ][A-ZÀ-Ý]", linha)) >= 2
    particulas = {"de", "da", "do", "dos", "das", "e"}
    # nome próprio: palavras em Título (inicial maiúscula, resto minúsculo); 'TRANSFUSAO SANGUiNEA:' (CAIXA ALTA com erro de OCR) não é
    return 2 <= len(ps) <= 6 and all(p.lower() in particulas or (p[0].isupper() and p[1:].replace(".", "").islower()) for p in ps)


def titulo_de_pagina(texto: str) -> str:
    """Título de uma página de artigo na web ou de um capítulo de livro, ignorando faixas de site, avisos e metadados.

    O título vem depois de uma pista ('ARTIGO DE REVISÃO', 'Published ...', 'CAPÍTULO 9') e vai até o primeiro autor, link, DOI ou trecho
    em inglês (tradução do título). Devolve '' quando não há pista.
    """
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    achado = ""
    for i, ln in enumerate(linhas[:400]):
        if not _CUE_TITULO.search(ln):
            continue
        partes: list[str] = []
        if re.match(r"(?i)^cap[ií]tulo\s*\d+\W*[-–:]\s*\S", ln):  # "CAPÍTULO 11 - TÍTULO" já na mesma linha
            partes.append(re.sub(r"(?i)^cap[ií]tulo\s*\d+\W*[-–:]\s*", "", ln))
        for prox in linhas[i + 1:i + 14]:
            if _LIXO_PAGINA.search(prox) and not partes:
                continue  # metadados entre a pista e o título (Published, Journal article, Open, Version v1)
            if _LIXO_PAGINA.search(prox) or re.match(r"^10\.\d{4,}/", prox) or _parece_nome(prox) or len(_INGLES.findall(prox)) >= 2 \
                    or re.search(r"(?i)universidade|instituto|doi\b|graduand|mestrand", prox):
                break
            partes.append(prox)
        titulo = " ".join(partes).strip(" -–:")
        if len(titulo) >= 12:
            achado = titulo  # vale a ÚLTIMA pista: em livro, o sumário vem antes da página do capítulo
    return achado


def unir_doi_quebrado(texto: str) -> str:
    """Junta o DOI que o PDF/OCR quebrou na troca de linha ('.../reaid-2026-v.100-n.2-' + 'art.2742')."""
    return re.sub(r"(10\.\d{4,9}/[^\s]*[-./_])[ \t]*\r?\n[ \t]*([A-Za-z0-9][^\s]*)", r"\1\2", texto)


def titulo_formatado(titulo: str) -> str:
    """CAIXA ALTA (mesmo com erro de OCR em 1–2 letras, 'SANGUiNEA') -> caixa de sentença; título já misto fica como está."""
    from certificado import sentence_title
    letras = [c for c in titulo if c.isalpha()]
    if letras and sum(c.isupper() for c in letras) / len(letras) >= 0.8:
        return sentence_title(titulo.upper())
    return titulo


# ---------------------------------------------------------------- artigos: DOI, ano e título em OCR de páginas de revista
def corrigir_doi_ocr(texto: str) -> str:
    """Conserta DOI que o OCR estragou: quebra de linha, espaço depois da barra ('10.34119/ bjhr...') e prefixo ('doi.orm0.23900/')."""
    t = unir_doi_quebrado(texto)
    t = re.sub(r"(10\.\d{4,9}/)[ \t]+(?=\S)", r"\1", t)
    t = re.sub(r"(?i)doi\.?\s*or[a-z]?\s*[o0]?\.?\s*(\d{4,5}/)", r"doi.org/10.\1", t)
    return t


_MES_ABREV = r"(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-z]*"


def ano_de_publicacao(texto: str) -> str:
    """Ano do artigo ignorando faixas de anos e indicadores de avaliação ('QUALIS 2017-2020', 'Sucupira'), que não são a data da publicação."""
    t = re.sub(r"(?i)(?:qualis|sucupira|quadri[êe]nio)[^\n]{0,40}", " ", texto)
    t = re.sub(r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)?\d{2,4}\b", " ", t)
    for pat in (r"(?i)(?:publicad[oa](?: em)?|published(?: on)?|publica[çc][ãa]o|edi[çc][ãa]o)[^\n]{0,40}?(?<!\d)(20[0-3]\d)(?!\d)",
                rf"(?i)\b{_MES_ABREV}\W{{0,3}}(20[0-3]\d)\b", r"\b\d{1,2}/\d{1,2}/(20[0-3]\d)\b",
                r"(?i)(?:recebido|aceito|received|accepted|submitted|approved)[^\n]{0,40}?(?<!\d)(20[0-3]\d)(?!\d)", r"\bv\.?\s*\d+\s*,?\s*n\.?\s*\d+\s*[,(]?\s*(20[0-3]\d)\b"):
        m = re.search(pat, t)
        if m:
            return m.group(1)
    m = re.search(r"\b(20[0-3]\d|199\d)\b", t)
    return m.group(1) if m else ""


_BANNER_ARTIGO = re.compile(
    r"(?i)journal|revista|issn|qualis|sucupira|\bdoi\b|volume|issue|vol\.|submitted|approved|received|accepted|copyright|universidade|faculdade|"
    r"graduand|e-mail|@|https?:|orcid|published|publicado|resumo|abstract|palavras|keywords|artigo|article|^\W*\d")


def _linha_autor(linha: str) -> bool:
    """Linha de autor(es) com índices de afiliação: 'Maria da Silva Souza1'."""
    limpa = re.sub(r"[\d¹²³⁴⁵⁶⁷⁸⁹⁰*,;]+", " ", linha).strip()
    return bool(limpa) and _parece_nome(re.sub(r"\s+", " ", limpa))


def titulo_provavel(texto: str) -> str:
    """Linha com cara de título (>= 5 palavras, sem faixa de revista, afiliação, e-mail ou nome de autor) nas primeiras linhas.

    Entre várias candidatas, vale a que vem seguida de uma linha de autores (o título de artigo precede os autores); as faixas de evento
    e de revista não têm autores logo depois.
    """
    linhas = [x.strip() for x in texto.splitlines() if x.strip()][:30]
    candidatas = {i for i, ln in enumerate(linhas) if len(ln.split()) >= 5 and len(ln) >= 30 and not _BANNER_ARTIGO.search(ln) and not _parece_nome(ln)}
    ia = next((i for i, ln in enumerate(linhas) if i > 0 and _linha_autor(ln)), None)
    if ia is not None and (ia - 1) in candidatas:
        j, partes = ia - 1, [linhas[ia - 1]]
        # título quebrado em linhas: junta a anterior quando ela termina "no ar" (conector, dois-pontos, hífen)
        while j - 1 in candidatas and re.search(r"(?i)(\bde|\bda|\bdo|\be|\bem|\bna|\bno|\ba|\bo|:|-|,)$", linhas[j - 1]) and len(partes) < 4:
            j -= 1
            partes.insert(0, linhas[j])
        return " ".join(partes)
    return linhas[min(candidatas)] if candidatas else ""
