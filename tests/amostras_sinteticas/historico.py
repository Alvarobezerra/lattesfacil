"""Histórico consolidado dos testes simulados: um registro por (execução, item, etapa) em tests/historico/execucoes.jsonl.

Quem registra: as rotinas automáticas (teste_amostras_sinteticas.py, teste_plataforma_sinteticos.py) e, para o que roda no
Lattes real (salvar, conferir, excluir), o próprio executor (`python tests/amostras_sinteticas/historico.py registrar ...`).
O painel (docs/historico-testes-simulados.md) é gerado por tests/amostras_sinteticas/painel.py. Regras: docs/regras-documentos-sinteticos.md.

Etapas (ordem do caminho do documento até o Lattes):
  modulos         classificador + leitor chamados direto (teste_amostras_sinteticas)
  plataforma      mesmo caminho do /api/extract: reconhecimento, valores e obrigatórios (teste_plataforma_sinteticos)
  vinculo_lattes  especificação com abertura, lista do Lattes mapeada e tratador da extensão
  lista_lattes    leitura da lista do item no currículo real (somente leitura)
  lattes_salvar   formulário preenchido e salvo no currículo real
  lattes_conferir o item novo aparece na lista do currículo
  lattes_excluir  exclusão do item de teste
  lattes_reconferir  após reentrar, o item não está mais na lista e os demais continuam
Resultados: ok | falha | lacuna (limite conhecido) | aviso (sem regra/tratador ainda) | parcial (precisou de ajuda manual)
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ARQ = Path(__file__).resolve().parent.parent / "historico" / "execucoes.jsonl"
ETAPAS = ["modulos", "plataforma", "vinculo_lattes", "lista_lattes", "lattes_salvar", "lattes_conferir", "lattes_excluir", "lattes_reconferir"]
RESULTADOS = {"ok", "falha", "lacuna", "aviso", "parcial"}


def _limpar(txt: str, nomes: list[str]) -> str:
    """Nada de dado pessoal no histórico: o nome do titular vira <titular>."""
    for n in nomes:
        if n:
            txt = re.sub(re.escape(n), "<titular>", txt, flags=re.I)
    return txt[:400]


def nova_execucao(origem: str) -> dict:
    return {"execucao": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "origem": origem, "_buf": []}


def registrar(exe: dict, item: str, etapa: str, resultado: str, detalhe: str = "", arquivo: str = "", nomes: list[str] | None = None) -> None:
    assert etapa in ETAPAS and resultado in RESULTADOS, (etapa, resultado)
    exe["_buf"].append({"execucao": exe["execucao"], "origem": exe["origem"], "item": item, "etapa": etapa, "resultado": resultado,
                        "detalhe": _limpar(detalhe, nomes or []), "arquivo": arquivo})


def gravar(exe: dict) -> int:
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    with ARQ.open("a", encoding="utf-8", newline="\n") as f:
        for r in exe["_buf"]:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(exe["_buf"])


def ler_tudo() -> list[dict]:
    if not ARQ.is_file():
        return []
    return [json.loads(l) for l in ARQ.read_text(encoding="utf-8").splitlines() if l.strip()]


if __name__ == "__main__":
    # python historico.py registrar <origem> <item> <etapa> <resultado> "<detalhe>"   (execuções feitas no Lattes real)
    if len(sys.argv) >= 6 and sys.argv[1] == "registrar":
        e = nova_execucao(sys.argv[2])
        registrar(e, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else "")
        print(gravar(e), "registro gravado")
