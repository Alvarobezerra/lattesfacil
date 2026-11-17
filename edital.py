"""EditalScore: leitor de barema (texto do edital), cálculo de pontuação, simulação "e se" e dossiê em PDF.

O barema vira um dicionário estruturado (blocos -> itens, com pontos unitários, tetos e janela de anos). O cálculo
cruza com os itens do currículo (lattes_xml.ler_curriculo). Tudo é determinístico; o que o edital pede e o sistema
não consegue medir (ex.: estrato Qualis sem a base) aparece como pendência, nunca como pontos inventados.
A leitura do edital é heurística: o candidato revisa/edita o barema antes de confiar na nota.
"""
from __future__ import annotations

import datetime
import io
import re
import unicodedata
from typing import Any

# palavras do edital (sem acento) -> categorias do currículo (lattes_xml.TIPOS). Ordem importa.
ALIAS: list[tuple[str, tuple[str, ...]]] = [
    (r"capitulo", ("capitulo",)),
    (r"\blivro", ("livro",)),
    (r"artigo", ("artigo",)),
    (r"anais|resumo expandido|trabalho completo|trabalho publicado em evento|trabalhos? em evento", ("trabalho_evento",)),
    (r"apresentacao de trabalho|palestra|comunicacao oral", ("apresentacao",)),
    (r"orientacao|orientac", ("orientacao_concluida", "orientacao_andamento")),
    (r"banca", ("banca",)),
    (r"ministr", ("curso_ministrado",)),
    (r"patente", ("patente",)),
    (r"software|programa de computador", ("software",)),
    (r"projeto", ("projeto",)),
    (r"premio|titulo honor", ("premio",)),
    (r"organizacao de evento|comissao organizadora", ("organizacao_evento",)),
    (r"participacao em evento|congresso|simposio", ("participacao_evento",)),
    (r"curso|capacitacao|aperfeicoamento|formacao complementar|extensao", ("formacao_complementar",)),
    (r"experiencia|docencia|magisterio|atuacao profissional|exercicio", ("atuacao_profissional",)),
    (r"especializacao|mestrado|doutorado|pos-doutorado|graduacao", ("formacao_academica",)),
]
_ALIAS = [(re.compile(p), c) for p, c in ALIAS]
_NUM = r"(\d+(?:[.,]\d+)?)"


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower())


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def categorias_de(desc: str) -> list[str]:
    d = _norm(desc)
    for rx, cats in _ALIAS:
        if rx.search(d):
            return list(cats)
    return []


def _teto(linha: str) -> float | None:
    m = re.search(rf"(?:m[aá]xim[oa]|limite|at[eé]|teto|no m[aá]ximo)\s*(?:de\s*)?{_NUM}\s*pontos?", linha, re.I)
    return _num(m.group(1)) if m else None


def _janela(linha: str) -> int | None:
    m = re.search(r"[uú]ltimos?\s+(\d{1,2})\s+anos", linha, re.I)
    return int(m.group(1)) if m else None


def _qualis(linha: str) -> str:
    m = re.search(r"qualis\s*(?:capes\s*)?([ABC][1-4]?)\b|estrato\s+([ABC][1-4]?)\b", linha, re.I)
    return (m.group(1) or m.group(2)).upper() if m else ""


def ler_barema(texto: str, nome: str = "Edital") -> dict[str, Any]:
    """Texto do edital/anexo -> {nome, teto_global, blocos:[{id,nome,teto,janela_anos,itens:[...]}], avisos}."""
    blocos: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None
    teto_global: float | None = None
    avisos: list[str] = []
    for bruta in texto.splitlines():
        linha = re.sub(r"\s+", " ", bruta).strip(" \t|")
        if len(linha) < 4:
            continue
        pontos = re.search(rf"{_NUM}\s*(?:ponto|pt)s?\b", linha, re.I)
        so_teto = _teto(linha)
        mg = re.search(rf"(?:pontua[cç][aã]o|nota|total)\s*(?:m[aá]xim[ao]|total|geral)?[^\d]{{0,25}}{_NUM}\s*pontos?", linha, re.I)
        if mg and re.search(r"(pontua[cç][aã]o|nota|total)\s*(m[aá]xim[ao]|total)|total m[aá]ximo|m[aá]xim[ao] total", linha, re.I) \
                and not re.search(r"\bpor\b|cada", linha, re.I):
            teto_global = _num(mg.group(1))
            continue
        eh_titulo = (not pontos or (so_teto is not None and not re.search(r"\bpor\b|cada|unidade", linha, re.I))) and len(linha) <= 90 and \
            (linha.isupper() or re.match(r"^(\d+(\.\d+)*[.)\-–]?\s*)?(bloco|grupo|crit[eé]rio|categoria|titula[cç][aã]o|produ[cç][aã]o|experi[eê]ncia|atividades?)\b", linha, re.I))
        if eh_titulo:
            atual = {"id": f"b{len(blocos) + 1}", "nome": re.sub(rf"\(?\s*(?:m[aá]xim[oa]|at[eé]).*$", "", linha, flags=re.I).strip(" -–:()") or linha,
                     "teto": so_teto, "janela_anos": _janela(linha), "itens": []}
            blocos.append(atual)
            continue
        if not pontos:
            continue
        if atual is None:
            atual = {"id": "b1", "nome": "Itens", "teto": None, "janela_anos": None, "itens": []}
            blocos.append(atual)
        desc = re.sub(rf"\s*[-–:]?\s*{_NUM}\s*(?:ponto|pt)s?\b.*$", "", linha, flags=re.I).strip(" -–:|.0123456789")
        cats = categorias_de(desc or linha)
        item = {"id": f"{atual['id']}.{len(atual['itens']) + 1}", "descricao": desc or linha, "categorias": cats,
                "pontos_unitarios": _num(pontos.group(1)), "teto": so_teto, "janela_anos": _janela(linha) or atual["janela_anos"],
                "qualis": _qualis(linha), "eliminatorio": bool(re.search(r"eliminat[oó]ri", linha, re.I))}
        if not cats:
            avisos.append(f"Item sem categoria reconhecida (pontuará 0 até você escolher): «{item['descricao'][:80]}».")
        atual["itens"].append(item)
    blocos = [b for b in blocos if b["itens"]]
    if not blocos:
        avisos.append("Nenhuma linha de pontuação encontrada: confira se o texto do barema foi colado inteiro.")
    return {"nome": nome, "teto_global": teto_global, "blocos": blocos, "avisos": avisos}


