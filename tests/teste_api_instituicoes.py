"""API do banco de instituições e do gerenciador da captação, de ponta a ponta (sobe o servidor numa porta de teste).
Uso: python tests/teste_api_instituicoes.py"""
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
PORT = "8797"
BASE = f"http://127.0.0.1:{PORT}"
DB = raiz / "teste_api_instituicoes.db"
if DB.exists():
    DB.unlink()
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123", LATTESFACIL_DB=str(DB))
proc = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
falhas = 0


class SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def checa(nome, cond, extra=""):
    global falhas
    print(("OK   " if cond else "FALHA ") + nome + (f" — {extra}" if extra and not cond else ""))
    falhas += 0 if cond else 1


def pedido(op, metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, method=metodo, data=dados, headers={"Content-Type": "application/json", "Origin": BASE} if dados is not None else {})
    try:
        with op.open(req, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


try:
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE + "/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    anon = urllib.request.build_opener(SemRedirect)
    checa("sem sessão: API do gerenciador exige login", pedido(anon, "GET", "/api/instituicoes/gerenciador")[0] == 401)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), SemRedirect)
    try:
        op.open(urllib.request.Request(f"{BASE}/login", data=b"codigo=teste-codigo-123"))
    except urllib.error.HTTPError:
        pass

    st, b = pedido(op, "GET", "/api/instituicoes/gerenciador")
    g = json.loads(b)
    checa("gerenciador: coleta nasce desligada e com os 6 prefixos", st == 200 and g["config"]["ativa"] == 0 and [p["termo"] for p in g["prefixos"]][:2] == ["Universidade", "Instituto"] and len(g["prefixos"]) == 6, g.get("config"))

    st, b = pedido(op, "GET", "/api/instituicoes/buscar?q=UFC")
    r = json.loads(b)
    checa("busca local por sigla (semente)", r["candidatas"] and r["candidatas"][0]["nome"] == "Universidade Federal do Ceará", r)

    lote = {"lote_id": "api-teste-1", "termo": "Universidade", "origem": "coleta", "ms": 1500, "itens": [{"nome": f"Universidade Federal de Teste {i} (CE)", "ref": f"'{1000 + i}',1"} for i in range(12)]}
    st, b = pedido(op, "POST", "/api/instituicoes/registrar", lote)
    checa("registrar grava candidatas da lupa", st == 200 and json.loads(b)["novas"] == 12, b)
    st, b = pedido(op, "POST", "/api/instituicoes/registrar", lote)
    checa("mesmo lote_id (outra aba) não grava de novo", json.loads(b).get("duplicado") == 1, b)
    st, b = pedido(op, "GET", "/api/instituicoes/buscar?q=Universidade+Federal+de+Teste+3")
    checa("busca local acha o que a lupa devolveu, com código", json.loads(b)["candidatas"][0]["codigo"] == "1003", b)

    st, b = pedido(op, "POST", "/api/instituicoes/config", {"ativa": 1, "limite_dia": 5, "limite_lote": 3, "intervalo_ms": 100})
    c = json.loads(b)["config"]
    checa("config limitada aos tetos", st == 200 and c["ativa"] == 1 and c["intervalo_ms"] == 2000 and c["limite_dia"] == 5, c)
    lt = json.loads(pedido(op, "GET", "/api/instituicoes/proximo-lote")[1])
    checa("próximo lote: 3 termos, a partir dos prefixos prioritários ainda pendentes", lt["termos"] == ["Instituto", "Faculdade", "Hospital"] and lt["restante_hoje"] == 4, lt)

    iid = json.loads(pedido(op, "GET", "/api/instituicoes/buscar?q=Universidade+Federal+de+Teste+3")[1])["candidatas"][0]["id"]
    checa("confirmar texto→instituição", json.loads(pedido(op, "POST", "/api/instituicoes/confirmar", {"texto": "UF Teste três", "id": iid, "usuario": "ana"})[1])["ok"])
    checa("busca pelo texto confirmado", json.loads(pedido(op, "GET", "/api/instituicoes/buscar?q=uf+teste+tres")[1])["confirmada"])
    checa("ação desconhecida: 404", pedido(op, "POST", "/api/instituicoes/xpto", {})[0] == 404)
    imp = json.loads(pedido(op, "POST", "/api/instituicoes/importar", {"csv": "Nome;Sigla\nUniversidade Teste Aberta;UTA\n"})[1])
    checa("importar semente", imp["novas"] == 1, imp)
    checa("página do gerenciador é servida", pedido(op, "GET", "/captacao.html")[0] == 200 and "Captação".encode("utf-8") in pedido(op, "GET", "/captacao.html")[1])
    req = urllib.request.Request(BASE + "/api/instituicoes/config", method="POST", data=b'{"ativa": 1}', headers={"Content-Type": "application/json", "Origin": "http://evil.test"})
    try:
        cod = op.open(req, timeout=10).status
    except urllib.error.HTTPError as e:
        cod = e.code
    checa("origem estranha não altera a configuração (403)", cod == 403, cod)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    for suf in ("", "-journal", "-wal", "-shm"):
        f = pathlib.Path(str(DB) + suf)
        if f.exists():
            try:
                f.unlink()
            except OSError:
                pass

print(f"{falhas} falha(s)")
sys.exit(1 if falhas else 0)
