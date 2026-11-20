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
from .variantes import sugerir_variante

TipoLeitor = Callable[[str, str], tuple[dict[str, Any], list[str]]]

NATUREZA_EVENTO = [("congresso", "Congresso"), ("seminario", "Seminário"), ("simposio", "Simpósio"), ("oficina", "Oficina"),
                   ("encontro", "Encontro"), ("jornada", "Encontro"), ("olimpiada", "Olimpíada"), ("feira", "Feira"),
                   ("exposicao", "Exposição"), ("reuniao", "Encontro")]


def _evento(flat: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = re.search(r"participa[cç][aã]o\s+(?:no|na|em|do|da)\s+(.+?)(?:,\s*realizad|\s+realizad|,\s*no per[ií]odo|$)", flat, re.I)
    if m:
        full = _clean_line(m.group(1))
        primeiro = re.match(r"(.+?\([^)]{2,15}\))(?:,|\s|$)", full)
        out["nome"] = (primeiro.group(1) if primeiro else full)[:255]
        out["nome_completo"] = full[:400]
    if "nome" not in out:
        m = re.search(rf"\b(?:no|na|do|da|em)\s+((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;]*?\([A-Z0-9]{{2,12}}\))", flat) or \
            re.search(rf"\b(?:no|na|do|da|em)\s+((?:[IVXLCDM]+|\d+[ºª°]?)\s+(?:{EVENT_WORDS})[^,;.]{{5,140}})", flat) or \
            re.search(rf"\b(?:no|na|do|da|em)\s+((?:{EVENT_WORDS})\s+[^,;.]{{5,140}})", flat)
        if m:
            out["nome"] = _clean_line(m.group(1))[:255]
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
    m = re.search(r"cidade de\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat) or \
        re.search(r"\bem\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ' ]{2,40}?)\s*[-–/]\s*([A-Z]{2})\b", flat)
    if m:
        out["cidade"] = f"{m.group(1).strip()} - {m.group(2)}"
    m = re.search(r"realizad[oa]\s+(?:pel[ao]s?|por)\s+(.+?)(?:,\s*no per[ií]odo|\s+no per[ií]odo|,\s*em\s)", flat, re.I)
    if m:
        out["promotora"] = _clean_line(m.group(1))[:255]
    return out


def _carga(flat: str) -> tuple[str, str]:
    m = re.search(r"carga hor[aá]ria(?: total)?(?: de|:)?\s*(\d{1,4})\s*(horas?|h\b|dias?|semanas?)?", flat, re.I)
    if not m:
        m = re.search(r"(\d{1,4})\s*(horas?|h)\s*(?:de carga|/aula|-aula|aula)", flat, re.I)
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
    m = re.search(r"(?:realizado|promovido|oferecido|ministrado)\s+(?:pel[ao]s?|por)\s+(.+?)(?:,|\s+no per|\s+com\s+carga|\.|$)", flat, re.I)
    v: dict[str, Any] = {
        "f_curso": _titulo_curso(flat), "f_carga": carga, "f_inst": _clean_line(m.group(1))[:255] if m else "",
        "f_nivel": "Extensão Universitária" if "extensao" in low else "Curso De Curta Duração",
        "F_STATUS": "incompleto" if re.search(r"n[aã]o conclu|incompleto|cursando|em andamento", low) else "concluído",
    }
    n = []
    for k, msg in (("f_curso", "Nome do curso não identificado."), ("f_inst", "Instituição não identificada.")):
        if not v[k]:
            n.append(msg)
    n.append("Ano de início/término e demais datas ficam na aba de período do Lattes; confira.")
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
        m = re.search(r"(?:Tese|Disserta[çc][ãa]o|Monografia|Trabalho)(?: de Conclus[ãa]o)?[^.]{0,50}?\bde\s+([A-ZÀ-Ý]{2,}(?: [A-ZÀ-Ý]{2,}| d[aeo]s?)+)\s+com\s+a\s+(?:tese|disserta)", flat)
    if m:
        cand = " ".join(w.capitalize() if w.lower() not in ("da", "de", "do", "das", "dos", "e") else w.lower() for w in m.group(1).split())
    titulo = ""
    m = re.search(r"T[ií]tulo(?: d[aeo]s?\s+\w+)?:\s*[\"“”](.+?)[\"“”]", flat) or \
        re.search(r"(?:tese|disserta[çc][ãa]o|monografia|trabalho)\s+intitulad[oa]:?\s*[\"“”]?(.+?)[\"“”]?,\s*no\s+(?:Programa|Curso)", flat, re.I)
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
    v: dict[str, Any] = {"f_titulo": nome[:255], "f_agencia": evento[:255], "f_ano": _ano_data(flat)}
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
    m = re.search(r"intitulad[oa]\s+[\"“]?(.+?)[\"”]?,\s*(?:coordenad|sob a coordena|desenvolvid|executad|de responsabilidade)", flat, re.I)
    titulo = sentence_title(m.group(1).strip(" \"“”.")) if m else ""
    ano = ""
    md = re.search(r"\d{1,2}\s+de\s+[a-zç]+\s+de\s+(20[0-3]\d|199\d)", flat, re.I)
    if md:
        ano = md.group(1)
    m = re.search(r"coordenad[oa]\s+pel[oa]\s+(?:Professor[a]?\s+|Prof\.?\s+|Dr\.?\s+)*([A-ZÀ-Ý][\wÀ-ÿ' ]{4,70}?)\s*,\s*(?:d[aoe]s?\s+)?(.+?),\s*vinculad[oa]\s+(?:a[o]?|à)\s+(.+?),\s*d[aoe]s?\s+(Universidade[^.,]+)", flat)
    coord, orgao, centro, inst = (m.group(1), m.group(2), m.group(3), m.group(4)) if m else ("", "", "", "")
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
    m = re.search(r"T[ií]tulo da Inven[çc][ãa]o ou Modelo de Utilidade(?: \(54\))?:\s*(.+?)\s+Resumo:", flat)
    titulo = sentence_title(m.group(1)) if m else ""
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
    m = re.search(r"\b(\d{2})/(\d{2})/(20[0-3]\d)\b", flat)
    dep_data = f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else ""
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
    return ler_anais_registro(parse_evidence_text(texto), texto)


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


from .leitores_onda2 import LEITORES_ONDA2  # noqa: E402

LEITORES.update(LEITORES_ONDA2)

PADROES_COMUNS = {"f_tpo_pesq_emp": "Não", "f_sta_inovacao": "Não", "f_pais": "Brasil", "F_IDIOMA": "Português", "F_RELEV": "não", "F_STA_DIVULGACAO_CIENTIFICA": "não"}


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
