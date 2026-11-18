"""Rotina: gera os PDFs fictícios de comprovação (tests/amostras_sinteticas/pdf) e confere reconhecimento + leitura.

Uso:
  python tests/teste_amostras_sinteticas.py            # gera e confere tudo
  python tests/teste_amostras_sinteticas.py --so-gerar # apenas (re)gera os PDFs
  python tests/teste_amostras_sinteticas.py banca premio   # só estes itens
  python tests/teste_amostras_sinteticas.py --nome "Seu Nome Completo"   # usa o seu nome em todos os documentos
Regras de criação: docs/regras-documentos-sinteticos.md
Saída: OK / FALHA (quebra o código de saída) / LACUNA (limite conhecido do leitor, marcado no catálogo) / AVISO (item sem regra no classificador) e um resumo de cobertura.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent / "amostras_sinteticas"))

if "--nome" in sys.argv:  # precisa valer antes de importar o catálogo
    _i = sys.argv.index("--nome")
    os.environ["LATTES_NOME"] = sys.argv[_i + 1]
    del sys.argv[_i:_i + 2]

import pymupdf  # noqa: E402

from historico import gravar, nova_execucao, registrar  # noqa: E402
from catalogo import CASOS, INST, NEGATIVOS, PESQUISADORA, nome_em_citacoes  # noqa: E402
from classificador import classificar  # noqa: E402
from extractor import extract_text_from_pdf_bytes  # noqa: E402
from certificado import parse_certificado  # noqa: E402
from itens.leitores import LEITORES, ler  # noqa: E402

# itens que têm leitor próprio fora de itens/leitores.py: item -> função(texto, usuario) -> dict de campos
LEITORES_PROPRIOS = {"apresentacao": lambda texto, usuario: parse_certificado(texto, usuario)}

PASTA = Path(__file__).resolve().parent / "amostras_sinteticas" / "pdf"
MARCA = "DOCUMENTO FICTÍCIO - gerado para testes do LattesFácil - sem valor legal"


def _escrever(caso: dict, destino: Path) -> None:
    doc = pymupdf.open()
    paginas = caso.get("paginas") or [caso["corpo"]]
    for n, corpo in enumerate(paginas):
        pg = doc.new_page(width=595, height=842)
        if caso.get("sem_texto"):  # só desenho: simula um escaneado sem camada de texto
            pg.draw_rect(pymupdf.Rect(80, 120, 500, 400), color=(0.4, 0.4, 0.4), fill=(0.9, 0.9, 0.9))
            continue
        if n == 0 and caso["titulo"]:
            pg.insert_textbox(pymupdf.Rect(60, 60, 535, 130), caso["titulo"], fontsize=16, fontname="hebo", align=1)
        topo = 140 if n == 0 else 60
        pg.insert_textbox(pymupdf.Rect(60, topo, 535, 760), corpo, fontsize=12, fontname="helv", align=0)
        pg.insert_textbox(pymupdf.Rect(60, 790, 535, 830), MARCA, fontsize=8, fontname="helv", align=1, color=(0.5, 0.5, 0.5))
    doc.set_metadata({"title": caso["titulo"] or caso["arquivo"], "author": "Gerador de amostras sintéticas", "subject": MARCA})
    doc.save(destino)
    doc.close()


def _tem_nome(texto: str) -> bool:
    """O nome completo (ou a forma de citação) precisa estar no texto extraído do PDF."""
    t = " ".join(texto.split()).lower()
    return PESQUISADORA.lower() in t or nome_em_citacoes(PESQUISADORA).lower() in t


def _caderno() -> dict:
    """Caderno de anais: >12 páginas e ≥10 resumos com 'Palavras-chave' (reconhecido como caderno)."""
    paginas = []
    for i in range(1, 15):
        paginas.append(f"Trabalho {i}: Estudo exemplar número {i}\n{PESQUISADORA}, Autores fictícios da {INST}\n\n"
                       f"Resumo: texto fictício do resumo {i} com introdução, metodologia e resultados.\n"
                       f"Palavras-chave: exemplo; fictício; trabalho {i}.\nKeywords: example; fictitious; work {i}.")
    return dict(arquivo="caderno", item="caderno", classe="caderno", titulo="CADERNO DE RESUMOS - Simpósio Exemplar 2024",
                corpo="", paginas=paginas)


def todos_os_casos() -> list[dict]:
    return CASOS + [_caderno()] + NEGATIVOS


def cobertura() -> tuple[list[str], list[str]]:
    """(itens da especificação sem documento, ids do catálogo que não existem na especificação)."""
    specs = {p.stem for p in (RAIZ / "itens" / "especificacao").glob("*.json")}
    itens_catalogo = {c["item"] for c in CASOS}
    return sorted(specs - itens_catalogo), sorted(i for i in itens_catalogo if i not in specs and i not in ("anais", "apresentacao", "artigo", "orientacao_concluida", "orientacao_andamento"))


def main(argv: list[str]) -> int:
    so_gerar = "--so-gerar" in argv
    filtro = [a for a in argv if not a.startswith("--")]
    PASTA.mkdir(parents=True, exist_ok=True)
    casos = [c for c in todos_os_casos() if not filtro or c["arquivo"] in filtro or c["item"] in filtro]
    falhas = avisos = ok = lacunas = 0
    exe = nova_execucao("teste_amostras_sinteticas")
    for c in casos:
        destino = PASTA / f"{c['arquivo']}.pdf"
        _escrever(c, destino)
        if so_gerar:
            continue
        info = extract_text_from_pdf_bytes(destino.read_bytes())
        resumos = info["text"].lower().count("palavras-chave:")
        cls = classificar(info["text"], "", info["page_count"], resumos)
        top = cls["candidatos"][0]["id"] if cls["candidatos"] else "nenhum"
        problemas = []
        if c["item"] and not _tem_nome(info["text"]):
            problemas.append(f"o nome do pesquisador ({PESQUISADORA}) não aparece no documento")
        if c["classe"] == "escolher":
            if cls["decisao"] != "escolher":
                problemas.append(f"deveria recusar, mas classificou como {top} ({cls['decisao']})")
        elif c["classe"]:
            if top != c["classe"] or cls["decisao"] == "escolher":
                problemas.append(f"classificou como {top} ({cls['decisao']}), esperado {c['classe']}")
        if c.get("campos"):
            if c["item"] in LEITORES_PROPRIOS:
                v = LEITORES_PROPRIOS[c["item"]](info["text"], PESQUISADORA)
                for campo, trecho in c["campos"].items():
                    if trecho.lower() not in str(v.get(campo, "")).lower():
                        problemas.append(f"{campo}={str(v.get(campo))[:80]!r}, esperado conter {trecho!r}")
            elif c["item"] not in LEITORES:
                problemas.append("catálogo espera campos, mas o item não tem leitor")
            else:
                r = ler(c["item"], info["text"], PESQUISADORA)
                v = (r or {}).get("valores", {})
                for campo, trecho in c["campos"].items():
                    if trecho.lower() not in str(v.get(campo, "")).lower():
                        problemas.append(f"{campo}={v.get(campo)!r}, esperado conter {trecho!r}")
        _res = ("lacuna" if problemas and c.get("lacuna") else "falha" if problemas else "aviso" if c["classe"] is None else "ok")
        if c["item"]:
            registrar(exe, c["item"], "modulos", _res, "; ".join(problemas) or (f"sem regra no classificador ({top}/{cls['decisao']})" if _res == "aviso" else ""),
                      c["arquivo"], [PESQUISADORA])
        if problemas and c.get("lacuna"):
            lacunas += 1
            print(f"LACUNA {c['arquivo']}: {'; '.join(problemas)}  [conhecida: {c['lacuna']}]")
        elif c.get("lacuna") and not problemas:
            print(f"RESOLVIDA {c['arquivo']}: a lacuna conhecida deixou de existir - remova a marca 'lacuna' do catálogo")
            ok += 1
        elif problemas:
            falhas += 1
            print(f"FALHA  {c['arquivo']}: " + "; ".join(problemas))
        elif c["classe"] is None:
            avisos += 1
            print(f"AVISO  {c['arquivo']}: item ainda sem regra no classificador (classificou como {top}/{cls['decisao']})")
        else:
            ok += 1
            print(f"OK     {c['arquivo']}")
    if so_gerar:
        print(f"{len(casos)} PDFs gerados em {PASTA}")
        return 0
    if not filtro:
        gravar(exe)
    sem_doc, desconhecidos = cobertura()
    print(f"\nOK {ok} | LACUNA {lacunas} | AVISO {avisos} | FALHA {falhas} | total {len(casos)}")
    print(f"Itens da especificação sem documento: {sem_doc or 'nenhum'}")
    if desconhecidos:
        print(f"Ids do catálogo que não existem na especificação: {desconhecidos}")
        falhas += 1
    if sem_doc and not filtro:
        falhas += 1
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
