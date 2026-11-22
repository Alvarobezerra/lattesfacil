"""Verificador e auditor da pasta de currículos em testes.

Inspeciona todos os currículos de candidatos presentes em:
  - tests/curriculos
  - tests/curriculos e modelos/1_INSCRIÇÕES

Verifica integridade dos arquivos PDF, camada de texto, identificador Lattes (ID de 16 dígitos),
data de atualização, contagem de páginas e presença dos documentos complementares.

Uso:
    python tests/verificar_curriculos.py [--detalhes] [--exportar relatorio.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import pymupdf  # PyMuPDF
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

RE_LATTES_URL = re.compile(r"lattes\.cnpq\.br/(\d{16})", re.IGNORECASE)
RE_ATUALIZACAO = re.compile(
    r"(?:Última atualização do currículo em|atualização do currículo em)\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
RE_NOME_CITACAO = re.compile(r"Nome em citações bibliográficas\s*([^\n\r]+)", re.IGNORECASE)


def encontrar_pasta_curriculos() -> Path | None:
    candidatos = [
        Path(__file__).resolve().parent / "curriculos",
        Path(__file__).resolve().parent / "curriculos e modelos" / "1_INSCRIÇÕES",
        Path(__file__).resolve().parent.parent / "tests" / "curriculos",
    ]
    for p in candidatos:
        if p.exists() and p.is_dir():
            return p
    return None


def verificar_candidato(pasta_cand: Path) -> dict:
    nome_pasta = pasta_cand.name
    arquivos = [f.name for f in pasta_cand.iterdir()]
    
    # Arquivo Q13 (Currículo)
    q13_nomes = [f for f in arquivos if f.upper().startswith("Q13") or "LATTES" in f.upper() or "CURRIC" in f.upper()]
    null_files = [f for f in arquivos if f == "null" or (pasta_cand / f).stat().st_size == 0]
    
    res = {
        "candidato": nome_pasta,
        "total_arquivos": len(arquivos),
        "arquivos_nulos": null_files,
        "tem_curriculo": bool(q13_nomes),
        "arquivo_curriculo": q13_nomes[0] if q13_nomes else None,
        "status": "DESCONHECIDO",
        "paginas": 0,
        "tamanho_mb": 0.0,
        "tem_camada_texto": False,
        "id_lattes": None,
        "data_atualizacao": None,
        "nome_citacoes": None,
        "erro": None,
    }

    if not q13_nomes:
        res["status"] = "FALTA_CURRICULO"
        return res

    pdf_path = pasta_cand / q13_nomes[0]
    tamanho = pdf_path.stat().st_size
    res["tamanho_mb"] = round(tamanho / (1024 * 1024), 2)

    if pymupdf is None:
        res["status"] = "SEM_PYMUPDF"
        return res

    try:
        doc = pymupdf.open(str(pdf_path))
        res["paginas"] = len(doc)
        
        # Lê primeiras páginas para extração de metadados
        txt_amostra = ""
        for i in range(min(5, len(doc))):
            txt_amostra += doc[i].get_text("text") + "\n"

        res["tem_camada_texto"] = len(txt_amostra.strip()) > 50

        # Identificador Lattes (16 dígitos)
        m_id = RE_LATTES_URL.search(txt_amostra)
        if m_id:
            res["id_lattes"] = m_id.group(1)

        # Atualização
        m_dt = RE_ATUALIZACAO.search(txt_amostra)
        if m_dt:
            res["data_atualizacao"] = m_dt.group(1)

        # Citações
        m_cit = RE_NOME_CITACAO.search(txt_amostra)
        if m_cit:
            res["nome_citacoes"] = m_cit.group(1).strip()

        # Determina o status
        if res["id_lattes"]:
            res["status"] = "OK_LATTES_VALIDADO"
        elif any(k in txt_amostra.lower() for k in ["lattes", "currículo", "curriculo"]):
            res["status"] = "OK_LATTES_TEXTO"
        elif not res["tem_camada_texto"]:
            res["status"] = "AVISO_SCAN_SEM_TEXTO"
        else:
            res["status"] = "AVISO_FORMATO_NAO_PADRAO"

    except Exception as e:
        res["status"] = "ERRO_LEITURA"
        res["erro"] = str(e)

    return res


def executar_auditoria(diretorio: Path, verbose: bool = False) -> tuple[dict, list[dict]]:
    pastas = sorted([p for p in diretorio.iterdir() if p.is_dir()])
    resultados = [verificar_candidato(p) for p in pastas]

    totais = {
        "diretorio": str(diretorio),
        "total_candidatos": len(pastas),
        "validados_com_id": sum(1 for r in resultados if r["status"] == "OK_LATTES_VALIDADO"),
        "lattes_com_texto": sum(1 for r in resultados if r["status"] == "OK_LATTES_TEXTO"),
        "scans_sem_texto": sum(1 for r in resultados if r["status"] == "AVISO_SCAN_SEM_TEXTO"),
        "formatos_alternativos": sum(1 for r in resultados if r["status"] == "AVISO_FORMATO_NAO_PADRAO"),
        "faltando_curriculo": sum(1 for r in resultados if r["status"] == "FALTA_CURRICULO"),
        "erros_corrompidos": sum(1 for r in resultados if r["status"] == "ERRO_LEITURA"),
        "total_paginas_somadas": sum(r["paginas"] for r in resultados),
        "total_tamanho_mb": round(sum(r["tamanho_mb"] for r in resultados), 2),
        "total_arquivos_nulos": sum(len(r["arquivos_nulos"]) for r in resultados),
    }

    return totais, resultados


def main():
    parser = argparse.ArgumentParser(description="Auditar e verificar pastas de currículos.")
    parser.add_argument("--pasta", type=str, default=None, help="Caminho da pasta de currículos")
    parser.add_argument("--detalhes", action="store_true", help="Exibir listagem completa detalhada")
    parser.add_argument("--exportar", type=str, default=None, help="Caminho para salvar JSON do relatório")
    args = parser.parse_args()

    diretorio = Path(args.pasta) if args.pasta else encontrar_pasta_curriculos()
    if not diretorio or not diretorio.exists():
        print("[FALHA] Nenhuma pasta de currículos encontrada em tests/.")
        sys.exit(1)

    print("=" * 70)
    print(" LATTESFÁCIL — AUDITORIA E VERIFICAÇÃO DE CURRÍCULOS EM TESTES")
    print("=" * 70)
    print(f"Diretório avaliado: {diretorio}")
    
    totais, resultados = executar_auditoria(diretorio, verbose=args.detalhes)

    print(f"\nTotal de candidatos encontrados : {totais['total_candidatos']}")
    print(f"Currículos Lattes digitais (ID)  : {totais['validados_com_id']}")
    print(f"Currículos Lattes (sem ID claro): {totais['lattes_com_texto']}")
    print(f"PDFs escaneados (sem texto OCR) : {totais['scans_sem_texto']}")
    print(f"Formatos alternativos / outros  : {totais['formatos_alternativos']}")
    print(f"Arquivos corrompidos            : {totais['erros_corrompidos']}")
    print(f"Páginas totais processadas      : {totais['total_paginas_somadas']}")
    print(f"Volume de dados em disco        : {totais['total_tamanho_mb']} MB")
    print(f"Arquivos nulos (0 bytes) achados: {totais['total_arquivos_nulos']}")

    if args.detalhes:
        print("\n" + "-" * 70)
        print("LISTAGEM DETALHADA POR CANDIDATO:")
        print("-" * 70)
        for r in resultados:
            id_txt = f"ID: {r['id_lattes']}" if r["id_lattes"] else "Sem ID"
            dt_txt = f"Atualizado: {r['data_atualizacao']}" if r["data_atualizacao"] else ""
            print(f"[{r['status']:<25}] {r['candidato']:<40} | {r['paginas']:>3} págs | {r['tamanho_mb']:>5.1f} MB | {id_txt} {dt_txt}")

    if args.exportar:
        export_path = Path(args.exportar)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump({"totais": totais, "detalhes": resultados}, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Relatório exportado com sucesso para: {export_path}")

    print("\n" + "=" * 70)
    if totais["erros_corrompidos"] == 0:
        print(f"[SUCESSO] Todos os {totais['total_candidatos']} currículos foram abertos e verificados sem corrupção!")
    else:
        print(f"[ALERTA] Encontrados {totais['erros_corrompidos']} arquivos com erro de leitura.")
    print("=" * 70)


if __name__ == "__main__":
    main()
