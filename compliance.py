"""Módulo de Conformidade CNPq (Portaria 2.664/2026 e CAPES Sucupira) - Protocolo 3V.

Fornece sanitização ativa de metadados para evitar erros de validação e encoding no Lattes,
e verificação de conformidade em tempo real.
"""

from __future__ import annotations

import re
import unittest
from typing import Any

# Caracteres de aspas que o Lattes rejeita ou corrompe em '?'
ASPAS_RE = re.compile(r'["\'“”‘’`«»]')

# Travessões tipográficos Unicode que viram '?' no encoding ISO-8859-1 do Lattes
TRAVESSOES_RE = re.compile(r"[—–]")

# Prefixos comuns de DOI que devem ser removidos para o padrão do Lattes
DOI_PREFIX_RE = re.compile(r"^(?:https?://)?(?:dx\.)?doi\.org/|^doi:\s*", re.IGNORECASE)
DOI_EXTRACT_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")

# Campos textuais que devem ter aspas e travessões sanitizados
CAMPOS_TEXTO_SANITIZAR = [
    "titulo",
    "titulo_anais",
    "titulo_en",
    "nome_evento",
    "cidade_evento",
    "local_evento",
    "instituicao_promotora",
    "editora",
    "cidade_editora",
    "periodico",
    "nome_orientando",
    "instituicao_orient",
    "curso_orient",
]


def formatar_doi(doi: str | None) -> str:
    """Valida e formata DOI para o formato nativo do Lattes (sem prefixo URL, iniciando em 10.)."""
    if not doi or not isinstance(doi, str):
        return ""
    limpo = doi.strip()
    limpo = DOI_PREFIX_RE.sub("", limpo).strip()
    m = DOI_EXTRACT_RE.search(limpo)
    if m:
        return m.group(1).rstrip(".")
    if limpo.startswith("10."):
        return limpo.rstrip(".")
    return limpo


def sanitizar_texto(texto: str | None) -> str:
    """Remove aspas e substitui travessões tipográficos por hífen ASCII simples."""
    if not texto or not isinstance(texto, str):
        return ""
    # Remove todas as variações de aspas
    sem_aspas = ASPAS_RE.sub("", texto)
    # Substitui travessões (em-dash / en-dash) por hífen padrão aceito pelo Lattes
    sem_traves = TRAVESSOES_RE.sub("-", sem_aspas)
    # Normaliza espaços múltiplos
    return re.sub(r"\s+", " ", sem_traves).strip()


def sanitizar_metadados(payload: dict[str, Any]) -> dict[str, Any]:
    """Sanitiza metadados para garantir conformidade técnica com o formulário do Lattes.

    1. Remove aspas e travessões problemáticos de títulos e nomes de eventos.
    2. Remove caracteres não numéricos de isbn_issn (mantém apenas dígitos para o campo f_isbn).
    3. Valida e formata DOI (garante início em 10. e remoção de URLs/prefixos).
    """
    if not isinstance(payload, dict):
        return {}

    dados = dict(payload)

    # 1. Sanitização de títulos e nomes de eventos
    for campo in CAMPOS_TEXTO_SANITIZAR:
        if campo in dados and isinstance(dados[campo], str):
            dados[campo] = sanitizar_texto(dados[campo])

    # 2. isbn_issn: apenas dígitos (conforme trava f_isbn do Lattes)
    if "isbn_issn" in dados and dados["isbn_issn"]:
        val = str(dados["isbn_issn"])
        dados["isbn_issn"] = re.sub(r"\D", "", val)

    # 3. DOI: formato 10.xxxx
    if "doi" in dados and dados["doi"]:
        dados["doi"] = formatar_doi(str(dados["doi"]))

    return dados


