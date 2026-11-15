"""LattesFácil - Organizador e Padronizador de Comprovantes (Dossiê Acadêmico).

Módulo responsável por:
1. Padronizar nomes de arquivos de comprovação acadêmica no padrão oficial
   exigido por comissões de avaliação da CAPES (Qualis/Sucupira) e editais do CNPq/FAPEMA:
   {ANO}_{TIPO}_{PRIMEIRO_AUTOR}_{SLUG_TITULO}.pdf
   Exemplos:
     - 2024_ARTIGO_REIS_SINTESE-CRISTAIS-COBRE.pdf
     - 2024_ANAIS_REIS_IMPORTANCIA-FARMACEUTICO.pdf
2. Organizar lotes de comprovantes em estrutura de pastas por ano acadêmico.
3. Gerar pacote ZIP do dossiê acadêmico para prestação de contas.
"""

from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from typing import Any

# Palavras de parada (preposições, artigos, conjunções) desconsideradas no slug
STOP_WORDS = {
    "DE", "DO", "DA", "DOS", "DAS", "E", "EM", "NO", "NA", "NOS", "NAS",
    "PARA", "POR", "COM", "UM", "UMA", "UNS", "UMAS", "O", "A", "OS", "AS",
    "AO", "AOS", "SOBRE", "ENTRE", "SEM", "SOB", "PELO", "PELA", "PELOS", "PELAS",
    "THE", "OF", "AND", "IN", "ON", "AT", "TO", "FOR", "WITH", "BY", "AN"
}

# Sufixos de parentesco que acompanham o sobrenome
PARENTESCO = {"JUNIOR", "FILHO", "NETO", "SOBRINHO", "SEGUNDO", "TERCEIRO"}

# Mapeamento amigável de tipos de produção
MAPA_TIPOS = {
    "artigo": "ARTIGO",
    "artigos": "ARTIGO",
    "periodico": "ARTIGO",
    "journal": "ARTIGO",
    "anais": "ANAIS",
    "evento": "ANAIS",
    "resumo": "ANAIS",
    "resumo_expandido": "ANAIS",
    "trabalho_completo": "ANAIS",
    "apresentacao": "APRESENTACAO",
    "palestra": "APRESENTACAO",
    "conferencia": "APRESENTACAO",
    "certificado": "CERTIFICADO",
    "orientacao": "ORIENTACAO",
    "dissertacao": "ORIENTACAO",
    "tese": "ORIENTACAO",
    "tcc": "ORIENTACAO",
    "ic": "ORIENTACAO",
    "capitulo": "CAPITULO",
    "livro": "LIVRO",
    "patente": "PATENTE",
    "relatorio": "RELATORIO",
    "projeto": "PROJETO",
    "premiacao": "PREMIO",
}


