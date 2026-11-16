"""Registro de envios ao Lattes (/api/lattes/envios): criar, listar, atualizar, ocultar e validar entradas.
Uso: python tests/teste_envios.py  (sobe o servidor numa porta local de teste)."""
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
PORT = "8795"
BASE = f"http://127.0.0.1:{PORT}"
DB = raiz / "teste_envios.db"
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123", LATTESFACIL_DB=str(DB))
proc = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def sessao():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), SemRedirect)
    try:
        op.open(urllib.request.Request(f"{BASE}/login", data=b"codigo=teste-codigo-123"))
    except urllib.error.HTTPError:
        pass
    return op


def chamar(op, metodo, caminho, corpo=None):
    req = urllib.request.Request(BASE + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        r = op.open(req, timeout=5)
        return r.status, json.loads(r.read() or b"{}")
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
    anon = urllib.request.build_opener(SemRedirect)
    a = sessao()

    ok(chamar(anon, "GET", "/api/lattes/envios")[0] == 401, "listar exige sessão")
    ok(chamar(anon, "POST", "/api/lattes/envios", {"titulo": "x"})[0] == 401, "criar exige sessão")

    st, r = chamar(a, "POST", "/api/lattes/envios", {"owner": "Álvaro", "titulo": "Artigo de teste", "tipo": "apresentacao", "ano": "2024x"})
    eid = r.get("id", "")
    ok(st == 200 and len(eid) == 12, "cria o envio com id")

    st, r = chamar(a, "GET", "/api/lattes/envios?owner=%C3%81lvaro")
    e = (r.get("envios") or [{}])[0]
    ok(e.get("id") == eid and e.get("status") == "enviando" and e.get("ano") == "2024" and e.get("tipo") == "apresentacao", "lista o envio (status enviando, ano limpo)")
    ok(chamar(a, "GET", "/api/lattes/envios?owner=Outro")[1].get("envios") == [], "filtra por usuário")

    ok(chamar(a, "POST", f"/api/lattes/envios/{eid}", {"status": "hackeado"})[0] == 400, "recusa status inválido")
    ok(chamar(a, "POST", "/api/lattes/envios/../etc", {"status": "salvo"})[0] in (400, 404), "recusa id inválido")
    ok(chamar(a, "POST", "/api/lattes/envios/aaaaaaaaaaaa", {"status": "salvo"})[0] == 404, "id inexistente dá 404")

    st, r = chamar(a, "POST", f"/api/lattes/envios/{eid}", {"status": "salvo", "mensagem": "ok", "lattes_seq": "69; DROP"})
    e = chamar(a, "GET", "/api/lattes/envios")[1]["envios"][0]
    ok(st == 200 and e["status"] == "salvo" and e["lattes_seq"] == "69", "atualiza status e guarda só dígitos do seq")

    chamar(a, "POST", f"/api/lattes/envios/{eid}", {"status": "removido", "mensagem": "removido"})
    e = chamar(a, "GET", "/api/lattes/envios")[1]["envios"][0]
    ok(e["status"] == "removido" and e["removido_em"] and e["lattes_seq"] == "69", "remoção registra data e mantém o seq")

    ok(chamar(a, "DELETE", f"/api/lattes/envios/{eid}")[0] == 200, "oculta da lista")
    ok(chamar(a, "GET", "/api/lattes/envios")[1]["envios"] == [], "item oculto some da lista")
finally:
    proc.terminate()
    try:
        proc.wait(5)
    except Exception:
        proc.kill()
    for suf in ("", "-wal", "-shm"):
        try:
            (raiz / f"teste_envios.db{suf}").unlink()
        except OSError:
            pass

if falhas:
    print(f"\n{len(falhas)} falha(s)")
    sys.exit(1)
print("\nTodos os testes passaram")
