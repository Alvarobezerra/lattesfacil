"""Regressão da segmentação do Q13: compara as fronteiras que o segmentador acha com a estrutura esperada em tests/gabarito_ocr/segmentacao.json.

Usa o cache de texto por página (tests/curriculos e modelos/_cache_texto_paginas, gerado por ferramentas/ocr_cache_inscricoes.py); não refaz OCR nem grava PDFs.
Uso: python tests/teste_segmentacao.py [prefixo ...]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("separar", RAIZ / "ferramentas" / "separar_evidencias_inscricoes.py")
sep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sep)

arq_gabarito = RAIZ / "tests" / "gabarito_ocr" / "segmentacao.json"
if not arq_gabarito.exists():
    # O gabarito vem de documentos de candidatos reais e fica só na máquina do desenvolvedor (não é versionado).
    print("PULADO: tests/gabarito_ocr/segmentacao.json não existe neste ambiente")
    sys.exit(0)
gab = json.loads(arq_gabarito.read_text(encoding="utf-8"))["candidatos"]
filtro = sys.argv[1:]
falhas = 0
for cand, g in gab.items():
    if filtro and not any(cand.startswith(f) for f in filtro):
        continue
    cache = RAIZ / "tests" / "curriculos e modelos" / "_cache_texto_paginas" / f"{cand}_Q13.json"
    if not cache.exists():
        print(f"PULADO {cand}: sem cache de texto (rode ferramentas/ocr_cache_inscricoes.py)")
        continue
    docs = sep.segmentar(json.loads(cache.read_text(encoding="utf-8"))["paginas"])
    obtido = [(d["ini"] + 1, d["fim"] + 1) for d in docs]
    esperado = [tuple(x) for x in g["docs"]]
    faltam = sorted({a for a, _ in esperado} - {a for a, _ in obtido})
    sobram = sorted({a for a, _ in obtido} - {a for a, _ in esperado})
    ok = obtido == esperado
    falhas += not ok
    sel = "conferido" if g.get("conferido_por_pessoa") else "gabarito a conferir"
    print(f"{'OK  ' if ok else 'FALHA'} {cand}: {len(obtido)} docs (esperados {len(esperado)}; {sel})")
    if not ok:
        print(f"      começos que faltam: {faltam} | começos a mais: {sobram}")
        print(f"      obtido: {obtido}")
print("\nFALHAS:", falhas or "nenhuma")
sys.exit(1 if falhas else 0)
