"""Dados da tela de abertura: indicadores de produção, citações e eventos de um pesquisador.

Só entra aqui o que existe de verdade: obras e citações vêm do OpenAlex/OpenCitations/Crossref (por ORCID)
e os envios vêm da tabela `records` do próprio LattesData. Nada é inventado; o que falta vem vazio.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from collections import Counter
from datetime import datetime
from typing import Any

from citacoes import fontes
from citacoes.servico import citacoes_do_pesquisador

TTL = 1800
ANOS = 11
_cache: dict[tuple[str, str], tuple[float, dict[str, Any]]] = {}
_lock = threading.Lock()

# tipo_producao dos registros -> grupo do indicador
EVENTOS = {"anais", "apresentacao", "evento", "participacao_evento", "organizacao_evento"}
ORIENTACOES = {"orientacao", "orientacao_concluida", "orientacao_andamento"}


def indice_h(contagens: list[int]) -> int:
    ordenadas = sorted(contagens, reverse=True)
    return sum(1 for i, c in enumerate(ordenadas, 1) if c >= i)


def _serie(por_ano: Counter[int], ano_fim: int) -> list[dict[str, int]]:
    return [{"ano": a, "valor": por_ano.get(a, 0)} for a in range(ano_fim - ANOS + 1, ano_fim + 1)]


def _ano(valor: Any) -> int | None:
    s = str(valor or "").strip()[:4]
    return int(s) if s.isdigit() and 1900 < int(s) < 2100 else None


def _envios(conn: sqlite3.Connection, usuario: str) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT titulo, payload, created_at FROM records WHERE deleted_at IS NULL AND owner = ? ORDER BY created_at DESC",
        (usuario,),
    ).fetchall()
    por_tipo: Counter[str] = Counter()
    eventos_ano: Counter[int] = Counter()
    recentes: list[dict[str, Any]] = []
    for titulo, payload, criado in rows:
        try:
            d = json.loads(payload)
        except ValueError:
            d = {}
        tipo = str(d.get("tipo_producao") or "outro")
        por_tipo[tipo] += 1
        if tipo in EVENTOS and _ano(d.get("ano")):
            eventos_ano[_ano(d.get("ano"))] += 1
        if len(recentes) < 6:
            recentes.append({"titulo": titulo, "tipo": tipo, "ano": _ano(d.get("ano")), "criado_em": criado})
    return {
        "total": len(rows), "por_tipo": dict(por_tipo), "eventos_por_ano": eventos_ano, "recentes": recentes,
        "eventos": sum(v for k, v in por_tipo.items() if k in EVENTOS),
        "orientacoes": sum(v for k, v in por_tipo.items() if k in ORIENTACOES),
    }


def montar_abertura(conn: sqlite3.Connection, usuario: str, orcid: str | None) -> dict[str, Any]:
    chave = (usuario, orcid or "")
    with _lock:
        hit = _cache.get(chave)
        if hit and time.time() - hit[0] < TTL:
            return hit[1]

    ano_fim = datetime.now().year
    avisos: list[str] = []
    envios = _envios(conn, usuario)

    obras: list[dict[str, Any]] = []
    cit: dict[str, Any] = {}
    if orcid:
        try:
            obras = fontes.openalex_obras_por_orcid(orcid, 100)
        except Exception:
            avisos.append("Não foi possível listar as obras no OpenAlex.")
        try:
            cit = citacoes_do_pesquisador(orcid=orcid, max_obras=25)
        except Exception:
            avisos.append("Não foi possível consultar as bases de citação.")
        if not obras and not cit.get("obras"):
            avisos.append("Nenhuma obra encontrada para este ORCID.")

    # produção por ano (obras indexadas no OpenAlex)
    prod_ano: Counter[int] = Counter(o["ano"] for o in obras if o.get("ano"))

    # citações
    resumo = cit.get("resumo", {})
    obras_cit = cit.get("obras", [])
    totais = [o["total_estimado"] for o in obras_cit]
    por_ano_cit = Counter({int(a): n for a, n in (resumo.get("por_ano") or {}).items()})
    citantes: list[dict[str, Any]] = []
    veiculos: Counter[str] = Counter()
    for o in obras_cit:
        for c in o["citantes"]:
            if c.get("veiculo"):
                veiculos[c["veiculo"]] += 1
            citantes.append({
                "titulo": c.get("titulo") or "", "doi": c.get("doi") or "", "ano": c.get("ano"),
                "veiculo": c.get("veiculo") or "", "fontes": c.get("fontes", []),
                "autocitacao": c.get("autocitacao", False),
                "obra": o["titulo"], "obra_doi": o["doi"],
            })
    citantes.sort(key=lambda c: c["ano"] or 0, reverse=True)

    res = {
        "usuario": usuario, "orcid": orcid or "", "ano_atual": ano_fim, "avisos": avisos,
        "consultado_em": resumo.get("consultado_em") or time.strftime("%Y-%m-%d %H:%M"),
        "producao": {
            "total": len(obras), "serie": _serie(prod_ano, ano_fim),
            "no_ano": prod_ano.get(ano_fim, 0), "ano_anterior": prod_ano.get(ano_fim - 1, 0),
            "melhor_ano": max(prod_ano.items(), key=lambda kv: kv[1]) if prod_ano else None,
        },
        "citacoes": {
            "total": resumo.get("citacoes_unicas", 0), "sem_autocitacao": resumo.get("sem_autocitacao", 0),
            "autocitacoes": resumo.get("autocitacoes", 0), "h": indice_h(totais),
            "i10": sum(1 for t in totais if t >= 10), "serie": _serie(por_ano_cit, ano_fim),
            "no_ano": por_ano_cit.get(ano_fim, 0), "obras_consideradas": len(obras_cit),
            "obras_indexadas": len(obras),
        },
        "eventos": {
            "total": envios["eventos"], "serie": _serie(envios["eventos_por_ano"], ano_fim),
            "orientacoes": envios["orientacoes"],
        },
        "alcance": {
            "citantes_unicos": len(citantes), "periodicos": len(veiculos),
            "top_periodicos": [{"nome": n, "citacoes": q} for n, q in veiculos.most_common(5)],
        },
        "obras_mais_citadas": [
            {"titulo": o["titulo"], "doi": o["doi"], "ano": o["ano"], "veiculo": o["veiculo"],
             "total": o["total_estimado"], "fontes": o["contagem_fontes"]}
            for o in obras_cit[:5]
        ],
        "citantes_recentes": citantes[:8],
        "envios": {"total": envios["total"], "por_tipo": envios["por_tipo"], "recentes": envios["recentes"]},
    }
    if orcid and not avisos:  # não guarda resposta parcial/falha no cache
        with _lock:
            _cache[chave] = (time.time(), res)
    return res
