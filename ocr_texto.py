"""Pós-processamento do texto de OCR: espaços perdidos e grafia do nome do pesquisador.

Nasceu do controle positivo (leitura visual × sistema, 25/11/2026): o RapidOCR às vezes cola palavras ("AlunaLuisaMarillakQueirozdeSousa",
"SantosMatricula", "21271176Monitora") e erra letras de nomes ("MOVRAO" por "MOURÃO"). As correções abaixo são gerais: não conhecem o documento.
"""
from __future__ import annotations

import difflib
import math
import re
import unicodedata
from functools import lru_cache

# "a" e "o" ficam de fora: terminações femininas/masculinas ("Monitora") viram falso "Monitor a"; "e" e as preposições servem de conector
_CONECTORES = {"de", "da", "do", "dos", "das", "e", "em", "no", "na", "nos", "nas", "com", "para", "por"}
# em palavra isolada curta só o "e" vale: preposições finais terminam muitos nomes ("Santana", "Luciana", "Aparecida")
_CONECTORES_CURTOS = {"e"}  # "Aparecida" não pode virar "Apareci da"; só "Dentale" -> "Dental e"
_FREQ_MIN = 100  # só palavras comuns entram no vocabulário (nomes próprios raros ficam de fora, de propósito)


def _sem_acento(t: str) -> str:
    return "".join(c for ch in t for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c)).lower()


@lru_cache(maxsize=1)
def _vocabulario() -> tuple[dict[str, int], float] | None:
    """Palavras comuns do português (sem acento -> frequência) e o total; None se o dicionário não estiver instalado."""
    try:
        from spellchecker import SpellChecker
        dic = SpellChecker(language="pt").word_frequency.dictionary
    except Exception:
        return None
    voc: dict[str, int] = {}
    for w, f in dic.items():
        if f >= _FREQ_MIN:
            k = _sem_acento(w)
            if k.isalpha():
                voc[k] = voc.get(k, 0) + f
    return voc, float(sum(voc.values()) or 1)


def _segmentar(tok: str) -> list[int] | None:
    """Tamanhos das partes se `tok` (minúsculo, sem acento) for a junção de palavras comuns; senão None.

    Em tokens muito longos (>= 14 letras) admite UMA parte desconhecida (nome próprio no meio: "CIENCIASETECNOLOGIADOMARANHAO"),
    desde que as partes conhecidas cubram a maior parte das letras.
    """
    v = _vocabulario()
    if not v:
        return None
    voc, total = v
    n = len(tok)
    livre = n >= 14  # token longo: sequência colada de palavras; curto: só "palavra + conector"
    conectores = (_CONECTORES | {"a", "o"}) if livre else _CONECTORES if n >= 9 else _CONECTORES_CURTOS  # "a/o" só em sequência longa ("apresentouo")  # 9+ letras: "denovembrode" (de+novembro+de) exige 3 partes, ver abaixo
    custo = [math.inf] * (n + 1)
    volta = [0] * (n + 1)
    desconhecida = [False] * (n + 1)
    custo[0] = 0.0
    for i in range(1, n + 1):
        for j in range(max(0, i - 24), i):
            if custo[j] == math.inf:
                continue
            p = tok[j:i]
            desc = False
            if p in conectores:
                c = 4.0
            elif len(p) >= 3 and p in voc:
                c = -math.log(voc[p] / total) + 6.0
            elif n >= 14 and len(p) >= 5:
                c, desc = 10.0 + 3.0 * len(p), True
            else:
                continue
            if custo[j] + c < custo[i]:
                custo[i], volta[i], desconhecida[i] = custo[j] + c, j, desc
    if custo[n] == math.inf:
        return None
    partes, i, n_desc, letras_desc = [], n, 0, 0
    while i > 0:
        partes.append(i - volta[i])
        if desconhecida[i]:
            n_desc += 1
            letras_desc += i - volta[i]
        i = volta[i]
    partes.reverse()
    if len(partes) < 2 or n_desc > 1 or letras_desc > 0.5 * n:
        return None
    if not livre:
        # palavra curta: "palavra comum + e" (Dentale -> Dental e) ou, com preposição, só se for uma sequência inteira de palavras comuns
        # com 3+ partes ("denovembrode" -> de novembro de); "Aparecida" -> "Apareci da" fica de fora
        pedacos, i = [], 0
        for t in partes:
            pedacos.append(tok[i:i + t])
            i += t
        so_e = all(p not in _CONECTORES or p == "e" for p in pedacos)
        if so_e and (len(partes) != 2 or partes[0] < 5):
            return None
        if not so_e and (len(partes) < 3 or n < 9):
            return None
    return partes


def _palavra_conhecida(tok: str) -> bool:
    v = _vocabulario()
    return bool(v) and tok in v[0]


def qualidade_texto(texto: str) -> float:
    """Fração das palavras (3+ letras) que existem no vocabulário português; 1.0 se não houver palavras ou dicionário.
    Camada de texto de escaneado mal reconhecido ("Curse:", "Pslco'Ogla") fica bem abaixo de texto limpo."""
    if not _vocabulario():
        return 1.0
    palavras = [_sem_acento(w) for w in re.findall(r"[^\W\d_]{3,}", texto)]
    if len(palavras) < 20:
        return 1.0
    return sum(1 for w in palavras if _palavra_conhecida(w)) / len(palavras)


