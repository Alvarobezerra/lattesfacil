"""Gera itens/especificacao/<id>.json a partir do mapeamento real dos formulários (docs/campos-lattes).

Cada especificação descreve, para um item do Lattes: como abrir o formulário, e todos os campos (nome técnico,
tipo, opções, limite, obrigatório, aba). É a fonte única para: formulário na tela, preenchimento no Lattes e testes.
Rode de novo se o mapeamento mudar:  python itens/gerar_specs.py
Curadoria manual (origem dos campos, regras de extração) fica em itens/curadoria.json e é mesclada aqui.
"""
import json, re, unicodedata, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MAPA = RAIZ / "docs" / "campos-lattes"
SAIDA = pathlib.Path(__file__).resolve().parent / "especificacao"

# id do classificador -> arquivos do mapeamento (e o nome de cada variante de formulário, quando há várias)
ITENS = {
    "participacao_evento": ["eventos/participacao-em-eventos-congressos-exposicoes-feiras-e-olimp.json"],
    "organizacao_evento": ["eventos/organizacao-de-eventos-congressos-exposicoes-feiras-e-olimpi.json"],
    "artigo": ["producoes/artigos-completos-publicados-em-periodicos.json"],
    "anais": ["producoes/trabalhos-publicados-em-anais-de-eventos.json"],
    "apresentacao": ["producoes/apresentacao-de-trabalho-e-palestra.json"],
    "artigo_aceito": ["producoes/artigos-aceitos-para-publicacao.json"],
    "livro_capitulo": ["producoes/livros-e-capitulos.json"],
    "banca": ["bancas/participacao-em-bancas-de-trabalhos-de-conclusao.json"],
    "curso_ministrado": ["producoes/curso-de-curta-duracao-ministrado.json"],
    "formacao_complementar": ["formacao/formacao-complementar.json"],
    "formacao_academica": ["formacao/formacao-academica-titulacao.json"],
    "atuacao_profissional": ["atuacao/atuacao-profissional.json"],
    "revisor_periodico": ["atuacao/revisor-de-periodico.json"],
    "corpo_editorial": ["atuacao/membro-de-corpo-editorial.json"],
    "patente": ["patentes-e-registros/patente.json"],
    "software_registro": ["patentes-e-registros/programa-de-computador-registrado.json"],
    "premio": ["dados-gerais/premios-e-titulos.json"],
    "projeto": ["projetos/projetos-de-pesquisa.json", "projetos/projeto-de-extensao.json", "projetos/projeto-de-ensino.json",
                "projetos/projeto-de-desenvolvimento-tecnologico.json", "projetos/outros-tipos-de-projetos.json"],
    "idioma": ["dados-gerais/idiomas.json"],
    "orientacao_concluida": ["orientacoes/orientacoes-e-supervisoes-concluidas.json"],
    "orientacao_andamento": ["orientacoes/orientacoes-e-supervisoes-em-andamento.json"],
    "licenca": ["dados-gerais/licenca-maternidade-paternidade-e-adocao.json"],
    "relatorio_tecnico": ["producoes/assessoria-e-consultoria.json"],
    # --- 43 itens restantes (só especificação: sem leitor de documento ainda) ---
    "comite_assessoramento": ["atuacao/membro-de-comite-de-assessoramento.json"],
    "revisor_projeto_fomento": ["atuacao/revisor-de-projeto-de-agencia-de-fomento.json"],
    "banca_comissao_julgadora": ["bancas/participacao-em-bancas-de-comissoes-julgadoras.json"],
    "citacao_outra_base": ["citacoes/citacoes-em-outra-base-bibliografica.json"],
    "citacao_google_scholar": ["citacoes/citacoes-no-google-scholar.json"],
    "citacao_scielo": ["citacoes/citacoes-no-scielo.json"],
    "citacao_scopus": ["citacoes/citacoes-no-scopus.json"],
    "citacao_web_of_science": ["citacoes/citacoes-no-web-of-science.json"],
    "endereco": ["dados-gerais/endereco.json"],
    "identificacao": ["dados-gerais/identificacao.json"],
    "outras_informacoes": ["dados-gerais/outras-informacoes-relevantes.json"],
    "texto_inicial": ["dados-gerais/texto-inicial-do-curriculo-lattes.json"],
    "pos_doutorado": ["formacao/pos-doutorado-e-ou-livre-docencia.json"],
    "cultivar_protegida": ["patentes-e-registros/cultivar-protegida.json"],
    "cultivar_registrada": ["patentes-e-registros/cultivar-registrada.json"],
    "desenho_industrial": ["patentes-e-registros/desenho-industrial-registrado.json"],
    "marca_registrada": ["patentes-e-registros/marca-registrada.json"],
    "topografia_circuito": ["patentes-e-registros/topografia-de-circuito-integrado-registrada.json"],
    "artes_cenicas": ["producoes/artes-cenicas.json"],
    "artes_visuais": ["producoes/artes-visuais.json"],
    "cartas_mapas": ["producoes/cartas-mapas-ou-similares.json"],
    "material_didatico": ["producoes/desenvolvimento-de-material-didatico-ou-instrucional.json"],
    "editoracao": ["producoes/editoracao.json"],
    "entrevista_midia": ["producoes/entrevistas-mesas-redondas-programas-e-comentarios-na-midia.json"],
    "extensao_tecnologica": ["producoes/extensao-tecnologica.json"],
    "manutencao_obra": ["producoes/manutencao-de-obra-artistica.json"],
    "maquete": ["producoes/maquete.json"],
    "musica": ["producoes/musica.json"],
    "outra_producao_artistica": ["producoes/outra-producao-artistica-cultural.json"],
    "outra_producao_bibliografica": ["producoes/outra-producao-bibliografica.json"],
    "outra_producao_tecnica": ["producoes/outra-producao-tecnica.json"],
    "partitura_musical": ["producoes/partitura-musical.json"],
    "prefacio_posfacio": ["producoes/prefacio-posfacio.json"],
    "processo_tecnica": ["producoes/processos-ou-tecnicas.json"],
    "produto": ["producoes/produtos.json"],
    "software_sem_registro": ["producoes/programa-de-computador-sem-registro.json"],
    "redes_sociais": ["producoes/redes-sociais-websites-e-blogs.json"],
    "relatorio_pesquisa": ["producoes/relatorio-de-pesquisa.json"],
    "texto_jornal_revista": ["producoes/texto-em-jornal-ou-revista-magazine.json"],
    "trabalho_tecnico": ["producoes/trabalhos-tecnicos.json"],
    "traducao": ["producoes/traducao.json"],
}


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode()


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", sem_acento(t).lower()).strip()


