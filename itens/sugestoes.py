"""Sugestões para as grades (listas) dos formulários do Lattes, a partir do texto do documento:

- participantes da banca (aba "Participantes", que é a grade de autores do Lattes);
- palavras-chave e áreas do conhecimento, a partir do título (e do nome do curso, quando há).

Tudo é sugestão heurística: aparece preenchido na tela de revisão, com aviso para conferir, e o usuário edita antes de enviar.
As áreas só saem do catálogo oficial do Lattes (docs/campos-lattes/catalogos/areas-do-conhecimento.json), pelo nome exato.
"""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata
from functools import lru_cache
from typing import Any

CATALOGO_AREAS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "campos-lattes" / "catalogos" / "areas-do-conhecimento.json"
PARTICULAS = {"da", "de", "do", "das", "dos", "e", "di", "du", "del", "van", "von", "bin", "ibn"}
STOP = set("de da do das dos e em no na nos nas por para com sem sobre entre a o as os um uma uns umas ao aos à às ou como sob ante após até que se seu sua seus suas pelo pela pelos pelas ser foi são é".split())
VERBOS = set("""atenua reduz induz melhora avalia analisa promove previne inibe protege potencializa modula interferir interfere
afeta altera aumenta diminui estimula regula revela demonstra mostra apresenta propõe discute investiga utiliza usa
contribui favorece compara determina identifica explora""".split())
GENERICAS = {"efeito", "efeitos", "estudo", "estudos", "análise", "avaliação", "uso", "papel", "impacto", "influência", "ação", "resultados",
             "caso", "relato", "revisão", "abordagem", "contribuição", "perspectiva", "proposta", "novo", "nova", "novos", "novas"}


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(t or "")) if unicodedata.category(c) != "Mn")


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", _sem_acento(t).lower())).strip()


def _nome_proprio(nome: str) -> str:
    return " ".join(p.lower() if p.lower() in PARTICULAS else p[:1].upper() + p[1:].lower() for p in re.split(r"\s+", nome.strip()) if p)


# ---------- participantes da banca ----------
_CABECALHO = re.compile(r"(membros|composi[cç][aã]o|integrantes|componentes)\s+d[aoe]s?\s+(banca|comiss[aã]o)|banca\s+examinadora|comiss[aã]o\s+examinadora", re.I)
_FIM = re.compile(r"^\s*(prof(?:\.|a|essor|essora)?\b.*(?:dr|coordena)|coordena|documento assinado|assinado|local e data|fortaleza|conforme|a autenticidade|refer[eê]ncia)", re.I)
_PAPEL = re.compile(r"orientador|coorientador|co-orientador|presidente|examinador|membro|suplente|avaliador|titular|externo|interno", re.I)
_LINHA = re.compile(r"^\s*(?:[-•*]\s*)?(?:prof(?:\.|a|essor|essora)?\s*)?(?:dr(?:a)?\.?\s*)?([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-. ]{4,80}?)\s*\(([^()]{2,120})\)\s*$")


def participantes_da_banca(texto: str, excluir: str = "") -> list[dict[str, str]]:
    """Lê a lista de membros no formato 'NOME (SIGLA - Papel)'; quando não há cabeçalho, exige palavra de papel entre parênteses."""
    linhas = [re.sub(r"\s+", " ", l).strip() for l in texto.splitlines()]
    ini = next((i for i, l in enumerate(linhas) if _CABECALHO.search(l) and len(l) < 80), None)
    escopo = linhas[ini + 1:] if ini is not None else linhas
    out: list[dict[str, str]] = []
    vistos: set[str] = set()
    ex = _norm(excluir)
    for l in escopo:
        if ini is not None and out and _FIM.search(l):
            break
        m = _LINHA.match(l)
        if not m:
            continue
        nome, detalhe = m.group(1).strip(" .-"), m.group(2).strip()
        if ini is None and not _PAPEL.search(detalhe):
            continue
        tok = [t for t in nome.split() if t.lower() not in PARTICULAS]
        if len(tok) < 2 or len(nome) > 70 or re.search(r"\d", nome) or _norm(nome) in vistos or (ex and _norm(nome) == ex):
            continue
        partes = re.split(r"\s+[-–—]\s+", detalhe, maxsplit=1)
        inst = partes[0].strip() if len(partes) == 2 else ""
        papel = (partes[1] if len(partes) == 2 else partes[0]).strip()
        vistos.add(_norm(nome))
        out.append({"nome": _nome_proprio(nome), "instituicao": inst, "papel": papel})
    return out