def verificar_conformidade(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Avalia regras da Portaria CNPq 2.664/2026 e CAPES Sucupira (Protocolo 3V).

    Retorna lista de alertas: [{"campo": ..., "nivel": "critico"|"aviso"|"sucesso", "mensagem": ...}].
    """
    if not isinstance(payload, dict):
        return []

    alertas: list[dict[str, str]] = []
    tipo = payload.get("tipo_producao") or payload.get("tipo") or "anais"
    titulo = str(payload.get("titulo") or "").strip()
    doi = str(payload.get("doi") or "").strip()
    pag_ini = str(payload.get("pagina_inicial") or "").strip()
    vol = str(payload.get("volume") or "").strip()
    isbn = str(payload.get("isbn_issn") or "").strip()

    # 1. Regra de Artigo sem DOI (Portaria CNPq 2.664/2026 e CAPES Sucupira)
    if tipo == "artigo":
        if not doi:
            alertas.append({
                "campo": "doi",
                "nivel": "critico",
                "mensagem": "Artigo sem DOI cadastrado. Conforme a Portaria CNPq 2.664/2026 e CAPES Sucupira, artigos sem DOI não são importados automaticamente pelo Sucupira, gerando inconsistência e perda de pontuação na avaliação do PPG.",
            })
        elif not doi.startswith("10.") or "/" not in doi:
            alertas.append({
                "campo": "doi",
                "nivel": "critico",
                "mensagem": f"DOI '{doi}' parece inválido. O DOI do Lattes deve iniciar com '10.' e conter barra '/', sem prefixos como 'https://doi.org/'.",
            })
        else:
            alertas.append({
                "campo": "doi",
                "nivel": "sucesso",
                "mensagem": f"DOI em conformidade com o padrão CNPq: {doi}",
            })
    elif doi:
        if doi.startswith("10.") and "/" in doi:
            alertas.append({
                "campo": "doi",
                "nivel": "sucesso",
                "mensagem": f"DOI em conformidade com o padrão CNPq: {doi}",
            })
        else:
            alertas.append({
                "campo": "doi",
                "nivel": "aviso",
                "mensagem": f"DOI '{doi}' fora do padrão oficial (esperado início com '10.').",
            })

    # 2. Regra de aspas e travessões no título
    if titulo:
        tem_aspas = bool(ASPAS_RE.search(titulo))
        tem_traves = bool(TRAVESSOES_RE.search(titulo))
        if tem_aspas or tem_traves:
            motivos = []
            if tem_aspas:
                motivos.append("aspas")
            if tem_traves:
                motivos.append("travessões tipográficos (—, –)")
            alertas.append({
                "campo": "titulo",
                "nivel": "aviso",
                "mensagem": f"O título contém {' e '.join(motivos)}, que o sistema Lattes frequentemente converte em '?'. Utilize a sanitização automática.",
            })
        else:
            alertas.append({
                "campo": "titulo",
                "nivel": "sucesso",
                "mensagem": "Título em conformidade, sem aspas ou caracteres conflitantes com o Lattes.",
            })
    else:
        alertas.append({
            "campo": "titulo",
            "nivel": "critico",
            "mensagem": "Título não informado. Campo de preenchimento obrigatório no Lattes.",
        })

    # 3. Regra de Página Inicial e Volume (Requisito Sucupira / CAPES)
    if tipo in ("artigo", "anais"):
        if not pag_ini:
            alertas.append({
                "campo": "pagina_inicial",
                "nivel": "aviso",
                "mensagem": "Página inicial não informada. Pode dificultar a localização e conferência nos relatórios CAPES/Sucupira.",
            })
        else:
            alertas.append({
                "campo": "pagina_inicial",
                "nivel": "sucesso",
                "mensagem": f"Página inicial ({pag_ini}) devidamente registrada.",
            })

        if not vol:
            alertas.append({
                "campo": "volume",
                "nivel": "aviso",
                "mensagem": "Volume não informado. Recomendado para citação bibliográfica completa.",
            })
        else:
            alertas.append({
                "campo": "volume",
                "nivel": "sucesso",
                "mensagem": f"Volume ({vol}) registrado.",
            })

    # 4. Regra de ISBN / ISSN (somente dígitos no Lattes)
    if isbn:
        if re.search(r"\D", isbn):
            alertas.append({
                "campo": "isbn_issn",
                "nivel": "aviso",
                "mensagem": f"ISBN/ISSN '{isbn}' contém caracteres não numéricos (ex: hífens). O Lattes aceita apenas dígitos no campo f_isbn.",
            })
        else:
            alertas.append({
                "campo": "isbn_issn",
                "nivel": "sucesso",
                "mensagem": f"ISBN/ISSN formatado apenas com dígitos ({isbn}), em conformidade com o Lattes.",
            })

    # 5. Preenchimento Duplo (Protocolo 3V)
    if payload.get("f_sta_divulgacao_cientifica") == "S":
        alertas.append({
            "campo": "f_sta_divulgacao_cientifica",
            "nivel": "sucesso",
            "mensagem": "Preenchimento Duplo: Configurado para replicação na aba Educação e Popularização de C&T.",
        })
    if payload.get("f_inovacao") == "S":
        alertas.append({
            "campo": "f_inovacao",
            "nivel": "sucesso",
            "mensagem": "Preenchimento Duplo: Configurado para replicação na aba Atividade de Inovação Tecnológica.",
        })

    return alertas


# ==============================================================================
# TESTES UNITÁRIOS
# ==============================================================================

class TestCompliance(unittest.TestCase):
    def test_sanitizar_aspas_e_travoes(self):
        entrada = {
            "titulo": '“Estudo” de Caso: \'COVID-19\' — Uma Análise – Parte "A"',
            "nome_evento": 'Congresso Nacional — Edição "2026"',
        }
        saida = sanitizar_metadados(entrada)
        # Aspas devem sumir completamente
        self.assertNotIn('"', saida["titulo"])
        self.assertNotIn("'", saida["titulo"])
        self.assertNotIn("“", saida["titulo"])
        self.assertNotIn("”", saida["titulo"])
        # Travessões devem ser substituídos por hífen simples ASCII
        self.assertNotIn("—", saida["titulo"])
        self.assertNotIn("–", saida["titulo"])
        self.assertIn("-", saida["titulo"])
        self.assertEqual(saida["titulo"], "Estudo de Caso: COVID-19 - Uma Análise - Parte A")
        self.assertEqual(saida["nome_evento"], "Congresso Nacional - Edição 2026")

    def test_sanitizar_isbn_issn(self):
        entrada = {"isbn_issn": "978-65-5363-471-8"}
        saida = sanitizar_metadados(entrada)
        self.assertEqual(saida["isbn_issn"], "9786553634718")

    def test_formatar_doi(self):
        self.assertEqual(
            formatar_doi("https://doi.org/10.1016/j.cell.2023.01.001"),
            "10.1016/j.cell.2023.01.001",
        )
        self.assertEqual(
            formatar_doi("http://dx.doi.org/10.1109/5.771073"),
            "10.1109/5.771073",
        )
        self.assertEqual(
            formatar_doi("doi: 10.1000/182."),
            "10.1000/182",
        )
        self.assertEqual(
            formatar_doi("10.1000/182"),
            "10.1000/182",
        )

    def test_verificar_artigo_sem_doi_critico(self):
        payload = {
            "tipo_producao": "artigo",
            "titulo": "Artigo sem identificador",
            "doi": "",
        }
        alertas = verificar_conformidade(payload)
        criticos = [a for a in alertas if a["campo"] == "doi" and a["nivel"] == "critico"]
        self.assertTrue(len(criticos) > 0)
        self.assertIn("Portaria CNPq 2.664/2026", criticos[0]["mensagem"])

    def test_verificar_titulo_com_aspas_aviso(self):
        payload = {
            "tipo_producao": "anais",
            "titulo": 'Trabalho com "aspas"',
        }
        alertas = verificar_conformidade(payload)
        avisos = [a for a in alertas if a["campo"] == "titulo" and a["nivel"] == "aviso"]
        self.assertTrue(len(avisos) > 0)
        self.assertIn("aspas", avisos[0]["mensagem"])

    def test_verificar_falta_pagina_e_volume_aviso(self):
        payload = {
            "tipo_producao": "artigo",
            "titulo": "Artigo Válido",
            "doi": "10.1016/j.cell.2023.01.001",
            "pagina_inicial": "",
            "volume": "",
        }
        alertas = verificar_conformidade(payload)
        aviso_pag = [a for a in alertas if a["campo"] == "pagina_inicial" and a["nivel"] == "aviso"]
        aviso_vol = [a for a in alertas if a["campo"] == "volume" and a["nivel"] == "aviso"]
        self.assertTrue(len(aviso_pag) > 0)
        self.assertTrue(len(aviso_vol) > 0)

    def test_verificar_sucesso_completo(self):
        payload = {
            "tipo_producao": "artigo",
            "titulo": "Artigo Completo em Conformidade",
            "doi": "10.1016/j.cell.2023.01.001",
            "pagina_inicial": "123",
            "volume": "45",
            "isbn_issn": "12345678",
            "f_sta_divulgacao_cientifica": "S",
            "f_inovacao": "S",
        }
        alertas = verificar_conformidade(payload)
        criticos = [a for a in alertas if a["nivel"] == "critico"]
        avisos = [a for a in alertas if a["nivel"] == "aviso"]
        sucessos = [a for a in alertas if a["nivel"] == "sucesso"]
        self.assertEqual(len(criticos), 0)
        self.assertEqual(len(avisos), 0)
        self.assertTrue(len(sucessos) >= 5)


if __name__ == "__main__":
    unittest.main()
