"""Isolamento da fila de jobs do agente: cada sessão só enxerga/consome os próprios jobs.
Uso: python tests/teste_agente_jobs.py  (sobe o servidor numa porta local de teste)."""
import json, os, subprocess, sys, time, urllib.request, urllib.parse, http.cookiejar, pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
PORT = "8791"
BASE = f"http://127.0.0.1:{PORT}"
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123")
proc = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def sessao():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), NoRedirect)
    try:
        op.open(urllib.request.Request(f"{BASE}/login", data=b"codigo=teste-codigo-123"))
    except urllib.error.HTTPError:
        pass  # 303 esperado; o cookie já foi gravado
    return op


def chamar(op, caminho, corpo=None, token=""):
    h = {"Content-Type": "application/json"}
    if token:
        h["X-LD-Token"] = token
    req = urllib.request.Request(BASE + caminho, data=json.dumps(corpo).encode() if corpo is not None else None, headers=h)
    try:
        r = op.open(req, timeout=5)
        corpo = r.read()
        try:
            return r.status, json.loads(corpo or b"{}")
        except ValueError:
            return r.status, {}  # corpo não-JSON (ex.: download do agente)
    except urllib.error.HTTPError as e:
        return e.code, {}


falhas = []
def ok(cond, msg):
    print(("OK   " if cond else "FALHA ") + msg)
    if not cond:
        falhas.append(msg)

try:
    for _ in range(40):
        try:
            urllib.request.urlopen(BASE + "/login", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    anon = urllib.request.build_opener(NoRedirect)
    a, b = sessao(), sessao()
    tok_a = chamar(a, "/api/lattes/pair")[1].get("token", "")
    tok_b = chamar(b, "/api/lattes/pair")[1].get("token", "")
    ok(tok_a and tok_b and tok_a != tok_b, "cada instalação recebe um token próprio")
    ok(chamar(anon, "/api/lattes/pair")[0] == 401, "emitir token exige sessão")

    st, j = chamar(a, "/api/lattes/job", {"titulo": "Artigo do A"})
    jid_a = j.get("job_id", "")
    ok(st == 200 and jid_a, "sessão A cria job")

    ok(chamar(anon, "/api/lattes/job?next=1")[0] == 401, "anônimo sem token não lê a fila (401)")
    ok(chamar(anon, "/api/lattes/job?next=1", token="invalido")[0] == 401, "token inválido é recusado (401)")
    ok(chamar(anon, f"/api/lattes/job?id={jid_a}")[0] == 401, "anônimo não busca job por id (401)")
    forjado = tok_a.rsplit(".", 1)[0] + "." + "0" * 32
    ok(chamar(anon, "/api/lattes/job?next=1", token=forjado)[0] == 401, "assinatura adulterada é recusada")
    expirado = "aaaaaaaaaaaa.1000000000." + "0" * 32
    ok(chamar(anon, "/api/lattes/job?next=1", token=expirado)[0] == 401, "token expirado/forjado é recusado")
    ok(chamar(anon, "/api/ativar?file=ps1&t=" + tok_a)[0] == 401, "token na URL não autentica o /api/ativar")
    ok(chamar(anon, "/api/ativar?file=ps1", token=tok_a)[0] == 200, "token por cabeçalho baixa o agente")

    # Um navegador (cookie) só enxerga os jobs da PRÓPRIA sessão
    ok(chamar(b, f"/api/lattes/job?id={jid_a}")[0] == 404, "sessão B não busca o job da sessão A (404)")
    ok(chamar(a, f"/api/lattes/job?check={jid_a}")[1].get("consumed") is False, "check: ainda não consumido")

    st, r = chamar(anon, "/api/lattes/job?next=1", token=tok_b)
    ok(r.get("ok") and r.get("data", {}).get("titulo") == "Artigo do A", "agente instalado recebe o job da fila")
    ok(chamar(a, f"/api/lattes/job?check={jid_a}")[1].get("consumed") is True, "check: consumido após entrega")
    ok(not chamar(anon, "/api/lattes/job?next=1", token=tok_a)[1].get("ok"), "job é de uso único")
    ok(chamar(anon, "/api/lattes/job?check=inexistente00")[0] == 401, "check exige autenticação")
finally:
    proc.terminate()

if falhas:
    print(f"\n{len(falhas)} falha(s)")
    sys.exit(1)
print("\nTodos os testes passaram")
