"""Gerador da base de documentos sintéticos de teste descaracterizados.

Utiliza os modelos e layouts reais dos dossiês de inscrição (Edital PPGST / UFMA),
substituindo os dados de autoria e identificação por:
  - Autor/Candidato: Álvaro Antônio Bezerra dos Santos
  - Citações bibliográficas: SANTOS, A. A. B.; SANTOS, Álvaro Antônio Bezerra dos
  - Dados pessoais: Hipotéticos (CPF, RG, Título Eleitoral, QR Codes fictícios)
  - Identificação dos arquivos: Padrão numérico 00001_<NOME> e prefixos Q9 a Q17

Estrutura do arquivo de currículo (Q13):
  - Parte 1 (Páginas 1 a 4): Currículo Lattes Oficial CNPq (pkg_impcv.trata)
  - Parte 2 (Página 5): Folha de Rosto e Sumário das Evidências
  - Parte 3 (Páginas 6 a 15): 10 Evidências acadêmicas fiéis para simular reconhecimento e lançamento

Também exporta as 10 evidências de forma individual na subpasta:
  tests/base_documentos_teste/evidencias_individuais/
"""
from __future__ import annotations

import io
import os
import shutil
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import pymupdf

NOME_COMPLETO = "Álvaro Antônio Bezerra dos Santos"
NOME_UPPER = "ÁLVARO ANTÔNIO BEZERRA DOS SANTOS"
NOME_CITACAO_LATTES = "SANTOS, A. A. B.; SANTOS, Álvaro Antônio Bezerra dos; BEZERRA DOS SANTOS, ÁLVARO ANTÔNIO"
CPF_HIPOTETICO = "123.456.789-00"
RG_HIPOTETICO = "023456782012-4 SSP/MA"
LATTES_ID = "3540029577221469"
ORCID_ID = "0000-0002-1825-0099"
TITULO_ELEITORAL = "0123 4567 8901"
INSCRICAO_NUM = "00001"
TITULO_PROJETO = "DESENVOLVIMENTO DE FITOPRODUTO ANTIMICROBIANO A PARTIR DA BIODIVERSIDADE MARANHENSE COMO TECNOLOGIA APLICADA À ATENÇÃO BÁSICA À SAÚDE"


def criar_diretorios() -> tuple[Path, Path]:
    destino = Path(__file__).resolve().parent / "base_documentos_teste" / f"{INSCRICAO_NUM}_ALVARO_ANTONIO_BEZERRA_DOS_SANTOS"
    destino.mkdir(parents=True, exist_ok=True)
    pasta_evid = Path(__file__).resolve().parent / "base_documentos_teste" / "evidencias_individuais"
    pasta_evid.mkdir(parents=True, exist_ok=True)
    return destino, pasta_evid


