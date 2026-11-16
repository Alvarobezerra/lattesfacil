"""Leitores das ondas 2 a 4: declarações com vínculo, produção com identificador e registros.

Mesma convenção de itens/leitores.py: `ler_x(texto, usuario) -> (valores {campo_Lattes: valor legível}, avisos)`.
Nada é inventado: o que o documento não traz fica de fora e vira aviso. Escritos sobre o padrão comum desses
documentos e ainda sem amostras reais (ver docs/plano-implantacao-itens.md, passo 1 e critério 1).
"""
from __future__ import annotations

import re
from typing import Any

from caderno import normalize
from certificado import sentence_title
from extractor import _clean_line

MESES = {"janeiro": "01", "fevereiro": "02", "marco": "03", "abril": "04", "maio": "05", "junho": "06", "julho": "07",
         "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"}
_MES_RX = "|".join(MESES)


def _datas(flat: str) -> list[tuple[str, str, str]]:
    """Datas do texto em ordem de aparição: (dia, mês 'MM', ano). Aceita '5 de março de 2024' e '05/03/2024'."""
    achados: list[tuple[int, tuple[str, str, str]]] = []
    for m in re.finditer(r"\b(\d{1,2})\s*(?:º|°)?\s+de\s+([A-Za-zçÇãÃéÉ]+)\s+de\s+(\d{4})", flat):
        mes = MESES.get(normalize(m.group(2)))
        if mes:
            achados.append((m.start(), (m.group(1).zfill(2), mes, m.group(3))))
    for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", flat):
        achados.append((m.start(), (m.group(1).zfill(2), m.group(2).zfill(2), m.group(3))))
    return [d for _, d in sorted(achados)]


def _fmt(d: tuple[str, str, str]) -> str:
    return f"{d[0]}/{d[1]}/{d[2]}"


def _ano_unico(flat: str) -> str:
    datas = _datas(flat)
    if datas:
        return datas[0][2]
    m = re.search(r"\b(20[0-3]\d|199\d)\b", flat)
    return m.group(1) if m else ""


def _mes_ano(flat: str) -> list[tuple[str, str]]:
    """Meses/anos citados: '03/2022', 'março de 2022'."""
    out: list[tuple[int, tuple[str, str]]] = []
    for m in re.finditer(r"(?<![\d/])(\d{1,2})/(\d{4})\b", flat):
        if 1 <= int(m.group(1)) <= 12:
            out.append((m.start(), (m.group(1).zfill(2), m.group(2))))
    for m in re.finditer(rf"\b({_MES_RX})\s+(?:de\s+)?(\d{{4}})", normalize(flat)):
        out.append((m.start(), (MESES[m.group(1)], m.group(2))))
    return [x for _, x in sorted(out)]


def _periodo(flat: str) -> dict[str, str]:
    """Início/fim de vínculo ou função: 'de 03/2020 a 05/2023', 'desde 2020', 'atualmente'."""
    low = normalize(flat)
    out: dict[str, str] = {}
    ma = _mes_ano(flat)
    m = re.search(r"(?:de|desde|a partir de|periodo de)\s+(?:\d{1,2}/)?(\d{4})\s+(?:a|ate)\s+(?:\d{1,2}/)?(\d{4})", low)
    if len(ma) >= 2 and re.search(r"\b(?:a|ate)\b", low):
        out.update(f_mes_ini=ma[0][0], f_ano_ini=ma[0][1], f_mes_fim=ma[1][0], f_ano_fim=ma[1][1], f_status="Anterior (finalizado)")
    elif m:
        out.update(f_ano_ini=m.group(1), f_ano_fim=m.group(2), f_status="Anterior (finalizado)")
    elif ma:
        out.update(f_mes_ini=ma[0][0], f_ano_ini=ma[0][1])
    else:
        m = re.search(r"\b(?:desde|a partir d[eo]|iniciou em|admitid[oa] em|nomead[oa] em|em exercicio desde)\s+(?:[^.]{0,25}?)?(\d{4})", low)
        if m:
            out["f_ano_ini"] = m.group(1)
        else:
            d = _datas(flat)
            if d:
                out.update(f_mes_ini=d[0][1], f_ano_ini=d[0][2])
    if re.search(r"atualmente|ate o presente|ate hoje|em exercicio|exerce|permanece|continua", low) and not out.get("f_ano_fim"):
        out["f_status"] = "Atual (não finalizado)"
    return out


def _revista(flat: str) -> str:
    m = re.search(r"\b((?:Revista|Journal|Peri[óo]dico|Anais)\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ý][^,.;\"“”]{3,140})", flat) or         re.search(r"(?:peri[óo]dico|revista|journal)\s+[\"“”]?([A-ZÀ-Ý][^,.;\"“”]{4,140})", flat)
    return _clean_line(m.group(1)).strip(" -–") if m else ""


