"""Inicialização local com entrada oculta da chave e teste real antes do servidor."""
import argparse
import getpass
import os
from pathlib import Path
import socket
import sys
import warnings

import gemini


def prompt_key():
    """No Windows, getpass/msvcrt pode ler Ctrl+V como um único caractere."""
    if os.name == "nt":
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return (simpledialog.askstring(
                "Lattes Fácil — configurar Gemini",
                "Copie a chave inteira no Google AI Studio.\nCole aqui com Ctrl+V e clique em OK.\nA chave não será salva em arquivo.",
                show="*", parent=root) or "").strip()
        finally:
            root.destroy()
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        return getpass.getpass("Chave Gemini: ").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("A porta deve estar entre 1 e 65535.")
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", args.port))
        except OSError:
            print(f"A porta {args.port} está ocupada ou indisponível. Encerre o servidor antigo ou use --port 8767.")
            return 1
    os.chdir(Path(__file__).resolve().parent)
    key = os.getenv("GEMINI_API_KEY", "").strip()
    try:
        gemini.validate_key(key)
    except gemini.GeminiError:
        print("A chave atual está ausente ou incompleta. Copie a chave inteira no Google AI Studio.")
        print("Cole a chave na janela de configuração que será aberta; não digite asteriscos.")
        try:
            key = prompt_key()
        except (getpass.GetPassWarning, EOFError, ImportError):
            print("Não foi possível abrir a entrada segura. Use Python com Tkinter no Windows ou configure GEMINI_API_KEY no ambiente.")
            return 1
        if not key:
            print("Configuração cancelada. Servidor não iniciado.")
            return 1
        try:
            gemini.validate_key(key)
        except gemini.GeminiError as exc:
            print(str(exc))
            return 1
    os.environ["GEMINI_API_KEY"] = key
    os.environ["GEMINI_ENABLED"] = "1"
    os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = str(args.port)
    print("Testando Gemini com documento fictício, sem salvar sua chave...")
    from ferramentas.diagnosticar_gemini import main as diagnose
    if diagnose(documents=True):
        print("Servidor não iniciado: confira o diagnóstico acima.")
        return 1
    print(f"Gemini validado. Abra http://127.0.0.1:{args.port}/ e envie sua evidência.")
    import server
    server.main()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
