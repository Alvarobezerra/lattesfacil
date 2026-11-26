"""Separa o PDF unificado de comprovações (Q13) de cada candidato em documentos individuais.

Documentos de várias páginas (histórico, TCE, certificado frente/verso, ficha de avaliação,
Currículo Lattes) permanecem juntos: a fronteira só é aberta quando há indício de documento novo.

Pré-requisito: python ferramentas/ocr_cache_inscricoes.py   (gera tests/curriculos e modelos/_cache_texto_paginas)
Uso: python ferramentas/separar_evidencias_inscricoes.py [prefixo_candidato ...]
Saída: tests/curriculos e modelos/2_EVIDENCIAS_SEPARADAS/<candidato>/NN_<tipo>_pAA-pBB.pdf + manifesto.json
       tests/curriculos e modelos/2_EVIDENCIAS_SEPARADAS/RELATORIO.md
"""
from __future__ import annotations
import difflib, glob, json, os, re, sys, unicodedata

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'curriculos e modelos')
CACHE = os.path.join(BASE, '_cache_texto_paginas')
SAIDA = os.path.join(BASE, '2_EVIDENCIAS_SEPARADAS')


def norm(t: str) -> str:
    t = unicodedata.normalize('NFKD', t or '')
    t = ''.join(c for c in t if not unicodedata.combining(c)).lower()
    # junta letras espaçadas ("P á g i n a" -> "pagina")
    for _ in range(3):
        t = re.sub(r'(?<![a-z0-9])([a-z0-9]) (?=[a-z0-9](?![a-z0-9]))', r'\1', t)
    return re.sub(r'\s+', ' ', t).strip()


START_KW = [
    ('certificado', r'\bcertificad[oa]s?\b|\bcertificamos\b|\bcertifico\b|\bcertifica-se\b|\bcertificate\b'),
    # certificado cujo texto nativo começa pelo nome da pessoa ("Fulana, concluiu o curso de X no dia ..."), sem a palavra "certificado" no topo
    ('certificado', r'^\W*(?:[a-z]+\s+){1,7}[a-z]+,?\s+(?:concluiu|participou|apresentou|ministrou|integrou)\b'),
    ('declaracao', r'\bdeclaracao\b|\bdeclaramos\b|\bdeclaro\b'),
    ('atestado', r'\batestado\b|\batestamos\b'),
    ('historico', r'historico escolar|historico academico|historico do aluno|historico de graduacao|historico de'),
    ('diploma', r'\bdiploma\b'),
    ('termo', r'termo de (compromisso|estagio|cessao|autorizacao|outorga)|\bcontrato\b'),
    ('certidao', r'\bcertidao\b'),
    ('comprovante', r'\bcomprovante\b|\brecibo\b'),
    ('portaria', r'\bportaria\b|\bresolucao\b|\bata n|\bata da\b|\boficio\b|\bmemorando\b'),
    ('publicacao', r'\banais\b|\bresumo\b|\bartigo\b|\bcarta de aceite\b|\baceite\b'),
    ('projeto', r'\banteprojeto\b|\bprojeto de pesquisa\b|\bplano de trabalho\b'),
]
LATTES_START = re.compile(r'curriculo do sistema de curriculos lattes|endereco para acessar este cv|nome em citacoes bibliograficas|curriculo lattes')
LATTES_MARK = re.compile(r'lattes\.cnpq|plataforma lattes|id lattes|ultima atualizacao do curriculo|producao bibliografica|formacao academica|imprimir curriculo|citacoes bibliograficas|areas de atuacao|idiomas|projetos de pesquisa|participacao em eventos')
LATTES_END = re.compile(r'configuracao de privacidade na plataforma lattes|imprimir curriculo|este curriculo')
FICHA_START = re.compile(r'ficha de avaliacao|barema|anexo vi\b|anexo vii\b|analise curricular|avaliacao curricular|tabela de pontuacao|pontuacao do curriculo|curriculo lattes e documentos')
FICHA_MARK = re.compile(r'pontuacao|pontos|barema|ficha de avaliacao|avaliacao curricular|pontuacao maxima|total de pontos|criterio|\bnota\b')
CONT_MARK = re.compile(r'conteudo programatico|programacao|ementa|verso|relacao de (participantes|alunos)|grade curricular|disciplinas|atividades complementares')
FRONT_RE = re.compile(r'dados internacionais de catalogacao|ficha catalografica|todos os direitos reservados|copyright|corpo editorial|editores academicos|comissao cientifica|organizadores?\b|\bapresentacao\b|\bsumario\b|\bindice\b|\bisbn\b|\b\d{1,2}\W{0,3}ed\b|\bedicao\b')
FORTE = {'certificado', 'declaracao', 'atestado', 'historico', 'diploma', 'termo', 'certidao', 'comprovante', 'portaria'}  # início de documento que encerra um pacote de publicação
PAG_RE = re.compile(r'(?:pagina|pag\.?|page)\s*(\d{1,3})\s*(?:de|/|\||of)\s*(\d{1,3})')
ID_RE = re.compile(r'\b(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[a-z0-9]{16,})\b')