# ------------------------------------------------------------------ onda 2: declarações com vínculo

def ler_revisor_periodico(texto: str, usuario: str):
    flat = _clean_line(texto)
    revista = _revista(flat)
    per = _periodo(flat)
    if not per and _ano_unico(flat):
        per = {"f_ano_ini": _ano_unico(flat)}
    v: dict[str, Any] = {"f_nme_agencia": revista, **per}
    n = ["Periódico é cadastro controlado do Lattes: o preenchimento procura pelo nome; se não achar, use a lupa."]
    if not revista:
        n.append("Nome do periódico não identificado.")
    if not per.get("f_ano_ini"):
        n.append("Ano de início da atividade de revisor não identificado.")
    n.append("Se o documento comprova uma revisão pontual, o ano é o da revisão; ajuste o período se a atuação for contínua.")
    return v, n


def ler_corpo_editorial(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    revista = _revista(flat)
    funcao = next((nome for rx, nome in [
        (r"editor[- ]chefe|editor in chief", "Editor-chefe"), (r"editor associado|associate editor", "Editor associado"),
        (r"editor de secao|section editor", "Editor de seção"), (r"conselho editorial|editorial board|conselheiro", "Membro do conselho editorial"),
        (r"corpo editorial", "Membro do corpo editorial"), (r"\beditor\b", "Editor")] if re.search(rx, low)), "")
    per = _periodo(flat)
    if not per and _ano_unico(flat):
        per = {"f_ano_ini": _ano_unico(flat)}
    v: dict[str, Any] = {"f_nme_agencia": revista, **per}
    if funcao:
        v["f_outras_inf"] = f"Função: {funcao}."
    n = ["Periódico é cadastro controlado do Lattes: o preenchimento procura pelo nome; se não achar, use a lupa."]
    if not revista:
        n.append("Nome do periódico não identificado.")
    n.append(f"Função citada: {funcao}; registrada em 'Outras informações'." if funcao else "Função no corpo editorial não identificada.")
    return v, n


def ler_atuacao_profissional(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    m = re.search(r"(Universidade [A-ZÀ-Ý][^,.;()]{3,80}|Instituto Federal [^,.;()]{3,80}|Funda[çc][ãa]o [A-ZÀ-Ý][^,.;()]{3,80}|"
                  r"Secretaria [^,.;()]{3,80}|Prefeitura [^,.;()]{3,60}|Hospital [A-ZÀ-Ý][^,.;()]{3,60}|Empresa [A-ZÀ-Ý][^,.;()]{3,60})", flat)
    inst = _clean_line(m.group(1)) if m else ""
    m = re.search(r"(?:cargo|fun[çc][ãa]o|exerce o cargo de|exerce a fun[çc][ãa]o de)\s*(?:de|:)?\s+([A-ZÀ-Ý][^,.;()]{3,80})", flat, re.I)
    cargo = _clean_line(m.group(1)).strip(" -–") if m else ""
    servidor = bool(re.search(r"servidor(a)? (publico|publica|efetivo|efetiva)|estatutari", low))
    empregado = servidor or bool(re.search(r"efetivo|\bclt\b|celetista|vinculo empregaticio|concursad", low))
    tipo = "Servidor público" if servidor else "Celetista" if re.search(r"\bclt\b|celetista", low) else "Outro"
    carga = re.search(r"(\d{2})\s*(?:h|horas)\s*(?:semanais|/semana)|carga horaria semanal(?: de)?\s*(\d{2})", low)
    per = _periodo(flat)
    v: dict[str, Any] = {"f_inst": inst, "f_enqua": cargo, "f_stavinc": "Sim" if empregado else "Não", "f_vinc": tipo,
                         "f_carga": (carga.group(1) or carga.group(2)) if carga else "", **per}
    if "dedicacao exclusiva" in low:
        v["f_regime"] = "Dedicação exclusiva"
    n = []
    if not inst:
        n.append("Instituição não identificada (é cadastro controlado do Lattes).")
    if not cargo:
        n.append("Enquadramento funcional (cargo/função) não identificado.")
    if not per.get("f_ano_ini"):
        n.append("Data de início do vínculo não identificada.")
    n.append("Tipo de vínculo e vínculo empregatício foram deduzidos do texto; confira antes de salvar.")
    return v, n


IDIOMAS = [("ingles", "Inglês"), ("english", "Inglês"), ("espanhol", "Espanhol"), ("spanish", "Espanhol"), ("frances", "Francês"),
           ("francais", "Francês"), ("italiano", "Italiano"), ("alemao", "Alemão"), ("deutsch", "Alemão"), ("mandarim", "Chinês"),
           ("chines", "Chinês"), ("japones", "Japonês"), ("libras", "Língua brasileira de sinais")]
NIVEL_CEFR = {"a1": "Pouco", "a2": "Pouco", "b1": "Razoavelmente", "b2": "Razoavelmente", "c1": "Bem", "c2": "Bem"}


def ler_idioma(texto: str, usuario: str):
    low = normalize(_clean_line(texto))
    idioma = next((nome for k, nome in IDIOMAS if re.search(rf"\b{k}\b", low)), "")
    if not idioma:
        idioma = ("Inglês" if re.search(r"toefl|ielts|cambridge|toeic", low) else "Espanhol" if re.search(r"\bdele\b|siele", low)
                  else "Francês" if re.search(r"\bdelf\b|\bdalf\b|\btcf\b", low) else "")
    cefr = re.search(r"\b(?:nivel|level|cefr)[:\s]*([abc][12])\b", low) or re.search(r"\b([abc][12])\b", low)
    nivel = NIVEL_CEFR.get(cefr.group(1), "") if cefr else ""
    origem = f"nível {cefr.group(1).upper()}" if cefr else ""
    if not nivel:
        m = re.search(r"toefl(?: ibt)?[^0-9]{0,30}(\d{2,3})", low)
        if m:
            nivel, origem = ("Bem" if int(m.group(1)) >= 95 else "Razoavelmente" if int(m.group(1)) >= 60 else "Pouco"), f"nota TOEFL {m.group(1)}"
        m = re.search(r"ielts[^0-9]{0,30}(\d(?:[.,]\d)?)", low)
        if m:
            nota = float(m.group(1).replace(",", "."))
            nivel, origem = ("Bem" if nota >= 7 else "Razoavelmente" if nota >= 5 else "Pouco"), f"nota IELTS {m.group(1)}"
    v: dict[str, Any] = {"F_COD_IDIOMA": idioma}
    n = []
    if not idioma:
        n.append("Idioma não identificado.")
    if nivel:
        for rad in ("F_LE", "F_CONVERSA", "F_ESCREVE", "F_COMPR"):
            v[rad] = nivel
        n.append(f"{origem.capitalize()} convertido para '{nivel}' em ler, falar, escrever e compreender; o certificado raramente "
                 "separa as habilidades, ajuste se houver nota por habilidade.")
    else:
        n.append("Nível de proficiência não identificado; informe as habilidades (Pouco, Razoavelmente, Bem).")
    return v, n


def ler_licenca(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    tipo = "Maternidade" if "maternidade" in low else "Paternidade" if "paternidade" in low else "Adoção" if "adocao" in low else ""
    datas = _datas(flat)
    dias = re.search(r"(\d{2,3})\s*(?:\([^)]*\)\s*)?dias", low)
    v: dict[str, Any] = {"f_tipo_licenca": tipo}
    n = []
    if datas:
        v["f_dta_inicio"] = _fmt(datas[0])
    if len(datas) >= 2:
        v["f_dta_fim"] = _fmt(datas[1])
    if not tipo:
        n.append("Tipo de licença não identificado.")
    if not datas:
        n.append("Datas da licença não identificadas.")
    elif len(datas) < 2:
        n.append("Só uma data encontrada (usada como início)" +
                 (f"; o documento cita {dias.group(1)} dias, calcule a data final." if dias else "; informe a data final."))
    n.append("Data de nascimento/adoção da criança não é inferida do documento; informe se quiser constar.")
    n.append("Licença é dado sensível: o Lattes permite marcar como privado; confira antes de salvar.")
    return v, n


# ------------------------------------------------------------------ onda 3: produção com identificador

def ler_artigo_aceito(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    m = re.search(r"\b(10\.\d{4,9}/[^\s,;]+)", flat)
    doi = m.group(1).rstrip(".") if m else ""
    m = re.search(r"(?:manuscrito|artigo|trabalho|manuscript|paper)\s*(?:intitulad[oa]|titled|entitled)?:?\s*[\"“”]([^\"“”]{10,300})[\"“”]", flat, re.I)
    titulo = sentence_title(m.group(1).strip(" .")) if m else ""
    revista = _revista(flat)
    m = re.search(r"\bISSN[:\s]*(\d{4}-?\d{3}[\dXx])", flat)
    ingles = bool(re.search(r"\b(dear|we are pleased|accepted for publication|manuscript)\b", low))
    v: dict[str, Any] = {"f_cod_doi": doi, "f_titulo": titulo, "f_titulo_periodico": revista, "f_issn": m.group(1) if m else "",
                         "f_ano": _ano_unico(flat), "F_IDIOMA": "Inglês" if ingles else "Português"}
    n = []
    for k, msg in (("f_titulo", "Título do artigo não identificado."), ("f_titulo_periodico", "Periódico não identificado.")):
        if not v[k]:
            n.append(msg)
    if doi:
        n.append("DOI encontrado: o Lattes pode recuperar os demais dados pelo botão do DOI.")
    n.append("Ano previsto assumido como o ano da carta de aceite; ajuste se a edição sair em outro ano.")
    n.append("Idioma deduzido pelo texto da carta; confira o idioma do artigo.")
    return v, n


def ler_relatorio_tecnico(texto: str, usuario: str):
    flat = _clean_line(texto)
    low = normalize(flat)
    cod = "Consultoria" if "consultoria" in low else "Assessoria"
    m = re.search(r"(?:intitulad[oa]|t[ií]tulo)[:\s]+[\"“”]?(.+?)[\"“”]?(?:,|\.\s|\s+(?:realizad|elaborad|para a|para o|junto))", flat, re.I) or \
        re.search(r"(?:parecer|relat[óo]rio|laudo)\s+t[ée]cnico\s+(?:sobre|referente a|de)\s+(.{8,160}?)(?:,|\.\s|$)", flat, re.I)
    titulo = sentence_title(m.group(1).strip(" \"“”.")) if m else ""
    m = re.search(r"dura[çc][ãa]o(?: de)?\s*(\d{1,3})\s*meses|(\d{1,3})\s*meses", low)
    v: dict[str, Any] = {"F_COD_PROD": cod, "f_titulo": titulo, "f_ano": _ano_unico(flat), "f_duracao": (m.group(1) or m.group(2)) if m else ""}
    n = []
    if not titulo:
        n.append("Título do trabalho não identificado.")
    if not v["f_ano"]:
        n.append("Ano não identificado.")
    n.append(f"Natureza assumida como '{cod}'; confira (Assessoria ou Consultoria).")
    n.append("Autores/coautores são preenchidos na aba própria do Lattes.")
    return v, n


# ------------------------------------------------------------------ onda 4: registros

def ler_software_registro(texto: str, usuario: str):
    flat = _clean_line(texto)
    m = re.search(r"\bBR\s?5\d\s?\d{4}\s?\d{6}[-\s]?\d\b", flat)
    reg = _clean_line(m.group(0)) if m else ""
    if not reg:
        m = re.search(r"\b(?:processo|registro|n[úu]mero)[^0-9A-Z]{0,30}(BR[\s\d.\-/]{8,25})", flat, re.I)
        reg = _clean_line(m.group(1)) if m else ""
    m = re.search(r"T[ií]tulo(?: do programa)?(?: de computador)?:\s*(.+?)\s+(?:Data|Linguagem|Campo|Autor|Titular|Tipo|Resumo|Processo)", flat) or \
        re.search(r"programa de computador\s+(?:denominado|intitulado)\s+[\"“”]?(.+?)[\"“”]?[,.]", flat, re.I)
    titulo = sentence_title(m.group(1).strip(" \"“”.")) if m else ""
    m = re.search(r"Linguage(?:m|ns)(?: de programa[çc][ãa]o)?:\s*(.+?)(?:\s+(?:Campo|Tipo|Data|Titular|Autor|Resumo)|$)", flat)
    ling = _clean_line(m.group(1)) if m else ""
    datas = _datas(flat)
    cert = _fmt(datas[-1]) if datas else ""
    v: dict[str, Any] = {"f_cod_reg": reg, "f_inst": "INPI", "f_pais": "Brasil", "f_titulo": titulo, "f_plataforma": ling,
                         "f_dta_conc": cert, "f_natureza": "Computacional"}
    n = []
    if not reg:
        n.append("Número do registro não identificado.")
    if not titulo:
        n.append("Título do programa não identificado.")
    if not ling:
        n.append("Linguagens de programação não identificadas (obrigatório no Lattes).")
    if cert:
        n.append(f"Data do certificado assumida como a última data do documento ({cert}); confira.")
    n.append("Finalidade e potencial de inovação são obrigatórios no Lattes e não vêm no certificado: preencha na tela de revisão.")
    return v, n


LEITORES_ONDA2 = {
    "revisor_periodico": ler_revisor_periodico,
    "corpo_editorial": ler_corpo_editorial,
    "atuacao_profissional": ler_atuacao_profissional,
    "idioma": ler_idioma,
    "licenca": ler_licenca,
    "artigo_aceito": ler_artigo_aceito,
    "relatorio_tecnico": ler_relatorio_tecnico,
    "software_registro": ler_software_registro,
}
