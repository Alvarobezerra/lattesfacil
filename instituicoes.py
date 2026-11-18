"""Banco de instituições do Lattes: dicionário de confirmações, índice local e gerenciador da captação gradual.

O cadastro de instituições do Lattes só é consultável pela lupa (busca por texto no servidor do CNPq). Este módulo guarda
o que a lupa devolveu (gravação oportunista a cada consulta e coleta limitada por prefixos) e o que os usuários confirmaram,
para que o preenchimento e a tela de revisão consultem primeiro o banco local. Só biblioteca padrão.

Captação: ordem fixa de prioridade com os 6 prefixos (Universidade, Instituto, Faculdade, Hospital, Centro, Fundação); quando
um prefixo satura (a lupa devolve o máximo que mostra), ele é aprofundado com as próximas palavras mais frequentes nos nomes
já guardados. Tudo com teto diário, teto por lote e intervalo mínimo entre consultas; desligada por padrão.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

PREFIXOS_PRIORITARIOS = ["Universidade", "Instituto", "Faculdade", "Hospital", "Centro", "Fundação"]
QUALIFICADORES = {  # primeira camada de aprofundamento quando o prefixo satura e o banco ainda não tem palavras suficientes
    "universidade": ["Federal", "Estadual", "Municipal", "Católica", "Tecnológica"],
    "instituto": ["Federal", "Nacional", "de Pesquisa", "de Tecnologia", "de Ciências"],
    "faculdade": ["de Medicina", "de Tecnologia", "de Ciências", "de Direito", "de Educação"],
    "hospital": ["Universitário", "das Clínicas", "de Clínicas", "Municipal", "Santa"],
    "centro": ["Universitário", "de Ciências", "de Tecnologia", "de Pesquisa", "Federal"],
    "fundação": ["Oswaldo Cruz", "de Amparo", "Universidade", "Instituto", "Centro"],
}
CONFIG_PADRAO = {"ativa": 0, "limite_dia": 40, "limite_lote": 10, "intervalo_ms": 4000, "cap_resultados": 0, "niveis_max": 3}
TETO = {"limite_dia": 200, "limite_lote": 25, "intervalo_ms": (2000, 60000), "cap_resultados": (0, 5000), "niveis_max": (1, 4)}
SIGLAS_SEMENTE = {
    "UFC": "Universidade Federal do Ceará", "UFMA": "Universidade Federal do Maranhão", "USP": "Universidade de São Paulo",
    "UNICAMP": "Universidade Estadual de Campinas", "UFRJ": "Universidade Federal do Rio de Janeiro",
    "UFMG": "Universidade Federal de Minas Gerais", "UFRGS": "Universidade Federal do Rio Grande do Sul",
    "UFPE": "Universidade Federal de Pernambuco", "UFBA": "Universidade Federal da Bahia",
    "UFSC": "Universidade Federal de Santa Catarina", "UFPR": "Universidade Federal do Paraná",
    "UNB": "Universidade de Brasília", "UNESP": "Universidade Estadual Paulista Júlio de Mesquita Filho",
    "UERJ": "Universidade do Estado do Rio de Janeiro", "UFF": "Universidade Federal Fluminense",
    "UFPA": "Universidade Federal do Pará", "UFAM": "Universidade Federal do Amazonas", "UFPB": "Universidade Federal da Paraíba",
    "UFRN": "Universidade Federal do Rio Grande do Norte", "UFPI": "Universidade Federal do Piauí",
    "UFS": "Universidade Federal de Sergipe", "UFAL": "Universidade Federal de Alagoas",
    "UFES": "Universidade Federal do Espírito Santo", "UFG": "Universidade Federal de Goiás",
    "UFMT": "Universidade Federal de Mato Grosso", "UFMS": "Universidade Federal de Mato Grosso do Sul",
    "UFU": "Universidade Federal de Uberlândia", "UFSCAR": "Universidade Federal de São Carlos",
    "UNIFESP": "Universidade Federal de São Paulo", "UECE": "Universidade Estadual do Ceará",
    "UFRPE": "Universidade Federal Rural de Pernambuco", "UFC-SOBRAL": "Universidade Federal do Ceará - Campus Sobral",
    "FIOCRUZ": "Fundação Oswaldo Cruz", "EMBRAPA": "Empresa Brasileira de Pesquisa Agropecuária",
    "IFCE": "Instituto Federal de Educação, Ciência e Tecnologia do Ceará", "UEMA": "Universidade Estadual do Maranhão",
}


def norm(t: Any) -> str:
    s = unicodedata.normalize("NFD", str(t or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"\s*\([a-z]{2}\)\s*$", "", s)  # sufixo de UF "(CE)" que a lupa acrescenta
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS inst_banco (
            id INTEGER PRIMARY KEY AUTOINCREMENT, chave TEXT NOT NULL UNIQUE, nome TEXT NOT NULL, sigla TEXT DEFAULT '',
            codigo TEXT DEFAULT '', ref TEXT DEFAULT '', origem TEXT NOT NULL, vezes INTEGER NOT NULL DEFAULT 1,
            primeira_em TEXT NOT NULL, ultima_em TEXT NOT NULL)"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS ix_inst_sigla ON inst_banco (sigla)")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS inst_alias (
            texto TEXT PRIMARY KEY, inst_id INTEGER NOT NULL, confirmada_por TEXT DEFAULT '', em TEXT NOT NULL)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS inst_fila (
            termo TEXT PRIMARY KEY, prioridade INTEGER NOT NULL, nivel INTEGER NOT NULL, estado TEXT NOT NULL DEFAULT 'pendente',
            tentativas INTEGER NOT NULL DEFAULT 0, ultimo_em TEXT, resultados INTEGER NOT NULL DEFAULT 0, novas INTEGER NOT NULL DEFAULT 0)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS inst_consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, quando TEXT NOT NULL, termo TEXT NOT NULL, origem TEXT NOT NULL,
            resultados INTEGER NOT NULL DEFAULT 0, novas INTEGER NOT NULL DEFAULT 0, ms INTEGER NOT NULL DEFAULT 0,
            amostra TEXT DEFAULT '', erro TEXT DEFAULT '')"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS ix_inst_consultas_q ON inst_consultas (quando)")
    if "lote_id" not in [r[1] for r in conn.execute("PRAGMA table_info(inst_consultas)").fetchall()]:
        conn.execute("ALTER TABLE inst_consultas ADD COLUMN lote_id TEXT")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_inst_consultas_lote ON inst_consultas (lote_id) WHERE lote_id IS NOT NULL")
    conn.execute("CREATE TABLE IF NOT EXISTS inst_config (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
    for i, p in enumerate(PREFIXOS_PRIORITARIOS):
        conn.execute("INSERT OR IGNORE INTO inst_fila (termo, prioridade, nivel) VALUES (?,?,1)", (p, i))
    agora_ = agora()
    for sigla, nome in SIGLAS_SEMENTE.items():
        conn.execute(
            "INSERT OR IGNORE INTO inst_banco (chave, nome, sigla, origem, primeira_em, ultima_em) VALUES (?,?,?,?,?,?)",
            (norm(nome), nome, sigla, "semente", agora_, agora_),
        )


# ---------- configuração ----------
def config(conn: sqlite3.Connection) -> dict[str, int]:
    out = dict(CONFIG_PADRAO)
    for k, v in conn.execute("SELECT chave, valor FROM inst_config").fetchall():
        if k in out:
            try:
                out[k] = int(v)
            except ValueError:
                pass
    return out


def definir_config(conn: sqlite3.Connection, novos: dict[str, Any]) -> dict[str, int]:
    """Grava só chaves conhecidas, sempre dentro dos tetos (o gerenciador não permite exagerar no ritmo da coleta)."""
    for k, v in (novos or {}).items():
        if k not in CONFIG_PADRAO:
            continue
        try:
            n = int(v)
        except (TypeError, ValueError):
            continue
        if k == "ativa":
            n = 1 if n else 0
        elif k in ("limite_dia", "limite_lote"):
            n = max(1, min(n, TETO[k]))
        else:
            lo, hi = TETO[k]
            n = max(lo, min(n, hi))
        conn.execute("INSERT INTO inst_config (chave, valor) VALUES (?,?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor", (k, str(n)))
    return config(conn)


# ---------- gravação ----------
def _sigla_do_nome(nome: str) -> str:
    m = re.search(r"\(([A-Za-z][A-Za-z0-9\-]{1,11})\)\s*$", nome.strip())
    return m.group(1).upper() if m and not re.fullmatch(r"[A-Z]{2}", m.group(1)) else ""


def _codigo_do_ref(ref: str) -> str:
    """Primeiro argumento de seleciona(...) quando é um código simples; o formato real é conferido pela amostra gravada."""
    m = re.match(r"\s*['\"]?([A-Za-z0-9_\-]{3,40})['\"]?\s*(?:,|$)", ref or "")
    return m.group(1) if m else ""


def registrar(conn: sqlite3.Connection, itens: list[dict[str, Any]], termo: str, origem: str, ms: int = 0, erro: str = "", lote_id: str = "") -> dict[str, int]:
    """Guarda as candidatas devolvidas por UMA consulta da lupa e registra a consulta (métrica). Devolve {total, novas}."""
    origem = origem if origem in ("coleta", "uso") else "uso"
    lote_id = re.sub(r"[^A-Za-z0-9_\-]", "", str(lote_id or ""))[:40] or None
    if lote_id and conn.execute("SELECT 1 FROM inst_consultas WHERE lote_id = ?", (lote_id,)).fetchone():
        return {"total": 0, "novas": 0, "duplicado": 1}  # a mesma consulta já chegou por outra aba do app
    termo = re.sub(r"\s+", " ", str(termo or "")).strip()[:120]
    agora_ = agora()
    novas = 0
    vistos: set[str] = set()
    amostra: list[str] = []
    for it in (itens or [])[:300]:
        nome = re.sub(r"\s+", " ", str((it or {}).get("nome", ""))).strip()[:200]
        chave = norm(nome)
        if len(chave) < 3 or chave in vistos:
            continue
        vistos.add(chave)
        ref = str((it or {}).get("ref", ""))[:200]
        if len(amostra) < 3 and ref:
            amostra.append(ref)
        codigo = str((it or {}).get("codigo", "") or _codigo_do_ref(ref))[:40]
        sigla = _sigla_do_nome(nome)
        ja = conn.execute("SELECT id, origem FROM inst_banco WHERE chave = ?", (chave,)).fetchone()
        if ja:
            conn.execute(
                "UPDATE inst_banco SET vezes = vezes + 1, ultima_em = ?, codigo = CASE WHEN ? != '' THEN ? ELSE codigo END, "
                "ref = CASE WHEN ? != '' THEN ? ELSE ref END, sigla = CASE WHEN sigla = '' THEN ? ELSE sigla END, "
                "origem = CASE WHEN origem = 'semente' THEN 'coletada' ELSE origem END WHERE id = ?",
                (agora_, codigo, codigo, ref, ref, sigla, ja[0]),
            )
        else:
            conn.execute(
                "INSERT INTO inst_banco (chave, nome, sigla, codigo, ref, origem, primeira_em, ultima_em) VALUES (?,?,?,?,?,?,?,?)",
                (chave, nome, sigla, codigo, ref, "coletada", agora_, agora_),
            )
            novas += 1
    total = len(vistos)
    conn.execute(
        "INSERT INTO inst_consultas (quando, termo, origem, resultados, novas, ms, amostra, erro, lote_id) VALUES (?,?,?,?,?,?,?,?,?)",
        (agora_, termo, origem, total, novas, max(0, int(ms or 0)), json.dumps(amostra, ensure_ascii=False), str(erro or "")[:200], lote_id),
    )
    if origem == "coleta" and termo:
        _atualizar_fila(conn, termo, total, novas, bool(erro))
    return {"total": total, "novas": novas}


# ---------- fila de prefixos ----------
def cap_detectado(conn: sqlite3.Connection) -> int:
    c = config(conn)["cap_resultados"]
    if c:
        return c
    linhas = conn.execute("SELECT resultados FROM inst_consultas WHERE erro = '' AND resultados > 0").fetchall()
    if len(linhas) < 3:
        return 0
    cont = Counter(r[0] for r in linhas)
    topo = max(cont)
    return topo if topo >= 10 and cont[topo] >= 2 else 0  # o máximo se repete: a lupa corta nesse número


def _atualizar_fila(conn: sqlite3.Connection, termo: str, total: int, novas: int, com_erro: bool) -> None:
    linha = conn.execute("SELECT nivel FROM inst_fila WHERE termo = ?", (termo,)).fetchone()
    if not linha:
        return
    if com_erro:
        conn.execute("UPDATE inst_fila SET tentativas = tentativas + 1, ultimo_em = ? WHERE termo = ?", (agora(), termo))
        return
    cap = cap_detectado(conn)
    saturou = bool(cap and total >= cap)
    conn.execute(
        "UPDATE inst_fila SET estado = ?, tentativas = tentativas + 1, ultimo_em = ?, resultados = ?, novas = ? WHERE termo = ?",
        ("saturado" if saturou else "feito", agora(), total, novas, termo),
    )
    if saturou:
        expandir(conn, termo, linha[0])


def expandir(conn: sqlite3.Connection, termo: str, nivel: int) -> int:
    """Aprofunda um termo saturado: próximas palavras mais frequentes nos nomes já guardados (e qualificadores iniciais)."""
    if nivel >= config(conn)["niveis_max"]:
        return 0
    base = norm(termo)
    prox: Counter[str] = Counter()
    for (nome,) in conn.execute("SELECT nome FROM inst_banco WHERE chave LIKE ?", (base + " %",)).fetchall():
        resto = nome[len(termo):].strip() if norm(nome).startswith(base) else ""
        pal = resto.split(" ")[0] if resto else ""
        if len(pal) > 2 and not re.fullmatch(r"(d[aeo]s?|e)", pal.lower()):
            prox[pal] += 1
    cands = [w for w, _ in prox.most_common(8)]
    if nivel == 1:
        cands = list(dict.fromkeys([*QUALIFICADORES.get(base, []), *cands]))
    prio = conn.execute("SELECT prioridade FROM inst_fila WHERE termo = ?", (termo,)).fetchone()
    prio = prio[0] if prio else 0
    n = 0
    for w in cands[:10]:
        novo = f"{termo} {w}".strip()
        cur = conn.execute("INSERT OR IGNORE INTO inst_fila (termo, prioridade, nivel) VALUES (?,?,?)", (novo, prio, nivel + 1))
        n += cur.rowcount
    return n


def consultas_hoje(conn: sqlite3.Connection, origem: str = "coleta") -> int:
    ini = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")
    return conn.execute("SELECT COUNT(*) FROM inst_consultas WHERE origem = ? AND quando >= ?", (origem, ini)).fetchone()[0]


def proximo_lote(conn: sqlite3.Connection) -> dict[str, Any]:
    """Termos a consultar agora. Respeita ativa/teto diário/teto do lote e SEMPRE esgota a camada dos 6 prefixos antes de aprofundar."""
    cfg = config(conn)
    feitas = consultas_hoje(conn)
    restante = max(0, cfg["limite_dia"] - feitas)
    out: dict[str, Any] = {"ativa": bool(cfg["ativa"]), "restante_hoje": restante, "intervalo_ms": cfg["intervalo_ms"], "termos": [], "motivo": ""}
    if not cfg["ativa"]:
        out["motivo"] = "coleta desligada no gerenciador"
        return out
    if restante <= 0:
        out["motivo"] = "teto diário atingido"
        return out
    n = min(cfg["limite_lote"], restante)
    rows = conn.execute(
        "SELECT termo FROM inst_fila WHERE estado = 'pendente' "
        "ORDER BY nivel ASC, prioridade ASC, tentativas ASC, termo ASC LIMIT ?", (n,),
    ).fetchall()
    out["termos"] = [r[0] for r in rows]
    if not out["termos"]:
        out["motivo"] = "fila concluída (nada pendente)"
    return out


# ---------- consulta local ----------
def _pontos(q: str, nome: str, sigla: str) -> float:
    qn, nn = norm(q), norm(nome)
    if not qn:
        return 0.0
    if sigla and qn == norm(sigla):
        return 1.0
    if qn == nn:
        return 1.0
    ta, tb = set(qn.split()) - {"de", "da", "do", "das", "dos", "e"}, set(nn.split()) - {"de", "da", "do", "das", "dos", "e"}
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return inter / len(ta | tb)


def buscar(conn: sqlite3.Connection, q: str, limite: int = 8) -> dict[str, Any]:
    """Procura no banco local: confirmação anterior > sigla/nome exato > similares. 'claro' = um candidato nítido."""
    q = re.sub(r"\s+", " ", str(q or "")).strip()[:200]
    if len(norm(q)) < 2:
        return {"consulta": q, "candidatas": [], "claro": False, "confirmada": False}
    al = conn.execute("SELECT inst_id FROM inst_alias WHERE texto = ?", (norm(q),)).fetchone()
    if al:
        r = conn.execute("SELECT id, nome, sigla, codigo, origem FROM inst_banco WHERE id = ?", (al[0],)).fetchone()
        if r:
            return {"consulta": q, "candidatas": [_linha(r, 1.0, "confirmada")], "claro": True, "confirmada": True}
    qn = norm(q)
    achadas: dict[int, tuple[float, tuple]] = {}
    for r in conn.execute("SELECT id, nome, sigla, codigo, origem FROM inst_banco WHERE sigla = ? OR chave = ? OR chave LIKE ? LIMIT 400", (q.upper(), qn, "%" + qn + "%")).fetchall():
        achadas[r[0]] = (_pontos(q, r[1], r[2]), r)
    pal = [p for p in qn.split() if len(p) > 3][:3]
    for p in pal:
        for r in conn.execute("SELECT id, nome, sigla, codigo, origem FROM inst_banco WHERE chave LIKE ? LIMIT 400", ("%" + p + "%",)).fetchall():
            achadas.setdefault(r[0], (_pontos(q, r[1], r[2]), r))
    ordem = sorted(achadas.values(), key=lambda x: (-x[0], -len(x[1][3] or ""), x[1][1]))[:limite]
    cands = [_linha(r, round(s, 2), "banco") for s, r in ordem if s >= 0.34]
    claro = bool(cands) and cands[0]["pontos"] >= 0.75 and (len(cands) < 2 or cands[1]["pontos"] <= cands[0]["pontos"] - 0.15)
    return {"consulta": q, "candidatas": cands, "claro": claro, "confirmada": False}


def _linha(r: tuple, pontos: float, fonte: str) -> dict[str, Any]:
    return {"id": r[0], "nome": r[1], "sigla": r[2], "codigo": r[3], "origem": r[4], "pontos": pontos, "fonte": fonte}


def confirmar(conn: sqlite3.Connection, texto: str, inst_id: int, usuario: str = "") -> bool:
    """Guarda 'texto do documento -> instituição' escolhido pelo usuário (e promove o registro a 'confirmada')."""
    chave = norm(texto)
    if len(chave) < 2 or not conn.execute("SELECT 1 FROM inst_banco WHERE id = ?", (int(inst_id),)).fetchone():
        return False
    conn.execute(
        "INSERT INTO inst_alias (texto, inst_id, confirmada_por, em) VALUES (?,?,?,?) "
        "ON CONFLICT(texto) DO UPDATE SET inst_id=excluded.inst_id, confirmada_por=excluded.confirmada_por, em=excluded.em",
        (chave, int(inst_id), str(usuario)[:60], agora()),
    )
    conn.execute("UPDATE inst_banco SET origem = 'confirmada' WHERE id = ?", (int(inst_id),))
    return True


def desfazer_confirmacao(conn: sqlite3.Connection, texto: str) -> bool:
    return conn.execute("DELETE FROM inst_alias WHERE texto = ?", (norm(texto),)).rowcount > 0


def importar_lista(conn: sqlite3.Connection, texto: str, primeira_e_nome: bool = False) -> dict[str, int]:
    """Lista de nomes como o Lattes mostra ('Universidade Federal do Maranhão (MA)'), um por linha, com cabeçalho 'Instituição'.
    O sufixo (UF/país) fica no nome, como no Lattes; não vira sigla. Repetidas (mesmo nome sem acento/caixa) entram uma vez."""
    lidas = novas = 0
    agora_ = agora()
    for i, linha in enumerate(texto.splitlines()):
        nome = re.sub(r"\s+", " ", linha).strip().strip('"')[:200]
        if i == 0 and not primeira_e_nome and norm(nome) in ("instituicao", "instituicoes", "nome", "nome da instituicao", "nome da ies"):
            continue
        if len(norm(nome)) < 3:
            continue
        lidas += 1
        cur = conn.execute(
            "INSERT OR IGNORE INTO inst_banco (chave, nome, sigla, origem, primeira_em, ultima_em) VALUES (?,?,?,?,?,?)",
            (norm(nome), nome, "", "semente", agora_, agora_),
        )
        novas += cur.rowcount
    return {"lidas": lidas, "novas": novas}


def importar_csv(conn: sqlite3.Connection, texto: str) -> dict[str, int]:
    """Semente a partir de uma lista pública (ex.: dados abertos do e-MEC): colunas de nome e sigla, separador ; ou ,."""
    primeira = next((l.strip() for l in texto.splitlines() if l.strip()), "")
    if norm(primeira) in ("instituicao", "instituicoes", "nome", "nome da instituicao", "nome da ies"):
        return importar_lista(conn, texto)  # uma coluna só, um nome por linha (nomes têm vírgula: não dá para tratar como CSV)
    amostra = texto[:2000]
    sep = ";" if amostra.count(";") >= amostra.count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=sep)
    campos = {norm(c): c for c in (leitor.fieldnames or [])}

    def col(*nomes: str) -> str | None:
        for n in nomes:
            for k, v in campos.items():
                if n in k:
                    return v
        return None

    c_nome = col("nome da ies", "no ies", "nome", "instituicao")
    c_sigla = col("sigla", "sg ies")
    if not c_nome:
        # sem cabeçalho conhecido e sem ';': é uma lista simples, um nome por linha (a 1ª linha também é nome)
        return importar_lista(conn, texto, primeira_e_nome=True) if ";" not in amostra else {"lidas": 0, "novas": 0}
    lidas = novas = 0
    agora_ = agora()
    for linha in leitor:
        nome = re.sub(r"\s+", " ", str(linha.get(c_nome, ""))).strip()[:200]
        if len(norm(nome)) < 4:
            continue
        lidas += 1
        sigla = str(linha.get(c_sigla, "") if c_sigla else "").strip().upper()[:12]
        cur = conn.execute(
            "INSERT OR IGNORE INTO inst_banco (chave, nome, sigla, origem, primeira_em, ultima_em) VALUES (?,?,?,?,?,?)",
            (norm(nome), nome, sigla, "semente", agora_, agora_),
        )
        novas += cur.rowcount
        if not cur.rowcount and sigla:
            conn.execute("UPDATE inst_banco SET sigla = ? WHERE chave = ? AND sigla = ''", (sigla, norm(nome)))
    return {"lidas": lidas, "novas": novas}


# ---------- gerenciador (monitoramento) ----------
def estatisticas(conn: sqlite3.Connection) -> dict[str, Any]:
    cfg = config(conn)
    por_origem = {o: n for o, n in conn.execute("SELECT origem, COUNT(*) FROM inst_banco GROUP BY origem").fetchall()}
    com_codigo = conn.execute("SELECT COUNT(*) FROM inst_banco WHERE codigo != ''").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM inst_banco").fetchone()[0]
    ult = conn.execute("SELECT resultados, novas, ms, erro FROM inst_consultas ORDER BY id DESC LIMIT 50").fetchall()
    ok = [r for r in ult if not r[3]]
    res_total = sum(r[0] for r in ok)
    desde = (datetime.now(timezone.utc) - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")
    por_dia = {d: {"coleta": 0, "uso": 0, "novas": 0} for d in ((datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1))}
    for quando, origem, novas in conn.execute("SELECT quando, origem, novas FROM inst_consultas WHERE quando >= ?", (desde,)).fetchall():
        d = quando[:10]
        if d in por_dia:
            por_dia[d][origem if origem in ("coleta", "uso") else "uso"] += 1
            por_dia[d]["novas"] += novas
    prefixos = []
    for p in PREFIXOS_PRIORITARIOS:
        r = conn.execute("SELECT estado, tentativas, resultados, novas, ultimo_em FROM inst_fila WHERE termo = ?", (p,)).fetchone()
        filhos = conn.execute("SELECT COUNT(*), SUM(estado != 'pendente') FROM inst_fila WHERE termo LIKE ? AND termo != ?", (p + " %", p)).fetchone()
        prefixos.append({"termo": p, "estado": r[0], "tentativas": r[1], "resultados": r[2], "novas": r[3], "ultimo_em": r[4],
                         "aprofundamentos": filhos[0] or 0, "aprofundamentos_feitos": filhos[1] or 0})
    fila = {e: n for e, n in conn.execute("SELECT estado, COUNT(*) FROM inst_fila GROUP BY estado").fetchall()}
    amostras = [json.loads(a) for (a,) in conn.execute("SELECT amostra FROM inst_consultas WHERE amostra != '' AND amostra != '[]' ORDER BY id DESC LIMIT 3").fetchall()]
    erros = conn.execute("SELECT quando, termo, erro FROM inst_consultas WHERE erro != '' ORDER BY id DESC LIMIT 5").fetchall()
    return {
        "config": cfg, "banco": {"total": total, "com_codigo": com_codigo, "por_origem": por_origem, "aliases": conn.execute("SELECT COUNT(*) FROM inst_alias").fetchone()[0]},
        "hoje": {"coleta": consultas_hoje(conn), "uso": consultas_hoje(conn, "uso"), "restante": max(0, cfg["limite_dia"] - consultas_hoje(conn))},
        "desempenho": {
            "consultas_total": conn.execute("SELECT COUNT(*) FROM inst_consultas").fetchone()[0],
            "ms_medio": round(sum(r[2] for r in ok) / len(ok)) if ok else 0,
            "resultados_medio": round(res_total / len(ok), 1) if ok else 0,
            "taxa_novidade": round(sum(r[1] for r in ok) / res_total, 3) if res_total else 0,
            "cap_detectado": cap_detectado(conn),
            "erros_recentes": [{"quando": q, "termo": t, "erro": e} for q, t, e in erros],
        },
        "prefixos": prefixos, "fila": fila, "por_dia": [{"dia": d, **v} for d, v in por_dia.items()],
        "amostras_ref": amostras,
    }
