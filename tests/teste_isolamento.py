"""Isolamento por dono e código de acesso em produção.

1. No Render, sem LATTESFACIL_CODIGO o servidor não pode usar um código padrão: tem que se recusar a subir.
2. Com LATTESFACIL_ISOLAR_OWNER=1, o "owner" vem da sessão: um usuário não lê, não grava em nome de outro
   nem altera/apaga registros e envios alheios, mesmo informando o owner dele na requisição.
Uso: python tests/teste_isolamento.py  (sobe o servidor numa porta local de teste)."""
import http.cookiejar
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

raiz = pathlib.Path(__file__).resolve().parent.parent
falhas = 0


def ok(cond, msg):
    global falhas
    print(("OK    " if cond else "FALHA ") + msg)
    if not cond:
        falhas += 1


# ---- 1. sem código padrão no Render
sys.path.insert(0, str(raiz))
os.environ.pop("LATTESFACIL_CODIGO", None)
os.environ["RENDER"] = "1"
import server  # noqa: E402

server.ACCESS_FILE = pathlib.Path(tempfile.gettempdir()) / "nao-existe-acesso-teste"
try:
    server.load_access_code()
    ok(False, "Render sem LATTESFACIL_CODIGO deve recusar subir")
except SystemExit:
    ok(True, "Render sem LATTESFACIL_CODIGO recusa subir (sem código padrão)")
os.environ["LATTESFACIL_CODIGO"] = "curto"
try:
    server.load_access_code()
    ok(False, "código curto deve ser recusado")
except SystemExit:
    ok(True, "código com menos de 10 caracteres é recusado")
os.environ.pop("RENDER")
os.environ.pop("LATTESFACIL_CODIGO")

# ---- 2. isolamento por dono
with socket.socket() as sk:
    sk.bind(("127.0.0.1", 0))
    PORT = str(sk.getsockname()[1])
BASE = f"http://127.0.0.1:{PORT}"
tmp = tempfile.mkdtemp()
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123",
           LATTESFACIL_DB=str(pathlib.Path(tmp) / "iso.db"), LATTESFACIL_ISOLAR_OWNER="1", LATTESFACIL_SKIP_WARMUP="1")
proc = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def sessao(usuario):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), SemRedirect)
    try:
        op.open(urllib.request.Request(f"{BASE}/login", data=f"codigo=teste-codigo-123&usuario={usuario}".encode()))
    except urllib.error.HTTPError:
        pass
    return op


def chamar(op, metodo, caminho, corpo=None):
    req = urllib.request.Request(BASE + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        r = op.open(req, timeout=30)
        return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}


try:
    for _ in range(120):
        try:
            urllib.request.urlopen(BASE + "/login", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    ana, bia = sessao("aramys"), sessao("alvaro")
    nome_a, nome_b = "Aramys Silva dos Reis", "Álvaro Antônio Bezerra dos Santos"

    # cada um grava dizendo ser o OUTRO: o servidor ignora o owner do cliente e usa o da sessão
    st, r = chamar(ana, "POST", "/api/records", {"id": "rec-ana", "owner": nome_b, "data": {"titulo": "Resumo da Ana"}})
    ok(st == 200, f"grava registro ({st})")
    st, r = chamar(bia, "POST", "/api/records", {"id": "rec-bia", "owner": nome_a, "data": {"titulo": "Resumo do Bia"}})
    lista_a = chamar(ana, "GET", "/api/records")[1].get("records", [])
    lista_b = chamar(bia, "GET", "/api/records")[1].get("records", [])
    ok([x["id"] for x in lista_a] == ["rec-ana"] and lista_a[0]["owner"] == nome_a, f"A só vê o próprio registro, com o owner da sessão ({[(x['id'], x['owner']) for x in lista_a]})")
    ok([x["id"] for x in lista_b] == ["rec-bia"], "B só vê o próprio registro")
    ok(chamar(bia, "GET", "/api/records?id=rec-ana")[1].get("records") == [], "B não lê o registro de A pelo id")

    # sobrescrever e apagar registro alheio
    st, _ = chamar(bia, "POST", "/api/records", {"id": "rec-ana", "data": {"titulo": "sequestrado"}})
    ok(st == 403, f"B não sobrescreve registro de A ({st})")
    st, _ = chamar(bia, "DELETE", "/api/records/rec-ana")
    ok(st == 403, f"B não apaga registro de A ({st})")
    ok(len(chamar(ana, "GET", "/api/records")[1]["records"]) == 1, "registro de A continua intacto")

    # envios ao Lattes: ?owner= do cliente não vale
    st, e = chamar(ana, "POST", "/api/lattes/envios", {"owner": nome_b, "titulo": "Livro da Ana", "tipo": "livro", "ano": "2020"})
    ok(st == 200, f"A registra envio ({st})")
    envio_id = e.get("id") or e.get("envio", {}).get("id")
    pelo_b = chamar(bia, "GET", f"/api/lattes/envios?owner={nome_a.replace(' ', '%20')}")[1].get("envios", [])
    ok(pelo_b == [], f"B não lista envios de A informando ?owner= ({len(pelo_b)})")
    pela_a = chamar(ana, "GET", "/api/lattes/envios")[1].get("envios", [])
    ok(len(pela_a) == 1 and pela_a[0]["owner"] == nome_a, "A lista o próprio envio, com o owner da sessão")
    if envio_id:
        st, _ = chamar(bia, "DELETE", f"/api/lattes/envios/{envio_id}")
        ok(st == 403, f"B não oculta envio de A ({st})")
    else:
        ok(False, "resposta do envio sem id")
finally:
    proc.terminate()

print(f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