def _no_periodo(it: dict[str, Any], ano_ref: int, janela: int | None) -> bool:
    if not janela:
        return True
    if not it.get("ano"):
        return False
    return ano_ref - janela < int(it["ano"]) <= ano_ref


def calcular(barema: dict[str, Any], curriculo_itens: list[dict[str, Any]], ano_ref: int | None = None,
             evidencias: dict[str, int] | None = None, qualis_por_issn: dict[str, str] | None = None) -> dict[str, Any]:
    """Pontuação por item/bloco/total.

    evidencias: {categoria: nº de comprovantes disponíveis}. Sem ele, não se afirma nada sobre comprovantes.
    qualis_por_issn: {issn: estrato}. Sem ele, itens que exigem estrato Qualis ficam como pendência (0 ponto).
    """
    ano_ref = ano_ref or datetime.date.today().year
    res_blocos = []
    total = 0.0
    total_sem_comp = 0.0
    for b in barema["blocos"]:
        linhas = []
        soma = soma_sem = 0.0
        for it in b["itens"]:
            pool = [x for x in curriculo_itens if x["categoria"] in it["categorias"] and _no_periodo(x, ano_ref, it["janela_anos"])]
            if it["qualis"]:
                q = {re.sub(r"\D", "", k): v.upper() for k, v in (qualis_por_issn or {}).items()}
                if q:
                    pool = [x for x in pool if q.get(re.sub(r"\D", "", x.get("issn", ""))) == it["qualis"]]
                else:
                    pool = []
            n = len(pool)
            bruto = n * it["pontos_unitarios"]
            teto_item = it["teto"]
            pontos = min(bruto, teto_item) if teto_item is not None else bruto
            comprov_n = n
            if evidencias is not None:
                comprov_n = min(n, sum(evidencias.get(c, 0) for c in it["categorias"]))
            bruto_c = comprov_n * it["pontos_unitarios"]
            pontos_c = min(bruto_c, teto_item) if teto_item is not None else bruto_c
            if it["eliminatorio"] and n == 0:
                status = "desqualificado"
            elif it["qualis"] and not qualis_por_issn:
                status = "pendente_qualis"
            elif n == 0:
                status = "sem_itens"
            elif teto_item is not None and bruto > teto_item:
                status = "excedente_ao_teto"
            elif evidencias is not None and comprov_n < n:
                status = "pontuou_pendente_de_comprovante"
            else:
                status = "pontuou_com_comprovante" if evidencias is not None else "pontuou"
            linhas.append({"id": it["id"], "descricao": it["descricao"], "quantidade": n, "pontos": round(pontos_c if evidencias is not None else pontos, 2),
                           "pontos_sem_comprovante": round(pontos, 2), "teto": teto_item, "status": status,
                           "itens_do_curriculo": [x.get("titulo", "")[:100] for x in pool[:25]]})
            soma += linhas[-1]["pontos"]
            soma_sem += pontos
        tb = b["teto"]
        pb = min(soma, tb) if tb is not None else soma
        pb_sem = min(soma_sem, tb) if tb is not None else soma_sem
        res_blocos.append({"id": b["id"], "nome": b["nome"], "teto": tb, "pontos": round(pb, 2), "pontos_sem_comprovante": round(pb_sem, 2),
                           "excedeu_teto": tb is not None and soma > tb, "itens": linhas})
        total += pb
        total_sem_comp += pb_sem
    tg = barema.get("teto_global")
    final = min(total, tg) if tg is not None else total
    final_sem = min(total_sem_comp, tg) if tg is not None else total_sem_comp
    return {"edital": barema["nome"], "ano_referencia": ano_ref, "total": round(final, 2), "total_sem_comprovante": round(final_sem, 2),
            "teto_global": tg, "excedeu_teto_global": tg is not None and total > tg, "blocos": res_blocos,
            "aviso": "Estimativa para planejamento; a banca é soberana. Itens com exigência de Qualis só pontuam com a base de estratos informada."}


