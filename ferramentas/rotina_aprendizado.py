"""Rotina de aprendizado: mede reconhecimento e preenchimento de evidências e registra tudo em planilha.

Uso:
    python ferramentas/rotina_aprendizado.py --lista lista.csv --pasta <pasta dos arquivos>
    python ferramentas/rotina_aprendizado.py --pasta <pasta>            # sem gabarito: só registra o que foi lido
    python ferramentas/rotina_aprendizado.py --lista lista.csv --pasta <pasta> --sem-cache

Lista (CSV com cabeçalho; separador , ou ;): arquivo, item_esperado [, grupo]
  - arquivo: caminho relativo à --pasta (ou só o nome, se a pasta for plana)
  - item_esperado: id do classificador (ex.: participacao_evento); vazio = sem gabarito
  - grupo: "treino" (padrão) ou "validacao" (conjunto que NÃO deve guiar a criação de regras)

Teste 1 — reconhecimento: sucesso quando o sistema escolhe UM item (decisão "avancar") e ele é o esperado.
  Dois ou mais candidatos plausíveis = AMBIGUO (precisa de análise e ajuste de código).
Teste 2 — preenchimento: sucesso = nenhum obrigatório faltando e ao menos 3 campos extraídos; a cobertura % é só informativa.
  Valores iguais ao padrão do formulário não contam como extraídos.

O Gemini fica DESLIGADO (resultado determinístico). Saída em ferramentas/saida/aprendizado/ (ignorada pelo git):
  aprendizado.xlsx (abas Resumo, Resultados, Regressoes), historico.jsonl, cache_texto.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

os.environ["GEMINI_ENABLED"] = "0"
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from classificador import INDICE, classificar  # noqa: E402
from extractor import extract_text_from_image_bytes, extract_text_from_pdf_bytes  # noqa: E402
from itens import especificacao  # noqa: E402
from itens.leitores import LEITORES, ler  # noqa: E402

SAIDA = RAIZ / "ferramentas" / "saida" / "aprendizado"
EXT_IMG = (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".jfif")
EXT_OK = (".pdf", ".txt", ".eml") + EXT_IMG
MIN_EXTRAIDOS = 3  # campos do documento que precisam ter sido extraídos (além de nenhum obrigatório faltando)
MAX_PAGINAS_SINGLE = 12
MIN_RESUMOS_CADERNO = 10


# ---------------------------------------------------------------- leitura do texto (com cache)
def _assinatura(p: Path) -> str:
    st = p.stat()
    codigo = (RAIZ / "extractor.py").stat().st_mtime  # mudou o OCR/extração: o cache perde a validade
    return hashlib.md5(f"{p}|{st.st_size}|{st.st_mtime}|{codigo}".encode()).hexdigest()


def ler_texto(p: Path) -> dict:
    nome = p.name.lower()
    dados = p.read_bytes()
    if nome.endswith(".pdf"):
        info = extract_text_from_pdf_bytes(dados)
        texto, paginas = info["text"], info["page_count"]
    elif nome.endswith(EXT_IMG):
        texto, paginas = extract_text_from_image_bytes(dados, p.name)["text"], 1
    elif nome.endswith(".eml"):
        from email_parser import parse_eml_bytes
        eml = parse_eml_bytes(dados)
        if eml.get("first_pdf"):
            info = extract_text_from_pdf_bytes(eml["first_pdf"]["data"])
            texto, paginas = info["text"], info["page_count"]
        elif eml.get("first_image"):
            texto, paginas = extract_text_from_image_bytes(eml["first_image"]["data"], "")["text"], 1
        else:
            texto, paginas = f"{eml.get('subject', '')}\n\n{eml.get('body', '')}".strip(), 0
    else:
        texto, paginas = dados.decode("utf-8", errors="replace"), 0
    n_kw = len(re.findall(r"keywords?\s*:|palavras[- ]chave\s*:", texto, re.I))
    return {"texto": texto, "paginas": paginas, "n_kw": n_kw}


def texto_do_arquivo(p: Path, cache: dict, usar_cache: bool) -> dict:
    chave = _assinatura(p)
    if usar_cache and chave in cache:
        return cache[chave]
    try:
        r = ler_texto(p)
    except Exception as exc:  # arquivo corrompido não pode derrubar a rotina
        r = {"texto": "", "paginas": 0, "n_kw": 0, "erro": f"{type(exc).__name__}: {exc}"[:200]}
    cache[chave] = r
    return r


# ---------------------------------------------------------------- teste 1: reconhecimento
def reconhecer(lido: dict, nome: str) -> dict:
    texto, paginas, n_kw = lido["texto"], lido["paginas"], lido["n_kw"]
    if paginas > MAX_PAGINAS_SINGLE and n_kw >= MIN_RESUMOS_CADERNO:
        return {"tipo": "caderno", "ids": ["caderno"], "cands": "caderno de anais", "decisao": "caderno", "motivos": ""}
    cls = classificar(texto, nome, paginas, n_kw)
    cands = cls.get("candidatos", [])
    if not texto.strip() or cls["motivo_decisao"].startswith("não consegui ler"):
        tipo = "nao_lido"
    elif not cands:
        tipo = "nenhum"
    elif cls["decisao"] == "avancar":
        tipo = "unico"
    elif len(cands) == 1:
        tipo = "fraco"  # só um candidato, mas sem confiança para avançar sozinho
    else:
        tipo = "ambiguo"
    return {"tipo": tipo, "ids": [c["id"] for c in cands], "decisao": cls["decisao"],
            "cands": "; ".join(f"{c['id']} ({c['confianca']})" for c in cands),
            "motivos": " | ".join(cands[0]["motivos"]) if cands else ""}


def status_reconhecimento(rec: dict, esperado: str) -> str:
    t = rec["tipo"]
    if t in ("nao_lido", "nenhum", "caderno"):
        return {"nao_lido": "NAO_LIDO", "nenhum": "NAO_RECONHECIDO", "caderno": "CADERNO"}[t]
    if not esperado:
        return "SEM_GABARITO_" + ("UNICO" if t == "unico" else t.upper())
    if t == "unico":
        return "OK" if rec["ids"][0] == esperado else "ERRADO"
    if t == "fraco":
        return "FRACO_CERTO" if rec["ids"][0] == esperado else "FRACO_ERRADO"
    return "AMBIGUO_COM_ESPERADO" if esperado in rec["ids"] else "AMBIGUO_SEM_ESPERADO"


# ---------------------------------------------------------------- teste 2: preenchimento
def campos_alvo(item_id: str, variante: str) -> list[dict]:
    spec = especificacao(item_id) or {}
    var = next((v for v in spec.get("variantes", []) if v["variante"] == variante), None)
    if not var:
        return []
    preenchiveis = [c for c in var["campos"] if not c.get("automatico") and c.get("tipo") in {"text", "textarea", "select", "radio"}]
    doc = [c for c in preenchiveis if c.get("origem") == "documento"]
    # specs sem "origem" marcada: usa os campos do formulário que não são fixos
    return doc or [c for c in preenchiveis if c.get("origem") != "fixo"]


def preencher(item_id: str, texto: str) -> dict:
    if not item_id or item_id not in LEITORES or not especificacao(item_id):
        return {"item": item_id, "avaliado": False}
    try:
        g = ler(item_id, texto, "")
    except Exception as exc:
        return {"item": item_id, "avaliado": False, "erro": f"{type(exc).__name__}: {exc}"[:200]}
    if not g:
        return {"item": item_id, "avaliado": False}
    alvo = campos_alvo(item_id, g["variante"])
    valores = g["valores"]
    extraidos, vazios = [], []
    for c in alvo:
        v = valores.get(c["name"])
        padrao = c.get("padrao")
        if v not in ("", None) and str(v) != str(padrao or ""):
            extraidos.append(c)
        else:
            vazios.append(c)
    total = len(alvo)
    cobertura = (len(extraidos) / total) if total else 1.0
    nomes_alvo = {c["name"] for c in alvo}
    extras = [k for k in valores if k.startswith("grade:") and valores[k]]
    return {
        "item": item_id, "avaliado": True, "variante": g["variante"], "total": total, "n_extraidos": len(extraidos),
        "cobertura": round(cobertura, 2), "faltam_obrigatorios": g.get("faltam_obrigatorios", []),
        "vazios": [c["rotulo"] for c in vazios],
        "campos": [f"{c['rotulo']} = {str(valores[c['name']])[:120]}" for c in extraidos]
                  + [f"{k} = {len(valores[k])} linha(s)" if isinstance(valores[k], list) else f"{k} = {str(valores[k])[:80]}" for k in extras],
        "notas": g.get("notas", []), "fora_alvo": [k for k in valores if k not in nomes_alvo and not k.startswith("grade:") and valores[k] and not k.startswith("__")][:10],
    }


def status_preenchimento(p: dict) -> str:
    if not p.get("avaliado"):
        return "NAO_AVALIADO"
    if p["faltam_obrigatorios"]:
        return "FALTA_OBRIGATORIO"
    # a cobertura % é informativa (o formulário tem campos que nenhum documento traz); o sucesso exige obrigatórios + mínimo extraído
    return "OK" if p["n_extraidos"] >= MIN_EXTRAIDOS else "BAIXA_COBERTURA"


# ---------------------------------------------------------------- lista e execução
def carregar_lista(caminho: Path | None, pasta: Path) -> list[dict]:
    itens: list[dict] = []
    if caminho:
        amostra = caminho.read_text(encoding="utf-8-sig")
        cab = amostra.split("\n", 1)[0]
        sep = ";" if cab.count(";") > cab.count(",") else ","
        for r in csv.DictReader(amostra.splitlines(), delimiter=sep):
            r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
            if r.get("arquivo"):
                itens.append({"arquivo": r["arquivo"], "esperado": r.get("item_esperado", ""),
                              "grupo": (r.get("grupo") or "treino").lower()})
    else:
        for p in sorted(pasta.rglob("*")):
            if p.suffix.lower() in EXT_OK and p.is_file():
                itens.append({"arquivo": str(p.relative_to(pasta)), "esperado": "", "grupo": "treino"})
    return itens


def executar(lista: list[dict], pasta: Path, usar_cache: bool, rodada: int) -> list[dict]:
    cache_p = SAIDA / "cache_texto.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    linhas = []
    for i, it in enumerate(lista, 1):
        p = (pasta / it["arquivo"])
        base = {"rodada": rodada, "execucao": datetime.now().isoformat(timespec="seconds"), "arquivo": it["arquivo"],
                "grupo": it["grupo"], "item_esperado": it["esperado"]}
        if it["esperado"] and it["esperado"] not in INDICE:
            base["aviso"] = f"item_esperado '{it['esperado']}' não existe no classificador"
        if not p.is_file():
            linhas.append({**base, "status_reconhecimento": "ARQUIVO_NAO_ENCONTRADO", "status_preenchimento": "NAO_AVALIADO"})
            continue
        lido = texto_do_arquivo(p, cache, usar_cache)
        rec = reconhecer(lido, p.name)
        st_rec = status_reconhecimento(rec, it["esperado"])
        # preenche o item esperado quando há gabarito (mede o leitor mesmo que o classificador tenha falhado); senão o reconhecido
        alvo = it["esperado"] or (rec["ids"][0] if rec["tipo"] == "unico" else "")
        pre = preencher(alvo, lido["texto"])
        linhas.append({**base, "paginas": lido["paginas"], "caracteres": len(lido["texto"]),
                       "item_reconhecido": rec["ids"][0] if rec["tipo"] in ("unico", "fraco") else "",
                       "candidatos": rec["cands"], "decisao": rec["decisao"], "motivos_top": rec["motivos"],
                       "status_reconhecimento": st_rec,
                       "item_preenchido": pre.get("item", ""), "variante": pre.get("variante", ""),
                       "cobertura": pre.get("cobertura", ""), "campos_extraidos_n": pre.get("n_extraidos", ""),
                       "campos_total": pre.get("total", ""),
                       "status_preenchimento": status_preenchimento(pre),
                       "obrigatorios_faltando": "; ".join(pre.get("faltam_obrigatorios", [])),
                       "campos_vazios": "; ".join(pre.get("vazios", [])),
                       "campos_extraidos": "\n".join(pre.get("campos", [])),
                       "observacoes": " | ".join(filter(None, [base.get("aviso", ""), lido.get("erro", ""), pre.get("erro", "")] + pre.get("notas", [])))[:800],
                       "trecho_texto": re.sub(r"\s+", " ", lido["texto"])[:400]})
        if i % 10 == 0:  # não perde o OCR já feito se a rotina for interrompida
            SAIDA.mkdir(parents=True, exist_ok=True)
            cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print(f"[{i}/{len(lista)}] {it['arquivo'][:50]:50} {st_rec:22} {linhas[-1]['status_preenchimento']}", flush=True)
    SAIDA.mkdir(parents=True, exist_ok=True)
    cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return linhas


# ---------------------------------------------------------------- histórico, resumo e planilha
def proxima_rodada(hist: Path) -> int:
    if not hist.exists():
        return 1
    rods = [json.loads(l)["rodada"] for l in hist.read_text(encoding="utf-8").splitlines() if l.strip()]
    return (max(rods) + 1) if rods else 1


def resumir(linhas: list[dict]) -> dict:
    com_gab = [l for l in linhas if l.get("item_esperado")]
    ok = [l for l in com_gab if l["status_reconhecimento"] == "OK"]
    aval = [l for l in linhas if l.get("status_preenchimento") not in (None, "NAO_AVALIADO")]
    cob = [l["cobertura"] for l in aval if isinstance(l.get("cobertura"), float)]
    return {"arquivos": len(linhas), "com_gabarito": len(com_gab), "reconhecimento_ok": len(ok),
            "reconhecimento_pct": round(100 * len(ok) / len(com_gab), 1) if com_gab else None,
            "ambiguos": sum(1 for l in linhas if l["status_reconhecimento"].startswith("AMBIGUO") or l["status_reconhecimento"].endswith("AMBIGUO")),
            "errados": sum(1 for l in com_gab if l["status_reconhecimento"] in ("ERRADO", "FRACO_ERRADO")),
            "nao_lidos": sum(1 for l in linhas if l["status_reconhecimento"] in ("NAO_LIDO", "NAO_RECONHECIDO")),
            "preenchimento_avaliados": len(aval),
            "preenchimento_ok": sum(1 for l in aval if l["status_preenchimento"] == "OK"),
            "cobertura_media": round(sum(cob) / len(cob), 2) if cob else None}


def regressoes(atual: list[dict], anterior: list[dict]) -> list[dict]:
    ant = {l["arquivo"]: l for l in anterior}
    out = []
    for l in atual:
        a = ant.get(l["arquivo"])
        if not a:
            continue
        for campo, bom in (("status_reconhecimento", "OK"), ("status_preenchimento", "OK")):
            if a.get(campo) == bom and l.get(campo) != bom:
                out.append({"rodada": l["rodada"], "arquivo": l["arquivo"], "teste": campo, "antes": a[campo], "agora": l.get(campo)})
    return out


COLUNAS = ["rodada", "execucao", "arquivo", "grupo", "item_esperado", "item_reconhecido", "status_reconhecimento", "decisao",
           "candidatos", "motivos_top", "item_preenchido", "variante", "status_preenchimento", "cobertura", "campos_extraidos_n",
           "campos_total", "obrigatorios_faltando", "campos_extraidos", "campos_vazios", "observacoes", "paginas", "caracteres", "trecho_texto"]


def gerar_planilha(hist: Path, destino: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    todas = [json.loads(l) for l in hist.read_text(encoding="utf-8").splitlines() if l.strip()]
    por_rodada: dict[int, list[dict]] = defaultdict(list)
    for l in todas:
        por_rodada[l["rodada"]].append(l)
    rods = sorted(por_rodada)
    wb = Workbook()

    ws = wb.active
    ws.title = "Resumo"
    cab = ["rodada", "arquivos", "com_gabarito", "reconhecimento_ok", "reconhecimento_pct", "ambiguos", "errados", "nao_lidos",
           "preenchimento_avaliados", "preenchimento_ok", "cobertura_media", "regressoes"]
    ws.append(cab)
    reg_todas: list[dict] = []
    for k, r in enumerate(rods):
        reg = regressoes(por_rodada[r], por_rodada[rods[k - 1]]) if k else []
        reg_todas += reg
        s = resumir(por_rodada[r])
        ws.append([r] + [s[c] for c in cab[1:-1]] + [len(reg)])

    wr = wb.create_sheet("Resultados")
    wr.append(COLUNAS)
    verde, amarelo, vermelho = (PatternFill("solid", fgColor=c) for c in ("C6EFCE", "FFEB9C", "FFC7CE"))
    for l in sorted(todas, key=lambda x: (-x["rodada"], x["arquivo"])):
        wr.append([l.get(c, "") for c in COLUNAS])
        for nome in ("status_reconhecimento", "status_preenchimento"):
            cel = wr.cell(row=wr.max_row, column=COLUNAS.index(nome) + 1)
            v = str(cel.value)
            cel.fill = verde if v == "OK" else amarelo if v.startswith(("AMBIGUO", "FRACO", "SEM_GABARITO", "BAIXA", "NAO_AVALIADO")) else vermelho
    larg = {"arquivo": 42, "candidatos": 45, "motivos_top": 40, "campos_extraidos": 60, "campos_vazios": 40, "observacoes": 50, "trecho_texto": 60, "obrigatorios_faltando": 30}
    for i, c in enumerate(COLUNAS, 1):
        wr.column_dimensions[get_column_letter(i)].width = larg.get(c, 16)
    for row in wr.iter_rows(min_row=2):
        for cel in row:
            cel.alignment = Alignment(wrap_text=True, vertical="top")

    wg = wb.create_sheet("Regressoes")
    wg.append(["rodada", "arquivo", "teste", "antes", "agora"])
    for g in reg_todas:
        wg.append([g[k] for k in ("rodada", "arquivo", "teste", "antes", "agora")])

    for w in (ws, wr, wg):
        w.freeze_panes = "A2"
        for cel in w[1]:
            cel.font = Font(bold=True)
    for i in range(1, len(cab) + 1):
        ws.column_dimensions[get_column_letter(i)].width = 22
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        wb.save(destino)
    except PermissionError:  # planilha aberta no Excel
        alt = destino.with_name(destino.stem + f"_{datetime.now():%H%M%S}.xlsx")
        wb.save(alt)
        print(f"AVISO: {destino.name} está aberta; salvei em {alt.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lista", type=Path, help="CSV: arquivo,item_esperado[,grupo]")
    ap.add_argument("--pasta", type=Path, required=True, help="pasta base dos arquivos")
    ap.add_argument("--sem-cache", action="store_true", help="relê PDFs/imagens (OCR) em vez de usar o texto em cache")
    ap.add_argument("--rodada", type=int, help="número da rodada (padrão: próxima)")
    a = ap.parse_args()
    pasta = a.pasta.resolve()
    lista = carregar_lista(a.lista, pasta)
    if not lista:
        print("Nenhum arquivo para processar.")
        return 1
    SAIDA.mkdir(parents=True, exist_ok=True)
    hist = SAIDA / "historico.jsonl"
    rodada = a.rodada or proxima_rodada(hist)
    linhas = executar(lista, pasta, not a.sem_cache, rodada)
    with hist.open("a", encoding="utf-8") as f:
        for l in linhas:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    gerar_planilha(hist, SAIDA / "aprendizado.xlsx")
    s = resumir(linhas)
    print(f"\n=== Rodada {rodada} ===")
    for k, v in s.items():
        print(f"{k}: {v}")
    ruins = [l for l in linhas if l["status_reconhecimento"] not in ("OK",) and l.get("item_esperado")]
    if ruins:
        print("\nPara analisar (reconhecimento):")
        for l in ruins:
            print(f"  {l['arquivo']}: {l['status_reconhecimento']} esperado={l['item_esperado']} candidatos={l.get('candidatos', '')}")
    print(f"\nPlanilha: {SAIDA / 'aprendizado.xlsx'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
