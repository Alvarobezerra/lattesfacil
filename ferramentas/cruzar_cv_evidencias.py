"""Cruza cada evidência segmentada com o lançamento do Lattes do mesmo candidato.

Para cada candidato do circuito de teste:
  1. lê o texto das páginas (cache do OCR) e o manifesto da segmentação;
  2. quebra o bloco Lattes em seções e lançamentos;
  3. casa cada evidência com o lançamento mais parecido (palavras raras do
     lançamento presentes no texto da evidência);
  4. compara a seção do lançamento com o item que o gabarito espera.

Saída: docs/validacao/cruzamento_cv_evidencias.md e .json (dados pessoais:
não enviar a serviço externo, não commitar sem pedido do usuário).

Uso: python ferramentas/cruzar_cv_evidencias.py [prefixo ...]
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "tests" / "curriculos e modelos"
CACHE = BASE / "_cache_texto_paginas"
SEPARADAS = BASE / "2_EVIDENCIAS_SEPARADAS"
GABARITOS = RAIZ / "tests" / "gabarito_ocr"
SAIDA = RAIZ / "docs" / "validacao"

# cabeçalho de seção (texto normalizado) -> (rótulo da seção, itens compatíveis)
SECOES = [
    (r"^formacaoacademica", "Formação acadêmica", {"formacao_academica"}),
    (r"^formacaocomplementar", "Formação complementar", {"formacao_complementar"}),
    (r"^atuacaoprofissional", "Atuação profissional", {"atuacao_profissional"}),
    (r"^projetos?depesquisa", "Projetos de pesquisa", {"projeto"}),
    (r"^projetos?deextensao", "Projetos de extensão", {"projeto"}),
    (r"^projetos?dedesenvolvimento", "Projetos de desenvolvimento", {"projeto"}),
    (r"^participacaoemprojetos?", "Projetos", {"projeto"}),
    (r"^projetos$", "Projetos", {"projeto"}),
    (r"^artigos(completos)?(publicados|noprelo)", "Artigos publicados", {"artigo"}),
    (r"^livros(publicados|organizados)", "Livros", {"livro_capitulo"}),
    (r"^capitulosdelivros", "Capítulos de livros", {"livro_capitulo"}),
    (r"^trabalhos(completos)?(publicados)?emanais|^resumos(simples|expandidos|publicados)", "Trabalhos em anais", {"anais", "apresentacao"}),
    (r"^apresentacoes?detrabalho", "Apresentação de trabalho", {"apresentacao", "anais"}),
    (r"^participacaoemeventos", "Participação em eventos", {"participacao_evento", "apresentacao"}),
    (r"^organizacaodeeventos?", "Organização de eventos", {"organizacao_evento"}),
    (r"^orientacoes", "Orientações", {"orientacao_concluida", "orientacao_andamento"}),
    (r"^participacaoembancas|^bancas", "Bancas", {"banca"}),
    (r"^producaotecnica", "Produção técnica", {"relatorio_tecnico", "produto_tecnico"}),
    (r"^trabalhostecnicos", "Trabalhos técnicos", {"relatorio_tecnico"}),
    (r"^premiosetitulos", "Prêmios e títulos", {"premio"}),
]
IGNORA = r"^(idiomas|areasdeatuacao|linhasdepesquisa|areasdoconhecimento|citacoes|producao$|producoes$|eventos$|identificacao|enderec)"

PARADA = set("""para como pelo pela pelos pelas desta deste esta este esse essa entre sobre com sem uma uns umas dos das nos nas
brasil carga horaria curso cursos universidade federal centro faculdade instituto escola ensino superior estado estadual
municipal secretaria participacao evento eventos congresso anais periodicos publicado publicados atual vinculo outras
informacoes areas conhecimento grande area especialidade setores atividade atividades projeto projetos pesquisa
certificamos certificado certifica declaramos declaracao aluno participante organizador realizado realizada promovido
promovida periodo duracao horas total aprovado aprovada numero data nome cpf registro autenticidade verificacao codigo""".split())


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[ \t\xa0]+", " ", s.lower()).strip()


def tokens(s: str) -> set[str]:
    out = set()
    for t in re.findall(r"[a-z0-9]+", norm(s)):
        if t in PARADA:
            continue
        if t.isdigit():
            if len(t) == 4 and t.startswith(("19", "20")):
                out.add(t)
            continue
        if len(t) >= 4:
            out.add(t)
    return out


def carregar(prefixo: str):
    cache = json.loads((CACHE / f"{prefixo}_Q13.json").read_text(encoding="utf-8"))
    pastas = [p for p in SEPARADAS.iterdir() if p.name.startswith(prefixo + "_")]
    if not pastas:
        return None
    pasta = pastas[0]
    man = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    gab = GABARITOS / f"{prefixo}.json"
    gabarito = json.loads(gab.read_text(encoding="utf-8")) if gab.exists() else {"casos": []}
    return cache["paginas"], man, gabarito, pasta.name


def secoes_e_lancamentos(linhas: list[str]) -> list[dict]:
    """Percorre as linhas do bloco Lattes e devolve os lançamentos com a seção."""
    sec = ("Seção não identificada", set())
    entradas: list[dict] = []
    atual: dict | None = None
    ano_rx = re.compile(r"^(\d{4})(\s*-\s*(\d{4}|atual))?\s*$", re.I)
    num_rx = re.compile(r"^\d{1,3}\.\s*(.*)$")

    def fecha():
        nonlocal atual
        if atual and atual["texto"].strip():
            entradas.append(atual)
        atual = None

    for i, bruta in enumerate(linhas):
        l = bruta.strip()
        if not l:
            continue
        n = re.sub(r'\s+', '', norm(l))
        achou = None
        if len(l) < 95:
            for rx, rot, itens in SECOES:
                if re.match(rx, n):
                    achou = (rot, itens)
                    break
        if achou:
            fecha()
            sec = achou
            continue
        if re.match(IGNORA, n) and len(l) < 60 and not achou:
            # o PDF do Lattes em duas colunas embaralha a ordem: não troca a seção
            continue
        if sec is None:
            continue
        inicio = False
        if ano_rx.match(l):
            inicio = True
        elif num_rx.match(l) and sec[0] not in ("Formação acadêmica", "Formação complementar"):
            inicio = True
        elif sec[0] in ("Participação em eventos", "Organização de eventos", "Apresentação de trabalho") and re.match(r"^\d{4}\s+\S", l):
            inicio = True
        if inicio:
            fecha()
            atual = {"secao": sec[0], "itens": sorted(sec[1]), "texto": ""}
            if sec[0] == "Atuação profissional" and i > 0:
                atual["texto"] = linhas[i - 1].strip() + "\n"
        if atual is not None:
            atual["texto"] += l + "\n"
    fecha()
    for e in entradas:
        inferir(e)
    # em atuação, a linha da instituição aparece antes do ano: o fecha() anterior
    # a levou para o lançamento anterior; tira-a de lá para não duplicar
    return entradas


def inferir(e: dict) -> None:
    """Corrige a seção pelo conteúdo: o PDF em duas colunas traz o cabeçalho depois das linhas."""
    t = norm(e["texto"])
    if e["secao"] not in ("Formação acadêmica", "Formação complementar", "Atuação profissional", "Seção não identificada"):
        return
    corpo = re.sub(r"^\s*\d{4}(\s*-\s*(\d{4}|atual))?\s*", "", t)
    novo = None
    if re.search(r"v\.\s*\d+.{0,40}p\.\s*\d+|issn|journal|revista", t, re.S) and re.match(r"\d{1,3}\.", t.strip()):
        novo = ("Artigos publicados", {"artigo"})
    elif re.match(r"\d{1,3}\.\s", t.strip()) and e["secao"] in ("Formação acadêmica", "Formação complementar", "Atuação profissional", "Seção não identificada") and not re.search(r"vinculo:|carga\s*hor", t):
        novo = ("Produção (seção do PDF embaralhada)", {"artigo", "livro_capitulo", "anais", "apresentacao", "participacao_evento", "organizacao_evento", "projeto"})
    elif re.search(r"vinculo:|enquadramento\s*funcional", t):
        novo = ("Atuação profissional", {"atuacao_profissional"})
    elif re.match(r"(graduacao|mestrado|doutorado|especializacao|ensino medio|residencia|pos-?doutorado|curso tecnico|ensino fundamental)", corpo) or re.search(r"orientador:|\btitulo:", t):
        novo = ("Formação acadêmica", {"formacao_academica"})
    elif re.search(r"carga\s*hor", t):
        novo = ("Formação complementar", {"formacao_complementar"})
    if novo:
        e["secao"], e["itens"] = novo[0], sorted(novo[1])


def titulo_curto(txt: str) -> str:
    linhas = [x.strip() for x in txt.split("\n") if x.strip()]
    linhas = [x for x in linhas if not ano_so(x)]
    return " ".join(linhas[:2])[:110]


def trecho(txt: str, E: set[str]) -> str:
    """Frase do lançamento que mais tem palavras em comum com a evidência."""
    junto = re.sub(r"\s+", " ", txt)
    frases = [f for f in re.split(r"(?<=[.;])\s+", junto) if len(f) > 8]
    if not frases:
        return junto[:110]
    melhor = max(frases, key=lambda f: len(tokens(f) & E))
    return melhor[:120]


def janelas(linhas: list[str]) -> list[dict]:
    """Lançamentos aproximados de um Lattes escaneado: janelas de 3 linhas por seção."""
    out, sec, buf = [], None, []
    def solta():
        for i in range(0, max(len(buf) - 1, 0), 2):
            out.append({"secao": sec[0], "itens": sorted(sec[1]), "texto": "\n".join(buf[i:i + 3])})
    for bruta in linhas:
        l = bruta.strip()
        if not l:
            continue
        n = re.sub(r"\s+", "", norm(l))
        achou = None
        if len(l) < 95:
            for rx, rot, itens in SECOES:
                if re.match(rx, n):
                    achou = (rot, itens)
                    break
        if achou:
            if sec:
                solta()
            sec, buf = achou, []
        elif sec:
            buf.append(l)
    if sec:
        solta()
    return out


def ano_so(x: str) -> bool:
    return bool(re.match(r"^\d{4}(\s*-\s*(\d{4}|atual))?$", x, re.I)) or bool(re.match(r"^\d{1,3}\.$", x))


def cruzar(prefixo: str) -> dict | None:
    r = carregar(prefixo)
    if not r:
        return None
    paginas, man, gab, nome = r
    docs = man["documentos"]
    pag_lattes: list[int] = []
    for d in docs:
        if d["tipo"] == "lattes":
            pag_lattes += list(range(d["paginas"][0], d["paginas"][1] + 1))
    linhas = []
    for n in pag_lattes:
        linhas += paginas[n - 1]["t"].split("\n")
    entradas = secoes_e_lancamentos(linhas)
    # idf por token entre os lançamentos do próprio candidato
    df: dict[str, int] = {}
    for e in entradas:
        e["tok"] = tokens(e["texto"])
        for t in e["tok"]:
            df[t] = df.get(t, 0) + 1
    N = max(len(entradas), 1)
    peso = lambda t: math.log((N + 1) / (df.get(t, 0) + 0.5)) + 0.2  # noqa: E731

    # CV escaneado (OCR ruidoso, sem anos/numeração confiáveis): janelas de linhas
    if len(entradas) < 5 and len(linhas) > 40:
        entradas = janelas(linhas)
        for e in entradas:
            e["tok"] = tokens(e["texto"])
        df = {}
        for e in entradas:
            for t in e["tok"]:
                df[t] = df.get(t, 0) + 1
    N = max(len(entradas), 1)

    # o gabarito pode usar outros nomes de arquivo: casa pela página inicial (_pNNN)
    esperado = {}
    for c in gab.get("casos", []):
        m = re.search(r"_p(\d+)", c["arquivo"]) or re.search(r"^\d+_p(\d+)", c["arquivo"])
        if m:
            esperado[int(m.group(1))] = c
    usados: dict[int, list[str]] = {}
    evid = []
    for d in docs:
        if d["tipo"] in ("lattes", "ficha"):
            continue
        a, b = d["paginas"]
        txt = "\n".join(paginas[n - 1]["t"] for n in range(a, b + 1))
        E = tokens(txt)
        cand = []
        for k, e in enumerate(entradas):
            T = e["tok"]
            if len([t for t in T if not t.isdigit()]) < 2:
                continue  # lançamento sem palavras próprias casaria com qualquer coisa
            tot = sum(peso(t) for t in T)
            com = sum(peso(t) for t in T & E)
            cand.append((com / tot if tot else 0.0, k))
        cand.sort(reverse=True)
        caso = esperado.get(a, {})
        item = caso.get("item_esperado")
        melhor = cand[0] if cand else (0.0, -1)
        # melhor dentro das seções compatíveis com o item esperado
        compat = [c for c in cand if item in entradas[c[1]]["itens"]]
        melhor_compat = compat[0] if compat else None
        reg = {
            "arquivo": d["arquivo"], "paginas": d["paginas"], "item_esperado": item,
            "melhor": None, "melhor_na_secao_esperada": None, "veredito": "",
        }
        def resumo(c):
            s, k = c
            e = entradas[k]
            return {"score": round(s, 2), "secao": e["secao"], "lancamento": trecho(e["texto"], E)}
        if item is None and d["tipo"] != "lattes" and melhor[1] >= 0 and melhor[0] >= 0.45:
            reg["melhor"] = resumo(melhor)
            usados.setdefault(melhor[1], []).append(d["arquivo"])
            reg["veredito"] = "SEM GABARITO: o CV lançou em " + entradas[melhor[1]]["secao"]
        elif item in (None, "__ficha__", "__cv__"):
            reg["veredito"] = "sem item esperado (ficha/CV/sem gabarito)"
        elif melhor[0] >= 0.45:
            reg["melhor"] = resumo(melhor)
            usados.setdefault(melhor[1], []).append(d["arquivo"])
            if item in entradas[melhor[1]]["itens"]:
                reg["veredito"] = "OK: lançado na seção compatível com o item"
            elif melhor_compat and melhor_compat[0] >= 0.45:
                reg["melhor_na_secao_esperada"] = resumo(melhor_compat)
                usados.setdefault(melhor_compat[1], []).append(d["arquivo"])
                reg["veredito"] = "OK: existe lançamento também na seção compatível"
            else:
                reg["veredito"] = "DIVERGE: o CV lançou em outra seção que a do item esperado"
        else:
            if melhor_compat and melhor_compat[0] >= 0.35:
                reg["melhor_na_secao_esperada"] = resumo(melhor_compat)
                usados.setdefault(melhor_compat[1], []).append(d["arquivo"])
                reg["veredito"] = "FRACO: lançamento provável na seção compatível, pouca evidência de texto"
            elif melhor_compat and melhor_compat[0] >= 0.18 and melhor_compat[0] >= melhor[0] - 0.05:
                reg["melhor_na_secao_esperada"] = resumo(melhor_compat)
                usados.setdefault(melhor_compat[1], []).append(d["arquivo"])
                reg["veredito"] = "FRACO: lançamento provável na seção compatível (texto da evidência pobre, conferir)"
            else:
                reg["melhor"] = resumo(melhor) if cand else None
                reg["veredito"] = "SEM LANÇAMENTO: nada no CV casa com esta evidência"
        evid.append(reg)
    sem_evid = []
    for k, e in enumerate(entradas):
        if k not in usados:
            sem_evid.append({"secao": e["secao"], "lancamento": titulo_curto(e["texto"])})
    return {
        "candidato": nome, "prefixo": prefixo, "paginas_lattes": [pag_lattes[0], pag_lattes[-1]] if pag_lattes else None,
        "lancamentos_no_cv": len(entradas), "evidencias": evid, "lancamentos_sem_evidencia": sem_evid,
        "por_secao": {s: sum(1 for e in entradas if e["secao"] == s) for s in sorted({e["secao"] for e in entradas})},
    }


def main():
    prefixos = sys.argv[1:] or sorted(p.name.split("_")[0] for p in CACHE.glob("*_Q13.json"))
    resultados = []
    for p in prefixos:
        r = cruzar(p)
        if r:
            resultados.append(r)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "cruzamento_cv_evidencias.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# Cruzamento: evidência x lançamento no Lattes", "",
          "Gerado por `ferramentas/cruzar_cv_evidencias.py`. Contém dados de candidatos: não enviar a serviço externo.",
          "O casamento é automático (palavras raras do lançamento presentes no texto da evidência) e precisa de conferência por pessoa.", ""]
    tot = {}
    for r in resultados:
        md += [f"## {r['candidato']}", "",
               f"Lattes nas páginas {r['paginas_lattes']}; {r['lancamentos_no_cv']} lançamentos: " + ", ".join(f"{k} {v}" for k, v in r["por_secao"].items()), "",
               "| Evidência | Item esperado | Lançamento no CV (seção) | Score | Veredito |", "|---|---|---|--:|---|"]
        for e in r["evidencias"]:
            m = e["melhor"] or e["melhor_na_secao_esperada"]
            if m:
                lan = f"{m['lancamento']} ({m['secao']})".replace("|", "/")
                sc = m["score"]
            else:
                lan, sc = "-", ""
            md.append(f"| {e['arquivo']} | {e['item_esperado']} | {lan} | {sc} | {e['veredito']} |")
            chave = e["veredito"].split(":")[0]
            tot[chave] = tot.get(chave, 0) + 1
        if r["lancamentos_sem_evidencia"]:
            md += ["", "Lançamentos do CV sem evidência anexada:", ""]
            md += [f"- {x['secao']}: {x['lancamento']}" for x in r["lancamentos_sem_evidencia"]]
        md.append("")
    md = md[:4] + ["Totais: " + ", ".join(f"{k} {v}" for k, v in sorted(tot.items())), ""] + md[4:]
    (SAIDA / "cruzamento_cv_evidencias.md").write_text("\n".join(md), encoding="utf-8")
    print("Totais:", tot)
    for r in resultados:
        print(r["prefixo"], r["lancamentos_no_cv"], "lançamentos;", len(r["evidencias"]), "evidências;", len(r["lancamentos_sem_evidencia"]), "lançamentos sem evidência")


if __name__ == "__main__":
    main()
