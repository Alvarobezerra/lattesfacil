"""Leitores por item (onda 1): texto do documento -> {nome_do_campo_no_Lattes: valor legível}.

Radios e selects recebem o RÓTULO da opção (o preenchimento converte para o código com a especificação).
O que o documento não traz fica de fora e vira aviso; nada é inventado. Padrões vêm de itens/curadoria.json.
Atenção: leitores da onda 1 foram escritos sobre o padrão comum dos certificados e ainda precisam de amostras
reais (ver docs/plano-implantacao-itens.md, passo 1 e critério 1).
"""
from __future__ import annotations

import re
from typing import Any, Callable

from caderno import name_matches, normalize
from certificado import EVENT_WORDS, sentence_title
from extractor import _clean_line
from . import especificacao
from .leitura_comum import par_de_datas, sem_referencias_legais, titulo_de_pagina, titulo_formatado, titulo_provavel, valor_do_rotulo
from .variantes import sugerir_variante

TipoLeitor = Callable[[str, str], tuple[dict[str, Any], list[str]]]

NATUREZA_EVENTO = [("congresso", "Congresso"), ("seminario", "Seminário"), ("simposio", "Simpósio"), ("oficina", "Oficina"),
                   ("encontro", "Encontro"), ("jornada", "Encontro"), ("olimpiada", "Olimpíada"), ("feira", "Feira"),
                   ("exposicao", "Exposição"), ("reuniao", "Encontro")]


def format_event_name(nome: str) -> str:
    """Padroniza o nome do evento em Title Case quando estiver em CAIXA ALTA (ex.: I CONGRESSO NACIONAL -> I Congresso Nacional)."""
    if not nome or not nome.isupper():
        return nome
    words = nome.split()
    lowers = {"de", "da", "do", "das", "dos", "e", "em", "na", "no", "com", "para"}
    res = []
    for i, w in enumerate(words):
        w_clean = re.sub(r"[,;.:]+$", "", w)
        punct = w[len(w_clean):]
        if re.fullmatch(r"[IVXLCDM]+", w_clean, re.I):
            res.append(w_clean.upper() + punct)
        elif w_clean.lower() in lowers and i > 0:
            res.append(w_clean.lower() + punct)
        else:
            res.append(w_clean.capitalize() + punct)
    return " ".join(res)


def _evento(flat: str) -> dict[str, str]:
    out: dict[str, str] = {}
    pat = (r"(?:participa[cç][aã]o|participou)(?:\s+(?:com\s+[êe]xito|com\s+sucesso|com\s+aproveitamento|ativamente|como\s+\w+|na\s+qualidade\s+de\s+\w+))?"
           # "participou, como organizador(a), com êxito o Congresso X": papel entre vírgulas, êxito e artigo antes do nome do evento
           r"(?:,?\s*como\s+[^,]{2,60}?,)?(?:\s*com\s+[êe]xito)?\s*(?:do|da|de|no|na|dos|das|em|o|a)?\s*"
           # função na organização ("participou da Comissão Organizadora da X", "na organização do evento com êxito da X"): o nome vem depois
           r"(?:(?:comiss[aã]o\s+(?:organizadora|cient[ií]fica|executiva)|organiza[cç][aã]o|coordena[cç][aã]o)(?:\s+d[oae]s?\s+evento)?(?:\s+com\s+[êe]xito)?\s+d[oae]s?\s+)?"
           r"(?:evento\s+)?(.+?)"
           r"(?:,\s*em\s+[A-ZÀ-Ý][^,]{2,40}?[-–/]\s*[A-Z]{2}\b|\s+entre\s+\d|,\s*realizad|\s+realizad|,\s*ocorrido|\s+ocorrido|,\s*no per[ií]odo|\s+no per[ií]odo|,\s*com carga|\s+com carga|,\s*contabilizando|\s+contabilizando|\s+promovid|\s+organizado\b|\s+exercendo|$)")
    m = re.search(pat, flat, re.I)
    if m:
        full = _clean_line(m.group(1))
        primeiro = re.match(r"(.+?\([^)]{2,15}\))(?:,|\s|$)", full)
        raw_name = (primeiro.group(1) if primeiro else full)[:255]
        raw_name = re.sub(r"(?<=\w)-\s+(?=\w)", "-", raw_name)  # "Nordeste- Norte": hífen de composto quebrado na linha do PDF
        out["nome"] = format_event_name(raw_name)
        out["nome_completo"] = format_event_name(full)[:400]
    if "nome" not in out:
        m = re.search(rf"\b(?:no|na|do|da|em|de)?\s*(?:evento\s+)?((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;]*?\([A-Z0-9]{{2,12}}\))", flat) or \
            re.search(rf"\b(?:no|na|do|da|em|de)?\s*(?:evento\s+)?((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;.]{{5,140}})", flat) or \
            re.search(rf"\b(?:no|na|do|da|em|de)?\s*(?:evento\s+)?((?:{EVENT_WORDS})\s+[^,;.]{{5,140}})", flat)
        if m:
            out["nome"] = format_event_name(_clean_line(m.group(1))[:255])
    if out.get("nome"):
        ev = normalize(out["nome"])
        out["natureza"] = next((n for k, n in NATUREZA_EVENTO if k in ev), "Outra")
        out["classif"] = ("Internacional" if "internacional" in ev else "Nacional" if re.search(r"nacional|brasileir", ev)
                          else "Regional" if "regional" in ev else "")
    m = re.search(r"per[ií]odo de\s+\d{1,2}(?:\s+de\s+[a-zçã]+)?\s+a\s+\d{1,2}\s+de\s+[a-zçã]+\s+de\s+(\d{4})", flat, re.I) or \
        re.search(r"\bde\s+\d{1,2}(?:\s+de\s+[a-zçã]+)?\s+a\s+\d{1,2}\s+de\s+[a-zçã]+\s+de\s+(\d{4})", flat, re.I) or \
        re.search(r"\b(?:de|em)\s+\d{1,2}(?:/\d{1,2})?\s+(?:a|à|e)\s+\d{1,2}/\d{1,2}/(\d{4})", flat) or \
        re.search(r"\b(20[0-3]\d|199\d)\b", flat)
    if m:
        out["ano"] = m.group(1)
    m = re.search(r"cidade de\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat, re.I) or \
        re.search(r"\bem\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat)
    if m:
        cidade_nome = m.group(1).strip()
        cidade_formatada = cidade_nome.title() if cidade_nome.isupper() else cidade_nome
        out["cidade"] = f"{cidade_formatada} - {m.group(2).upper()}"
    if "cidade" not in out:
        mc = re.search(r"(?:Faculdade|Universidade|Campus|Cidade|Município)\s+(?:[A-Za-zÀ-ÿ'\s-]{1,30}?\s+)?(Santo\s+[A-Za-zÀ-ÿ]+|[A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+)?)\s*[-–/]\s*([A-Z]{2})\b", flat) or \
             re.search(r"\b(Santo\s+Ângelo|Santo\s+Angelo)\b", flat, re.I)
        if mc:
            if mc.lastindex and mc.lastindex >= 2:
                out["cidade"] = f"{mc.group(1).strip()} - {mc.group(2)}"
            else:
                out["cidade"] = mc.group(1).strip()
    m = re.search(r"realizad[oa]\s+(?:pel[ao]s?|por)\s+(.+?)(?:,\s*no per[ií]odo|\s+no per[ií]odo|,\s*em\s)", flat, re.I)
    if m:
        out["promotora"] = _clean_line(m.group(1))[:255]
    return out


def _carga(flat: str) -> tuple[str, str]:
    m = re.search(r"carga hor[aá]ria(?: total)?(?: de|:)?\s*(\d{1,4})\s*(horas?|h\b|dias?|semanas?)?", flat, re.I)
    if not m:
        m = re.search(r"(\d{1,4})\s*(horas?|h)\s*(?:de carga|/aula|-aula|aula)", flat, re.I)
    if not m:  # "num total de 200 horas", "totalizando 100h", "perfazendo 192 horas"
        m = re.search(r"(?:total de|totalizando|perfazendo(?: um total de)?)\s*(\d{1,4})\s*(horas?|h\b)", flat, re.I)
    if not m:
        m = re.search(r"dura[cç][aã]o\s+(?:total\s+)?de\s+(\d{1,4})\s*(h)(?![a-z])", flat, re.I)  # "com duração de 20h0m"
    if not m:
        return "", ""
    un = (m.group(2) or "horas").lower()
    return m.group(1), "dias" if un.startswith("dia") else "semanas" if un.startswith("sem") else "horas"


def _titulo_curso(flat: str) -> str:
    pat = (r"(?:minicurso|mini-curso|oficina|curso)\s+(?:de\s+|sobre\s+|intitulad[oa]\s+)?[\"“”']?(.{5,160}?)[\"“”']?"
           r"(?=\s*,|\s+(?:realizad|promovid|ministrad|com carga|no per[ií]odo|na modalidade|em\s+\d)|\.\s|$)")
    m = re.search(pat, flat, re.I)
    return sentence_title(m.group(1).strip(" \"“”'.,")) if m else ""


