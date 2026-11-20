"""Análise consolidada dos currículos de referência em lotes de 10 por ciclo.

Lê os arquivos disponíveis em 'Lattes para referencia/' e cruza com os coautores
mapeados no banco de dados para gerar a métrica de cobertura e prioridades do lote.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
import pypdf

RAIZ = Path(__file__).resolve().parent.parent
DIR_REFS = RAIZ / "Lattes para referencia"

CICLO_1_ALVOS = [
    {"num": 1, "nome": "Richard Pereira Dutra", "arquivo": "Richard.pdf", "id_lattes": "3540029577221469", "area": "Farmácia / Fitoquímica", "ufma": True},
    {"num": 2, "nome": "Márcia Cristina Gonçalves Maciel", "arquivo": "Marcia.pdf", "id_lattes": "0645092224285117", "area": "Imunologia / Saúde", "ufma": True},
    {"num": 3, "nome": "Adriana Gomes Nogueira Ferreira", "arquivo": "Adriana Gomes.pdf", "id_lattes": "4245835067415813", "area": "Saúde / Biotecnologia", "ufma": True},
    {"num": 4, "nome": "Marcelino Santos Neto", "arquivo": "Marcelino Santos Neto.pdf", "id_lattes": "", "area": "Enfermagem / Saúde Coletiva", "ufma": True},
    {"num": 5, "nome": "Ana Lúcia Fernandes Pereira", "arquivo": "Ana Lucia.pdf", "id_lattes": "7841826430721579", "area": "Tecnologia de Alimentos / PPGST", "ufma": True},
    {"num": 6, "nome": "Valério Monteiro-Neto", "arquivo": "Valerio Monteiro.pdf", "id_lattes": "5476942147520772", "area": "Microbiologia / PPGST", "ufma": True},
    {"num": 7, "nome": "Liliane dos Santos Rodrigues", "arquivo": "Liliane Rodrigues.pdf", "id_lattes": "6248322274107804", "area": "Saúde / Biotecnologia", "ufma": True},
    {"num": 8, "nome": "Fernanda Farias Costa", "arquivo": "Fernanda Costa.pdf", "id_lattes": "", "area": "Saúde / Farmácia", "ufma": True},
    {"num": 9, "nome": "Alberto Jorge Oliveira Lopes", "arquivo": "Alberto Lopes.pdf", "id_lattes": "", "area": "Química / Produtos Naturais", "ufma": True},
    {"num": 10, "nome": "Tatielle Gomes Dias", "arquivo": "Tatielle Dias.pdf", "id_lattes": "", "area": "Saúde / Biotecnologia", "ufma": True},
]


def analisar_ciclo_atual() -> dict:
    itens_resultado = []
    concluidos = 0
    total_paginas = 0
    total_bytes = 0

    for item in CICLO_1_ALVOS:
        arq_path = DIR_REFS / item["arquivo"]
        existe = arq_path.is_file()
        pags = 0
        tamanho = 0
        if existe:
            tamanho = arq_path.stat().st_size
            total_bytes += tamanho
            try:
                reader = pypdf.PdfReader(str(arq_path))
                pags = len(reader.pages)
            except Exception:
                pags = 0
            total_paginas += pags
            concluidos += 1

        tam_mb = round(tamanho / (1024 * 1024), 1) if tamanho else 0
        itens_resultado.append({
            "num": item["num"],
            "nome": item["nome"],
            "arquivo": item["arquivo"],
            "id_lattes": item["id_lattes"],
            "area": item["area"],
            "presente": existe,
            "paginas": pags,
            "tamanho_formatado": f"{tam_mb} MB" if tam_mb >= 1 else (f"{round(tamanho/1024,1)} KB" if tamanho else "Pendente"),
            "link_lattes": f"http://lattes.cnpq.br/{item['id_lattes']}" if item["id_lattes"] else None,
        })

    percentual = round((concluidos / len(CICLO_1_ALVOS)) * 100)
    return {
        "ciclo": 1,
        "titulo": "Ciclo 1: Núcleo de Coautores do PPGST / UFMA",
        "total_alvos": len(CICLO_1_ALVOS),
        "concluidos": concluidos,
        "percentual": percentual,
        "total_paginas_amostra": total_paginas,
        "total_megabytes": round(total_bytes / (1024 * 1024), 1),
        "itens": itens_resultado,
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    rel = analisar_ciclo_atual()
    print("=" * 60)
    print(f" {rel['titulo']} ")
    print(f" Progresso: {rel['concluidos']}/{rel['total_alvos']} ({rel['percentual']}%) | {rel['total_paginas_amostra']} págs totais ({rel['total_megabytes']} MB)")
    print("=" * 60)
    for it in rel["itens"]:
        status = f"✓ {it['paginas']} págs ({it['tamanho_formatado']})" if it["presente"] else "⏳ Pendente"
        print(f"[{it['num']:02d}] {it['nome']} - {it['area']}: {status}")
