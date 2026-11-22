"""Histórico de currículos importados (snapshots), comparação entre versões, dashboard e conciliação de envios.

Cada XML do Lattes enviado vira um snapshot no SQLite (um por conteúdo distinto; reenviar o mesmo arquivo não duplica).
Comparando snapshots dá para saber o que entrou e saiu do currículo, e com isso confirmar (ou não) as inclusões e
exclusões feitas pelo NautiScience. Só biblioteca padrão.
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


# ------------------------------------------------------------------ dimensões e legado (concepção DORA / Trajetória)
DIMENSOES_CATEGORIAS: tuple[tuple[str, str, str, set[str]], ...] = (
    ("conhecimento", "Geração de conhecimento", "Artigos, livros, capítulos e trabalhos em anais",
     {"artigo", "artigo_aceito", "livro", "capitulo", "trabalho_evento", "texto_jornal",
      "outra_producao_bibliografica", "producao_artistica", "demais_trabalhos"}),
    ("formacao", "Formação de pessoas e ensino", "Orientações, bancas, cursos ministrados e formação",
     {"orientacao_concluida", "orientacao_andamento", "banca", "curso_ministrado",
      "formacao_academica", "formacao_complementar"}),
    ("comunidade", "Comunidade e diálogo científico", "Apresentações, eventos organizados, participações e prêmios",
     {"apresentacao", "participacao_evento", "organizacao_evento", "premio"}),
    ("impacto", "Inovação, projetos e prática aplicada", "Patentes, softwares, produtos técnicos, projetos e atuação",
     {"patente", "software", "produto_tecnologico", "registro_propriedade", "trabalho_tecnico",
      "outra_producao_tecnica", "projeto", "atuacao_profissional"}),
)


def calcular_dimensoes(por_cat: dict[str, int]) -> list[dict[str, Any]]:
    """Agrupa contagens por categoria nas 4 dimensões de contribuição da trajetória."""
    brutos = [
        (dim_id, nome, desc, sum(int(por_cat.get(c, 0) or 0) for c in cats))
        for dim_id, nome, desc, cats in DIMENSOES_CATEGORIAS
    ]
    max_dim = max((t for _, _, _, t in brutos), default=0)
    soma_geral = sum(t for _, _, _, t in brutos)
    saida: list[dict[str, Any]] = []
    for dim_id, nome, desc, total in brutos:
        if total == 0:
            percentual = 0
            nivel = "ponto de partida"
        else:
            percentual = max(12, round(total * 100 / max_dim)) if max_dim > 0 else 0
            if percentual >= 75:
                nivel = "frente principal"
            elif percentual >= 40:
                nivel = "frente ativa"
            else:
                nivel = "em expansão"
        proporcao = round(total * 100 / soma_geral) if soma_geral > 0 else 0
        saida.append({
            "id": dim_id,
            "nome": nome,
            "descricao": desc,
            "total": total,
            "percentual": percentual,
            "proporcao": proporcao,
            "nivel": nivel,
        })
    return saida


def calcular_legado_e_oportunidades(
    cur: dict[str, Any],
    por_cat: dict[str, int],
    artigos_info: dict[str, int],
    coautores_total: int,
) -> tuple[dict[str, int], list[dict[str, str]]]:
    """Calcula indicadores humanos de legado e sugestões construtivas de valorização."""
    del cur  # reservado para enriquecimentos futuros a partir de metadados do currículo
    legado = {
        "pessoas_orientadas": por_cat.get("orientacao_concluida", 0) + por_cat.get("orientacao_andamento", 0),
        "orientacoes_concluidas": por_cat.get("orientacao_concluida", 0),
        "orientacoes_andamento": por_cat.get("orientacao_andamento", 0),
        "bancas_participadas": por_cat.get("banca", 0),
        "projetos": por_cat.get("projeto", 0),
        "inovacao_tecnica": sum(por_cat.get(k, 0) for k in (
            "patente", "software", "produto_tecnologico", "registro_propriedade",
            "trabalho_tecnico", "outra_producao_tecnica",
        )),
        "coautores_unicos": coautores_total,
    }

    oportunidades: list[dict[str, str]] = []
    sem_doi = int(artigos_info.get("sem_doi", 0) or 0)
    if sem_doi > 0:
        plural = "s" if sem_doi != 1 else ""
        oportunidades.append({
            "id": "valorizar_doi",
            "titulo": f"{sem_doi} artigo{plural} pode{'' if sem_doi == 1 else 'm'} ganhar visibilidade com DOI",
            "descricao": "Completar o DOI amplia a localização automática na Plataforma Sucupira e nas bases abertas de citação.",
            "acao": "Valorizar artigos",
            "href": "/auditoria.html",
        })
    andamento = legado["orientacoes_andamento"]
    if andamento > 0:
        plural = "ões" if andamento != 1 else "ão"
        oportunidades.append({
            "id": "celebrar_orientacoes",
            "titulo": f"{andamento} orientaç{plural} em andamento para revisar",
            "descricao": "Se alguma defesa já foi concluída, atualizar o status celebra a formação e soma pontuação integral nos editais.",
            "acao": "Revisar trajetória",
            "href": "/meu-curriculo.html",
        })
    if legado["inovacao_tecnica"] > 0 or legado["projetos"] > 0:
        oportunidades.append({
            "id": "conectar_triade",
            "titulo": "Conectar projetos, produções técnicas e inovação",
            "descricao": "Amarrar patentes, softwares e artigos aos seus projetos fortalece a leitura de impacto na CAPES e no CNPq.",
            "acao": "Abrir painel relacional",
            "href": "/painel.html",
        })
    oportunidades.append({
        "id": "bussola_editais",
        "titulo": "Planejar próximo passo na Bússola de Editais",
        "descricao": "Simule metas para progressão, bolsas PQ ou concursos e organize seu dossiê paginado sem pressa.",
        "acao": "Simular cenário",
        "href": "/painel.html#secEdi",
    })
    return legado, oportunidades


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
    artigos_info = {
        "total": len(artigos),
        "sem_doi": sum(1 for a in artigos if not formatar_doi(a.get("doi", ""))),
        "sem_issn": sum(1 for a in artigos if not a.get("issn")),
    }
    producao = {"artigo", "artigo_aceito", "trabalho_evento", "livro", "capitulo", "texto_jornal", "patente", "software", "trabalho_tecnico",
                "produto_tecnologico", "apresentacao", "outra_producao_bibliografica", "outra_producao_tecnica", "producao_artistica"}
    dimensoes = calcular_dimensoes(por_cat)
    legado, oportunidades = calcular_legado_e_oportunidades(cur, por_cat, artigos_info, len(coautores))
    return {
        "nome": cur.get("nome", ""), "id_lattes": cur.get("id_lattes", ""), "atualizacao": cur.get("atualizacao", ""),
        "fonte": cur.get("fonte", "xml"), "total_itens": len(itens), "por_categoria": dict(por_cat.most_common()),
        "por_ano": [{"ano": a, "total": sum(por_ano[a].values()), "producao": sum(v for k, v in por_ano[a].items() if k in producao),
                     "por_categoria": dict(por_ano[a])} for a in anos],
        "ultimos_5_anos": sum(sum(v.values()) for a, v in por_ano.items() if ano_atual - 4 <= int(a) <= ano_atual),
        "artigos": artigos_info,
        "periodicos_top": Counter(a["veiculo"] for a in artigos if a.get("veiculo")).most_common(8),
        "coautores_top": coautores.most_common(10),
        "orientacoes": {"concluidas": por_cat.get("orientacao_concluida", 0), "em_andamento": por_cat.get("orientacao_andamento", 0)},
        "bancas": por_cat.get("banca", 0),
        "perfil": cur.get("perfil", {}),
        "nao_classificados": cur.get("nao_classificados", {}),
        "dimensoes": dimensoes,
        "legado": legado,
        "oportunidades": oportunidades,
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
    """Confere, contra o XML, os envios do NautiScience deste pesquisador e grava `xml_status` em cada um.

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
