"""Dados da tela de abertura: indicadores de produção, citações e eventos de um pesquisador.

Só entra aqui o que existe de verdade: obras e citações vêm do OpenAlex/OpenCitations/Crossref (por ORCID)
e os envios vêm da tabela `records` do próprio LattesData. Nada é inventado; o que falta vem vazio.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from collections import Counter
from datetime import datetime
from typing import Any

from citacoes import fontes
from citacoes.servico import citacoes_do_pesquisador

TTL = 1800
ANOS = 11
ESPERA = 4  # segundos que o pedido espera pelas bases externas antes de responder só com o que já tem
_cache: dict[str, tuple[float, tuple[list, dict, list]]] = {}  # orcid -> (quando, (obras, citações, avisos))
_jobs: dict[str, Future] = {}
_lock = threading.Lock()
_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="abertura")

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


def _db_path(conn: sqlite3.Connection) -> str:
    try:
        return conn.execute("PRAGMA database_list").fetchone()[2] or ""
    except Exception:
        return ""


def _ler_disco(path: str, orcid: str) -> tuple[float, tuple[list, dict, list]] | None:
    if not path:
        return None
    try:
        with sqlite3.connect(path) as c:
            c.execute("CREATE TABLE IF NOT EXISTS abertura_cache (orcid TEXT PRIMARY KEY, ts REAL, payload TEXT)")
            r = c.execute("SELECT ts, payload FROM abertura_cache WHERE orcid = ?", (orcid,)).fetchone()
        if r:
            o, ci, av = json.loads(r[1])
            return r[0], (o, ci, av)
    except Exception:
        pass
    return None


def _gravar_disco(path: str, orcid: str, ts: float, res: tuple[list, dict, list]) -> None:
    if not path:
        return
    try:
        with sqlite3.connect(path) as c:
            c.execute("CREATE TABLE IF NOT EXISTS abertura_cache (orcid TEXT PRIMARY KEY, ts REAL, payload TEXT)")
            c.execute("INSERT OR REPLACE INTO abertura_cache VALUES (?, ?, ?)", (orcid, ts, json.dumps(res, ensure_ascii=False)))
    except Exception:
        pass


def _externo(orcid: str, path: str) -> tuple[list, dict, list]:
    """Consulta lenta (OpenAlex/OpenCitations/Crossref). Roda em segundo plano e guarda o resultado (memória e disco)."""
    avisos: list[str] = []
    obras: list[dict[str, Any]] = []
    cit: dict[str, Any] = {}
    try:
        obras = fontes.openalex_obras_por_orcid(orcid, 100)
    except Exception:
        avisos.append("Não foi possível listar as obras no OpenAlex.")
    try:
        cit = citacoes_do_pesquisador(orcid=orcid, max_obras=15, max_citantes=100, obras_prontas=obras)
    except Exception:
        avisos.append("Não foi possível consultar as bases de citação.")
    if not obras and not cit.get("obras"):
        avisos.append("Nenhuma obra encontrada para este ORCID.")
    res = (obras, cit, avisos)
    if not avisos:  # resposta parcial/falha nunca sobrescreve o que já estava salvo
        agora = time.time()
        with _lock:
            _cache[orcid] = (agora, res)
        _gravar_disco(path, orcid, agora, res)
    return res


def _externo_ou_pendente(orcid: str, path: str) -> tuple[list, dict, list, bool, bool]:
    """(obras, citações, avisos, pendente, atualizando). Com qualquer resultado salvo, responde na hora."""
    with _lock:
        hit = _cache.get(orcid)
    if not hit:
        hit = _ler_disco(path, orcid)
        if hit:
            with _lock:
                _cache[orcid] = hit
    fresco = bool(hit and time.time() - hit[0] < TTL)
    if not fresco:
        with _lock:
            job = _jobs.get(orcid)
            if job is None or job.done():
                job = _pool.submit(_externo, orcid, path)
                _jobs[orcid] = job
    if hit:  # instantâneo: dado salvo (mesmo velho) enquanto o job atualiza por trás
        return (*hit[1], False, not fresco)
    try:
        return (*job.result(timeout=ESPERA), False, False)
    except TimeoutError:
        return [], {}, ["Calculando produção e citações nas bases externas…"], True, False
    except Exception:
        return [], {}, ["Não foi possível consultar as bases externas."], False, False


def montar_abertura(conn: sqlite3.Connection, usuario: str, orcid: str | None) -> dict[str, Any]:
    ano_fim = datetime.now().year
    envios = _envios(conn, usuario)
    obras: list[dict[str, Any]] = []
    cit: dict[str, Any] = {}
    avisos: list[str] = []
    pendente = atualizando = False
    if orcid:
        obras, cit, avisos, pendente, atualizando = _externo_ou_pendente(orcid, _db_path(conn))

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
        "usuario": usuario, "orcid": orcid or "", "ano_atual": ano_fim, "avisos": avisos, "pendente": pendente, "atualizando": atualizando,
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
    return res


# Pesquisadores cujo painel é aquecido ao subir o servidor e renovado de tempos em tempos (entrada sempre instantânea).
ORCIDS_AQUECIDOS = ("0000-0003-4999-6382",)  # Aramys Silva dos Reis


def aquecer(path: str, orcids: tuple[str, ...] = ORCIDS_AQUECIDOS, a_cada: int = TTL - 120) -> None:
    """Mantém o cache externo desses ORCIDs quente: carrega do disco, atualiza em segundo plano e repete."""
    def ciclo() -> None:
        while True:
            for o in orcids:
                try:
                    hit = _ler_disco(path, o)
                    if hit:
                        with _lock:
                            _cache.setdefault(o, hit)
                    _externo(o, path)
                except Exception:
                    pass
            time.sleep(a_cada)
    threading.Thread(target=ciclo, daemon=True, name="abertura-aquecer").start()
