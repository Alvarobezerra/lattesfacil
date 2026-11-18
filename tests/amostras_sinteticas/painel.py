"""Gera docs/historico-testes-simulados.md a partir de tests/historico/execucoes.jsonl.

Uso: python tests/amostras_sinteticas/painel.py
Mostra, por item e por etapa, o último resultado, quantas vezes foi testado e onde há êxito, lacuna ou falha, para
decidir onde testar mais e onde aprimorar. Não edite o .md à mão: ele é regenerado (as notas manuais ficam em
tests/historico/notas.md e são incluídas no fim).
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from historico import ETAPAS, ler_tudo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent.parent
SAIDA = RAIZ / "docs" / "historico-testes-simulados.md"
NOTAS = RAIZ / "tests" / "historico" / "notas.md"
ICONE = {"ok": "✅", "falha": "❌", "lacuna": "🟡", "parcial": "🟠", "aviso": "⚪", None: "·"}
ROTULO = {"modulos": "Módulos", "plataforma": "Plataforma", "vinculo_lattes": "Vínculo", "lista_lattes": "Lista Lattes",
          "lattes_salvar": "Salvar", "lattes_conferir": "Conferir", "lattes_excluir": "Excluir", "lattes_reconferir": "Reconferir"}
PESO_PROBLEMA = {"falha": 3, "parcial": 2, "lacuna": 1, "aviso": 0, "ok": 0}


def main() -> None:
    ev = ler_tudo()
    if not ev:
        print("histórico vazio")
        return
    ev.sort(key=lambda r: r["execucao"])
    ultimo: dict[tuple[str, str], dict] = {}
    cont: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    variacoes: dict[tuple[str, str], dict] = {}
    for r in ev:
        if "__" in (r.get("arquivo") or ""):  # variação do documento (redação diferente): não substitui o resultado do item
            variacoes[(r["arquivo"], r["etapa"])] = r
            continue
        ultimo[(r["item"], r["etapa"])] = r
        cont[(r["item"], r["etapa"])][r["resultado"]] += 1
    itens = sorted({r["item"] for r in ev})
    execs = sorted({r["execucao"] for r in ev})
    L: list[str] = []
    A = L.append
    A("# Histórico consolidado dos testes simulados")
    A("")
    A(f"Gerado por `tests/amostras_sinteticas/painel.py` a partir de `tests/historico/execucoes.jsonl` — "
      f"{len(ev)} registros em {len(execs)} execuções (de {execs[0][:10]} a {execs[-1][:10]}), {len(itens)} itens.")
    A("")
    A("Legenda: ✅ ok · ❌ falha · 🟡 lacuna conhecida · 🟠 parcial (precisou de ajuda manual / não observado) · ⚪ aviso (sem regra ou tratador ainda) · · não testado.")
    A("Etapas, na ordem do caminho do documento até o Lattes: **Módulos** (classificador+leitor direto), **Plataforma** (caminho do /api/extract), "
      "**Vínculo** (abertura do formulário, lista mapeada e tratador), **Lista Lattes** (leitura da lista no currículo real), "
      "**Salvar**, **Conferir**, **Excluir** e **Reconferir** (ciclo no currículo real).")
    A("")
    # ---- resumo por etapa
    A("## 1. Resumo por etapa (último resultado de cada item)")
    A("")
    A("| Etapa | ✅ ok | 🟡 lacuna | 🟠 parcial | ⚪ aviso | ❌ falha | · não testado | % ok (sem os avisos) |")
    A("| --- | --: | --: | --: | --: | --: | --: | --: |")
    for e in ETAPAS:
        c = collections.Counter(ultimo[(i, e)]["resultado"] for i in itens if (i, e) in ultimo)
        n = sum(c.values())
        t = n - c["aviso"]  # "aviso" = ainda sem regra/tratador: não conta como testado com êxito ou falha
        A(f"| {ROTULO[e]} | {c['ok']} | {c['lacuna']} | {c['parcial']} | {c['aviso']} | {c['falha']} | {len(itens) - n} | "
          f"{round(100 * c['ok'] / t) if t else 0}% ({c['ok']}/{t}) |")
    A("")
    # ---- matriz
    A("## 2. Matriz item × etapa")
    A("")
    A("| Item | " + " | ".join(ROTULO[e] for e in ETAPAS) + " | Registros | Última execução |")
    A("| --- | " + " | ".join(":-:" for _ in ETAPAS) + " | --: | --- |")
    por_item = collections.defaultdict(list)
    for r in ev:
        por_item[r["item"]].append(r)

    def chave(i: str):
        etapas_feitas = sum(1 for e in ETAPAS if (i, e) in ultimo and ultimo[(i, e)]["resultado"] != "aviso")
        return (-etapas_feitas, i)

    for i in sorted(itens, key=chave):
        cel = [ICONE[ultimo[(i, e)]["resultado"]] if (i, e) in ultimo else "·" for e in ETAPAS]
        A(f"| `{i}` | " + " | ".join(cel) + f" | {len(por_item[i])} | {max(r['execucao'] for r in por_item[i])[:16].replace('T', ' ')} |")
    A("")
    # ---- onde testamos mais ou menos
    A("## 3. Onde testamos mais e onde menos")
    A("")
    prof = {i: sum(1 for e in ETAPAS if (i, e) in ultimo and ultimo[(i, e)]["resultado"] in ("ok", "lacuna", "falha", "parcial")) for i in itens}
    mais = [i for i in itens if prof[i] >= 5]
    A(f"- **Testados de ponta a ponta no currículo real (Salvar → Excluir → Reconferir):** "
      + (", ".join(f"`{i}`" for i in itens if (i, 'lattes_reconferir') in ultimo) or "nenhum") + ".")
    A(f"- **Profundidade ≥ 5 etapas:** " + (", ".join(f"`{i}`" for i in mais) or "nenhum") + ".")
    so_simulado = [i for i in itens if (i, "lattes_salvar") not in ultimo and prof[i] >= 2]
    A(f"- **Só testados no simulado (sem salvar no Lattes), com vínculo/lista prontos:** "
      + ", ".join(f"`{i}`" for i in so_simulado if (i, 'vinculo_lattes') in ultimo and ultimo[(i, 'vinculo_lattes')]['resultado'] == 'ok' and (i, 'lista_lattes') in ultimo and ultimo[(i, 'lista_lattes')]['resultado'] == 'ok') + ".")
    sem_regra = [i for i in itens if (i, "plataforma") in ultimo and ultimo[(i, "plataforma")]["resultado"] == "aviso"]
    A(f"- **Menos testados (sem regra no classificador, só o documento simulado existe):** {len(sem_regra)} itens — "
      + ", ".join(f"`{i}`" for i in sem_regra) + ".")
    A("")
    # ---- êxito e aprimorar
    A("## 4. Onde já temos êxito")
    A("")
    exito = [i for i in itens if all(ultimo[(i, e)]["resultado"] == "ok" for e in ETAPAS if (i, e) in ultimo and ultimo[(i, e)]["resultado"] != "aviso") and prof[i] >= 3]
    A(", ".join(f"`{i}`" for i in exito) or "—")
    A("")
    A("## 5. Onde aprimorar (do mais grave ao menos grave)")
    A("")
    A("| Item | Etapa | Resultado | O que aconteceu |")
    A("| --- | --- | :-: | --- |")
    prob = [(PESO_PROBLEMA[r["resultado"]], r) for (i, e), r in list(ultimo.items()) + list(variacoes.items())
            if r["resultado"] in ("falha", "parcial", "lacuna")]
    for _, r in sorted(prob, key=lambda x: (-x[0], x[1]["item"], ETAPAS.index(x[1]["etapa"]))):
        nome = r["item"] + (f" (variação `{r['arquivo']}`)" if "__" in (r.get("arquivo") or "") else "")
        A(f"| `{nome}` | {ROTULO[r['etapa']]} | {ICONE[r['resultado']]} | {r['detalhe'].replace('|', '/')[:220]} |")
    A("")
    A("**Recorrentes** (mesma causa em vários itens):")
    A("")
    causas = collections.Counter()
    for _, r in prob:
        d = r["detalhe"]
        if "janela de escolha" in d:
            causas["Abertura por janela de escolha sem tratador na extensão"] += 1
        elif "nome do arquivo" in d:
            causas["Nome padronizado do arquivo sem o sobrenome do usuário"] += 1
        elif "obrigatórios" in d:
            causas["Obrigatório do Lattes que o documento traz não é lido"] += 1
        elif "lista" in d and "vazia" in d:
            causas["Lista vazia no currículo: formato da linha não observado"] += 1
    for k, v in causas.most_common():
        A(f"- {k}: {v} item(ns)")
    A("")
    # ---- registro cronológico
    A("## 6. Registro das ações testadas (cronológico)")
    A("")
    A("| Execução | Origem | Registros | ✅ | 🟡 | 🟠 | ⚪ | ❌ | Itens com ocorrência não-ok (resumo) |")
    A("| --- | --- | --: | --: | --: | --: | --: | --: | --- |")
    por_exec = collections.defaultdict(list)
    for r in ev:
        por_exec[(r["execucao"], r["origem"])].append(r)
    for (ex, orig), rs in sorted(por_exec.items()):
        c = collections.Counter(r["resultado"] for r in rs)
        nok = sorted({r["item"] for r in rs if r["resultado"] in ("falha", "parcial")})
        A(f"| {ex.replace('T', ' ')} | `{orig}` | {len(rs)} | {c['ok']} | {c['lacuna']} | {c['parcial']} | {c['aviso']} | {c['falha']} | "
          + (", ".join(nok[:8]) + (" …" if len(nok) > 8 else "") if nok else "—") + " |")
    A("")
    A("### Detalhe das execuções no currículo real")
    A("")
    for (ex, orig), rs in sorted(por_exec.items()):
        if orig != "manual_lattes_real":
            continue
        A(f"**{ex.replace('T', ' ')}**")
        A("")
        for r in rs:
            if r["etapa"] == "lista_lattes" and r["resultado"] == "aviso":
                continue
            A(f"- `{r['item']}` · {ROTULO[r['etapa']]} · {ICONE[r['resultado']]} {r['detalhe']}")
        A("")
    if NOTAS.is_file():
        A("## 7. Notas e decisões")
        A("")
        A(NOTAS.read_text(encoding="utf-8").strip())
        A("")
    SAIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{SAIDA.relative_to(RAIZ)} gerado: {len(ev)} registros, {len(itens)} itens")


if __name__ == "__main__":
    main()