def head(n, k=450):
    return n[:k]


def _caixa_alta(texto: str) -> float:
    """Fração de letras maiúsculas nos primeiros 80 caracteres (capas e títulos são em caixa alta; texto corrido não)."""
    letras = [c for c in texto[:80] if c.isalpha()]
    return sum(c.isupper() for c in letras) / max(len(letras), 1)


def info_pagina(p, total=0):
    n = norm(p['t'])
    m = PAG_RE.search(n)
    pag = (int(m.group(1)), int(m.group(2))) if m and int(m.group(1)) <= int(m.group(2)) and int(m.group(2)) != total else None
    ids = {i for i in ID_RE.findall(n) if re.search(r'\d', i) and re.search(r'[a-f-]', i)}
    tipo = None
    h = head(n)
    for nome, rx in START_KW:
        if re.search(rx, h):
            tipo = nome; break
    return dict(n=n, pag=pag, ids=ids, kw=tipo, vazio=len(n) < 25, lat=bool(LATTES_START.search(n[:600]) or len(LATTES_MARK.findall(n)) >= 3),
                ficha=bool(FICHA_START.search(n[:500])), fmark=len(FICHA_MARK.findall(n)),
                cont=bool(CONT_MARK.search(n[:500])), cont_any=bool(CONT_MARK.search(n)),
                # capa de publicação: pouco texto + imagem, sem cara de certificado; parte de livro: ficha, copyright, sumário, corpo editorial...
                # (topo em CAIXA ALTA tolera um subtítulo com vírgulas; texto corrido de resumo/capítulo não é capa)
                cover=bool(len(n) < 500 and (p.get('nimg', 0) >= 1 or len(n) < 200)
                           and len(re.findall(r'[a-z]{3,}[,.;]\s+[a-z]{3,}', n)) <= (3 if _caixa_alta(p['t']) >= 0.7 else 1) and not re.search(r'menc|honrosa|certific|declar|concede|confere|outorga|premi|diploma|historico|portaria|termo de|atestado|aluno|matricula', n)),
                front=bool(FRONT_RE.search(n[:400])), fp=re.sub(r'[^a-z0-9]', '', n[:60]),
                minus=bool(re.match(r'[^a-z0-9]*[a-z]', n) and re.match(r'[^A-Za-z0-9]*[a-z]', p['t'].strip() or 'A')))


