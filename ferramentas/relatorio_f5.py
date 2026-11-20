"""Resume os resultados da fase 5 (docs/campos-lattes/ref/<item>_f5/*.json): contagem por status e lista do que não ficou OK.

Uso:  python ferramentas/relatorio_f5.py projeto
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def main(item):
    pasta = RAIZ / "docs" / "campos-lattes" / "ref" / f"{item}_f5"
    arquivos = sorted(pasta.glob("*.json"))
    if not arquivos:
        print("sem resultados em", pasta)
        return 2
    total_ruim = 0
    for p in arquivos:
        d = json.loads(p.read_text(encoding="utf-8"))
        res = d.get("resultados", [])
        print(f"\n=== {d.get('variante')} ({d.get('executado_em', '')[:19]}) casos={len(res)} resumo={d.get('resumo')}")
        for r in res:
            if r["status"] not in ("OK",):
                total_ruim += 1
                print(f"  - {r['id']}: {r['status']} {r.get('detalhe', '')} {('| ' + r['aviso']) if r.get('aviso') else ''}")
    print(f"\nNão-OK no total: {total_ruim}")
    return 0 if total_ruim == 0 else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    sys.exit(main(sys.argv[1]))
