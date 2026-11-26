"""Diagnóstico real com texto sintético. Não grava a chave nem documentos do usuário."""
import json
import os
from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import gemini


def main(documents=False):
    gemini.load_dotenv_file(ROOT)
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = gemini.current_model()
    report = {"modelo": model,
              "chave_configurada": bool(key),
              "configuracao": {"tamanho_chave": len(key),
                  "tipo_chave": "auth" if key.startswith("AQ.") else "standard" if key.startswith("AIza") else "desconhecido",
                  "formato_compativel": bool(gemini.re.fullmatch(r"(?:AQ\.|AIza)[A-Za-z0-9_.-]+", key)),
                  "contem_espacos": any(c.isspace() for c in key),
                  "contem_aspas_ou_barras": any(c in key for c in "\"'\\"),
                  "proxy_configurado": any(os.getenv(k) for k in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"))}}
    try:
        result = gemini.classify("Certificamos que Pessoa Teste participou como ouvinte do Congresso de Biologia em 2026.",
                                {"participacao_evento": "Participação como ouvinte em evento", "artigo": "Artigo científico publicado"})
        report.update(ok=result == "participacao_evento", resultado=result)
        if report["ok"] and documents:
            import pymupdf
            from itens import especificacao
            with pymupdf.open() as doc:
                page = doc.new_page()
                page.insert_text((72, 72), "CERTIFICADO\nPessoa Teste participou como ouvinte do Congresso de Biologia.\nAno do evento: 2026. Carga horaria: 20 horas.")
                pdf = doc.tobytes()
            text = gemini.transcribe(pdf, "application/pdf")
            values, evidence = gemini.fields(text, especificacao("participacao_evento"), "único")
            passed = values.get("f_ano") == "2026" and "biologia" in values.get("f_nme_evento", "").lower()
            report.update(ok=passed, documento_pdf={"transcricao": bool(text), "campos_validados": passed,
                                                   "campos": sorted(values), "trechos": len(evidence)})
    except gemini.GeminiError as exc:
        report.update(ok=False, erro=str(exc), diagnostico=exc.diagnostic)
        if report["chave_configurada"] and report["configuracao"]["formato_compativel"] and len(key) >= 20:
            key = os.environ["GEMINI_API_KEY"].strip()
            if gemini.re.fullmatch(r"gemini-[a-zA-Z0-9.-]+", model):
                try:
                    minimal = requests.post(
                        gemini.INTERACTIONS_URL,
                        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                        json={"model": model, "input": "Responda apenas OK.", "store": False},
                        timeout=(10, 45), allow_redirects=False)
                    report["requisicao_minima"] = ({"http": 200} if minimal.status_code == 200
                                                  else gemini.api_error(minimal, key).diagnostic)
                    models = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                                          headers={"x-goog-api-key": key}, timeout=(10, 30), allow_redirects=False)
                    report["consulta_modelos"] = ({"http": 200, "modelos": [m.get("name") for m in models.json().get("models", [])]}
                                                  if models.status_code == 200 else gemini.api_error(models, key).diagnostic)
                    control = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                                           timeout=(10, 30), allow_redirects=False)
                    report["controle_sem_chave"] = {"http": control.status_code,
                                                    "tipo_resposta": control.headers.get("Content-Type", "")}
                except (requests.RequestException, ValueError):
                    report["comparacao"] = "Não foi possível completar a comparação por rede/resposta inválida."
    target = ROOT / "tmp" / "diagnostico-gemini.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Teste concluído:", "OK" if report["ok"] else report.get("erro", "resultado inesperado"))
    print("Relatório sem chave:", target)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
