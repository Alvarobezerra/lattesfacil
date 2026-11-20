"""Leitura de evidências de orientação (declaração, ata de defesa, certificado) para 'Orientações e supervisões' do Lattes."""

from __future__ import annotations

import re
from typing import Any

from caderno import LATTES_AREAS, name_matches, normalize
from certificado import title_name
from extractor import _clean_line, to_citation_name
from itens.sugestoes import areas_do_texto, palavras_chave

NATUREZAS = [
    # (padrão no texto normalizado, nome da natureza no formulário)
    (r"disserta[cç][aã]o|mestrado|mestrand", "Dissertação de mestrado"),
    (r"tese\b|doutorado|doutorand", "Tese de doutorado"),
    (r"especializa[cç][aã]o|aperfei[cç]oamento", "Monografia de conclusão de curso de aperfeiçoamento/especialização"),
    (r"trabalho de conclus[aã]o de curso|\btcc\b|monografia|gradua[cç][aã]o", "Trabalho de conclusão de curso de graduação"),
    (r"inicia[cç][aã]o cient[ií]fica|\bpibic\b|\bpibiti\b|\bpivic\b", "Iniciação Científica"),
    (r"p[oó]s-?doutorado|supervis[aã]o", "Supervisão de pós-doutorado"),
]
INST_RE = re.compile(
    r"((?:Universidade|Instituto Federal|Faculdade|Centro Universit[aá]rio|Escola Superior|Funda[cç][aã]o)\s+[A-ZÀ-Ý][^,.;\n()]{3,70}?)(?=\s*(?:\(|,|\.|;|-|–|\n|$|\s+em\s|\s+no\s|\s+na\s))")


# Nome próprio: palavras capitalizadas, com partículas (da, de, dos...) no meio.
NAME = r"((?:[A-ZÀ-Ý][\wÀ-ÿ'’-]*)(?:\s+(?:d[aeo]s?\s+|e\s+)?[A-ZÀ-Ý][\wÀ-ÿ'’-]*){1,7})"
PROF = r"\s*(?:(?i:Prof\w*)\.?\s*)?(?:(?i:Dr\w*)\.?\s*)*"


def is_orientacao(text: str) -> bool:
    low = normalize(text[:5000])
    tem_papel = bool(re.search(r"\b(?:co-?)?orientador|\b(?:co-?)?orientou|\b(?:co-?)?orientac|\b(?:co-?)?orientand|banca examinadora|\bdefesa\b|\bdefendid", low))
    tem_natureza = any(re.search(p, low) for p, _ in NATUREZAS)
    return tem_papel and tem_natureza


def new_orientacao() -> dict[str, Any]:
    return {
        "tipo_producao": "orientacao", "natureza": "", "situacao_orientacao": "Concluída", "papel_orientacao": "Orientador principal",
        "tipo_mestrado": "", "titulo": "", "ano": "", "pais": "Brasil", "idioma": "Português", "homepage": "",
        "nome_orientando": "", "instituicao_orient": "", "curso_orient": "", "relevante": "Não", "bolsa": "Não", "agencia_financiadora": "",
        "autores": [], "palavras_chave": [], "area_conhecimento": "", "outras_informacoes": "",
        "visibilidade": "Público", "extraction_notes": [],
    }


def _name(raw: str) -> str:
    raw = _clean_line(raw).strip(" .;:,-")
    return title_name(raw) if (raw.isupper() or raw.islower()) else raw


