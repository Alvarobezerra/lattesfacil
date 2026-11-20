"""Receptor local das capturas do formulário real do Lattes (ferramenta de desenvolvimento, fase 1 da metodologia).

O script ferramentas/auditoria_lattes.js, rodando no formulário aberto no Chrome, envia o resultado (JSON) para cá.
Grava em docs/campos-lattes/ref/<item>/<variante>.json. Só aceita conexões locais e nomes de arquivo simples.
Uso:  python ferramentas/receptor_captura.py   (porta 8798; encerre com Ctrl+C quando terminar a captura)
"""
import json
import pathlib
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "docs" / "campos-lattes" / "ref"
PORTA = 8798
SLUG = re.compile(r"^[a-z0-9_]{1,60}$")


class Receptor(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # Transporte alternativo (a página do Lattes bloqueia fetch/POST): o script manda a captura em partes como pedidos de
    # imagem  GET /p?k=<chave>&i=<n>&t=<total>&d=<trecho já codificado>  e o receptor remonta e grava quando chegam todas.
    PARTES = {}

    # Arquivos servidos só para teste (preenchimento real no formulário aberto do Lattes): lista fechada.
    ARQUIVOS = {
        "/autofill_core.js": RAIZ / "extensao" / "autofill_core.js",
        "/executor_preenchimento.js": RAIZ / "ferramentas" / "executor_preenchimento.js",
        "/casos_projeto.js": RAIZ / "ferramentas" / "saida" / "casos_projeto.js",
        "/auditoria_lattes.js": RAIZ / "ferramentas" / "auditoria_lattes.js",
        "/payload_artigo.js": RAIZ / "ferramentas" / "saida" / "payload_artigo.js",
        "/casos_artigo.js": RAIZ / "ferramentas" / "saida" / "casos_artigo.js",
    }

    def do_GET(self):
        caminho = self.path.split("?")[0]
        ms = re.match(r"^/saida/([a-z0-9_]+\.js)$", caminho)  # cargas e casos gerados (ferramentas/saida/*.js)
        arq = (RAIZ / "ferramentas" / "saida" / ms.group(1)) if ms else Receptor.ARQUIVOS.get(caminho)
        if arq is not None and arq.is_file():
            corpo = arq.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self._cors()
            self.end_headers()
            self.wfile.write(corpo)
            return
        m = re.match(r"^/p\?k=([a-z0-9]{4,20})&i=(\d{1,4})&t=(\d{1,4})&d=([A-Za-z0-9%._~!'()*\-]*)$", self.path)
        gif = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        if m:
            chave, i, t, trecho = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
            partes = Receptor.PARTES.setdefault(chave, {})
            partes[i] = trecho
            if len(partes) == t and t <= 400:
                try:
                    from urllib.parse import unquote
                    dados = json.loads(unquote("".join(partes[k] for k in range(t))))
                    item, variante = str(dados.get("item", "")), str(dados.get("variante_slug", ""))
                    if SLUG.match(item) and SLUG.match(variante):
                        destino = SAIDA / item
                        destino.mkdir(parents=True, exist_ok=True)
                        (destino / f"{variante}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
                        print(f"gravado {item}/{variante}.json ({len(dados.get('campos', []))} campos)", flush=True)
                except Exception as e:  # noqa: BLE001
                    print("erro ao remontar:", e, flush=True)
                Receptor.PARTES.pop(chave, None)
        self.send_response(200)
        self.send_header("Content-Type", "image/gif")
        self.send_header("Content-Length", str(len(gif)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(gif)

    def do_POST(self):
        try:
            tam = int(self.headers.get("Content-Length", "0"))
            if tam <= 0 or tam > 5_000_000:
                raise ValueError("tamanho inválido")
            dados = json.loads(self.rfile.read(tam).decode("utf-8"))
            item, variante = str(dados.get("item", "")), str(dados.get("variante_slug", ""))
            if not SLUG.match(item) or not SLUG.match(variante):
                raise ValueError("item/variante inválidos")
            destino = SAIDA / item
            destino.mkdir(parents=True, exist_ok=True)
            (destino / f"{variante}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
            corpo = json.dumps({"ok": True, "arquivo": f"{item}/{variante}.json", "campos": len(dados.get("campos", []))}).encode()
            self.send_response(200)
        except Exception as e:  # noqa: BLE001 - ferramenta local, devolve o motivo
            corpo = json.dumps({"ok": False, "erro": str(e)}).encode()
            self.send_response(400)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *a):  # silencioso
        pass


if __name__ == "__main__":
    print(f"Receptor de capturas em http://127.0.0.1:{PORTA} -> {SAIDA}".encode("ascii", "replace").decode())
    try:
        ThreadingHTTPServer(("127.0.0.1", PORTA), Receptor).serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