def opcoes_dict(op):
    """Normaliza opções: dict rótulo->valor, ou lista 'valor=rótulo' (a '=' vazia é o 'selecione')."""
    if isinstance(op, dict):
        return {str(k): str(v) for k, v in op.items()}
    out = {}
    for o in op or []:
        if "=" in str(o):
            v, _, r = str(o).partition("=")
            if r.strip():
                out[r.strip()] = v.strip()
    return out


def campos_do_formulario(f):
    obrig = [norm(x) for x in f.get("campos_obrigatorios_segundo_mensagens", [])]
    campos = []
    for aba in f.get("abas", []):
        for c in aba.get("campos", []):
            c = dict(c)
            c.setdefault("name", c.get("id", ""))
            if not c["name"]:
                continue
            rot = c.get("rotulo_provavel") or c.get("rotulo") or ""
            item = {
                "chave": re.sub(r"^f_", "", c["name"].lower()),
                "name": c["name"],
                "rotulo": rot or c["name"],
                "aba": aba.get("aba", ""),
                "tipo": c.get("tipo", "text"),
            }
            if c.get("maxlength"):
                item["maxlength"] = c["maxlength"]
            ops = opcoes_dict(c.get("opcoes"))
            if ops:
                item["opcoes"] = ops
            if c.get("catalogo"):
                item["catalogo"] = c["catalogo"]
            if c.get("oculto_inicialmente"):
                item["oculto"] = True
            r = norm(rot)
            item["obrigatorio"] = bool(r) and any(r == o or (len(r) > 3 and (r in o or o in r)) for o in obrig)
            campos.append(item)
    return campos


