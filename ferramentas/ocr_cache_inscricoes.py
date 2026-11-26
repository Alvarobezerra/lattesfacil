"""Extrai texto por página (nativo; OCR via rapidocr quando a página é imagem) e grava cache JSON.
Uso: python ferramentas/ocr_cache_inscricoes.py [workers]
"""
import glob, json, os, sys, re
from multiprocessing import Pool
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'curriculos e modelos', '1_INSCRIÇÕES')
CACHE = os.path.join(RAIZ, '..', '_cache_texto_paginas')
_ocr = None

def alvos():
    fs = sorted(glob.glob(os.path.join(RAIZ, '*', 'Q13*.pdf')) + glob.glob(os.path.join(RAIZ, '25664*', 'Q12_Hist*ACAD*.pdf')))
    return fs

def tarefa(f):
    global _ocr
    import pymupdf
    cand = os.path.basename(os.path.dirname(f))[:5]
    out = os.path.join(CACHE, f'{cand}_{os.path.basename(f)[:3]}.json')
    if os.path.exists(out): return out
    doc = pymupdf.open(f); pgs = []
    for p in doc:
        t = p.get_text() or ''
        ocr = False
        nativo = t
        # PDF gráfico (TCPDF/Even3/Canva): fundo em imagem e só uma linha vetorial (nome, rodapé). OCR também nesses casos.
        if len(t.strip()) < 30 or (len(t.strip()) < 200 and p.get_images()):
            try:
                if _ocr is None:
                    from rapidocr_onnxruntime import RapidOCR
                    _ocr = RapidOCR()
                pix = p.get_pixmap(dpi=90)
                r, _ = _ocr(pix.tobytes('png'))
                t = '\n'.join(x[1] for x in (r or [])); ocr = True
                if nativo.strip():
                    t = t + '\n' + nativo  # texto vetorial tem os acentos exatos; OCR traz o corpo
            except Exception as e:
                t = ''
        fonts = sorted({x[3] for x in p.get_fonts()})
        pgs.append(dict(w=round(p.rect.width), h=round(p.rect.height), t=t, ocr=ocr, nimg=len(p.get_images()), fonts=fonts))
    os.makedirs(CACHE, exist_ok=True)
    json.dump(dict(arquivo=f, paginas=pgs), open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('ok', out, len(pgs), flush=True)
    return out

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    with Pool(n) as p:
        list(p.imap_unordered(tarefa, alvos()))
