"""Reconhece que tipo de evidência é um documento e a que item do Lattes ele pertence.

Protótipo isolado (não está ligado ao servidor nem à tela). Devolve candidatos ranqueados, cada um com o motivo em
linguagem simples, e uma decisão:

- "avancar":   um candidato claramente à frente -> o sistema segue sozinho e só mostra o que entendeu;
- "confirmar": poucos candidatos plausíveis -> mostra até 3 opções para o usuário escolher;
- "escolher":  nada convincente -> abre o escolhedor guiado (ver docs/fluxo-intuitivo.md).
"""

from __future__ import annotations

import difflib
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
        # (uma regra só: somar regras positivas novas aumenta o teto e derruba a confiança de quem já pontuava)
        (r"titulo dos anais|anais d[oe] .{0,60}(congresso|evento|simposio)|como citar.{0,200}\banais\b|\(anais\s*[-–]?\s*issn|anais\s*[-–]\s*issn|publicacao d[oe] (artigo|resumo|trabalho).{0,250}\banais\b", 3.0, "trabalho nos anais (título dos anais, como citar ou certificado de publicação)"),
        (r"congresso|simposio|seminario|jornada|encontro", 0.8, "cita um evento"),
        (r"\bintroducao\b|\bmetodologia\b|\bresultados\b", 0.7, "tem estrutura de resumo científico"),
        (r"certificamos|certificado|declaramos|declaro", -3.0, "parece certificado, não resumo"),
    ], True, "Resumo do SEMIC 2024"),
    Item("apresentacao", "Produções", "Apresentação de trabalho e palestra", "Apresentei um trabalho, pôster ou palestra", [
        (r"certificamos|certificado|declaramos", 1.2, "é um certificado/declaração"),
        (r"apresentacao oral|apresentacao de poster|comunicacao oral|\bposter\b|formato de apresentacao|apresentado por|apresentou|foi (submetido e )?apresentado|apresentado no evento|atividade apresentacao de trabalho|apresentacao de trabalhos? cientificos?|modalidade .{0,3}banner|banner digital", 3.5, "diz que o trabalho foi apresentado"),
        (r"trabalho (cientifico )?intitulado|trabalho (cientifico )?(com o )?titulo", 2.0, "cita o título do trabalho"),
        (r"palestra|conferencia proferida|proferiu", 2.5, "cita palestra proferida"),
    ], True, "Certificado COIMAMA 2024"),
    Item("participacao_evento", "Eventos", "Participação em eventos, congressos, exposições, feiras e olimpíadas", "Participei de um evento como ouvinte", [
        (r"(?:participa[cç][aã]o|participou)(?:\s+(?:com\s+[êe]xito|com\s+sucesso|com\s+aproveitamento|ativamente|como\s+\w+|na\s+qualidade\s+de\s+\w+))?\s*(?:do|da|de|no|na|dos|das|em)?\s*(?:[\w.\-]{1,12}\s+){0,3}?(?:evento|congresso|simposio|jornada|seminario|encontro|semana|workshop|feira|forum|reuniao|olimpiada)", 3.5, "cita participação expressa em evento"),
        (r"participou(?:\s+(?:com\s+[êe]xito|com\s+sucesso|com\s+aproveitamento|ativamente))?\s+(?:do|da|de|no|na|dos|das|em)|participa[cç][aã]o\s+(?:no|na|do|da|em)|na qualidade de (participante|ouvinte)|\bouvinte\b|\bparticipante\b", 2.5, "diz que participou do evento"),
        (r"evento|congresso|simposio|jornada|seminario|encontro|semana|workshop|feira|olimpiada|reuniao anual", 1.0, "cita um evento"),
        (r"carga horaria", 0.5, "tem carga horária"),
        (r"participou d[oa](?:\(a\))? monitoria|monitoria academica|exerceu (a )?monitoria|atuou como monitor(a)?|monitoria (da|na|de) disciplina", -4.0, "é monitoria (atuação profissional), não evento"),
        (r"comissao (organizadora|cientifica)|organizacao do evento|historico escolar|colacao de grau|denominacao das ucs", -3.0, "é organização de evento ou documento acadêmico, não só participação"),
        (r"apresentou|apresentacao oral|\bposter\b|ministrou|palestrante|atestado de restauro|conservacao do painel|apresentacao de trabalhos? cientificos?|atividade apresentacao de trabalho|foi (submetido e )?apresentado|banner digital|participou,? como organizador", -2.0, "houve apresentação, organização ou restauro, não só participação"),
    ], True, "Certificado de participação no congresso"),
    Item("organizacao_evento", "Eventos", "Organização de eventos, congressos, exposições, feiras e olimpíadas", "Organizei ou coordenei um evento", [
        (r"(integrou|integrante|membro|atuou como|participou como|participou|coordenou|presidiu|presidente)( d[ao]s?)?( a| da)? comissao (organizadora|cientifica)|(participou|atuou|atuacao),? como (organizador|organizadora|coordenador|coordenadora)(\(a\))?|organizou o|coordenou o (evento|congresso|simposio|seminario)|coordenacao geral|participou (com exito )?(da|na) organizacao d[oae]|organizacao do evento", 4.0, "foi da comissão organizadora"),
        (r"congresso|simposio|jornada|seminario|encontro|semana|workshop", 1.0, "cita um evento"),
    ], False, "Certificado da comissão organizadora"),
    Item("artigo", "Produções", "Artigos completos publicados em periódicos", "Publiquei um artigo em revista científica", [
        (r"\bdoi\b|10\.\d{4,9}/|d[o0][il1]\s*:|[a-z]*doi\.or|revista[^\n]{0,90}\bv\.?\s*\d+[^\n]{0,12}\bn\.?\s*\d+[^\n]{0,12}\bp\.?\s*\d+\W{1,2}\d+|revista[^\n]{0,90}\bn\.?\s*\d+\s*,?\s*p\.?\s*\d+\W{1,2}\d+|certificado de publicacao|declaracao de publicacao|publicou o artigo|publicaram (no|o) (artigo)?|artigo intitulado", 4.0, "tem DOI ou é comprovante de publicação de artigo em periódico"),
        (r"\bjournal\b|\brevista\b|periodico", 1.0, "cita revista"),
        (r"\babstract\b|\bresumo\b", 0.8, "tem resumo"),
        (r"received|accepted|recebido em|aceito em|published", 1.2, "tem datas de recebimento/aceite"),
        (r"\bvolume\b|\bissn\b|\bvol\.", 1.2, "tem volume ou ISSN"),
        (r"\(anais\s*[-–]?\s*issn|anais\s*[-–]\s*issn", -3.0, "é publicação em anais de evento, não em periódico"),
        (r"(?<!de )certificamos que (apresentou|participou)|declaramos que (apresentou|participou)", -2.5, "parece certificado de apresentação/participação, não artigo"),
        (r"carta de aceite|aceito para publicacao|accepted for publication|we are pleased to inform", -3.0, "é carta de aceite, ainda não publicado"),
    ], True, "DOI ou PDF de artigo"),
    Item("artigo_aceito", "Produções", "Artigos aceitos para publicação", "Meu artigo foi aceito, mas ainda não saiu", [
        (r"carta de aceite|aceito para publicacao|accepted for publication|temos o prazer de informar.{0,80}aceit", 4.5, "é uma carta/comunicado de aceite"),
    ], False, "Carta de aceite da revista"),
    Item("livro_capitulo", "Produções", "Livros e capítulos", "Publiquei um livro ou capítulo de livro", [
        (r"\bisbn\b", 3.0, "tem ISBN"),
        (r"capitulo|organizador(es)?|\beditora\b(?! associad)|ficha catalografica", 1.5, "cita capítulo/editora"),
        (r"\bprefacio\b|\bposfacio\b|traduziu|declaracao de traducao|declaracao de editoracao|atuou como editor|\bpartitura\b", -3.5, "é prefácio, tradução, editoração ou partitura"),
    ], False, "Ficha catalográfica do livro"),
    Item("outra_producao_bibliografica", "Produções", "Outra produção bibliográfica", "Publiquei outra produção bibliográfica (resenha, boletim)", [
        (r"declaracao de publicacao|\bresenha\b|\bboletim\b", 4.0, "cita resenha/boletim"),
    ], True, "Declaração de publicação de resenha"),
    Item("prefacio_posfacio", "Produções", "Prefácio, posfácio", "Escrevi prefácio, posfácio ou apresentação de livro", [
        (r"\bprefacio\b|\bposfacio\b|redacao do prefacio|redacao do posfacio|carta do organizador", 4.5, "cita prefácio ou posfácio"),
        (r"\blivro\b|\bisbn\b|\beditora\b", 1.0, "cita livro/editora"),
    ], True, "Carta de agradecimento por prefácio"),
    Item("texto_jornal_revista", "Produções", "Textos em jornais de notícias/revistas", "Publiquei texto em jornal ou revista de divulgação", [
        (r"declaracao da redacao|artigo de divulgacao|no jornal\b|caderno\s+[a-z]+", 4.5, "cita texto em jornal/revista de notícias"),
    ], True, "Declaração de publicação em jornal"),
    Item("traducao", "Produções", "Tradução", "Traduzi um livro, artigo ou outra obra", [
        (r"declaracao de traducao|\btraduziu\b|traducao d[eo] (livro|artigo|obra)", 4.5, "cita tradução de obra"),
    ], True, "Declaração de tradução"),
    Item("editoracao", "Produções", "Editoração", "Atuei na editoração de livro, periódico ou anais", [
        (r"declaracao de editoracao|atuou como editor(a)? d[oa] (livro|periodico|anais|catalogo)|\beditoracao\b", 4.5, "cita editoração"),
    ], True, "Declaração de editoração"),
    Item("orientacao_concluida", "Orientações", "Orientações e supervisões concluídas", "Orientei um trabalho (mestrado, doutorado, TCC, IC)", [
        (r"orientou|orientador(a)?\b|orientacao d[oa]|orientando", 2.5, "cita orientador/orientando"),
        (r"defendeu|defesa|aprovad[oa]|concluiu|concluida", 1.5, "diz que foi defendido/concluído"),
        (r"disserta[c]ao|\btese\b|\btcc\b|trabalho de conclusao|iniciacao cientifica|monografia|pibic", 2.0, "cita o tipo de trabalho orientado"),
        (r"em andamento|em curso|atualmente orienta", -3.0, "está em andamento"),
        (r"banca examinadora|membro da banca", -1.5, "fala de banca"),
        (r"historico (escolar|academico)|componentes curriculares cursados", -3.0, "é histórico: 'orientador' e 'trabalho de conclusão' aparecem só como disciplinas e docentes"),
        # (a ata de defesa fica ambígua entre banca e orientação, por decisão do teste_classificador; esta regra nunca disparava no commit
        # anterior por causa de um backspace no padrão, e o comportamento da ata é mantido)
        (r"^(?!.*ata d[aeo]s? defesa).*(?:examinador(?:a|es)?\b|comissao de defesa|membros da banca)", -3.0, "cita quem avaliou (examinador/comissão), não orientação"),
        (r"certificamos|declaramos que .{0,60}(apresentou|participou)", -1.0, "parece certificado de evento"),
        (r"termo de compromisso de estagio|estagio (curricular )?(nao )?obrigatorio|supervisor(a)? de estagio", -3.5, "é termo de estágio: o orientador/curso citado é o do estágio (atuação), não orientação nem curso ministrado"),
    ], True, "Declaração de orientação de TCC"),
    Item("orientacao_andamento", "Orientações", "Orientações e supervisões em andamento", "Oriento um trabalho que ainda não terminou", [
        (r"orientou|orientador(a)?\b|orientacao d[oa]|orientando", 2.0, "cita orientador/orientando"),
        (r"em andamento|em curso|atualmente orienta|vigencia da bolsa", 3.5, "diz que está em andamento"),
        (r"disserta[c]ao|\btese\b|\btcc\b|trabalho de conclusao|iniciacao cientifica|monografia|pibic", 1.5, "cita o tipo de trabalho orientado"),
        (r"termo de compromisso de estagio|estagio (curricular )?(nao )?obrigatorio|supervisor(a)? de estagio", -3.5, "é termo de estágio: o orientador/curso citado é o do estágio (atuação), não orientação nem curso ministrado"),
    ], True, "Declaração de IC em andamento"),
    Item("banca", "Bancas", "Participação em bancas de trabalhos de conclusão", "Participei de uma banca examinadora", [
        (r"banca examinadora|membro da banca|participou da banca|comissao julgadora|examinador(a)?|avaliador(a)? externo", 4.0, "diz que integrou a banca"),
        (r"defesa|qualificacao", 1.0, "cita defesa ou qualificação"),
        (r"disserta[c]ao|\btese\b|\btcc\b|monografia|trabalho de conclusao", 1.0, "cita o trabalho avaliado"),
        (r"concurso publico|professor adjunto|processo seletivo para professor", -3.5, "é banca de comissão julgadora/concurso"),
    ], False, "Declaração de participação em banca"),
    Item("banca_comissao_julgadora", "Bancas", "Participação em bancas de comissões julgadoras", "Integrei comissão julgadora de concurso ou seleção", [
        (r"comissao julgadora.{0,60}concurso|concurso publico|professor adjunto|banca de concurso", 4.5, "cita comissão julgadora de concurso"),
    ], True, "Declaração de comissão julgadora"),
    Item("curso_ministrado", "Produções", "Curso de curta duração ministrado", "Ministrei um curso, minicurso ou oficina", [
        (r"ministrou|ministrante|docente do curso|instrutor(a)?|professor(a)? do curso|oficina ministrada", 4.0, "diz que ministrou o curso"),
        (r"\bcurso\b|minicurso|oficina|capacitacao", 1.0, "cita curso"),
        (r"carga horaria", 0.8, "tem carga horária"),
        (r"termo de compromisso de estagio|estagio (curricular )?(nao )?obrigatorio|supervisor(a)? de estagio", -3.5, "é termo de estágio: o orientador/curso citado é o do estágio (atuação), não orientação nem curso ministrado"),
    ], False, "Certificado de ministrante"),
    Item("formacao_complementar", "Formação", "Formação complementar", "Fiz um curso (como aluno)", [
        (r"concluiu (?:com exito )?o curso|participou do curso|cursou|carga horaria de \d+|certificado de conclusao do curso|curso de (extensao|capacitacao|atualizacao|aperfeicoamento)", 3.0, "diz que concluiu/participou do curso"),
        (r"carga horaria", 1.5, "tem carga horária"),
        (r"comissao (organizadora|cientifica)|organizacao do evento", -3.5, "é organização de evento, não curso"),
        (r"curso livre|formacao continuada|participou e concluiu|certificado do curso de", 3.0, "diz que concluiu curso livre/formação continuada"),
        (r"pos-graduacao lato sensu|especializacao lato sensu|nivel de pos-graduacao|titulo de especialista|especializacao\s*lato", -4.0, "é pós-graduação formal (titulação), não curso complementar"),
        (r"ministrou|ministrante|palestrante|instrutor", -3.5, "ele ministrou, não cursou"),
        (r"congresso|simposio|jornada", -1.0, "parece evento, não curso"),
        (r"(?:participa[cç][aã]o|participou)\s+(?:no|na|em|do|da|de)?\s*(?:[\w.\-]{1,12}\s+){0,3}?(?:evento|congresso|reuniao|simposio|jornada|encontro|semana|workshop|feira|forum)", -3.5, "é participação em evento, não curso"),
        (r"participacao (no|na|em|do|da)\b.{0,80}(congresso|reuniao|simposio|jornada|encontro|semana|workshop|feira)", -3.5, "é participação em evento, não curso"),
        (r"trabalho (cientifico )?intitulado|foi (submetido e )?apresentado|apresentacao de trabalhos? cientificos?|banner digital", -3.5, "é apresentação de trabalho, não curso"),
        (r"\bmonitoria\b|\bmonitor(a)? (bolsista|voluntari[oa])|\bestagio\b|\bestagiari[oa]\b", -3.5, "é monitoria/estágio (atuação), não curso"),
        (r"participou como (1o |primeiro |vice-)?(diretor|diretora|presidente|coordenador|coordenadora|tesoureiro|secretario|secretaria)\b", -3.5, "é cargo em liga/projeto/grupo, não curso"),
        (r"(voluntari|bolsista|integrante|membro|colaborador|coordenador)\w*.{0,60}projeto de (pesquisa|extensao|ensino|desenvolvimento)|projeto de (pesquisa|extensao|ensino|desenvolvimento).{0,20}intitulado", -3.5, "é atuação em projeto, não curso"),
    ], False, "Certificado de curso de extensão"),
    Item("formacao_academica", "Formação", "Formação acadêmica/titulação", "Concluí ou curso graduação, especialização, mestrado ou doutorado", [
        (r"\bdiploma\b|colacao de grau|conferiu o grau|historico (escolar|academico)|componentes curriculares cursados|grau de (mestre|doutor|bacharel|especialista|licenciado)|certificado de (conclusao|especializacao|pos-graduacao)|declaracao (de|da) matricula|aluno(?:\([a-z]\))? vinculado(?:\([a-z]\))?|declaramos.{0,100}aluno|matriculad[oa] no curso|vinculad[oa] a esta universidade|no curso de.{0,60}lato sensu", 4.5, "é diploma, certificado de titulação/aperfeiçoamento ou declaração de matrícula"),
        (r"confere .{0,80}titulo de (especialista|mestre|doutor|bacharel|licenciado)|titulo de especialista|pos-graduacao lato sensu|certificado de conclusao do curso de pos", 4.5, "confere título de especialista/mestre/doutor ou pós-graduação"),
        (r"nivel do curso\s*:?\s*(especializacao|mestrado|doutorado|graduacao)|identificacao da instituicao/?\s*curso", 4.0, "dados do curso com nível de titulação (certificado de pós/graduação)"),
        (r"bacharel|licenciatura|especializacao|mestrado|doutorado|lato sensu|stricto sensu|pos-graduacao", 1.5, "cita o nível de formação"),
    ], False, "Diploma de graduação"),
    Item("atuacao_profissional", "Atuação", "Atuação profissional", "Trabalho ou trabalhei em uma instituição", [
        (r"declaracao de vinculo|portaria de nomeacao|contrato de trabalho|admissao|exerce o cargo|lotado|matricula funcional|vinculo empregaticio|servidor(a)? (publico|efetivo)|termo de compromisso de estagio|estagio (curricular )?nao obrigatorio|\bestagiari[oa]\b|selecao para monitoria|\bmonitor(a)? (bolsista|voluntari[oa])|\bmonitoria\b", 3.5, "comprova vínculo, estágio ou monitoria (registrados na atuação profissional)"),
        (r"participou como (1o |primeiro |vice-)?(diretor|diretora|presidente|coordenador|coordenadora|tesoureiro|secretario|secretaria)\b.{0,100}\b(liga|projeto|nucleo|grupo|laboratorio)\b|diretor(a)? cientifico", 3.0, "diz que exerceu cargo em liga/projeto/grupo"),
        (r"faz parte do (nosso )?quadro (de )?pessoal|exercendo (atualmente )?a funcao de|presta servicos? (a|nesta|neste)", 3.5, "declara que integra o quadro de pessoal/exerce função"),
        (r"\bcargo\b|\bfuncao\b|regime de trabalho|carga horaria semanal", 1.2, "cita cargo/função"),
    ], False, "Declaração de vínculo"),
    Item("revisor_periodico", "Atuação", "Revisor de periódico", "Fui revisor/parecerista de uma revista", [
        (r"revisor(a)?|reviewer|parecerista|peer review|avaliacao de manuscrito|referee", 4.0, "diz que foi revisor/parecerista"),
        (r"periodico|journal|revista", 1.0, "cita revista"),
        (r"em projetos|edital universal|declaracao da agencia", -3.0, "é revisor de projeto de fomento"),
    ], False, "Certificado de revisor"),
    Item("revisor_projeto_fomento", "Atuação", "Revisor de projeto de agência de fomento", "Emiti parecer ad hoc em projetos de agência de fomento", [
        (r"parecer ad hoc em projetos|declaracao da agencia|revisor(a)? de projeto|projetos do edital", 4.5, "cita parecer em projetos de agência de fomento"),
    ], True, "Declaração da agência de fomento"),
    Item("comite_assessoramento", "Atuação", "Membro de comitê de assessoramento", "Integrei comitê de assessoramento de agência de fomento", [
        (r"comite de assessoramento|comite assessor", 4.5, "cita comitê de assessoramento"),
    ], True, "Portaria de comitê de assessoramento"),
    Item("pos_doutorado", "Formação", "Pós-doutorado", "Realizei estágio de pós-doutorado", [
        (r"pos-doutorado|pos doutorado|estagio de pos-doutorado", 4.5, "cita pós-doutorado"),
    ], True, "Declaração de pós-doutorado"),
    Item("corpo_editorial", "Atuação", "Membro de corpo editorial", "Sou do corpo editorial de uma revista", [
        (r"corpo editorial|editor(a)? associad[oa]|editor(a)?-chefe|editor(a)? chefe|editorial board|conselho editorial", 4.5, "cita corpo/conselho editorial"),
        (r"certificado de publicacao|declaracao de publicacao|publicaram no|publicaram o artigo|o artigo intitulado|artigo intitulado", -5.0, "é certificado de publicação assinado pelo editor, não atuação como editor"),
    ], False, "Portaria de editor"),
    Item("patente", "Patentes e Registros", "Patente", "Depositei ou obtive uma patente", [
        (r"carta patente|pedido de patente|\bpatente\b|\binpi\b|modelo de utilidade|privilegio de invencao", 4.0, "cita patente/INPI"),
    ], False, "Carta patente"),
    Item("software_registro", "Patentes e Registros", "Programa de Computador Registrado", "Registrei um programa de computador", [
        (r"registro de programa de computador|certificado de registro.{0,40}programa|programa de computador", 4.5, "cita registro de programa de computador"),
    ], False, "Certificado de registro de software"),
    Item("desenho_industrial", "Patentes e Registros", "Desenho Industrial Registrado", "Registrei um desenho industrial", [
        (r"desenho industrial|registro\s+di\s*\d", 4.5, "cita registro de desenho industrial"),
    ], True, "Certificado de registro de desenho industrial"),
    Item("marca_registrada", "Patentes e Registros", "Marca Registrada", "Registrei uma marca", [
        (r"registro de marca|certificado de registro de marca", 4.5, "cita registro de marca"),
    ], True, "Certificado de registro de marca"),
    Item("topografia_circuito", "Patentes e Registros", "Topografia de Circuito Integrado Registrada", "Registrei topografia de circuito integrado", [
        (r"topografia de circuito integrado|circuito integrado", 4.5, "cita topografia de circuito integrado"),
    ], True, "Certificado de topografia de circuito integrado"),
    Item("cultivar_protegida", "Patentes e Registros", "Cultivar Protegida", "Obtive certificado de proteção de cultivar", [
        (r"protecao de cultivar|certificado de protecao.{0,40}cultivar|obtentor(a)?", 4.5, "cita proteção de cultivar"),
    ], True, "Certificado de proteção de cultivar"),
    Item("cultivar_registrada", "Patentes e Registros", "Cultivar Registrada", "Registrei cultivar no Registro Nacional de Cultivares", [
        (r"registro de cultivar|registro nacional de cultivares|mantenedor(a)?", 4.5, "cita registro de cultivar"),
    ], True, "Certificado de registro de cultivar"),
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
        (r"relatorio tecnico|parecer tecnico|\blaudo\b", 3.5, "cita relatório/parecer/laudo"),
        (r"consultoria|assessoria", 1.5, "cita consultoria/assessoria"),  # sozinha não prova: aparece em nomes de disciplinas e cargos
        (r"portaria (reitoria )?n|resultado da selecao|relacao de (alunos|aprovados)|\bmonitor(a)?\b", -3.0, "é portaria/lista de seleção, não trabalho técnico"),
        (r"declaracao de servico tecnico|analise fisico-quimica", -3.0, "é serviço/trabalho técnico"),
    ], False, "Parecer técnico"),
    Item("trabalho_tecnico", "Produções", "Demais trabalhos técnicos", "Realizei serviço ou análise técnica com laudo", [
        (r"declaracao de servico tecnico|servico tecnico|analise fisico-quimica.{0,80}laudo", 4.5, "cita serviço/trabalho técnico"),
    ], True, "Declaração de serviço técnico"),
    Item("software_sem_registro", "Produções", "Programa de computador sem registro", "Desenvolvi um programa ou aplicativo sem registro no INPI", [
        (r"declaracao de desenvolvimento|desenvolveu o (aplicativo|programa|software|sistema).{0,80}sem registro|sem registro em orgao competente", 4.5, "cita desenvolvimento de software sem registro"),
    ], True, "Declaração de desenvolvimento de software"),
    Item("produto", "Produções", "Produtos tecnológicos", "Desenvolvi um produto tecnológico", [
        (r"ficha de produto|\bproduto:\s+[^\n]+desenvolvido por", 4.5, "cita ficha/desenvolvimento de produto tecnológico"),
    ], True, "Ficha de produto tecnológico"),
    Item("processo_tecnica", "Produções", "Processos ou técnicas", "Desenvolvi um processo ou técnica", [
        (r"descricao de processo|processo de extracao.{0,80}desenvolvido por|processo ou tecnica", 4.5, "cita desenvolvimento de processo ou técnica"),
    ], True, "Descrição de processo ou técnica"),
    Item("material_didatico", "Produções", "Desenvolvimento de material didático ou instrucional", "Desenvolvi material didático ou apostila", [
        (r"desenvolveu o material didatico|material didatico|apostila de", 4.5, "cita desenvolvimento de material didático/apostila"),
    ], True, "Declaração de material didático"),
    Item("extensao_tecnologica", "Produções", "Extensão tecnológica", "Prestei atividade de extensão tecnológica", [
        (r"declaracao de extensao tecnologica|prestou extensao tecnologica|\bextensao tecnologica\b", 4.5, "cita extensão tecnológica"),
    ], True, "Declaração de extensão tecnológica"),
    Item("entrevista_midia", "Produções", "Programas de rádio ou TV", "Concedi entrevista ou participei de programa de rádio/TV", [
        (r"declaracao da emissora|concedeu entrevista ao programa|programa de (radio|tv|televisao)", 4.5, "cita entrevista ou programa de rádio/TV"),
    ], True, "Declaração de entrevista em emissora"),
    Item("redes_sociais", "Produções", "Redes sociais, websites e blogs", "Mantenho blog, site ou canal de divulgação científica", [
        (r"captura de pagina|\bblog\b.{0,80}mantido por|finalidade:\s*divulgacao cientifica", 4.5, "cita blog/site de divulgação científica"),
    ], True, "Captura de página de blog científico"),
    Item("relatorio_pesquisa", "Produções", "Relatório de pesquisa", "Elaborei relatório final ou parcial de pesquisa", [
        (r"relatorio de pesquisa|relatorio final do projeto", 4.5, "cita relatório de pesquisa"),
    ], True, "Relatório final de pesquisa"),
    Item("outra_producao_tecnica", "Produções", "Outra produção técnica", "Elaborei outra produção técnica (regimento, norma, protocolo)", [
        (r"elaborou o regimento|regimento do laboratorio|outra producao tecnica", 4.5, "cita regimento/norma técnica"),
    ], True, "Declaração de elaboração de regimento"),
    Item("artes_cenicas", "Produções", "Artes cênicas", "Participei de espetáculo teatral ou artes cênicas", [
        (r"declaracao do teatro|preparadora vocal|espetaculo\b.{0,80}teatro|artes cenicas|peca teatral", 4.5, "cita espetáculo teatral (artes cênicas)"),
    ], True, "Declaração do teatro"),
    Item("artes_visuais", "Produções", "Artes visuais", "Participei de exposição de artes visuais ou fotografia", [
        (r"certificado de exposicao|exposicao coletiva|\bgaleria\b|artes visuais", 4.5, "cita exposição de artes visuais"),
    ], True, "Certificado de exposição"),
    Item("musica", "Produções", "Música", "Compus ou gravei obra musical", [
        (r"declaracao de composicao|compos a cancao|gravada no album|composicao musical", 4.5, "cita composição musical"),
    ], True, "Declaração de composição"),
    Item("partitura_musical", "Produções", "Partitura musical", "Publiquei ou elaborei partitura musical", [
        (r"ficha da partitura|\bpartitura\b", 4.5, "cita partitura musical"),
    ], True, "Ficha da partitura"),
    Item("cartas_mapas", "Produções", "Cartas, mapas ou similares", "Elaborei carta temática ou mapa", [
        (r"declaracao cartografica|carta tematica|mapa tematico", 4.5, "cita carta temática ou mapa"),
    ], True, "Declaração cartográfica"),
    Item("maquete", "Produções", "Maquete", "Projetei ou construí uma maquete", [
        (r"projetou a maquete|\bmaquete\b", 4.5, "cita maquete"),
    ], True, "Declaração de maquete"),
    Item("manutencao_obra", "Produções", "Manutenção de obra artística", "Atuei na conservação ou restauro de obra artística", [
        (r"atestado de restauro|conservacao do painel|restauracao de obra|manutencao de obra", 4.5, "cita restauro ou conservação de obra"),
    ], True, "Atestado de restauro"),
    Item("outra_producao_artistica", "Produções", "Outra produção artística/cultural", "Realizei curadoria ou outra produção artística/cultural", [
        (r"fez a curadoria da mostra|curadoria da mostra|centro cultural|outra producao artistica", 4.5, "cita curadoria/produção artística"),
    ], True, "Declaração de curadoria"),
    Item("identificacao", "Dados gerais", "Identificação", "Atualizar dados de identificação do currículo", [
        (r"ficha cadastral institucional|nome em citacoes bibliograficas", 4.5, "é ficha cadastral institucional"),
    ], True, "Ficha cadastral institucional"),
    Item("endereco", "Dados gerais", "Endereço", "Atualizar endereço profissional ou residencial", [
        (r"comprovante de endereco|endereco profissional|endereco residencial", 4.5, "é comprovante de endereço"),
    ], True, "Comprovante de endereço profissional"),
    Item("texto_inicial", "Dados gerais", "Texto inicial do currículo Lattes", "Atualizar o resumo/texto inicial do currículo", [
        (r"resumo do curriculo|texto inicial do curriculo", 4.5, "é resumo do currículo"),
    ], True, "Resumo do currículo"),
    Item("outras_informacoes", "Dados gerais", "Outras informações relevantes", "Incluir outras informações relevantes no currículo", [
        (r"informacao relevante complementar|outras informacoes relevantes", 4.5, "cita informação relevante complementar"),
    ], True, "Declaração de informação relevante"),
    Item("citacao_scopus", "Citações", "Citações — Scopus", "Atualizar indicadores de citações da base Scopus", [
        (r"\bscopus\b", 1.5, "cita base Scopus"),
        (r"(?:citacoes|indice h|h-index|times cited).{0,300}\bscopus\b|\bscopus\b.{0,300}(?:citacoes|indice h|h-index|times cited)", 3.5, "base Scopus junto de indicadores de citações"),
        (r"citacoes|indice h|h-index", 1.0, "cita indicadores de citações"),
    ], True, "Perfil de autor no Scopus"),
    Item("citacao_web_of_science", "Citações", "Citações — Web of Science", "Atualizar indicadores de citações da Web of Science", [
        (r"web of science|researcher profile|researcherid", 1.5, "cita base Web of Science"),
        (r"(?:times cited|citacoes|h-index).{0,300}(?:web of science|researcherid)|(?:web of science|researcherid).{0,300}(?:times cited|citacoes|h-index)", 3.5, "Web of Science junto de indicadores de citações"),
        (r"times cited|citacoes|h-index", 1.0, "cita indicadores de citações"),
    ], True, "Perfil de autor na Web of Science"),
    Item("citacao_google_scholar", "Citações", "Citações — Google Scholar", "Atualizar indicadores de citações do Google Acadêmico", [
        (r"google academico|google scholar", 1.5, "cita Google Acadêmico/Scholar"),
        (r"(?:citacoes|indice h|indice i10).{0,300}(?:google academico|google scholar)|(?:google academico|google scholar).{0,300}(?:citacoes|indice h|indice i10)", 3.5, "Google Acadêmico junto de indicadores de citações"),
        (r"citacoes|indice h|indice i10", 1.0, "cita indicadores de citações"),
    ], True, "Perfil no Google Acadêmico"),
    Item("citacao_scielo", "Citações", "Citações — SciELO", "Atualizar indicadores de citações da base SciELO", [
        (r"\bscielo\b", 1.5, "cita base SciELO"),  # só citar a base não basta: artigos listam SciELO como fonte de busca
        (r"(?:citacoes|indice h|h-index|times cited).{0,300}\bscielo\b|\bscielo\b.{0,300}(?:citacoes|indice h|h-index|times cited)", 3.5, "base SciELO junto de indicadores de citações"),
        (r"citacoes|documentos", 1.0, "cita indicadores de citações"),
    ], True, "Indicadores de citações SciELO"),
    Item("citacao_outra_base", "Citações", "Citações — Outra base", "Atualizar indicadores de citações de outra base bibliográfica", [
        (r"base bibliografica.{0,40}citacoes|citacoes:\s*\d+.{0,60}\bbase:", 4.5, "cita citações em outra base bibliográfica"),
    ], True, "Indicadores de citações em outra base"),
]
INDICE = {i.id: i for i in ITENS}