# Nome da variante quando o mapeamento traz só "único" (formulários de uma forma só, validados contra a captura real).
VARIANTE_UNICA = {"artigo": "Artigo completo publicado em periódico", "anais": "Trabalho publicado em anais de evento", "apresentacao": "Apresentação de trabalho e palestra",
                  "orientacao_concluida": "Orientação concluída", "orientacao_andamento": "Orientação em andamento",
                  "banca": "Participação em bancas de trabalhos de conclusão",
                  "banca_comissao_julgadora": "Participação em bancas de comissões julgadoras"}


GRADES = {  # aba do Lattes -> (chave, rótulo, dica de preenchimento)
    "autores": ("autores", "Autores", "Um por linha: Nome completo; Nome em citações (opcional)"),
    "participantes": ("autores", "Participantes da banca", "Um por linha: nome completo; nome em citações (opcional). O seu nome entra sozinho."),
    "palavras chave": ("palavras_chave", "Palavras-chave", "Uma por linha (até 50 caracteres cada)"),
    "areas": ("areas", "Áreas do conhecimento", "Uma por linha, com o nome exato da área do Lattes"),
    "setores": ("setores", "Setores de atividade", "Um por linha, com o nome exato do setor do Lattes"),
}


ITENS_COM_PARTICIPANTES = {"banca", "banca_comissao_julgadora"}  # aba "Participantes" = grade de autores (autorHolder), confirmada só nas bancas


# Moedas da janela "Instituição financeira" do Lattes (REAL primeiro; texto exato das opções).
MOEDAS_LATTES = ["REAL", "DOLAR AMERICANO", "UNIDADE MONET.EUROPEIA", "BOLIVAR VENEZUELANO", "BTN", "COROA DINAMARQUESA",
                 "COROA NORUEGUESA", "COROA SUECA", "COROA TCHECA", "CRUZADO", "CRUZADO NOVO", "CRUZEIRO (ATE 1986)", "CRUZEIRO REAL",
                 "CRUZEIRO (1990)", "DOLAR AUSTRALIANO", "DOLAR CANADENSE", "DOLAR NEOZELANDES", "ESCUDO PORTUGUES", "FLORINS HOLANDESES",
                 "FRANCO BELGA", "FRANCO FRANCES", "FRANCO SUICO", "INDEFINIDO", "LIBRA ESTERLINA", "LIRA ITALIANA", "MARCO ALEMAO",
                 "PESETAS", "PESO CHILENO", "PESO MEXICANO", "RANDE/AFRICA DO SUL", "RUBLO/RUSSIA", "UFIR", "URV", "XELIM AUSTRIACO", "YENE"]