def parse_orientacao(text: str, usuario: str = "") -> dict[str, Any]:
    flat = _clean_line(text)
    low = normalize(flat)
    rec = new_orientacao()
    notes: list[str] = rec["extraction_notes"]

    for pat, nat in NATUREZAS:
        if re.search(pat, low):
            rec["natureza"] = nat
            break
    if not rec["natureza"]:
        notes.append("Natureza (mestrado, doutorado, TCC...) não identificada; escolha no formulário.")
    if rec["natureza"] == "Dissertação de mestrado":
        rec["tipo_mestrado"] = "Profissional" if re.search(r"mestrado profissional|programa profissional", low) else "Acadêmico"
        notes.append(f"Tipo de mestrado assumido como {rec['tipo_mestrado']}; confira.")

    if re.search(r"em andamento|em curso|orienta atualmente|atualmente orienta", low):
        rec["situacao_orientacao"] = "Em andamento"

    fim_periodo = ""
    m = re.search(r"[“\"«]([^”\"»]{15,300})[”\"»]", flat)
    if not m:
        m = re.search(r"(?:intitulad[oa]|t[ií]tulo)\s*[:\-]?\s*(.{15,300}?)(?:\.\s|,\s*(?:sob|orientad|defendid|apresentad|no\s)|;|$)", flat, re.I)
    if m:
        t = _clean_line(m.group(1)).strip(" .,;:\"“”")
        per = re.search(r"\s+(?:de\s+)?[a-zç]+\s+de\s+(20[0-3]\d|19\d\d)\s+a\s+(?:\d{1,2}\s+de\s+)?[a-zç]+\s+de\s+(20[0-3]\d|19\d\d)\.?$", t, re.I)
        if per:
            fim_periodo = per.group(2)
            t = t[: per.start()].strip(" .,;:")
        rec["titulo"] = (t[:1].upper() + t[1:].lower()) if t.isupper() else t
    else:
        notes.append("Título do trabalho orientado não identificado.")

    m = re.search(r"(?i:aluno|aluna|discente|mestrand[oa]|doutorand[oa]|orientand[oa]|acad[eê]mic[oa]|estudante)\s*(?:\(a\))?\s*[:\-]?\s*" + NAME, flat)
    if not m:
        m = re.search(r"(?i:co-?orientou|orientou)\s+(?:(?i:o\(a\)|o|a)\s+)?(?:(?i:mestr[ea]|doutor(?:a)?|graduand[oa]|bacharel|aluno\(a\)|aluno|aluna|discente)\s+)?" + NAME, flat)
    if not m:
        # "trabalho de conclusão de curso de Fulano de Tal, do curso de ...": o nome vem logo depois da natureza
        m = re.search(r"(?i:conclus[aã]o de curso|disserta[cç][aã]o|tese|monografia|inicia[cç][aã]o cient[ií]fica|supervis[aã]o)\s+(?i:de|do aluno|da aluna|do mestrando|da mestranda|do doutorando|da doutoranda)\s+" + NAME + r"\s*,\s*(?i:d[oa]s?\s+(?:curso|programa))", flat)
    if m:
        rec["nome_orientando"] = _name(m.group(1))[:60]
    else:
        notes.append("Nome do orientando não identificado.")

    ori = re.search(r"(?<![-\w])(?i:orientador(?:a)?|orienta[cç][aã]o\s+d[oa]s?)\s*(?:(?i:principal))?\s*[:\-]?" + PROF + NAME, flat)
    coo = re.search(r"(?i:co-?orientador(?:a)?|co-?orienta[cç][aã]o\s+d[oa]s?)\s*[:\-]?" + PROF + NAME, flat)
    orientador = _name(ori.group(1)) if ori else ""
    coorientador = _name(coo.group(1)) if coo else ""
    if usuario:
        if orientador and name_matches(usuario, orientador):
            rec["papel_orientacao"] = "Orientador principal"
            notes.insert(0, f"{usuario} consta como orientador.")
        elif coorientador and name_matches(usuario, coorientador):
            rec["papel_orientacao"] = "Coorientador"
            notes.insert(0, f"{usuario} consta como coorientador.")
        elif (mv := re.search(r"(co-?orientou|orientou)", low)) and re.search(re.escape(normalize(usuario).split()[-1]), low[max(0, mv.start() - 140): mv.start()]):
            rec["papel_orientacao"] = "Coorientador" if mv.group(1).startswith("co") else "Orientador principal"
            notes.insert(0, f"{usuario} consta como {'coorientador' if mv.group(1).startswith('co') else 'orientador'} (pelo verbo '{mv.group(1)}').")
        elif re.search(re.escape(normalize(usuario).split()[-1]), low) and not (orientador or coorientador):
            notes.insert(0, f"{usuario} aparece no documento, mas não identifiquei o papel; confira orientador/coorientador.")
        else:
            notes.insert(0, f"ATENÇÃO: nome do usuário não encontrado: {usuario} não consta como orientador nem coorientador neste documento"
                          + (f" (consta: {orientador or coorientador})" if (orientador or coorientador) else "") + ". Escolha o tipo de orientação manualmente e confira se é o arquivo certo.")
    if orientador:
        notes.append(f"Orientador identificado no documento: {orientador}" + (f"; coorientador: {coorientador}" if coorientador else "") + ".")

    m = INST_RE.search(flat)
    if m:
        rec["instituicao_orient"] = _clean_line(m.group(1))
    else:
        notes.append("Instituição não identificada.")
    _fim_curso = r"(?=\s*(?:,|\.|;|\(|\s+(?:d[aoe]s?\s+(?:Universidade|Instituto|Faculdade|Centro|Escola|Funda[cç][aã]o)|na\s|no\s|em\s|pela\s|pelo\s|sob\s|conclu\w+|defend\w+|intitulad\w+)|$))"
    m = re.search(r"(?i:d[oa]s?\s+curso\s+de(?:\s+gradua[cç][aã]o\s+em)?)\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ,' ]{3,60}?)" + _fim_curso, flat)
    if not m:
        m = re.search(r"(?i:Programa de P[óo]s-?Gradua[cç][aã]o (?:em|de)|curso de(?: gradua[cç][aã]o em)?|mestrado em|doutorado em|bacharelado em|licenciatura em)\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ,' ]{3,60}?)(?=\s*(?:,|\.|;|\(|\s+(?:d[aoe]s?\s+(?:Universidade|Instituto|Faculdade|Centro|Escola|Funda[cç][aã]o)|na\s|no\s|em\s|pela\s|pelo\s|sob\s|conclu\w+|defend\w+)|$))", flat)
    if m:
        rec["curso_orient"] = _clean_line(m.group(1))
    else:
        notes.append("Curso não identificado.")

    ano = fim_periodo or None
    m = None if ano else re.search(r"(?:defend\w+|aprovad\w+|conclu\w+|realizad\w+).{0,80}?(\d{1,2}/\d{1,2}/(20[0-3]\d|19\d\d)|(?:de\s+)?[a-zç]+\s+de\s+(20[0-3]\d|19\d\d))", flat, re.I)
    if m:
        ano = re.search(r"(20[0-3]\d|19\d\d)", m.group(1)).group(1)
    if not ano:
        anos = re.findall(r"\b(20[0-3]\d|19\d\d)\b", flat)
        ano = anos[-1] if anos else None
    if ano:
        rec["ano"] = ano
    else:
        notes.append("Ano não identificado.")

    if rec["titulo"]:
        rec["palavras_chave"] = palavras_chave(rec["titulo"], maximo=5)

    hay = normalize(rec["titulo"] + " " + rec["curso_orient"])
    areas = [lat for term, lat in LATTES_AREAS if re.search(r"\b" + term + r"\b", hay)]
    for area in areas_do_texto(rec["titulo"], rec["curso_orient"], maximo=2):
        if area not in areas:
            areas.append(area)
    if areas:
        rec["area_conhecimento"] = "; ".join(areas[:3])
    notes.append("Documento lido por heurística: confira todos os campos antes de aplicar no Lattes.")
    return rec
