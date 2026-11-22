"""API de lote, XML, auditoria, duplicatas e EditalScore, de ponta a ponta (sobe o servidor numa porta de teste).
Uso: python tests/teste_api_novos.py"""
import http.cookiejar
import io
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile

raiz = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))
sys.path.insert(0, str(raiz / "tests"))
import pymupdf  # noqa: E402
from teste_novos_modulos import BAREMA, XML, pdf  # noqa: E402

PORT = "8796"
BASE = f"http://127.0.0.1:{PORT}"
DB = raiz / "teste_api_novos.db"
env = dict(os.environ, PORT=PORT, HOST="127.0.0.1", LATTESFACIL_CODIGO="teste-codigo-123", LATTESFACIL_DB=str(DB))
proc = subprocess.Popen([sys.executable, str(raiz / "server.py")], cwd=raiz, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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


def pedido(op, metodo, caminho, corpo=None, ctype="application/json"):
    req = urllib.request.Request(BASE + caminho, method=metodo, data=corpo, headers={"Content-Type": ctype} if corpo is not None else {})
    try:
        r = op.open(req, timeout=30)
        return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()


def json_(op, metodo, caminho, obj=None):
    st, _, raw = pedido(op, metodo, caminho, json.dumps(obj).encode() if obj is not None else None)
    try:
        return st, json.loads(raw or b"{}")
    except ValueError:
        return st, {}


def multipart(campos, arquivos):
    b = uuid.uuid4().hex
    partes = []
    for k, v in campos.items():
        partes.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for nome, dados in arquivos:
        partes.append(f'--{b}\r\nContent-Disposition: form-data; name="arquivo"; filename="{nome}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + dados + b"\r\n")
    partes.append(f"--{b}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={b}"


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
    a, outra = sessao(), sessao()

    for rota in ("/api/auditoria", "/api/lattes-xml"):
        ok(pedido(anon, "GET", rota)[0] == 401, f"{rota} exige sessão")
    ok(pedido(anon, "POST", "/api/lote", b"x", "multipart/form-data; boundary=x")[0] == 401, "lote exige sessão")

    ok(pedido(a, "GET", "/painel.html")[0] == 200 and pedido(a, "GET", "/painel.js")[0] == 200, "painel é servido")
    ok(json_(a, "GET", "/api/auditoria")[0] == 409, "auditoria sem XML orienta a carregar")
    ok(json_(a, "POST", "/api/duplicatas", {"titulo": "x"})[0] == 409, "duplicatas sem XML orienta a carregar")

    corpo, ct = multipart({}, [("cv.xml", XML.encode("iso-8859-1"))])
    st, _, raw = pedido(a, "POST", "/api/lattes-xml", corpo, ct)
    r = json.loads(raw)
    ok(st == 200 and r["carregado"] and r["por_categoria"]["artigo"] == 3, "XML carregado e resumido")
    ok(json_(outra, "GET", "/api/lattes-xml")[1].get("carregado") is False, "XML de uma sessão não vaza para outra")
    corpo, ct = multipart({}, [("cv.xml", b"<html/>")])
    ok(pedido(a, "POST", "/api/lattes-xml", corpo, ct)[0] == 400, "XML inválido é recusado")

    st, r = json_(a, "GET", "/api/auditoria")
    ok(st == 200 and r["resumo"]["Gravíssimo"] >= 1 and r["total"] > 3, "auditoria devolve pendências por risco")
    st, r = json_(a, "POST", "/api/duplicatas", {"titulo": "Probiotic beverages from babassu", "ano": "2022"})
    ok(st == 200 and r["duplicatas"], "duplicata encontrada")

    zbytes = io.BytesIO()
    with zipfile.ZipFile(zbytes, "w") as z:
        z.writestr("cert.pdf", pdf("Declaração de licença-maternidade de 01 de março de 2024 a 28 de agosto de 2024 concedida a servidora"))
    corpo, ct = multipart({"usuario": "Maria Souza"}, [("lote.zip", zbytes.getvalue()), ("outro.pdf", pdf("Probiotic beverages from babassu 10.1016/j.jff.2022.001"))])
    st, _, raw = pedido(a, "POST", "/api/lote", corpo, ct)
    r = json.loads(raw)
    ok(st == 200 and r["total"] == 2, f"lote processa ZIP + PDF avulso ({r.get('por_status')})")
    corpo, ct = multipart({"usuario": "Maria Souza", "saida": "zip"}, [("lote.zip", zbytes.getvalue())])
    st, tipo, raw = pedido(a, "POST", "/api/lote", corpo, ct)
    ok(st == 200 and tipo == "application/zip" and zipfile.ZipFile(io.BytesIO(raw)).testzip() is None, "lote devolve ZIP organizado")

    st, bar = json_(a, "POST", "/api/edital/barema", {"texto": BAREMA, "nome": "Edital 12/2026"})
    ok(st == 200 and bar["teto_global"] == 50, "barema lido do texto do edital")
    st, calc = json_(a, "POST", "/api/edital/calcular", {"barema": bar, "ano": 2026})
    ok(st == 200 and calc["total"] > 0 and "lacunas" in calc, f"pontuação calculada ({calc.get('total')})")
    st, sim = json_(a, "POST", "/api/edital/simular", {"barema": bar, "ano": 2026, "extras": [{"categoria": "livro"}]})
    ok(st == 200 and sim["depois"] >= sim["antes"], "simulação 'e se'")
    ok(json_(outra, "POST", "/api/edital/calcular", {"barema": bar})[0] == 409, "cálculo sem XML na sessão é recusado")
    ok(json_(a, "POST", "/api/edital/calcular", {"barema": {"blocos": "x"}})[0] == 400, "barema inválido é recusado")

    # histórico de versões, dashboard, comparação e conciliação de envios
    ok(pedido(anon, "GET", "/api/curriculo/snapshots")[0] == 401, "histórico exige sessão")
    ok(json_(outra, "GET", "/api/curriculo/dashboard")[0] == 409, "dashboard sem XML orienta a carregar")
    st, r = json_(a, "GET", "/api/curriculo/snapshots")
    ok(st == 200 and len(r["snapshots"]) == 1, "XML carregado virou uma versão guardada")
    sid1 = r["snapshots"][0]["id"]
    corpo, ct = multipart({}, [("cv.xml", XML.encode("iso-8859-1"))])
    st, _, raw = pedido(a, "POST", "/api/lattes-xml", corpo, ct)
    ok(json.loads(raw)["novo_snapshot"] is False, "reenviar o mesmo XML não cria versão")
    st, d = json_(a, "GET", "/api/curriculo/dashboard")
    ok(st == 200 and d["artigos"]["total"] == 3 and d["snapshot_id"] == sid1, "dashboard da sessão")
    st, _, raw = pedido(a, "POST", "/api/lattes-xml", *multipart({}, [("cv2.xml", XML.encode("iso-8859-1").replace(b"Livro de testes", b"Livro novo"))]))
    r2 = json.loads(raw)
    ok(r2["novo_snapshot"] and r2["comparacao"] == {"de": sid1, "adicionados": 1, "removidos": 1}, f"segunda versão compara com a primeira ({r2.get('comparacao')})")
    st, c = json_(a, "GET", "/api/curriculo/comparar")
    ok(st == 200 and c["adicionados"][0]["titulo"] == "Livro novo", "endpoint de comparação")
    ok(json_(a, "POST", "/api/curriculo/ativar", {"snapshot": sid1})[0] == 200 and json_(a, "GET", "/api/curriculo")[1]["snapshot_id"] == sid1, "reabrir versão antiga na sessão")
    ok(json_(a, "GET", "/api/curriculo?snapshot=../../x")[0] == 409 and json_(a, "POST", "/api/curriculo/ativar", {"snapshot": "zz"})[0] == 404, "id de versão inválido é recusado")
    st, e = json_(a, "POST", "/api/lattes/envios", {"owner": "Joao da Silva", "titulo": "Livro novo", "tipo": "livro", "ano": "2020"})
    json_(a, "POST", "/api/lattes/envios/" + e["id"], {"status": "salvo"})
    st, _, raw = pedido(a, "POST", "/api/lattes-xml", *multipart({}, [("cv3.xml", XML.encode("iso-8859-1").replace(b"Livro de testes", b"Livro novo").replace(b'DATA-ATUALIZACAO="01012026"', b'DATA-ATUALIZACAO="01012099"'))]))
    ok(json.loads(raw)["envios_conciliados"] == {"confirmado": 1}, f"envio confirmado pelo XML ({json.loads(raw).get('envios_conciliados')})")
    envios = json_(a, "GET", "/api/lattes/envios?owner=Joao%20da%20Silva")[1]["envios"]
    ok(envios and envios[0]["xml_status"] == "confirmado", "lista de envios traz o status do XML")
    st, rotina = json_(a, "GET", "/api/rotina?usuario=Joao%20da%20Silva")
    ok(st == 200 and rotina["envios_confirmados"] == 1 and rotina["atividade"][0]["titulo"] == "Livro novo", "rotina mostra o envio realmente confirmado")
    st, rotina = json_(a, "GET", "/api/rotina?usuario=Outro%20Pesquisador")
    ok(st == 200 and rotina["envios_confirmados"] == 0 and not rotina["atividade"], "rotina filtra pelo pesquisador selecionado")
    st, tipo, video = pedido(a, "GET", "/media/boas-vindas.mp4")
    ok(st == 200 and tipo.startswith("video/mp4") and b"ftyp" in video[:16], "animação de boas-vindas é servida como MP4")
    ok(pedido(anon, "DELETE", "/api/curriculo/snapshots/" + sid1)[0] == 401, "apagar versão exige sessão")
    ok(pedido(a, "DELETE", "/api/curriculo/snapshots/" + sid1)[0] == 200 and len(json_(a, "GET", "/api/curriculo/snapshots")[1]["snapshots"]) == 2, "versão apagada")
    ok(pedido(a, "GET", "/meu-curriculo.html")[0] == 200 and pedido(a, "GET", "/meu-curriculo.js")[0] == 200, "página Meu currículo é servida")

    # leitura em tempo real (página para impressão do Lattes, buscada pela extensão)
    pag = ('<html><body>Última atualização do currículo em 17/11/2026 lattes.cnpq.br/1234567890123456<div class="conteudo-cv">'
           '<a name="Participacaoemeventos"></a><div class="agrupadorsub">Participação em eventos</div>'
           '<table class="IndicProdTabela"><tr><td class="ano">1.</td><td class="texto">Congresso Y, 2019. (Congresso) .</td></tr></table></div></body></html>')
    ok(pedido(anon, "POST", "/api/curriculo/pagina", b"{}", "application/json")[0] == 401, "leitura ao vivo exige sessão")
    ok(json_(a, "POST", "/api/curriculo/pagina", {"html": "<html>nada</html>"})[0] == 400, "HTML que não é a página do Lattes é recusado")
    st, r = json_(a, "POST", "/api/curriculo/pagina", {"html": pag, "nome": "Joao da Silva"})
    ok(st == 200 and r["fonte"] == "pagina" and r["novo_snapshot"] and r["por_categoria"] == {"participacao_evento": 1}, f"página interpretada e guardada ({r.get('por_categoria')})")
    st, r2 = json_(a, "POST", "/api/curriculo/pagina", {"html": pag + "<!-- ruído -->", "nome": "Joao da Silva"})
    ok(st == 200 and r2["novo_snapshot"] is False, "mesmo conteúdo (HTML diferente) não cria outra versão")
    fontes = {s["fonte"] for s in json_(a, "GET", "/api/curriculo/snapshots")[1]["snapshots"]}
    ok(fontes == {"xml", "pagina"}, f"versões guardam a fonte ({fontes})")
    ok(json_(a, "GET", "/api/curriculo/dashboard")[1]["fonte"] == "pagina", "dashboard informa a fonte")

    mapa = json.dumps({"a.pdf": {"item": "1.1", "descricao": "Artigo"}, "b.pdf": {"item": "1.2", "descricao": "Livro"}})
    corpo, ct = multipart({"candidato": "João", "edital": "12/2026", "itens": mapa}, [("a.pdf", pdf("A")), ("b.pdf", pdf("B"))])
    st, tipo, raw = pedido(a, "POST", "/api/edital/dossie", corpo, ct)
    ok(st == 200 and tipo == "application/pdf" and len(pymupdf.open(stream=raw, filetype="pdf")) == 4, "dossiê PDF gerado")
finally:
    proc.terminate()
    proc.wait(5)
    for suf in ("", "-wal", "-shm"):
        try:
            pathlib.Path(str(DB) + suf).unlink()
        except OSError:
            pass

print("\nTodos os testes passaram" if not falhas else f"\n{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