def lacunas(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    """Onde ainda dá para ganhar pontos e onde o teto já foi atingido (não vale a pena submeter mais)."""
    saida = []
    for b in resultado["blocos"]:
        for it in b["itens"]:
            if it["status"] == "excedente_ao_teto" or (it["teto"] is not None and it["pontos_sem_comprovante"] >= it["teto"]):
                saida.append({"item": it["descricao"], "situacao": "teto atingido", "dica": "Mais itens aqui não somam pontos."})
            elif it["teto"] is not None:
                saida.append({"item": it["descricao"], "situacao": "há espaço", "faltam": round(it["teto"] - it["pontos_sem_comprovante"], 2),
                              "dica": f"Faltam {round(it['teto'] - it['pontos_sem_comprovante'], 2)} pontos para o teto do item."})
            if it["status"] == "pontuou_pendente_de_comprovante":
                saida.append({"item": it["descricao"], "situacao": "falta comprovante", "dica": "Anexe os comprovantes dos itens que já estão no currículo."})
            if it["status"] == "pendente_qualis":
                saida.append({"item": it["descricao"], "situacao": "classificar Qualis", "dica": "Informe o estrato Qualis dos periódicos para pontuar."})
    return saida


def simular(barema: dict[str, Any], curriculo_itens: list[dict[str, Any]], extras: list[dict[str, Any]], ano_ref: int | None = None) -> dict[str, Any]:
    """'E se eu adicionar...': extras = [{categoria, ano?, titulo?, issn?}] -> nota antes, depois e diferença."""
    antes = calcular(barema, curriculo_itens, ano_ref)
    ano_ref = ano_ref or datetime.date.today().year
    novos = [{"ano": str(ano_ref), "titulo": "(simulado)", **e} for e in extras]
    depois = calcular(barema, curriculo_itens + novos, ano_ref)
    return {"antes": antes["total"], "depois": depois["total"], "diferenca": round(depois["total"] - antes["total"], 2),
            "teto_global": antes["teto_global"]}


def gerar_dossie(candidato: str, edital: str, anexos: list[dict[str, Any]]) -> bytes:
    """PDF único: folha de rosto, sumário e todos os PDFs com cabeçalho `[Item X] descrição — Página n de N`.

    anexos: [{item, descricao, nome, dados: bytes}] na ordem de entrega. Arquivos que não abrem como PDF são listados
    no sumário como 'não incluído'.
    """
    import pymupdf

    corpo = pymupdf.open()
    sumario: list[tuple[str, str, int, int]] = []  # (item, descricao, pagina_inicial, n)
    for a in anexos:
        try:
            doc = pymupdf.open(stream=a["dados"], filetype="pdf")
        except Exception:
            sumario.append((a["item"], f"{a['descricao']} (arquivo {a['nome']} não incluído: não é PDF legível)", 0, 0))
            continue
        ini = len(corpo)
        corpo.insert_pdf(doc)
        sumario.append((a["item"], a["descricao"], ini + 1, len(doc)))
        doc.close()
    pag_sumario, y_sim = 1, 110
    for _ in sumario:
        y_sim += 16
        if y_sim > 780:
            pag_sumario, y_sim = pag_sumario + 1, 72
    paginas_extras = 1 + pag_sumario  # capa + sumário
    total = len(corpo) + paginas_extras
    for it, desc, ini, n in sumario:
        for p in range(n):
            pg = corpo[ini - 1 + p]
            texto = f"[Item {it}] {desc[:70]} — Página {ini + p + paginas_extras} de {total}"
            pg.insert_text((24, 18), texto, fontsize=8, color=(0.1, 0.1, 0.1))
    saida = pymupdf.open()
    capa = saida.new_page()
    capa.insert_text((72, 200), "Dossiê comprobatório", fontsize=26)
    capa.insert_text((72, 250), f"Candidato(a): {candidato}", fontsize=13)
    capa.insert_text((72, 275), f"Processo seletivo: {edital}", fontsize=13)
    capa.insert_text((72, 300), f"Gerado em {datetime.date.today():%d/%m/%Y} pelo LattesFácil", fontsize=10)
    sm = saida.new_page()
    sm.insert_text((72, 72), "Sumário", fontsize=18)
    y = 110
    for it, desc, ini, n in sumario:
        pag = f"p. {ini + paginas_extras}" if ini else "—"
        sm.insert_text((72, y), f"Item {it}  {desc[:78]}  {pag}", fontsize=9)
        y += 16
        if y > 780:
            sm = saida.new_page()
            y = 72
    saida.insert_pdf(corpo)
    buf = io.BytesIO()
    saida.save(buf)
    return buf.getvalue()
