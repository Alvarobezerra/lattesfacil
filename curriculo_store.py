"""Histórico de currículos importados (snapshots), comparação entre versões, dashboard e conciliação de envios.

Cada XML do Lattes enviado vira um snapshot no SQLite (um por conteúdo distinto; reenviar o mesmo arquivo não duplica).
Comparando snapshots dá para saber o que entrou e saiu do currículo, e com isso confirmar (ou não) as inclusões e
exclusões feitas pelo LattesData. Só biblioteca padrão.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from lattes_xml import _chave_titulo, _norm, _similar, formatar_doi

MANTER_POR_CURRICULO = 30  # snapshots guardados por id_lattes (os mais antigos saem)
LIMIAR_TITULO = 0.9


def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cv_snapshots (
            id TEXT PRIMARY KEY, id_lattes TEXT NOT NULL, nome TEXT NOT NULL, atualizacao_iso TEXT,
            carregado_em TEXT NOT NULL, total INTEGER NOT NULL, hash TEXT NOT NULL, payload TEXT NOT NULL)"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS ix_cv_snap_lattes ON cv_snapshots (id_lattes, carregado_em)")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(lattes_envios)").fetchall()]
    for col in ("xml_status", "xml_verificado_em"):  # bancos criados antes da conciliação
        if cols and col not in cols:
            conn.execute(f"ALTER TABLE lattes_envios ADD COLUMN {col} TEXT")
    if "fonte" not in [r[1] for r in conn.execute("PRAGMA table_info(cv_snapshots)").fetchall()]:  # 'xml' (exportado) ou 'pagina' (ao vivo)
        conn.execute("ALTER TABLE cv_snapshots ADD COLUMN fonte TEXT NOT NULL DEFAULT 'xml'")


def hash_arquivo(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def salvar(conn: sqlite3.Connection, cur: dict[str, Any], hash_xml: str) -> tuple[str, bool]:
    """Grava o currículo como snapshot. Devolve (id, novo). Mesmo conteúdo já guardado -> devolve o existente."""
    chave = cur.get("id_lattes") or _norm(cur.get("nome", "")) or "sem-id"
    ja = conn.execute("SELECT id FROM cv_snapshots WHERE id_lattes = ? AND hash = ?", (chave, hash_xml)).fetchone()
    if ja:
        return ja[0], False
    sid = uuid.uuid4().hex[:12]
    conn.execute(
        "INSERT INTO cv_snapshots (id, id_lattes, nome, atualizacao_iso, carregado_em, total, hash, payload, fonte) VALUES (?,?,?,?,?,?,?,?,?)",
        (sid, chave, cur.get("nome", ""), cur.get("atualizacao_iso", ""), datetime.now(timezone.utc).isoformat(), len(cur["itens"]),
         hash_xml, json.dumps(cur, ensure_ascii=False), cur.get("fonte", "xml")),
    )
    conn.execute(
        "DELETE FROM cv_snapshots WHERE id_lattes = ? AND id NOT IN (SELECT id FROM cv_snapshots WHERE id_lattes = ? ORDER BY carregado_em DESC LIMIT ?)",
        (chave, chave, MANTER_POR_CURRICULO),
    )
    return sid, True


def listar(conn: sqlite3.Connection, id_lattes: str = "") -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, id_lattes, nome, atualizacao_iso, carregado_em, total, fonte FROM cv_snapshots WHERE (? = '' OR id_lattes = ?) "
        "ORDER BY carregado_em DESC LIMIT 200", (id_lattes, id_lattes)).fetchall()
    return [dict(zip(("id", "id_lattes", "nome", "atualizacao_iso", "carregado_em", "total", "fonte"), r)) for r in rows]


def carregar(conn: sqlite3.Connection, sid: str) -> dict[str, Any] | None:
    r = conn.execute("SELECT payload FROM cv_snapshots WHERE id = ?", (sid,)).fetchone()
    return json.loads(r[0]) if r else None


def anterior(conn: sqlite3.Connection, sid: str) -> str | None:
    """Id do snapshot imediatamente anterior ao informado, do mesmo currículo."""
    r = conn.execute("SELECT id_lattes, carregado_em, fonte FROM cv_snapshots WHERE id = ?", (sid,)).fetchone()
    if not r:
        return None
    # só compara versões da mesma fonte: o texto de uma página e o XML descrevem o mesmo item de formas diferentes
    p = conn.execute("SELECT id FROM cv_snapshots WHERE id_lattes = ? AND carregado_em < ? AND fonte = ? ORDER BY carregado_em DESC LIMIT 1", r).fetchone()
    return p[0] if p else None


def excluir(conn: sqlite3.Connection, sid: str) -> bool:
    return conn.execute("DELETE FROM cv_snapshots WHERE id = ?", (sid,)).rowcount > 0


# ------------------------------------------------------------------ comparação
def chave_item(it: dict[str, Any]) -> str:
    doi = formatar_doi(it.get("doi", ""))
    if doi:
        return "doi:" + doi
    return f"{it.get('categoria', '')}|{_chave_titulo(it.get('titulo', ''))}|{it.get('ano', '')}"


def comparar(antes: dict[str, Any], depois: dict[str, Any]) -> dict[str, Any]:
    """O que entrou e o que saiu entre duas versões. Título editado no Lattes aparece como saiu + entrou."""
    a = Counter(chave_item(i) for i in antes["itens"])
    d = Counter(chave_item(i) for i in depois["itens"])

    def pegar(itens: list[dict[str, Any]], restantes: Counter) -> list[dict[str, Any]]:
        restantes = Counter(restantes)  # cópia: cada ocorrência é consumida uma vez
        saida = []
        for it in itens:
            k = chave_item(it)
            if restantes[k] > 0:
                restantes[k] -= 1
                saida.append({c: it.get(c, "") for c in ("categoria", "titulo", "ano", "doi", "veiculo")})
        return saida

    return {"adicionados": pegar(depois["itens"], d - a), "removidos": pegar(antes["itens"], a - d),
            "total_antes": len(antes["itens"]), "total_depois": len(depois["itens"])}


# ------------------------------------------------------------------ dashboard
def dashboard(cur: dict[str, Any], ano_atual: int | None = None) -> dict[str, Any]:
    ano_atual = ano_atual or datetime.now().year
    itens = cur["itens"]
    por_cat = Counter(i["categoria"] for i in itens)
    por_ano: dict[str, Counter] = {}
    for i in itens:
        if i.get("ano"):
            por_ano.setdefault(i["ano"], Counter())[i["categoria"]] += 1
    anos = sorted(por_ano)
    eu = {_norm(cur.get("nome", "")), _norm(cur.get("nome_citacao", ""))} - {""}
    coautores: Counter = Counter()
    for i in itens:
        for au in i.get("autores", []):
            if _norm(au) not in eu:
                coautores[au] += 1
    artigos = [i for i in itens if i["categoria"] == "artigo"]
    producao = {"artigo", "artigo_aceito", "trabalho_evento", "livro", "capitulo", "texto_jornal", "patente", "software", "trabalho_tecnico",
                "produto_tecnologico", "apresentacao", "outra_producao_bibliografica", "outra_producao_tecnica", "producao_artistica"}
    return {
        "nome": cur.get("nome", ""), "id_lattes": cur.get("id_lattes", ""), "atualizacao": cur.get("atualizacao", ""),
        "fonte": cur.get("fonte", "xml"), "total_itens": len(itens), "por_categoria": dict(por_cat.most_common()),
        "por_ano": [{"ano": a, "total": sum(por_ano[a].values()), "producao": sum(v for k, v in por_ano[a].items() if k in producao),
                     "por_categoria": dict(por_ano[a])} for a in anos],
        "ultimos_5_anos": sum(sum(v.values()) for a, v in por_ano.items() if ano_atual - 4 <= int(a) <= ano_atual),
        "artigos": {"total": len(artigos), "sem_doi": sum(1 for a in artigos if not formatar_doi(a.get("doi", ""))),
                    "sem_issn": sum(1 for a in artigos if not a.get("issn"))},
        "periodicos_top": Counter(a["veiculo"] for a in artigos if a.get("veiculo")).most_common(8),
        "coautores_top": coautores.most_common(10),
        "orientacoes": {"concluidas": por_cat.get("orientacao_concluida", 0), "em_andamento": por_cat.get("orientacao_andamento", 0)},
        "bancas": por_cat.get("banca", 0),
        "perfil": cur.get("perfil", {}),
        "nao_classificados": cur.get("nao_classificados", {}),
    }


# ------------------------------------------------------------------ conciliação de envios
def _mesmo_dono(owner: str, nome_cv: str) -> bool:
    o, n = _norm(owner).split(), set(_norm(nome_cv).split())
    return bool(o) and bool(n) and (_norm(owner) == _norm(nome_cv) or (o[0] in n and o[-1] in n))


def _presente(cur: dict[str, Any], titulo: str, ano: str) -> bool:
    t = _chave_titulo(titulo)
    for it in cur["itens"]:
        if _similar(t, _chave_titulo(it.get("titulo", ""))) >= LIMIAR_TITULO and (not ano or not it.get("ano") or ano == it["ano"]):
            return True
    return False


def conciliar_envios(conn: sqlite3.Connection, cur: dict[str, Any]) -> dict[str, int]:
    """Confere, contra o XML, os envios do LattesData deste pesquisador e grava `xml_status` em cada um.

    Inclusão: 'confirmado' (título consta no XML), 'ausente' (não consta) ou 'xml_anterior' (o XML é mais antigo que o envio,
    então não prova nada). Exclusão: 'remocao_confirmada', 'ainda_presente' ou 'xml_anterior'.
    """
    ref = cur.get("atualizacao_iso", "")
    agora = datetime.now(timezone.utc).isoformat()
    cont: Counter = Counter()
    rows = conn.execute("SELECT id, owner, titulo, ano, status, enviado_em, removido_em FROM lattes_envios WHERE oculto_em IS NULL").fetchall()
    for eid, owner, titulo, ano, status, enviado, removido in rows:
        if not _mesmo_dono(owner or "", cur.get("nome", "")):
            continue
        if status in ("salvo", "preenchido", "atencao"):
            quando, esperado = enviado, True
        elif status in ("removido", "removendo"):
            quando, esperado = removido or enviado, False
        else:
            continue
        presente = _presente(cur, titulo or "", str(ano or ""))
        if not ref or (quando and ref < quando):
            res = "xml_anterior"
        elif esperado:
            res = "confirmado" if presente else "ausente"
        else:
            res = "ainda_presente" if presente else "remocao_confirmada"
        conn.execute("UPDATE lattes_envios SET xml_status = ?, xml_verificado_em = ? WHERE id = ?", (res, agora, eid))
        cont[res] += 1
    return dict(cont)
