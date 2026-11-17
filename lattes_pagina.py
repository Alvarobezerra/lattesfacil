"""Leitura em tempo real do currículo: interpreta a "página para impressão" do Lattes (pkg_impcv.trata, modelo Completo).

O XML exportado pode estar anos defasado; esta página é gerada na hora a partir do currículo atual. Ela é HTML, não um formato
estruturado, então a leitura se apoia em marcadores estáveis da página: âncoras de seção (<a name="...">), subtítulos de grupo
(.agrupadorsub / .subtitMenu) e linhas de tabela com td.ano + td.texto. O resultado tem o mesmo formato de lattes_xml.ler_curriculo,
com fonte="pagina". Os itens vêm de texto corrido (citação), então título/autores/ano são extraídos por heurística.
Só biblioteca padrão.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from lattes_xml import _norm, formatar_doi

MAX_HTML_BYTES = 8 * 1024 * 1024
_VOID = {"br", "img", "hr", "input", "meta", "link", "area", "base", "col", "param", "source", "track", "wbr"}

# âncora normalizada -> categoria (mesmas categorias do leitor de XML)
_POR_SECAO = {
    "premiosetitulos": "premio", "formacaoacademica/titulacao": "formacao_academica", "formacaocomplementar": "formacao_complementar",
    "atuacaoprofissional": "atuacao_profissional", "projetoextensao": "projeto", "projetopesquisa": "projeto", "projetoensino": "projeto",
    "projetodesenvolvimento": "projeto", "projetooutros": "projeto", "trabalhoseventos": "trabalho_evento", "apresentacaotrabalho": "apresentacao",
    "organizacaoeventos": "organizacao_evento", "participacaoemeventos": "participacao_evento", "softwarecompatente": "software",
}
# subtítulo de grupo (normalizado, por prefixo/trecho) -> categoria. Vale antes da âncora, que às vezes fica "velha" na página.
_POR_GRUPO = [
    (r"^artigos completos publicados", "artigo"), (r"^artigos aceitos", "artigo_aceito"), (r"^livros publicados", "livro"),
    (r"^capitulos de livros", "capitulo"), (r"^textos em jornais", "texto_jornal"), (r"^trabalhos publicados em anais", "trabalho_evento"),
    (r"^apresentacao de trabalho", "apresentacao"), (r"^organizacao de evento", "organizacao_evento"), (r"^participacao em evento", "participacao_evento"),
    (r"^producao artistica", "producao_artistica"), (r"^programa de computador", "software"), (r"^trabalhos tecnicos", "trabalho_tecnico"), (r"^patentes?\b", "patente"),
    (r"^curso de curta duracao ministrado", "curso_ministrado"), (r"^processos ou tecnicas", "produto_tecnologico"),
    (r"^produtos tecnologicos", "produto_tecnologico"),
]
_SEM_ITEM = {"dadospessoais", "endereco", "idiomas", "areasdeatuacao"}  # tratados no perfil, não são itens
_CRONOLOGICAS = {"formacao_academica", "formacao_complementar", "atuacao_profissional", "premio", "projeto"}
_RE_ANO = re.compile(r"\b(?:19|20)\d{2}\b")


class _Pagina(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anc = ""
        self.grupo = ""
        self.linhas: list[dict[str, Any]] = []
        self._cap: tuple[str, str] | None = None  # (campo, tag que abriu)
        self._prof = 0
        self._buf: list[str] = []
        self._ano = ""
        self._texto = ""
        self._hrefs: list[str] = []
        self._em_tr = False
        self._dentro_texto = False

    @staticmethod
    def _classes(attrs: list[tuple[str, str | None]]) -> set[str]:
        return set(((dict(attrs).get("class")) or "").split())

    # A página real é HTML 4 com tags de fechamento omitidas (<TR><TD class="ano">2019<TD class="texto">...<BR></TABLE>), então
    # <td>, <tr> e <table> também encerram, de forma implícita, a célula/linha que estiver aberta.
    _LIMITES = {"td", "th", "tr", "table", "div"}  # a âncora de seção também encerra a célula aberta (ver handle_starttag)

    def _fechar_captura(self) -> None:
        if not self._cap:
            return
        campo = self._cap[0]
        texto = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._cap, self._prof, self._buf = None, 0, []
        if campo == "grupo":
            self.grupo = texto
        elif campo == "ano":
            self._ano = texto
        else:
            self._texto = texto

    def _fechar_linha(self) -> None:
        if self._cap and self._cap[0] in ("ano", "texto"):
            self._fechar_captura()
        if self._em_tr and self._texto:  # idiomas e áreas vêm sem ano
            self.linhas.append({"anc": self.anc, "grupo": self.grupo, "ano": self._ano, "texto": self._texto, "hrefs": list(self._hrefs)})
        self._em_tr, self._ano, self._texto, self._hrefs = False, "", "", []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _VOID:
            return
        cls = self._classes(attrs)
        ancora = tag == "a" and bool(dict(attrs).get("name"))
        if self._cap and self._cap[0] in ("ano", "texto") and (tag in self._LIMITES or ancora):
            self._fechar_captura()  # fim implícito da célula
            if tag in ("tr", "table", "div") or ancora:
                self._fechar_linha()
        if self._cap:
            self._prof += 1
            if tag == "a" and self._cap[0] == "texto":
                self._hrefs.append(dict(attrs).get("href") or "")
            return
        if tag == "a" and dict(attrs).get("name"):
            self._fechar_linha()
            self.anc, self.grupo = dict(attrs)["name"], ""
        elif tag in ("tr", "table"):
            self._fechar_linha()
            self._em_tr = tag == "tr"
        elif tag == "td" and cls & {"ano", "campos"}:  # 1ª coluna: ano/período (ano) ou rótulo (campos, ex.: nome do idioma)
            self._abrir("ano", tag)
        elif tag == "td" and "texto" in cls:
            self._abrir("texto", tag)
        elif cls & {"agrupadorsub", "subtitMenu"}:
            self._abrir("grupo", tag)

    def _abrir(self, campo: str, tag: str) -> None:
        self._cap, self._prof, self._buf = (campo, tag), 1, []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        pass  # <br/>, <img/>: sem texto

    def handle_data(self, data: str) -> None:
        if self._cap:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in _VOID:
            return
        if self._cap and self._cap[0] in ("ano", "texto") and tag in self._LIMITES:
            self._fechar_captura()
            if tag in ("tr", "table"):
                self._fechar_linha()
            return
        if self._cap:
            self._prof -= 1
            if self._prof <= 0:
                self._fechar_captura()
        elif tag in ("tr", "table"):
            self._fechar_linha()

    def close(self) -> None:
        super().close()
        self._fechar_linha()


def _categoria(anc: str, grupo: str) -> str | None:
    g = _norm(grupo)
    for rx, cat in _POR_GRUPO:
        if re.search(rx, g):
            return cat
    return _POR_SECAO.get(anc.lower())


def _anos(s: str) -> list[str]:
    return [m.group(0) for m in _RE_ANO.finditer(s)]


def _item(cat: str, ano_td: str, texto: str, hrefs: list[str]) -> dict[str, Any]:
    doi = formatar_doi(" ".join(hrefs) + " " + texto)
    autores: list[str] = []
    veiculo = ""
    ano_fim = ""
    if cat in _CRONOLOGICAS:
        a = _anos(ano_td)
        ano = a[0] if a else ""
        ano_fim = a[1] if len(a) > 1 else ""
        titulo = re.split(r"\.\s|,\s|\s\(", texto, maxsplit=1)[0].strip() if cat != "atuacao_profissional" else texto[:120]
    else:
        resto = texto
        if ".. " in texto:  # "SOBRENOME, A. B.; OUTRO, C.. Título ..." -> lista de autores termina em ".."
            autores_txt, resto = texto.split(".. ", 1)
            autores = [x.strip() for x in (autores_txt + ".").split(";") if x.strip()]  # o ".." perdeu o ponto do último nome
        if " In: " in resto:
            titulo, resto2 = resto.split(" In: ", 1)
            veiculo = re.split(r",\s*(?:19|20)\d{2}\b", resto2, maxsplit=1)[0].strip(" .,")
        else:
            titulo = re.split(r",\s*(?:19|20)\d{2}\b", resto, maxsplit=1)[0]
        titulo = titulo.strip(" .,")
        m = re.search(r",\s*((?:19|20)\d{2})\b", resto) or None
        todos = _anos(resto)
        ano = m.group(1) if m else (todos[0] if todos else "")
    return {"categoria": cat, "titulo": titulo, "ano": ano, "doi": doi, "issn": "", "isbn": "", "veiculo": veiculo, "autores": autores,
            "ano_fim": ano_fim, "tag": "PAGINA", "seq": "", "natureza": ""}


def ler_pagina(html: str, nome: str = "") -> dict[str, Any]:
    """HTML da página para impressão -> {"nome", "id_lattes", "itens": [...], "perfil", "nao_classificados", "fonte": "pagina", ...}."""
    if len(html.encode("utf-8", "ignore")) > MAX_HTML_BYTES:
        raise ValueError("Página grande demais.")
    if "conteudo-cv" not in html or "IndicProdTabela" not in html:
        raise ValueError("O texto não parece a página de impressão do Lattes (faltam as tabelas do currículo).")
    p = _Pagina()
    p.feed(html)
    p.close()
    itens: list[dict[str, Any]] = []
    vistos: set[tuple[str, str]] = set()
    desconhecidos: dict[str, int] = {}
    perfil: dict[str, Any] = {"resumo": "", "idiomas": [], "areas": []}
    for ln in p.linhas:
        anc = ln["anc"].lower()
        if not anc:
            continue  # cabeçalho de identificação (nome, nascimento, ID) antes da 1ª seção: dado pessoal, nunca vira item
        if anc.endswith("pop") or anc == "popularizacao":
            continue  # seção "Popularização": repete itens já listados nas seções principais
        if anc == "areasdeatuacao":
            area = re.sub(r"Grande [áa]rea:\s*", "", ln["texto"], flags=re.I).replace(" / Área: ", " › ").replace(" / Subárea: ", " › ").replace(" / Especialidade: ", " › ")
            if area not in perfil["areas"]:
                perfil["areas"].append(area)
            continue
        if anc == "idiomas":
            perfil["idiomas"].append((ln["ano"] or ln["texto"].split(" - ")[0]).strip(" ."))  # na página real o idioma vem na 1ª coluna
            continue
        if anc in _SEM_ITEM:
            continue
        cat = _categoria(ln["anc"], ln["grupo"])
        if not cat:
            k = f"{ln['anc']} | {ln['grupo']}".strip(" |")
            desconhecidos[k] = desconhecidos.get(k, 0) + 1
            continue
        if cat in _CRONOLOGICAS and not ln["ano"].strip() and itens and itens[-1]["categoria"] == cat:
            continue  # linha de detalhe (Descrição:/Situação:/Integrantes:) do item anterior, sem período próprio
        chave = (cat, _norm(ln["texto"]))
        if chave in vistos:
            continue
        vistos.add(chave)
        itens.append(_item(cat, ln["ano"], ln["texto"], ln["hrefs"]))
    m_data = re.search(r"[Úú]ltima atualiza[çc][ãa]o do curr[íi]culo em\s*(\d{2}/\d{2}/\d{4})", html)
    m_id = re.search(r"lattes\.cnpq\.br/(\d{16})", html) or re.search(r"\b(\d{16})\b", html)
    agora = datetime.now(timezone.utc)
    return {"nome": nome.strip()[:200], "nome_citacao": "", "id_lattes": m_id.group(1) if m_id else "",
            "atualizacao": m_data.group(1).replace("/", "") if m_data else "",
            "atualizacao_iso": agora.strftime("%Y-%m-%dT%H:%M:%S+00:00"),  # leitura ao vivo: vale o instante da leitura
            "itens": itens, "perfil": perfil, "nao_classificados": desconhecidos, "fonte": "pagina"}