# Grades que o formulário do Lattes tem em abas de lista e o mapeamento automático não nomeia (holders confirmados na captura da patente).
GRADES_EXTRA = {
    "patente": [
        {"chave": "situacoes", "rotulo": "Situação do Depósito/Patente", "aba": "Situação do Depósito/Patente",
         "dica": "Uma por linha: situação; data (dd/mm/aaaa). Ex.: Depósito; 26/02/2024 (também Concessão, Expiração, Depósito PCT, Pedido de exame)"},
        {"chave": "titulares_pessoa", "rotulo": "Depositante/Titular – Pessoas", "aba": "Depositante/Titular",
         "dica": "Uma pessoa por linha (nome completo), como no campo Pessoas do Lattes"},
        {"chave": "titulares_inst", "rotulo": "Depositante/Titular – Instituições", "aba": "Depositante/Titular",
         "dica": "Uma instituição por linha, como no campo Instituições do Lattes. Ex.: Universidade Federal do Maranhão"},
        {"chave": "autores", "rotulo": "Inventores", "aba": "Inventores",
         "dica": "Um por linha: nome completo; nome em citações (opcional). O seu nome só entra se constar entre os inventores."},
    ],
    "artigo": [
        {"chave": "autores", "rotulo": "Autores", "aba": "Autores",
         "dica": "Um por linha: Nome completo; Nome em citações (opcional). Na ordem de autoria do artigo."},
    ],
    # Aba Equipe e Instituição de financiamento dos projetos (formulário real conferido em 18/11/2026).
    "projeto": [
        {"chave": "autores", "rotulo": "Pesquisadores", "aba": "Equipe",
         "dica": "Um por linha: nome completo; nome em citações (opcional); coordenador (opcional). O seu nome entra sozinho. Ex.: Maria de Sousa Lima; LIMA, M. S.; coordenador"},
        {"chave": "instituicoes_envolvidas", "rotulo": "Instituições envolvidas no projeto", "aba": "Equipe",
         "dica": "Uma por linha, com o nome como no cadastro do Lattes (lupa \"Selecionar\")"},
        {"chave": "financiamentos", "rotulo": "Instituição de financiamento", "aba": "Equipe",
         "dica": "O valor financiado não será exibido na internet.",
         "colunas": [
             {"rotulo": "Instituição", "dica": "Nome como no cadastro do Lattes (lupa)"},
             {"rotulo": "Código do projeto", "maxlength": 20, "numerico": True},
             {"rotulo": "Moeda", "opcoes": MOEDAS_LATTES, "padrao": "REAL"},
             {"rotulo": "Valor financiado", "maxlength": 19, "valor": True},
             {"rotulo": "Natureza", "opcoes": ["Auxílio Financeiro", "Bolsa", "Remuneração", "Cooperação", "Outra"]},
         ]},
    ],
}

# Abas do Lattes que só vinculam itens já cadastrados no currículo (não dá para criar a partir do documento).
ABAS_INFORMATIVAS = {
    "projeto": [
        {"aba": "Produção C & T", "colunas": ["Título da produção", "Ano", "Tipo"], "nota": "Lista de produções do seu currículo (título, ano, tipo) que resultaram do projeto. É um vínculo com itens já cadastrados: vincule no Lattes depois de incluir as produções."},
        {"aba": "Orientações", "colunas": ["Título da orientação", "Ano", "Tipo"], "nota": "Lista de orientações do seu currículo (título, ano, tipo) ligadas ao projeto. É um vínculo com itens já cadastrados: vincule no Lattes depois de incluir as orientações."},
    ],
}


def grades_do_formulario(f, item_id=""):
    """Abas de lista (sem campos nomeados) que o preenchedor genérico sabe preencher."""
    out = []
    for aba in f.get("abas", []):
        nome_aba = norm(aba.get("aba", ""))
        if nome_aba == "participantes" and item_id not in ITENS_COM_PARTICIPANTES:
            continue
        g = GRADES.get(nome_aba)
        if g:
            out.append({"chave": g[0], "rotulo": g[1], "dica": g[2], "aba": aba.get("aba", "")})
    out.extend(dict(g) for g in GRADES_EXTRA.get(item_id, []) if g["chave"] not in {x["chave"] for x in out})
    return out


def carregar_padroes():
    p = pathlib.Path(__file__).resolve().parent / "padroes_campos.json"
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {k.lower(): v for k, v in d.get("campos", {}).items()}