def ler_participacao_evento(texto: str, usuario: str):
    flat = _clean_line(texto)
    ev = _evento(flat)
    low = normalize(flat)
    v: dict[str, Any] = {
        "f_nme_evento": ev.get("nome", ""), "f_ano": ev.get("ano", ""), "F_COD_PROD": ev.get("natureza", ""),
        "f_classif": ev.get("classif", ""), "f_cidade": ev.get("cidade", ""),
        "F_FORMA": "Convidado" if re.search(r"convidad[oa]|palestrante|conferencista", low) else
        "Participante" if re.search(r"na qualidade de participante|participante\b", low) else "Ouvinte",
        "f_pais": "Brasil",
        "F_STA_DIVULGACAO_CIENTIFICA": "não",
    }
    n = []
    if not ev.get("nome"):
        n.append("Nome do evento não identificado.")
    if not ev.get("ano"):
        n.append("Ano do evento não identificado.")
    n.append("Tipo da apresentação/participação: o Lattes monta esta lista conforme a forma de participação; confira após o preenchimento.")
    return v, n


def ler_organizacao_evento(texto: str, usuario: str):
    flat = _clean_line(texto)
    ev = _evento(flat)
    low = normalize(flat)
    v: dict[str, Any] = {"f_titulo": ev.get("nome", ""), "f_ano": ev.get("ano", ""), "f_cidade": ev.get("cidade", ""),
                         "f_inst": ev.get("promotora", ""), "F_SUB_PROD": "Organização",
                         "F_COD_PROD": ev.get("natureza") if ev.get("natureza") in ("Congresso", "Feira", "Olimpíada", "Exposição") else "Outro"}
    n = []
    m = re.search(r"(coordenador|coordenou|presidente|presidiu|membro|integrou|comiss[aã]o (organizadora|cient[ií]fica))", low)
    if m:
        n.append(f"Função no evento citada no documento: «{m.group(0)}». Registrada em 'Outras informações'.")
        v["f_ref"] = f"Função: {m.group(0)}."
    if not ev.get("nome"):
        n.append("Nome do evento não identificado.")
    return v, n


def ler_curso_ministrado(texto: str, usuario: str):
    flat = _clean_line(texto)
    ev = _evento(flat)
    dur, un = _carga(flat)
    v: dict[str, Any] = {"f_titulo": _titulo_curso(flat) or ev.get("nome", ""), "f_ano": ev.get("ano", ""),
                         "f_duracao": dur, "f_unidade": un, "f_inst": ev.get("promotora", ""), "f_cidade": ev.get("cidade", ""),
                         "f_participacao": "Docente", "F_COD_PROD": "Extensão"}
    n = []
    if not v["f_titulo"]:
        n.append("Título do curso não identificado.")
    if not dur:
        n.append("Carga horária não identificada.")
    n.append("Nível do curso assumido como 'Extensão'; ajuste (Aperfeiçoamento, Especialização, Outro) se for o caso.")
    return v, n


