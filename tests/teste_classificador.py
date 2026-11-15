"""Teste do classificador de evidências: documentos reais (se existirem) + casos sintéticos.

Uso:  python tests/teste_classificador.py
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from classificador import classificar  # noqa: E402
from extractor import extract_text_from_pdf_bytes  # noqa: E402

DOWNLOADS = Path.home() / "Downloads"

# (descrição, texto, resultado esperado: id | "ambiguo:<id1>,<id2>" | "escolher")
SINTETICOS = [
    ("Declaração de orientação de TCC", 'Declaro que orientei o aluno JOÃO PEDRO ALVES no Trabalho de Conclusão de Curso intitulado "Perícia criminal", concluído em 2024. Orientador: Fulano de Tal.', "orientacao_concluida"),
    ("IC em andamento", "Declaramos que o aluno CARLOS NETO realiza iniciação científica em andamento sob orientação do Prof. Fulano, vigência da bolsa 2025-2026.", "orientacao_andamento"),
    ("Declaração de banca", "Declaramos que Fulano de Tal participou como membro da banca examinadora da defesa da dissertação de mestrado de Maria Souza.", "banca"),
    ("Certificado de participação", "Certificamos que Fulano de Tal participou do XV Congresso Brasileiro de Saúde, na qualidade de participante, com carga horária de 20 horas.", "participacao_evento"),
    ("Certificado comissão organizadora", "Certificamos que Fulano de Tal integrou a comissão organizadora do II Simpósio de Farmácia Clínica.", "organizacao_evento"),
    ("Certificado de ministrante", "Certificamos que Fulano de Tal ministrou o minicurso Introdução à Farmacovigilância, com carga horária de 8 horas.", "curso_ministrado"),
    ("Certificado de curso (aluno)", "Certificamos que Fulano de Tal concluiu o curso de extensão em Gestão Hospitalar, com carga horária de 60 horas.", "formacao_complementar"),
    ("Diploma", "A Universidade conferiu o grau de bacharel em Farmácia a Fulano de Tal, em colação de grau realizada em 2010. DIPLOMA.", "formacao_academica"),
    ("Declaração de vínculo", "Declaramos para os devidos fins que Fulano de Tal exerce o cargo de Perito Criminal, matrícula funcional 123, vínculo de servidor público efetivo.", "atuacao_profissional"),
    ("Carta de aceite", "Prezado autor, temos o prazer de informar que seu manuscrito foi aceito para publicação na Revista Brasileira de Farmácia.", "artigo_aceito"),
    ("Certificado de revisor", "Certificamos que Fulano de Tal atuou como revisor (peer review) de manuscritos do periódico Journal of Clinical Pharmacy.", "revisor_periodico"),
    ("Corpo editorial", "Portaria: Fulano de Tal designado editor associado do corpo editorial da Revista de Saúde Pública.", "corpo_editorial"),
    ("Carta patente", "O INPI concede a CARTA PATENTE nº BR 10 2020 000001-0 ao titular, para a invenção intitulada Processo de fermentação.", "patente"),
    ("Registro de software", "Certificado de registro de programa de computador, INPI, titulares Fulano e Beltrano.", "software_registro"),
    ("Prêmio", "Certificamos que o trabalho foi premiado como Melhor Trabalho da área de Farmacologia no congresso.", "premio"),
    ("Projeto", "Declaramos que Fulano de Tal é integrante do projeto de pesquisa Atividade antioxidante de plantas, financiado pela FAPEMA (edital 2024).", "projeto"),
    ("Idioma", "Certificado de proficiência em inglês, nível B2, CEFR, Cambridge.", "idioma"),
    ("Licença", "Portaria concede licença-maternidade à servidora por 180 dias.", "licenca"),
    ("DOI de artigo", "10.1371/journal.pmed.0020124 Journal PLoS Medicine volume 2 abstract received 2005 accepted 2005", "artigo"),
    ("Ambíguo: apresentou + participou", "Certificamos que Fulano de Tal participou do Congresso Internacional de Saúde e apresentou o trabalho intitulado Efeito antioxidante em formato de pôster.", "apresentacao"),
    ("Palestrante", "Certificamos que Fulano de Tal proferiu a palestra Segurança do Paciente no IX Simpósio de Enfermagem.", "apresentacao"),
    ("Coorientação", "Declaramos que a Profa. Maria Lima atuou como coorientadora da dissertação de mestrado de Pedro Alves, defendida em 2022.", "orientacao_concluida"),
    ("Ata de defesa (ambígua)", "ATA DE DEFESA DE DISSERTAÇÃO. Realizou-se a defesa da dissertação de mestrado de Maria Souza perante a banca examinadora composta por Prof. A (orientador), Prof. B e Prof. C. A candidata foi aprovada.", "ambiguo:banca,orientacao_concluida"),
    ("Monitoria (sem item claro)", "Certificado de monitoria da disciplina de Anatomia Humana, semestre 2023.1, 60 horas.", "escolher"),
    ("Sem relação", "Lista de compras: arroz, feijão, macarrão, sabão em pó e detergente. Comprar na sexta.", "escolher"),
    ("Texto vazio (imagem escaneada)", "", "escolher"),
]


def lerpdf(caminho: Path):
    b = caminho.read_bytes()
    info = extract_text_from_pdf_bytes(b)
    kw = len(re.findall(r"keywords?\s*:|palavras[- ]chave\s*:", info["text"], re.I))
    return info["text"], info["page_count"], kw


def mostrar(rotulo, r, esperado=None):
    c = r["candidatos"]
    top = f'{c[0]["item"][:38]} ({c[0]["confianca"]:.2f})' if c else "—"
    segundo = f'{c[1]["item"][:30]} ({c[1]["confianca"]:.2f})' if len(c) > 1 else ""
    ok = ""
    if esperado is not None:
        if esperado.startswith("ambiguo:"):
            ids = esperado.split(":")[1].split(",")
            top3 = [x["id"] for x in c[:3]]
            good = r["decisao"] == "confirmar" and all(i in top3 for i in ids)
        elif esperado == "escolher":
            good = r["decisao"] == "escolher"
        else:
            good = bool(c) and c[0]["id"] == esperado
        ok = "OK " if good else f"ERRO (esperado {esperado})"
    print(f'{ok:6} {rotulo[:30]:30} -> {r["decisao"]:9} | {top} | 2º: {segundo}')
    return ok.strip() == "OK" if esperado else None


def main():
    certos = total = 0
    print("=== DOCUMENTOS REAIS ===")
    reais = [("Certificado COIMAMA 2024.pdf", "apresentacao", DOWNLOADS / "Certificado COIMAMA 2024.pdf"),
             ("2024-SEMICresumo.pdf", "anais", RAIZ / "exemplos" / "2024-SEMICresumo.pdf"),
             ("Caderno FeSBE 2026 (891 pág.)", "caderno", RAIZ / "exemplos" / "bbr.ptm.23.384_FeSBE2026.pdf"),
             ("avaliação.pdf (imagem)", "escolher", DOWNLOADS / "avaliação.pdf")]
    for nome, esp, caminho in reais:
        if not caminho.exists():
            print(f"(pulado: {caminho.name} não encontrado)")
            continue
        texto, pags, kw = lerpdf(caminho)
        r = classificar(texto, caminho.name, pags, kw)
        total += 1
        certos += bool(mostrar(nome, r, esp))
    print("\n=== CASOS SINTÉTICOS ===")
    for rotulo, texto, esp in SINTETICOS:
        r = classificar(texto)
        total += 1
        certos += bool(mostrar(rotulo, r, esp))
    print(f"\nAcertos: {certos}/{total}")
    return 0 if certos == total else 1


if __name__ == "__main__":
    sys.exit(main())