def como_citado(nome: str) -> str:
    """'Nylane Maria Nunes de Alencar' -> 'ALENCAR, N. M. N.' (padrão de citação bibliográfica)."""
    partes = [p for p in nome.split() if p]
    if len(partes) < 2:
        return nome.upper()
    ini = [p[0].upper() + "." for p in partes[:-1] if p.lower() not in PARTICULAS]
    return f"{partes[-1].upper()}, {' '.join(ini)}"


# ---------- palavras-chave ----------
def _eh_verbo_ou_participio(w: str) -> bool:
    l = w.lower()
    return l in VERBOS or bool(re.search(r"(ida|ido|idas|idos|ada|ado|adas|ados|ndo|ar|er|ir|ua)$", l)) and len(l) > 3 and l not in ("lúpus",)


def palavras_chave(titulo: str, maximo: int = 5) -> list[str]:
    """Frases do título entre conectivos e verbos (ex.: 'mucosite intestinal', 'Moringa oleífera'), sem palavras genéricas."""
    t = re.sub(r"[\"“”‘’()\[\]:;,.!?/]+", " | ", str(titulo or ""))
    frases: list[list[str]] = []
    atual: list[str] = []

    def fecha() -> None:
        nonlocal atual
        while atual and (_eh_verbo_ou_participio(atual[-1]) and len(atual) > 1):
            atual = atual[:-1]
        if atual:
            frases.append(atual)
        atual = []

    for w in t.split():
        l = w.lower()
        if w == "|" or l in STOP or l in VERBOS or (_eh_verbo_ou_participio(w) and not atual):
            fecha()
            continue
        if not re.search(r"[A-Za-zÀ-ÿ]", w):
            fecha()
            continue
        atual.append(w.strip("-'"))
    fecha()
    cand: list[tuple[int, int, str]] = []
    for f in frases:
        f = [w for w in f[:3]]
        texto = " ".join(f)
        if len(f) == 1 and (len(texto) < 6 or texto.lower() in GENERICAS or _eh_verbo_ou_participio(texto)):
            continue
        if f[0].lower() in GENERICAS and len(f) == 1:
            continue
        cand.append((-len(f), -len(texto), texto[:50]))
    cand.sort()
    saida: list[str] = []
    vistos: set[str] = set()
    for _, _, c in cand:
        k = _norm(c)
        if k and k not in vistos and not any(k in v or v in k for v in vistos):
            vistos.add(k)
            saida.append(c[:1].upper() + c[1:])
        if len(saida) >= maximo:
            break
    return saida


# ---------- áreas do conhecimento ----------
@lru_cache(maxsize=1)
def _areas() -> list[tuple[str, frozenset[str], int]]:
    try:
        arvore = json.loads(CATALOGO_AREAS.read_text(encoding="utf-8"))["arvore"]
    except Exception:
        return []
    out: list[tuple[str, frozenset[str], int]] = []

    def anda(no: dict[str, Any], nivel: int) -> None:
        nome = no.get("nome", "")
        toks = frozenset(_radical(t) for t in _norm(nome).split() if len(t) > 2 and t not in {"de", "da", "do", "das", "dos"})
        if toks and len(_norm(nome)) >= 5:
            out.append((nome, toks, nivel))
        for f in no.get("filhos", []):
            anda(f, nivel + 1)

    for g in arvore:
        anda(g, 0)
    return out


def _radical(t: str) -> str:
    return re.sub(r"(s|es)$", "", t) if len(t) > 4 else t


def areas_do_texto(titulo: str, contexto: str = "", maximo: int = 2) -> list[str]:
    """Áreas cujo nome inteiro aparece no título ou no nome do curso (contexto pesa mais). Devolve o nome exato do catálogo."""
    tt = {_radical(t) for t in _norm(titulo).split() if len(t) > 2}
    tc = {_radical(t) for t in _norm(contexto).split() if len(t) > 2}
    pts: dict[str, tuple[int, int, int, str]] = {}  # chave normalizada -> (contexto, nº de palavras, -nível, nome)
    for nome, toks, nivel in _areas():
        if toks <= (tt | tc):
            peso = (1 if toks & tc else 0, len(toks), -nivel, nome if nome != nome.upper() else "~" + nome)  # nome em CAIXA ALTA perde o empate
            k = _norm(nome)
            if k not in pts or peso > pts[k]:
                pts[k] = peso
    ordem = sorted(pts.values(), key=lambda x: (-x[0], -x[1], -x[2], x[3]))
    return [p[3].lstrip("~") for p in ordem][:maximo]