def aplicar_padroes_comuns(campos, padroes):
    """Preenche 'padrao' (+ origem e 'confira') nos campos repetidos entre formulários, sem sobrepor a curadoria."""
    for c in campos:
        pd = padroes.get(c["name"].lower())
        if not pd or c.get("padrao"):
            continue
        if "codigo" in pd:
            chave = next((r for r, cod in (c.get("opcoes") or {}).items() if cod == pd["codigo"]), None)
            if not chave:
                continue
            c["padrao"] = chave
        else:
            c["padrao"] = pd["valor"]
        c["origem_padrao"] = "padrao_comum"
        c["confira"] = True


# Radios Sim/Não repetidos entre formulários: a captura trouxe opções trocadas ("Não"="S", "N"="N") e o nome técnico como rótulo.
# No Lattes são radios "Sim" (S) / "Não" (N), padrão Não. Rótulos conforme o formulário real (conferido em 18/11/2026).
RADIOS_SIM_NAO = {
    "f_tpo_pesq_emp": "É um projeto de cooperação instituição de pesquisa e empresa?",
    "f_sta_inovacao": "O projeto possui potencial de inovação de produtos, processos ou serviços?",
}
# Campos que o Lattes só mostra quando o radio correspondente está em "Sim".
MOSTRAR_QUANDO = {
    "f_cnpj_empresa": "f_tpo_pesq_emp", "f_txt_nme_empresa": "f_tpo_pesq_emp",
    "f_txt_email_institucional": "f_tpo_pesq_emp", "f_txt_setor": "f_tpo_pesq_emp",
    "f_txt_potencial": "f_sta_inovacao",
}
SOMENTE_LEITURA = {"f_txt_nme_empresa": "O Lattes preenche o nome da empresa a partir do CNPJ (campo somente leitura)."}


# Projeto de ensino: o formulário real tem outros textos e grupos de caixas de marcação (conferido em 18/11/2026).
ENSINO_ROTULOS = {
    "f_sta_inovacao": "O projeto possui ações inovadoras e produtos, processos ou serviços?",
    "f_tpo_cooperacao": "É um projeto em cooperação com:",
    "f_tpo_acao_inov": "O projeto possui ações inovadoras na:",
    "f_tematica": "Em relação a temática:",
}
ENSINO_OCULTOS = {"f_tpo_pesq_emp"}  # existe no formulário, mas não aparece para o usuário
ENSINO_MOSTRAR_QUANDO = {"f_especifique": {"name": "f_tematica", "valor": "Outra"}}


# Artigo em periódico (formulário real conferido em 20/11/2026, abertura manual por ISSN/periódico/volume/página).
ARTIGO_ROTULOS = {
    "f_relev": "É um dos 10 trabalhos mais relevantes de sua produção?",
    "f_sta_divulgacao_cientifica": "É uma produção para educação e popularização de CeT?",
}


# Orientação concluída/em andamento (formulário real conferido em 21/11/2026).
ORIENT_ROTULOS = {"f_cod_prod": "Natureza", "f_tpo_orient": "Tipo de orientação (apenas para dissertação de mestrado e tese de doutorado)",
                  "f_bolsa": "Com bolsa?", "f_dsc_outra": "Tipo (apenas para dissertação de mestrado e orientação de outra natureza)"}


# Trabalho em anais (formulário real conferido em 21/11/2026): rótulos dos grupos de radio.
ANAIS_ROTULOS = {"f_cod_prod": "Natureza", "f_tipo_evento": "Classificação do evento"}


