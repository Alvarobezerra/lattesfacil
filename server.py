"""LattesFácil - Web server for evidence extraction, enrichment, and Lattes form assistance."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import threading
import time
from urllib.parse import parse_qs, urlparse

from caderno import abstract_to_record, name_tokens, scan_caderno
from artigo import doi_only, is_article, parse_artigo
from orientacao import is_orientacao, parse_orientacao
from certificado import is_certificate, parse_certificado
from extractor import enrich_missing_fields, extract_text_from_pdf_bytes, parse_evidence_text
from radar import buscar_obras_radar
from compliance import sanitizar_metadados, verificar_conformidade
from organizer import extrair_ano, gerar_nome_padronizado, gerar_zip_dossie, organizar_lote_comprovantes

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "lattes_records.db"
MAX_UPLOAD_BYTES = 60 * 1024 * 1024  # cadernos de anais podem ter centenas de páginas
MAX_SINGLE_ABSTRACT_PAGES = 12  # acima disso (e com vários resumos), o PDF é tratado como caderno
MIN_ABSTRACTS_FOR_CADERNO = 10
SID_RE = re.compile(r"^[a-z0-9]{8,40}$")
LATTES_STATUS: dict[str, dict[str, Any]] = {}  # sid do navegador -> último sinal do conector (só em memória)


@contextmanager
def db():
    """Conexão SQLite que realmente fecha ao sair (sqlite3 'with' só faz commit)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize SQLite storage for shared test records."""
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                titulo TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], tuple[str, bytes] | None]:
    """Lê multipart/form-data sem o módulo cgi: devolve (campos de texto, primeiro arquivo)."""
    m = re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))', content_type)
    if not m:
        return {}, None
    boundary = (m.group(1) or m.group(2)).encode("latin-1")
    fields: dict[str, str] = {}
    file_part: tuple[str, bytes] | None = None
    for part in body.split(b"--" + boundary)[1:]:
        if part.startswith(b"--"):
            break
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            continue
        raw_headers = part[:header_end].decode("utf-8", errors="replace")
        content = part[header_end + 4 :]
        if content.endswith(b"\r\n"):
            content = content[:-2]
        name = re.search(r'\bname="([^"]*)"', raw_headers)
        fn = re.search(r'filename="([^"]*)"', raw_headers)
        if fn:
            if file_part is None:
                file_part = (fn.group(1), content)
        elif name:
            fields[name.group(1)] = content.decode("utf-8", errors="replace")
    return fields, file_part


def parse_multipart_file(content_type: str, body: bytes) -> tuple[str, bytes] | None:
    return parse_multipart(content_type, body)[1]


UPLOAD_TTL = 30 * 60  # segundos que um PDF enviado fica na memória do servidor (busca repetida sem reenviar)
MAX_CHUNK = 3 * 1024 * 1024
MAX_UPLOADS_BYTES = 300 * 1024 * 1024
UPLOADS: dict[str, dict[str, Any]] = {}
UPLOADS_LOCK = threading.Lock()


def _purge_uploads() -> None:
    """Remove envios vencidos e, se a memória passar do teto, os mais antigos (chamar com o lock)."""
    now = time.time()
    for k in [k for k, v in UPLOADS.items() if now - v["ts"] > UPLOAD_TTL]:
        UPLOADS.pop(k, None)

    def size(v: dict[str, Any]) -> int:
        return len(v["data"] or b"") + sum(len(c) for c in v["chunks"].values())

    while UPLOADS and sum(size(v) for v in UPLOADS.values()) > MAX_UPLOADS_BYTES:
        UPLOADS.pop(min(UPLOADS, key=lambda k: UPLOADS[k]["ts"]), None)


def process_extract(filename: str, file_bytes: bytes, usuario: str) -> dict[str, Any]:
    """Lê um arquivo de evidência e devolve o JSON de resposta de /api/extract."""
    if filename.lower().endswith(".pdf"):
        pdf_info = extract_text_from_pdf_bytes(file_bytes)
        if pdf_info["page_count"] > MAX_SINGLE_ABSTRACT_PAGES and len(
            re.findall(r"keywords?\s*:|palavras[- ]chave\s*:", pdf_info["text"], re.I)
        ) >= MIN_ABSTRACTS_FOR_CADERNO:
            # PDF longo = caderno de anais com vários trabalhos; o cliente segue para a busca por autor
            return {"caderno": True, "page_count": pdf_info["page_count"], "filename": filename}
        raw_text = pdf_info["text"]
    else:
        raw_text = file_bytes.decode("utf-8", errors="replace")
    if is_certificate(raw_text):
        extracted = parse_certificado(raw_text, usuario)
    elif is_article(raw_text):
        extracted = parse_artigo(raw_text, usuario)
    elif is_orientacao(raw_text):
        extracted = parse_orientacao(raw_text, usuario)
    else:
        extracted = parse_evidence_text(raw_text, filename=filename)
    extracted = sanitizar_metadados(extracted)
    nome_padrao = gerar_nome_padronizado(extracted)
    ano = extrair_ano(extracted)
    return {
        "extracted": extracted,
        "raw_text": raw_text[:4000],
        "filename": filename,
        "nome_padronizado": nome_padrao,
        "caminho_sugerido": f"{ano}/{nome_padrao}",
    }


def run_caderno(file_bytes: bytes, filename: str, pesquisador: str) -> tuple[dict[str, Any], int]:
    pesquisador = pesquisador.strip()
    if not pesquisador:
        return {"error": "Informe o nome do pesquisador para localizar os resumos."}, HTTPStatus.BAD_REQUEST
    if len(name_tokens(pesquisador)) < 2:
        return {"error": "Informe nome e sobrenome do pesquisador (um nome só traz autores demais)."}, HTTPStatus.BAD_REQUEST
    scan = scan_caderno(file_bytes, pesquisador)
    results = [
        {"pdf_page": a["pdf_page"], "page_label": a["page_label"], "titulo": a["titulo"],
         "autores": [x["nome"] for x in a["autores"]], "record": abstract_to_record(a, scan["meta"])}
        for a in scan["resumos"]
    ]
    return {"meta": scan["meta"], "total_resumos": scan["total_resumos"], "paginas_pdf": scan["paginas_pdf"],
            "resultados": results, "filename": filename}, HTTPStatus.OK


class LattesHandler(BaseHTTPRequestHandler):
    """HTTP request handler for LattesFácil API and static frontend."""

    server_version = "LattesFacil/1.0"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self) -> bytes | None:
        """Lê o corpo; devolve None (e responde 413) se passar do limite."""
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length > MAX_UPLOAD_BYTES:
            self._send_json({"error": "Arquivo grande demais (máximo 60 MB)."}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return None
        return self.rfile.read(length) if length > 0 else b""

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json({"ok": True, "service": "LattesFácil"})
            return

        if path == "/api/radar":
            qs = parse_qs(parsed.query)
            autor = (qs.get("autor") or [""])[0].strip()
            orcid = (qs.get("orcid") or [""])[0].strip() or None
            try:
                obras = buscar_obras_radar(autor, orcid=orcid)
                self._send_json({"ok": True, "obras": obras})
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc), "obras": []}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/lattes/ping":
            # Sinal do conector (roda na aba do Lattes). GET para funcionar como "beacon" de imagem, sem CORS.
            qs = parse_qs(parsed.query)
            sid = (qs.get("sid") or [""])[0]
            if SID_RE.match(sid):
                if len(LATTES_STATUS) > 200:
                    LATTES_STATUS.clear()
                LATTES_STATUS[sid] = {
                    "online": (qs.get("online") or ["0"])[0] == "1",
                    "name": (qs.get("name") or [""])[0][:120],
                    "ts": time.time(),
                }
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        if path == "/api/lattes/status":
            sid = (parse_qs(parsed.query).get("sid") or [""])[0]
            entry = LATTES_STATUS.get(sid) if SID_RE.match(sid) else None
            if not entry:
                self._send_json({"seen": False})
            else:
                self._send_json({"seen": True, "online": entry["online"], "name": entry["name"],
                                 "age": round(time.time() - entry["ts"], 1)})
            return

        if path == "/api/records":
            with db() as conn:
                rows = conn.execute(
                    "SELECT id, owner, titulo, payload, created_at FROM records ORDER BY created_at DESC LIMIT 50"
                ).fetchall()
            records = [
                {
                    "id": r[0],
                    "owner": r[1],
                    "titulo": r[2],
                    "data": json.loads(r[3]),
                    "created_at": r[4],
                }
                for r in rows
            ]
            self._send_json({"records": records})
            return

        if path == "/api/dossie/download":
            qs = parse_qs(parsed.query)
            uid = (qs.get("id") or [""])[0]
            nome = (qs.get("nome") or [""])[0]
            data = None
            with UPLOADS_LOCK:
                up = UPLOADS.get(uid) if SID_RE.match(uid) else None
                if up and up.get("data"):
                    data = up["data"]
                    if not nome and up.get("name"):
                        nome = up["name"]
            if not data:
                # Se for download do exemplo oficial (SEMIC UFMA)
                if uid == "sample" or (qs.get("sample") or [""])[0] == "1":
                    sample_file = BASE_DIR / "exemplos" / "2024-SEMICresumo.pdf"
                    if sample_file.exists():
                        data = sample_file.read_bytes()
            if not data:
                self._send_json({"error": "Arquivo não encontrado ou sessão expirada."}, HTTPStatus.NOT_FOUND)
                return
            if not nome:
                nome = "comprovante_padronizado.pdf"
            if not nome.lower().endswith(".pdf"):
                nome += ".pdf"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{nome}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/api/dossie/padronizar":
            qs = parse_qs(parsed.query)
            params = {k: v[0] for k, v in qs.items()}
            nome = gerar_nome_padronizado(params)
            ano = extrair_ano(params)
            self._send_json({
                "ok": True,
                "nome_padronizado": nome,
                "caminho_sugerido": f"{ano}/{nome}",
            })
            return

        if path.startswith("/exemplos/"):
            rel_exemplo = path.replace("/exemplos/", "", 1).lstrip("/")
            target_ex = (BASE_DIR / "exemplos" / rel_exemplo).resolve()
            if target_ex.is_relative_to((BASE_DIR / "exemplos").resolve()) and target_ex.is_file():
                ctype, _ = mimetypes.guess_type(str(target_ex))
                raw = target_ex.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", f"{ctype or 'application/octet-stream'}")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return

        # Serve static files
        rel_path = "index.html" if path == "/" else path.lstrip("/")
        target = (STATIC_DIR / rel_path).resolve()
        if not target.is_relative_to(STATIC_DIR.resolve()) or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        ctype, _ = mimetypes.guess_type(str(target))
        raw = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{ctype or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()
        if body is None:
            return
        ctype = self.headers.get("Content-Type", "")

        if path == "/api/upload/chunk":
            # Envio em pedaços de ~1 MB: túneis lentos derrubam requisições longas, então cada pedaço é curto.
            qs = parse_qs(parsed.query)
            uid = (qs.get("id") or [""])[0]
            try:
                i, n = int((qs.get("i") or ["-1"])[0]), int((qs.get("n") or ["0"])[0])
            except ValueError:
                i, n = -1, 0
            if not SID_RE.match(uid) or not (0 <= i < n <= 100) or len(body) > MAX_CHUNK:
                self._send_json({"error": "Pedaço de arquivo inválido."}, HTTPStatus.BAD_REQUEST)
                return
            with UPLOADS_LOCK:
                _purge_uploads()
                up = UPLOADS.setdefault(uid, {"chunks": {}, "n": n, "name": "", "ts": time.time(), "data": None})
                up["name"] = (qs.get("name") or [""])[0][:200] or up["name"]
                up["n"], up["ts"] = n, time.time()
                up["chunks"][i] = body
                received = len(up["chunks"])
            self._send_json({"ok": True, "received": received})
            return

        if path == "/api/upload/finish":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                uid = str(payload.get("id", ""))
                usuario = str(payload.get("usuario", "")).strip()
                with UPLOADS_LOCK:
                    up = UPLOADS.get(uid) if SID_RE.match(uid) else None
                    if not up:
                        self._send_json({"error": "Envio não encontrado ou vencido. Envie o arquivo de novo.", "expired": True}, HTTPStatus.GONE)
                        return
                    faltam = [k for k in range(up["n"]) if k not in up["chunks"]]
                    if faltam:
                        self._send_json({"error": "Faltam pedaços do arquivo.", "missing": faltam[:20]}, HTTPStatus.BAD_REQUEST)
                        return
                    data = b"".join(up["chunks"][k] for k in range(up["n"]))
                    up.update(data=data, chunks={}, ts=time.time())
                    filename = up["name"] or "arquivo.pdf"
                result = process_extract(filename, data, usuario)
                result["upload_id"] = uid
                self._send_json(result)
            except Exception:
                self._send_json({"error": "Falha na extração do arquivo. Verifique se é um PDF válido."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/extract":
            try:
                if "multipart/form-data" in ctype:
                    form_fields, parsed_file = parse_multipart(ctype, body)
                    if not parsed_file:
                        self._send_json({"error": "Nenhum arquivo encontrado no envio."}, HTTPStatus.BAD_REQUEST)
                        return
                    uid = str(uuid.uuid4()).replace("-", "")[:16]
                    with UPLOADS_LOCK:
                        _purge_uploads()
                        UPLOADS[uid] = {"chunks": {}, "n": 1, "name": parsed_file[0], "ts": time.time(), "data": parsed_file[1]}
                    res = process_extract(parsed_file[0], parsed_file[1], form_fields.get("usuario", "").strip())
                    res["upload_id"] = uid
                    self._send_json(res)
                    return

                payload = json.loads(body.decode("utf-8") or "{}")
                raw_text = payload.get("text", "")
                if not raw_text.strip():
                    self._send_json({"error": "Envie um arquivo PDF ou cole o texto da evidência."}, HTTPStatus.BAD_REQUEST)
                    return
                usuario_txt = str(payload.get("usuario", "")).strip()
                if doi_only(raw_text):
                    extracted = parse_artigo("", usuario_txt, doi=doi_only(raw_text))
                elif is_certificate(raw_text):
                    extracted = parse_certificado(raw_text, usuario_txt)
                elif is_article(raw_text):
                    extracted = parse_artigo(raw_text, usuario_txt)
                elif is_orientacao(raw_text):
                    extracted = parse_orientacao(raw_text, usuario_txt)
                else:
                    extracted = parse_evidence_text(raw_text, filename=payload.get("filename", ""))
                nome_padrao = gerar_nome_padronizado(extracted)
                ano = extrair_ano(extracted)
                self._send_json({
                    "extracted": extracted,
                    "raw_text": raw_text[:4000],
                    "nome_padronizado": nome_padrao,
                    "caminho_sugerido": f"{ano}/{nome_padrao}",
                })
            except Exception:
                self._send_json({"error": "Falha na extração do arquivo. Verifique se é um PDF válido."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/caderno":
            try:
                if "application/json" in ctype:
                    payload = json.loads(body.decode("utf-8") or "{}")
                    uid = str(payload.get("upload_id", ""))
                    with UPLOADS_LOCK:
                        up = UPLOADS.get(uid) if SID_RE.match(uid) else None
                        data = up["data"] if up else None
                        if up:
                            up["ts"] = time.time()
                        filename = up["name"] if up else ""
                    if not data:
                        self._send_json({"error": "Arquivo vencido no servidor. Envie o caderno de novo.", "expired": True}, HTTPStatus.GONE)
                        return
                    result, status = run_caderno(data, filename, str(payload.get("pesquisador", "")))
                    self._send_json(result, status)
                    return
                fields, file_part = parse_multipart(ctype, body) if "multipart/form-data" in ctype else ({}, None)
                if not file_part or not file_part[0].lower().endswith(".pdf"):
                    self._send_json({"error": "Envie o PDF do caderno de resumos."}, HTTPStatus.BAD_REQUEST)
                    return
                result, status = run_caderno(file_part[1], file_part[0], fields.get("pesquisador", ""))
                self._send_json(result, status)
            except Exception:
                self._send_json({"error": "Falha ao ler o caderno de resumos."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/compliance":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                alerts = verificar_conformidade(payload)
                self._send_json({"alerts": alerts})
            except Exception:
                self._send_json({"error": "Falha na verificação de conformidade."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/sanitize":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                sanitized = sanitizar_metadados(payload)
                alerts = verificar_conformidade(sanitized)
                self._send_json({"sanitized": sanitized, "alerts": alerts})
            except Exception:
                self._send_json({"error": "Falha na sanitização de metadados."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/dossie/padronizar":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                if "lote" in payload or "arquivos" in payload:
                    itens = payload.get("lote") or payload.get("arquivos") or []
                    res = organizar_lote_comprovantes(itens)
                    self._send_json(res)
                    return
                dados = payload.get("dados") if isinstance(payload.get("dados"), dict) else payload
                nome = gerar_nome_padronizado(dados)
                ano = extrair_ano(dados)
                self._send_json({
                    "ok": True,
                    "nome_padronizado": nome,
                    "caminho_sugerido": f"{ano}/{nome}",
                })
            except Exception as exc:
                self._send_json({"error": f"Falha na padronização: {str(exc)}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/dossie/zip":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                itens = payload.get("lote") or payload.get("arquivos") or []
                zip_bytes = gerar_zip_dossie(itens)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", 'attachment; filename="dossie_academico_capes.zip"')
                self.send_header("Content-Length", str(len(zip_bytes)))
                self.end_headers()
                self.wfile.write(zip_bytes)
            except Exception as exc:
                self._send_json({"error": f"Falha ao gerar ZIP do dossiê: {str(exc)}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/enrich":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                result = enrich_missing_fields(payload)
                self._send_json(result)
            except Exception as exc:
                self._send_json({"error": "Falha ao buscar dados faltantes."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/records":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                rec_id = payload.get("id") or str(uuid.uuid4())[:8]
                owner = (payload.get("owner") or "Convidado").strip()[:60]
                data = payload.get("data") or {}
                titulo = (data.get("titulo") or "Resumo sem título").strip()[:200]
                now = datetime.now(timezone.utc).isoformat()
                with db() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO records (id, owner, titulo, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                        (rec_id, owner, titulo, json.dumps(data, ensure_ascii=False), now),
                    )
                    conn.commit()
                self._send_json({"ok": True, "id": rec_id, "created_at": now})
            except Exception as exc:
                self._send_json({"error": "Falha ao salvar registro."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/records/"):
            rec_id = parsed.path.split("/")[-1]
            with db() as conn:
                conn.execute("DELETE FROM records WHERE id = ?", (rec_id,))
                conn.commit()
            self._send_json({"ok": True})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")


def main() -> None:
    init_db()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), LattesHandler)
    print(f"LattesFácil rodando em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
