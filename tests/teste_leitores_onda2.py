"""Leitores das ondas 2 a 4 com textos sintéticos (não substituem amostras reais; ver plano de implantação).

Uso: python tests/teste_leitores_onda2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classificador import classificar  # noqa: E402
from itens.leitores import ler  # noqa: E402

CASOS = [
    ("revisor_periodico",
     "CERTIFICADO. Certificamos que o Dr. João Silva atuou como revisor ad hoc da Revista Brasileira de Saúde, "
     "no período de 03/2022 a 05/2023, avaliando manuscritos submetidos ao periódico.",
     {"f_nme_agencia": "Brasileira de Saúde", "f_ano_ini": "2022", "f_mes_ini": "03", "f_ano_fim": "2023"}),
    ("corpo_editorial",
     "Declaramos que a Profa. Maria Souza é Editora Associada da Revista de Ciências Médicas desde 2021.",
     {"f_nme_agencia": "de Ciências Médicas", "f_ano_ini": "2021"}),
    ("atuacao_profissional",
     "Declaração de vínculo. Declaramos que Ana Lima é servidora pública efetiva da Universidade Federal do Maranhão, "
     "exerce o cargo de Professor Associado, com regime de dedicação exclusiva, desde 10 de março de 2015.",
     {"f_inst": "Universidade Federal do Maranhão", "f_stavinc": "Sim", "f_vinc": "Servidor público", "f_regime": "Dedicação exclusiva",
      "f_ano_ini": "2015"}),
    ("idioma", "Certificado de proficiência em língua inglesa. Cambridge English, nível B2 (CEFR).",
     {"F_COD_IDIOMA": "Inglês", "F_LE": "Razoavelmente"}),
    ("licenca",
     "Portaria concede licença-maternidade à servidora de 01 de março de 2024 a 28 de agosto de 2024, por 180 dias.",
     {"f_tipo_licenca": "Maternidade", "f_dta_inicio": "01/03/2024", "f_dta_fim": "28/08/2024"}),
    ("artigo_aceito",
     "Dear Dr. Silva, we are pleased to inform you that your manuscript \"Probiotic beverages from babassu\" has been accepted "
     "for publication in the Journal of Functional Foods. DOI 10.1016/j.jff.2025.001. 12 de maio de 2025",
     {"f_cod_doi": "10.1016/j.jff.2025.001", "F_IDIOMA": "Inglês", "f_ano": "2025"}),
    ("relatorio_tecnico",
     "Parecer técnico sobre a viabilidade de produção de bebidas probióticas, elaborado em 4 de junho de 2023 como consultoria.",
     {"F_COD_PROD": "Consultoria", "f_ano": "2023"}),
    ("software_registro",
     "Certificado de registro de programa de computador. Processo BR 51 2023 001234 5. Título: Sistema Lattes Facil "
     "Linguagem: Python; JavaScript Campo de aplicação: Educação. 20 de novembro de 2023",
     {"f_cod_reg": "BR 51 2023 001234 5", "f_inst": "INPI", "f_plataforma": "Python; JavaScript", "f_dta_conc": "20/11/2023"}),
]


def main() -> int:
    erros = 0
    for item, texto, esperado in CASOS:
        r = ler(item, texto, "João Silva")
        falhas = []
        if r is None:
            falhas.append("sem leitor/especificação")
        else:
            for campo, trecho in esperado.items():
                if trecho.lower() not in str(r["valores"].get(campo, "")).lower():
                    falhas.append(f"{campo}={r['valores'].get(campo)!r}, esperado conter {trecho!r}")
        cls = classificar(texto)
        top = cls["candidatos"][0]["id"] if cls["candidatos"] else "nenhum"
        aviso = "" if top == item else f" [classificador: {top}]"
        print(("FALHA " if falhas else "OK    ") + item + aviso + ("  | " + "; ".join(falhas) if falhas else ""))
        erros += bool(falhas)
    print(f"\nAcertos: {len(CASOS) - erros}/{len(CASOS)}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
