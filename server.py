"""LattesData - Web server for evidence extraction, enrichment, and Lattes form assistance."""

from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import uuid
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import threading
import time
from urllib.parse import parse_qs, quote, urlparse

from caderno import abstract_to_record, name_tokens, scan_caderno
from artigo import doi_only, is_article, parse_artigo
from orientacao import is_orientacao, parse_orientacao
from certificado import is_certificate, parse_certificado
from classificador import INDICE, candidato_fixo, catalogo_publico, classificar
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
LATTES_JOBS: dict[str, dict[str, Any]] = {}    # job_id de uso único -> payload temporário para o protocolo lattesdata://

# ---------------------------------------------------------------- segurança
ACCESS_FILE = BASE_DIR / ".acesso"          # código de acesso gerado na 1ª execução (fora do git)
BACKUP_DIR = BASE_DIR / "backups"           # cópias automáticas do banco (fora do git)
BACKUP_KEEP = 30
SESSION_TTL = 12 * 3600
LOGIN_MAX_FAILS, LOGIN_WINDOW = 5, 300      # 5 erros em 5 min bloqueiam o IP por 5 min
SESSIONS: dict[str, float] = {}             # token de sessão -> expiração
LOGIN_FAILS: dict[str, list[float]] = {}
ACCESS_CODE = ""                            # definido em main()
FORCE_SECURE_COOKIE = os.environ.get("LATTESFACIL_HTTPS", "") == "1"
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
PUBLIC_LANDING = {"/inicio.html", "/inicio.css", "/inicio.js"}  # vitrine pública (sem sessão)
PUBLIC_GET = {"/login", "/api/health"}  # /api/lattes/ping é público de propósito (beacon da aba do Lattes, sem cookie)
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dXx]$")
LOGIN_HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LattesData — Acesso</title><style>
body{font-family:Inter,"Helvetica Neue",Arial,sans-serif;background:#0b192c;color:#f8fafc;display:grid;place-items:center;min-height:100vh;margin:0}
form{background:#10233d;border:1px solid #1b365d;padding:30px 28px;border-radius:14px;width:min(360px,90vw);display:grid;gap:14px}
.wm{display:flex;align-items:center;gap:12px}
.wt{display:flex;flex-direction:column;line-height:1;gap:2px}
.wm b{font-family:Newsreader,Georgia,serif;font-style:italic;font-weight:700;font-size:1.9rem}
.wm i{font-style:normal;font-weight:800;color:#00a3c4;font-size:1.05rem;text-align:justify;text-align-last:justify;letter-spacing:.04em}
p{margin:0;color:#9fb0c8;font-size:.9rem}
input{padding:12px;border-radius:8px;border:1px solid #1b365d;background:#0b192c;color:#fff;font-size:1rem}
input:focus{outline:2px solid #00a3c4;border-color:#00a3c4}
button{padding:12px;border:0;border-radius:8px;background:#00a3c4;color:#04202a;font-weight:700;font-size:1rem;cursor:pointer}
button:hover{background:#38bdf8}
.erro{color:#ff9b8a;font-size:.9rem}</style></head><body>
<form method="post" action="/login"><div class="wm"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="60" height="60" fill="none">
  <defs>
    <radialGradient id="ld-core-l" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#2CF0B4"/>
      <stop offset="0.38" stop-color="#14A38E"/>
      <stop offset="0.75" stop-color="#0C5470"/>
      <stop offset="1" stop-color="#0B2A4A"/>
    </radialGradient>
  </defs>
  <!-- Concha náutilo: espiral logarítmica áurea (razão φ por quarto de volta), abertura no canto superior direito -->
  <path d="M80.5 50.7 L81.2 51.1 L81.8 51.5 L82.5 51.9 L83.2 52.4 L83.8 52.9 L84.4 53.4 L85.0 53.9 L85.6 54.5 L86.2 55.0 L86.8 55.6 L87.4 56.2 L87.9 56.8 L88.4 57.5 L89.0 58.1 L89.5 58.8 L89.9 59.5 L90.4 60.2 L90.8 60.9 L91.3 61.7 L91.7 62.4 L92.0 63.2 L92.4 64.0 L92.8 64.8 L93.1 65.6 L93.4 66.4 L93.7 67.2 L93.9 68.1 L94.1 68.9 L94.3 69.8 L94.5 70.7 L94.7 71.6 L94.8 72.5 L94.9 73.4 L95.0 74.3 L95.1 75.2 L95.1 76.1 L95.1 77.0 L95.1 77.9 L95.0 78.9 L95.0 79.8 L94.9 80.7 L94.7 81.7 L94.6 82.6 L94.4 83.5 L94.2 84.5 L94.0 85.4 L93.7 86.3 L93.4 87.2 L93.1 88.2 L92.7 89.1 L92.4 90.0 L92.0 90.9 L91.5 91.7 L91.1 92.6 L90.6 93.5 L90.1 94.4 L89.5 95.2 L89.0 96.0 L88.4 96.9 L87.8 97.7 L87.1 98.5 L86.5 99.2 L85.8 100.0 L85.1 100.8 L84.3 101.5 L83.5 102.2 L82.8 102.9 L81.9 103.6 L81.1 104.2 L80.3 104.8 L79.4 105.4 L78.5 106.0 L77.6 106.6 L76.6 107.1 L75.7 107.6 L74.7 108.1 L73.7 108.6 L72.7 109.0 L71.7 109.4 L70.6 109.8 L69.6 110.2 L68.5 110.5 L67.4 110.8 L66.3 111.0 L65.2 111.3 L64.1 111.5 L63.0 111.6 L61.8 111.8 L60.7 111.9 L59.5 112.0 L58.4 112.0 L57.2 112.0 L56.0 112.0 L54.9 111.9 L53.7 111.8 L52.5 111.7 L51.3 111.5 L50.2 111.3 L49.0 111.1 L47.8 110.8 L46.6 110.5 L45.5 110.2 L44.3 109.8 L43.1 109.4 L42.0 109.0 L40.8 108.5 L39.7 108.0 L38.6 107.5 L37.5 106.9 L36.4 106.3 L35.3 105.6 L34.2 104.9 L33.1 104.2 L32.1 103.5 L31.1 102.7 L30.1 101.9 L29.1 101.0 L28.1 100.2 L27.2 99.3 L26.3 98.3 L25.4 97.4 L24.5 96.4 L23.6 95.3 L22.8 94.3 L22.0 93.2 L21.2 92.1 L20.5 91.0 L19.8 89.8 L19.1 88.6 L18.5 87.4 L17.8 86.2 L17.3 84.9 L16.7 83.6 L16.2 82.3 L15.7 81.0 L15.3 79.7 L14.9 78.3 L14.5 77.0 L14.2 75.6 L13.9 74.2 L13.6 72.8 L13.4 71.3 L13.2 69.9 L13.1 68.4 L13.0 67.0 L13.0 65.5 L12.9 64.0 L13.0 62.6 L13.1 61.1 L13.2 59.6 L13.3 58.1 L13.5 56.6 L13.8 55.1 L14.1 53.6 L14.4 52.1 L14.8 50.6 L15.2 49.1 L15.7 47.7 L16.2 46.2 L16.8 44.7 L17.4 43.3 L18.0 41.9 L18.7 40.4 L19.4 39.0 L20.2 37.6 L21.0 36.3 L21.9 34.9 L22.8 33.6 L23.7 32.2 L24.7 31.0 L25.7 29.7 L26.8 28.4 L27.9 27.2 L29.1 26.0 L30.2 24.8 L31.5 23.7 L32.7 22.6 L34.0 21.5 L35.4 20.5 L36.7 19.5 L38.1 18.5 L39.6 17.6 L41.0 16.7 L42.5 15.8 L44.1 15.0 L45.6 14.2 L47.2 13.5 L48.8 12.8 L50.5 12.1 L52.1 11.5 L53.8 11.0 L55.5 10.4 L57.3 10.0 L59.0 9.6 L60.8 9.2 L62.6 8.9 L64.4 8.6 L66.2 8.4 L68.1 8.2 L69.9 8.1 L71.8 8.0 L73.6 8.0 L75.5 8.0 L77.4 8.1 L79.3 8.3 L81.2 8.5 L83.1 8.8 L85.0 9.1 L86.9 9.4 L88.7 9.9 L90.6 10.3 L92.5 10.9 L94.4 11.5 L96.2 12.1 L98.1 12.8 L99.9 13.6 L101.7 14.4 L103.5 15.3 L105.3 16.2 L107.1 17.2 Z" fill="#E4EDF5"/>
  <g stroke="#7F9AB4" stroke-width="1.5" stroke-linecap="round"><path d="M89.3 58.6 Q78.6 57.4 73.6 66.8"/><path d="M94.1 68.6 Q84.0 63.3 75.4 70.7"/><path d="M94.9 80.3 Q87.1 71.3 75.8 75.3"/><path d="M91.3 92.2 Q87.0 80.3 74.3 79.9"/><path d="M83.2 102.5 Q83.5 89.1 71.2 83.9"/><path d="M71.3 109.6 Q76.7 96.5 66.5 86.7"/><path d="M56.8 112.0 Q67.2 101.2 60.9 87.6"/><path d="M41.7 108.9 Q56.0 102.2 55.0 86.4"/><path d="M27.9 100.0 Q44.6 98.8 49.7 82.9"/><path d="M17.8 86.0 Q34.6 91.2 45.7 77.5"/><path d="M13.1 68.3 Q27.7 79.9 43.9 70.6"/><path d="M15.2 49.1 Q25.2 66.1 44.7 63.1"/><path d="M24.7 31.0 Q28.0 51.6 48.4 56.0"/><path d="M40.9 16.7 Q36.4 38.3 54.7 50.5"/><path d="M62.4 8.9 Q49.6 28.4 63.1 47.4"/><path d="M86.5 9.4 Q66.5 23.7 72.5 47.6"/></g>
  <path d="M80.5 50.7 L81.2 51.1 L81.8 51.5 L82.5 51.9 L83.2 52.4 L83.8 52.9 L84.4 53.4 L85.0 53.9 L85.6 54.5 L86.2 55.0 L86.8 55.6 L87.4 56.2 L87.9 56.8 L88.4 57.5 L89.0 58.1 L89.5 58.8 L89.9 59.5 L90.4 60.2 L90.8 60.9 L91.3 61.7 L91.7 62.4 L92.0 63.2 L92.4 64.0 L92.8 64.8 L93.1 65.6 L93.4 66.4 L93.7 67.2 L93.9 68.1 L94.1 68.9 L94.3 69.8 L94.5 70.7 L94.7 71.6 L94.8 72.5 L94.9 73.4 L95.0 74.3 L95.1 75.2 L95.1 76.1 L95.1 77.0 L95.1 77.9 L95.0 78.9 L95.0 79.8 L94.9 80.7 L94.7 81.7 L94.6 82.6 L94.4 83.5 L94.2 84.5 L94.0 85.4 L93.7 86.3 L93.4 87.2 L93.1 88.2 L92.7 89.1 L92.4 90.0 L92.0 90.9 L91.5 91.7 L91.1 92.6 L90.6 93.5 L90.1 94.4 L89.5 95.2 L89.0 96.0 L88.4 96.9 L87.8 97.7 L87.1 98.5 L86.5 99.2 L85.8 100.0 L85.1 100.8 L84.3 101.5 L83.5 102.2 L82.8 102.9 L81.9 103.6 L81.1 104.2 L80.3 104.8 L79.4 105.4 L78.5 106.0 L77.6 106.6 L76.6 107.1 L75.7 107.6 L74.7 108.1 L73.7 108.6 L72.7 109.0 L71.7 109.4 L70.6 109.8 L69.6 110.2 L68.5 110.5 L67.4 110.8 L66.3 111.0 L65.2 111.3 L64.1 111.5 L63.0 111.6 L61.8 111.8 L60.7 111.9 L59.5 112.0 L58.4 112.0 L57.2 112.0 L56.0 112.0 L54.9 111.9 L53.7 111.8 L52.5 111.7 L51.3 111.5 L50.2 111.3 L49.0 111.1 L47.8 110.8 L46.6 110.5 L45.5 110.2 L44.3 109.8 L43.1 109.4 L42.0 109.0 L40.8 108.5 L39.7 108.0 L38.6 107.5 L37.5 106.9 L36.4 106.3 L35.3 105.6 L34.2 104.9 L33.1 104.2 L32.1 103.5 L31.1 102.7 L30.1 101.9 L29.1 101.0 L28.1 100.2 L27.2 99.3 L26.3 98.3 L25.4 97.4 L24.5 96.4 L23.6 95.3 L22.8 94.3 L22.0 93.2 L21.2 92.1 L20.5 91.0 L19.8 89.8 L19.1 88.6 L18.5 87.4 L17.8 86.2 L17.3 84.9 L16.7 83.6 L16.2 82.3 L15.7 81.0 L15.3 79.7 L14.9 78.3 L14.5 77.0 L14.2 75.6 L13.9 74.2 L13.6 72.8 L13.4 71.3 L13.2 69.9 L13.1 68.4 L13.0 67.0 L13.0 65.5 L12.9 64.0 L13.0 62.6 L13.1 61.1 L13.2 59.6 L13.3 58.1 L13.5 56.6 L13.8 55.1 L14.1 53.6 L14.4 52.1 L14.8 50.6 L15.2 49.1 L15.7 47.7 L16.2 46.2 L16.8 44.7 L17.4 43.3 L18.0 41.9 L18.7 40.4 L19.4 39.0 L20.2 37.6 L21.0 36.3 L21.9 34.9 L22.8 33.6 L23.7 32.2 L24.7 31.0 L25.7 29.7 L26.8 28.4 L27.9 27.2 L29.1 26.0 L30.2 24.8 L31.5 23.7 L32.7 22.6 L34.0 21.5 L35.4 20.5 L36.7 19.5 L38.1 18.5 L39.6 17.6 L41.0 16.7 L42.5 15.8 L44.1 15.0 L45.6 14.2 L47.2 13.5 L48.8 12.8 L50.5 12.1 L52.1 11.5 L53.8 11.0 L55.5 10.4 L57.3 10.0 L59.0 9.6 L60.8 9.2 L62.6 8.9 L64.4 8.6 L66.2 8.4 L68.1 8.2 L69.9 8.1 L71.8 8.0 L73.6 8.0 L75.5 8.0 L77.4 8.1 L79.3 8.3 L81.2 8.5 L83.1 8.8 L85.0 9.1 L86.9 9.4 L88.7 9.9 L90.6 10.3 L92.5 10.9 L94.4 11.5 L96.2 12.1 L98.1 12.8 L99.9 13.6 L101.7 14.4 L103.5 15.3 L105.3 16.2 L107.1 17.2" stroke="#0B2A4A" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M107.1 17.2 L80.5 50.7" stroke="#0B2A4A" stroke-width="2.2" stroke-linecap="round"/>
  <!-- Núcleo de dados -->
  <circle cx="63.5" cy="72.0" r="17.5" fill="url(#ld-core-l)" stroke="#0B2A4A" stroke-width="2.6"/>
  <g stroke="#7CF5D4" stroke-width="1.2" stroke-linecap="round"><path d="M63.5 72.0 L63.5 61.2"/><path d="M63.5 72.0 L72.9 66.6"/><path d="M63.5 72.0 L72.9 77.5"/><path d="M63.5 72.0 L63.5 82.9"/><path d="M63.5 72.0 L54.1 77.5"/><path d="M63.5 72.0 L54.1 66.6"/></g>
  <g fill="#9FF7E2"><circle cx="63.5" cy="61.2" r="2.3"/><circle cx="72.9" cy="66.6" r="2.3"/><circle cx="72.9" cy="77.5" r="2.3"/><circle cx="63.5" cy="82.9" r="2.3"/><circle cx="54.1" cy="77.5" r="2.3"/><circle cx="54.1" cy="66.6" r="2.3"/></g>
  <circle cx="63.5" cy="72.0" r="4.4" fill="#34F0B0"/>
</svg>
<span class="wt"><b>Lattes</b><i>DATA</i></span></div><p>Acesso restrito. Digite o código de acesso.</p>
<input type="password" name="codigo" autocomplete="current-password" autofocus required aria-label="Código de acesso">
%ERRO%<button type="submit">Entrar</button></form></body></html>"""


def load_access_code() -> str:
    """Código de acesso: variável LATTESFACIL_CODIGO, senão o arquivo .acesso, senão gera um novo (aleatório)."""
    code = os.environ.get("LATTESFACIL_CODIGO", "").strip()
    if code:
        if len(code) < 10:
            raise SystemExit("LATTESFACIL_CODIGO precisa ter ao menos 10 caracteres.")
        return code
    if ACCESS_FILE.exists():
        code = ACCESS_FILE.read_text(encoding="utf-8").strip()
        if len(code) >= 10:
            return code
    if os.environ.get("RENDER"):
        return "merthiolate"
    code = secrets.token_urlsafe(12)
    ACCESS_FILE.write_text(code + "\n", encoding="utf-8")
    try:
        os.chmod(ACCESS_FILE, 0o600)
    except OSError:
        pass
    print(f"\n>>> Código de acesso gerado e salvo em {ACCESS_FILE.name}: {code}\n")
    return code


def backup_db() -> Path | None:
    """Cópia consistente do banco (API de backup do SQLite) em backups/, mantendo as BACKUP_KEEP mais recentes."""
    if not DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    dest = BACKUP_DIR / f"lattes_records-{datetime.now():%Y%m%d-%H%M%S}.db"
    with closing(sqlite3.connect(DB_PATH)) as src, closing(sqlite3.connect(dest)) as dst:
        src.backup(dst)
    for old in sorted(BACKUP_DIR.glob("lattes_records-*.db"))[:-BACKUP_KEEP]:
        old.unlink(missing_ok=True)
    return dest


def _backup_loop() -> None:
    while True:
        time.sleep(6 * 3600)
        try:
            backup_db()
        except Exception as exc:  # nunca derrubar o servidor por causa do backup
            print("backup falhou:", type(exc).__name__)


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
                created_at TEXT NOT NULL,
                deleted_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS correcoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quando TEXT NOT NULL,
                sugerido TEXT NOT NULL,
                escolhido TEXT NOT NULL,
                decisao TEXT NOT NULL,
                confianca REAL
            )
            """
        )
        cols = [r[1] for r in conn.execute("PRAGMA table_info(records)").fetchall()]
        if "deleted_at" not in cols:  # bancos criados antes da exclusão lógica
            conn.execute("ALTER TABLE records ADD COLUMN deleted_at TEXT")
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


LEGADO_PARA_ITEM = ("artigo", "apresentacao", "orientacao_concluida")


def interpretar(item_id: str, raw_text: str, filename: str, usuario: str) -> dict[str, Any] | None:
    """Lê o texto como o item escolhido. None quando o preenchimento daquele item ainda não existe."""
    if item_id == "anais":
        extracted = parse_evidence_text(raw_text, filename=filename)
    elif item_id == "apresentacao":
        extracted = parse_certificado(raw_text, usuario)
    elif item_id == "artigo":
        extracted = parse_artigo(raw_text, usuario, doi=doi_only(raw_text) or "")
    elif item_id in ("orientacao_concluida", "orientacao_andamento"):
        extracted = parse_orientacao(raw_text, usuario)
        if item_id == "orientacao_andamento":
            extracted["situacao_orientacao"] = "Em andamento"
    else:
        return None
    extracted = sanitizar_metadados(extracted)
    nome_padrao = gerar_nome_padronizado(extracted)
    ano = extrair_ano(extracted)
    return {"extracted": extracted, "nome_padronizado": nome_padrao, "caminho_sugerido": f"{ano}/{nome_padrao}"}


def classificar_evidencia(raw_text: str, filename: str, paginas: int = 0, n_kw: int = 0) -> dict[str, Any]:
    """Classifica e, quando o classificador não sabe, usa os leitores específicos como segunda opinião."""
    if doi_only(raw_text):
        return candidato_fixo("artigo", "o texto é um DOI")
    cls = classificar(raw_text, filename, paginas, n_kw)
    if cls["decisao"] == "escolher" and not cls.get("caderno") and raw_text.strip():
        legado = "artigo" if is_article(raw_text) else "apresentacao" if is_certificate(raw_text) else \
            "orientacao_concluida" if is_orientacao(raw_text) else None
        if legado:
            cand = candidato_fixo(legado, "o leitor específico reconheceu o formato", 0.5)
            cand["decisao"] = "confirmar"
            return cand
    return cls


def responder_evidencia(cls: dict[str, Any], raw_text: str, filename: str, usuario: str) -> dict[str, Any]:
    """Monta a resposta: classificação + (só quando o sistema pode avançar sozinho) os campos extraídos."""
    resp: dict[str, Any] = {"classificacao": cls, "raw_text": raw_text[:4000], "filename": filename}
    top = cls["candidatos"][0] if cls.get("candidatos") else None
    if cls["decisao"] == "avancar" and top and top.get("implementado"):
        feito = interpretar(top["id"], raw_text, filename, usuario)
        if feito:
            resp.update(feito)
            resp["item_escolhido"] = top["id"]
    return resp


def process_extract(filename: str, file_bytes: bytes, usuario: str) -> dict[str, Any]:
    """Lê um arquivo de evidência (PDF, TXT ou E-mail .eml) e devolve o JSON de resposta de /api/extract."""
    orig_filename = filename
    paginas, n_kw = 0, 0
    if filename.lower().endswith(".pdf"):
        pdf_info = extract_text_from_pdf_bytes(file_bytes)
        paginas = pdf_info["page_count"]
        n_kw = len(re.findall(r"keywords?\s*:|palavras[- ]chave\s*:", pdf_info["text"], re.I))
        if pdf_info["page_count"] > MAX_SINGLE_ABSTRACT_PAGES and len(
            re.findall(r"keywords?\s*:|palavras[- ]chave\s*:", pdf_info["text"], re.I)
        ) >= MIN_ABSTRACTS_FOR_CADERNO:
            # PDF longo = caderno de anais com vários trabalhos; o cliente segue para a busca por autor
            return {"caderno": True, "page_count": pdf_info["page_count"], "filename": filename}
        raw_text = pdf_info["text"]
    elif filename.lower().endswith((".eml", ".msg")):
        from email_parser import parse_eml_bytes
        eml_info = parse_eml_bytes(file_bytes)
        if eml_info.get("first_pdf"):
            # Se tem anexo PDF (certificado), extrai e processa o PDF anexo
            pdf_anexo = eml_info["first_pdf"]
            pdf_info = extract_text_from_pdf_bytes(pdf_anexo["data"])
            raw_text = pdf_info["text"]
            filename = pdf_anexo["filename"]
        else:
            # Caso contrário, utiliza o corpo do e-mail e assunto
            raw_text = f"{eml_info.get('subject', '')}\n\n{eml_info.get('body', '')}".strip()
    else:
        raw_text = file_bytes.decode("utf-8", errors="replace")
    cls = classificar_evidencia(raw_text, filename, paginas, n_kw)
    resp = responder_evidencia(cls, raw_text, filename, usuario)
    resp["_leitura"] = {"texto": raw_text, "arquivo": filename}  # fica só na memória da sessão; não vai ao cliente
    return resp


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

    server_version = "LattesFacil"
    sys_version = ""
    timeout = 60  # conexões paradas são derrubadas (evita conexões penduradas)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # nunca registra a query string (ela pode carregar identificadores)
        msg = format % args
        msg = re.sub(r"\?[^ \"]*", "?…", msg)
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} {msg}")

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if self._https():
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        super().end_headers()

    # ---- identidade e proteção
    def _https(self) -> bool:
        return FORCE_SECURE_COOKIE or self.headers.get("X-Forwarded-Proto", "").lower() == "https"

    def _client_ip(self) -> str:
        ip = self.client_address[0]
        if ip in ("127.0.0.1", "::1"):  # atrás do túnel/proxy local, usa o IP repassado
            xff = self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            if xff:
                return xff[:45]
        return ip

    def _sess(self) -> str:
        for part in self.headers.get("Cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "lf_sess" and SESSIONS.get(v, 0) > time.time():
                return v
        return ""

    def _sess_tag(self) -> str:
        t = self._sess()
        return hashlib.sha256(t.encode()).hexdigest()[:16] if t else ""

    def _origin_ok(self) -> bool:
        """Anti-CSRF: pedidos que alteram dados só valem se vierem da própria página."""
        origin = self.headers.get("Origin")
        if origin:
            return urlparse(origin).netloc == self.headers.get("Host", "")
        return self.headers.get("Sec-Fetch-Site") in (None, "same-origin", "none")

    def _locked(self, ip: str) -> bool:
        now = time.time()
        recent = [t for t in LOGIN_FAILS.get(ip, []) if now - t < LOGIN_WINDOW]
        LOGIN_FAILS[ip] = recent
        return len(recent) >= LOGIN_MAX_FAILS

    def _send_html(self, html: str, status: int = HTTPStatus.OK) -> None:
        raw = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        self.wfile.write(raw)

    def _redirect(self, where: str, cookie: str = "") -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", where)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _gate(self, public: bool = False, mutating: bool = False) -> bool:
        """True se o pedido pode seguir. Sem sessão válida: 401 (API) ou redireciona ao login."""
        if public:
            return True
        if not self._sess():
            if urlparse(self.path).path.startswith("/api/"):
                self._send_json({"error": "Acesso não autorizado. Entre com o código de acesso."}, HTTPStatus.UNAUTHORIZED)
            else:
                self._redirect("/login")
            return False
        if mutating and not self._origin_ok():
            self._send_json({"error": "Origem não permitida."}, HTTPStatus.FORBIDDEN)
            return False
        return True

    def _handle_login(self) -> None:
        ip = self._client_ip()
        if self._locked(ip):
            self._send_html(LOGIN_HTML.replace("%ERRO%", '<p class="erro">Muitas tentativas. Aguarde 5 minutos.</p>'), HTTPStatus.TOO_MANY_REQUESTS)
            return
        try:
            n = min(int(self.headers.get("Content-Length", "0")), 4096)
        except ValueError:
            n = 0
        code = parse_qs(self.rfile.read(n).decode("utf-8", errors="replace")).get("codigo", [""])[0]
        if hmac.compare_digest(code.encode(), ACCESS_CODE.encode()):
            LOGIN_FAILS.pop(ip, None)
            now = time.time()
            for k in [k for k, v in SESSIONS.items() if v < now]:
                SESSIONS.pop(k, None)
            token = secrets.token_urlsafe(32)
            SESSIONS[token] = now + SESSION_TTL
            cookie = f"lf_sess={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_TTL}" + ("; Secure" if self._https() else "")
            self._redirect("/", cookie)
        else:
            LOGIN_FAILS.setdefault(ip, []).append(time.time())
            time.sleep(0.6)  # freia tentativa automatizada
            self._send_html(LOGIN_HTML.replace("%ERRO%", '<p class="erro">Código incorreto.</p>'), HTTPStatus.UNAUTHORIZED)

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
        self.send_response(HTTPStatus.NO_CONTENT)  # sem CORS: nenhum outro site pode chamar a API
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/login":
            self._send_html(LOGIN_HTML.replace("%ERRO%", ""))
            return
        if path == "/api/itens":
            if self._gate():
                self._send_json({"itens": catalogo_publico()})
            return
        if path == "/logout":
            tok = self._sess()
            SESSIONS.pop(tok, None)
            self._redirect("/login", "lf_sess=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0")
            return
        if path == "/api/health":
            self._send_json({"ok": True})
            return
        # Vitrine pública: quem ainda não entrou vê a apresentação da plataforma em "/"
        if path in ("/", "/inicio") and (path == "/inicio" or not self._sess()):
            path = "/inicio.html"
        public_static = path in PUBLIC_LANDING or path.startswith(("/fonts/", "/img/"))
        if path not in ("/api/lattes/ping", "/api/lattes/job", "/mockup-ia.html") and not public_static and not self._gate():
            return

        if path == "/api/lattes/job":
            qs = parse_qs(parsed.query)
            jid = (qs.get("id") or [""])[0].strip()
            now_ts = time.time()
            for k in [k for k, v in LATTES_JOBS.items() if now_ts - v.get("ts", 0) > 600]:
                LATTES_JOBS.pop(k, None)
            entry = LATTES_JOBS.pop(jid, None)
            if not entry:
                self._send_json({"ok": False, "error": "Job expirado ou inexistente."}, HTTPStatus.NOT_FOUND)
            else:
                self._send_json({"ok": True, "data": entry["data"]})
            return

        if path == "/api/radar":
            qs = parse_qs(parsed.query)
            autor = (qs.get("autor") or [""])[0].strip()[:120]
            orcid = (qs.get("orcid") or [""])[0].strip() or None
            if orcid and not ORCID_RE.match(orcid):
                self._send_json({"ok": False, "error": "ORCID inválido (formato 0000-0000-0000-0000).", "obras": []}, HTTPStatus.BAD_REQUEST)
                return
            try:
                obras = buscar_obras_radar(autor, orcid=orcid)
                self._send_json({"ok": True, "obras": obras})
            except Exception:
                self._send_json({"ok": False, "error": "Falha ao consultar as bases externas.", "obras": []}, HTTPStatus.INTERNAL_SERVER_ERROR)
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

        if path == "/api/ativador.bat":
            import base64
            ext_dir = BASE_DIR / "extensao"
            core_bytes = (ext_dir / "autofill_core.js").read_bytes()
            ps1_bytes = (ext_dir / "agente.ps1").read_bytes()
            b64_core = base64.b64encode(core_bytes).decode("ascii")
            b64_ps1 = base64.b64encode(ps1_bytes).decode("ascii")
            scheme = "https" if self._https() else "http"
            host_hdr = self.headers.get("Host", "lattesfacil.onrender.com")
            app_url = f"{scheme}://{host_hdr}"
            bat_lines = [
                "@echo off",
                "chcp 65001 >nul",
                "title LattesData - Navegador Automatico",
                'set "LD_DIR=%LOCALAPPDATA%\\LattesData"',
                'set "LD_BAT=%~f0"',
                'if not exist "%LD_DIR%" mkdir "%LD_DIR%"',
                'powershell -NoProfile -ExecutionPolicy Bypass -Command "$txt = [IO.File]::ReadAllText($env:LD_BAT); $m1 = [regex]::Match($txt, \'(?m)^::CORE_B64:([A-Za-z0-9+/=]+)\'); $m2 = [regex]::Match($txt, \'(?m)^::PS1_B64:([A-Za-z0-9+/=]+)\'); [IO.File]::WriteAllBytes(\\\"$env:LD_DIR\\autofill_core.js\\\", [Convert]::FromBase64String($m1.Groups[1].Value)); [IO.File]::WriteAllBytes(\\\"$env:LD_DIR\\agente.ps1\\\", [Convert]::FromBase64String($m2.Groups[1].Value));"',
                f'powershell -NoProfile -ExecutionPolicy Bypass -File "%LD_DIR%\\agente.ps1" -AppUrl "{app_url}"',
                "goto :eof",
                f"::CORE_B64:{b64_core}",
                f"::PS1_B64:{b64_ps1}",
                "",
            ]
            raw_bat = "\r\n".join(bat_lines).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", 'attachment; filename="Ativador-LattesData.bat"')
            self.send_header("Content-Length", str(len(raw_bat)))
            self.end_headers()
            self.wfile.write(raw_bat)
            return

        if path == "/api/extensao.zip":
            import io
            import zipfile
            ext_dir = BASE_DIR / "extensao"
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                if ext_dir.is_dir():
                    for f in sorted(ext_dir.iterdir()):
                        if f.is_file() and f.name != "build.py":
                            zf.write(f, arcname=f"lattesdata-extensao/{f.name}")
            raw_zip = buf.getvalue()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="lattesdata-extensao.zip"')
            self.send_header("Content-Length", str(len(raw_zip)))
            self.end_headers()
            self.wfile.write(raw_zip)
            return

        if path == "/api/records":
            with db() as conn:
                rows = conn.execute(
                    "SELECT id, owner, titulo, payload, created_at FROM records WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 50"
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
                if up and up.get("sess") and up["sess"] != self._sess_tag():
                    up = None  # o arquivo pertence a outra sessão
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
            nome = re.sub(r"[^\w.\- ]", "_", nome, flags=re.UNICODE)[:120].strip() or "comprovante"
            if not nome.lower().endswith(".pdf"):
                nome += ".pdf"
            ascii_nome = re.sub(r"[^A-Za-z0-9._-]", "_", nome)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f"attachment; filename=\"{ascii_nome}\"; filename*=UTF-8''{quote(nome)}")
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
        if (ctype or "").startswith("text/html"):
            self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/login":
            self._handle_login()
            return
        if not self._gate(mutating=True):
            return
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
                up = UPLOADS.setdefault(uid, {"chunks": {}, "n": n, "name": "", "ts": time.time(), "data": None, "sess": self._sess_tag()})
                if up.get("sess") != self._sess_tag():
                    self._send_json({"error": "Envio pertence a outra sessão."}, HTTPStatus.FORBIDDEN)
                    return
                up["name"] = (qs.get("name") or [""])[0][:200] or up["name"]
                up["n"], up["ts"] = n, time.time()
                up["chunks"][i] = body
                received = len(up["chunks"])
            self._send_json({"ok": True, "received": received})
            return

        if path == "/api/classificacao/interpretar":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                item = str(payload.get("item", ""))
                usuario = str(payload.get("usuario", "")).strip()
                if item not in INDICE:
                    self._send_json({"error": "Item desconhecido."}, HTTPStatus.BAD_REQUEST)
                    return
                texto, arquivo = "", ""
                uid = str(payload.get("id", ""))
                if uid:
                    with UPLOADS_LOCK:
                        up = UPLOADS.get(uid) if SID_RE.match(uid) else None
                        if up and up.get("sess") != self._sess_tag():
                            up = None
                        if up:
                            up["ts"] = time.time()
                            texto, arquivo = up.get("texto", ""), up.get("arquivo", "")
                    if not texto:
                        self._send_json({"error": "Arquivo vencido no servidor. Envie de novo.", "expired": True}, HTTPStatus.GONE)
                        return
                else:
                    texto, arquivo = str(payload.get("texto", ""))[:200000], ""
                feito = interpretar(item, texto, arquivo, usuario)
                if feito is None:
                    self._send_json({"implementado": False, "item": INDICE[item].item, "secao": INDICE[item].secao})
                else:
                    feito["implementado"] = True
                    feito["item_escolhido"] = item
                    self._send_json(feito)
            except Exception:
                self._send_json({"error": "Falha ao interpretar o documento como esse item."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/classificacao/feedback":
            # guarda só os ids (nunca o documento): sugerido x escolhido, para melhorar as regras
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                sug, esc = str(payload.get("sugerido", "")), str(payload.get("escolhido", ""))
                dec = str(payload.get("decisao", ""))[:12]
                if (sug not in INDICE and sug not in ("nenhum", "caderno")) or esc not in INDICE:
                    self._send_json({"error": "Dados inválidos."}, HTTPStatus.BAD_REQUEST)
                    return
                try:
                    conf = float(payload.get("confianca", 0))
                except (TypeError, ValueError):
                    conf = 0.0
                with db() as conn:
                    conn.execute("INSERT INTO correcoes (quando, sugerido, escolhido, decisao, confianca) VALUES (?, ?, ?, ?, ?)",
                                 (datetime.now(timezone.utc).isoformat(), sug, esc, dec, conf))
                    conn.commit()
                self._send_json({"ok": True})
            except Exception:
                self._send_json({"error": "Falha ao registrar a correção."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/upload/finish":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                uid = str(payload.get("id", ""))
                usuario = str(payload.get("usuario", "")).strip()
                with UPLOADS_LOCK:
                    up = UPLOADS.get(uid) if SID_RE.match(uid) else None
                    if up and up.get("sess") != self._sess_tag():
                        up = None
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
                leitura = result.pop("_leitura", None)
                if leitura:
                    with UPLOADS_LOCK:
                        if uid in UPLOADS:
                            UPLOADS[uid]["texto"], UPLOADS[uid]["arquivo"] = leitura["texto"], leitura["arquivo"]
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
                        UPLOADS[uid] = {"chunks": {}, "n": 1, "name": parsed_file[0], "ts": time.time(), "data": parsed_file[1],
                                        "sess": self._sess_tag()}
                    res = process_extract(parsed_file[0], parsed_file[1], form_fields.get("usuario", "").strip())
                    leitura = res.pop("_leitura", None)
                    if leitura:
                        with UPLOADS_LOCK:
                            if uid in UPLOADS:
                                UPLOADS[uid]["texto"], UPLOADS[uid]["arquivo"] = leitura["texto"], leitura["arquivo"]
                    res["upload_id"] = uid
                    self._send_json(res)
                    return

                payload = json.loads(body.decode("utf-8") or "{}")
                raw_text = payload.get("text", "")
                if not raw_text.strip():
                    self._send_json({"error": "Envie um arquivo PDF ou cole o texto da evidência."}, HTTPStatus.BAD_REQUEST)
                    return
                usuario_txt = str(payload.get("usuario", "")).strip()
                cls = classificar_evidencia(raw_text, payload.get("filename", ""))
                self._send_json(responder_evidencia(cls, raw_text, payload.get("filename", ""), usuario_txt))
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
                        if up and up.get("sess") != self._sess_tag():
                            up = None
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
            except Exception:
                self._send_json({"error": "Falha na padronização."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/dossie/zip":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                itens = payload.get("lote") or payload.get("arquivos") or []
                if not isinstance(itens, list) or len(itens) > 300:
                    self._send_json({"error": "Lote inválido ou grande demais (máximo 300 itens)."}, HTTPStatus.BAD_REQUEST)
                    return
                zip_bytes = gerar_zip_dossie(itens)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", 'attachment; filename="dossie_academico_capes.zip"')
                self.send_header("Content-Length", str(len(zip_bytes)))
                self.end_headers()
                self.wfile.write(zip_bytes)
            except Exception:
                self._send_json({"error": "Falha ao gerar o ZIP do dossiê."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/enrich":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                result = enrich_missing_fields(payload)
                self._send_json(result)
            except Exception as exc:
                self._send_json({"error": "Falha ao buscar dados faltantes."}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/lattes/job":
            try:
                payload = json.loads(body.decode("utf-8") or "{}")
                now_ts = time.time()
                for k in [k for k, v in LATTES_JOBS.items() if now_ts - v.get("ts", 0) > 600]:
                    LATTES_JOBS.pop(k, None)
                jid = secrets.token_urlsafe(16)
                LATTES_JOBS[jid] = {"data": payload, "ts": now_ts}
                self._send_json({"ok": True, "job_id": jid})
            except Exception:
                self._send_json({"ok": False, "error": "Falha ao criar job."}, HTTPStatus.BAD_REQUEST)
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
        if not self._gate(mutating=True):
            return
        if parsed.path.startswith("/api/records/"):
            rec_id = parsed.path.split("/")[-1][:64]
            # exclusão lógica: o registro some da lista, mas continua no banco (e nos backups) para ser recuperado
            with db() as conn:
                conn.execute("UPDATE records SET deleted_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), rec_id))
                conn.commit()
            self._send_json({"ok": True})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")


def main() -> None:
    global ACCESS_CODE
    init_db()
    ACCESS_CODE = load_access_code()
    try:
        backup_db()  # cópia ao iniciar
    except Exception as exc:
        print("backup inicial falhou:", type(exc).__name__)
    threading.Thread(target=_backup_loop, daemon=True).start()
    default_host = "0.0.0.0" if (os.environ.get("RENDER") or os.environ.get("PORT")) else "0.0.0.0"
    host = os.environ.get("HOST", default_host)
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), LattesHandler)
    if host not in ("127.0.0.1", "localhost", "::1"):
        print("Atenção: escutando fora do localhost. O acesso exige o código; use sempre HTTPS (LATTESFACIL_HTTPS=1).")
    print(f"LattesData rodando em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
