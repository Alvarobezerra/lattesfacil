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
# Nomes conferidos com a DTD oficial do Lattes (LMPLCurriculo.DTD). Só elementos-FOLHA de item entram aqui: um contêiner
# (PARTICIPACAO-EM-BANCA-JULGADORA, PARTICIPACAO-EM-EVENTOS-CONGRESSOS, ORIENTACOES-*...) casaria o grupo todo como 1 item e perderia os filhos.
TIPOS: list[tuple[str, str]] = [
    # produção bibliográfica
    (r"^ARTIGO-PUBLICADO$", "artigo"),
    (r"^ARTIGO-ACEITO-PARA-PUBLICACAO$", "artigo_aceito"),
    (r"^TRABALHO-EM-EVENTOS$", "trabalho_evento"),
    (r"^LIVRO-PUBLICADO-OU-ORGANIZADO$", "livro"),
    (r"^CAPITULO-DE-LIVRO-PUBLICADO$", "capitulo"),
    (r"^TEXTO-EM-JORNAL-OU-REVISTA$", "texto_jornal"),
    (r"^(PREFACIO-POSFACIO|TRADUCAO|PARTITURA-MUSICAL|OUTRA-PRODUCAO-BIBLIOGRAFICA)$", "outra_producao_bibliografica"),
    # produção técnica
    (r"^APRESENTACAO-DE-TRABALHO$", "apresentacao"),
    (r"^ORGANIZACAO-DE-EVENTO$", "organizacao_evento"),
    (r"^CURSO-DE-CURTA-DURACAO-MINISTRADO$", "curso_ministrado"),
    (r"^SOFTWARE$", "software"),
    (r"^(PATENTE|REGISTRO-OU-PATENTE)$", "patente"),  # REGISTRO-OU-PATENTE vem aninhado em OUTRA-PRODUCAO-TECNICA
    (r"^(CULTIVAR-PROTEGIDA|CULTIVAR-REGISTRADA|DESENHO-INDUSTRIAL|MARCA|TOPOGRAFIA-DE-CIRCUITO-INTEGRADO)$", "registro_propriedade"),
    (r"^TRABALHO-TECNICO$", "trabalho_tecnico"),
    (r"^(PRODUTO-TECNOLOGICO|PROCESSOS-OU-TECNICAS)$", "produto_tecnologico"),
    (r"^(CARTA-MAPA-OU-SIMILAR|DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL|EDITORACAO|MANUTENCAO-DE-OBRA-ARTISTICA|MAQUETE|"
     r"PROGRAMA-DE-RADIO-OU-TV|RELATORIO-DE-PESQUISA|MIDIA-SOCIAL-WEBSITE-BLOG|OUTRA-PRODUCAO-TECNICA)$", "outra_producao_tecnica"),
    # outra produção (artística/cultural e demais trabalhos). O CURSO-DE-CURTA-DURACAO sem prefixo é da produção artística, NÃO formação.
    (r"^(APRESENTACAO-DE-OBRA-ARTISTICA|APRESENTACAO-EM-RADIO-OU-TV|ARRANJO-MUSICAL|COMPOSICAO-MUSICAL|OBRA-DE-ARTES-VISUAIS|SONOPLASTIA|"
     r"OUTRA-PRODUCAO-ARTISTICA-CULTURAL|ARTES-CENICAS|ARTES-VISUAIS|MUSICA)$", "producao_artistica"),
    (r"^CURSO-DE-CURTA-DURACAO$", "curso_ministrado"),
    (r"^DEMAIS-TRABALHOS$", "demais_trabalhos"),
    (r"^(OUTRAS-ORIENTACOES-CONCLUIDAS|ORIENTACOES-CONCLUIDAS-PARA-(MESTRADO|DOUTORADO|POS-DOUTORADO))$", "orientacao_concluida"),
    # dados complementares
    (r"^(FORMACAO-COMPLEMENTAR-CURSO-DE-CURTA-DURACAO|FORMACAO-COMPLEMENTAR-DE-EXTENSAO-UNIVERSITARIA|MBA)$", "formacao_complementar"),  # + OUTROS (ver visitar)
    (r"^(PARTICIPACAO-EM-BANCA-DE-(MESTRADO|DOUTORADO|GRADUACAO|APERFEICOAMENTO-ESPECIALIZACAO|EXAME-QUALIFICACAO)|OUTRAS-PARTICIPACOES-EM-BANCA|"
     r"BANCA-JULGADORA-PARA-(PROFESSOR-TITULAR|CONCURSO-PUBLICO|LIVRE-DOCENCIA|AVALIACAO-CURSOS)|OUTRAS-BANCAS-JULGADORAS)$", "banca"),
    (r"^(ORIENTACAO-EM-ANDAMENTO-DE-.+|OUTRAS-ORIENTACOES-EM-ANDAMENTO)$", "orientacao_andamento"),
    (r"^(PARTICIPACAO-EM-(CONGRESSO|ENCONTRO|OFICINA|SEMINARIO|SIMPOSIO|FEIRA|EXPOSICAO|OLIMPIADA)|OUTRAS-PARTICIPACOES-EM-EVENTOS-CONGRESSOS)$", "participacao_evento"),
    # dados gerais
    (r"^PROJETO-DE-PESQUISA$", "projeto"),
    (r"^PREMIO-TITULO$", "premio"),
    (r"^ATUACAO-PROFISSIONAL$", "atuacao_profissional"),
    (r"^(GRADUACAO|ESPECIALIZACAO|MESTRADO|DOUTORADO|POS-DOUTORADO|APERFEICOAMENTO|LIVRE-DOCENCIA|MESTRADO-PROFISSIONALIZANTE|RESIDENCIA-MEDICA|"
     r"CURSO-TECNICO-PROFISSIONALIZANTE|ENSINO-FUNDAMENTAL-PRIMEIRO-GRAU|ENSINO-MEDIO-SEGUNDO-GRAU)$", "formacao_academica"),
]
_TIPOS = [(re.compile(p), c) for p, c in TIPOS]