def mesmo_tamanho(a, b):
    return abs(a['w'] - b['w']) <= 8 and abs(a['h'] - b['h']) <= 8


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def segmentar(paginas):
    """Retorna lista de (inicio, fim, tipo, confianca, motivo) com índices 0-based inclusivos."""
    I = [info_pagina(p, len(paginas)) for p in paginas]
    N = len(paginas)
    rotulo = [None] * N           # 'lattes' | 'ficha'
    # --- bloco Lattes: do início do CV até a página com marcador final (ou até o 1º documento com palavra-chave)
    i = 0
    while i < N:
        if I[i]['lat'] and rotulo[i] is None and LATTES_START.search(I[i]['n'][:600]):
            j = i
            fim = None
            while j < N:
                if j > i and LATTES_START.search(I[j]['n'][:600]) and not LATTES_MARK.search(I[j]['n']): break
                if j > i and not mesmo_tamanho(paginas[j], paginas[i]): break  # o CV é uniforme: mudar tamanho/orientação encerra o bloco
                # página do CV é texto nativo e longo; página escaneada curta sem termos do Lattes já é outro documento (ex.: diploma)
                if j > i and paginas[j].get('ocr') and len(I[j]['n']) < 900 and not LATTES_MARK.search(I[j]['n']): break
                if LATTES_END.search(I[j]['n']) and 'configuracao de privacidade' in I[j]['n']:
                    fim = j; break
                if j > i and I[j]['kw'] and I[j]['kw'] != 'publicacao' and len(LATTES_MARK.findall(I[j]['n'])) == 0:
                    break
                j += 1
            fim = fim if fim is not None else min(j, N) - 1 if j >= N or True else j - 1
            if fim < i: fim = i
            for k in range(i, fim + 1): rotulo[k] = 'lattes'
            i = fim + 1
        else:
            i += 1
    # folha de rosto do currículo ("Curriculum Vitae Julho/2026") logo antes do bloco Lattes faz parte dele
    if N > 1 and rotulo[1] == 'lattes' and rotulo[0] is None and not I[0]['vazio'] and len(I[0]['n']) < 400:
        rotulo[0] = 'lattes'
    # --- fichas/barema
    i = 0
    while i < N:
        # ficha por título ("Ficha de avaliação") ou, quando o OCR estraga o título, por 3 páginas seguidas cheias de termos de pontuação
        corrida = I[i]['fmark'] >= 3 and i + 2 < N and I[i + 1]['fmark'] >= 3 and I[i + 2]['fmark'] >= 3
        if rotulo[i] is None and ((I[i]['ficha'] and I[i]['fmark'] >= 2) or corrida):
            j = i + 1
            while j < N and rotulo[j] is None and (I[j]['fmark'] >= 2 or (I[j]['pag'] and I[j]['pag'][0] > 1 and I[j-1]['fmark'] >= 2)) and not (I[j]['kw'] in ('certificado', 'declaracao', 'diploma', 'historico') and I[j]['fmark'] < 4):
                j += 1
            for k in range(i, j): rotulo[k] = 'ficha'
            i = j
        else:
            i += 1

    # --- decisão página a página
    def _capa(k):  # capa: pouco texto/aspecto de título, ou página curta logo antes de ficha/copyright/sumário
        if I[k]['cover']:
            return True
        if I[k]['kw'] in FORTE or I[k]['front']:
            return False
        return bool( (k + 1 < N and I[k + 1]['front'] and len(I[k]['n']) < 800 and not I[k]['lat']
                             and (len(I[k]['n']) < 250 or _caixa_alta(paginas[k]['t']) >= 0.3)))  # texto corrido em minúsculas não é capa
    CAPA = [_capa(k) for k in range(N)]
    fecha_em = -1
    inicios = [0]
    conf = {0: ('alta', 'primeira página')}
    em_pub, capas = bool(CAPA[0]), ([I[0]['fp']] if CAPA[0] and len(I[0]['fp']) >= 20 else [])
    for k in range(1, N):
        a, b = I[k - 1], I[k]
        pa, pb = paginas[k - 1], paginas[k]
        if rotulo[k] and rotulo[k] == rotulo[k - 1]:
            continue
        if rotulo[k] != rotulo[k - 1]:
            inicios.append(k); conf[k] = ('alta', f'muda bloco ({rotulo[k-1]}->{rotulo[k]})'); continue
        if a['ids'] & b['ids']:
            continue
        # continuação por paginação explícita
        if b['pag']:
            if b['pag'][0] > 1 and (not a['pag'] or (a['pag'][1] == b['pag'][1] and a['pag'][0] == b['pag'][0] - 1)):
                continue
            if b['pag'][0] == 1 and b['pag'][1] > 1:
                inicios.append(k); conf[k] = ('alta', 'paginação 1/N'); continue
        if a['ids'] & b['ids']:
            continue
        # página só de verificação de autenticidade (código/QR) é continuação do documento anterior. Mas o Even3 coloca
        # "Verifique o código de autenticidade" no topo do PRÓPRIO certificado: se a página tem corpo de certificado
        # (certificamos/participou/apresentou...), é documento novo.
        if (re.match(r'\W*(verifique|valide|confira|acesse)\b.{0,40}(autenticidade|autenticacao|verificacao|documento)', b['n'][:120])
                and len(b['n']) < 600
                and not re.search(r'certificamos|certifico|declaramos|declaro|atestamos|participou|apresentou|concluiu|ministrou|integrou', b['n'])):
            continue
        # página de validação/assinatura digital (PortalAVP, hash SHA256, "Assinado digitalmente por") e verso de diploma
        # ("Divisão de Registro de Diplomas") seguem o documento anterior mesmo quando repetem a palavra que abre o documento
        if (re.search(r'portalavp|informacoes do documento|nome do arquivo\s*:|id do documento|assinatura\(sha256\)|assinado digitalmente por', b['n'][:300])
                and len(b['n']) < 900) or re.search(r'registrodediplomas|diplomaregistrado', re.sub(r'\W', '', b['n'][:700])):  # OCR cola/separa palavras: compara sem espaços
            continue
        # artigos de uma mesma revista no mesmo layout, com número de artigo diferente no cabeçalho (|e10433| x |e10674|): documentos distintos
        ida, idb = re.search(r'\be\d{4,6}\b', a['n'][:150]), re.search(r'\be\d{4,6}\b', b['n'][:150])
        if ida and idb and ida.group() != idb.group():
            inicios.append(k); conf[k] = ('media', 'outro número de artigo no cabeçalho'); continue
        # capítulo cujo número não consta no sumário da página anterior: é de outro livro
        mcap = re.match(r'\W*capitulo\s*0*(\d+)', b['n'][:60])
        if mcap and re.match(r'\W*sumario\b', a['n'][:80]) and not re.search(rf'capitulo\s*0*{mcap.group(1)}\b', a['n']):
            inicios.append(k); conf[k] = ('media', 'capítulo fora do sumário anterior'); continue
        # página de assinatura/log (Clicksign) segue o documento
        if re.search(r'clicksign|log de assinaturas|documento assinado com validade|autenticacao|assinatura digital', b['n'][:300]) and not b['kw']:
            continue
        tam = mesmo_tamanho(pa, pb)
        fj = jacc(pa['fonts'], pb['fonts']) if pa['fonts'] and pb['fonts'] else None
        # histórico/verso com o mesmo cabeçalho institucional da página anterior = mesmo documento
        if b['kw'] == 'historico' and tam and len(a['n'][:30]) >= 25 and (a['n'][:30] == b['n'][:30] or difflib.SequenceMatcher(
                None, re.sub(r'\W', '', a['n'][:60]), re.sub(r'\W', '', b['n'][:60])).ratio() >= 0.8):  # OCR varia letras do cabeçalho
            continue  # mesmo título de histórico no topo (a data/matrícula da linha seguinte muda)
        # verso do certificado (conteúdo programático, carga horária por módulo) sem palavra de início
        # página que recomeça no meio de uma frase (minúscula) e é curta, no mesmo tamanho, continua o certificado/documento anterior
        if tam and a['kw'] in ('certificado', 'declaracao', 'diploma', 'atestado') and not b['cover'] and b['minus'] and re.match(r'[a-z]', b['n'][:1]) \
                and len(b['n']) < 700 and not re.match(r'\W*(certificamos|certificado|declaramos|declaro)\b', b['n'][:40]):
            continue
        verso_cert = bool(re.search(r'dados do aluno e da matricula|conteudo programatico|matriz curricular', b['n']))  # rótulos do verso, em qualquer ponto
        lista_topicos = b['n'].startswith('- ') and b['n'].count(' - ') >= 4  # página só com lista de tópicos (conteúdo programático) sem título
        if a['kw'] == 'certificado' and not b['kw'] and (verso_cert or lista_topicos or (b['cont_any'] and not b['cover'])):
            continue
        # mesmo papel timbrado no topo, mesmo tamanho e nenhuma palavra de início de documento: continuação
        # (ex.: portaria com a lista de nomes seguindo por várias páginas)
        if not b['kw'] and tam and not b['vazio'] and not a['vazio'] \
                and (difflib.SequenceMatcher(None, a['n'][:50], b['n'][:50]).ratio() >= 0.8
                     or (len(a['n']) > 80 and len(b['n']) > 80 and difflib.SequenceMatcher(None, a['n'][-60:], b['n'][-60:]).ratio() >= 0.8)):
            continue  # o papel timbrado pode estar no topo ou no rodapé
        # página de artigo na web (OJS/Zenodo/SciELO: "Published ...", "Journal article", "Início / Arquivos / v.99 n.3") abre documento novo,
        # mesmo depois de outra página de artigo sem palavra de início
        if not b['minus'] and not CAPA[k] and re.search(r'published\s+\w+\s+\d{1,2},?\s+\d{4}|journal article|inicio\s*/\s*arquivos|\bv\.\s*\d+\s*n\.\s*\d+', b['n'][:300]):
            inicios.append(k); conf[k] = ('media', 'página de artigo na web'); continue
        # partes de livro/volume (ficha catalográfica, sumário, índice) acompanham a capa/página anterior
        if re.match(r'\W*(dados internacionais de catalogacao|ficha catalografica|sumario\b|indice\b)', b['n'][:80]) and not a['vazio'] and not b['kw']:
            continue
        # o título desta página aparece no sumário da página anterior: é capítulo do mesmo livro
        titulo_b = re.sub(r'[^a-z0-9]', '', re.sub(r'^\W*capitulo\s*\d+\W*', '', b['n'][:200]))[:40]
        if not b['kw'] and len(titulo_b) >= 30 and titulo_b in re.sub(r'[^a-z0-9]', '', a['n']):
            continue
        # pacote de publicação (livro, anais, caderno de resumos): capa + ficha/copyright/sumário + a página do trabalho formam UMA evidência.
        # Começa numa capa (ou numa página que repete o topo de uma capa anterior); só termina em outra capa ou em início de documento forte.
        forte = b['kw'] in FORTE and not b['front'] and not CAPA[k]
        # logo depois de uma capa de fechamento (trabalho + capa da publicação) começa outra evidência
        if k == fecha_em and not b['front'] and not CAPA[k] and not (b['pag'] and b['pag'][0] > 1):
            inicios.append(k); conf[k] = ('media', 'depois da capa de fechamento'); em_pub = False
            continue
        # o título do trabalho repetido (página do trabalho + a mesma obra na web/anais) mantém as páginas juntas
        if not forte and not CAPA[k] and not b['front'] and a['kw'] != 'certificado':
            sa, sb = re.sub(r'[^a-z0-9]', '', a['n'][:300]), re.sub(r'[^a-z0-9]', '', b['n'][:400])
            if len(sa) >= 60 and len(sb) >= 60 and difflib.SequenceMatcher(None, sa, sb, autojunk=False).find_longest_match(0, len(sa), 0, len(sb)).size >= 40:
                continue
        repete = len(b['fp']) >= 20 and any(difflib.SequenceMatcher(None, b['fp'], f).ratio() >= 0.85 for f in capas)
        # página de artigo de periódico (ISSN + volume/número no topo) é evidência por si só, mesmo dentro de um pacote
        if not CAPA[k] and not repete and re.search(r'issn\W*\d{4}-?\d{3}[\dx].{0,140}v\W*\d+\W{0,3}n[pº°o]?\W*\d+', b['n'][:320]):
            inicios.append(k); conf[k] = ('media', 'página de artigo de periódico (ISSN, volume, número)')
            em_pub = False
            continue
        # capa isolada (sem ficha/capa logo depois) que vem depois de uma página de trabalho publicado: é a capa da publicação desse trabalho
        if CAPA[k] and not repete and a['kw'] == 'publicacao' and not a['front'] and not CAPA[k - 1]                 and not (k + 1 < N and (I[k + 1]['front'] or CAPA[k + 1])):
            em_pub = False
            fecha_em = k + 1
            continue
        if repete or (CAPA[k] and not forte):
            if em_pub and CAPA[k - 1]:
                continue  # capa seguida de outra página de capa (colorida/cinza, frente/verso, folha de rosto): mesma publicação
            inicios.append(k); conf[k] = ('media', 'capa repetida' if repete else 'capa de publicação')
            if len(b['fp']) >= 20:
                capas.append(b['fp'])
            em_pub = True
            continue
        if em_pub and not forte:
            continue
        if forte:
            em_pub = False
        # início explícito
        if b['kw'] and not b['cont']:
            # certificado com título repetido na verso é raro; considera novo documento
            inicios.append(k); conf[k] = ('alta' if not tam or b['kw'] != a['kw'] else 'media', f"palavra-chave '{b['kw']}'"); continue
        if b['cont']:
            continue
        if not tam:
            inicios.append(k); conf[k] = ('media', 'muda tamanho/orientação'); continue
        if fj is not None and fj < 0.15 and not b['vazio'] and not a['vazio']:
            inicios.append(k); conf[k] = ('media', 'muda conjunto de fontes'); continue
        if b['minus'] and not b['vazio']:
            continue
        # sem pistas: página sem palavra-chave, mesmo tamanho
        if b['vazio'] or a['vazio']:
            # imagem sem texto reconhecido: mantém junto se vier após outra página de imagem do mesmo tamanho (verso/continuação provável)
            if a['vazio'] and b['vazio'] and tam:
                continue
            inicios.append(k); conf[k] = ('baixa', 'página sem texto — decidido por tamanho'); continue
        if a['kw'] in ('historico', 'termo', 'projeto', 'publicacao') and not b['kw']:
            continue
        # texto nativo com o mesmo conjunto de fontes e tamanho, sem palavra de início: continuação (tabela/lista que segue na página seguinte)
        sub = bool(pa['fonts'] and pb['fonts'] and len(pa['fonts']) + len(pb['fonts']) >= 3
                   and (set(pa['fonts']) <= set(pb['fonts']) or set(pb['fonts']) <= set(pa['fonts'])))  # um conjunto contido no outro
        if fj is not None and (fj >= 0.8 or sub) and tam and not b['kw'] and not b['cover']:
            continue
        inicios.append(k); conf[k] = ('baixa', 'sem palavra-chave; assumido novo documento'); continue

    docs = []
    for idx, ini in enumerate(inicios):
        fim = (inicios[idx + 1] - 1) if idx + 1 < len(inicios) else N - 1
        tipos = [I[x]['kw'] for x in range(ini, fim + 1) if I[x]['kw']]
        tipo = rotulo[ini] or (tipos[0] if tipos else 'documento')
        docs.append(dict(ini=ini, fim=fim, tipo=tipo, conf=conf[ini][0], motivo=conf[ini][1],
                         titulo=re.sub(r'\s+', ' ', paginas[ini]['t']).strip()[:110]))
    return docs


