"""Etapa PLATAFORMA da rotina: passa cada PDF simulado pelo mesmo caminho do /api/extract do servidor e confere
(1) reconhecimento do item, (2) valores extraídos, (3) obrigatórios que faltam, (4) nome padronizado do arquivo e
(5) vínculo com o Lattes (especificação com abertura, lista do Lattes mapeada). Não toca no Lattes.

Uso:  python tests/teste_plataforma_sinteticos.py [id ...]
Antes: python tests/teste_amostras_sinteticas.py --so-gerar   (gera os PDFs com o seu nome)
Saída: OK / FALHA / LACUNA (variação marcada no catálogo) / AVISO (item ainda sem regra no classificador) e o relatório
em tests/amostras_sinteticas/pdf/relatorio_plataforma.json. Regras: docs/regras-documentos-sinteticos.md
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent / "amostras_sinteticas"))

from catalogo import CASOS, NEGATIVOS, PESQUISADORA  # noqa: E402
from historico import gravar, nova_execucao, registrar  # noqa: E402
import server  # noqa: E402
from itens import especificacao  # noqa: E402

PDFS = Path(__file__).resolve().parent / "amostras_sinteticas" / "pdf"
LISTAS = json.loads((RAIZ / "itens" / "listas_lattes.json").read_text(encoding="utf-8"))
SEM_ESPEC = {"caderno"}


def _sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().upper()


def _valores(res: dict) -> dict:
    v = dict((res.get("extracted") or {}))
    v.update((res.get("generico") or {}).get("valores") or {})
    return v


def _vinculo_lattes(item: str) -> list[str]:
    """Problemas no elo plataforma -> Lattes para o item (vazio = ok).

    O Lattes abre alguns formulários por uma janela de escolha (patente, livro, formação...), mas o formulário também abre
    direto pela URL da variante (confirmado no currículo real em 17/11/2026), então a janela não é necessária."""
    if item in ():
        return []
    spec = especificacao(item)
    if not spec:
        return ["sem especificação de formulário"]
    p = []
    for v in spec["variantes"]:
        u = (v.get("url") or "").lower()
        if not u:
            p.append(f"variante {v['variante']} sem URL direta do formulário")
    if item not in LISTAS:
        p.append("lista do Lattes não mapeada")
    return p


def main(argv: list[str]) -> int:
    filtro = set(argv)
    relatorio, falhas, lacunas, avisos, oks = [], 0, 0, 0, 0
    exe = nova_execucao("teste_plataforma_sinteticos")
    for c in CASOS + NEGATIVOS:
        if filtro and c["arquivo"] not in filtro and c["item"] not in filtro:
            continue
        pdf = PDFS / f"{c['arquivo']}.pdf"
        if not pdf.is_file():
            print(f"FALHA  {c['arquivo']}: PDF não gerado (rode tests/teste_amostras_sinteticas.py --so-gerar)")
            falhas += 1
            continue
        res = server.process_extract(pdf.name, pdf.read_bytes(), PESQUISADORA)
        leitura = res.pop("_leitura", None) or {}
        res.pop("raw_text", None)
        cls = res.get("classificacao") or {}
        top = cls["candidatos"][0]["id"] if cls.get("candidatos") else "nenhum"
        decisao = cls.get("decisao")
        observacoes = []
        if decisao == "confirmar" and top == c["classe"] and not res.get("extracted") and not res.get("generico"):
            # a plataforma pede 1 clique de confirmação; depois do clique ela lê como o item escolhido
            observacoes.append("pediu confirmação do usuário (empate com " + ", ".join(
                x["id"] for x in cls["candidatos"][1:3]) + ")")
            feito = server.interpretar(top, leitura.get("texto", ""), leitura.get("arquivo", ""), PESQUISADORA)
            if feito:
                res.update(feito)
        v = _valores(res)
        problemas = []
        if c["classe"] == "escolher":
            if decisao != "escolher":
                problemas.append(f"deveria pedir escolha, mas reconheceu {top} ({decisao})")
        elif c["classe"]:
            if top != c["classe"] or decisao == "escolher":
                problemas.append(f"reconheceu {top} ({decisao}), esperado {c['classe']}")
        for campo, trecho in (c.get("campos") or {}).items():
            if trecho.lower() not in str(v.get(campo, "")).lower():
                problemas.append(f"valor {campo}={str(v.get(campo))[:60]!r}, esperado conter {trecho!r}")
        faltam = (res.get("generico") or {}).get("faltam_obrigatorios") or []
        faltam_reais = [f for f in faltam if f not in (c.get("nao_traz") or [])]
        if faltam_reais and c["classe"] and not c.get("lacuna"):
            problemas.append(f"obrigatórios do Lattes sem valor que o documento traz: {faltam_reais}")
        if c["item"] and c["classe"] and c["classe"] != "escolher":
            sobrenome = _sem_acento(PESQUISADORA.split()[-1])
            nome = _sem_acento(res.get("nome_padronizado") or "")
            if nome and sobrenome not in nome:
                observacoes.append(f"nome do arquivo sem o seu sobrenome ({res.get('nome_padronizado')})")
        elo = _vinculo_lattes(c["item"]) if c["item"] and c["classe"] not in (None, "escolher") else []
        problemas += [f"vínculo Lattes: {e}" for e in elo]
        if c["item"]:
            p_plat = [x for x in problemas if not x.startswith("vínculo Lattes")]
            p_elo = [x for x in problemas if x.startswith("vínculo Lattes")]
            r_plat = "lacuna" if p_plat and c.get("lacuna") else "falha" if p_plat else "aviso" if c["classe"] is None else "ok"
            registrar(exe, c["item"], "plataforma", r_plat, "; ".join(p_plat + observacoes) if (p_plat or observacoes) else "", c["arquivo"], [PESQUISADORA])
            if c["classe"] not in (None, "escolher") and not c.get("lacuna"):
                registrar(exe, c["item"], "vinculo_lattes", "falha" if p_elo else "ok", "; ".join(p_elo), c["arquivo"], [PESQUISADORA])
        estado = "OK"
        if problemas and c.get("lacuna"):
            estado = "LACUNA"
            lacunas += 1
        elif problemas:
            estado = "FALHA"
            falhas += 1
        elif c["classe"] is None:
            estado = "AVISO"
            avisos += 1
        else:
            oks += 1
        if observacoes and estado in ("OK", "LACUNA"):
            problemas_txt = " | obs: " + "; ".join(observacoes)
        else:
            problemas_txt = ""
        det = ("; ".join(problemas) + problemas_txt) if problemas else (problemas_txt.strip(" |") if problemas_txt else "") or (f"sem regra no classificador (reconheceu {top}/{decisao})" if estado == "AVISO" else "")
        print(f"{estado:6s} {c['arquivo']}" + (f": {det}" if det else ""))
        relatorio.append({"arquivo": c["arquivo"], "item": c["item"], "estado": estado, "reconheceu": top, "decisao": decisao,
                          "problemas": problemas, "observacoes": observacoes, "valores": {k: str(x)[:120] for k, x in v.items()},
                          "nome_padronizado": res.get("nome_padronizado"), "faltam_obrigatorios": faltam})
    if not filtro:
        gravar(exe)
    (PDFS / "relatorio_plataforma.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nOK {oks} | LACUNA {lacunas} | AVISO {avisos} | FALHA {falhas} | total {len(relatorio)}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