# itens cujo texto, em frase própria, os define sem ambiguidade; a confiança sobe sem inflar o "máximo possível" das regras
DECISIVOS = {
    "atuacao_profissional": (r"participou d[oa](?:\(a\))? monitoria|monitoria academica|exerceu (a )?monitoria|atuou como monitor(a)?|monitoria (da|na|de) disciplina",
                             "o certificado é de monitoria (registrada na atuação profissional)"),
    "apresentacao": (r"atividade apresentacao de trabalho|participou[^.]{0,80}atividade[^.]{0,20}apresentacao de trabalhos? cientificos?",
                     "o certificado diz que a atividade foi apresentar trabalho"),
}
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


TITULOS_DE_DOCUMENTO = ("historico academico", "historico escolar", "certificado de conclusao", "declaracao de vinculo", "ata de defesa")


def _titulos_aproximados(t: str) -> str:
    """Títulos de documento muito discriminativos, achados por aproximação nas primeiras linhas (OCR de documento antigo/torto troca letras).

    Devolve os títulos canônicos encontrados para serem acrescentados ao texto antes da pontuação. Só olha o começo e exige 80% de semelhança.
    """
    base = re.sub(r"[^a-z0-9]", "", t[:600])
    achados = []
    for titulo in TITULOS_DE_DOCUMENTO:
        chave = titulo.replace(" ", "")
        if chave in base:
            continue  # já está escrito certo: a regra normal pega
        n = len(chave)
        for i in range(0, max(1, len(base) - n + 1)):
            if difflib.SequenceMatcher(None, chave, base[i:i + n]).ratio() >= (0.75 if n >= 15 else 0.85):  # frase longa tolera mais erro de OCR
                # a última palavra do título (vínculo, acadêmico, defesa...) também precisa aparecer: "declaração" + "declaramos"
                # sozinhos não fazem uma "declaração de vínculo"
                ultima = titulo.split()[-1]
                trecho = base[i + n - len(ultima) - 1:i + n + 1]
                if difflib.SequenceMatcher(None, ultima, trecho).find_longest_match(0, len(ultima), 0, len(trecho)).size >= len(ultima) - 2:
                    achados.append(titulo)
                    break
    return " ".join(achados)


