"""Escolha da variante do formulário do Lattes pelo tipo do documento (itens com mais de um formulário).

Itens: livro_capitulo (Livro/Capítulo), projeto (5 tipos), formacao_academica (10 níveis), pos_doutorado (2).
As variantes são reconhecidas pela URL do formulário (estável), não pelo nome, que na especificação gerada
pode ser genérico ("Formulário 3"). Sem sugestão clara devolve variante=None e o usuário escolhe na tela.
"""
from __future__ import annotations

import copy
import re
import unicodedata
from typing import Any

from . import especificacao


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


# trecho da URL (ou do nome) -> rótulo legível
ROTULOS: dict[str, dict[str, str]] = {
    "livro_capitulo": {"form_lvr": "Livro", "form_cap": "Capítulo de livro"},
    "formacao_academica": {
        "f_nivel=4": "Doutorado", "f_nivel=3": "Mestrado", "f_nivel=9": "Mestrado profissional",
        "f_nivel=2": "Especialização", "f_nivel=d": "Especialização - Residência médica", "f_nivel=1": "Graduação",
        "f_nivel=7": "Ensino profissional de nível técnico", "f_nivel=c": "Ensino médio (2º grau)",
        "f_nivel=b": "Ensino fundamental (1º grau)", "f_nivel=x": "Aperfeiçoamento",
    },
    "pos_doutorado": {"f_nivel=5": "Pós-doutorado", "f_nivel=6": "Livre-docência"},
}

# (chave do rótulo, regex sobre o texto normalizado, motivo); a ordem importa: o mais específico primeiro
REGRAS: dict[str, list[tuple[str, str, str]]] = {
    "livro_capitulo": [
        ("form_cap", r"\bcapitulo\b|\bcap\s?\d|in\s*:\s*\w", "o texto fala em capítulo"),
        ("form_lvr", r"\blivro\b|\bisbn\b|\bedicao\b|\borganizador|\borganizacao do livro", "o texto fala em livro/ISBN"),
    ],
    "formacao_academica": [
        ("f_nivel=9", r"mestrado profissional|mestrado profissionalizante", "menciona mestrado profissional"),
        ("f_nivel=d", r"residencia medica|residencia multiprofissional", "menciona residência médica"),
        ("f_nivel=4", r"(?<!pos )(?<!pos-)\bdoutorado\b|\bphd\b|\bdoutor em\b|\bdoutora em\b", "menciona doutorado"),
        ("f_nivel=3", r"\bmestrado\b|\bmestre em\b|\bmestra em\b", "menciona mestrado"),
        ("f_nivel=2", r"especializacao|pos graduacao lato sensu|\blato sensu\b|\bmba\b", "menciona especialização"),
        ("f_nivel=1", r"\bgraduacao\b|bacharel|licenciatura|tecnologo|\bgraduado\b", "menciona graduação"),
        ("f_nivel=7", r"ensino profissional|curso tecnico|nivel tecnico|tecnico em", "menciona curso técnico"),
        ("f_nivel=c", r"ensino medio|2o grau|segundo grau", "menciona ensino médio"),
        ("f_nivel=b", r"ensino fundamental|1o grau|primeiro grau", "menciona ensino fundamental"),
        ("f_nivel=x", r"aperfeicoamento", "menciona aperfeiçoamento"),
    ],
    "pos_doutorado": [
        ("f_nivel=6", r"livre docencia", "menciona livre-docência"),
        ("f_nivel=5", r"pos doutorado|pos doutoral|postdoc|post doctoral", "menciona pós-doutorado"),
    ],
    "projeto": [
        ("extens", r"projeto de extensao|\bextensao\b", "menciona projeto de extensão"),
        ("ensino", r"projeto de ensino|\bensino\b", "menciona projeto de ensino"),
        ("desenvolvimento", r"desenvolvimento tecnologico|\binovacao\b|\bprototipo\b", "menciona desenvolvimento tecnológico"),
        ("pesquisa", r"projeto de pesquisa|\bpesquisa\b", "menciona projeto de pesquisa"),
    ],
}


def _chave_da_variante(item_id: str, v: dict[str, Any]) -> str:
    """Rótulo-chave da variante: trecho da URL conhecido ou, no projeto, palavra do nome."""
    url = str(v.get("url", "")).lower()
    if item_id == "projeto":
        nome = _norm(v.get("variante", ""))
        for k in ("extens", "ensino", "desenvolvimento", "pesquisa"):
            if k in nome:
                return k
        return "outros"
    for k in ROTULOS.get(item_id, {}):
        if k in url:
            return k
    return ""


def rotulo_variante(item_id: str, v: dict[str, Any]) -> str:
    if item_id == "projeto":
        return str(v.get("variante", ""))
    return ROTULOS.get(item_id, {}).get(_chave_da_variante(item_id, v), str(v.get("variante", "")))


def spec_com_rotulos(item_id: str) -> dict[str, Any] | None:
    """Especificação para a tela: cada variante ganha 'rotulo' (a especificação em disco não muda)."""
    spec = especificacao(item_id)
    if not spec:
        return None
    spec = copy.deepcopy(spec)
    for v in spec["variantes"]:
        v["rotulo"] = rotulo_variante(item_id, v)
    return spec


def sugerir_variante(item_id: str, texto: str = "", valores: dict[str, Any] | None = None) -> dict[str, Any]:
    """{'variante': nome na especificação ou None, 'rotulo', 'motivo', 'opcoes': [{variante, rotulo}]}.

    Só sugere quando uma regra bate; texto vazio, item sem regras ou nenhuma regra: variante=None.
    """
    spec = especificacao(item_id)
    out: dict[str, Any] = {"variante": None, "rotulo": "", "motivo": "", "opcoes": []}
    if not spec:
        return out
    vs = spec["variantes"]
    out["opcoes"] = [{"variante": v["variante"], "rotulo": rotulo_variante(item_id, v)} for v in vs]
    if len(vs) < 2:
        if vs:
            out.update(variante=vs[0]["variante"], rotulo=out["opcoes"][0]["rotulo"], motivo="único formulário do item")
        return out
    flat = _norm(" ".join([str(texto or "")] + [str(x) for x in (valores or {}).values() if isinstance(x, str)]))
    if not flat:
        return out
    por_chave = {_chave_da_variante(item_id, v): v for v in vs}
    for chave, rx, motivo in REGRAS.get(item_id, []):
        v = por_chave.get(chave)
        if v and re.search(rx, flat):
            out.update(variante=v["variante"], rotulo=rotulo_variante(item_id, v), motivo=motivo)
            return out
    return out
