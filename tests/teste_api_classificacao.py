"""Testa a API de classificação contra o servidor em execução (login com o código de .acesso).

Uso:  python tests/teste_api_classificacao.py [http://127.0.0.1:8765]
"""

import math
import os
import sys
import time
from pathlib import Path

import requests

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765").rstrip("/")
RAIZ = Path(__file__).resolve().parent.parent
CODIGO = os.environ.get("LATTESFACIL_CODIGO") or (RAIZ / ".acesso").read_text(encoding="utf-8").strip()
DOWNLOADS = Path.home() / "Downloads"
ORIGEM = {"Origin": BASE}
falhas = []

s = requests.Session()
r = s.post(BASE + "/login", data={"codigo": CODIGO}, allow_redirects=False)
assert r.status_code == 303, "login falhou"


def checa(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA"), nome, ("— " + str(detalhe)) if detalhe and not ok else "")
    if not ok:
        falhas.append(nome)


def enviar(caminho: Path, usuario="Aramys Silva dos Reis"):
    dados = caminho.read_bytes()
    uid = "t" + str(int(time.time() * 1000))[-10:] + "ab"
    n = max(1, math.ceil(len(dados) / (1024 * 1024)))
    for i in range(n):
        s.post(f"{BASE}/api/upload/chunk?id={uid}&i={i}&n={n}&name={caminho.name}", data=dados[i * 1048576:(i + 1) * 1048576],
               headers={"Content-Type": "application/octet-stream", **ORIGEM})
    r = s.post(BASE + "/api/upload/finish", json={"id": uid, "usuario": usuario}, headers=ORIGEM)
    return uid, r.json()


print("== catálogo")
itens = s.get(BASE + "/api/itens").json()["itens"]
checa("catálogo com os itens reconhecíveis", len(itens) >= 20 and all("grupo" in i for i in itens), len(itens))
checa("itens implementados marcados", sum(i["implementado"] for i in itens) >= 3)

print("== certificado COIMAMA")
uid, j = enviar(DOWNLOADS / "Certificado COIMAMA 2024.pdf")
c = j["classificacao"]
checa("avança sozinho", c["decisao"] == "avancar", c["decisao"])
checa("reconhece Apresentação de trabalho", c["candidatos"][0]["id"] == "apresentacao")
checa("traz o motivo em português", bool(c["candidatos"][0]["motivos"]))
checa("já devolve os campos extraídos", j.get("extracted", {}).get("tipo_producao") == "apresentacao")
checa("texto bruto do arquivo NÃO volta no campo interno", "_leitura" not in j)
r = s.post(BASE + "/api/classificacao/interpretar", json={"id": uid, "item": "livro_capitulo"}, headers=ORIGEM).json()
checa("interpreta livro_capitulo pelo formulário do spec", r.get("implementado") is True and "extracted" in r, r)
r = s.post(BASE + "/api/classificacao/interpretar", json={"id": uid, "item": "anais"}, headers=ORIGEM).json()
checa("interpreta o mesmo arquivo como outro item (anais)", r.get("implementado") is True and "extracted" in r)

print("== resumo SEMIC")
uid, j = enviar(RAIZ / "exemplos" / "2024-SEMICresumo.pdf")
checa("resumo vira Trabalhos em anais", j["classificacao"]["candidatos"][0]["id"] == "anais" and j["classificacao"]["decisao"] == "avancar", j["classificacao"]["decisao"])

print("== arquivo sem texto (imagem)")
if (DOWNLOADS / "avaliação.pdf").exists():
    uid, j = enviar(DOWNLOADS / "avaliação.pdf")
    checa("pede escolha guiada", j["classificacao"]["decisao"] == "escolher" and "extracted" not in j, j["classificacao"]["decisao"])
    checa("explica o motivo", "texto" in j["classificacao"]["motivo_decisao"])

print("== caderno grande")
cad = RAIZ / "exemplos" / "bbr.ptm.23.384_FeSBE2026.pdf"
if cad.exists():
    uid, j = enviar(cad)
    checa("caderno segue para a busca por autor", j.get("caderno") is True)

print("== texto colado")
j = s.post(BASE + "/api/extract", json={"text": "10.1371/journal.pmed.0020124", "usuario": "Aramys Silva dos Reis"}, headers=ORIGEM).json()
checa("DOI vira artigo", j["classificacao"]["candidatos"][0]["id"] == "artigo" and j.get("extracted", {}).get("tipo_producao") == "artigo")
j = s.post(BASE + "/api/extract", json={"text": "Lista de compras: arroz, feijão, macarrão, sabão em pó e detergente. Comprar na sexta."}, headers=ORIGEM).json()
checa("texto sem relação vai para o escolhedor", j["classificacao"]["decisao"] == "escolher" and "extracted" not in j)

print("== feedback de correção (só ids, nunca o documento)")
r = s.post(BASE + "/api/classificacao/feedback", json={"sugerido": "apresentacao", "escolhido": "participacao_evento", "decisao": "avancar", "confianca": 0.95}, headers=ORIGEM)
checa("correção registrada", r.status_code == 200, r.text)
r = s.post(BASE + "/api/classificacao/feedback", json={"sugerido": "x'; DROP TABLE records;--", "escolhido": "anais"}, headers=ORIGEM)
checa("entrada maliciosa recusada", r.status_code == 400, r.status_code)

print("== segurança das rotas novas")
anon = requests.Session()
for rota, met in [("/api/itens", "get"), ("/api/classificacao/interpretar", "post"), ("/api/classificacao/feedback", "post")]:
    rr = getattr(anon, met)(BASE + rota, json={} if met == "post" else None, allow_redirects=False)
    checa(f"{rota} exige login", rr.status_code in (401, 303), rr.status_code)
s2 = requests.Session()
s2.post(BASE + "/login", data={"codigo": CODIGO}, allow_redirects=False)
r = s2.post(BASE + "/api/classificacao/interpretar", json={"id": uid, "item": "anais"}, headers=ORIGEM)
checa("outra sessão não interpreta o arquivo alheio", r.status_code == 410, r.status_code)
r = s.post(BASE + "/api/classificacao/interpretar", json={"texto": "x", "item": "anais"}, headers={"Origin": "https://malicioso.example"})
checa("origem externa recusada", r.status_code == 403, r.status_code)

print("\nFALHAS:", falhas if falhas else "nenhuma")
sys.exit(1 if falhas else 0)