# tema (regex sobre texto sem acento) -> (áreas, setores) com o nome exato do catálogo do Lattes
TEMAS_PATENTE = [
    (r"bebida|aliment|probiotic|fermenta|extrato hidrossolu|polpa de fruta|iogurte|leite", ["Ciência e Tecnologia de Alimentos", "Microbiologia de Alimentos"], ["Fabricação de Produtos Alimentícios"]),
    (r"bebida", [], ["Fabricação de Bebidas"]),
    (r"medicament|farmac|fitoterap|formulacao terapeutica", ["Farmacotecnia"], ["Fabricação de produtos farmoquímicos e farmacêuticos"]),
]


# ---------- catálogos para o "Listar todos" da tela ----------
CATALOGO_SETORES = pathlib.Path(__file__).resolve().parent.parent / "docs" / "campos-lattes" / "catalogos" / "setores-de-atividade.json"


@lru_cache(maxsize=1)
def catalogo_areas_planas() -> list[dict[str, Any]]:
    """Todas as áreas do Lattes em lista plana: nome exato (o que o Lattes grava), caminho completo e nível (0 = grande área)."""
    try:
        arvore = json.loads(CATALOGO_AREAS.read_text(encoding="utf-8"))["arvore"]
    except Exception:
        return []
    out: list[dict[str, Any]] = []

    def anda(no: dict[str, Any], caminho: list[str]) -> None:
        cam = caminho + [no.get("nome", "")]
        out.append({"nome": no.get("nome", ""), "caminho": " › ".join(cam), "nivel": len(cam) - 1})
        for f in no.get("filhos", []):
            anda(f, cam)

    for g in arvore:
        anda(g, [])
    return out


@lru_cache(maxsize=1)
def catalogo_setores() -> list[dict[str, Any]]:
    try:
        return [{"nome": n, "caminho": n, "nivel": 0} for n in json.loads(CATALOGO_SETORES.read_text(encoding="utf-8"))["setores"]]
    except Exception:
        return []


# ---------- entrada única usada por itens.leitores.ler ----------
def grades_para(item_id: str, texto: str, valores: dict[str, Any], chaves_grade: set[str]) -> tuple[dict[str, list[Any]], list[str]]:
    """Devolve ({'grade:<chave>': lista}, avisos) só para as grades que o formulário do item realmente tem."""
    out: dict[str, list[Any]] = {}
    notas: list[str] = []
    if item_id == "banca" and "autores" in chaves_grade:
        membros = participantes_da_banca(texto, excluir=str(valores.get("f_nme_orient", "")))
        if membros:
            out["grade:autores"] = [{"nome": m["nome"], "citacao": como_citado(m["nome"])} for m in membros]
            notas.append(f"Participantes da banca lidos do documento ({len(membros)}); o titular é incluído automaticamente. Confira os nomes.")
        else:
            notas.append("Lista de membros da banca não identificada: preencha os participantes na aba Participantes.")
    if item_id == "patente":  # áreas e setores por tema (título + resumo); só nomes que existem nos catálogos do Lattes
        tema = _norm(str(valores.get("f_titulo", "")) + " " + str(valores.get("f_ref", "")))
        ar_ok = {x["nome"] for x in catalogo_areas_planas()}
        se_ok = {x["nome"] for x in catalogo_setores()}
        ar: list[str] = []
        se: list[str] = []
        for rx, areas_t, setores_t in TEMAS_PATENTE:
            if re.search(rx, tema):
                ar += [x for x in areas_t if x in ar_ok and x not in ar]
                se += [x for x in setores_t if x in se_ok and x not in se]
        if ar and "areas" in chaves_grade:
            out["grade:areas"] = ar[:3]
        if se and "setores" in chaves_grade:
            out["grade:setores"] = se[:2]
        if ar or se:
            notas.append("Áreas e setores sugeridos pelo tema do título e do resumo; confira e ajuste antes de enviar.")
    titulo = str(valores.get("f_titulo", "") or "")
    if titulo:
        if "palavras_chave" in chaves_grade:
            pc = palavras_chave(titulo)
            if pc:
                out["grade:palavras_chave"] = pc
        if "areas" in chaves_grade:
            ar = areas_do_texto(titulo, str(valores.get("f_curso", "") or ""))
            if ar:
                out["grade:areas"] = ar
        if "grade:palavras_chave" in out or "grade:areas" in out:
            notas.append("Palavras-chave e áreas foram sugeridas a partir do título" + (" e do curso" if valores.get("f_curso") else "") + "; confira e ajuste antes de enviar.")
    return out, notas
