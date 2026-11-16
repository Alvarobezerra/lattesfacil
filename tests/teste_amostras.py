"""Documentos reais de teste (pasta Downloads/Projeto/Teste): reconhecimento + leitura por item.

Uso: python tests/teste_amostras.py [pasta]   (a pasta padrão fica ao lado do projeto; sem ela, o teste é ignorado).
Cada caso diz o item esperado e os campos que o leitor deve extrair. Acrescente casos conforme novos documentos chegarem.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from classificador import classificar  # noqa: E402
from extractor import extract_text_from_pdf_bytes  # noqa: E402
from itens.leitores import LEITORES, ler  # noqa: E402

PASTA = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ.parent / "Teste"

# arquivo -> (item esperado, {campo: trecho que deve conter})
CASOS = {
    "Certificate.pdf": ("apresentacao", {}),
    "Certificate_part.pdf": ("participacao_evento", {"f_nme_evento": "Reunião Anual", "f_ano": "2026", "f_cidade": "São Paulo - SP", "F_FORMA": "Ouvinte"}),
    "DOC-20260923-WA0086.pdf": ("banca", {"F_COD_PROD": "Exame de qualificação de doutorado", "f_ano": "2026", "f_nme_orient": "Antônia Fernanda Lopes da Silva"}),
    "Declaração Aramys dos Reis.pdf": ("banca", {"F_COD_PROD": "Doutorado", "f_ano": "2024", "f_nme_orient": "Kayanny Queiroz Ferreira", "f_inst": "Ceará"}),
    "MENÇÃO HONROSA - PÓS GRADUAÇÃO.pdf": ("premio", {"f_titulo": "Menção honrosa", "f_ano": "2023"}),
    "Patente - probiotico de babaçu.pdf": ("patente", {"f_cod_reg": "BR 10 2024 003766 9", "f_tipo": "Patente de Invenção", "f_titulo": "Bebidas mistas probióticas"}),
    "SEI_0529614_Declaracao.pdf": ("orientacao_concluida", {"nome_orientando": "Mércia Machado Araújo Lima", "curso_orient": "Saúde e Tecnologia", "papel_orientacao": "Orientador principal", "ano": "2023", "titulo": "atividade antioxidante e fotoprotetora"}),
    "SEI_0888683_Declaracao.pdf": ("orientacao_concluida", {"nome_orientando": "Tatielle Gomes Dias", "curso_orient": "Saúde e Tecnologia", "papel_orientacao": "Coorientador", "ano": "2023"}),
    "nomeação.pdf": ("projeto", {"f_titulo": "Ciência na Rede", "F_TPO_NATUREZA": "Extensão", "f_inst": "Universidade Federal do Maranhão"}),
}


def main() -> int:
    if not PASTA.is_dir():
        print(f"IGNORADO: pasta de amostras não encontrada ({PASTA}).")
        return 0
    erros = ok = 0
    for arq, (item, campos) in CASOS.items():
        f = PASTA / arq
        if not f.is_file():
            print(f"IGNORADO {arq}: arquivo ausente")
            continue
        info = extract_text_from_pdf_bytes(f.read_bytes())
        cls = classificar(info["text"], arq, info["page_count"], 0)
        top = cls["candidatos"][0]["id"] if cls["candidatos"] else "nenhum"
        falhas = []
        if top != item or cls["decisao"] == "escolher":
            falhas.append(f"classificou como {top} ({cls['decisao']}), esperado {item}")
        if campos:
            if item.startswith("orientacao"):
                from orientacao import parse_orientacao
                v = parse_orientacao(info["text"], "Aramys Silva dos Reis")
            elif item not in LEITORES:
                falhas.append("sem leitor")
                v = {}
            else:
                v = ler(item, info["text"], "")["valores"]
            if v:
                for k, trecho in campos.items():
                    if trecho.lower() not in str(v.get(k, "")).lower():
                        falhas.append(f"{k}={v.get(k)!r}, esperado conter {trecho!r}")
        if falhas:
            erros += 1
            print(f"ERRO   {arq}: " + "; ".join(falhas))
        else:
            ok += 1
            print(f"OK     {arq} -> {item}")
    print(f"\nAcertos: {ok}/{ok + erros}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
