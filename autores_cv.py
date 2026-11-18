"""Autores citados no currículo Lattes de cada usuário (menu lateral "Autores citados no currículo", pkg_dic_autor.lista).

Rotina de primeiro acesso: a extensão lê essa lista no Lattes e o servidor guarda por usuário. Depois ela ajuda a
completar o "nome em citações" de coautores e inventores sem o usuário digitar de novo.
A página do Lattes só foi mapeada pelo link do menu; por isso a leitura é tolerante (guarda também as células brutas).
"""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from datetime import datetime
from typing import Any

# "SANTOS, A. A. B." / "REIS, A. S." / "Silva, J. R." (sobrenome, iniciais com ponto)
RX_CITACAO = re.compile(r"^[^,;]{2,60},\s*(?:[A-Za-zÀ-ÿ]\.\s*){1,8}(?:[A-Za-zÀ-ÿ\-]+\.?)?\s*$")


def norm(t: Any) -> str:
    s = unicodedata.normalize("NFD", str(t or ""))
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").lower()).strip()


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cv_autores (
            owner_chave TEXT NOT NULL,
            chave TEXT NOT NULL,
            nome TEXT NOT NULL DEFAULT '',
            citacao TEXT NOT NULL DEFAULT '',
            bruto TEXT NOT NULL DEFAULT '',
            coletado_em TEXT NOT NULL,
            PRIMARY KEY (owner_chave, chave)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cv_autores_estado (
            owner_chave TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            id_cv TEXT NOT NULL DEFAULT '',
            total INTEGER NOT NULL DEFAULT 0,
            coletado_em TEXT NOT NULL
        )"""
    )


def _eh_citacao(c: str) -> bool:
    return bool(RX_CITACAO.match(c.strip()))


def interpretar_linhas(linhas: list[Any]) -> list[dict[str, str]]:
    """Cada linha é a lista de textos das células da tabela. Devolve [{nome, citacao, bruto}] sem repetidas."""
    out: dict[str, dict[str, str]] = {}
    for linha in linhas[:5000]:
        if isinstance(linha, str):
            linha = [linha]
        if not isinstance(linha, list):
            continue
        cels = [re.sub(r"\s+", " ", str(c or "")).strip()[:200] for c in linha]
        cels = [c for c in cels if c and not re.fullmatch(r"[\d.\s]+", c)]
        if not cels:
            continue
        cit = next((c for c in cels if _eh_citacao(c)), "")
        # citações podem vir juntas na mesma célula, separadas por ";"
        if not cit:
            partes = [p.strip() for c in cels for p in c.split(";") if p.strip()]
            cit = "; ".join(p for p in partes if _eh_citacao(p))
        nomes = [c for c in cels if c != cit and not _eh_citacao(c) and len(c.split()) >= 2 and re.search(r"[A-Za-zÀ-ÿ]{3}", c)]
        nome = nomes[0] if nomes else ""
        if not nome and not cit:
            continue
        # cabeçalhos da tabela não são autores
        if norm(nome or cit) in ("nome", "autor", "autores", "nome completo", "nome em citacoes bibliograficas", "nomes em citacoes bibliograficas"):
            continue
        chave = norm(nome) or norm(cit)
        if chave and chave not in out:
            out[chave] = {"nome": nome, "citacao": cit, "bruto": json.dumps(cels, ensure_ascii=False)[:600]}
    return list(out.values())


def salvar(conn: sqlite3.Connection, owner: str, linhas: list[Any], id_cv: str = "") -> dict[str, int]:
    chave_dono = norm(owner)
    if not chave_dono:
        return {"total": 0}
    itens = interpretar_linhas(linhas)
    quando = agora()
    conn.execute("DELETE FROM cv_autores WHERE owner_chave = ?", (chave_dono,))  # a coleta mais recente substitui a anterior
    for it in itens:
        chave = norm(it["nome"]) or norm(it["citacao"])
        conn.execute(
            "INSERT OR REPLACE INTO cv_autores (owner_chave, chave, nome, citacao, bruto, coletado_em) VALUES (?,?,?,?,?,?)",
            (chave_dono, chave, it["nome"], it["citacao"], it["bruto"], quando),
        )
    conn.execute(
        "INSERT INTO cv_autores_estado (owner_chave, owner, id_cv, total, coletado_em) VALUES (?,?,?,?,?) "
        "ON CONFLICT(owner_chave) DO UPDATE SET owner=excluded.owner, id_cv=excluded.id_cv, total=excluded.total, coletado_em=excluded.coletado_em",
        (chave_dono, owner.strip()[:120], re.sub(r"[^A-Za-z0-9]", "", id_cv)[:20], len(itens), quando),
    )
    return {"total": len(itens), "linhas_lidas": len(linhas)}


def estado(conn: sqlite3.Connection, owner: str) -> dict[str, Any]:
    r = conn.execute("SELECT total, coletado_em, id_cv FROM cv_autores_estado WHERE owner_chave = ?", (norm(owner),)).fetchone()
    return {"coletado": bool(r), "total": r[0] if r else 0, "coletado_em": r[1] if r else "", "id_cv": r[2] if r else ""}


def listar(conn: sqlite3.Connection, owner: str) -> dict[str, Any]:
    rows = conn.execute("SELECT nome, citacao FROM cv_autores WHERE owner_chave = ? ORDER BY nome COLLATE NOCASE", (norm(owner),)).fetchall()
    return {**estado(conn, owner), "autores": [{"nome": n, "citacao": c} for n, c in rows]}


def citacao_de(conn: sqlite3.Connection, owner: str, nome: str) -> str:
    """Nome em citações já conhecido para esse nome (casa por primeiro e último nome)."""
    t = norm(nome).split()
    if len(t) < 2:
        return ""
    for n, c in conn.execute("SELECT nome, citacao FROM cv_autores WHERE owner_chave = ? AND citacao != ''", (norm(owner),)).fetchall():
        u = norm(n).split()
        if len(u) >= 2 and u[0] == t[0] and u[-1] == t[-1]:
            return c
    return ""
