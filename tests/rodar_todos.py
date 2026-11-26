"""Executa toda a suíte: scripts tests/teste_*.py (um processo por script) e o pytest.

Uso:  python tests/rodar_todos.py
Sai com código 1 se algum teste fora da lista CONHECIDOS_COM_FALHA falhar.

Scripts em CONHECIDOS_COM_FALHA são executados e relatados, mas não quebram o
build. Tire o nome da lista assim que o problema for corrigido.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TESTES = RAIZ / "tests"

CONHECIDOS_COM_FALHA = {
    # depende de um PDF local fora do repositório (Downloads do desenvolvedor)
    "teste_api_classificacao.py": "usa arquivo local fora do repositório",
}


def main() -> int:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", LATTESFACIL_SKIP_WARMUP="1")
    quebrou, tolerado = [], []

    for script in sorted(TESTES.glob("teste_*.py")):
        # banco isolado por script: um teste não enxerga nem suja o estado de outro
        with tempfile.TemporaryDirectory() as tmp:
            env["LATTESFACIL_DB"] = str(Path(tmp) / "teste.db")
            r = subprocess.run([sys.executable, str(script)],
                           cwd=RAIZ, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        ok = r.returncode == 0
        print(("OK    " if ok else "FALHA ") + script.name)
        if not ok:
            (tolerado if script.name in CONHECIDOS_COM_FALHA else quebrou).append(script.name)
            linhas = (r.stdout + r.stderr).strip().splitlines()
            falhas = [l for l in linhas if l.lstrip().startswith("FALHA")]
            print("\n".join(falhas[:10] + linhas[-6:]))

    r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(TESTES / "test_gemini.py")], cwd=RAIZ, env=env)
    if r.returncode != 0:
        quebrou.append("pytest")

    print(f"\nTolerados (falha conhecida): {tolerado or 'nenhum'}")
    print(f"Quebraram: {quebrou or 'nenhum'}")
    return 1 if quebrou else 0


if __name__ == "__main__":
    sys.exit(main())