def remover_acentos(texto: str) -> str:
    """Remove acentos e caracteres diacríticos mantendo apenas ASCII básico."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def limpar_string_alfanumerica(texto: str) -> str:
    """Converte para maiúsculas e remove qualquer caractere que não seja A-Z, 0-9 ou espaço/hífen."""
    sem_acento = remover_acentos(texto).upper()
    return re.sub(r"[^A-Z0-9\s\-_]", " ", sem_acento).strip()


def extrair_ano(dados: dict[str, Any]) -> str:
    """Extrai um ano de 4 dígitos válido a partir dos dados do comprovante."""
    candidatos = [
        dados.get("ano"),
        dados.get("ano_evento"),
        dados.get("ano_publicacao"),
        dados.get("created_at"),
        dados.get("data"),
    ]
    for c in candidatos:
        if c:
            m = re.search(r"\b(19\d\d|20\d\d)\b", str(c))
            if m:
                return m.group(1)
    return "SEM-ANO"


def extrair_tipo(dados: dict[str, Any]) -> str:
    """Determina o tipo normalizado da produção acadêmica."""
    tipo_bruto = (
        dados.get("tipo_producao")
        or dados.get("tipo")
        or dados.get("natureza")
        or ""
    ).strip().lower()

    if tipo_bruto in MAPA_TIPOS:
        return MAPA_TIPOS[tipo_bruto]

    # Checa palavras-chave na string do tipo ou natureza
    for chave, val in MAPA_TIPOS.items():
        if chave in tipo_bruto:
            return val

    # Checa presença de DOI ou periódico -> Artigo
    if dados.get("doi") or dados.get("periodico"):
        return "ARTIGO"
    if dados.get("nome_evento") or dados.get("titulo_anais"):
        return "ANAIS"
    if dados.get("nome_orientando") or dados.get("instituicao_orient"):
        return "ORIENTACAO"

    return "PRODUCAO"


def extrair_primeiro_autor(dados: dict[str, Any]) -> str:
    """Extrai o sobrenome oficial do primeiro autor para o padrão CAPES/CNPq."""
    candidato: str = ""

    # 1. Se vier em lista de autores
    autores = dados.get("autores")
    if isinstance(autores, list) and len(autores) > 0:
        primeiro = autores[0]
        if isinstance(primeiro, dict):
            # Tenta pegar da citação (ex.: "REIS, A. S." -> "REIS")
            cit = primeiro.get("citacao") or ""
            if "," in cit:
                candidato = cit.split(",")[0].strip()
            else:
                candidato = primeiro.get("nome") or ""
        elif isinstance(primeiro, str):
            candidato = primeiro

    # 2. Outras chaves de autor
    if not candidato:
        candidato = (
            dados.get("primeiro_autor")
            or dados.get("autor")
            or dados.get("usuario")
            or dados.get("owner")
            or dados.get("nome_orientando")
            or ""
        )

    if not candidato:
        return "AUTOR"

    # Se estiver no formato "SOBRENOME, Nomes"
    if "," in candidato:
        sobrenome = candidato.split(",")[0].strip()
        sobrenome_limpo = limpar_string_alfanumerica(sobrenome)
        if sobrenome_limpo:
            return re.sub(r"\s+", "-", sobrenome_limpo)

    # Caso nome direto "Aramys Silva dos Reis"
    limpo = limpar_string_alfanumerica(candidato)
    tokens = [t for t in limpo.split() if t]
    if not tokens:
        return "AUTOR"

    if len(tokens) == 1:
        return tokens[0]

    # Checar se último token é sufixo de parentesco (Junior, Filho, etc.)
    ultimo = tokens[-1]
    penultimo = tokens[-2] if len(tokens) >= 2 else ""

    if ultimo in PARENTESCO and penultimo:
        return f"{penultimo}-{ultimo}"

    # Retorna o último sobrenome
    return ultimo


def gerar_slug_titulo(dados: dict[str, Any], max_palavras: int = 5, max_chars: int = 40) -> str:
    """Gera um slug limpo e informativo a partir do título do trabalho.
    
    Remove acentos, caracteres especiais e stop words comuns, mantendo
    as palavras-chave principais legíveis e compactas.
    """
    titulo = str(
        dados.get("titulo")
        or dados.get("title")
        or dados.get("nome_evento")
        or "DOCUMENTO"
    )

    limpo = limpar_string_alfanumerica(titulo)
    tokens = [t for t in limpo.split() if t]

    # Filtra stop words se houver palavras suficientes
    relevantes = [t for t in tokens if t not in STOP_WORDS]
    if not relevantes:
        relevantes = tokens

    # Limita quantidade de palavras
    selecionadas: list[str] = []
    tamanho_atual = 0

    for p in relevantes[:max_palavras]:
        adicional = len(p) + (1 if selecionadas else 0)
        if tamanho_atual + adicional > max_chars and selecionadas:
            break
        selecionadas.append(p)
        tamanho_atual += adicional

    if not selecionadas:
        slug = "DOCUMENTO"
    else:
        slug = "-".join(selecionadas)

    # Limpeza final
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "DOCUMENTO"


def gerar_nome_padronizado(dados: dict[str, Any]) -> str:
    """Gera o nome de arquivo no padrão acadêmico oficial exigido pela CAPES/CNPq:
    
    Formato: {ANO}_{TIPO}_{PRIMEIRO_AUTOR}_{SLUG_TITULO}.pdf
    Exemplo: 2024_ARTIGO_REIS_SINTESE-CRISTAIS-COBRE.pdf
             2024_ANAIS_REIS_IMPORTANCIA-FARMACEUTICO.pdf
    
    Garante limpeza total de acentos, caracteres especiais e espaços.
    """
    if not isinstance(dados, dict):
        dados = {}

    ano = extrair_ano(dados)
    tipo = extrair_tipo(dados)
    autor = extrair_primeiro_autor(dados)
    slug = gerar_slug_titulo(dados)

    nome_base = f"{ano}_{tipo}_{autor}_{slug}"

    # Sanitização rigorosa: apenas A-Z, 0-9, hífen e underscore
    nome_sanitizado = re.sub(r"[^A-Z0-9_\-]", "", nome_base)
    # Evita repetição excessiva de separadores
    nome_sanitizado = re.sub(r"_{2,}", "_", nome_sanitizado)
    nome_sanitizado = re.sub(r"-{2,}", "-", nome_sanitizado)

    return f"{nome_sanitizado}.pdf"


def organizar_lote_comprovantes(arquivos_info: list[dict[str, Any]]) -> dict[str, Any]:
    """Mapeia e organiza uma lista de comprovantes em estrutura de pastas por ano acadêmico.
    
    Retorna:
        dict contendo:
          - total: número de arquivos processados
          - anos: dicionário agrupando itens por ano ('2024/', '2025/', etc.)
          - estrutura_pastas: lista de caminhos relativos sugeridos
          - relatorio_markdown: visão tabular do dossiê acadêmico
    """
    anos_map: dict[str, list[dict[str, Any]]] = {}
    estrutura_pastas: list[str] = []
    itens_processados: list[dict[str, Any]] = []

    for idx, item in enumerate(arquivos_info, start=1):
        if not isinstance(item, dict):
            continue

        dados = item.get("dados") if isinstance(item.get("dados"), dict) else item
        nome_orig = str(item.get("nome_original") or item.get("filename") or f"documento_{idx}.pdf")

        nome_padrao = gerar_nome_padronizado(dados)
        ano = extrair_ano(dados)
        pasta_ano = f"{ano}"
        caminho_sugerido = f"{pasta_ano}/{nome_padrao}"

        registro = {
            "indice": idx,
            "nome_original": nome_orig,
            "nome_padronizado": nome_padrao,
            "ano": ano,
            "pasta": pasta_ano,
            "caminho_sugerido": caminho_sugerido,
            "tipo": extrair_tipo(dados),
            "autor": extrair_primeiro_autor(dados),
            "titulo": dados.get("titulo") or "Sem título",
        }

        anos_map.setdefault(pasta_ano, []).append(registro)
        estrutura_pastas.append(caminho_sugerido)
        itens_processados.append(registro)

    # Ordenação por ano decrescente
    anos_ordenados = dict(sorted(anos_map.items(), key=lambda kv: kv[0], reverse=True))

    # Geração do relatório descritivo para prestação de contas
    linhas_md = [
        "# Dossiê Acadêmico de Comprovações (Padrão CAPES / CNPq)",
        f"**Total de Documentos:** {len(itens_processados)}",
        "",
        "| Ano | Tipo | Primeiro Autor | Nome Padronizado Oficial | Caminho Sugerido |",
        "|:---:|:---:|:---|:---|:---|",
    ]
    for r in itens_processados:
        linhas_md.append(
            f"| {r['ano']} | `{r['tipo']}` | {r['autor']} | **`{r['nome_padronizado']}`** | `{r['caminho_sugerido']}` |"
        )

    return {
        "ok": True,
        "total": len(itens_processados),
        "anos": anos_ordenados,
        "estrutura_pastas": estrutura_pastas,
        "itens": itens_processados,
        "relatorio_markdown": "\n".join(linhas_md),
    }


def gerar_zip_dossie(lote_comprovantes: list[dict[str, Any]]) -> bytes:
    """Gera um arquivo ZIP em memória com os comprovantes organizados nas pastas por ano.
    
    Cada item pode conter:
      - 'conteudo': bytes do arquivo PDF
      - 'dados': dict com metadados para nome padronizado
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        org = organizar_lote_comprovantes(lote_comprovantes)
        for idx, item in enumerate(lote_comprovantes):
            reg = org["itens"][idx]
            conteudo = item.get("conteudo") or item.get("bytes") or b""
            if not conteudo and item.get("texto"):
                conteudo = str(item.get("texto")).encode("utf-8")
            if not conteudo:
                # Cria documento informativo stub se não houver binário
                conteudo = (
                    f"Comprovante Acadêmico: {reg['nome_padronizado']}\n"
                    f"Título: {reg['titulo']}\n"
                    f"Autor: {reg['autor']}\n"
                    f"Ano: {reg['ano']}\n"
                ).encode("utf-8")

            caminho_zip = reg["caminho_sugerido"]
            zf.writestr(caminho_zip, conteudo)

        # Inclui o relatório do dossiê na raiz do ZIP
        zf.writestr("DOSSIE_INDICE_CAPES.md", org["relatorio_markdown"].encode("utf-8"))

    buffer.seek(0)
    return buffer.getvalue()