def espelhar_lattes(campos, item_id="", variante=""):
    nomes = {c["name"].lower() for c in campos}
    if item_id in ("orientacao_concluida", "orientacao_andamento"):
        for c in campos:
            n = c["name"].lower()
            if n in ORIENT_ROTULOS:
                c["rotulo"] = ORIENT_ROTULOS[n]
            if n == "f_nme_agencia":
                c["lupa"] = True  # o Lattes só aceita a agência escolhida na lista ("Utilize o link para selecionar a agência")
                c["dica"] = "Escolhida na lista de agências do Lattes (a plataforma escolhe pela sigla ou nome idêntico)."
            if n == "f_dsc_outra":
                c["obrigatorio"] = False  # só vale para dissertação de mestrado e orientação de outra natureza (campo bloqueado nas demais)
            if n == "f_tpo_orient":
                c["obrigatorio"] = False  # só vale para dissertação de mestrado e tese de doutorado (exige_antes); nas demais o Lattes recusa
            if n in ARTIGO_ROTULOS or n == "f_bolsa":
                if n in ARTIGO_ROTULOS:
                    c["rotulo"] = ARTIGO_ROTULOS[n]
                c["opcoes"] = {"Sim": "S", "Não": "N"}
    if item_id in ("banca", "banca_comissao_julgadora"):
        for c in campos:
            if c["name"].lower() == "f_cod_prod":
                c["rotulo"] = "Natureza"
            if c["name"].lower() == "f_sub_prod" and item_id == "banca":
                c["opcoes"] = {"Acadêmico": "34 ", "Profissional": "35 "}  # o Lattes grava os valores com espaço no fim
                c["rotulo"] = "(apenas para mestrado)"
        nat = next((c for c in campos if c["name"].lower() == "f_cod_prod"), None)
        if nat and nat.get("opcoes"):
            for c in campos:  # o Lattes responde "Informe a natureza" se a lupa de instituição/curso for usada antes de escolher a natureza
                if c["name"].lower() == "f_inst" and item_id == "banca_comissao_julgadora":
                    c["obrigatorio"] = True  # asterisco vermelho ao lado do campo no Lattes (a mensagem de obrigatórios do servidor não o inclui)
                if c["name"].lower() in ("f_inst", "f_curso"):
                    c["exige_antes"] = {"name": nat["name"], "valores": list(nat["opcoes"].keys())}
                if c["name"].lower() == "f_sub_prod" and item_id == "banca":
                    c["exige_antes"] = {"name": nat["name"], "valores": ["Mestrado"]}
    if item_id in ("anais", "apresentacao"):
        for c in campos:
            n = c["name"].lower()
            if n in ANAIS_ROTULOS:
                c["rotulo"] = ANAIS_ROTULOS[n]
            if n in ARTIGO_ROTULOS:
                c["rotulo"] = ARTIGO_ROTULOS[n]
                c["opcoes"] = {"Sim": "S", "Não": "N"}
    if item_id == "artigo":
        for c in campos:
            n = c["name"].lower()
            if n in ARTIGO_ROTULOS:
                c["rotulo"] = ARTIGO_ROTULOS[n]
                c["opcoes"] = {"Sim": "S", "Não": "N"}
            if n == "f_jcr":
                c["bloqueado_no_lattes"] = True  # o Lattes preenche o fator de impacto a partir do periódico; o campo aparece bloqueado
                c["dica"] = "O Lattes preenche o fator de impacto (JCR) a partir do periódico; campo bloqueado."
            if n in ("f_titulo_periodico", "f_issn", "f_volume", "f_serie", "f_pag_ini"):
                # Na abertura manual o Lattes recebe esses dados pelo endereço (janela "Informar dados") e os bloqueia no formulário.
                c["bloqueado_no_lattes"] = True
                c["dica"] = "Informado na abertura (ISSN, periódico, volume, edição e página inicial); fica bloqueado no formulário do Lattes."
    ensino = item_id == "projeto" and variante == "Projeto de ensino"
    for c in campos:
        n = c["name"].lower()
        if ensino:
            if n in ENSINO_ROTULOS:
                c["rotulo"] = ENSINO_ROTULOS[n]
            if n in ENSINO_OCULTOS:
                c["oculto"] = True
            if n in ENSINO_MOSTRAR_QUANDO:
                c["mostrar_quando"] = ENSINO_MOSTRAR_QUANDO[n]
        if c.get("tipo") == "radio" and n in RADIOS_SIM_NAO:
            c["opcoes"] = {"Sim": "S", "Não": "N"}
            if c.get("rotulo", "") in ("", c["name"]) and not (ensino and n in ENSINO_ROTULOS):
                c["rotulo"] = RADIOS_SIM_NAO[n]
        gatilho = MOSTRAR_QUANDO.get(n)
        if gatilho and gatilho in nomes:
            c["mostrar_quando"] = {"name": gatilho, "valor": "Sim"}
        if n in SOMENTE_LEITURA:
            c["dica"] = SOMENTE_LEITURA[n]
        if item_id == "projeto":
            # Regras lidas do check() do formulário real (18-20/11/2026): Ano fim só é exigido (e só é aceito) quando a situação é
            # "Concluído"; com cooperação com empresa em Sim exige CNPJ, e-mail institucional e setor; com inovação em Sim exige o potencial.
            if n == "f_ano_fim":
                c["obrigatorio"] = False
                c["obrigatorio_quando"] = {"name": "F_TPO_SITUACAO", "valor": "Concluído"}
            if n in ("f_cnpj_empresa", "f_txt_email_institucional", "f_txt_setor", "f_txt_potencial"):
                c["obrigatorio"] = True  # só vale quando o campo está visível (condicional)
            if n in ("f_inst", "f_orgao"):
                c["obrigatorio"] = True  # o Lattes recusa o salvamento do Projeto de ensino sem instituição e órgão (confirmado em 20/11/2026)