def ler_formacao_complementar(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    carga, _ = _carga(flat)
    flat_dt = sem_referencias_legais(flat)  # "Decreto 5.154, de 2004", "Parecer 64/2004" no rodapé não são o ano do curso
    datas = _datas(flat_dt)
    ano_ini = datas[0][2] if datas else _ano_unico(flat_dt)
    ano_fim = datas[-1][2] if len(datas) > 1 else ano_ini
    m = re.search(r"(?:realizado|promovido|oferecido|ministrado)\s+(?:pel[ao]s?|por)\s+(.+?)(?:,|\s+no per|\s+com\s+carga|\.|$)", flat, re.I)
    v: dict[str, Any] = {
        "f_curso": _titulo_curso(flat), "f_carga": carga, "f_inst": _clean_line(m.group(1))[:255] if m else "",
        "f_nivel": "Extensão Universitária" if "extensao" in low else "Curso De Curta Duração",
        "F_STATUS": "incompleto" if re.search(r"n[aã]o conclu|incompleto|cursando|em andamento", low) else "concluído",
        "f_ano_ini": ano_ini,
        "f_ano_fim": ano_fim,
        "F_BOLSA": "Não",
    }
    n = []
    for k, msg in (("f_curso", "Nome do curso não identificado."), ("f_inst", "Instituição não identificada."), ("f_ano_ini", "Ano de início não identificado.")):
        if not v[k]:
            n.append(msg)
    n.append("Confira o ano de início/término e se houve bolsa na 2ª tela do Lattes.")
    return v, n


def _ano_data(flat: str) -> str:
    m = re.search(r"\d{1,2}\s+de\s+[a-zç]+\s+de\s+(20[0-3]\d|199\d)", flat, re.I)
    return m.group(1) if m else ""


def ler_banca(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    qualif = "qualificacao" in low
    if qualif and "doutor" in low:
        tipo = "Exame de qualificação de doutorado"
    elif qualif and re.search(r"mestr|dissertacao", low):
        tipo = "Exame de qualificação de mestrado"
    elif re.search(r"doutorado|\btese\b", low):
        tipo = "Doutorado"
    elif re.search(r"mestrado|dissertacao", low):
        tipo = "Mestrado"
    elif re.search(r"aperfeicoamento|especializacao", low):
        tipo = "Curso de aperfeiçoamento/especialização"
    elif re.search(r"graduacao|\btcc\b|monografia|bacharel|licenciatura", low):
        tipo = "Graduação"
    else:
        tipo = ""
    cand = ""
    m = re.search(r"(?:doutorand[ao]|mestrand[ao]|candidat[ao]|discente|aluno|aluna)\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{4,70}?)(?:,|\s+do curso|\s+no curso|\s+com\b)", flat)
    if not m:
        m = re.search(r"(?:Tese|Disserta[çc][ãa]o|Monografia|Trabalho)(?: de Conclus[ãa]o)?[^.]{0,50}?\bde\s+([A-ZÀ-Ý]{2,}(?: [A-ZÀ-Ý]{2,}| d[aeo]s?)+)\s+com\s+a\s+(?:tese|disserta)", flat) or \
            re.search(r"(?:Tese|Disserta[çc][ãa]o|Monografia|Trabalho)(?:\s+de\s+(?:Mestrado|Doutorado|Conclus[ãa]o(?:\s+de\s+Curso)?))?\s+de\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{4,70}?)(?:,\s*intitulad|\s+intitulad|\s+com\s+a\s+(?:tese|disserta))", flat, re.I)
    if m:
        cand = " ".join(w.capitalize() if w.lower() not in ("da", "de", "do", "das", "dos", "e") else w.lower() for w in m.group(1).split())
    titulo = ""
    m = re.search(r"T[ií]tulo(?: d[aeo]s?\s+\w+)?:\s*[\"“”](.+?)[\"“”]", flat) or \
        re.search(r"(?:tese|disserta[çc][ãa]o|monografia|trabalho)\s+intitulad[oa]:?\s*[\"“”]?(.+?)[\"“”]?,\s*no\s+(?:Programa|Curso)", flat, re.I) or \
        re.search(r"intitulad[oa]:?\s*[\"“”]([^\"“”]{3,200})[\"“”]", flat, re.I)
    caixa_alta = False
    if m:
        from certificado import sentence_title
        caixa_alta = m.group(1).strip().isupper()
        titulo = sentence_title(m.group(1).strip(" \"“”."))
    m = re.search(r"Programa de P[óo]s-Gradua[çc][ãa]o em ([^,.]+?)(?:\s+da\s+(Universidade[^,.]+?)|\s*[-–(]|,|\.|\s+em\s+sess)", flat)
    curso = _clean_line(m.group(0).split(" da Universidade")[0]).rstrip(" ,.-") if m else ""
    inst = ""
    mi = re.search(r"(Universidade (?:Federal|Estadual|de)[^,.;()]{3,60})", flat)
    if mi and not re.search(r"^\s*UNIVERSIDADE", flat[:30]):
        inst = _clean_line(mi.group(1))
    mi2 = re.search(r"no\s+Programa\s+de\s+P[óo]s-Gradua[çc][ãa]o\s+em\s+[^,]+?\s+da\s+(Universidade[^,.;]+)", flat)
    if mi2:
        inst = _clean_line(mi2.group(1))
    papel = ""
    mp = re.search(r"como\s+(Presidente|Examinador(?:a)?(?: Externo(?:\(a\))?)?(?: [àa] Institui[çc][ãa]o)?|Membro(?: titular| externo| interno)?|Orientador(?:a)?|Coorientador(?:a)?)", flat, re.I)
    if mp:
        papel = _clean_line(mp.group(1))
    v: dict[str, Any] = {"F_COD_PROD": tipo, "f_titulo": titulo, "f_ano": _ano_data(flat), "f_nme_orient": cand,
                         "f_inst": inst, "f_curso": curso, "f_ref": f"Papel na banca: {papel}." if papel else ""}
    if tipo == "Mestrado":
        v["f_sub_prod"] = "Acadêmico"
    n = ["Instituição e curso são cadastros controlados do Lattes: o preenchimento tenta escolher; se não achar, use a lupa."]
    if not titulo:
        n.append("Título do trabalho avaliado não identificado.")
    if not cand:
        n.append("Nome do candidato não identificado.")
    if not tipo:
        n.append("Tipo da banca (mestrado, doutorado, qualificação...) não identificado.")
    if titulo and caixa_alta:
        n.append("Título convertido de CAIXA ALTA; confira nomes científicos e siglas.")
    if tipo == "Mestrado":
        n.append("Tipo do mestrado assumido como Acadêmico; ajuste se for Profissional.")
    return v, n


def ler_premio(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    termo = "Menção honrosa" if "mencao honrosa" in low else "Prêmio de melhor trabalho" if "melhor trabalho" in low else \
        "Prêmio"
    m = re.search(r"(?:premiad[oa]|agraciad[oa]|recebeu|conferid[oa]|concedid[oa])[^.]{0,60}?\b(?:no|na|em|do|da)\s+((?:[IVXLCDM]+|\d+[ºª°]?)?\s*[A-ZÀ-Ý][^,.]{6,120}?)(?:,|\.|\s+realizad)", flat)
    evento = _clean_line(m.group(1)) if m else ""
    nome = f"{termo} - {evento}" if evento else termo
    v: dict[str, Any] = {"f_titulo": nome[:255], "f_agencia": evento[:255], "f_ano": _ano_data(flat) or _ano_unico(flat)}
    n = ["Entidade promotora assumida como o evento; troque pela instituição organizadora se o certificado indicar outra."]
    if not evento:
        n.append("Evento/entidade do prêmio não identificado.")
    return v, n


def ler_projeto(texto: str, usuario: str):
    """Resolução/portaria que homologa ou institui um projeto (pesquisa, extensão, ensino, desenvolvimento)."""
    from certificado import sentence_title
    flat = _clean_line(texto)
    low = normalize(flat)
    tipo = ("Projeto de extensão" if re.search(r"projeto de extensao", low) else
            "Projetos de pesquisa" if re.search(r"projeto de pesquisa", low) else
            "Projeto de ensino" if re.search(r"projeto de ensino", low) else
            "Projeto de desenvolvimento tecnológico" if re.search(r"desenvolvimento tecnologico", low) else "Outros tipos de projetos")
    natureza = {"Projeto de extensão": "Extensão", "Projetos de pesquisa": "Pesquisa", "Projeto de ensino": "Ensino",
                "Projeto de desenvolvimento tecnológico": "Desenvolvimento"}.get(tipo, "Outra")
    m = re.search(r"intitulad[oa]\s*[\"“”]?(.+?)[\"“”]?\s*,\s*(?:coordenad|sob a coordena|desenvolvid|executad|de responsabilidade)", flat, re.I) or \
        re.search(r"projeto\s+de\s+(?:pesquisa|extens[ãa]o|ensino|desenvolvimento(?:\s+tecnol[óo]gico)?)\s+[\"“”]([^\"“”]{3,200})[\"“”]", flat, re.I)
    titulo = sentence_title(m.group(1).strip(" \"“”.")) if m else ""
    ano = ""
    md = re.search(r"\d{1,2}\s+de\s+[a-zç]+\s+de\s+(20[0-3]\d|199\d)", flat, re.I)
    if md:
        ano = md.group(1)
    if not ano:
        ano = _ano_unico(flat)
    m = re.search(r"coordenad[oa]\s+pel[oa]\s+(?:Professor[a]?\s+|Prof\.?\s+|Dr\.?\s+)*([A-ZÀ-Ý][\wÀ-ÿ' ]{4,70}?)\s*,\s*(?:d[aoe]s?\s+)?(.+?),\s*vinculad[oa]\s+(?:a[o]?|à)\s+(.+?),\s*d[aoe]s?\s+(Universidade[^.,]+)", flat)
    coord, orgao, centro, inst = (m.group(1), m.group(2), m.group(3), m.group(4)) if m else ("", "", "", "")
    if not inst:
        mi = re.search(r"\b(Universidade\s+(?:Federal|Estadual|de)[^,.;()]{3,80})", flat)
        if mi:
            inst = mi.group(1)
    if not coord:
        mc = re.search(r"(?:declaramos\s+que\s+)([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{4,70}?)\s+[ée]\s+coordenador(?:a)?\b", flat, re.I)
        if mc:
            coord = mc.group(1)
    orgao_txt = _clean_line(orgao).strip(" ,.")
    inst_txt = _clean_line(inst).strip(" ,.")
    v: dict[str, Any] = {"__variante": tipo, "f_titulo": titulo, "F_TPO_NATUREZA": natureza, "F_TPO_SITUACAO": "Em andamento",
                         "F_ANO_INIC": ano, "f_inst": inst_txt, "f_orgao": (_clean_line(centro).strip(" ,.") if centro else orgao_txt)}
    if coord:
        from itens.sugestoes import como_citado
        nome_coord = _clean_line(coord).strip(" ,.")
        v["grade:autores"] = [{"nome": nome_coord, "citacao": como_citado(nome_coord), "coordenador": True}]
    n = []
    if not titulo:
        n.append("Nome do projeto não identificado.")
    n.append("Ano de início assumido como o ano do documento e situação como 'Em andamento'; confira e informe o ano fim se o projeto já terminou.")
    if coord:
        n.append(f"Coordenador citado no documento: {_clean_line(coord)}. O integrante/papel é registrado na aba Equipe do Lattes (não preenchida aqui).")
        if usuario and not name_matches(usuario, coord):
            n.append(f"ATENÇÃO: {usuario} não é o coordenador citado; confira se participa da equipe.")
    if orgao_txt:
        n.append("Órgão/Unidade: o Lattes costuma ter só o nível do centro/campus (não a coordenação \"" + orgao_txt + "\"); sugeri o centro citado no documento" + (" (" + _clean_line(centro).strip(" ,.") + ")" if centro else "") + ". Na lupa, o preenchimento escolhe o órgão da instituição pela cidade/nome; confira.")
    if tipo == "Outros tipos de projetos":
        n.append("Tipo de projeto não identificado (pesquisa, extensão, ensino ou desenvolvimento); usei 'Outros tipos'.")
    return v, n


def _nome_proprio(nome: str) -> str:
    """'ANA LÚCIA DE SOUSA' -> 'Ana Lúcia de Sousa' (só quando veio em CAIXA ALTA)."""
    if not nome.isupper():
        return nome
    liga = {"de", "da", "do", "das", "dos", "e"}
    return " ".join(p.lower() if p.lower() in liga else p.capitalize() for p in nome.lower().split())


def ler_patente(texto: str, usuario: str):
    """Comprovante de depósito do INPI (peticionamento eletrônico)."""
    from certificado import sentence_title
    flat = _clean_line(texto)
    low = normalize(flat)
    m = re.search(r"N[úu]mero do Processo:\s*(BR[\s\d]+?\d)\s+(?:Dados|Depositante)", flat)
    proc = _clean_line(m.group(1)) if m else ""
    if not proc:
        m = re.search(r"\bBR\s?\d{2}\s?\d{4}\s?\d{6}\s?\d\b", flat)
        proc = _clean_line(m.group(0)) if m else ""
    tipo = "Patente de Modelo de Utilidade" if re.search(r"patente de modelo de utilidade|\(mu\)", low) else \
        "Patente de Invenção" if re.search(r"patente de invencao|\(pi\)", low) else ""
    m = re.search(r"T[ií]tulo da Inven[çc][ãa]o ou Modelo de Utilidade(?: \(54\))?:\s*(.+?)\s+Resumo:", flat) or \
        re.search(r"\bT[ií]tulo:\s*(.+?)(?:\.\s*(?:Inventores|Titular|Depositante|Resumo|Concess[ãa]o)|$)", flat)
    titulo = sentence_title(m.group(1).strip(" .")) if m else ""
    m = re.search(r"Resumo:\s*(.+?)(?:\s+Peti[çc][ãa]o\s+\d{6,}\s*,\s*de\s+\d|\s+Dados do Inventor|\s+Documentos anexados|$)", flat)
    resumo = _clean_line(m.group(1)) if m else ""
    natureza = ""
    if titulo:
        tl = normalize(titulo)
        natureza = "Produto e Processo" if (re.search(r"\bprocesso\b", tl) and re.search(r"\b(bebida|composicao|formulacao|produto|dispositivo|equipamento|kit|extrato)\b", tl)) else \
            "Processo" if re.search(r"\bprocesso\b|\bmetodo\b", tl) else "Produto"
    titulares = [{"nome": _nome_proprio(_clean_line(a)), "tipo": "instituição" if "jur" in normalize(b) else "pessoa"}
                 for a, b in re.findall(r"Nome ou Raz[ãa]o Social:\s*(.+?)\s+Tipo de Pessoa:\s*(Pessoa Jur[íi]dica|Pessoa F[íi]sica)", flat)]
    depositante = titulares[0]["nome"] if titulares else ""
    inventores = list(dict.fromkeys(_clean_line(x) for x in re.findall(r"\bNome:\s*(.+?)\s+CPF:", flat)))
    if not inventores:
        mi = re.search(r"\bInventores:\s*(.+?)(?:\.\s*(?:Concess[ãa]o|Dep[óo]sito|Titular)|\.|$)", flat)
        if mi:
            inventores = [_clean_line(x).strip(" .;") for x in re.split(r"\s*;\s*|\s*,\s*", mi.group(1)) if _clean_line(x).strip(" .;")]
    if not titulares and inventores:
        titulares = [{"nome": inventores[0], "tipo": "pessoa"}]
    m = re.search(r"\b(\d{2})/(\d{2})/(20[0-3]\d)\b", flat)
    dep_data = f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else (_fmt(d[0]) if (d := _datas(flat)) else "")
    from itens.sugestoes import como_citado
    # O Lattes limita o número do registro a 16 caracteres e o aceita sem espaços (BR1020240037669).
    v: dict[str, Any] = {"f_cod_reg": re.sub(r"\s+", "", proc), "f_inst": "INPI - Instituto Nacional da Propriedade Industrial", "f_pais": "Brasil",
                         "f_tipo": tipo, "f_titulo": titulo, "f_natureza": natureza, "f_ref": resumo}
    if dep_data:
        v["grade:situacoes"] = [{"nome": "Depósito", "citacao": dep_data}]
    if any(t["tipo"] == "instituição" for t in titulares):
        v["grade:titulares_inst"] = [t["nome"] for t in titulares if t["tipo"] == "instituição"]
    if any(t["tipo"] == "pessoa" for t in titulares):
        v["grade:titulares_pessoa"] = [t["nome"] for t in titulares if t["tipo"] == "pessoa"]
    if inventores:
        v["grade:autores"] = [{"nome": _nome_proprio(i), "citacao": como_citado(_nome_proprio(i))} for i in inventores]
    n = []
    if proc:
        n.append(f"Número do processo ({proc}) usado como número do registro, sem espaços, como o Lattes pede.")
    else:
        n.append("Número do processo não identificado.")
    if natureza:
        n.append(f"Natureza assumida como '{natureza}' pelo título; confira (Produto, Processo ou Produto e Processo).")
    if dep_data:
        n.append(f"Situação: depósito em {dep_data} (aba Situação do Depósito/Patente); se já houve concessão, inclua a nova situação com a data.")
    if titulares:
        n.append(f"Depositante/titular lido do documento: {'; '.join(t['nome'] for t in titulares)}. O Lattes exige ao menos um; ele vai para o campo Pessoas ou Instituições conforme o tipo de pessoa do documento.")
    if inventores:
        achou = [i for i in inventores if usuario and name_matches(usuario, i)]
        n.append(f"{len(inventores)} inventores no documento" + (f"; {usuario} consta entre eles." if achou else
                 (f"; ATENÇÃO: {usuario} não consta entre eles." if usuario else ".")) + " Estão na aba Inventores; confira os nomes em citações.")
    if len(resumo) > 0:
        n.append("O resumo pode passar do limite do campo do Lattes; o preenchimento corta e avisa.")
    return v, n


def ler_anais(texto: str, usuario: str):
    """Trabalho publicado em anais de evento (resumo/trabalho avulso): leitura de antes (extractor.parse_evidence_text), agora no formulário por spec."""
    from extractor import parse_evidence_text
    rec = parse_evidence_text(texto)
    tit = rec.get("titulo", "")
    m_int = re.search(r"intitulad[oa]\s*:?\s*[\"“”]\s*([^\"“”]{10,300}?)\s*[\"“”]", texto)
    if m_int and re.search(r"(?i)certificamos|certificado|declaramos", texto):  # certificado de publicação: o título vem entre aspas depois de "intitulado"
        rec["titulo"] = titulo_formatado(_clean_line(m_int.group(1)))
        tit = rec["titulo"]
    elif re.search(r"(?i)issn|revista|journal|anais do evento|\bv\.\s*\d", tit) or re.match(r"\s*\d", tit) or len(tit.split()) < 4:  # pegou a faixa da revista/dos anais/do evento em vez do título
        melhor = titulo_de_pagina(texto) or titulo_provavel(texto)
        if melhor:
            rec["titulo"] = titulo_formatado(melhor)
    return ler_anais_registro(rec, texto)


def ler_anais_registro(rec: dict, texto: str = ""):
    """Valores do formulário de anais a partir de um registro no formato antigo (usado também pelo caderno, histórico e enriquecimento)."""
    v: dict[str, Any] = {
        "F_COD_PROD": rec.get("natureza", ""), "f_titulo": rec.get("titulo", ""), "f_ano": rec.get("ano", ""), "f_pais": rec.get("pais", ""),
        "F_IDIOMA": rec.get("idioma", ""), "f_meio": rec.get("meio_divulgacao", ""), "f_homepage": rec.get("homepage", ""), "f_cod_doi": rec.get("doi", ""),
        "f_tipo_evento": rec.get("classificacao_evento", ""), "f_evento": rec.get("nome_evento", ""), "f_cidade_evento": rec.get("cidade_evento", ""),
        "f_ano_evento": rec.get("ano_evento", ""), "f_titulo_pub": rec.get("titulo_anais", ""), "f_volume": rec.get("volume", ""),
        "f_fasciculo": rec.get("fasciculo", ""), "f_serie": rec.get("serie", ""), "f_pag_ini": rec.get("pagina_inicial", ""), "f_pag_fim": rec.get("pagina_final", ""),
        "f_isbn": rec.get("isbn_issn", ""), "f_editora": rec.get("editora", ""), "f_cidade_ed": rec.get("cidade_editora", ""), "f_ref": rec.get("outras_informacoes", ""),
    }
    # O campo ISBN/ISSN do Lattes aceita 13 caracteres: o ISBN com hífens (17) seria cortado; grava só os dígitos (e X).
    digitos = re.sub(r"[^0-9Xx]", "", str(v["f_isbn"]))
    if len(str(v["f_isbn"])) > 13 and len(digitos) in (8, 10, 13):
        v["f_isbn"] = digitos.upper()
    # "Anais do Simpósio X, 2024": título dos anais e nome do evento, quando a extração antiga não os trouxe.
    m = re.search(r"(Anais\s+(?:do|da|de|dos|das)\s+([^,.;\n]{5,160}))", texto)
    if m:
        v["f_titulo_pub"] = v["f_titulo_pub"] or _clean_line(m.group(1))
        v["f_evento"] = v["f_evento"] or _clean_line(m.group(2))
    if rec.get("autores"):
        v["grade:autores"] = [{"nome": a["nome"], "citacao": a.get("citacao", "")} for a in rec["autores"]]
    if rec.get("palavras_chave"):
        v["grade:palavras_chave"] = [k for k in rec["palavras_chave"] if not re.fullmatch(r"\d{4}", str(k).strip())][:8]
    if rec.get("area_conhecimento"):
        v["grade:areas"] = [x.strip() for x in str(rec["area_conhecimento"]).split(";") if x.strip()]
    return v, list(rec.get("extraction_notes", []))


def ler_apresentacao(texto: str, usuario: str):
    """Apresentação de trabalho e palestra (certificado): leitura de antes (certificado.parse_certificado), agora no formulário por spec."""
    from certificado import parse_certificado
    return ler_apresentacao_registro(parse_certificado(texto, usuario))


def ler_apresentacao_registro(rec: dict):
    """Valores do formulário de apresentação a partir de um registro no formato antigo (certificado, histórico)."""
    v: dict[str, Any] = {
        "F_COD_PROD": rec.get("natureza", ""), "f_titulo": rec.get("titulo", ""), "f_ano": rec.get("ano", ""), "f_pais": rec.get("pais", ""),
        "F_IDIOMA": rec.get("idioma", ""), "f_meio": rec.get("meio_divulgacao", ""), "f_homepage": rec.get("homepage", ""),
        "f_nme_evento": rec.get("nome_evento", ""), "f_inst": rec.get("instituicao_promotora", ""), "f_local": rec.get("local_evento", ""),
        "f_cidade": rec.get("cidade_evento", ""), "f_ref": rec.get("outras_informacoes", ""),
    }
    if rec.get("autores"):
        v["grade:autores"] = [{"nome": a["nome"], "citacao": a.get("citacao", "")} for a in rec["autores"]]
    if rec.get("palavras_chave"):
        v["grade:palavras_chave"] = list(rec["palavras_chave"])
    if rec.get("area_conhecimento"):
        v["grade:areas"] = [x.strip() for x in str(rec["area_conhecimento"]).split(";") if x.strip()]
    return v, list(rec.get("extraction_notes", []))


def ler_orientacao_concluida(texto: str, usuario: str):
    from orientacao import parse_orientacao
    return ler_orientacao_registro(parse_orientacao(texto, usuario))


def ler_orientacao_andamento(texto: str, usuario: str):
    from orientacao import parse_orientacao
    return ler_orientacao_registro(parse_orientacao(texto, usuario))


def ler_orientacao_registro(rec: dict):
    """Valores do formulário de orientação (concluída ou em andamento) a partir de um registro no formato antigo."""
    v: dict[str, Any] = {
        "F_COD_PROD": rec.get("natureza", ""), "f_dsc_outra": rec.get("tipo_mestrado", ""), "f_titulo": rec.get("titulo", ""), "f_ano": rec.get("ano", ""),
        "f_pais": rec.get("pais", ""), "F_IDIOMA": rec.get("idioma", ""), "f_homepage": rec.get("homepage", ""), "f_tpo_orient": rec.get("papel_orientacao", ""),
        "f_nme_orient": rec.get("nome_orientando", ""), "f_inst": rec.get("instituicao_orient", ""), "f_curso": rec.get("curso_orient", ""),
        "F_BOLSA": rec.get("bolsa", ""), "f_nme_agencia": rec.get("agencia_financiadora", ""), "f_ref": rec.get("outras_informacoes", ""),
        "F_RELEV": rec.get("relevante", ""),
    }
    if not re.search(r"disserta|tese", normalize(str(v["F_COD_PROD"]))):
        v["f_tpo_orient"] = ""  # o Lattes só aceita o tipo de orientação em dissertação de mestrado e tese de doutorado
    if str(v["f_tpo_orient"]).lower().startswith("co"):
        v["f_tpo_orient"] = "coorientador"  # texto da opção no Lattes
    if rec.get("palavras_chave"):
        v["grade:palavras_chave"] = list(rec["palavras_chave"])
    if rec.get("area_conhecimento"):
        v["grade:areas"] = [x.strip() for x in str(rec["area_conhecimento"]).split(";") if x.strip()]
    return v, list(rec.get("extraction_notes", []))


def ler_artigo(texto: str, usuario: str):
    """Artigo completo em periódico: DOI (Crossref) ou PDF do artigo. Mesma leitura de antes (artigo.parse_artigo), agora no formulário por spec."""
    from artigo import parse_artigo, doi_only
    return ler_artigo_registro(parse_artigo(texto, usuario, doi=doi_only(texto) or ""))


def ler_artigo_registro(rec: dict):
    """Valores do formulário de artigo a partir de um registro no formato antigo (histórico e enriquecimento)."""
    v: dict[str, Any] = {
        "f_titulo": rec.get("titulo", ""), "f_ano": rec.get("ano", ""), "F_IDIOMA": rec.get("idioma", ""), "f_meio": rec.get("meio_divulgacao", ""),
        "f_homepage": rec.get("homepage", ""), "f_cod_doi": rec.get("doi", ""), "f_titulo_periodico": rec.get("periodico", ""),
        "f_issn": rec.get("isbn_issn", ""), "f_volume": rec.get("volume", ""), "f_serie": rec.get("serie", ""),
        "f_pag_ini": rec.get("pagina_inicial", ""), "f_pag_fim": rec.get("pagina_final", ""),
    }
    if rec.get("autores"):
        v["grade:autores"] = [{"nome": a["nome"], "citacao": a.get("citacao", "")} for a in rec["autores"]]
    if rec.get("palavras_chave"):
        v["grade:palavras_chave"] = list(rec["palavras_chave"])
    if rec.get("area_conhecimento"):
        v["grade:areas"] = [x.strip() for x in str(rec["area_conhecimento"]).split(";") if x.strip()]
    return v, list(rec.get("extraction_notes", []))


# Nome do campo do formulário (spec) -> chave do registro no formato antigo, para o enriquecimento (Crossref/OpenAlex) e para o histórico.
_CAMPO_PARA_REGISTRO = {
    "anais": {"F_COD_PROD": "natureza", "f_titulo": "titulo", "f_ano": "ano", "f_pais": "pais", "F_IDIOMA": "idioma", "f_meio": "meio_divulgacao",
              "f_homepage": "homepage", "f_cod_doi": "doi", "f_tipo_evento": "classificacao_evento", "f_evento": "nome_evento", "f_cidade_evento": "cidade_evento",
              "f_ano_evento": "ano_evento", "f_titulo_pub": "titulo_anais", "f_volume": "volume", "f_fasciculo": "fasciculo", "f_serie": "serie",
              "f_pag_ini": "pagina_inicial", "f_pag_fim": "pagina_final", "f_isbn": "isbn_issn", "f_editora": "editora", "f_cidade_ed": "cidade_editora", "f_ref": "outras_informacoes"},
    "artigo": {"f_titulo": "titulo", "f_ano": "ano", "F_IDIOMA": "idioma", "f_meio": "meio_divulgacao", "f_homepage": "homepage", "f_cod_doi": "doi",
               "f_titulo_periodico": "periodico", "f_issn": "isbn_issn", "f_volume": "volume", "f_serie": "serie", "f_pag_ini": "pagina_inicial", "f_pag_fim": "pagina_final"},
}


def para_registro_antigo(item_id: str, valores: dict[str, Any]) -> dict[str, Any]:
    mapa = _CAMPO_PARA_REGISTRO.get(item_id, {})
    rec: dict[str, Any] = {mapa[k]: v for k, v in valores.items() if k in mapa and v not in ("", None)}
    rec["tipo_producao"] = item_id
    return rec


def enriquecer(item_id: str, valores: dict[str, Any]) -> dict[str, Any]:
    """Completa campos vazios do formulário com Crossref/OpenAlex (mesma busca de antes), devolvendo só valores novos no formato do spec."""
    from extractor import enrich_missing_fields
    rec = para_registro_antigo(item_id, valores)
    res = enrich_missing_fields(rec)
    sug = res.get("suggestions") or {}
    if item_id == "artigo" and sug.get("titulo_anais") and not rec.get("periodico"):
        sug = {**sug, "periodico": sug["titulo_anais"]}  # no artigo, o container do Crossref é o periódico
    fn = {"anais": ler_anais_registro, "artigo": ler_artigo_registro}[item_id]
    novos, _ = fn({**rec, **sug})
    out = {k: v for k, v in novos.items() if v not in ("", None) and not str(k).startswith("grade:") and not valores.get(k)
           and k not in ("F_RELEV", "F_STA_DIVULGACAO_CIENTIFICA", "f_pais", "F_IDIOMA", "f_meio")}
    return {"valores": out, "fontes": res.get("sources") or []}


LEITORES: dict[str, TipoLeitor] = {
    "orientacao_concluida": ler_orientacao_concluida,
    "orientacao_andamento": ler_orientacao_andamento,
    "apresentacao": ler_apresentacao,
    "anais": ler_anais,
    "artigo": ler_artigo,
    "projeto": ler_projeto,
    "patente": ler_patente,
    "banca": ler_banca,
    "premio": ler_premio,
    "participacao_evento": ler_participacao_evento,
    "organizacao_evento": ler_organizacao_evento,
    "curso_ministrado": ler_curso_ministrado,
    "formacao_complementar": ler_formacao_complementar,
}


from .leitores_onda2 import LEITORES_ONDA2, _ano_unico, _datas, _fmt, _mes_ano  # noqa: E402


def ler_livro_capitulo(texto: str, usuario: str):
    """Leitor heurístico para livros e capítulos (ficha catalográfica ou texto de referência)."""
    flat = _clean_line(texto)
    v: dict[str, Any] = {}
    m = re.search(r"ISBN\s*[:.]?\s*([0-9][0-9\-Xx ]{8,19}[0-9Xx])", flat, re.I)
    if m:
        v["f_isbn"] = re.sub(r"[^0-9Xx]", "", m.group(1).upper())[:13]
    m = re.search(r"\b(20[0-3]\d|19[89]\d)\b", flat)
    if m:
        v["f_ano"] = m.group(1)
    m = re.search(r"\b(\d{1,3})\s*[ªº°]?\s*edi[çc][ãa]o\b", flat, re.I)
    if m:
        v["f_edicao"] = m.group(1)
    m = re.search(r"\bp{1,2}\.\s*(\d{1,5})\s*[-–]\s*(\d{1,5})\b", flat, re.I)
    if m:
        v["f_pag_ini"], v["f_pag_fim"] = m.group(1), m.group(2)
    m = re.search(r"\b(\d{1,5})\s*p[áa]ginas?\b", flat, re.I)
    if m:
        v["f_paginas"] = m.group(1)
    m = re.search(r"Organizadores?\s*:\s*(.+?)(?:\.|\n|$)", flat, re.I)
    if m:
        v["f_organizadores"] = _clean_line(m.group(1)).strip(" .;")[:255]
    m = re.search(r"Cap[íi]tulo\s+\d+\s*[:\-–]\s*(.+?)(?:,\s*por\b|\s+p{1,2}\.\s*\d|\.|\n|$)", flat, re.I)
    if m:
        v["f_titulo_cap"] = titulo_formatado(sentence_title(m.group(1).strip(" \"“”.,")))[:400]  # CAIXA ALTA com erro de OCR também vira sentença
    if not v.get("f_titulo_cap"):  # página de capítulo: "CAPÍTULO 9" e o título nas linhas seguintes (ou "CAPÍTULO 11 - TÍTULO" quebrado em linhas)
        pagina = titulo_de_pagina(texto)
        if pagina:
            v["f_titulo_cap"] = titulo_formatado(pagina)[:400]
    m = re.search(r"^(?:FICHA CATALOGR[ÁA]FICA\s+)?(.+?)(?:\.\s*Organizadores?:|\.\s*Cap[íi]tulo\b|\s+ISBN\b)", flat, re.I)
    if not m:
        m = re.search(r"[\"“”']([^\"“”']{4,250})[\"“”']", flat)
    if m:
        tit = re.sub(r"^(?:FICHA CATALOGR[ÁA]FICA|LIVRO)\s+", "", _clean_line(m.group(1)).strip(" ."), flags=re.I)
        if tit:
            v["f_titulo"] = tit[:400]
    m = re.search(r"\b(Editora\s+[^,.\n]{2,120})(?:,\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}))?", flat)
    if m:
        v["f_editora"] = _clean_line(m.group(1)).strip(" .,")[:100]
        if m.group(2):
            v["f_cidade_ed"] = _clean_line(m.group(2)).strip(" .,")[:30]
    if True:  # ficha catalográfica (CIP): "[código] Título [subtítulo] / Organizadores ..." — é mais confiável que o 1º trecho do texto
        mc = re.search(r"(?s)Cataloga[çc][ãa]o na Publica[çc][ãa]o.{0,300}?\n(?:[A-Z]{1,3}\d{0,4}[a-z]?[ \t]*\n)?[ \t]*(?:[A-Z]{1,3}\d{0,4}[a-z]?[ \t]+)?([A-ZÀ-Ý][^\n/]{8,160}?)[ \t]*/", texto)
        if mc:
            v["f_titulo"] = re.sub(r"\s*\[livro eletr[ôo]nico\]\s*:?", "", _clean_line(mc.group(1))).strip(" .:")[:400]
    return v, ["Confira se é Livro ou Capítulo de livro e complete autores/palavras-chave."]


def ler_formacao_academica(texto: str, usuario: str):
    """Leitor heurístico para diplomas, declarações de titulação e certificados de aperfeiçoamento/especialização."""
    flat = _clean_line(texto)
    v: dict[str, Any] = {}

    # 1. Nome do Curso / Titulação
    curso_rotulado = valor_do_rotulo(texto, ("Curso",))  # "CURSO: Bacharelado em Odontologia" (valor na linha ou na seguinte)
    if not curso_rotulado:  # tabela: rótulo e valor distantes; a linha do grau ("Bacharelado em X") identifica o curso
        m_grau = re.search(r"^\W*((?:Bacharelado|Licenciatura|Tecnologia|Curso Superior de Tecnologia)\s+(?:em|de)\s+[^\n\-–:]{3,70}?)\s*(?:-|–|$)", texto, re.I | re.M)
        curso_rotulado = m_grau.group(1).strip() if m_grau else ""
    if not curso_rotulado:  # linha de sistema acadêmico: "ENFERMAGEM - IMPERATRIZ - PRESENCIAL - BACHARELADO - MT"
        m_sis = re.search(r"^\W*([A-ZÀ-Ý][A-ZÀ-Ý ]{3,60}?)\s+-\s+[A-ZÀ-Ý ]{3,40}\s+-\s+(?:PRESENCIAL|EAD|A DIST[ÂA]NCIA|SEMIPRESENCIAL)\s+-\s+(BACHARELADO|LICENCIATURA|TECN[ÓO]LOG\w*)", texto, re.M)
        if m_sis:
            curso_rotulado = f"{m_sis.group(2).capitalize()} em {m_sis.group(1).title()}"
    if not curso_rotulado:  # diploma/certificado: "confere o título de BACHARELA EM SERVIÇO SOCIAL" ou "conclusão do Curso de SERVIÇO SOCIAL e outorga-lhe"
        m_tit = re.search(r"t[ií]tulo de (?:Bacharel(?:a)?|Licenciad[oa]|Mestre|Mestra|Doutor(?:a)?|Tecn[óo]log[oa])\s+em\s+(.+?)(?=\s+em vista|\s+tendo|,|\.|$)", flat, re.I) or \
            re.search(r"conclus[ãa]o do curso de\s+(.+?)(?=\s+em\s+\d|\s+e outorga|\s+outorga|,|\.|$)", flat, re.I)
        if m_tit and not re.search(r"(?i)\bem vista\b", m_tit.group(1)):
            nome_curso = _clean_line(m_tit.group(1)).strip(" .,")
            curso_rotulado = format_event_name(nome_curso) if nome_curso.isupper() else nome_curso
    if not curso_rotulado:  # "HISTÓRICO ESCOLAR DE CURSO DE PÓS-GRADUAÇÃO LATO SENSU EM: ENFERMAGEM DO TRABALHO": curso depois do "EM:"
        m_ls = re.search(r"(?:LATO SENSU|STRICTO SENSU|P[ÓO]S-GRADUA[ÇC][ÃA]O)\s+EM\s*:?\s*([A-ZÀ-Ý][A-ZÀ-Ý ]{4,60}?)(?=\s{2,}|\n|\s+PLANEJ|\s+CARGA|$)", texto)
        if m_ls:
            curso_rotulado = "Pós-graduação em " + format_event_name(m_ls.group(1).strip())
    if not curso_rotulado:  # "Psicologia - Bacharelado": curso e grau na mesma linha, sem rótulo
        m_cg = re.search(r"^\W*([A-ZÀ-Ý][A-Za-zÀ-ÿ ,]{3,60}?)\s*[-–]\s*(Bacharelado|Licenciatura|Tecn[óo]log\w*)\s*$", texto, re.M)
        if m_cg:
            curso_rotulado = f"{m_cg.group(2).capitalize()} em {m_cg.group(1).strip()}"
    m = None if curso_rotulado else re.search(r"grau de (?:Doutor(?:a)?|Mestre|Mestra|Bacharel|Licenciad[oa]|Especialista)\s+(?:em\s+)?(.+?)(?:\s+a\s+[A-ZÀ-Ý]|,|\.|$)", flat, re.I)
    if not m and not curso_rotulado:
        m = re.search(r"(?:concluiu o curso de|curso de|conclus[aã]o do curso de)\s+([^,.\n]+?)(?:\s+(?:com\s+tripla|com\s+carga|promovido|realizado|no\s+per[ií]odo|perfazendo)|,|\.|$)", flat, re.I)
    if not m:
        m = re.search(r"(?:aperfei[çc]oamento em|especializa[çc][ãa]o em|mestrado em|doutorado em|gradua[çc][ãa]o em)\s+([^,.\n]+?)(?:\s+(?:com\s+tripla|com\s+carga|promovido|realizado|no\s+per[ií]odo)|,|\.|$)", flat, re.I)
    if not m:
        m = re.search(r"curso\s*:\s*([^,.\n]+)", flat, re.I)
    if curso_rotulado:
        v["f_curso"] = _clean_line(curso_rotulado).strip(" .,")[:150]
    elif m and ":" not in m.group(1):  # valor com ':' é outro rótulo capturado por engano (ex.: "AUTORIZAÇÃO: RECONHECIMENTO: ...")
        v["f_curso"] = _clean_line(m.group(1)).strip(" .,")[:150]

    # 2. Instituição
    m_inst = re.search(r"promovido pel[oa]\s+([^,.\n]+)", flat, re.I)
    if not m_inst:
        m_inst = re.search(r"\b((?:Universidade|Instituto|Faculdade|Centro Universit[áa]rio|Associa[çc][ãa]o|Escola|Funda[çc][ãa]o|Sociedade|Academia)\s+[^,.\n]{3,120})", flat, re.I)
    if not re.search(r"promovido pel[oa]", flat, re.I):  # histórico/declaração: a instituição está no cabeçalho, antes de "Entidade realizada: UNIC..."
        for ln in texto.splitlines()[:6]:
            if re.match(r"^\W*(?:FACULDADE|UNIVERSIDADE|CENTRO UNIVERSIT[ÁA]RIO|INSTITUTO)\b[^\n]{3,80}$", ln.strip(), re.I):
                v["f_inst"] = format_event_name(_clean_line(ln).strip(" .,-"))[:150]
                m_inst = None
                break
    if m_inst:
        v["f_inst"] = _clean_line(m_inst.group(1)).strip(" .,")[:150]
    if not v.get("f_inst") or not re.search(r"(?i)universidade|faculdade|instituto|centro|escola|associa|funda", v["f_inst"]):
        # certificado de título: "O Diretor-Geral em exercício da FACUMINAS, no uso de suas atribuições, confere o título..."
        m_dir = re.search(r"(?:Diretor(?:a)?(?:-Geral)?(?: em exerc[ií]cio)?|Reitor(?:a)?)\s+d[aeo]s?\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ0-9 ]{2,60}?)(?=\s*[,.]|\s+no uso)", flat)
        if m_dir:
            v["f_inst"] = format_event_name(m_dir.group(1).strip()) if m_dir.group(1).isupper() else m_dir.group(1).strip()

    # 3. Carga Horária (Aperfeiçoamento / Especialização)
    carga, _ = _carga(flat)
    if carga:
        v["f_carga"] = carga
    else:
        m_carga = re.search(r"(\d{2,4})\s*horas?[/ -]aula|carga hor[áa]ria\s*(?:total\s+)?(?:de)?\s*:?\s*(\d{2,4})", flat, re.I)
        if m_carga:
            v["f_carga"] = (m_carga.group(1) or m_carga.group(2)).strip()

    # Situação do aluno: histórico "pré-concluinte/cursando" e declaração de matrícula são curso EM ANDAMENTO; nesses casos
    # não existe ano de conclusão (a data de emissão do documento e as portarias de autorização do curso não são conclusão).
    situacao = normalize(valor_do_rotulo(texto, ("Situação acadêmica", "Situação do aluno", "Situação")))
    # em histórico em tabela, rótulo e valor saem em linhas distantes: palavras de situação inequívocas valem em qualquer ponto
    situacao = situacao or " ".join(re.findall(r"pre-?concluinte|cursando|trancad[oa]", normalize(flat)))
    em_andamento = bool(re.search(r"pre-?concluinte|cursando|matriculad|ativo|regular|trancad|em andamento|em curso", situacao)) or \
        (not situacao and bool(re.search(r"matriculad[oa]|vinculad[oa]|em andamento|aluno\(a\)", flat, re.I))
         and not re.search(r"concluiu|conferiu o grau|conclu[ií]do|colou grau|diploma", flat, re.I))
    flat_dt = sem_referencias_legais(flat)  # datas de leis/portarias não são as do documento

    # 4. Período (Ano Início e Fim)
    par = par_de_datas(flat_dt)
    m_per = None if par else re.search(r"(?:per[ií]odo\s+de|per[ií]odo|de)\s+(?:[a-zçã]+\s+de\s+)?(?:\d{1,2}\s+de\s+[a-zç]+\s+de\s+)?(20\d{2}|199\d)\s+[aà]\s+(?:[a-zçã]+\s+de\s+)?(?:\d{1,2}\s+de\s+[a-zç]+\s+de\s+)?(20\d{2}|199\d)", flat, re.I)
    if par:
        v["f_ano_ini"] = par[0][2]
        if not em_andamento:
            v["f_ano_fim"] = v["f_ano_obten"] = par[1][2]
            v["f_mes_obten"] = par[1][1]
    elif m_per:
        v["f_ano_ini"] = m_per.group(1)
        if not em_andamento:
            v["f_ano_fim"] = v["f_ano_obten"] = m_per.group(2)
    elif not em_andamento:
        datas = _datas(flat_dt)
        if datas:
            v["f_mes_obten"], v["f_ano_obten"], v["f_ano_fim"] = datas[0][1], datas[0][2], datas[0][2]
        else:
            ano = _ano_unico(flat_dt)
            if ano:
                v["f_ano_obten"] = v["f_ano_fim"] = ano

    # Histórico escolar: o ingresso aparece como "ANO/SEM: 2021/1" (ou o primeiro período cursado, "2021.1")
    if not v.get("f_ano_ini"):
        m_ing = re.search(r"ANO/SEM:\s*(20\d{2}|199\d)", flat, re.I) or re.search(r"ingresso\D{0,40}(20\d{2}|199\d)", flat, re.I) or \
            re.search(r"per[ií]odo letivo inicial\W{0,6}(20\d{2}|199\d)|ano/per[ií]odo inicial\W{0,6}(20\d{2}|199\d)", flat, re.I)
        if m_ing:
            v["f_ano_ini"] = m_ing.group(1)

    # 5. Status do curso e bolsa
    if em_andamento:
        v["F_STATUS"] = "em andamento"
        v["f_status"] = "em andamento"
    elif re.search(r"concluiu|conferiu|diploma|conclu[ií]do|certificado de conclus", flat, re.I) or v.get("f_ano_obten"):
        v["F_STATUS"] = "concluído"
        v["f_status"] = "concluído"

    v["F_BOLSA"] = "Não"

    return v, ["Instituição e curso são campos de busca controlada no Lattes: confira antes de confirmar."]


def ler_generico_spec(item_id: str) -> TipoLeitor:
    """Leitor genérico guiado pelos nomes de campos do spec (itens sem leitor específico ainda)."""
    def _ler(texto: str, usuario: str):
        flat = _clean_line(texto)
        spec = especificacao(item_id) or {}
        nomes = {c["name"] for v_ in spec.get("variantes", [])[:1] for c in v_.get("campos", [])}
        v: dict[str, Any] = {}
        ano = _ano_unico(flat) or (m_ano.group(1) if (m_ano := re.search(r"\b(20\d{2}|199\d)\b", flat)) else "")
        datas = _datas(flat)
        ma = _mes_ano(flat)
        m_doi = re.search(r"\b(10\.\d{4,9}/[^\s,;\"'<>]+)", flat)
        m_isbn = re.search(r"ISBN\s*[:.]?\s*([0-9][0-9\-Xx ]{8,19}[0-9Xx])", flat, re.I)
        m_issn = re.search(r"ISSN\s*[:.]?\s*([0-9]{4}-?[0-9]{3}[0-9Xx])", flat, re.I)
        m_reg = re.search(r"\b(?:BR|DI)[\s\d.\-/]{8,25}\b", flat) or re.search(r"\bn[º°]\s*([0-9\-]{4,20})\b", flat, re.I)
        m_tit = re.search(r"[\"“”']([^\"“”']{5,200})[\"“”']", flat) or re.search(r"(?:T[ií]tulo|Marca)\s*:\s*([^.\n]{3,200})", flat, re.I)
        m_comite = re.search(r"\b(Comit[êe]\s+de\s+Assessoramento[^,.\n]{2,100})", flat, re.I)
        m_inst = re.search(r"\b((?:Universidade|Instituto|Faculdade|Centro Universit[áa]rio|Funda[çc][ãa]o|Empresa)\s+[^,.\n]{3,120})", flat)
        m_cid = re.search(r"\bem\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat)
        m_jor = re.search(r"\b(?:no|na)\s+(?:jornal|revista|boletim)\s+([A-ZÀ-Ý][^,.\n]{3,120})", flat, re.I)
        m_idi_orig = re.search(r"traduziu\s+d[oa]\s+(ingl[êe]s|espanhol|franc[êe]s|alem[ãa]o|italiano|portugu[êe]s)", flat, re.I)
        idi_map = {"ingles": "Inglês", "espanhol": "Espanhol", "frances": "Francês", "alemao": "Alemão", "italiano": "Italiano", "portugues": "Português"}
        m_nat_bib = re.search(r"\b(resenha|pref[áa]cio|posf[áa]cio|boletim|folheto|cat[áa]logo|apostila|material did[áa]tico|regimento)\b", flat, re.I)
        m_ling = re.search(r"\b(Python|JavaScript|Java|C\+\+|C#|R|SQL|PHP|TypeScript|MATLAB)\b", flat, re.I)
        m_fin = re.search(r"(?:finalidade:\s*([^.\n]{3,160})|\b(uso interno|divulga[çc][ãa]o cient[íi]fica|ensino|pesquisa)\b)", flat, re.I)
        m_prod_tit = re.search(r"\bProduto\s*:\s*([^.\n]{4,200})", flat, re.I)
        m_cit = re.search(r"(?:Total de cita[çc][õo]es|Cita[çc][õo]es(?:\s+recebidas)?|Times cited)\s*:\s*(\d+)", flat, re.I)
        m_trab = re.search(r"(?:Documentos|Publications|Trabalhos)\s*:\s*(\d+)", flat, re.I)
        m_base = re.search(r"\bBase\s*:\s*([^.\n]{2,120})", flat, re.I)
        m_nome = re.search(r"\bNome\s*:\s*([^.\n]{4,120})", flat)
        m_cep = re.search(r"\bCEP\s*:?\s*([0-9]{5}-?[0-9]{3})\b", flat, re.I)
        m_fone = re.search(r"\btelefone\s*:?\s*([0-9()\- ]{8,20})", flat, re.I)
        m_rua = re.search(r"\b((?:Avenida|Rua|Alameda|Pra[çc]a)[^,\n]{3,100}(?:,\s*\d+)?)", flat, re.I)
        m_cid_uf = re.search(r",\s*([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat)
        tit = _clean_line((m_tit or m_prod_tit).group(1)).strip(" \"“”.,") if (m_tit or m_prod_tit) else _clean_line(texto.splitlines()[0] if texto.strip() else "")[:180]
        ext = {
            "f_titulo": tit, "f_titulo_cap": tit, "f_tit_obra": tit, "F_TEXTO": flat[:2000],
            "f_ano": ano, "f_ano_ini": ano, "F_ANO_INIC": ano,
            "f_data": _fmt(datas[0]) if datas else "", "f_dta_dep": _fmt(datas[0]) if datas else "",
            "f_dta_conc": _fmt(datas[-1]) if datas else "", "f_mes_ini": ma[0][0] if ma else "",
            "f_cod_doi": m_doi.group(1).rstrip(".,;)") if m_doi else "",
            "f_isbn": re.sub(r"[^0-9Xx]", "", m_isbn.group(1).upper())[:13] if m_isbn else "",
            "f_issn": re.sub(r"[^0-9Xx]", "", m_issn.group(1).upper())[:8] if m_issn else "",
            "f_cod_reg": re.sub(r"\s+", "", (m_reg.group(1) if m_reg.lastindex else m_reg.group(0)))[:16] if m_reg else "",
            "f_comite": _clean_line(m_comite.group(1)).strip(" .,")[:150] if m_comite else "",
            "f_inst": _clean_line(m_inst.group(1)).strip(" .,")[:150] if m_inst else "",
            "f_nme_agencia": _clean_line(m_inst.group(1)).strip(" .,")[:150] if m_inst else "",
            "f_cidade": f"{m_cid.group(1).strip()} - {m_cid.group(2)}" if m_cid else "",
            "f_cidade_ed": m_cid.group(1).strip()[:30] if m_cid else "",
            "f_titulo_periodico": _clean_line(m_jor.group(1)).strip(" .,")[:150] if m_jor else "",
            "F_IDIOMA_OBRA": idi_map.get(normalize(m_idi_orig.group(1)), "") if m_idi_orig else "",
            "f_natureza": m_nat_bib.group(1).capitalize() if m_nat_bib else "",
            "f_plataforma": m_ling.group(1) if m_ling else "",
            "f_finalidade": _clean_line(m_fin.group(1) or m_fin.group(2)).strip(" .,")[:255] if m_fin else "",
            "F_SUB_PROD": "Outra" if item_id == "produto" else "",
            "f_qtd_citacoes": m_cit.group(1) if m_cit else "",
            "f_qtd_trabalhos": m_trab.group(1) if m_trab else "",
            "f_txt_base": _clean_line(m_base.group(1)).strip(" .,")[:150] if m_base else "",
            "f_nome": _clean_line(m_nome.group(1)).strip(" .,")[:150] if m_nome else "",
            "f_pais_nacio": "Brasil" if re.search(r"brasileir[ao]", flat, re.I) else "",
            "f_pais_i": "Brasil" if m_cep else "",
            "f_cep_i": m_cep.group(1) if m_cep else "",
            "f_fone_i": _clean_line(m_fone.group(1)).strip(" .,") if m_fone else "",
            "f_rua_i": _clean_line(m_rua.group(1)).strip(" .,")[:150] if m_rua else "",
            "f_munic_i": m_cid_uf.group(1).strip() if m_cid_uf else "",
            "f_estado_i": m_cid_uf.group(2).strip() if m_cid_uf else "",
        }
        for n in nomes:
            if ext.get(n):
                v[n] = ext[n]
        return v, ["Preenchimento automático genérico a partir do texto; revise todos os campos antes de enviar ao Lattes."]
    return _ler


LEITORES.update(LEITORES_ONDA2)
LEITORES["livro_capitulo"] = ler_livro_capitulo
LEITORES["formacao_academica"] = ler_formacao_academica
from . import ids_especificados  # noqa: E402
for _item_id in ids_especificados():
    LEITORES.setdefault(_item_id, ler_generico_spec(_item_id))

PADROES_COMUNS = {"f_tpo_pesq_emp": "Não", "f_sta_inovacao": "Não", "f_pais": "Brasil", "f_pais_inst": "Brasil", "F_IDIOMA": "Português", "F_RELEV": "não", "F_STA_DIVULGACAO_CIENTIFICA": "não"}


def aplicar_padroes(item_id: str, valores: dict[str, Any], variante: str | None = None) -> dict[str, Any]:
    """Completa com valores-padrão da curadoria o que o documento não trouxe."""
    spec = especificacao(item_id) or {}
    for var in [x for x in spec.get("variantes", []) if variante is None or x["variante"] == variante]:
        for c in var["campos"]:
            padrao = c.get("padrao") or PADROES_COMUNS.get(c["name"])
            if not valores.get(c["name"]) and padrao:
                ops = c.get("opcoes") or {}
                if ops and padrao not in ops:  # "não" -> "Não": confere ignorando maiúsculas
                    padrao = next((o for o in ops if str(o).lower() == str(padrao).lower()), padrao)
                valores[c["name"]] = padrao
    return valores


def ler(item_id: str, texto: str, usuario: str = "") -> dict[str, Any] | None:
    """Resposta genérica de um item especificado: valores por campo + avisos + obrigatórios que faltam."""
    spec = especificacao(item_id)
    fn = LEITORES.get(item_id)
    if not spec or not fn:
        return None
    valores, notas = fn(texto, usuario)
    return montar_resposta(item_id, texto, valores, notas)


def de_registro_antigo(item_id: str, rec: dict) -> dict[str, Any] | None:
    """Abre um registro no formato antigo (caderno de resumos, histórico) no formulário gerado pelo spec."""
    if item_id == "orientacao":  # o formulário antigo era um só; o Lattes tem dois (concluída e em andamento)
        item_id = "orientacao_andamento" if "andamento" in str(rec.get("situacao_orientacao", "")).lower() else "orientacao_concluida"
    fn = {"anais": ler_anais_registro, "artigo": ler_artigo_registro, "apresentacao": ler_apresentacao_registro,
          "orientacao_concluida": ler_orientacao_registro, "orientacao_andamento": ler_orientacao_registro}.get(item_id)
    if not fn:
        return None
    valores, notas = fn(rec)
    return montar_resposta(item_id, "", valores, notas)


def montar_resposta(item_id: str, texto: str, valores: dict[str, Any], notas: list[str]) -> dict[str, Any]:
    spec = especificacao(item_id)
    nome_var = valores.pop("__variante", None)
    sug = sugerir_variante(item_id, texto, valores)
    if not nome_var:
        nome_var = sug["variante"]
    valores = aplicar_padroes(item_id, {k: v for k, v in valores.items() if v not in ("", None)}, nome_var)
    var = next((x for x in spec["variantes"] if x["variante"] == nome_var), spec["variantes"][0])
    def obrigatorio_agora(c):
        if c.get("mostrar_quando"):
            return False  # campo condicional: só é exigido se o gatilho estiver acionado (o leitor não aciona gatilhos)
        oq = c.get("obrigatorio_quando")
        if oq:
            return str(valores.get(oq["name"], "")) == oq["valor"]  # ex.: Ano fim só quando a situação é "Concluído"
        return bool(c["obrigatorio"])
    faltam = [c["rotulo"] for c in var["campos"] if obrigatorio_agora(c) and not c.get("automatico") and not valores.get(c["name"])]
    from itens.sugestoes import grades_para  # grades (participantes, palavras-chave, áreas) sugeridas a partir do documento
    grades, notas_g = grades_para(item_id, texto, valores, {g["chave"] for g in var.get("grades", [])})
    valores.update({k: x for k, x in grades.items() if not valores.get(k)})  # o que o leitor já trouxe (ex.: palavras-chave do PDF) vale mais que a sugestão
    notas = list(notas) + notas_g
    out = {"item": item_id, "variante": var["variante"], "valores": valores, "notas": notas, "faltam_obrigatorios": faltam}
    if len(spec["variantes"]) > 1:
        out["variantes"] = sug["opcoes"]
        out["motivo_variante"] = sug["motivo"] if sug["variante"] == var["variante"] else ""
    return out
