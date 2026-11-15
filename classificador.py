"""Reconhece que tipo de evidência é um documento e a que item do Lattes ele pertence.

Protótipo isolado (não está ligado ao servidor nem à tela). Devolve candidatos ranqueados, cada um com o motivo em
linguagem simples, e uma decisão:

- "avancar":   um candidato claramente à frente -> o sistema segue sozinho e só mostra o que entendeu;
- "confirmar": poucos candidatos plausíveis -> mostra até 3 opções para o usuário escolher;
- "escolher":  nada convincente -> abre o escolhedor guiado (ver docs/fluxo-intuitivo.md).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any


def norm(text: str) -> str:
    base = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", base).lower()


@dataclass
class Item:
    id: str
    secao: str
    item: str  # nome do item no menu do Lattes
    grupo: str  # pergunta em linguagem simples (usada no escolhedor guiado)
    regras: list[tuple[str, float, str]] = field(default_factory=list)  # (regex, peso, motivo)
    implementado: bool = False  # já temos leitor + preenchimento para este item?
    exemplo: str = ""


# Cada regra: padrão no texto normalizado (sem acento, minúsculo), peso e o motivo mostrado ao usuário.
ITENS: list[Item] = [
    Item("anais", "Produções", "Trabalhos publicados em anais de eventos", "Publiquei um resumo ou trabalho em anais", [
        (r"palavras-?chave|keywords", 2.5, "tem palavras-chave"),
        (r"\bresumo\b|\babstract\b", 1.5, "tem resumo"),
        (r"\banais\b|caderno de resumos|proceedings", 2.5, "cita anais ou caderno de resumos"),
        (r"congresso|simposio|seminario|jornada|encontro", 0.8, "cita um evento"),
        (r"\bintroducao\b|\bmetodologia\b|\bresultados\b", 0.7, "tem estrutura de resumo científico"),
        (r"certificamos|certificado|declaramos|declaro", -3.0, "parece certificado, não resumo"),
    ], True, "Resumo do SEMIC 2024"),
    Item("apresentacao", "Produções", "Apresentação de trabalho e palestra", "Apresentei um trabalho, pôster ou palestra", [
        (r"certificamos|certificado|declaramos", 1.2, "é um certificado/declaração"),
        (r"apresentacao oral|apresentacao de poster|comunicacao oral|\bposter\b|formato de apresentacao|apresentado por|apresentou", 3.5, "diz que o trabalho foi apresentado"),
        (r"trabalho (cientifico )?intitulado|trabalho (cientifico )?(com o )?titulo", 2.0, "cita o título do trabalho"),
        (r"palestra|conferencia proferida|proferiu", 2.5, "cita palestra proferida"),
    ], True, "Certificado COIMAMA 2024"),
    Item("participacao_evento", "Eventos", "Participação em eventos, congressos, exposições, feiras e olimpíadas", "Participei de um evento como ouvinte", [
        (r"participou (do|da|de|dos|das)|participacao (no|na|do|da)|na qualidade de (participante|ouvinte)|\bouvinte\b|\bparticipante\b", 3.0, "diz que participou do evento"),
        (r"congresso|simposio|jornada|seminario|encontro|semana|workshop|feira|olimpiada", 1.0, "cita um evento"),
        (r"carga horaria", 0.5, "tem carga horária"),
        (r"apresentou|apresentacao oral|\bposter\b|ministrou|palestrante", -2.0, "houve apresentação, não só participação"),
    ], False, "Certificado de participação no congresso"),
    Item("organizacao_evento", "Eventos", "Organização de eventos, congressos, exposições, feiras e olimpíadas", "Organizei ou coordenei um evento", [
        (r"(integrou|integrante|membro|atuou como|participou como|coordenou|presidiu|presidente)( d[ao]s?)?( a| da)? comissao (organizadora|cientifica)|organizou o|coordenou o (evento|congresso|simposio|seminario)|coordenacao geral", 4.0, "foi da comissão organizadora"),
        (r"congresso|simposio|jornada|seminario|encontro|semana|workshop", 1.0, "cita um evento"),
    ], False, "Certificado da comissão organizadora"),
    Item("artigo", "Produções", "Artigos completos publicados em periódicos", "Publiquei um artigo em revista científica", [
        (r"\bdoi\b|10\.\d{4,9}/", 3.0, "tem DOI"),
        (r"\bjournal\b|\brevista\b|periodico", 1.0, "cita revista"),
        (r"\babstract\b|\bresumo\b", 0.8, "tem resumo"),
        (r"received|accepted|recebido em|aceito em|published", 1.2, "tem datas de recebimento/aceite"),
        (r"\bvolume\b|\bissn\b|\bvol\.", 1.2, "tem volume ou ISSN"),
        (r"certificamos|certificado|declaramos", -2.5, "parece certificado, não artigo"),
    ], True, "DOI ou PDF de artigo"),
    Item("artigo_aceito", "Produções", "Artigos aceitos para publicação", "Meu artigo foi aceito, mas ainda não saiu", [
        (r"carta de aceite|aceito para publicacao|accepted for publication|temos o prazer de informar.{0,80}aceit", 4.5, "é uma carta/comunicado de aceite"),
    ], False, "Carta de aceite da revista"),
    Item("livro_capitulo", "Produções", "Livros e capítulos", "Publiquei um livro ou capítulo de livro", [
        (r"\bisbn\b", 3.0, "tem ISBN"),
        (r"capitulo|organizador(es)?|\beditora\b|ficha catalografica", 1.5, "cita capítulo/editora"),
    ], False, "Ficha catalográfica do livro"),
    Item("orientacao_concluida", "Orientações", "Orientações e supervisões concluídas", "Orientei um trabalho (mestrado, doutorado, TCC, IC)", [
        (r"orientou|orientador(a)?\b|orientacao d[oa]|orientando", 2.5, "cita orientador/orientando"),
        (r"defendeu|defesa|aprovad[oa]|concluiu|concluida", 1.5, "diz que foi defendido/concluído"),
        (r"disserta[c]ao|\btese\b|\btcc\b|trabalho de conclusao|iniciacao cientifica|monografia|pibic", 2.0, "cita o tipo de trabalho orientado"),
        (r"em andamento|em curso|atualmente orienta", -3.0, "está em andamento"),
        (r"banca examinadora|membro da banca|examinador", -1.5, "fala de banca"),
        (r"certificamos|declaramos que .{0,60}(apresentou|participou)", -1.0, "parece certificado de evento"),
    ], True, "Declaração de orientação de TCC"),
    Item("orientacao_andamento", "Orientações", "Orientações e supervisões em andamento", "Oriento um trabalho que ainda não terminou", [
        (r"orientou|orientador(a)?\b|orientacao d[oa]|orientando", 2.0, "cita orientador/orientando"),
        (r"em andamento|em curso|atualmente orienta|vigencia da bolsa", 3.5, "diz que está em andamento"),
        (r"disserta[c]ao|\btese\b|\btcc\b|trabalho de conclusao|iniciacao cientifica|monografia|pibic", 1.5, "cita o tipo de trabalho orientado"),
    ], True, "Declaração de IC em andamento"),
    Item("banca", "Bancas", "Participação em bancas de trabalhos de conclusão", "Participei de uma banca examinadora", [
        (r"banca examinadora|membro da banca|participou da banca|comissao julgadora|examinador(a)?|avaliador(a)? externo", 4.0, "diz que integrou a banca"),
        (r"defesa|qualificacao", 1.0, "cita defesa ou qualificação"),
        (r"disserta[c]ao|\btese\b|\btcc\b|monografia|trabalho de conclusao", 1.0, "cita o trabalho avaliado"),
    ], False, "Declaração de participação em banca"),
    Item("curso_ministrado", "Produções", "Curso de curta duração ministrado", "Ministrei um curso, minicurso ou oficina", [
        (r"ministrou|ministrante|docente do curso|instrutor(a)?|professor(a)? do curso|oficina ministrada", 4.0, "diz que ministrou o curso"),
        (r"\bcurso\b|minicurso|oficina|capacitacao", 1.0, "cita curso"),
        (r"carga horaria", 0.8, "tem carga horária"),
    ], False, "Certificado de ministrante"),
    Item("formacao_complementar", "Formação", "Formação complementar", "Fiz um curso (como aluno)", [
        (r"concluiu o curso|participou do curso|cursou|carga horaria de \d+|certificado de conclusao do curso|curso de (extensao|aperfeicoamento|capacitacao|atualizacao)", 3.0, "diz que concluiu/participou do curso"),
        (r"carga horaria", 1.5, "tem carga horária"),
        (r"ministrou|ministrante|palestrante|instrutor", -3.5, "ele ministrou, não cursou"),
        (r"congresso|simposio|jornada", -1.0, "parece evento, não curso"),
    ], False, "Certificado de curso de extensão"),
    Item("formacao_academica", "Formação", "Formação acadêmica/titulação", "Concluí uma graduação, especialização, mestrado ou doutorado", [
        (r"\bdiploma\b|colacao de grau|conferiu o grau|historico escolar|grau de (mestre|doutor|bacharel|especialista|licenciado)|certificado de (conclusao|especializacao|pos-graduacao)", 4.0, "é diploma/histórico/certificado de titulação"),
        (r"bacharel|licenciatura|especializacao|mestrado|doutorado", 1.0, "cita o nível de formação"),
    ], False, "Diploma de graduação"),
    Item("atuacao_profissional", "Atuação", "Atuação profissional", "Trabalho ou trabalhei em uma instituição", [
        (r"declaracao de vinculo|portaria de nomeacao|contrato de trabalho|admissao|exerce o cargo|lotado|matricula funcional|vinculo empregaticio|servidor(a)? (publico|efetivo)", 3.5, "comprova vínculo de trabalho"),
        (r"\bcargo\b|\bfuncao\b|regime de trabalho|carga horaria semanal", 1.2, "cita cargo/função"),
    ], False, "Declaração de vínculo"),
    Item("revisor_periodico", "Atuação", "Revisor de periódico", "Fui revisor/parecerista de uma revista", [
        (r"revisor(a)?|reviewer|parecerista|peer review|avaliacao de manuscrito|referee", 4.0, "diz que foi revisor/parecerista"),
        (r"periodico|journal|revista", 1.0, "cita revista"),
    ], False, "Certificado de revisor"),
    Item("corpo_editorial", "Atuação", "Membro de corpo editorial", "Sou do corpo editorial de uma revista", [
        (r"corpo editorial|editor associado|editor-chefe|editor chefe|editorial board|conselho editorial", 4.5, "cita corpo/conselho editorial"),
    ], False, "Portaria de editor"),
    Item("patente", "Patentes e Registros", "Patente", "Depositei ou obtive uma patente", [
        (r"carta patente|pedido de patente|\bpatente\b|\binpi\b|modelo de utilidade|privilegio de invencao", 4.0, "cita patente/INPI"),
    ], False, "Carta patente"),
    Item("software_registro", "Patentes e Registros", "Programa de Computador Registrado", "Registrei um programa de computador", [
        (r"registro de programa de computador|certificado de registro.{0,40}programa|programa de computador", 4.5, "cita registro de programa de computador"),
    ], False, "Certificado de registro de software"),
    Item("premio", "Dados gerais", "Prêmios e títulos", "Recebi um prêmio ou título", [
        (r"\bpremio\b|premiacao|mencao honrosa|melhor trabalho|homenagem|titulo de (cidadao|doutor honoris)", 3.5, "cita prêmio/menção honrosa"),
    ], False, "Certificado de melhor trabalho"),
    Item("projeto", "Projetos", "Projetos de pesquisa", "Participei de um projeto (pesquisa, extensão, ensino)", [
        (r"coordenador(a)? do projeto|integrante do projeto|membro da equipe do projeto|projeto de (pesquisa|extensao|ensino|desenvolvimento)|plano de trabalho", 3.5, "cita participação em projeto"),
        (r"edital|fomento|bolsa|fapema|cnpq|capes|fapesp", 0.8, "cita agência/edital"),
    ], False, "Declaração de participação em projeto"),
    Item("idioma", "Dados gerais", "Idiomas", "Tenho certificado de idioma", [
        (r"proficiencia|toefl|ielts|cambridge|\bdelf\b|\bdele\b|\bcefr\b|nivel [abc][12]", 4.5, "é prova/certificado de idioma"),
    ], False, "Certificado de proficiência"),
    Item("licenca", "Dados gerais", "Licença Maternidade, Paternidade e Adoção", "Tive licença maternidade, paternidade ou adoção", [
        (r"licenca[- ](maternidade|paternidade)|licenca[- ]adocao|adocao", 4.5, "cita licença maternidade/paternidade/adoção"),
    ], False, "Portaria de licença"),
    Item("relatorio_tecnico", "Produções", "Trabalhos técnicos", "Fiz um parecer, relatório ou consultoria", [
        (r"relatorio tecnico|parecer tecnico|laudo|consultoria|assessoria", 3.5, "cita relatório/parecer/consultoria"),
    ], False, "Parecer técnico"),
]
INDICE = {i.id: i for i in ITENS}

LIMIAR_AVANCAR = 0.70   # confiança mínima do 1º candidato para seguir sozinho
MARGEM_AVANCAR = 0.25   # vantagem sobre o 2º
LIMIAR_CONFIRMAR = 0.35  # abaixo disso nada é plausível


def _pontuar(item: Item, texto: str) -> tuple[float, list[str], float]:
    pontos, motivos = 0.0, []
    for padrao, peso, motivo in item.regras:
        if re.search(padrao, texto):
            pontos += peso
            if peso > 0:
                motivos.append(motivo)
    maximo = sum(p for _, p, _ in item.regras if p > 0)
    return pontos, motivos if pontos > 0 else [], maximo


def classificar(texto: str, nome_arquivo: str = "", paginas: int = 0, resumos_no_pdf: int = 0) -> dict[str, Any]:
    """Classifica o texto de uma evidência. `resumos_no_pdf` = quantas vezes 'Keywords:' aparece (detecta caderno)."""
    t = norm(texto)
    nome = norm(nome_arquivo)
    if len(t.strip()) < 40:
        return {"decisao": "escolher", "motivo_decisao": "não consegui ler texto no arquivo (pode ser imagem escaneada)",
                "candidatos": [], "dica": "Tente um PDF com texto ou use a escolha guiada."}
    if paginas > 12 and resumos_no_pdf >= 10:
        return {"decisao": "avancar", "motivo_decisao": "é um caderno com vários resumos", "caderno": True,
                "candidatos": [{"id": "caderno", "item": "Caderno de anais (vários resumos)", "secao": "Produções", "confianca": 0.98,
                                "motivos": [f"{resumos_no_pdf} resumos com palavras-chave em {paginas} páginas"], "implementado": True}]}
    cands = []
    for it in ITENS:
        pontos, motivos, maximo = _pontuar(it, t + " " + nome)
        if pontos <= 0:
            continue
        # confiança: parte do máximo possível, limitada para não superar 1; exige ao menos uma regra forte
        conf = pontos / (0.75 * maximo)
        fortes = sum(1 for padrao, peso, _ in it.regras if peso >= 2.5 and re.search(padrao, t + " " + nome))
        conf = min(conf, 0.95 if fortes >= 1 else 0.6)
        if len(motivos) == 1:
            conf = min(conf, 0.78)  # uma única pista isolada nunca passa de "provável"
        cands.append({"id": it.id, "item": it.item, "secao": it.secao, "grupo": it.grupo, "pontos": round(pontos, 2),
                      "confianca": round(conf, 2), "motivos": motivos, "implementado": it.implementado})
    cands.sort(key=lambda c: (-c["confianca"], -c["pontos"]))
    cands = [c for c in cands if c["confianca"] >= LIMIAR_CONFIRMAR][:4]
    if not cands:
        return {"decisao": "escolher", "motivo_decisao": "nada no documento aponta claramente para um item", "candidatos": []}
    top = cands[0]
    margem = top["confianca"] - (cands[1]["confianca"] if len(cands) > 1 else 0)
    if top["confianca"] >= LIMIAR_AVANCAR and margem >= MARGEM_AVANCAR:
        decisao, why = "avancar", "um item se destaca"
    else:
        decisao, why = "confirmar", "há mais de uma possibilidade plausível"
    # um documento pode gerar mais de um registro (ex.: certificado de apresentação também comprova a participação)
    relacionados = []
    if top["id"] == "apresentacao":
        relacionados.append({"id": "participacao_evento", "motivo": "o mesmo certificado também comprova a participação no evento"})
    return {"decisao": decisao, "motivo_decisao": why, "candidatos": cands, "tambem_pode_gerar": relacionados}