REFS = RAIZ / "docs" / "campos-lattes" / "ref"


def opcoes_reais_da_captura(item_id, var_):
    """Seleções por catálogo em que o Lattes oferece só parte do catálogo (ex.: 80 de 152 idiomas no artigo): usa a lista real da captura."""
    ref = None
    for cap in sorted((REFS / item_id).glob("*.json")) if (REFS / item_id).exists() else []:
        if cap.name == "excecoes.json":
            continue
        r_ = json.loads(cap.read_text(encoding="utf-8"))
        if norm(r_.get("variante", "")) == norm(var_.get("variante", "")):
            ref = r_
            break
    if ref is None:
        return
    por_nome = {c["name"].lower(): c for c in ref.get("campos", [])}
    for c in var_["campos"]:
        r = por_nome.get(c["name"].lower())
        # radios com texto de opção diferente do Lattes (ex.: texto cortado no mapeamento antigo): usa o texto real da captura (mesmos valores)
        if r and c.get("tipo") == "radio" and c.get("opcoes") and r.get("opcoes"):
            reais_r = {o["texto"]: o["valor"] for o in r["opcoes"] if o.get("texto") and o.get("valor") not in ("", "DUMMY")}
            if reais_r and set(reais_r.values()) == set(c["opcoes"].values()) and not all(norm(k) in ("sim", "nao") for k in reais_r):
                c["opcoes"] = reais_r
        if not r or c.get("tipo") != "select" or not c.get("catalogo") or c.get("opcoes") or c["name"].lower() in ("f_pais_inst",):
            continue
        reais = {o["texto"]: o["valor"] for o in r.get("opcoes", []) if o.get("valor") not in ("", "DUMMY", "Selecione") and o.get("texto")}
        cat = json.loads((MAPA / c["catalogo"]).read_text(encoding="utf-8"))
        todos = {v["valor"] for v in cat.get("valores", []) if v.get("valor")}
        if reais and set(reais.values()) < todos:
            c["opcoes"] = reais
            c["catalogo_completo"] = c.pop("catalogo")  # o app oferece só o que o Lattes oferece neste formulário