# Atributos de título e de ano, na ordem de preferência (nomes da DTD). O primeiro presente vence.
_TITULO = ("TITULO-DO-ARTIGO", "TITULO-DO-TRABALHO", "TITULO-DO-LIVRO", "TITULO-DO-CAPITULO-DO-LIVRO", "TITULO-DO-TEXTO", "TITULO-DO-SOFTWARE",
           "TITULO-DO-PROCESSO", "TITULO-DO-PRODUTO", "TITULO-DO-TRABALHO-TECNICO", "TITULO-PATENTE", "TITULO", "DENOMINACAO", "NOME-CURSO",
           "NOME-DO-PROJETO", "NOME-DO-PREMIO-OU-TITULO", "NOME-DO-EVENTO", "TITULO-DA-DISSERTACAO-TESE", "TITULO-DA-MONOGRAFIA",
           "TITULO-DA-RESIDENCIA-MEDICA", "TITULO-DO-TRABALHO-DE-CONCLUSAO-DE-CURSO", "TITULO-DO-TRABALHO-DE-INICIACAO-CIENTIFICA",
           "NOME-DO-CANDIDATO", "NOME-DO-ORIENTANDO", "NOME-INSTITUICAO")
_ANO = ("ANO-DO-ARTIGO", "ANO-DO-TRABALHO", "ANO-DO-TEXTO", "ANO", "ANO-DE-CONCLUSAO", "ANO-DE-INICIO", "ANO-INICIO", "ANO-DA-DEFESA",
        "ANO-DE-OBTENCAO-DO-TITULO", "ANO-DE-REALIZACAO", "ANO-DE-REGISTRO", "ANO-DO-PREMIO", "ANO-DA-PREMIACAO", "ANO-DESENVOLVIMENTO",
        "ANO-SOLICITACAO")
# Só estes descendentes entram na junta de atributos de um item (o resto são sub-itens, ex.: EQUIPE-DO-PROJETO, FINANCIADORES-DO-PROJETO).
_FONTES_ATRIBUTOS = ("DADOS-BASICOS", "DETALHAMENTO", "VINCULOS")
# Sub-itens que são itens por si e vêm aninhados em outro item: visitados à parte (ex.: a patente dentro de OUTRA-PRODUCAO-TECNICA).
_ANINHADOS = {"REGISTRO-OU-PATENTE"}


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


def _descendentes(el: ET.Element):
    """Descendentes de `el`, sem entrar nos sub-itens aninhados (cujos atributos não são do item pai)."""
    for filho in el:
        if _tag(filho) in _ANINHADOS:
            continue
        yield filho
        yield from _descendentes(filho)


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
            for filho in _descendentes(el):
                t = _tag(filho)
                if t == "AUTORES":
                    autores.append(filho.get("NOME-COMPLETO-DO-AUTOR", ""))
                if t.startswith(_FONTES_ATRIBUTOS):
                    for k, v in filho.attrib.items():
                        attrs.setdefault(k, v)
            ano = _primeiro(attrs, _ANO)
            if not ano.isdigit():  # patente: o ano vem das datas ddmmaaaa (pedido de depósito, concessão)
                ano = next((d[-4:] for d in (attrs.get("DATA-PEDIDO-DE-DEPOSITO", ""), attrs.get("DATA-DE-CONCESSAO", "")) if len(d) == 8 and d.isdigit()), "")
            item = {"categoria": cat, "titulo": _primeiro(attrs, _TITULO), "ano": ano if ano.isdigit() else "",
                    "doi": attrs.get("DOI", "").strip(), "issn": attrs.get("ISSN", "").strip(),
                    "isbn": attrs.get("ISBN", "").strip(), "veiculo": _primeiro(attrs, ("TITULO-DO-PERIODICO-OU-REVISTA", "NOME-DO-EVENTO", "EDITORA", "NOME-DA-EDITORA")),
                    "autores": [a for a in autores if a], "ano_fim": attrs.get("ANO-FIM", "") or attrs.get("ANO-DE-CONCLUSAO", ""),
                    "tag": _tag(el), "seq": attrs.get("SEQUENCIA-PRODUCAO", "") or attrs.get("SEQUENCIA-FORMACAO", ""),
                    "natureza": attrs.get("NATUREZA", "")}
            if item["titulo"] or item["doi"]:
                itens.append(item)
            for filho in el:  # sub-itens aninhados (patente dentro de outra produção técnica)
                if _tag(filho) in _ANINHADOS:
                    visitar(filho, _tag(el))
            return  # não desce no resto: já juntou os atributos dos filhos
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
