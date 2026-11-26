"""Upload em lote: ZIP (ou vários arquivos) -> cada documento classificado, lido e com nome/pasta padronizados.

Não conhece o servidor: recebe a função `processar(nome, bytes, usuario)` (a mesma de /api/extract). Defesas contra ZIP
malicioso: limite de arquivos, de tamanho descompactado, de taxa de compressão; nomes com caminho são reduzidos ao
nome do arquivo (sem sair da pasta) e entradas escondidas ou de sistema são ignoradas.
"""
from __future__ import annotations

import io
import posixpath
import re
import zipfile
from typing import Any, Callable

EXTENSOES = (".pdf", ".txt", ".eml", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")
MAX_ARQUIVOS = 150
MAX_TOTAL = 400 * 1024 * 1024
MAX_ARQUIVO = 60 * 1024 * 1024
MAX_TAXA = 120  # descompactado/compactado acima disso é suspeito (zip bomb)


def _nome_seguro(nome: str) -> str:
    base = posixpath.basename(nome.replace("\\", "/"))
    base = re.sub(r"[^\w .()\-áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]", "_", base).strip(" .")
    return base[:150] or "arquivo"


def expandir(arquivos: list[tuple[str, bytes]]) -> tuple[list[tuple[str, bytes]], list[dict[str, str]]]:
    """Lista (nome, bytes) com ZIPs abertos. Devolve (arquivos aceitos, ignorados com motivo)."""
    aceitos: list[tuple[str, bytes]] = []
    ignorados: list[dict[str, str]] = []
    total = 0

    def adicionar(nome: str, dados: bytes) -> None:
        nonlocal total
        seguro = _nome_seguro(nome)
        if seguro.startswith(".") or seguro.lower() in ("thumbs.db", "desktop.ini"):
            return
        if not seguro.lower().endswith(EXTENSOES):
            ignorados.append({"arquivo": seguro, "motivo": "tipo não suportado (use PDF, TXT ou EML)"})
            return
        if len(aceitos) >= MAX_ARQUIVOS:
            ignorados.append({"arquivo": seguro, "motivo": f"limite de {MAX_ARQUIVOS} arquivos por lote"})
            return
        if len(dados) > MAX_ARQUIVO or total + len(dados) > MAX_TOTAL:
            ignorados.append({"arquivo": seguro, "motivo": "arquivo ou lote grande demais"})
            return
        total += len(dados)
        aceitos.append((seguro, dados))

    for nome, dados in arquivos:
        if nome.lower().endswith(".zip") or dados[:2] == b"PK":
            try:
                with zipfile.ZipFile(io.BytesIO(dados)) as z:
                    infos = [i for i in z.infolist() if not i.is_dir()]
                    if sum(i.file_size for i in infos) > MAX_TOTAL:
                        ignorados.append({"arquivo": nome, "motivo": "ZIP descompactado passa do limite"})
                        continue
                    if len(dados) and sum(i.file_size for i in infos) / max(len(dados), 1) > MAX_TAXA:
                        ignorados.append({"arquivo": nome, "motivo": "taxa de compressão suspeita"})
                        continue
                    for i in infos:
                        if i.filename.startswith("__MACOSX/"):
                            continue
                        if i.file_size > MAX_ARQUIVO:
                            ignorados.append({"arquivo": _nome_seguro(i.filename), "motivo": "arquivo grande demais"})
                            continue
                        adicionar(i.filename, z.read(i))
            except zipfile.BadZipFile:
                ignorados.append({"arquivo": nome, "motivo": "ZIP inválido ou corrompido"})
        else:
            adicionar(nome, dados)
    return aceitos, ignorados


def processar_lote(arquivos: list[tuple[str, bytes]], usuario: str, processar: Callable[[str, bytes, str], dict[str, Any]],
                   duplicata: Callable[[dict[str, Any]], list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    """Classifica cada documento. `duplicata(resposta)` (opcional) devolve itens do currículo já cadastrados parecidos."""
    aceitos, ignorados = expandir(arquivos)
    linhas: list[dict[str, Any]] = []
    for nome, dados in aceitos:
        try:
            r = processar(nome, dados, usuario)
            r.pop("_leitura", None)
        except Exception:
            linhas.append({"arquivo": nome, "status": "erro", "mensagem": "Não consegui ler este arquivo."})
            continue
        cls = r.get("classificacao") or {}
        top = (cls.get("candidatos") or [None])[0]
        if r.get("caderno"):
            linhas.append({"arquivo": nome, "status": "caderno", "mensagem": "Caderno de resumos: use a busca por autor.", "paginas": r.get("page_count")})
            continue
        if not top:
            linhas.append({"arquivo": nome, "status": "sem_classificacao",
                           "mensagem": cls.get("motivo_decisao") or "Não identifiquei o tipo; classifique manualmente."})
            continue
        status = {"avancar": "reconhecido", "confirmar": "confirmar"}.get(cls.get("decisao", ""), "sem_classificacao")
        linha = {"arquivo": nome, "status": status, "item": top["id"], "item_nome": top["item"], "confianca": top["confianca"],
                 "motivos": top.get("motivos", []), "outras_opcoes": [{"id": c["id"], "item": c["item"], "confianca": c["confianca"]}
                                                                     for c in (cls.get("candidatos") or [])[1:3]],
                 "implementado": top.get("implementado", False), "nome_padronizado": r.get("nome_padronizado", ""),
                 "caminho_sugerido": r.get("caminho_sugerido", ""), "extraido": (r.get("generico") or {}).get("valores") or r.get("extracted"),
                 "faltam_obrigatorios": (r.get("generico") or {}).get("faltam_obrigatorios", [])}
        if duplicata:
            achados = duplicata(r)
            if achados:
                linha["possivel_duplicata"] = [{"titulo": a.get("titulo", ""), "ano": a.get("ano", ""), "motivo": a["motivo"]} for a in achados[:3]]
        linhas.append(linha)
    cont: dict[str, int] = {}
    for l in linhas:
        cont[l["status"]] = cont.get(l["status"], 0) + 1
    return {"total": len(linhas), "por_status": cont, "arquivos": linhas, "ignorados": ignorados}


def gerar_zip_organizado(arquivos: list[tuple[str, bytes]], resultado: dict[str, Any]) -> bytes:
    """ZIP com os comprovantes renomeados e separados por ano (`ano/NOME_PADRONIZADO.pdf`); o que não foi reconhecido vai para `revisar/`."""
    dados = {n: d for n, d in expandir(arquivos)[0]}
    buf = io.BytesIO()
    usados: set[str] = set()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for linha in resultado["arquivos"]:
            raw = dados.get(linha["arquivo"])
            if raw is None:
                continue
            ext = posixpath.splitext(linha["arquivo"])[1].lower()
            destino = linha.get("caminho_sugerido") if linha.get("status") == "reconhecido" and linha.get("caminho_sugerido") else \
                f"revisar/{linha['arquivo']}"
            if destino and not destino.lower().endswith(ext):
                destino += ext
            destino = "/".join(_nome_seguro(p) for p in destino.split("/"))
            base, n = destino, 2
            while destino in usados:
                destino = re.sub(r"(\.\w+)$", rf"_{n}\1", base)
                n += 1
            usados.add(destino)
            z.writestr(destino, raw)
        z.writestr("LEIAME.txt", "Comprovantes organizados pelo LattesFácil.\n"
                   "Pastas por ano = reconhecidos com nome padronizado. 'revisar' = precisam de conferência manual.\n")
    return buf.getvalue()