def main():
    import pymupdf
    filtro = sys.argv[1:]
    os.makedirs(SAIDA, exist_ok=True)
    rel = ['# Separação das evidências por documento\n', 'Gerado por `ferramentas/separar_evidencias_inscricoes.py`. Confiança **baixa** = fronteira decidida sem indício forte: conferir.\n',
           '| Candidato | PDF | Páginas | Documentos | Fronteiras de baixa confiança |', '|---|---|---|---|---|']
    for c in sorted(glob.glob(os.path.join(CACHE, '*.json'))):
        cand = os.path.basename(c)[:5]
        if filtro and not any(cand.startswith(f) for f in filtro): continue
        d = json.load(open(c, encoding='utf-8'))
        pdf = d['arquivo']
        pasta_nome = os.path.basename(os.path.dirname(pdf))
        sub = os.path.join(SAIDA, pasta_nome)
        os.makedirs(sub, exist_ok=True)
        for velho in glob.glob(os.path.join(sub, '*.pdf')): os.remove(velho)
        docs = segmentar(d['paginas'])
        src = pymupdf.open(pdf)
        man = []
        for n, dc in enumerate(docs, 1):
            nome = f"{n:02d}_{dc['tipo']}_p{dc['ini']+1:03d}" + (f"-p{dc['fim']+1:03d}" if dc['fim'] > dc['ini'] else '') + '.pdf'
            out = pymupdf.open()
            out.insert_pdf(src, from_page=dc['ini'], to_page=dc['fim'])
            out.save(os.path.join(sub, nome), garbage=3, deflate=True)
            out.close()
            man.append(dict(arquivo=nome, paginas=[dc['ini'] + 1, dc['fim'] + 1], tipo=dc['tipo'], confianca=dc['conf'], motivo=dc['motivo'], titulo=dc['titulo']))
        json.dump(dict(origem=os.path.basename(pdf), total_paginas=len(d['paginas']), documentos=man), open(os.path.join(sub, 'manifesto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        baixos = sum(1 for m in man if m['confianca'] == 'baixa')
        rel.append(f"| {pasta_nome} | {os.path.basename(pdf)[:40]} | {len(d['paginas'])} | {len(man)} | {baixos} |")
        print(pasta_nome, len(d['paginas']), '->', len(man), 'docs', baixos, 'baixa', flush=True)
    if not filtro:
        open(os.path.join(SAIDA, 'RELATORIO.md'), 'w', encoding='utf-8').write('\n'.join(rel) + '\n')


if __name__ == '__main__':
    main()