def _separar_token(tok: str) -> str:
    """Corrige um token longo: fronteira minúscula→Maiúscula, depois separação por vocabulário das partes desconhecidas."""
    if len(tok) >= 10:
        # conector colado entre um nome e a palavra seguinte ("QueirozdeSousa"): só separa se a palavra com o conector não existir
        # ("SaudeColetiva": "saude" existe, então fica)
        def _conector(m: re.Match) -> str:
            return m.group(0) if _palavra_conhecida(_sem_acento(m.group(1) + m.group(2))) else f"{m.group(1)} {m.group(2)}"
        tok = re.sub(r"([A-ZÀ-Ý]?[a-zà-ÿ]{2,})(de|da|do|dos|das)(?=[A-ZÀ-Ý][a-zà-ÿ])", _conector, tok)
    if len(tok) >= 12:
        tok = re.sub(r"(?<=[a-zà-ÿ]{2})(?=[A-ZÀ-Ý][a-zà-ÿ])", " ", tok)  # "SantosMatricula" -> "Santos Matricula"
    if len(tok) >= 10:
        tok = re.sub(r"^(e|de|da|do)(?=[A-ZÀ-Ý])", r"\1 ", tok)  # "eMetodos" -> "e Metodos"
    saida = []
    for parte in tok.split(" "):
        # caixa alta só entra se for longa (siglas e nomes curtos em maiúsculas não são palavras coladas)
        if len(parte) >= (12 if parte.isupper() else 7) and parte.isalpha() and not _palavra_conhecida(_sem_acento(parte)):
            tam = _segmentar(_sem_acento(parte))  # "Dentale" -> "Dental e"; "Queirozde" -> "Queiroz de" só se "queiroz" for comum: senão fica
            if tam:
                pedacos, i = [], 0
                for t in tam:
                    pedacos.append(parte[i:i + t])
                    i += t
                parte = " ".join(pedacos)
        saida.append(parte)
    return " ".join(saida)


def corrigir_espacos(texto: str) -> str:
    """Recoloca espaços perdidos pelo OCR. Conservador: só mexe em palavras longas ou em fronteiras inequívocas."""
    if not texto:
        return texto
    texto = re.sub(r"(?<=[A-Za-zÀ-ÿ]):(?=[A-Za-zÀ-ÿ])", ": ", texto)  # "Aluna:Luisa"
    texto = re.sub(r"(?<![A-Za-z0-9])(\d{4,})(?=[A-Za-zÀ-ÿ]{3,}\b)", r"\1 ", texto)  # "21271176Monitora"
    texto = re.sub(r"(?<=[a-zà-ÿ])(?=(?:19|20)\d{2}\b)", " ", texto)  # "de2022" -> "de 2022"
    return re.sub(r"[A-Za-zÀ-ÿ]{7,}", lambda m: _separar_token(m.group(0)), texto)


def _estilo(original: str, canonico: str) -> str:
    if original.isupper():
        return canonico.upper()
    if original.islower():
        return canonico.lower()
    return canonico[:1].upper() + canonico[1:]


def reconciliar_nome(texto: str, usuario: str) -> str:
    """Troca por a grafia do pesquisador as variações do nome dele criadas por erro de OCR ("MARIA SOUZ4 LIMA" -> "MARIA SOUZA LIMA").

    Só corrige quando pelo menos duas palavras consecutivas do texto acompanham, na ordem, palavras do nome informado: uma palavra isolada
    parecida ("Moura" perto de "Mourão") nunca é trocada, porque pode ser outra pessoa.
    """
    nome = [p for p in re.findall(r"[A-Za-zÀ-ÿ]+", usuario or "")]
    if len(nome) < 2 or not texto:
        return texto
    chave = [_sem_acento(p) for p in nome]
    palavras = [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"[A-Za-zÀ-ÿ]+", texto)]
    chaves_doc = [_sem_acento(w) for _, _, w in palavras]
    trocas: list[tuple[int, int, str]] = []
    i = 0
    while i < len(palavras):
        melhor: list[tuple[int, float]] = []
        for u0 in range(len(chave)):
            casos: list[tuple[int, float]] = []
            j = 0
            while i + j < len(palavras) and u0 + j < len(chave):
                a, b = chaves_doc[i + j], chave[u0 + j]
                r = 1.0 if a == b else difflib.SequenceMatcher(None, a, b).ratio() if min(len(a), len(b)) >= 4 else 0.0
                if r < 0.8:
                    break
                casos.append((u0 + j, r))
                j += 1
            if len(casos) > len(melhor):
                melhor = casos
        if len(melhor) >= 2 and any(r == 1.0 for _, r in melhor):
            for k, (uj, r) in enumerate(melhor):
                s, e, w = palavras[i + k]
                canonico = _estilo(w, nome[uj])
                if canonico != w:  # inclui só a acentuação: "VITORIA" -> "VITÓRIA"
                    trocas.append((s, e, canonico))
            i += len(melhor)
        else:
            i += 1
    for s, e, novo in reversed(trocas):
        texto = texto[:s] + novo + texto[e:]
    return texto