# ----------------------------------------------------------------------
# Testes Unitários
# ----------------------------------------------------------------------
def test_gerar_nome_padronizado() -> None:
    """Executa bateria de testes unitários para o padronizador de comprovantes."""
    # Teste 1: Artigo com autor em lista e acentos no título
    d1 = {
        "tipo_producao": "artigo",
        "ano": "2024",
        "autores": [{"nome": "Aramys Silva dos Reis", "citacao": "REIS, A. S."}],
        "titulo": "Síntese de Cristais de Cobre e Caracterização Espectroscópica",
    }
    n1 = gerar_nome_padronizado(d1)
    assert n1.startswith("2024_ARTIGO_REIS_"), f"Falha no teste 1: {n1}"
    assert "SINTESE-CRISTAIS-COBRE" in n1, f"Falha slug teste 1: {n1}"
    assert n1.endswith(".pdf"), f"Falha extensão teste 1: {n1}"
    assert "Í" not in n1 and "í" not in n1, f"Acentos não removidos: {n1}"

    # Teste 2: Anais com autor string e título com stop words
    d2 = {
        "tipo_producao": "anais",
        "ano": 2024,
        "autor": "Aramys Silva dos Reis",
        "titulo": "Importância do Farmacêutico no Cuidado ao Paciente Hipertenso",
    }
    n2 = gerar_nome_padronizado(d2)
    assert n2.startswith("2024_ANAIS_REIS_"), f"Falha no teste 2: {n2}"
    assert "IMPORTANCIA-FARMACEUTICO" in n2, f"Falha slug teste 2: {n2}"

    # Teste 3: Orientação e sufixo de parentesco
    d3 = {
        "tipo_producao": "orientacao",
        "ano": "2023",
        "autores": ["José da Silva Filho"],
        "titulo": "Estudo de Caso sobre Biodiversidade na Amazônia",
    }
    n3 = gerar_nome_padronizado(d3)
    assert "SILVA-FILHO" in n3, f"Falha sufixo parentesco teste 3: {n3}"
    assert n3.startswith("2023_ORIENTACAO_"), f"Falha tipo orientacao teste 3: {n3}"

    # Teste 4: Dados faltantes ou vazios (resiliência)
    d4: dict[str, Any] = {}
    n4 = gerar_nome_padronizado(d4)
    assert n4 == "SEM-ANO_PRODUCAO_AUTOR_DOCUMENTO.pdf", f"Falha defaults teste 4: {n4}"

    # Teste 5: Certificado
    d5 = {
        "tipo_producao": "apresentacao",
        "natureza": "Comunicação",
        "ano_evento": "2025",
        "autores": [{"nome": "Álvaro Antônio Bezerra dos Santos", "citacao": "SANTOS, A. A. B."}],
        "titulo": "Nanotecnologia Aplicada à Medicina Diagnóstica",
    }
    n5 = gerar_nome_padronizado(d5)
    assert n5.startswith("2025_APRESENTACAO_SANTOS_"), f"Falha teste 5: {n5}"
    assert "NANOTECNOLOGIA-APLICADA-MEDICINA" in n5, f"Falha slug teste 5: {n5}"


