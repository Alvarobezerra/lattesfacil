"""Sugestões das grades: participantes da banca, palavras-chave e áreas a partir do título (nomes fictícios).
Uso: python tests/teste_sugestoes.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from itens import sugestoes as S  # noqa: E402
from itens.leitores import ler  # noqa: E402

falhas = 0


def checa(nome, cond, extra=""):
    global falhas
    print(("OK   " if cond else "FALHA ") + nome + (f" — {extra}" if extra and not cond else ""))
    falhas += 0 if cond else 1


DECL = """UNIVERSIDADE FEDERAL DO EXEMPLO
DECLARAÇÃO
Declaramos que a Profa. Dra. HELENA MORAES TAVARES participou como Examinadora Externa à Instituição
da Comissão de Defesa de Tese de Doutorado de CARLA MENDES SOUZA com a tese intitulada:
Extrato aquoso de folhas de Exemplaria teste atenua a inflamação hepática induzida por tetracloreto em ratos sem alterar a
função renal, no Programa de Pós-Graduação em Farmacologia da Universidade Federal do Exemplo, em sessão pública realizada
no dia 18 de dezembro de 2024.
Membros da Banca
ANA LUCIA PEREIRA DE ALMEIDA (UFEX - Orientadora)
JOSE ROBERTO DA SILVA (UFEX - Examinador Interno)
HELENA MORAES TAVARES (UEOUTRA - Examinadora Externa à Instituição)
MARCOS ANTONIO LIMA (INST - Examinador Externo à Instituição)
à Instituição)
Prof. Dr. PAULO ROBERTO COORDENADOR
Coordenador do Programa de Pós-Graduação em Farmacologia - UFEX
Documento assinado eletronicamente por PAULO ROBERTO COORDENADOR, em 16/01/2025.
"""

m = S.participantes_da_banca(DECL)
checa("participantes: 4 membros, sem o coordenador da assinatura nem o candidato", [x["nome"] for x in m] == ["Ana Lucia Pereira de Almeida", "Jose Roberto da Silva", "Helena Moraes Tavares", "Marcos Antonio Lima"], m)
checa("participante: separa instituição e papel", m[2]["instituicao"] == "UEOUTRA" and m[2]["papel"].startswith("Examinadora Externa"), m[2])
checa("citação no padrão bibliográfico", S.como_citado("Ana Lucia Pereira de Almeida") == "ALMEIDA, A. L. P.", S.como_citado("Ana Lucia Pereira de Almeida"))
checa("sem cabeçalho e sem papel entre parênteses: não inventa participantes", S.participantes_da_banca("Joao Silva (Fortaleza)\nMaria Souza (2024)") == [])
checa("sem cabeçalho, com papel entre parênteses: aceita", len(S.participantes_da_banca("Joao Silva Santos (UFC - Presidente)\nMaria Souza Lima (UFC - Membro)")) == 2)

pc = S.palavras_chave("Extrato aquoso de folhas de Exemplaria teste atenua a inflamação hepática induzida por tetracloreto em ratos sem alterar a função renal")
checa("palavras-chave: frases do título, sem verbos nem conectivos", "Inflamação hepática" in pc and not any(p.lower().startswith(("atenua", "induzida")) for p in pc) and len(pc) <= 5, pc)
checa("palavras-chave: limite de 50 caracteres cada", all(len(p) <= 50 for p in pc))
checa("palavras-chave: título vazio não gera nada", S.palavras_chave("") == [])

ar = S.areas_do_texto("Extrato de folhas atenua inflamação", "Programa de Pós-Graduação em Farmacologia")
checa("áreas: nome exato do catálogo, curso pesa mais", ar and ar[0] == "Farmacologia", ar)
checa("áreas: sem correspondência não inventa", S.areas_do_texto("Xyzzy qwerty", "") == [])

r = ler("banca", DECL, "Helena Moraes Tavares")
v = r["valores"]
checa("banca: leitor devolve as 3 grades", len(v.get("grade:autores", [])) == 4 and v.get("grade:palavras_chave") and v.get("grade:areas"), list(v))
checa("banca: avisos pedem conferência", any("Participantes da banca" in n for n in r["notas"]) and any("sugeridas a partir do título" in n for n in r["notas"]), r["notas"])
checa("banca: título já em minúsculas não gera aviso de CAIXA ALTA", not any("CAIXA ALTA" in n for n in r["notas"]), r["notas"])
checa("outro item sem grade de autores não recebe participantes", "grade:autores" not in ler("participacao_evento", "Certificamos que Maria participou do evento X.", "Maria")["valores"])

# patente: depositante, inventores e situação (documento fictício no formato do comprovante do INPI)
_pat = ("Número do Processo: BR 10 2099 000001 0 Dados do Depositante (71) Depositante 1 de 1 Nome ou Razão Social: UNIVERSIDADE FEDERAL DE EXEMPLO "
        "Tipo de Pessoa: Pessoa Jurídica CPF/CNPJ: 00000000000000 26/02/2029 Dados do Pedido Natureza Patente: 10 - Patente de Invenção (PI) "
        "Título da Invenção ou Modelo de Utilidade (54): BEBIDA PROBIÓTICA E SEU PROCESSO Resumo: Bebida fermentada. "
        "Dados do Inventor (72) Inventor 1 de 2 Nome: MARIA DE SOUSA LIMA CPF: 00000000000 Inventor 2 de 2 Nome: JOSÉ DA SILVA CPF: 00000000001")
rp = ler("patente", _pat, "Maria de Sousa Lima")
vp = rp["valores"]
checa("patente: número do registro sem espaços (limite do Lattes)", vp.get("f_cod_reg") == "BR1020990000010", vp.get("f_cod_reg"))
checa("patente: depositante instituição", vp.get("grade:titulares_inst") == ["Universidade Federal de Exemplo"] and "grade:titulares_pessoa" not in vp, vp.get("grade:titulares_inst"))
checa("patente: inventores com citação", [a["nome"] for a in vp.get("grade:autores", [])] == ["Maria de Sousa Lima", "José da Silva"] and vp["grade:autores"][0]["citacao"] == "LIMA, M. S.", vp.get("grade:autores"))
checa("patente: situação de depósito com data", vp.get("grade:situacoes") == [{"nome": "Depósito", "citacao": "26/02/2029"}], vp.get("grade:situacoes"))

print(f"{falhas} falha(s)")
sys.exit(1 if falhas else 0)
