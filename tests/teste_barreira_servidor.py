"""Barreira contra servidor duplicado e desatualizado: segunda instância na mesma porta recusa iniciar, e a rota
/api/servidor/estado avisa quando um arquivo de código muda depois que o servidor iniciou.
Uso: python tests/teste_barreira_servidor.py"""
import http.cookiejar
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

raiz = pathlib.Path(__file__).resolve().parent.parent
PORT = "8799"
BASE = f"http://127.0.0.1:{PORT}"
DB = raiz / "teste_barreira.db"
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123", LATTESFACIL_DB=str(DB))
falhas = 0


def checa(nome, cond, extra=""):
    global falhas
    print(("OK   " if cond else "FALHA ") + nome + (f" — {extra}" if extra and not cond else ""))
    falhas += 0 if cond else 1


class SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def estado(op):
    with op.open(BASE + "/api/servidor/estado", timeout=10) as r:
        return json.loads(r.read())["desatualizado"]


alvo = raiz / "itens" / "especificacao" / "banca.json"
tempos = (alvo.stat().st_atime_ns, alvo.stat().st_mtime_ns)
primeiro = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(80):
        try:
            urllib.request.urlopen(BASE + "/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    segundo = subprocess.run([sys.executable, str(raiz / "server.py")], cwd=raiz, env=dict(env, PYTHONIOENCODING="utf-8"), capture_output=True, text=True, encoding="utf-8", timeout=60)
    checa("segunda instância na mesma porta recusa iniciar (código 1)", segundo.returncode == 1, (segundo.returncode, segundo.stderr[-200:]))
    checa("a mensagem explica o motivo", "Já existe um servidor" in segundo.stdout, segundo.stdout[-200:])
    checa("o primeiro servidor segue respondendo", urllib.request.urlopen(BASE + "/api/health", timeout=5).status == 200)

    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), SemRedirect)
    try:
        op.open(urllib.request.Request(f"{BASE}/login", data=b"codigo=teste-codigo-123"))
    except urllib.error.HTTPError:
        pass
    checa("recém-iniciado: não está desatualizado", estado(op) is False)
    agora = time.time_ns() + 5_000_000_000
    os.utime(alvo, ns=(agora, agora))  # simula edição de um arquivo de código
    time.sleep(3.3)  # a checagem é cacheada por 3 s
    checa("arquivo de código mudou: servidor se declara desatualizado", estado(op) is True)
    anon = urllib.request.build_opener(SemRedirect)
    try:
        cod = anon.open(BASE + "/api/servidor/estado", timeout=10).status
    except urllib.error.HTTPError as e:
        cod = e.code
    checa("a rota de estado exige sessão", cod == 401, cod)
    checa("health público segue mínimo", json.loads(urllib.request.urlopen(BASE + "/api/health", timeout=5).read()) == {"ok": True})
finally:
    os.utime(alvo, ns=tempos)  # devolve a data original do arquivo
    primeiro.terminate()
    try:
        primeiro.wait(timeout=5)
    except Exception:
        primeiro.kill()
    for suf in ("", "-journal", "-wal", "-shm"):
        f = pathlib.Path(str(DB) + suf)
        if f.exists():
            try:
                f.unlink()
            except OSError:
                pass

print(f"{falhas} falha(s)")
sys.exit(1 if falhas else 0)
