"""Leitura do currículo exportado do Lattes (XML) e checagem de duplicatas.

O pesquisador baixa o XML (ou o ZIP que o contém) no próprio Lattes e envia ao LattesFácil. A leitura é tolerante:
em vez de depender de um caminho fixo por tipo de produção, percorre a árvore, reconhece o tipo pelo nome da tag e
junta os atributos de `DADOS-BASICOS-*` e `DETALHAMENTO-*` do mesmo item. Usa só a biblioteca padrão; DTD e entidades
externas são recusadas (XML vem de fora).
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from difflib import SequenceMatcher
from typing import Any
from xml.etree import ElementTree as ET

MAX_XML_BYTES = 40 * 1024 * 1024

# (regex sobre o nome da tag, categoria). Ordem importa: o primeiro que casa vence.
TIPOS: list[tuple[str, str]] = [
    (r"^ARTIGO-PUBLICADO$", "artigo"),
    (r"^ARTIGO-ACEITO-PARA-PUBLICACAO$", "artigo_aceito"),
    (r"^TRABALHO-EM-EVENTOS$", "trabalho_evento"),
    (r"^APRESENTACAO-DE-TRABALHO$", "apresentacao"),
    (r"^LIVRO-PUBLICADO-OU-ORGANIZADO$", "livro"),
    (r"^CAPITULO-DE-LIVRO-PUBLICADO$", "capitulo"),
    (r"^TEXTO-EM-JORNAL-OU-REVISTA$", "texto_jornal"),
    (r"^CURSO-DE-CURTA-DURACAO-MINISTRADO$", "curso_ministrado"),
    (r"^(CURSO-DE-CURTA-DURACAO|FORMACAO-COMPLEMENTAR-CURSO-DE-CURTA-DURACAO)$", "formacao_complementar"),  # o 2º é o nome real (XML do Lattes)
    (r"^(PATENTE|REGISTRO-OU-PATENTE)$", "patente"),
    (r"^SOFTWARE$", "software"),
    (r"^TRABALHO-TECNICO$", "trabalho_tecnico"),
    (r"^(PRODUTO-TECNOLOGICO|PROCESSOS-OU-TECNICAS)$", "produto_tecnologico"),
    (r"^PARTICIPACAO-EM-BANCA-DE-(MESTRADO|DOUTORADO|GRADUACAO|APERFEICOAMENTO-ESPECIALIZACAO|EXAME-QUALIFICACAO)$", "banca"),
    (r"^PARTICIPACAO-EM-BANCA-JULGADORA$", "banca"),
    (r"^(OUTRAS-ORIENTACOES-CONCLUIDAS|ORIENTACOES-CONCLUIDAS-PARA-(MESTRADO|DOUTORADO|POS-DOUTORADO))$", "orientacao_concluida"),
    (r"^ORIENTACAO-EM-ANDAMENTO-DE-.+$", "orientacao_andamento"),
    (r"^PROJETO-DE-PESQUISA$", "projeto"),
    # No XML real cada participação é um elemento próprio dentro do contêiner PARTICIPACAO-EM-EVENTOS-CONGRESSOS (que não pode casar:
    # casaria o contêiner inteiro como 1 item e perderia as participações).
    (r"^(PARTICIPACAO-EM-(CONGRESSO|ENCONTRO|OFICINA|SEMINARIO|SIMPOSIO|FEIRA|EXPOSICAO|FESTIVAL|OLIMPIADA)|OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS)$", "participacao_evento"),
    (r"^ORGANIZACAO-DE-EVENTO$", "organizacao_evento"),
    (r"^PREMIO-TITULO$", "premio"),
    (r"^ATUACAO-PROFISSIONAL$", "atuacao_profissional"),
    (r"^(GRADUACAO|ESPECIALIZACAO|MESTRADO|DOUTORADO|POS-DOUTORADO|APERFEICOAMENTO|LIVRE-DOCENCIA|MESTRADO-PROFISSIONALIZANTE|RESIDENCIA-MEDICA)$", "formacao_academica"),
    (r"^FORMACAO-COMPLEMENTAR-DE-EXTENSAO-UNIVERSITARIA$", "formacao_complementar"),
    # ondas ampliadas: só nomes de elementos-folha (um item por elemento). Um nome de contêiner aqui engoliria os filhos.
    (r"^(PREFACIO-POSFACIO|TRADUCAO|PARTITURA-MUSICAL|OUTRA-PRODUCAO-BIBLIOGRAFICA)$", "outra_producao_bibliografica"),
    (r"^(CARTA-MAPA-OU-SIMILAR|DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL|EDITORACAO|MANUTENCAO-DE-OBRA-ARTISTICA|MAQUETE|"
     r"ENTREVISTA-MESA-REDONDA-PROGRAMA-E-COMENTARIO|RELATORIO-DE-PESQUISA|REDE-SOCIAL-WEBSITE-BLOG|ASSESSORIA-CONSULTORIA|"
     r"EXTENSAO-TECNOLOGICA|OUTRA-PRODUCAO-TECNICA)$", "outra_producao_tecnica"),
    (r"^(ARTES-CENICAS|ARTES-VISUAIS|MUSICA|OUTRA-PRODUCAO-ARTISTICA-CULTURAL)$", "producao_artistica"),
]
_TIPOS = [(re.compile(p), c) for p, c in TIPOS]

_TITULO = ("TITULO-DO-ARTIGO", "TITULO-DO-TRABALHO", "TITULO-DO-LIVRO", "TITULO-DO-CAPITULO-DO-LIVRO", "TITULO", "NOME-CURSO",
           "NOME-DO-PROJETO", "NOME-DO-PREMIO-OU-TITULO", "NOME-DO-EVENTO", "NOME-INSTITUICAO", "TITULO-DA-DISSERTACAO-TESE",
           "TITULO-DO-TRABALHO-DE-CONCLUSAO-DE-CURSO", "TITULO-DO-TRABALHO-DE-INICIACAO-CIENTIFICA", "NOME-CURSO")
_ANO = ("ANO-DO-ARTIGO", "ANO-DO-TRABALHO", "ANO", "ANO-DE-CONCLUSAO", "ANO-DE-INICIO", "ANO-INICIO", "ANO-DA-DEFESA",
        "ANO-DE-OBTENCAO-DO-TITULO", "ANO-DE-REALIZACAO", "ANO-DE-REGISTRO", "ANO-DO-PREMIO")


def _norm(t: str) -> str:
    base = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", base).strip()


def _chave_titulo(t: str) -> str:
    return re.sub(r"\s+", " ", _norm(t))


def _tag(el: ET.Element) -> str:
    return el.tag.split("}")[-1]


def _abrir(dados: bytes) -> bytes:
    """Aceita o XML puro ou o ZIP exportado pelo Lattes (pega o 1º .xml, com limite de tamanho)."""
    if dados[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            for info in z.infolist():
                if info.filename.lower().endswith(".xml") and not info.is_dir():
                    if info.file_size > MAX_XML_BYTES:
                        raise ValueError("XML grande demais.")
                    return z.read(info)
        raise ValueError("O ZIP não contém um arquivo .xml.")
    return dados


def _primeiro(attrs: dict[str, str], chaves: tuple[str, ...]) -> str:
    for k in chaves:
        if attrs.get(k):
            return attrs[k].strip()
    return ""


def ler_curriculo(dados: bytes) -> dict[str, Any]:
    """XML do Lattes -> {"nome", "id_lattes", "itens": [{categoria, titulo, ano, doi, issn, isbn, ...}]}."""
    xml = _abrir(dados)
    if len(xml) > MAX_XML_BYTES:
        raise ValueError("XML grande demais.")
    if re.search(rb"<!DOCTYPE[^>]*\[|<!ENTITY", xml[:4096], re.I):
        raise ValueError("XML com DTD/entidades não é aceito.")
    try:
        raiz = ET.fromstring(xml)
    except ET.ParseError as e:
        raise ValueError(f"Arquivo não é um XML válido do Lattes ({e}).") from e
    if _tag(raiz) != "CURRICULO-VITAE":
        raise ValueError("O arquivo não parece ser um currículo Lattes (falta CURRICULO-VITAE).")
    dg = next((e for e in raiz if _tag(e) == "DADOS-GERAIS"), None)
    nome = dg.get("NOME-COMPLETO", "") if dg is not None else ""
    citacao = dg.get("NOME-EM-CITACOES-BIBLIOGRAFICAS", "") if dg is not None else ""
    itens: list[dict[str, Any]] = []
    desconhecidos: dict[str, int] = {}  # elementos com título que o leitor não classificou (aparecem no dashboard)

    def visitar(el: ET.Element, pai: str = "") -> None:
        cat = next((c for rx, c in _TIPOS if rx.match(_tag(el))), None)
        if not cat and _tag(el) == "OUTROS" and pai == "FORMACAO-COMPLEMENTAR":  # nome genérico: só vale dentro da formação complementar
            cat = "formacao_complementar"
        if (not cat and _tag(el) != "DADOS-GERAIS" and any(k in _TITULO for k in el.attrib)
                and not _tag(el).startswith(("DADOS-BASICOS", "DETALHAMENTO", "INFORMACAO-ADICIONAL-"))):  # INFORMACAO-ADICIONAL-*: metadado de curso/instituição
            desconhecidos[_tag(el)] = desconhecidos.get(_tag(el), 0) + 1
        if cat:
            attrs: dict[str, str] = dict(el.attrib)
            autores: list[str] = []
            for filho in el.iter():
                if filho is el:
                    continue
                t = _tag(filho)
                if t == "AUTORES":
                    autores.append(filho.get("NOME-COMPLETO-DO-AUTOR", ""))
                for k, v in filho.attrib.items():
                    attrs.setdefault(k, v)
            ano = _primeiro(attrs, _ANO)
            item = {"categoria": cat, "titulo": _primeiro(attrs, _TITULO), "ano": ano if ano.isdigit() else "",
                    "doi": attrs.get("DOI", "").strip(), "issn": attrs.get("ISSN", "").strip(),
                    "isbn": attrs.get("ISBN", "").strip(), "veiculo": _primeiro(attrs, ("TITULO-DO-PERIODICO-OU-REVISTA", "NOME-DO-EVENTO", "EDITORA", "NOME-DA-EDITORA")),
                    "autores": [a for a in autores if a], "ano_fim": attrs.get("ANO-FIM", "") or attrs.get("ANO-DE-CONCLUSAO", ""),
                    "tag": _tag(el), "seq": attrs.get("SEQUENCIA-PRODUCAO", "") or attrs.get("SEQUENCIA-FORMACAO", ""),
                    "natureza": attrs.get("NATUREZA", "")}
            if item["titulo"] or item["doi"]:
                itens.append(item)
            return  # não desce: já juntou os atributos dos filhos
        for filho in el:
            visitar(filho, _tag(el))

    visitar(raiz)
    perfil: dict[str, Any] = {"resumo": "", "idiomas": [], "areas": []}
    if dg is not None:
        for e in dg.iter():
            t = _tag(e)
            if t == "RESUMO-CV":
                perfil["resumo"] = e.get("TEXTO-RESUMO-CV-RH", "")
            elif t == "IDIOMA" and e.get("DESCRICAO-DO-IDIOMA"):
                perfil["idiomas"].append(e.get("DESCRICAO-DO-IDIOMA"))
            elif t == "AREA-DE-ATUACAO":  # grande área › área › subárea › especialidade (só o que estiver preenchido)
                a = " › ".join(p for p in (e.get(k, "").strip() for k in ("NOME-GRANDE-AREA-DO-CONHECIMENTO", "NOME-DA-AREA-DO-CONHECIMENTO",
                                                                         "NOME-DA-SUB-AREA-DO-CONHECIMENTO", "NOME-DA-ESPECIALIDADE")) if p)
                if a and a not in perfil["areas"]:
                    perfil["areas"].append(a)
    return {"nome": nome, "nome_citacao": citacao, "id_lattes": raiz.get("NUMERO-IDENTIFICADOR", ""),
            "atualizacao": raiz.get("DATA-ATUALIZACAO", ""), "atualizacao_iso": _data_atualizacao(raiz),
            "itens": itens, "perfil": perfil, "nao_classificados": desconhecidos}


def _data_atualizacao(raiz: ET.Element) -> str:
    """DATA-ATUALIZACAO (ddmmaaaa) + HORA-ATUALIZACAO (hhmmss), horário de Brasília -> ISO 8601 em UTC; '' se ilegível."""
    from datetime import datetime, timedelta
    d, h = raiz.get("DATA-ATUALIZACAO", ""), (raiz.get("HORA-ATUALIZACAO", "") or "000000").ljust(6, "0")[:6]
    try:
        return (datetime.strptime(d + h, "%d%m%Y%H%M%S") + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except ValueError:
        return ""


def formatar_doi(doi: str) -> str:
    m = re.search(r"10\.\d{4,9}/\S+", doi or "")
    return m.group(0).rstrip(".,;").lower() if m else ""


def _similar(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def procurar_duplicata(curriculo: dict[str, Any], candidato: dict[str, Any], limiar: float = 0.88) -> list[dict[str, Any]]:
    """Itens do currículo que parecem ser o mesmo que `candidato` ({titulo, ano, doi, categoria?}).

    Mesmo DOI = duplicata certa. Título muito parecido (e ano igual ou ausente) = provável. Não bloqueia nada: só avisa.
    """
    achados = []
    doi_c = formatar_doi(candidato.get("doi", ""))
    tit_c = _chave_titulo(candidato.get("titulo", ""))
    ano_c = str(candidato.get("ano", "") or "")
    for it in curriculo.get("itens", []):
        if doi_c and formatar_doi(it.get("doi", "")) == doi_c:
            achados.append({**it, "motivo": "mesmo DOI", "similaridade": 1.0})
            continue
        s = _similar(tit_c, _chave_titulo(it.get("titulo", "")))
        mesmo_ano = not ano_c or not it.get("ano") or ano_c == it["ano"]
        if s >= limiar and mesmo_ano:
            achados.append({**it, "motivo": "título muito parecido" + ("" if ano_c and it.get("ano") else " (ano não comparado)"),
                            "similaridade": round(s, 2)})
    achados.sort(key=lambda x: -x["similaridade"])
    return achados


def resumo(curriculo: dict[str, Any]) -> dict[str, Any]:
    cont: dict[str, int] = {}
    for it in curriculo["itens"]:
        cont[it["categoria"]] = cont.get(it["categoria"], 0) + 1
    return {"nome": curriculo["nome"], "id_lattes": curriculo["id_lattes"], "atualizacao": curriculo["atualizacao"],
            "total_itens": len(curriculo["itens"]), "por_categoria": cont}