def test_organizar_lote() -> None:
    """Testa organização em lote e estrutura por ano."""
    lote = [
        {
            "filename": "comprovante_antigo_1.pdf",
            "dados": {
                "tipo_producao": "artigo",
                "ano": "2024",
                "autor": "Aramys Silva dos Reis",
                "titulo": "Síntese de Cristais de Cobre",
            },
        },
        {
            "filename": "meu_certificado.pdf",
            "dados": {
                "tipo_producao": "apresentacao",
                "ano": "2025",
                "autor": "Álvaro Antônio Bezerra dos Santos",
                "titulo": "Palestra de Abertura",
            },
        },
        {
            "filename": "outro_doc.pdf",
            "dados": {
                "tipo_producao": "anais",
                "ano": "2024",
                "autor": "Aramys Silva dos Reis",
                "titulo": "Importância do Farmacêutico",
            },
        },
    ]

    res = organizar_lote_comprovantes(lote)
    assert res["total"] == 3
    assert "2024" in res["anos"] and len(res["anos"]["2024"]) == 2
    assert "2025" in res["anos"] and len(res["anos"]["2025"]) == 1
    assert len(res["estrutura_pastas"]) == 3
    assert any("2024/2024_ARTIGO_REIS_" in p for p in res["estrutura_pastas"])

    # Teste de geração de ZIP
    zip_bytes = gerar_zip_dossie(lote)
    assert len(zip_bytes) > 100
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        namelist = zf.namelist()
        assert "DOSSIE_INDICE_CAPES.md" in namelist
        assert any(n.startswith("2024/2024_ARTIGO_REIS_") for n in namelist)


if __name__ == "__main__":
    test_gerar_nome_padronizado()
    test_organizar_lote()
    print("✅ Todos os testes unitários do organizer.py passaram com 100% de sucesso!")
