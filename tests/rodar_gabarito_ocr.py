"""Roda o pipeline (OCR -> classificador -> leitor) nos documentos separados de um candidato e compara com o gabarito.

Uso: python tests/rodar_gabarito_ocr.py 25331 [--grava]
Gabarito: tests/gabarito_ocr/<candidato>.json (item_esperado e campos que o documento afirma).
Documentos: tests/curriculos e modelos/2_EVIDENCIAS_SEPARADAS/<pasta do candidato>/ (ferramentas/separar_evidencias_inscricoes.py).
Falha atribuída ao 1º estágio que errou: item (E2) ou campo (E3). --grava acrescenta o resultado em tests/historico/execucoes.jsonl.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

os.environ.setdefault("LATTESFACIL_SKIP_WARMUP", "1")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import server  # noqa: E402

SEPARADAS = RAIZ / "tests" / "curriculos e modelos" / "2_EVIDENCIAS_SEPARADAS"


def n(t) -> str:
    return " ".join(unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower().split())


def _confere(esperado, obtido) -> bool:
    """Esperado contido no obtido, ignorando acentos, caixa, espaços e pontuação (OCR perde espaços); aceita 1–2 letras trocadas pelo OCR
    em valores longos (>= 25 caracteres)."""
    import difflib
    k = lambda t: "".join(c for c in n(t) if c.isalnum())  # noqa: E731
    e, o = k(esperado), k(obtido)
    if e in o:
        return True
    if len(e) < 25:
        return False
    return difflib.SequenceMatcher(None, e, o[:len(e) + 6], autojunk=False).ratio() >= 0.93 or \
        max((difflib.SequenceMatcher(None, e, o[i:i + len(e)], autojunk=False).ratio() for i in range(0, max(1, len(o) - len(e) + 1), 4)), default=0) >= 0.93


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    gab_path = next((p for p in (RAIZ / "tests" / "gabarito_ocr").glob("*.json") if p.name.startswith(args[0])), None)
    if not gab_path:
        print("sem gabarito para", args[0])
        return 2
    gab = json.loads(gab_path.read_text(encoding="utf-8"))
    pasta = SEPARADAS.parent / gab.get("pasta", SEPARADAS.name) / gab["candidato"]  # "pasta": estrutura conferida em vez da do segmentador
    ok_item = ok_campo = tot_item = tot_campo = 0
    linhas = []
    agora = datetime.now().isoformat(timespec="seconds")
    for caso in gab["casos"]:
        esperado = caso["item_esperado"]
        if esperado in ("__cv__", "__ficha__", "a_definir"):
            print(f"{caso['arquivo'][:34]:34} -- {esperado}: {caso.get('observacao', '')[:70]}")
            continue
        alvo = pasta / caso["arquivo"]
        if not alvo.exists():  # o tipo no nome ("documento"/"certificado") pode mudar com o segmentador; vale o intervalo de páginas (pNNN-pNNN)
            achados = sorted(pasta.glob("*_" + re.search(r"(p\d{3}(?:-p\d{3})?)\.pdf$", caso["arquivo"]).group(1) + ".pdf"))
            alvo = achados[0] if achados else alvo
        r = server.process_extract(alvo.name, alvo.read_bytes(), gab["pessoa"])
        c = r.get("classificacao", {})
        top = (c.get("candidatos") or [{}])[0].get("id")
        item = r.get("item_escolhido") or top
        vals = (r.get("generico") or {}).get("valores") or {}
        if not r.get("item_escolhido") and esperado in [x.get("id") for x in c.get("candidatos", [])]:
            # a tela pede confirmação: simula o clique do usuário no item esperado (o mesmo caminho de /api/classificacao/interpretar)
            feito = server.interpretar(esperado, r.get("_leitura", {}).get("texto", ""), caso["arquivo"], gab["pessoa"]) or {}
            vals = (feito.get("generico") or {}).get("valores") or {}
            item = esperado
        acertou_item = item == esperado
        tot_item += 1
        ok_item += acertou_item
        falhas = []
        for campo, valor in (caso.get("campos") or {}).items():
            tot_campo += 1
            if _confere(valor, vals.get(campo, "")):
                ok_campo += 1
            else:
                falhas.append(f"{campo}: esperado '{valor}' / veio '{str(vals.get(campo, ''))[:60]}'")
        for campo in caso.get("deve_ficar_vazio") or []:
            tot_campo += 1
            if not str(vals.get(campo, "")).strip():
                ok_campo += 1
            else:
                falhas.append(f"{campo}: deveria ficar vazio / veio '{str(vals.get(campo))[:60]}'")
        estado = "OK  " if acertou_item and not falhas else ("E2  " if not acertou_item else "E3  ")
        print(f"{estado}{caso['arquivo'][:30]:30} item={item} (esp. {esperado}) {c.get('decisao')}")
        for f in falhas:
            print("      ", f)
        linhas.append({"execucao": agora, "origem": "rodar_gabarito_ocr", "item": esperado, "etapa": "ocr_item",
                       "resultado": "ok" if acertou_item else "falha", "detalhe": "" if acertou_item else f"veio {item}",
                       "arquivo": caso["arquivo"]})
        if caso.get("campos"):
            linhas.append({"execucao": agora, "origem": "rodar_gabarito_ocr", "item": esperado, "etapa": "ocr_campos",
                           "resultado": "ok" if not falhas else "falha", "detalhe": "; ".join(falhas)[:300], "arquivo": caso["arquivo"]})
    print(f"\nItem certo: {ok_item}/{tot_item} | campos certos: {ok_campo}/{tot_campo}"
          + ("" if gab.get("conferido_por_pessoa") else "  (gabarito ainda NÃO conferido por pessoa)"))
    if "--grava" in sys.argv:
        with open(RAIZ / "tests" / "historico" / "execucoes.jsonl", "a", encoding="utf-8") as fh:
            for ln in linhas:
                fh.write(json.dumps(ln, ensure_ascii=False) + "\n")
    return 0 if ok_item == tot_item and ok_campo == tot_campo else 1


if __name__ == "__main__":
    sys.exit(main())