def dependencias_da_captura(item_id, var_):
    """Dependências entre campos descobertas na captura (aceitação): o Lattes só aceita o valor do campo depois que outro campo é escolhido
    (ex.: tipo de orientação só com natureza mestrado/doutorado). Vira `exige_antes` no spec; o app desabilita o campo até lá e a matriz escolhe antes."""
    ref = None
    for cap in sorted((REFS / item_id).glob("*.json")) if (REFS / item_id).exists() else []:
        if cap.name == "excecoes.json":
            continue
        r_ = json.loads(cap.read_text(encoding="utf-8"))
        if norm(r_.get("variante", "")) == norm(var_.get("variante", "")):
            ref = r_
            break
    if not ref:
        return
    por_nome = {c["name"].lower(): c for c in var_["campos"]}
    for acc in ref.get("aceitacao", []):
        alvo = por_nome.get(acc["campo"].lower())
        if not alvo or not acc.get("depende"):
            continue
        dep = acc["depende"][0]
        gat = por_nome.get(dep["gatilho"].lower())
        if not gat:
            continue
        rotulos = []
        for v in dep["valores"]:
            rot = next((k for k, cod in (gat.get("opcoes") or {}).items() if cod == v["valor"] or cod.endswith(str(v["valor"])) or str(v["valor"]).endswith(cod)), None)
            rotulos.append(rot or v["texto"])
        alvo["exige_antes"] = {"name": gat["name"], "valores": rotulos}


def gerar():
    SAIDA.mkdir(exist_ok=True)
    cur_p = pathlib.Path(__file__).resolve().parent / "curadoria.json"
    curadoria = json.loads(cur_p.read_text(encoding="utf-8")) if cur_p.exists() else {}
    padroes = carregar_padroes()
    resumo = []
    for item_id, arquivos in ITENS.items():
        variantes = []
        for rel in arquivos:
            d = json.loads((MAPA / rel).read_text(encoding="utf-8"))
            inicio = len(variantes)
            for i, f in enumerate(d.get("formularios", [])):
                variantes.append({
                    "variante": VARIANTE_UNICA.get(item_id) or f.get("nome") or f.get("formulario") or (d["item"] if len(arquivos) > 1 else (f"Formulário {i + 1}" if len(d.get("formularios", [])) > 1 else "único")),
                    "url": f.get("url", ""),
                    "abertura": d.get("abertura", {}),
                    "janelas_auxiliares": f.get("janelas_auxiliares", []),
                    "campos": campos_do_formulario(f),
                    "grades": grades_do_formulario(f, item_id),
                    **({"abas_informativas": ABAS_INFORMATIVAS[item_id]} if item_id in ABAS_INFORMATIVAS else {}),
                    "obrigatorios_mensagens": f.get("campos_obrigatorios_segundo_mensagens", []),
                })
            primeiro = d
            over = curadoria.get(item_id, {}).get("campos", {})
            for var_ in variantes[inicio:]:
                for c in var_["campos"]:
                    c.update(over.get(c["name"], {}))
                espelhar_lattes(var_["campos"], item_id, var_.get("variante", ""))
                opcoes_reais_da_captura(item_id, var_)
                dependencias_da_captura(item_id, var_)
                aplicar_padroes_comuns(var_["campos"], padroes)
        spec = {
            "id": item_id,
            "lista": (json.loads((pathlib.Path(__file__).resolve().parent / "listas_lattes.json").read_text(encoding="utf-8")).get(item_id, "")),
            "secao": primeiro.get("secao", ""),
            "item": primeiro.get("item", ""),
            "como_abrir": primeiro.get("como_abrir", ""),
            "salvar": "O LattesFácil nunca clica em Salvar sozinho; o usuário confere e salva.",
            "variantes": variantes,
            "curadoria": curadoria.get(item_id, {}),
        }
        (SAIDA / f"{item_id}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        resumo.append((item_id, len(variantes), sum(len(v["campos"]) for v in variantes), sum(c["obrigatorio"] for v in variantes for c in v["campos"])))
    return resumo


if __name__ == "__main__":
    for r in gerar():
        print("%-22s variantes=%d campos=%d obrigatorios=%d" % r)