# --------------------------------------------------------------------------------------------------
# 1. 00001.docx - Ficha de Avaliação da Banca
# --------------------------------------------------------------------------------------------------
def gerar_docx(destino: Path) -> None:
    docx_modelo = Path(__file__).resolve().parent / "curriculos e modelos" / "1_INSCRIÇÕES" / "25331_VANESSA_VITORIA_MOURAO_PEREIRA" / "25331.docx"
    arq_saida = destino / f"{INSCRICAO_NUM}.docx"

    if docx_modelo.exists():
        with zipfile.ZipFile(docx_modelo, "r") as zin, zipfile.ZipFile(arq_saida, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                dados = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    xml_str = dados.decode("utf-8")
                    xml_str = xml_str.replace("25331", INSCRICAO_NUM)
                    xml_str = xml_str.replace(
                        "ESTRATÉGIA EDUCATIVA E CUIDADO EM SAÚDE BUCAL DE PESSOAS ACOMETIDAS PELA HANSENÍASE NA ATENÇÃO PRIMÁRIA",
                        TITULO_PROJETO
                    )
                    dados = xml_str.encode("utf-8")
                zout.writestr(item, dados)
    else:
        with zipfile.ZipFile(arq_saida, "w", zipfile.ZIP_DEFLATED) as zout:
            doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>EDITAL PPGST Nº 04/2026 - FICHA DE AVALIAÇÃO DO ANTEPROJETO</w:t></w:r></w:p>
    <w:p><w:r><w:t>Inscrição: {INSCRICAO_NUM} - Candidato: {NOME_COMPLETO}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Título: {TITULO_PROJETO}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
            zout.writestr("word/document.xml", doc_xml.encode("utf-8"))


# --------------------------------------------------------------------------------------------------
# 2. Q9 - Carteira de Identidade Nacional (CIN)
# --------------------------------------------------------------------------------------------------
def gerar_q9_identidade(destino: Path) -> None:
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)

    pg.draw_rect(pymupdf.Rect(40, 40, 555, 800), color=(0.7, 0.7, 0.7), width=1)
    pg.draw_rect(pymupdf.Rect(50, 50, 545, 120), color=(0.1, 0.4, 0.2), fill=(0.95, 0.98, 0.95), width=1.5)
    pg.insert_textbox(pymupdf.Rect(60, 58, 535, 115), 
                      "REPÚBLICA FEDERATIVA DO BRASIL\nMINISTÉRIO DA JUSTIÇA E SEGURANÇA PÚBLICA\nGOVERNO DO ESTADO DO MARANHÃO — SECRETARIA DE SEGURANÇA PÚBLICA\nCARTEIRA DE IDENTIDADE NACIONAL (CIN)",
                      fontsize=10, fontname="hebo", align=1, color=(0.1, 0.3, 0.1))

    top_doc = 140
    pg.draw_rect(pymupdf.Rect(50, top_doc, 545, 520), color=(0.2, 0.4, 0.3), width=1.5, fill=(1, 1, 1))

    pg.draw_rect(pymupdf.Rect(70, top_doc + 20, 180, top_doc + 170), color=(0.5, 0.5, 0.5), fill=(0.92, 0.92, 0.92))
    pg.insert_textbox(pymupdf.Rect(70, top_doc + 75, 180, top_doc + 120), "FOTO 3x4\nHIPOTÉTICA\nPARA TESTES", fontsize=9, fontname="hebo", align=1, color=(0.4, 0.4, 0.4))

    pg.draw_rect(pymupdf.Rect(70, top_doc + 185, 180, top_doc + 300), color=(0.5, 0.5, 0.5), fill=(0.95, 0.95, 0.95))
    pg.insert_textbox(pymupdf.Rect(70, top_doc + 230, 180, top_doc + 270), "POLEGAR DIREITO\nDIGITAL", fontsize=8, fontname="helv", align=1, color=(0.5, 0.5, 0.5))

    cx = 200
    cy = top_doc + 20
    campos = [
        ("NOME COMPLETO", NOME_UPPER),
        ("REGISTRO GERAL (RG)", RG_HIPOTETICO),
        ("CADASTRO DE PESSOAS FÍSICAS (CPF)", CPF_HIPOTETICO),
        ("DATA DE NASCIMENTO", "15/05/1996"),
        ("NATURALIDADE", "SÃO LUÍS - MA"),
        ("NACIONALIDADE", "BRASILEIRA"),
        ("FILIAÇÃO", "ANTÔNIO CARLOS DOS SANTOS\nMARIA HELENA BEZERRA DOS SANTOS"),
        ("ÓRGÃO EXPEDIDOR", "SSP / INSTITUTO DE IDENTIFICAÇÃO DO MARANHÃO"),
        ("DATA DE EXPEDIÇÃO", "10/01/2024"),
        ("VALIDADE", "INDETERMINADA (LEI FEDERAL Nº 14.534/2023)"),
    ]

    for label, val in campos:
        pg.insert_text((cx, cy + 8), label, fontsize=7, fontname="hebo", color=(0.4, 0.4, 0.4))
        pg.insert_textbox(pymupdf.Rect(cx, cy + 10, 530, cy + 36), val, fontsize=10, fontname="hebo" if "NOME" in label or "CPF" in label else "helv", color=(0.1, 0.1, 0.1))
        cy += 32 if "\n" not in val else 40

    pg.draw_line(pymupdf.Point(200, cy + 25), pymupdf.Point(450, cy + 25), color=(0.3, 0.3, 0.3), width=1)
    pg.insert_text((220, cy + 35), "Álvaro Antônio Bezerra dos Santos (Assinatura do Titular)", fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))

    pg.draw_rect(pymupdf.Rect(50, 540, 545, 650), color=(0.2, 0.5, 0.3), fill=(0.96, 0.98, 0.96))
    pg.insert_textbox(pymupdf.Rect(70, 550, 420, 640),
                      "DOCUMENTO DE IDENTIFICAÇÃO DIGITAL GERADO PARA AMBIENTE DE TESTES DO LATTESFÁCIL\n"
                      "Conformidade: Lei Federal nº 14.534/2023 (CPF como identificador unívoco nacional).\n"
                      f"Código de Autenticação Digital: CIN-MA-2024-{INSCRICAO_NUM}-HYPOTHETICAL-TEST-ONLY\n"
                      "Verificação de autenticidade: aplicativo gov.br ou portal oficial de validação.",
                      fontsize=8, fontname="helv", color=(0.2, 0.3, 0.2))

    pg.draw_rect(pymupdf.Rect(440, 555, 525, 635), color=(0.3, 0.3, 0.3), fill=(0.9, 0.9, 0.9))
    pg.insert_textbox(pymupdf.Rect(440, 585, 525, 620), "QR CODE\nGOV.BR", fontsize=8, fontname="hebo", align=1, color=(0.3, 0.3, 0.3))

    doc.save(destino / "Q9_identidade_nacional_alvaro.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 3. Q10 - Certidão de Quitação Eleitoral (TSE)
# --------------------------------------------------------------------------------------------------
def gerar_q10_eleitoral(destino: Path) -> None:
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)

    pg.insert_textbox(pymupdf.Rect(50, 50, 545, 110),
                      "JUSTIÇA ELEITORAL\nTRIBUNAL SUPERIOR ELEITORAL\nCERTIDÃO DE QUITAÇÃO ELEITORAL",
                      fontsize=12, fontname="hebo", align=1, color=(0.1, 0.1, 0.1))

    corpo = (
        "Certifico que, de acordo com os assentamentos do Cadastro Eleitoral e com o que dispõe a Lei Nº 9.504/1997, "
        "o(a) eleitor(a) abaixo qualificado(a) está QUITE com a Justiça Eleitoral na presente data.\n\n"
        "Certidão emitida às 14:30 em 22/09/2026\n\n"
        "Res.-TSE nº 21.823/2004:\n"
        "O conceito de quitação eleitoral reúne a plenitude do gozo dos direitos políticos, o regular exercício do voto, "
        "salvo quando facultativo, o atendimento a convocações da Justiça Eleitoral para auxiliar os trabalhos relativos "
        "ao pleito, a inexistência de multas aplicadas, em caráter definitivo, pela Justiça Eleitoral e não remitidas, "
        "excetuadas as anistias legais, e a regular prestação de contas de campanha eleitoral, quando se tratar de candidatos.\n\n"
        "A plenitude do gozo de direitos políticos decorre da inocorrência de perda de nacionalidade; cancelamento de "
        "naturalização por sentença transitada em julgado; interdição por incapacidade civil absoluta; condenação criminal "
        "transitada em julgado, enquanto durarem seus efeitos; recusa de cumprir obrigação a todos imposta ou prestação "
        "alternativa; condenação por improbidade administrativa; conscrição; e opção, em Portugal, pelo estatuto da igualdade.\n\n"
        "Esta certidão de quitação eleitoral é expedida gratuitamente. Sua autenticidade poderá ser confirmada na página "
        "do Tribunal Superior Eleitoral na Internet, no endereço: http://www.tse.jus.br ou pelo aplicativo e-Título, por meio do código:"
    )
    pg.insert_textbox(pymupdf.Rect(50, 125, 545, 420), corpo, fontsize=9.5, fontname="helv", color=(0.1, 0.1, 0.1))

    pg.draw_rect(pymupdf.Rect(180, 425, 415, 455), color=(0.3, 0.3, 0.3), fill=(0.95, 0.95, 0.95))
    pg.insert_textbox(pymupdf.Rect(180, 432, 415, 450), "ALVR.TEST.2026.TSE4", fontsize=11, fontname="hebo", align=1)

    pg.draw_rect(pymupdf.Rect(50, 475, 545, 680), color=(0.3, 0.3, 0.3), width=1)
    
    y = 490
    dados = [
        ("Eleitor(a):", NOME_UPPER),
        ("Inscrição (Título):", f"{TITULO_ELEITORAL}   |   Zona: 001   |   Seção: 0012"),
        ("Data de nascimento:", "15/05/1996"),
        ("Município / UF:", "0921 - SÃO LUÍS - MA   |   Domicílio eleitoral desde: 10/02/2014"),
        ("Filiação:", "- MARIA HELENA BEZERRA DOS SANTOS\n- ANTÔNIO CARLOS DOS SANTOS"),
        ("Ocupação declarada:", "FARMACÊUTICO, PESQUISADOR E ASSEMELHADOS"),
    ]
    for rotulo, valor in dados:
        pg.insert_text((65, y), rotulo, fontsize=8.5, fontname="hebo", color=(0.3, 0.3, 0.3))
        pg.insert_textbox(pymupdf.Rect(190, y - 9, 530, y + 25), valor, fontsize=9.5, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 28 if "\n" not in valor else 36

    doc.save(destino / "Q10_certidao_quitacao_eleitoral.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 4. Q11 - Diploma Universitário de Graduação
# --------------------------------------------------------------------------------------------------
def gerar_q11_diploma(destino: Path) -> None:
    doc = pymupdf.open()
    pg1 = doc.new_page(width=842, height=595)

    pg1.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.2, 0.35, 0.6), width=2.5)
    pg1.draw_rect(pymupdf.Rect(38, 38, 804, 557), color=(0.7, 0.6, 0.3), width=1.5)

    pg1.insert_textbox(pymupdf.Rect(50, 55, 792, 115),
                       "REPÚBLICA FEDERATIVA DO BRASIL\nUNIVERSIDADE FEDERAL DO MARANHÃO\nCENTRO DE CIÊNCIAS BIOLÓGICAS E DA SAÚDE",
                       fontsize=12, fontname="hebo", align=1, color=(0.1, 0.2, 0.4))

    pg1.insert_textbox(pymupdf.Rect(50, 130, 792, 175), "DIPLOMA", fontsize=24, fontname="hebo", align=1, color=(0.2, 0.2, 0.2))

    texto_outorga = (
        f"O Reitor da Universidade Federal do Maranhão, no uso de suas atribuições legais e tendo em vista a conclusão "
        f"do Curso de Bacharelado em Farmácia, em 18 de dezembro de 2020, e a colação de grau realizada em 22 de janeiro de 2021, "
        f"confere o grau de BACHAREL EM FARMÁCIA a\n\n"
        f"{NOME_UPPER}\n\n"
        f"nacionalidade brasileira, natural de São Luís - MA, nascido em 15 de maio de 1996, portador do RG nº {RG_HIPOTETICO} "
        f"e do CPF nº {CPF_HIPOTETICO}, e outorga-lhe o presente Diploma para que possa gozar de todos os direitos e prerrogativas legais."
    )
    pg1.insert_textbox(pymupdf.Rect(80, 185, 762, 380), texto_outorga, fontsize=12.5, fontname="helv", align=1, color=(0.1, 0.1, 0.1))

    pg1.insert_text((100, 415), "São Luís - MA, 22 de janeiro de 2021.", fontsize=11, fontname="helv")

    pg1.draw_line(pymupdf.Point(100, 485), pymupdf.Point(320, 485), color=(0.2, 0.2, 0.2))
    pg1.insert_textbox(pymupdf.Rect(100, 490, 320, 525), "Prof. Dr. Natalino Salgado Filho\nReitor da UFMA", fontsize=9, fontname="hebo", align=1)

    pg1.draw_line(pymupdf.Point(360, 485), pymupdf.Point(580, 485), color=(0.2, 0.2, 0.2))
    pg1.insert_textbox(pymupdf.Rect(360, 490, 580, 525), "Diretoria do Centro de Ciências da Saúde\nUFMA", fontsize=9, fontname="hebo", align=1)

    pg1.draw_line(pymupdf.Point(620, 485), pymupdf.Point(780, 485), color=(0.2, 0.2, 0.2))
    pg1.insert_textbox(pymupdf.Rect(620, 490, 780, 525), f"{NOME_COMPLETO}\nDiplomado", fontsize=9, fontname="hebo", align=1)

    pg2 = doc.new_page(width=842, height=595)
    pg2.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.6, 0.6, 0.6), width=1)
    pg2.insert_textbox(pymupdf.Rect(60, 50, 782, 100),
                       "UNIVERSIDADE FEDERAL DO MARANHÃO — REGISTRO GERAL DE DIPLOMAS",
                       fontsize=12, fontname="hebo", align=1)

    verso_txt = (
        f"Diploma registrado sob o nº 154041-FARM-2021, Livro D-45, Folha 88, Processo nº 23115.001234/2021-10.\n"
        f"Curso reconhecido pela Portaria MEC nº 890 de 20/11/2018, publicada no Diário Oficial da União em 21/11/2018.\n"
        f"Habilitação profissional registrada conforme Lei Federal nº 3.820/1960.\n\n"
        f"Titular: {NOME_UPPER}\n"
        f"CPF: {CPF_HIPOTETICO} | RG: {RG_HIPOTETICO}\n\n"
        f"Divisão de Registro e Controle Acadêmico - DRCA / PROEN / UFMA\n"
        f"Responsável pelo Registro: Matrícula SIAPE 1827364"
    )
    pg2.insert_textbox(pymupdf.Rect(80, 120, 762, 350), verso_txt, fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))

    doc.save(destino / "Q11_diploma_graduacao_farmacia.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 5. Q12 - Histórico Escolar de Graduação
# --------------------------------------------------------------------------------------------------
def gerar_q12_historico(destino: Path) -> None:
    doc = pymupdf.open()
    
    disciplinas_semestres = [
        ("1º SEMESTRE (2016.1)", [
            ("FAR101", "Química Geral e Inorgânica", 60, 4, 9.5, "APROVADO"),
            ("BIO102", "Biologia Celular e Tecidual", 60, 4, 9.0, "APROVADO"),
            ("ANA103", "Anatomia Humana Básica", 75, 5, 8.5, "APROVADO"),
            ("MET104", "Metodologia da Pesquisa Científica", 45, 3, 10.0, "APROVADO"),
        ]),
        ("2º SEMESTRE (2016.2)", [
            ("QUI201", "Química Orgânica Fundamental", 90, 6, 8.8, "APROVADO"),
            ("BIO202", "Bioquímica Básica", 75, 5, 9.2, "APROVADO"),
            ("FIS203", "Fisiologia Humana I", 75, 5, 8.7, "APROVADO"),
            ("FAR204", "História e Deontologia Farmacêutica", 45, 3, 9.8, "APROVADO"),
        ]),
        ("3º SEMESTRE (2017.1)", [
            ("FIS301", "Fisiologia Humana II", 75, 5, 9.0, "APROVADO"),
            ("MIC302", "Microbiologia Médica e Aplicada", 90, 6, 9.4, "APROVADO"),
            ("IMU303", "Imunologia Geral e Básica", 60, 4, 9.6, "APROVADO"),
            ("FAR304", "Farmacognosia e Plantas Medicinais", 90, 6, 9.7, "APROVADO"),
        ]),
        ("4º SEMESTRE (2017.2)", [
            ("FMC401", "Farmacologia Geral", 90, 6, 9.3, "APROVADO"),
            ("FIT402", "Fitoquímica e Bioprospecção", 75, 5, 9.8, "APROVADO"),
            ("PAR403", "Parasitologia Clínica", 60, 4, 8.9, "APROVADO"),
            ("GEN404", "Genética e Biologia Molecular", 60, 4, 9.1, "APROVADO"),
        ]),
        ("5º SEMESTRE (2018.1)", [
            ("FMC501", "Farmacologia Clínica e Terapêutica I", 90, 6, 9.5, "APROVADO"),
            ("TEC502", "Tecnologia Farmacêutica I", 90, 6, 8.8, "APROVADO"),
            ("PAT503", "Patologia Geral", 60, 4, 9.0, "APROVADO"),
            ("EPI504", "Epidemiologia e Saúde Coletiva", 45, 3, 9.7, "APROVADO"),
        ]),
        ("6º SEMESTRE (2018.2)", [
            ("FMC601", "Farmacologia Clínica e Terapêutica II", 90, 6, 9.4, "APROVADO"),
            ("TEC602", "Tecnologia Farmacêutica II", 90, 6, 9.0, "APROVADO"),
            ("CLI603", "Bioquímica Clínica", 90, 6, 9.2, "APROVADO"),
            ("TOX604", "Toxicologia Geral e Ocupacional", 60, 4, 9.6, "APROVADO"),
        ]),
        ("7º SEMESTRE (2019.1)", [
            ("CLI701", "Hematologia e Imunologia Clínica", 90, 6, 9.3, "APROVADO"),
            ("HOS702", "Farmácia Hospitalar e Clínica", 75, 5, 9.8, "APROVADO"),
            ("BIO703", "Biotecnologia Farmacêutica", 60, 4, 9.5, "APROVADO"),
            ("TCC704", "Trabalho de Conclusão de Curso I", 60, 4, 10.0, "APROVADO"),
        ]),
        ("8º SEMESTRE (2019.2)", [
            ("ATE801", "Atenção e Assistência Farmacêutica", 60, 4, 9.7, "APROVADO"),
            ("BRO802", "Bromatologia e Análise de Alimentos", 75, 5, 9.1, "APROVADO"),
            ("TCC803", "Trabalho de Conclusão de Curso II", 90, 6, 10.0, "APROVADO"),
            ("OPT804", "Tópicos Avançados em Produtos Naturais", 60, 4, 9.9, "APROVADO"),
        ]),
        ("9º e 10º SEMESTRES (2020.1 - 2020.2)", [
            ("EST901", "Estágio Supervisionado em Farmácia Comunitária", 400, 20, 10.0, "APROVADO"),
            ("EST902", "Estágio Supervisionado em Farmácia Hospitalar", 400, 20, 10.0, "APROVADO"),
            ("EST903", "Estágio Supervisionado em Análises Clínicas", 400, 20, 9.8, "APROVADO"),
            ("EST904", "Estágio Supervisionado em Indústria/P&D", 300, 15, 10.0, "APROVADO"),
        ]),
    ]

    paginas_divisao = [
        disciplinas_semestres[0:3],
        disciplinas_semestres[3:6],
        disciplinas_semestres[6:9],
    ]

    for num_pg, semestres in enumerate(paginas_divisao, 1):
        pg = doc.new_page(width=595, height=842)

        pg.insert_textbox(pymupdf.Rect(40, 30, 555, 75),
                          "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\nPRÓ-REITORIA DE ENSINO — DEPARTAMENTO DE DESENVOLVIMENTO DO ENSINO DE GRADUAÇÃO\nHISTÓRICO ESCOLAR OFICIAL DE GRADUAÇÃO",
                          fontsize=9, fontname="hebo", align=1)
        pg.draw_line(pymupdf.Point(40, 80), pymupdf.Point(555, 80), color=(0.3, 0.3, 0.3), width=1)

        pg.insert_textbox(pymupdf.Rect(40, 85, 555, 140),
                          f"Discente: {NOME_UPPER}  |  Matrícula: 2016012345  |  CPF: {CPF_HIPOTETICO}\n"
                          f"Curso: FARMÁCIA - BACHARELADO  |  Grau conferido: BACHAREL EM FARMÁCIA\n"
                          f"Ingresso: 2016/1 (Processo Seletivo SiSU)  |  Conclusão: 2020/2  |  Colação de Grau: 22/01/2021\n"
                          f"Situação do Aluno: GRADUADO  |  Regime: Semestral / Integral",
                          fontsize=8.5, fontname="helv")

        pg.draw_line(pymupdf.Point(40, 145), pymupdf.Point(555, 145), color=(0.3, 0.3, 0.3), width=1)

        y = 155
        for nome_semestre, mat_lista in semestres:
            pg.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.5, 0.4), fill=(0.92, 0.95, 0.93))
            pg.insert_text((45, y + 13), nome_semestre, fontsize=8, fontname="hebo", color=(0.1, 0.3, 0.1))
            y += 20

            pg.insert_text((45, y + 10), "CÓDIGO", fontsize=7.5, fontname="hebo")
            pg.insert_text((105, y + 10), "COMPONENTE CURRICULAR", fontsize=7.5, fontname="hebo")
            pg.insert_text((380, y + 10), "CH", fontsize=7.5, fontname="hebo")
            pg.insert_text((415, y + 10), "CRÉD.", fontsize=7.5, fontname="hebo")
            pg.insert_text((460, y + 10), "MÉDIA", fontsize=7.5, fontname="hebo")
            pg.insert_text((505, y + 10), "SITUAÇÃO", fontsize=7.5, fontname="hebo")
            y += 14

            for cod, desc, ch, cr, nota, sit in mat_lista:
                pg.insert_text((45, y + 10), cod, fontsize=8, fontname="helv")
                pg.insert_text((105, y + 10), desc, fontsize=8, fontname="helv")
                pg.insert_text((380, y + 10), str(ch), fontsize=8, fontname="helv")
                pg.insert_text((420, y + 10), str(cr), fontsize=8, fontname="helv")
                pg.insert_text((465, y + 10), f"{nota:.1f}", fontsize=8, fontname="hebo")
                pg.insert_text((505, y + 10), sit, fontsize=7.5, fontname="helv", color=(0.1, 0.5, 0.2))
                y += 14
            y += 8

        if num_pg == 3:
            pg.draw_rect(pymupdf.Rect(40, y + 10, 555, y + 75), color=(0.3, 0.3, 0.3), fill=(0.97, 0.97, 0.97))
            pg.insert_textbox(pymupdf.Rect(50, y + 15, 545, y + 70),
                              "RESUMO DO RENDIMENTO ACADÊMICO:\n"
                              "Carga Horária Total Obrigatória Concluída: 4.250 Horas  |  Total de Créditos: 215\n"
                              "Coeficiente de Rendimento Geral (CRG): 9.38  |  Classificação na Turma: 1º Lugar\n"
                              "Título do TCC: 'Avaliação da atividade antibacteriana de extratos da flora maranhense' (Nota: 10.0)",
                              fontsize=8.5, fontname="hebo", color=(0.1, 0.1, 0.1))

            pg.insert_textbox(pymupdf.Rect(40, 770, 555, 820),
                              f"Documento emitido eletronicamente pela Pró-Reitoria de Ensino da UFMA.\n"
                              f"Código de Autenticação: HIST-UFMA-2021-{INSCRICAO_NUM}-VALIDO\n"
                              f"Página {num_pg} de 3",
                              fontsize=8, fontname="helv", align=1, color=(0.4, 0.4, 0.4))
        else:
            pg.insert_text((270, 815), f"Página {num_pg} de 3", fontsize=8, fontname="helv")

    doc.save(destino / "Q12_historico_escolar_farmacia.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 6. Q13 - Currículo Lattes Oficial CNPq + Caderno de 10 Evidências Paginadas
# --------------------------------------------------------------------------------------------------
def gerar_q13_completo_e_evidencias_individuais(destino_dossie: Path, destino_evidencias: Path) -> None:
    doc_mestre = pymupdf.open()

    def topo_lattes(pg, num_pg, total_pgs=16):
        pg.draw_line(pymupdf.Point(40, 35), pymupdf.Point(555, 35), color=(0.7, 0.7, 0.7), width=0.5)
        pg.insert_text((40, 28), NOME_COMPLETO, fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
        pg.insert_text((450, 28), f"Página {num_pg} de {total_pgs}", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))

    # --- PARTE 1: Currículo Lattes Completo (Layout Oficial CNPq pkg_impcv.trata - 4 Páginas) ---
    p1 = doc_mestre.new_page(width=595, height=842)
    topo_lattes(p1, 1)

    p1.insert_text((40, 55), "Currículo do Sistema de Currículos Lattes (CNPq)", fontsize=11, fontname="hebo", color=(0.1, 0.2, 0.4))

    y = 75
    linhas_bio = [
        ("Nome", NOME_COMPLETO),
        ("Nome em citações bibliográficas", NOME_CITACAO_LATTES),
        ("Lattes iD", f"http://lattes.cnpq.br/{LATTES_ID}"),
        ("Orcid iD", f"https://orcid.org/{ORCID_ID}"),
        ("País de Nacionalidade", "Brasil"),
    ]
    for rotulo, valor in linhas_bio:
        p1.insert_text((40, y + 10), rotulo, fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
        p1.insert_textbox(pymupdf.Rect(180, y, 555, y + 25), valor, fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 22

    y += 10
    p1.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p1.insert_text((45, y + 13), "Resumo", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    resumo_txt = (
        f"Farmacêutico graduado pela Universidade Federal do Maranhão (UFMA). Especialista em Farmacologia Clínica "
        f"e Terapêutica pela Universidade Estadual do Maranhão (UEMA). Atua nas áreas de Ciências da Saúde e Biotecnologia, "
        f"com ênfase em Farmacognosia, Fitoquímica e Bioprospecção de Produtos Naturais e Ensaios Antimicrobianos. "
        f"Possui publicações em periódicos científicos internacionais e nacionais, apresentação de trabalhos em congressos, "
        f"conferências ministradas e experiência em comissão organizadora de eventos científicos. Atuou como pesquisador "
        f"em projetos de pesquisa financiados pela FAPEMA e CNPq. Linhas de interesse: Fitoterapia aplicada, formulação de "
        f"tecnologias educacionais e em saúde, e vigilância farmacológica na atenção primária."
    )
    p1.insert_textbox(pymupdf.Rect(40, y, 555, y + 100), resumo_txt, fontsize=8.5, fontname="helv")
    y += 105

    p1.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p1.insert_text((45, y + 13), "Formação acadêmica/titulação", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    formacoes = [
        ("2021 - 2023", "Especialização em Farmacologia Clínica e Terapêutica. (Carga Horária: 420h).\n"
                        "Universidade Estadual do Maranhão, UEMA, Brasil.\n"
                        "Título: Abordagem farmacoterapêutica em pacientes com doenças crônicas na atenção primária.\n"
                        "Orientador: Profa. Dra. Márcia Cristina Gonçalves Maciel."),
        ("2016 - 2020", "Graduação em Bacharelado em Farmácia.\n"
                        "Universidade Federal do Maranhão, UFMA, Brasil.\n"
                        "Título: Avaliação da atividade antibacteriana e perfil fitoquímico de espécies do Maranhão.\n"
                        "Orientador: Prof. Dr. Richard Pereira Dutra. Bolsista FAPEMA."),
    ]
    for anos, desc in formacoes:
        p1.insert_text((40, y + 10), anos, fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
        p1.insert_textbox(pymupdf.Rect(140, y, 555, y + 60), desc, fontsize=8.5, fontname="helv")
        y += 65

    # Página 2 Lattes
    p2 = doc_mestre.new_page(width=595, height=842)
    topo_lattes(p2, 2)
    y = 50

    p2.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p2.insert_text((45, y + 13), "Atuação Profissional", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    atuacoes = [
        ("2021 - Atual", "Hospital Universitário da Universidade Federal do Maranhão — HU-UFMA\n"
                         "Vínculo: Farmacêutico Clínico Hospitalar, Enquadramento funcional: Efetivo (40h semanais).\n"
                         "Atividades: Farmácia clínica, comissão de controle de infecção hospitalar e farmacovigilância."),
        ("2022 - Atual", "Faculdade de Educação e Ciências da Saúde\n"
                         "Vínculo: Professor Convidado / Instrutor, Carga horária: 10h semanais.\n"
                         "Atividades: Ministrante de disciplinas de Farmacologia e Assistência Farmacêutica."),
    ]
    for periodo, txt_at in atuacoes:
        p2.insert_text((40, y + 10), periodo, fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
        p2.insert_textbox(pymupdf.Rect(140, y, 555, y + 55), txt_at, fontsize=8.5, fontname="helv")
        y += 58

    p2.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p2.insert_text((45, y + 13), "Projetos de pesquisa", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p2.insert_text((40, y + 10), "2022 - Atual", fontsize=8, fontname="hebo", color=(0.2, 0.2, 0.2))
    p2_proj = (
        "Bioprospecção de Moléculas Bioativas e Desenvolvimento de Formulações Antimicrobianas Tópicas\n"
        "Descrição: Projeto focado no isolamento de metabólitos secundários e avaliação de atividade antimicrobiana "
        "frente a patógenos multirresistentes de interesse clínico.\n"
        "Situação: Em andamento; Natureza: Pesquisa.\n"
        "Alunos envolvidos: Graduação: (2) / Mestrado acadêmico: (1).\n"
        "Integrantes: Álvaro Antônio Bezerra dos Santos - Integrante / Márcia Cristina Gonçalves Maciel - Coordenadora."
    )
    p2.insert_textbox(pymupdf.Rect(140, y, 555, y + 95), p2_proj, fontsize=8.5, fontname="helv")
    y += 105

    p2.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p2.insert_text((45, y + 13), "Produções — Artigos completos publicados em periódicos", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    artigos = [
        ("1.", f"SANTOS, A. A. B.; DUTRA, R. P.; MACIEL, M. C. G. Avaliação da atividade antibacteriana e perfil fitoquímico "
               f"de extratos de plantas nativas do Maranhão frente a Staphylococcus aureus. REVISTA BRASILEIRA DE FARMACOGNOSIA, "
               f"v. 32, p. 115-124, 2023.\nDOI: 10.1007/s43450-023-00412-x"),
        ("2.", f"SANTOS, A. A. B.; FERREIRA, A. G. N.; LOPES, A. J. O. Bioprospecção de metabólitos secundários e ensaios de citotoxicidade "
               f"in vitro frente a linhagens celulares saudáveis e tumorais. BRAZILIAN JOURNAL OF HEALTH REVIEW, v. 6, p. 1420-1435, 2024.\n"
               f"DOI: 10.34119/bjhrv6n1-112"),
    ]
    for num, art_txt in artigos:
        p2.insert_text((40, y + 10), num, fontsize=8.5, fontname="hebo")
        p2.insert_textbox(pymupdf.Rect(60, y, 555, y + 60), art_txt, fontsize=8.5, fontname="helv")
        y += 65

    # Página 3 Lattes
    p3 = doc_mestre.new_page(width=595, height=842)
    topo_lattes(p3, 3)
    y = 50

    p3.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p3.insert_text((45, y + 13), "Trabalhos completos publicados em anais de congressos", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p3.insert_text((40, y + 10), "1.", fontsize=8.5, fontname="hebo")
    trab_anais = (
        f"SANTOS, A. A. B.; MACIEL, M. C. G. Potencial imunomodulador e antioxidante de extratos vegetais amazônicos. "
        f"In: XXVIII Congresso Brasileiro de Farmácia e Saúde Integrada, 2023, São Luís - MA. "
        f"Anais do XXVIII Congresso Brasileiro de Farmácia e Saúde, 2023. v. 1. p. 45-46. ISSN: 2318-1234."
    )
    p3.insert_textbox(pymupdf.Rect(60, y, 555, y + 55), trab_anais, fontsize=8.5, fontname="helv")
    y += 65

    p3.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p3.insert_text((45, y + 13), "Apresentações de Trabalho", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    apresentacoes = [
        ("1.", f"SANTOS, A. A. B. Manejo farmacoterapêutico racional de antimicrobianos na Atenção Primária à Saúde. "
               f"2024. (Apresentação de Trabalho/Conferência ou Palestra)."),
        ("2.", f"SANTOS, A. A. B.; DUTRA, R. P. Triagem fitoquímica e atividade bactericida de extratos polares da flora maranhense. "
               f"2023. (Apresentação de Trabalho/Comunicação Oral)."),
    ]
    for num, ap_txt in apresentacoes:
        p3.insert_text((40, y + 10), num, fontsize=8.5, fontname="hebo")
        p3.insert_textbox(pymupdf.Rect(60, y, 555, y + 45), ap_txt, fontsize=8.5, fontname="helv")
        y += 48

    p3.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p3.insert_text((45, y + 13), "Cursos de curta duração ministrados", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p3.insert_text((40, y + 10), "1.", fontsize=8.5, fontname="hebo")
    p3.insert_textbox(pymupdf.Rect(60, y, 555, y + 45),
                      f"SANTOS, A. A. B. Boas Práticas em Farmácia Hospitalar e Segurança do Paciente na Terapia Medicamentosa. "
                      f"2023. (Curso de curta duração ministrado/Extensão, Carga Horária: 20h).",
                      fontsize=8.5, fontname="helv")
    y += 50

    p3.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p3.insert_text((45, y + 13), "Organização de eventos, congressos, exposições e feiras", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p3.insert_text((40, y + 10), "1.", fontsize=8.5, fontname="hebo")
    p3.insert_textbox(pymupdf.Rect(60, y, 555, y + 45),
                      f"SANTOS, A. A. B.; FERREIRA, A. G. N. I Jornada Maranhense de Ciências Farmacêuticas e Biotecnologia em Saúde. "
                      f"2024. (Congresso, Organização de evento).",
                      fontsize=8.5, fontname="helv")
    y += 50

    # Página 4 Lattes: Bancas, Orientações e Participações
    p4 = doc_mestre.new_page(width=595, height=842)
    topo_lattes(p4, 4)
    y = 50

    p4.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p4.insert_text((45, y + 13), "Participação em bancas de trabalhos de conclusão", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p4.insert_text((40, y + 10), "1.", fontsize=8.5, fontname="hebo")
    p4.insert_textbox(pymupdf.Rect(60, y, 555, y + 45),
                      f"SANTOS, A. A. B.; DUTRA, R. P. Participação em banca examinadora de Graduação em Farmácia "
                      f"do aluno Lucas Silva Ramos, intitulado: Perfil Fitoquímico e Controle de Qualidade de Fitoterápicos. 2023. (UFMA).",
                      fontsize=8.5, fontname="helv")
    y += 50

    p4.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p4.insert_text((45, y + 13), "Orientações e supervisões concluídas", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    p4.insert_text((40, y + 10), "1.", fontsize=8.5, fontname="hebo")
    p4.insert_textbox(pymupdf.Rect(60, y, 555, y + 45),
                      f"SANTOS, A. A. B. Orientação de Trabalho de Conclusão de Curso (Graduação em Farmácia) "
                      f"do aluno Felipe Mendes da Silva, intitulado: Triagem de Metabólitos Secundários. 2023. (UFMA).",
                      fontsize=8.5, fontname="helv")
    y += 50

    p4.draw_rect(pymupdf.Rect(40, y, 555, y + 18), color=(0.3, 0.4, 0.6), fill=(0.92, 0.94, 0.98))
    p4.insert_text((45, y + 13), "Participação em eventos, congressos, exposições e feiras", fontsize=9, fontname="hebo", color=(0.1, 0.2, 0.5))
    y += 24

    participacoes = [
        ("1.", "XXVIII Congresso Brasileiro de Farmácia e Saúde Integrada, 2023. (Congresso)."),
        ("2.", "15º Simpósio Brasileiro de Bioprospecção e Produtos Naturais, 2022. (Simpósio)."),
    ]
    for num, pt_txt in participacoes:
        p4.insert_text((40, y + 10), num, fontsize=8.5, fontname="hebo")
        p4.insert_textbox(pymupdf.Rect(60, y, 555, y + 25), pt_txt, fontsize=8.5, fontname="helv")
        y += 28

    p4.insert_textbox(pymupdf.Rect(40, 720, 555, 780),
                      "Página gerada pelo Sistema Lattes em 20/10/2026 às 11:45:00.\n"
                      "Última atualização do currículo em 18/10/2026.\n"
                      f"Identificador Lattes Oficial: http://lattes.cnpq.br/{LATTES_ID}",
                      fontsize=8, fontname="helv", align=1, color=(0.5, 0.5, 0.5))

    # --- PARTE 2: Folha de Rosto e Sumário das Evidências (Página 5) ---
    p5 = doc_mestre.new_page(width=595, height=842)
    topo_lattes(p5, 5)
    p5.draw_rect(pymupdf.Rect(40, 60, 555, 120), color=(0.2, 0.4, 0.3), fill=(0.94, 0.97, 0.94), width=1.5)
    p5.insert_textbox(pymupdf.Rect(50, 75, 545, 115),
                      "PROGRAMA DE PÓS-GRADUAÇÃO EM SAÚDE E TECNOLOGIA — UFMA\n"
                      "CADERNO DE COMPROVAÇÕES E EVIDÊNCIAS ACADÊMICAS (ANEXO AO LATTES)\n"
                      f"Candidato: {NOME_UPPER}  |  Inscrição: {INSCRICAO_NUM}",
                      fontsize=10, fontname="hebo", align=1, color=(0.1, 0.3, 0.1))

    indice_txt = (
        "SUMÁRIO DAS 10 EVIDÊNCIAS COMPROBATÓRIAS PAGINADAS:\n\n"
        "• Evidência 01 (Pág. 06): Certificado de Apresentação de Trabalho Oral (XXVIII Cong. Bras. Farmácia)\n"
        "• Evidência 02 (Pág. 07): 1ª Página de Artigo Publicado em Periódico (Revista Brasileira de Farmacognosia)\n"
        "• Evidência 03 (Pág. 08): 1ª Página de Artigo Publicado em Periódico (Brazilian Journal of Health Review)\n"
        "• Evidência 04 (Pág. 09): Trabalho Publicado em Anais de Congresso (Anais do XXVIII CBFS)\n"
        "• Evidência 05 (Pág. 10): Declaração de Participação em Projeto de Pesquisa Institucional (UFMA / PPPGI)\n"
        "• Evidência 06 (Pág. 11): Certificado de Curso de Curta Duração Ministrado (PROEC / UFMA)\n"
        "• Evidência 07 (Pág. 12): Declaração de Membro da Comissão Organizadora de Evento Científico\n"
        "• Evidência 08 (Pág. 13): Declaração de Participação em Banca Examinadora de Graduação (UFMA)\n"
        "• Evidência 09 (Pág. 14): Declaração de Orientação de Conclusão de Curso Concluída (UFMA)\n"
        "• Evidência 10 (Pág. 15): Certificado de Participação em Evento como Ouvinte (Plataforma Even3)"
    )
    p5.insert_textbox(pymupdf.Rect(45, 140, 550, 520), indice_txt, fontsize=9.5, fontname="helv", color=(0.15, 0.15, 0.15))

    # Helper para salvar cada evidência individualmente
    def salvar_individual(doc_fonte, nome_arq):
        doc_indiv = pymupdf.open()
        doc_indiv.insert_pdf(doc_fonte, from_page=len(doc_fonte)-1, to_page=len(doc_fonte)-1)
        doc_indiv.save(destino_evidencias / nome_arq)
        doc_indiv.close()

    # --- PARTE 3: GERAÇÃO DAS 10 EVIDÊNCIAS ---

    # Evidência 01: Certificado de Apresentação de Trabalho Oral
    p6 = doc_mestre.new_page(width=842, height=595)  # Paisagem
    p6.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.15, 0.35, 0.25), width=2.5)
    p6.draw_rect(pymupdf.Rect(38, 38, 804, 557), color=(0.7, 0.6, 0.2), width=1.5)
    p6.insert_text((50, 22), f"COMPROVANTE: APRESENTAÇÃO DE TRABALHO ORAL", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p6.insert_textbox(pymupdf.Rect(50, 60, 792, 110),
                      "XXVIII CONGRESSO BRASILEIRO DE FARMÁCIA E SAÚDE INTEGRADA\nSOCIEDADE BRASILEIRA DE CIÊNCIAS FARMACÊUTICAS — SBCF",
                      fontsize=12, fontname="hebo", align=1, color=(0.1, 0.2, 0.3))
    p6.insert_textbox(pymupdf.Rect(50, 125, 792, 170), "CERTIFICADO DE APRESENTAÇÃO DE TRABALHO", fontsize=20, fontname="hebo", align=1, color=(0.15, 0.35, 0.25))
    cert_ap_txt = (
        f"Certificamos que {NOME_UPPER} apresentou a Comunicação Oral intitulada "
        f"\"Triagem fitoquímica e atividade bactericida de extratos polares da flora maranhense\", "
        f"de autoria de SANTOS, A. A. B.; DUTRA, R. P., no XXVIII Congresso Brasileiro de Farmácia e Saúde Integrada, "
        f"realizado no Centro de Convenções de São Luís - MA, no período de 14 a 17 de novembro de 2023, com carga horária total de 40 horas."
    )
    p6.insert_textbox(pymupdf.Rect(80, 190, 762, 330), cert_ap_txt, fontsize=13, fontname="helv", align=1, color=(0.1, 0.1, 0.1))
    p6.insert_text((100, 370), "São Luís - MA, 17 de novembro de 2023.", fontsize=11, fontname="helv")
    p6.draw_line(pymupdf.Point(120, 470), pymupdf.Point(400, 470), color=(0.3, 0.3, 0.3))
    p6.insert_textbox(pymupdf.Rect(120, 475, 400, 520), "Coordenação Científica do Congresso\nSBCF — Regional Maranhão", fontsize=9, fontname="hebo", align=1)
    p6.draw_line(pymupdf.Point(440, 470), pymupdf.Point(720, 470), color=(0.3, 0.3, 0.3))
    p6.insert_textbox(pymupdf.Rect(440, 475, 720, 520), "Presidente do XXVIII CBFS\nComissão Organizadora", fontsize=9, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "01_apresentacao_trabalho_oral.pdf")

    # Evidência 02: Artigo em Periódico 1 (Revista Brasileira de Farmacognosia)
    p7 = doc_mestre.new_page(width=595, height=842)
    p7.insert_text((40, 22), f"COMPROVANTE: ARTIGO EM PERIÓDICO (QUALIS A)", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p7.draw_rect(pymupdf.Rect(40, 40, 555, 95), color=(0.3, 0.3, 0.3), fill=(0.96, 0.96, 0.96))
    p7.insert_textbox(pymupdf.Rect(50, 48, 545, 90),
                      "Revista Brasileira de Farmacognosia — Brazilian Journal of Pharmacognosy\n"
                      "Volume 32, Issue 2, Pages 115-124, March 2023 | ISSN 0102-695X | e-ISSN 1981-528X\n"
                      "https://doi.org/10.1007/s43450-023-00412-x | Original Research Article",
                      fontsize=8.5, fontname="hebo", color=(0.2, 0.2, 0.2))
    art_titulo = "Avaliação da atividade antibacteriana e perfil fitoquímico de extratos de plantas nativas do Maranhão frente a Staphylococcus aureus"
    p7.insert_textbox(pymupdf.Rect(40, 115, 555, 175), art_titulo, fontsize=14, fontname="hebo", color=(0.1, 0.1, 0.3))
    art_autores = f"Álvaro Antônio Bezerra dos Santos 1*, Richard Pereira Dutra 1, Márcia Cristina Gonçalves Maciel 2"
    p7.insert_textbox(pymupdf.Rect(40, 180, 555, 205), art_autores, fontsize=9.5, fontname="hebo", color=(0.2, 0.2, 0.2))
    p7.insert_textbox(pymupdf.Rect(40, 205, 555, 245),
                      "1 Laboratório de Fitoquímica e Produtos Naturais, Universidade Federal do Maranhão, São Luís, MA, Brasil.\n"
                      "2 Laboratório de Imunologia Básica e Aplicada, Universidade Federal do Maranhão, São Luís, MA, Brasil.\n"
                      "* Autor correspondente: alvaro.santos@ufma.br",
                      fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    p7.draw_line(pymupdf.Point(40, 250), pymupdf.Point(555, 250), color=(0.7, 0.7, 0.7))
    p7.insert_text((40, 265), "ABSTRACT", fontsize=10, fontname="hebo")
    abstract_txt = (
        "Infections caused by multi-resistant bacterial strains represent a critical challenge to global public health. "
        "The aim of this work was to evaluate the in vitro antibacterial activity and chemical profile of polar extracts obtained "
        "from native medicinal species of the state of Maranhão against clinical isolates of Staphylococcus aureus (ATCC 25923). "
        "Phytochemical screening revealed high concentrations of flavonoids, condensed tannins, and triterpenes. The minimum "
        "inhibitory concentration (MIC) ranged between 62.5 and 250 μg/mL, demonstrating marked bactericidal potential. These "
        "results support the potential of these species as promising candidates for the formulation of topical herbal medicines."
    )
    p7.insert_textbox(pymupdf.Rect(40, 275, 555, 370), abstract_txt, fontsize=8.5, fontname="helv")
    p7.insert_textbox(pymupdf.Rect(40, 375, 555, 400), "Keywords: Phytochemistry; Antibacterial activity; Medicinal plants; Staphylococcus aureus; Flavonoids.", fontsize=8.5, fontname="hebo")
    salvar_individual(doc_mestre, "02_artigo_revista_farmacognosia.pdf")

    # Evidência 03: Artigo em Periódico 2 (Brazilian Journal of Health Review)
    p8 = doc_mestre.new_page(width=595, height=842)
    p8.insert_text((40, 22), f"COMPROVANTE: ARTIGO EM PERIÓDICO (BJHR)", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p8.draw_rect(pymupdf.Rect(40, 40, 555, 95), color=(0.3, 0.3, 0.3), fill=(0.96, 0.96, 0.96))
    p8.insert_textbox(pymupdf.Rect(50, 48, 545, 90),
                      "Brazilian Journal of Health Review — Curitiba, v. 6, n. 1, p. 1420-1435, jan./fev. 2024\n"
                      "ISSN 2595-6825 | DOI: 10.34119/bjhrv6n1-112\n"
                      "Artigo Original de Pesquisa em Saúde e Biotecnologia",
                      fontsize=8.5, fontname="hebo", color=(0.2, 0.2, 0.2))
    art2_titulo = "Bioprospecção de metabólitos secundários e ensaios de citotoxicidade in vitro frente a linhagens celulares saudáveis e tumorais"
    p8.insert_textbox(pymupdf.Rect(40, 115, 555, 175), art2_titulo, fontsize=13, fontname="hebo", color=(0.1, 0.1, 0.3))
    art2_autores = f"Álvaro Antônio Bezerra dos Santos 1, Adriana Gomes Nogueira Ferreira 2, Alberto Jorge Oliveira Lopes 3"
    p8.insert_textbox(pymupdf.Rect(40, 180, 555, 205), art2_autores, fontsize=9.5, fontname="hebo", color=(0.2, 0.2, 0.2))
    p8.insert_textbox(pymupdf.Rect(40, 205, 555, 245),
                      "1 Farmacêutico, Mestrando em Saúde e Tecnologia, Universidade Federal do Maranhão (UFMA).\n"
                      "2 Doutora em Biotecnologia em Saúde, Programa de Pós-Graduação em Saúde e Tecnologia (PPGST/UFMA).\n"
                      "3 Doutor em Química, Departamento de Farmácia, UFMA.",
                      fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    p8.draw_line(pymupdf.Point(40, 250), pymupdf.Point(555, 250), color=(0.7, 0.7, 0.7))
    p8.insert_text((40, 265), "RESUMO", fontsize=10, fontname="hebo")
    res_art2 = (
        "O presente estudo investigou a citotoxicidade e a seletividade de extratos vegetais enriquecidos em triterpenos frente "
        "a linhagens celulares tumorais (MCF-7 e HepG2) e mononucleares de sangue periférico humano (PBMC). O ensaio do MTT "
        "revelou índice de seletividade superior a 3.0 para a linhagem MCF-7, indicando baixa toxicidade para células não neoplásicas. "
        "Os dados evidenciam o potencial biotecnológico para o desenvolvimento de insumos farmacêuticos inovadores."
    )
    p8.insert_textbox(pymupdf.Rect(40, 275, 555, 360), res_art2, fontsize=8.5, fontname="helv")
    p8.insert_textbox(pymupdf.Rect(40, 365, 555, 390), "Palavras-chave: Bioprospecção; Citotoxicidade; Produtos naturais; Biotecnologia em saúde.", fontsize=8.5, fontname="hebo")
    salvar_individual(doc_mestre, "03_artigo_bjhr.pdf")

    # Evidência 04: Trabalho Publicado em Anais de Congresso (Resumo Expandido)
    p_anais = doc_mestre.new_page(width=595, height=842)
    p_anais.insert_text((40, 22), f"COMPROVANTE: TRABALHO EM ANAIS DE CONGRESSO", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p_anais.draw_rect(pymupdf.Rect(40, 40, 555, 95), color=(0.2, 0.35, 0.5), fill=(0.95, 0.97, 1.0))
    p_anais.insert_textbox(pymupdf.Rect(50, 48, 545, 90),
                           "XXVIII CONGRESSO BRASILEIRO DE FARMÁCIA E SAÚDE INTEGRADA\n"
                           "Anais do XXVIII CBFS — Volume 1, Páginas 45-46, Ano 2023 | ISSN 2318-1234\n"
                           "Trabalho Completo Publicado em Anais de Evento Nacional",
                           fontsize=8.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    p_anais.insert_textbox(pymupdf.Rect(40, 115, 555, 165),
                           "Potencial imunomodulador e antioxidante de extratos vegetais amazônicos",
                           fontsize=13, fontname="hebo", color=(0.1, 0.1, 0.3))
    p_anais.insert_textbox(pymupdf.Rect(40, 170, 555, 195),
                           f"Álvaro Antônio Bezerra dos Santos 1, Márcia Cristina Gonçalves Maciel 2",
                           fontsize=9.5, fontname="hebo", color=(0.2, 0.2, 0.2))
    p_anais.insert_textbox(pymupdf.Rect(40, 195, 555, 230),
                           "1 Graduado em Farmácia, UFMA. 2 Profa. Dra. Departamento de Imunologia, UFMA.",
                           fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
    p_anais.draw_line(pymupdf.Point(40, 235), pymupdf.Point(555, 235), color=(0.7, 0.7, 0.7))
    p_anais.insert_text((40, 250), "RESUMO EXPANDIDO", fontsize=10, fontname="hebo")
    txt_anais = (
        "Espécies vegetais da flora amazônica e do cerrado maranhense vêm sendo investigadas por suas propriedades farmacológicas. "
        "O presente trabalho publicado nos anais avaliou o extrato hidroalcoólico quanto à capacidade sequestradora de radicais livres "
        "(método DPPH) e modulação da produção de óxido nítrico por macrófagos murinos ativados por LPS. Constatou-se inibição de 68% "
        "na produção de óxido nítrico na concentração de 50 μg/mL sem comprometimento da viabilidade celular. Os achados comprovam ação "
        "anti-inflamatória promissora para o tratamento coadjuvante de processos inflamatórios cutâneos."
    )
    p_anais.insert_textbox(pymupdf.Rect(40, 265, 555, 380), txt_anais, fontsize=9, fontname="helv")
    p_anais.insert_textbox(pymupdf.Rect(40, 390, 555, 415), "Palavras-chave: Antioxidante; Imunomodulação; Fitoprodutos; Inflamação.", fontsize=8.5, fontname="hebo")
    salvar_individual(doc_mestre, "04_trabalho_anais_congresso.pdf")

    # Evidência 05: Declaração de Projeto de Pesquisa (UFMA/PPPGI)
    p9 = doc_mestre.new_page(width=595, height=842)
    p9.insert_text((40, 22), f"COMPROVANTE: PROJETO DE PESQUISA (PPPGI)", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p9.insert_textbox(pymupdf.Rect(40, 60, 555, 120),
                      "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\nPRÓ-REITORIA DE PESQUISA, PÓS-GRADUAÇÃO E INOVAÇÃO — PPPGI\nCOORDENAÇÃO DE PESQUISA E INICIAÇÃO CIENTÍFICA",
                      fontsize=10, fontname="hebo", align=1)
    p9.insert_textbox(pymupdf.Rect(40, 160, 555, 200), "DECLARAÇÃO DE PESQUISA", fontsize=16, fontname="hebo", align=1, color=(0.1, 0.3, 0.2))
    dec_proj = (
        f"Declaramos, para os devidos fins de comprovação acadêmica e científica de pesquisa, "
        f"que o Farmacêutico {NOME_UPPER}, portador do CPF nº {CPF_HIPOTETICO}, atua como PESQUISADOR INTEGRANTE "
        f"no projeto de pesquisa e desenvolvimento científico intitulado \"Bioprospecção de Moléculas Bioativas e Desenvolvimento de Formulações "
        f"Antimicrobianas Tópicas\", registrado sob o processo SIPAC nº 23115.008912/2022-44, sob a coordenação da "
        f"Profa. Dra. Márcia Cristina Gonçalves Maciel, com vigência no período de 01/03/2022 até a presente data, com dedicação de 12 horas semanais."
    )
    p9.insert_textbox(pymupdf.Rect(60, 220, 535, 360), dec_proj, fontsize=11, fontname="helv", align=0)
    p9.insert_text((60, 390), "São Luís - MA, 15 de setembro de 2026.", fontsize=11, fontname="helv")
    p9.draw_line(pymupdf.Point(140, 480), pymupdf.Point(450, 480), color=(0.3, 0.3, 0.3))
    p9.insert_textbox(pymupdf.Rect(140, 485, 450, 530),
                      "Pró-Reitoria de Pesquisa, Pós-Graduação e Inovação\nPPPGI / Universidade Federal do Maranhão",
                      fontsize=9.5, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "05_declaracao_projeto_pesquisa.pdf")

    # Evidência 06: Certificado de Curso de Curta Duração Ministrado (PROEC)
    p10 = doc_mestre.new_page(width=842, height=595)  # Paisagem
    p10.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.3, 0.2, 0.5), width=2.5)
    p10.draw_rect(pymupdf.Rect(38, 38, 804, 557), color=(0.7, 0.6, 0.2), width=1.5)
    p10.insert_text((50, 22), f"COMPROVANTE: CURSO DE CURTA DURAÇÃO MINISTRADO", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p10.insert_textbox(pymupdf.Rect(50, 60, 792, 110),
                       "UNIVERSIDADE FEDERAL DO MARANHÃO\nPRÓ-REITORIA DE EXTENSÃO E CULTURA — PROEC",
                       fontsize=12, fontname="hebo", align=1)
    p10.insert_textbox(pymupdf.Rect(50, 130, 792, 175), "CERTIFICADO DE MINISTRANTE DE CURSO", fontsize=20, fontname="hebo", align=1, color=(0.2, 0.1, 0.4))
    cert_curso = (
        f"Certificamos que {NOME_UPPER} ministrou o curso de extensão universitária intitulado "
        f"\"Boas Práticas em Farmácia Hospitalar e Segurança do Paciente na Terapia Medicamentosa\", "
        f"promovido pela Pró-Reitoria de Extensão da UFMA em parceria com o Hospital Universitário, "
        f"no período de 05 a 09 de junho de 2023, com carga horária total de 20 horas."
    )
    p10.insert_textbox(pymupdf.Rect(80, 195, 762, 330), cert_curso, fontsize=13, fontname="helv", align=1)
    p10.insert_text((100, 370), "São Luís - MA, 10 de junho de 2023.", fontsize=11, fontname="helv")
    p10.draw_line(pymupdf.Point(260, 470), pymupdf.Point(580, 470), color=(0.3, 0.3, 0.3))
    p10.insert_textbox(pymupdf.Rect(260, 475, 580, 520), "Pró-Reitoria de Extensão e Cultura — PROEC/UFMA\nRegistro nº EXT-2023-8871", fontsize=9, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "06_certificado_curso_ministrado.pdf")

    # Evidência 07: Declaração de Membro de Comissão Organizadora de Evento
    p11 = doc_mestre.new_page(width=595, height=842)
    p11.insert_text((40, 22), f"COMPROVANTE: ORGANIZAÇÃO DE EVENTO CIENTÍFICO", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p11.insert_textbox(pymupdf.Rect(40, 60, 555, 120),
                       "I JORNADA MARANHENSE DE CIÊNCIAS FARMACÊUTICAS E BIOTECNOLOGIA EM SAÚDE\n"
                       "ASSOCIAÇÃO DOS FARMACÊUTICOS DO MARANHÃO & UFMA",
                       fontsize=10.5, fontname="hebo", align=1)
    p11.insert_textbox(pymupdf.Rect(40, 160, 555, 200), "DECLARAÇÃO DE ORGANIZAÇÃO", fontsize=16, fontname="hebo", align=1, color=(0.1, 0.2, 0.4))
    dec_org = (
        f"Declaramos que o Farmacêutico {NOME_UPPER} integrou a COMISSÃO ORGANIZADORA CIENTÍFICA da "
        f"\"I Jornada Maranhense de Ciências Farmacêuticas e Biotecnologia em Saúde\", realizada nos dias "
        f"18 e 19 de outubro de 2024 no Centro Pedagógico Paulo Freire / UFMA, com carga horária total de 30 horas, "
        f"atuando na avaliação de trabalhos e coordenação de mesas-redondas."
    )
    p11.insert_textbox(pymupdf.Rect(60, 220, 535, 360), dec_org, fontsize=11, fontname="helv", align=0)
    p11.insert_text((60, 390), "São Luís - MA, 20 de outubro de 2024.", fontsize=11, fontname="helv")
    p11.draw_line(pymupdf.Point(140, 480), pymupdf.Point(450, 480), color=(0.3, 0.3, 0.3))
    p11.insert_textbox(pymupdf.Rect(140, 485, 450, 530),
                      "Coordenação Geral da I JMCFB\nComissão Organizadora Oficial",
                      fontsize=9.5, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "07_declaracao_organizacao_evento.pdf")

    # Evidência 08: Declaração de Membro de Banca Examinadora de Graduação
    p_banca = doc_mestre.new_page(width=595, height=842)
    p_banca.insert_text((40, 22), f"COMPROVANTE: PARTICIPAÇÃO EM BANCA EXAMINADORA", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p_banca.insert_textbox(pymupdf.Rect(40, 60, 555, 120),
                           "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\nDEPARTAMENTO DE FARMÁCIA — COORDENAÇÃO DE TCC",
                           fontsize=10.5, fontname="hebo", align=1)
    p_banca.insert_textbox(pymupdf.Rect(40, 160, 555, 200), "DECLARAÇÃO DE BANCA EXAMINADORA", fontsize=16, fontname="hebo", align=1, color=(0.2, 0.2, 0.4))
    dec_banca = (
        f"Declaramos, para os devidos fins de direito, que o Farmacêutico {NOME_UPPER} "
        f"participou como MEMBRO EXAMINADOR TITULAR da comissão julgadora da Banca Examinadora de Defesa de "
        f"Trabalho de Conclusão de Curso (Graduação em Farmácia) do estudante Lucas Silva Ramos, intitulado "
        f"\"Perfil Fitoquímico e Controle de Qualidade de Fitoterápicos Comercializados em São Luís - MA\", "
        f"realizada em 14 de dezembro de 2023, na Universidade Federal do Maranhão."
    )
    p_banca.insert_textbox(pymupdf.Rect(60, 220, 535, 360), dec_banca, fontsize=11, fontname="helv", align=0)
    p_banca.insert_text((60, 390), "São Luís - MA, 15 de dezembro de 2023.", fontsize=11, fontname="helv")
    p_banca.draw_line(pymupdf.Point(140, 480), pymupdf.Point(450, 480), color=(0.3, 0.3, 0.3))
    p_banca.insert_textbox(pymupdf.Rect(140, 485, 450, 530),
                           "Coordenação de TCC em Farmácia\nUniversidade Federal do Maranhão",
                           fontsize=9.5, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "08_declaracao_banca_examinadora.pdf")

    # Evidência 09: Declaração de Orientação de Conclusão de Curso Concluída
    p_orient = doc_mestre.new_page(width=595, height=842)
    p_orient.insert_text((40, 22), f"COMPROVANTE: ORIENTAÇÃO ACADÊMICA CONCLUÍDA", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p_orient.insert_textbox(pymupdf.Rect(40, 60, 555, 120),
                            "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\nCURSO DE GRADUAÇÃO EM FARMÁCIA — COORDENAÇÃO DE CURSO",
                            fontsize=10.5, fontname="hebo", align=1)
    p_orient.insert_textbox(pymupdf.Rect(40, 160, 555, 200), "DECLARAÇÃO DE ORIENTAÇÃO", fontsize=16, fontname="hebo", align=1, color=(0.2, 0.3, 0.2))
    dec_orient = (
        f"Declaramos que o Farmacêutico {NOME_UPPER} atuou como ORIENTADOR PRINCIPAL do Trabalho de Conclusão de Curso "
        f"de Graduação em Farmácia do discente Felipe Mendes da Silva, intitulado \"Triagem de Metabólitos Secundários e "
        f"Atividade Antioxidante de Espécies do Bioma Maranhense\", concluído e aprovado com nota máxima no segundo semestre "
        f"letivo de 2023 na Universidade Federal do Maranhão."
    )
    p_orient.insert_textbox(pymupdf.Rect(60, 220, 535, 360), dec_orient, fontsize=11, fontname="helv", align=0)
    p_orient.insert_text((60, 390), "São Luís - MA, 20 de dezembro de 2023.", fontsize=11, fontname="helv")
    p_orient.draw_line(pymupdf.Point(140, 480), pymupdf.Point(450, 480), color=(0.3, 0.3, 0.3))
    p_orient.insert_textbox(pymupdf.Rect(140, 485, 450, 530),
                            "Coordenação do Curso de Farmácia\nUFMA / CCBS",
                            fontsize=9.5, fontname="hebo", align=1)
    salvar_individual(doc_mestre, "09_declaracao_orientacao_concluida.pdf")

    # Evidência 10: Certificado de Participação em Evento como Ouvinte (Even3)
    p_part = doc_mestre.new_page(width=842, height=595)  # Paisagem
    p_part.draw_rect(pymupdf.Rect(30, 30, 812, 565), color=(0.1, 0.3, 0.5), width=2.5)
    p_part.draw_rect(pymupdf.Rect(38, 38, 804, 557), color=(0.6, 0.6, 0.6), width=1.0)
    p_part.insert_text((50, 22), f"COMPROVANTE: PARTICIPAÇÃO EM EVENTO (OUVINTE)", fontsize=8, fontname="hebo", color=(0.4, 0.4, 0.4))
    p_part.insert_textbox(pymupdf.Rect(50, 60, 792, 110),
                          "XXVIII CONGRESSO BRASILEIRO DE FARMÁCIA E SAÚDE INTEGRADA\nPLATAFORMA DE GESTÃO DE EVENTOS EVEN3",
                          fontsize=12, fontname="hebo", align=1, color=(0.1, 0.2, 0.4))
    p_part.insert_textbox(pymupdf.Rect(50, 130, 792, 175), "CERTIFICADO DE PARTICIPAÇÃO", fontsize=20, fontname="hebo", align=1, color=(0.1, 0.3, 0.5))
    cert_part = (
        f"Certificamos que {NOME_UPPER} participou do XXVIII Congresso Brasileiro de Farmácia e Saúde Integrada, "
        f"promovido pela Sociedade Brasileira de Ciências Farmacêuticas, realizado em São Luís - MA, no período de "
        f"14 a 17 de novembro de 2023, na qualidade de OUVINTE / CONGRESSISTA, totalizando 40 horas de atividades."
    )
    p_part.insert_textbox(pymupdf.Rect(80, 195, 762, 330), cert_part, fontsize=13, fontname="helv", align=1)
    p_part.insert_text((100, 370), "São Luís - MA, 17 de novembro de 2023.", fontsize=11, fontname="helv")
    p_part.draw_line(pymupdf.Point(260, 460), pymupdf.Point(580, 460), color=(0.3, 0.3, 0.3))
    p_part.insert_textbox(pymupdf.Rect(260, 465, 580, 500), "Comissão Organizadora Oficial do XXVIII CBFS", fontsize=9, fontname="hebo", align=1)
    p_part.insert_textbox(pymupdf.Rect(50, 520, 792, 550),
                          "Código de autenticidade Even3: 9847120.2023.ALVARO.VALIDO — Acesse https://www.even3.com.br/documentos",
                          fontsize=8, fontname="helv", align=1, color=(0.4, 0.4, 0.4))
    salvar_individual(doc_mestre, "10_certificado_participacao_ouvinte.pdf")

    # Salva o dossiê unificado mestre Q13
    doc_mestre.save(destino_dossie / "Q13_curriculo_lattes_comprovacoes.pdf")
    doc_mestre.close()
    p_part.insert_textbox(pymupdf.Rect(50, 60, 792, 110),
                          "XXVIII CONGRESSO BRASILEIRO DE FARMÁCIA E SAÚDE INTEGRADA\nPLATAFORMA DE GESTÃO DE EVENTOS EVEN3",
                          fontsize=12, fontname="hebo", align=1, color=(0.1, 0.2, 0.4))
    p_part.insert_textbox(pymupdf.Rect(50, 130, 792, 175), "CERTIFICADO DE PARTICIPAÇÃO", fontsize=20, fontname="hebo", align=1, color=(0.1, 0.3, 0.5))
    cert_part = (
        f"Certificamos que {NOME_UPPER} participou do XXVIII Congresso Brasileiro de Farmácia e Saúde Integrada, "
        f"promovido pela Sociedade Brasileira de Ciências Farmacêuticas, realizado em São Luís - MA, no período de "
        f"14 a 17 de novembro de 2023, na qualidade de OUVINTE / CONGRESSISTA, totalizando 40 horas de atividades."
    )
    p_part.insert_textbox(pymupdf.Rect(80, 195, 762, 330), cert_part, fontsize=13, fontname="helv", align=1)
    p_part.insert_text((100, 370), "São Luís - MA, 17 de novembro de 2023.", fontsize=11, fontname="helv")
    p_part.draw_line(pymupdf.Point(260, 460), pymupdf.Point(580, 460), color=(0.3, 0.3, 0.3))
    p_part.insert_textbox(pymupdf.Rect(260, 465, 580, 500), "Comissão Organizadora Oficial do XXVIII CBFS", fontsize=9, fontname="hebo", align=1)
    p_part.insert_textbox(pymupdf.Rect(50, 520, 792, 550),
                          "Código de autenticidade Even3: 9847120.2023.ALVARO.VALIDO — Acesse https://www.even3.com.br/documentos",
                          fontsize=8, fontname="helv", align=1, color=(0.4, 0.4, 0.4))
    salvar_individual(doc_mestre, "10_certificado_participacao_ouvinte.pdf")

    # Salva o dossiê unificado mestre Q13
    doc_mestre.save(destino_dossie / "Q13_curriculo_lattes_comprovacoes.pdf")
    doc_mestre.close()


# --------------------------------------------------------------------------------------------------
# 7. Q14 - Anteprojeto de Pesquisa PPGST
# --------------------------------------------------------------------------------------------------
def gerar_q14_anteprojeto(destino: Path) -> None:
    doc = pymupdf.open()
    p1 = doc.new_page(width=595, height=842)
    p1.insert_textbox(pymupdf.Rect(40, 50, 555, 120),
                      "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\n"
                      "CENTRO DE CIÊNCIAS BIOLÓGICAS E DA SAÚDE — CCBS\n"
                      "PROGRAMA DE PÓS-GRADUAÇÃO EM SAÚDE E TECNOLOGIA — PPGST\n"
                      "MESTRADO PROFISSIONAL EM SAÚDE E TECNOLOGIA\n"
                      "EDITAL PPGST Nº 04/2026",
                      fontsize=10, fontname="hebo", align=1)

    p1.insert_textbox(pymupdf.Rect(40, 180, 555, 230),
                      f"LINHA DE PESQUISA: SAÚDE E SOCIEDADE\n"
                      f"ORIENTADORA SUGERIDA: PROFA. DRA. MÁRCIA CRISTINA GONÇALVES MACIEL\n"
                      f"ÁREA TEMÁTICA: BIOPROSPECÇÃO, FITOTERAPIA E VIGILÂNCIA EM SAÚDE",
                      fontsize=9, fontname="hebo", align=1, color=(0.2, 0.2, 0.4))

    p1.insert_textbox(pymupdf.Rect(40, 270, 555, 360),
                      TITULO_PROJETO,
                      fontsize=14, fontname="hebo", align=1, color=(0.1, 0.1, 0.3))

    p1.insert_textbox(pymupdf.Rect(40, 400, 555, 460),
                      f"Candidato: {NOME_UPPER}\n"
                      f"Número de Inscrição: {INSCRICAO_NUM}\n"
                      f"Formação: Bacharel em Farmácia",
                      fontsize=10.5, fontname="hebo", align=1)

    p1.insert_textbox(pymupdf.Rect(40, 750, 555, 800),
                      "SÃO LUÍS — MA\nOUTUBRO / 2026",
                      fontsize=10, fontname="hebo", align=1)

    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((40, 40), "1. RESUMO", fontsize=11, fontname="hebo")
    res_txt = (
        "O aumento progressivo de infecções causadas por microrganismos resistentes a antimicrobianos convencionais "
        "impõe a busca urgente por novas alternativas terapêuticas eficazes e acessíveis à Atenção Primária à Saúde. "
        "O bioma maranhense abriga vasta biodiversidade vegetal com histórico de uso etnofarmacológico comprovado. "
        "Este projeto tem como objetivo desenvolver uma formulação fitoterápica antimicrobiana padronizada a partir "
        "de extratos de espécies vegetais do cerrado maranhense, acompanhada da elaboração de uma cartilha técnica "
        "educativa para os profissionais de saúde da atenção básica no Sistema Único de Saúde (SUS).\n\n"
        "Palavras-chave: Fitoterapia; Atenção Primária; Produtos Naturais; Tecnologia em Saúde; Antimicrobianos."
    )
    p2.insert_textbox(pymupdf.Rect(40, 55, 555, 185), res_txt, fontsize=9.5, fontname="helv")

    p2.insert_text((40, 205), "2. INTRODUÇÃO E JUSTIFICATIVA", fontsize=11, fontname="hebo")
    intro_txt = (
        "A resistência bacteriana a antimicrobianos (RAM) constitui uma das dez maiores ameaças globais à saúde pública "
        "segundo a Organização Mundial da Saúde (OMS). No âmbito da Atenção Básica no Maranhão, infecções de pele, tecidos "
        "moles e do trato respiratório frequentemente evoluem com falhas terapêuticas devido ao uso empírico e irracional de "
        "antibacterianos.\n\n"
        "Nesse cenário, a Política Nacional de Práticas Integrativas e Complementares (PNPIC) e a Política Nacional de Plantas "
        "Medicinais e Fitoterápicos incentivam o aproveitamento sustentável da flora nativa como recurso terapêutico no SUS. "
        "O desenvolvimento de um fitoproduto padronizado, seguro e de baixo custo, aliado a diretrizes clínicas para as equipes "
        "da Estratégia Saúde da Família (ESF), atende diretamente às prioridades tecnológicas e assistenciais do Estado do Maranhão."
    )
    p2.insert_textbox(pymupdf.Rect(40, 220, 555, 450), intro_txt, fontsize=9.5, fontname="helv")

    p2.insert_text((40, 470), "3. OBJETIVOS", fontsize=11, fontname="hebo")
    obj_txt = (
        "3.1. Objetivo Geral:\n"
        "Desenvolver e caracterizar formulação fitoterapêutica tópica com atividade antimicrobiana a partir de espécies "
        "nativas do Maranhão e estruturar tecnologia educacional para sua aplicação no âmbito da Atenção Primária à Saúde.\n\n"
        "3.2. Objetivos Específicos:\n"
        "• Obter e quantificar o perfil fitoquímico (flavonoides e fenólicos totais) dos extratos vegetais;\n"
        "• Determinar a Concentração Inibitória Mínima (CIM) frente a cepas clínicas de S. aureus e P. aeruginosa;\n"
        "• Formular gel fitoterápico com testes de estabilidade físico-química preliminar;\n"
        "• Elaborar cartilha digital e fluxograma de apoio à prescrição farmacêutica na ESF."
    )
    p2.insert_textbox(pymupdf.Rect(40, 485, 555, 760), obj_txt, fontsize=9.5, fontname="helv")

    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((40, 40), "4. METODOLOGIA", fontsize=11, fontname="hebo")
    metod_txt = (
        "4.1. Coleta e Preparação Botânica: Espécimes vegetais devidamente autorizados pelo SISGEN serão coletados, "
        "identificados no Herbário da UFMA e secos em estufa de ar circulante (40°C).\n\n"
        "4.2. Extração e Fracionamento: Obtenção do extrato hidroalcoólico por maceração dinâmica e fracionamento "
        "por partição líquido-líquido com solventes de polaridade crescente (hexano, acetato de etila e n-butanol).\n\n"
        "4.3. Caracterização Química: Quantificação espectrofotométrica de fenólicos e flavonoides totais e cromatografia "
        "em camada delgada (CCD) acoplada a HPLC-DAD.\n\n"
        "4.4. Ensaios Antimicrobianos: Microdiluição em caldo (norma CLSI M07-A10) em placas de 96 poços com controle positivo "
        "(ciprofloxacino) e leitura de densidade óptica e revelação por resazurina.\n\n"
        "4.5. Desenvolvimento do Produto Técnico: Manipulação de hidrogel de carbopol a 1,0% incorporando a fração ativa, "
        "com controle de pH, viscosidade e espalhabilidade.\n\n"
        "4.6. Tecnologia Educacional: Criação de cartilha e guia rápido com validação por painel de juízes especialistas "
        "utilizando o Índice de Validade de Conteúdo (IVC >= 0.80)."
    )
    p3.insert_textbox(pymupdf.Rect(40, 55, 555, 450), metod_txt, fontsize=9.5, fontname="helv")

    p4 = doc.new_page(width=595, height=842)
    p4.insert_text((40, 40), "5. CRONOGRAMA DE EXECUÇÃO (24 MESES)", fontsize=11, fontname="hebo")
    p4.draw_rect(pymupdf.Rect(40, 60, 555, 80), color=(0.3, 0.3, 0.3), fill=(0.92, 0.92, 0.92))
    p4.insert_text((45, 73), "ATIVIDADE / ETAPA", fontsize=8, fontname="hebo")
    p4.insert_text((270, 73), "B1", fontsize=7.5, fontname="hebo")
    p4.insert_text((315, 73), "B2", fontsize=7.5, fontname="hebo")
    p4.insert_text((360, 73), "B3", fontsize=7.5, fontname="hebo")
    p4.insert_text((405, 73), "B4", fontsize=7.5, fontname="hebo")
    p4.insert_text((450, 73), "B5", fontsize=7.5, fontname="hebo")
    p4.insert_text((495, 73), "B6", fontsize=7.5, fontname="hebo")
    p4.insert_text((535, 73), "B7-12", fontsize=7.5, fontname="hebo")

    etapas = [
        ("Revisão de literatura e disciplinas PPGST", [1, 1, 0, 0, 0, 0, 0]),
        ("Coleta botânica e obtenção dos extratos", [0, 1, 1, 0, 0, 0, 0]),
        ("Ensaios antimicrobianos in vitro (CIM/CBM)", [0, 0, 1, 1, 0, 0, 0]),
        ("Desenvolvimento da formulação do gel", [0, 0, 0, 1, 1, 0, 0]),
        ("Exame de Qualificação do Mestrado", [0, 0, 0, 0, 1, 0, 0]),
        ("Elaboração da tecnologia educacional/cartilha", [0, 0, 0, 0, 1, 1, 0]),
        ("Redação da Dissertação e Defesa Final", [0, 0, 0, 0, 0, 1, 1]),
    ]
    y_cr = 85
    for desc, marcacoes in etapas:
        p4.insert_text((45, y_cr + 12), desc, fontsize=8, fontname="helv")
        xs = [272, 317, 362, 407, 452, 497, 542]
        for idx, m in enumerate(marcacoes):
            if m:
                p4.insert_text((xs[idx], y_cr + 12), "X", fontsize=8, fontname="hebo", color=(0.1, 0.4, 0.2))
        y_cr += 18

    p5 = doc.new_page(width=595, height=842)
    p5.insert_text((40, 40), "6. REFERÊNCIAS BIBLIOGRÁFICAS", fontsize=11, fontname="hebo")
    refs_txt = (
        "BRASIL. Ministério da Saúde. Secretaria de Atenção Primária à Saúde. Guia prático de manejo de feridas e infecções "
        "na Atenção Primária. Brasília: Ministério da Saúde, 2023.\n\n"
        "DUTRA, R. P. et al. Antimicrobial and antioxidant activities of plants from the Brazilian Cerrado. "
        "Journal of Ethnopharmacology, v. 194, p. 892-901, 2020.\n\n"
        "MACIEL, M. C. G. et al. Phytochemical screening and biological applications of natural extracts in inflammatory conditions. "
        "Phytomedicine, v. 45, p. 112-120, 2021.\n\n"
        "SANTOS, A. A. B.; DUTRA, R. P.; MACIEL, M. C. G. Avaliação da atividade antibacteriana e perfil fitoquímico "
        "de extratos de plantas nativas do Maranhão frente a Staphylococcus aureus. Revista Brasileira de Farmacognosia, "
        "v. 32, p. 115-124, 2023.\n\n"
        "WORLD HEALTH ORGANIZATION - WHO. Global action plan on antimicrobial resistance. Geneva: World Health Organization, 2022."
    )
    p5.insert_textbox(pymupdf.Rect(40, 60, 555, 450), refs_txt, fontsize=9.5, fontname="helv")

    doc.save(destino / "Q14_anteprojeto_mestrado_ppgst.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 8. Q15 - Comprovante de Pagamento PagTesouro / GRU
# --------------------------------------------------------------------------------------------------
def gerar_q15_gru(destino: Path) -> None:
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)

    pg.draw_rect(pymupdf.Rect(40, 40, 555, 110), color=(0.1, 0.45, 0.25), fill=(0.94, 0.98, 0.95), width=1.5)
    pg.insert_textbox(pymupdf.Rect(50, 48, 545, 105),
                      "GOVERNO FEDERAL — MINISTÉRIO DA FAZENDA\nSECRETARIA DO TESOURO NACIONAL — PORTAL PAGTESOURO\n"
                      "COMPROVANTE DE PAGAMENTO DE GRU (GUIA DE RECOLHIMENTO DA UNIÃO)",
                      fontsize=10, fontname="hebo", align=1, color=(0.1, 0.35, 0.2))

    pg.insert_textbox(pymupdf.Rect(40, 130, 555, 170),
                      "PAGAMENTO REALIZADO COM SUCESSO VIA PIX / LIQUIDAÇÃO INSTANTÂNEA",
                      fontsize=12, fontname="hebo", align=1, color=(0.1, 0.5, 0.2))

    pg.draw_rect(pymupdf.Rect(40, 180, 555, 520), color=(0.4, 0.4, 0.4), width=1)

    y = 200
    linhas_gru = [
        ("Órgão Favorecido:", "UNIVERSIDADE FEDERAL DO MARANHÃO — UFMA"),
        ("Código Favorecido / Unidade:", "154041 / Gestão: 15258"),
        ("Código de Recolhimento:", "28830-6 (Serviços Administrativos e Inscrições em Concursos)"),
        ("Número de Referência:", f"202604{INSCRICAO_NUM}"),
        ("Competência:", "10/2026"),
        ("Contribuinte / Pagador:", NOME_UPPER),
        ("CPF do Pagador:", CPF_HIPOTETICO),
        ("Valor Principal:", "R$ 100,00"),
        ("Descontos / Deduções:", "R$ 0,00"),
        ("Valor Total Pago:", "R$ 100,00"),
        ("Data e Hora do Pagamento:", "05/10/2026 às 14:12:35 BRT"),
        ("Instituição Liquidante:", "001 - BANCO DO BRASIL S.A. / PAGTESOURO"),
        ("ID da Transação E2E:", f"E15404120261005141200{INSCRICAO_NUM}998877"),
        ("Autenticação Bancária:", "B3.C4.D5.E6.F7.A8.20.26.VAL-OK"),
    ]

    for rotulo, val in linhas_gru:
        pg.insert_text((55, y), rotulo, fontsize=8.5, fontname="hebo", color=(0.3, 0.3, 0.3))
        pg.insert_text((220, y), val, fontsize=9, fontname="hebo" if "Valor Total" in rotulo or "Contribuinte" in rotulo else "helv")
        y += 22

    pg.insert_textbox(pymupdf.Rect(40, 540, 555, 600),
                      "Atenção: Guarde este comprovante. A confirmação da inscrição ocorre de forma automática "
                      "junto ao Sistema Integrado de Gestão de Atividades Acadêmicas (SIGAA/UFMA) após a liquidação pelo Tesouro Nacional.",
                      fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4))

    doc.save(destino / "Q15_comprovante_pagamento_gru.pdf")
    doc.close()


# --------------------------------------------------------------------------------------------------
# 9. Q17 - Termo de Autorização e Declaração de Veracidade (Anexo IV)
# --------------------------------------------------------------------------------------------------
def gerar_q17_termo(destino: Path) -> None:
    doc = pymupdf.open()
    pg = doc.new_page(width=595, height=842)

    pg.insert_textbox(pymupdf.Rect(40, 40, 555, 95),
                      "PROGRAMA DE PÓS-GRADUAÇÃO EM SAÚDE E TECNOLOGIA — PPGST\nUNIVERSIDADE FEDERAL DO MARANHÃO — UFMA\n"
                      "EDITAL PPGST Nº 04/2026 — ANEXO IV\nTERMO DE AUTORIZAÇÃO DE USO DE ÁUDIO-IMAGEM E DECLARAÇÃO DE VERACIDADE",
                      fontsize=10, fontname="hebo", align=1)

    pg.draw_line(pymupdf.Point(40, 105), pymupdf.Point(555, 105), color=(0.3, 0.3, 0.3), width=1)

    termo_txt = (
        f"Eu, {NOME_UPPER}, de profissão Farmacêutico, portador(a) da Carteira de Identidade (RG) nº {RG_HIPOTETICO}, "
        f"inscrito(a) no Cadastro de Pessoas Físicas (CPF) sob nº {CPF_HIPOTETICO}, residente e domiciliado(a) na "
        f"cidade de São Luís - MA, candidato(a) inscrito(a) sob o número {INSCRICAO_NUM} no Processo Seletivo do Mestrado "
        f"em Saúde e Tecnologia (Edital PPGST nº 04/2026):\n\n"
        f"1. DECLARO, sob as penas da lei (art. 299 do Código Penal Brasileiro - Falsidade Ideológica), a inteira veracidade, "
        f"autenticidade e exatidão de todos os dados informados no formulário de inscrição e de todos os documentos comprobatórios "
        f"apresentados em anexo (diploma, histórico escolar, currículo Lattes e certificados).\n\n"
        f"2. AUTORIZO expressamente a Universidade Federal do Maranhão (UFMA) e a Comissão de Seleção do PPGST a gravar em áudio "
        f"e vídeo a sessão pública de defesa do anteprojeto de pesquisa e arguição oral da etapa seletiva, bem como a utilização "
        f"desses registros exclusivamente para fins de avaliação acadêmica, fiscalização institucional e eventual julgamento de recursos.\n\n"
        f"3. DECLARO ter pleno conhecimento de todas as normas, critérios de avaliação, barema de pontuação e cronograma "
        f"estabelecidos no Edital PPGST nº 04/2026, com os quais manifesto minha integral e irrevogável concordância."
    )
    pg.insert_textbox(pymupdf.Rect(40, 125, 555, 450), termo_txt, fontsize=10, fontname="helv")

    pg.insert_text((60, 480), "São Luís - MA, 10 de outubro de 2026.", fontsize=10.5, fontname="helv")

    pg.draw_rect(pymupdf.Rect(60, 520, 535, 610), color=(0.2, 0.4, 0.6), fill=(0.95, 0.97, 1.0))
    pg.insert_textbox(pymupdf.Rect(75, 530, 520, 600),
                      f"Documento assinado digitalmente\n"
                      f"Nome: {NOME_UPPER}\n"
                      f"CPF: {CPF_HIPOTETICO}\n"
                      f"Data: 10/10/2026 15:42:10 BRT  |  Certificado Digital ICP-Brasil / gov.br Prata\n"
                      f"Hash SHA-256 de Validação: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                      fontsize=8.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    doc.save(destino / "Q17_termo_autorizacao_audio_imagem.pdf")
    doc.close()


def main():
    print("=" * 70)
    print(" GERADOR DE BASE DE DOCUMENTOS E EVIDÊNCIAS — LATTESFÁCIL")
    print("=" * 70)
    destino, pasta_evid = criar_diretorios()
    print(f"Diretório Candidato : {destino}")
    print(f"Pasta Evidências    : {pasta_evid}")
    print(f"Autor/Pesquisador   : {NOME_COMPLETO}")
    print(f"Citações Lattes     : {NOME_CITACAO_LATTES}")
    print(f"Inscrição           : {INSCRICAO_NUM}")
    print("-" * 70)

    print("-> Gerando 00001.docx (Ficha de Avaliação da Banca)...")
    gerar_docx(destino)

    print("-> Gerando Q9 (Carteira de Identidade Nacional)...")
    gerar_q9_identidade(destino)

    print("-> Gerando Q10 (Certidão de Quitação Eleitoral TSE)...")
    gerar_q10_eleitoral(destino)

    print("-> Gerando Q11 (Diploma de Bacharel em Farmácia)...")
    gerar_q11_diploma(destino)

    print("-> Gerando Q12 (Histórico Escolar de Graduação)...")
    gerar_q12_historico(destino)

    print("-> Gerando Q13 (Currículo Lattes + 10 Evidências Paginadas)...")
    gerar_q13_completo_e_evidencias_individuais(destino, pasta_evid)

    print("-> Gerando Q14 (Anteprojeto de Pesquisa PPGST)...")
    gerar_q14_anteprojeto(destino)

    print("-> Gerando Q15 (Comprovante de Pagamento PagTesouro GRU)...")
    gerar_q15_gru(destino)

    print("-> Gerando Q17 (Termo de Autorização e Declaração Anexo IV)...")
    gerar_q17_termo(destino)

    # Copia o candidato para o diretório de testes/curriculos
    cand_em_curriculos = Path(__file__).resolve().parent / "curriculos e modelos" / "1_INSCRIÇÕES" / destino.name
    cand_em_curriculos.mkdir(parents=True, exist_ok=True)
    for arq in destino.iterdir():
        if arq.is_file():
            shutil.copy2(arq, cand_em_curriculos / arq.name)

    print("-" * 70)
    print("[SUCESSO] Base e Evidências geradas com sucesso!")
    print(f"Total de arquivos no Dossiê ({destino.name}): {len(list(destino.iterdir()))}")
    print(f"Total de Evidências Individuais geradas: {len(list(pasta_evid.iterdir()))}")
    print("\nEvidências Individuais disponíveis em tests/base_documentos_teste/evidencias_individuais/:")
    for f in sorted(pasta_evid.iterdir()):
        tam_kb = round(f.stat().st_size / 1024, 1)
        print(f"  * {f.name:<45} ({tam_kb:>5.1f} KB)")
    print("=" * 70)


if __name__ == "__main__":
    main()
