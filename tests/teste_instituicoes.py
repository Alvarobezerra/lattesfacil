"""Banco de instituições: gravação oportunista, busca local, confirmações, fila dos 6 prefixos, tetos e métricas.
Uso: python tests/teste_instituicoes.py"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import instituicoes as I  # noqa: E402

falhas = 0


def checa(nome, cond, extra=""):
    global falhas
    print(("OK   " if cond else "FALHA ") + nome + (f" — {extra}" if extra and not cond else ""))
    falhas += 0 if cond else 1


c = sqlite3.connect(":memory:")
I.criar_tabelas(c)

# semente e fila inicial
b = I.buscar(c, "UFC")
checa("sigla da semente encontra a instituição", b["candidatas"] and b["candidatas"][0]["nome"] == "Universidade Federal do Ceará", b)
checa("semente não tem código (falta confirmar na lupa)", b["candidatas"][0]["codigo"] == "")
fila = [r[0] for r in c.execute("SELECT termo FROM inst_fila ORDER BY prioridade").fetchall()]
checa("fila nasce com os 6 prefixos, na ordem", fila == I.PREFIXOS_PRIORITARIOS, fila)

# desligada por padrão e teto diário
lote = I.proximo_lote(c)
checa("coleta nasce desligada", not lote["ativa"] and not lote["termos"], lote)
cfg = I.definir_config(c, {"ativa": 1, "limite_dia": 3, "limite_lote": 10, "intervalo_ms": 100, "xpto": 5})
checa("config respeita tetos e ignora chave desconhecida", cfg["intervalo_ms"] == 2000 and "xpto" not in cfg and cfg["limite_dia"] == 3, cfg)
lote = I.proximo_lote(c)
checa("lote limitado pelo teto diário e começa pelos prefixos prioritários", lote["termos"] == ["Universidade", "Instituto", "Faculdade"], lote)

# gravação oportunista (uso) não mexe na fila e alimenta o banco
r = I.registrar(c, [{"nome": "Universidade Federal do Ceará (CE)", "ref": "'12345',1"}, {"nome": "Universidade Federal do Ceará - Campus Sobral (CE)", "ref": "'12346',1"}], "Universidade Federal do Ceará", "uso", 900)
checa("registrar: itens já presentes na semente viram coletados e não contam como novos", r["total"] == 2 and r["novas"] == 0, r)
b = I.buscar(c, "Universidade Federal do Ceará")
checa("busca local agora traz código vindo da lupa", b["candidatas"][0]["codigo"] == "12345", b)
checa("consulta de 'uso' não consome o teto da coleta", I.consultas_hoje(c) == 0)
checa("fila intacta após consulta de uso", c.execute("SELECT COUNT(*) FROM inst_fila WHERE estado != 'pendente'").fetchone()[0] == 0)

# confirmação do usuário e desfazer
iid = b["candidatas"][0]["id"]
checa("confirmar grava o par texto→instituição", I.confirmar(c, "UFC - Fortaleza", iid, "ana"))
b2 = I.buscar(c, "ufc  fortaleza")
checa("busca por texto confirmado volta a confirmada e clara", b2["confirmada"] and b2["claro"] and b2["candidatas"][0]["id"] == iid, b2)
checa("confirmar id inexistente falha", not I.confirmar(c, "x y", 99999))
checa("desfazer remove a confirmação", I.desfazer_confirmacao(c, "UFC - Fortaleza") and not I.buscar(c, "UFC - Fortaleza")["confirmada"])

# coleta: saturação e aprofundamento (cap detectado quando o máximo se repete)
def itens(prefixo, n):
    return [{"nome": f"{prefixo} Federal do Lugar{i}", "ref": f"'{prefixo[:2]}{i:04d}',1"} for i in range(n)]

I.definir_config(c, {"limite_dia": 200, "limite_lote": 25})
I.registrar(c, itens("Universidade", 30), "Universidade", "coleta", 1200)
I.registrar(c, itens("Instituto", 30), "Instituto", "coleta", 1100)
checa("cap detectado quando o máximo se repete", I.cap_detectado(c) == 30, I.cap_detectado(c))
I.registrar(c, itens("Faculdade", 30), "Faculdade", "coleta", 1000)
est = {r[0]: r[1] for r in c.execute("SELECT termo, estado FROM inst_fila").fetchall()}
checa("prefixo que devolve o máximo fica 'saturado'", est["Faculdade"] == "saturado", est)
filhos = [r[0] for r in c.execute("SELECT termo FROM inst_fila WHERE termo LIKE 'Faculdade %'").fetchall()]
checa("saturado gera aprofundamentos (nível 2)", len(filhos) >= 3, filhos)
lote = I.proximo_lote(c)
checa("próximo lote esgota os prefixos restantes (nível 1) antes dos aprofundamentos", lote["termos"][:3] == ["Hospital", "Centro", "Fundação"], lote["termos"])

# a mesma consulta recebida por duas abas do app não conta duas vezes
a = I.registrar(c, itens("Centro", 3), "Centro", "uso", 500, "", "abc123")
b_ = I.registrar(c, itens("Centro", 3), "Centro", "uso", 500, "", "abc123")
checa("lote_id repetido é ignorado (várias abas do app)", a["total"] == 3 and b_.get("duplicado") == 1 and c.execute("SELECT COUNT(*) FROM inst_consultas WHERE lote_id='abc123'").fetchone()[0] == 1, (a, b_))

# erro não marca como feito
I.registrar(c, [], "Hospital", "coleta", 0, "timeout")
checa("consulta com erro mantém o prefixo pendente", c.execute("SELECT estado FROM inst_fila WHERE termo='Hospital'").fetchone()[0] == "pendente")

# importar semente (e-MEC) e estatísticas
imp = I.importar_csv(c, "Nome da IES;Sigla\nUniversidade Federal do Piauí;UFPI\nFaculdade Teste de Saúde;FTS\n")
checa("importar CSV de semente", imp["lidas"] == 2 and imp["novas"] >= 1, imp)
st = I.estatisticas(c)
checa("estatísticas: banco, prefixos, desempenho e série diária", st["banco"]["total"] > 30 and len(st["prefixos"]) == 6 and len(st["por_dia"]) == 14 and st["desempenho"]["consultas_total"] >= 5, st["desempenho"])
checa("estatísticas guardam amostra do formato do link (sondagem)", st["amostras_ref"], st["amostras_ref"])
checa("teto diário reflete as consultas feitas", st["hoje"]["coleta"] == 4 and st["hoje"]["uso"] == 2, st["hoje"])

print(f"{falhas} falha(s)")
sys.exit(1 if falhas else 0)