def classificar(texto: str, nome_arquivo: str = "", paginas: int = 0, resumos_no_pdf: int = 0) -> dict[str, Any]:
    """Classifica o texto de uma evidência. `resumos_no_pdf` = quantas vezes 'Keywords:' aparece (detecta caderno)."""
    t = norm(texto)
    t = (t + " " + _titulos_aproximados(t)).strip()  # título do documento lido com erro de OCR ("H lst6rico Acad6m !co")
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
        if it.id in DECISIVOS and re.search(DECISIVOS[it.id][0], t) and pontos > 0:
            conf = max(conf, 0.85)  # documento cujo texto o define sem dúvida (ex.: "participou da Monitoria Acadêmica"): segue sozinho
            motivos = motivos + [DECISIVOS[it.id][1]]
        rotulo = it.item
        if it.id == "projeto":  # o menu do Lattes tem um item por tipo de projeto: mostra o que o documento diz
            for pad, nome_tipo in ((r"projeto de extensao", "Projeto de extensão"), (r"projeto de ensino", "Projeto de ensino"),
                                   (r"projeto de desenvolvimento", "Projeto de desenvolvimento tecnológico"), (r"projeto de pesquisa", "Projetos de pesquisa")):
                if re.search(pad, t):
                    rotulo = nome_tipo
                    break
        cands.append({"id": it.id, "item": rotulo, "secao": it.secao, "grupo": it.grupo, "pontos": round(pontos, 2),
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
        if re.search(r"\banais\b|titulo dos anais|caderno de resumos", t):
            relacionados.append({"id": "anais", "motivo": "o documento também registra publicação nos anais do evento"})
    elif top["id"] == "anais" and re.search(r"comunicacao oral|\bposter\b|apresentacao oral|modalidade.{0,30}(oral|poster|banner)", t):
        relacionados.append({"id": "apresentacao", "motivo": "o documento também indica modalidade de apresentação (comunicação oral/pôster)"})
    return {"decisao": decisao, "motivo_decisao": why, "candidatos": cands, "tambem_pode_gerar": relacionados}


def _marcar_especificados() -> None:
    """Todos os itens com especificação + leitor passam a reconhecidos com formulário estruturado."""
    from itens import especificacao, ids_especificados
    from itens.leitores import LEITORES
    existentes = {i.id for i in ITENS}
    for item_id in ids_especificados():
        if item_id not in existentes:
            spec = especificacao(item_id) or {}
            nome = spec.get("item") or item_id
            ITENS.append(Item(item_id, spec.get("secao") or "Outros", nome, f"Cadastrar {nome.lower()}", [],
                              item_id in LEITORES, spec.get("como_abrir") or ""))
    for i in ITENS:
        if i.id in LEITORES:
            i.implementado = True
    INDICE.update({i.id: i for i in ITENS})


_marcar_especificados()


def catalogo_publico() -> list[dict[str, Any]]:
    """Lista dos itens reconhecíveis, para o escolhedor guiado da tela."""
    return [{"id": i.id, "secao": i.secao, "item": i.item, "grupo": i.grupo, "implementado": i.implementado,
             "exemplo": i.exemplo} for i in ITENS]


def candidato_fixo(item_id: str, motivo: str, confianca: float = 0.95) -> dict[str, Any]:
    """Resultado de classificação para quando outro leitor já sabe o que é (ex.: o texto é só um DOI)."""
    i = INDICE[item_id]
    return {"decisao": "avancar", "motivo_decisao": motivo, "tambem_pode_gerar": [],
            "candidatos": [{"id": i.id, "item": i.item, "secao": i.secao, "grupo": i.grupo, "pontos": 0,
                            "confianca": confianca, "motivos": [motivo], "implementado": i.implementado}]}
