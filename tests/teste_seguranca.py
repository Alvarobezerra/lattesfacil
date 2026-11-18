"""Testes de segurança contra o servidor em execução (python server.py).

Uso:  python tests/teste_seguranca.py [http://127.0.0.1:8765]
Lê o código de acesso de .acesso (ou da variável LATTESFACIL_CODIGO).
"""

import os
import sys
import time
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
_PROC = None
_DB = None
if len(sys.argv) > 1:
    BASE = sys.argv[1].rstrip("/")
    CODIGO = os.environ.get("LATTESFACIL_CODIGO") or (RAIZ / ".acesso").read_text(encoding="utf-8").strip()
else:
    # Sem endereço: sobe um servidor próprio (porta de teste, banco temporário, bloqueio de login ligado). O teste de força bruta
    # termina bloqueando o IP; contra o servidor de uso diário isso trancaria o dono para fora.
    import atexit
    import subprocess
    BASE = "http://127.0.0.1:8802"
    CODIGO = "teste-codigo-123"
    _DB = RAIZ / "teste_seguranca.db"
    _PROC = subprocess.Popen([sys.executable, str(RAIZ / "server.py")], cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             env=dict(os.environ, PORT="8802", HOST="127.0.0.1", LATTESFACIL_CODIGO=CODIGO, LATTESFACIL_DB=str(_DB), LATTESFACIL_BLOQUEIO_LOCAL="1"))

    def _encerrar():
        _PROC.terminate()
        try:
            _PROC.wait(timeout=5)
        except Exception:
            _PROC.kill()
        for suf in ("", "-journal", "-wal", "-shm"):
            f = Path(str(_DB) + suf)
            if f.exists():
                try:
                    f.unlink()
                except OSError:
                    pass

    atexit.register(_encerrar)
    for _ in range(80):
        try:
            requests.get(BASE + "/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
HOST = BASE.split("//")[1]
falhas = []


def checa(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA"), nome, ("— " + str(detalhe)) if detalhe and not ok else "")
    if not ok:
        falhas.append(nome)


def nova_sessao():
    s = requests.Session()
    r = s.post(BASE + "/login", data={"codigo": CODIGO}, allow_redirects=False)
    return s, r


print("== 1. Sem login, nada é entregue")
anon = requests.Session()
for rota in ["/api/records", "/api/radar?autor=x", "/api/lattes/status?sid=abcdefgh12", "/exemplos/2024-SEMICresumo.pdf", "/app.js"]:
    r = anon.get(BASE + rota, allow_redirects=False)
    checa(f"GET {rota} bloqueado", r.status_code in (401, 303), r.status_code)
r = anon.post(BASE + "/api/records", json={"data": {"titulo": "x"}}, allow_redirects=False)
checa("POST /api/records bloqueado", r.status_code in (401, 303), r.status_code)
r = anon.delete(BASE + "/api/records/qualquer", allow_redirects=False)
checa("DELETE bloqueado", r.status_code in (401, 303), r.status_code)
r = anon.get(BASE + "/api/health")
checa("health público e mínimo", r.status_code == 200 and r.json() == {"ok": True}, r.text)
r = anon.get(BASE + "/api/lattes/ping?sid=abcdefgh12&online=1&name=x")
checa("ping do conector continua público (sem cookie)", r.status_code == 204, r.status_code)

print("== 2. Login")
s, r = nova_sessao()
cookie = r.headers.get("Set-Cookie", "")
checa("login correto redireciona", r.status_code == 303, r.status_code)
checa("cookie HttpOnly", "HttpOnly" in cookie)
checa("cookie SameSite=Strict", "SameSite=Strict" in cookie)
checa("página protegida abre com sessão", s.get(BASE + "/").status_code == 200)
checa("API abre com sessão", s.get(BASE + "/api/records").status_code == 200)

print("== 3. Cabeçalhos de segurança")
h = s.get(BASE + "/").headers
for k in ["X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Content-Security-Policy", "Cache-Control"]:
    checa(f"cabeçalho {k}", k in h)
checa("CSP bloqueia scripts externos", "script-src 'self'" in h.get("Content-Security-Policy", ""))
checa("sem CORS aberto", "Access-Control-Allow-Origin" not in h)
checa("versão do servidor não exposta", "Python" not in h.get("Server", ""), h.get("Server"))

print("== 4. CSRF: pedido vindo de outro site")
r = s.post(BASE + "/api/records", json={"data": {"titulo": "csrf"}}, headers={"Origin": "https://site-malicioso.example"})
checa("origem externa recusada", r.status_code == 403, r.status_code)
r = s.post(BASE + "/api/records", json={"owner": "teste-seguranca", "data": {"titulo": "TESTE SEGURANCA"}}, headers={"Origin": "http://" + HOST})
checa("mesma origem aceita", r.status_code == 200, r.status_code)
rec_id = r.json().get("id")

print("== 5. Exclusão lógica (dados recuperáveis)")
r = s.delete(BASE + f"/api/records/{rec_id}", headers={"Origin": "http://" + HOST})
checa("exclusão responde ok", r.status_code == 200)
ids = [x["id"] for x in s.get(BASE + "/api/records").json()["records"]]
checa("registro sumiu da lista", rec_id not in ids)
import sqlite3
con = sqlite3.connect(_DB if _PROC else RAIZ / "lattes_records.db")
linha = con.execute("select deleted_at from records where id=?", (rec_id,)).fetchone()
con.execute("delete from records where id=?", (rec_id,))  # limpa o registro de teste
con.commit()
con.close()
checa("registro continuava no banco (marcado como excluído)", linha is not None and linha[0] is not None, linha)

print("== 6. Envios ligados à sessão")
s2, _ = nova_sessao()
uid = "t" + str(int(time.time()))[-8:] + "zz"
r = s.post(BASE + f"/api/upload/chunk?id={uid}&i=0&n=1&name=a.pdf", data=b"%PDF-1.4 teste", headers={"Content-Type": "application/octet-stream", "Origin": "http://" + HOST})
checa("sessão A envia", r.status_code == 200, r.status_code)
r = s2.post(BASE + f"/api/upload/chunk?id={uid}&i=0&n=1&name=a.pdf", data=b"x", headers={"Content-Type": "application/octet-stream", "Origin": "http://" + HOST})
checa("sessão B não mexe no envio da A", r.status_code == 403, r.status_code)
r = s2.post(BASE + "/api/upload/finish", json={"id": uid}, headers={"Origin": "http://" + HOST})
checa("sessão B não finaliza o envio da A", r.status_code == 410, r.status_code)
r = s2.get(BASE + f"/api/dossie/download?id={uid}")
checa("sessão B não baixa o arquivo da A", r.status_code == 404, r.status_code)

print("== 7. Injeção no nome do arquivo baixado")
r = s.get(BASE + "/api/dossie/download?sample=1&nome=a%0d%0aX-Injetado:%201%0d%0a.pdf")
cd = r.headers.get("Content-Disposition", "")
checa("sem quebra de cabeçalho", "X-Injetado" not in r.headers and "\r" not in cd and "\n" not in cd, cd)

print("== 8. Travessia de diretório")
for rota in ["/..%2fserver.py", "/%2e%2e/server.py", "/exemplos/..%2f..%2fserver.py", "/static/../server.py", "/.acesso", "/lattes_records.db"]:
    r = s.get(BASE + rota, allow_redirects=False)
    checa(f"{rota} não entrega arquivos internos", r.status_code in (404, 400) or ("import hashlib" not in r.text and "SQLite" not in r.text[:20]), r.status_code)

print("== 9. Radar valida entrada")
r = s.get(BASE + "/api/radar?orcid=../../etc/passwd")
checa("ORCID inválido recusado", r.status_code == 400, r.status_code)

print("== 10. Força bruta no login (por último, pois bloqueia o IP)")
ruim = requests.Session()
codigos = []
for _ in range(7):
    codigos.append(ruim.post(BASE + "/login", data={"codigo": "errado-errado"}, allow_redirects=False).status_code)
checa("erros repetidos viram bloqueio (429)", 429 in codigos, codigos)
r = ruim.post(BASE + "/login", data={"codigo": CODIGO}, allow_redirects=False)
checa("mesmo com o código certo, o IP bloqueado espera", r.status_code == 429, r.status_code)

print("\nFALHAS:", falhas if falhas else "nenhuma")
sys.exit(1 if falhas else 0)
