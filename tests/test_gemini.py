import os
import unittest
from unittest.mock import Mock, patch

import gemini
import server
from itens import especificacao


class GeminiTests(unittest.TestCase):
    def test_transient_overload_retries_then_succeeds(self):
        busy = Mock(status_code=503)
        success = Mock(status_code=200)
        success.json.return_value = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": '{"item":"artigo"}'}]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), \
             patch("gemini.requests.post", side_effect=[busy, success]) as post, patch("gemini.time.sleep") as sleep:
            self.assertEqual(gemini.classify("doc", {"artigo": "Artigo"}), "artigo")
            self.assertEqual(post.call_count, 2)
            sleep.assert_called_once_with(1)

    def test_overload_has_bounded_retries(self):
        response = Mock(status_code=503, headers={}, text="")
        response.json.return_value = {"error": {"message": "High demand"}}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), \
             patch("gemini.requests.post", return_value=response) as post, patch("gemini.time.sleep"):
            with self.assertRaisesRegex(gemini.GeminiError, "MODEL_BUSY"):
                gemini.ask("test", {}, "doc")
            self.assertEqual(post.call_count, 3)

    def test_google_error_reason_and_secret_redaction(self):
        response = Mock(status_code=400)
        response.json.return_value = {"error": {"message": "API key not valid: test-key-with-at-least-20-characters", "details": [
            {"reason": "API_KEY_INVALID", "metadata": {"key": "test-key-with-at-least-20-characters"}}]}}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=response):
            with self.assertRaises(gemini.GeminiError) as caught:
                gemini.ask("test", {}, "doc")
        self.assertIn("API_KEY_INVALID", str(caught.exception))
        self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception))
        self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception.diagnostic))

    def test_bad_schema_is_distinct_from_invalid_key(self):
        response = Mock(status_code=400)
        response.json.return_value = {"error": {"message": "Invalid generationConfig.responseJsonSchema"}}
        error = gemini.api_error(response, "secret")
        self.assertEqual(error.diagnostic["motivo"], "JSON_SCHEMA")

    def test_non_json_error_preserves_fallback(self):
        response = Mock(status_code=503)
        response.json.side_effect = ValueError("not json")
        self.assertIn("HTTP 503", str(gemini.api_error(response, "secret")))

    def test_html_400_does_not_claim_schema_or_key_failure(self):
        response = Mock(status_code=400, text="<html>Error 400</html>", headers={"Content-Type": "text/html"})
        response.json.side_effect = ValueError("not json")
        error = gemini.api_error(response, "secret")
        self.assertEqual(error.diagnostic["motivo"], "HTTP_BAD_REQUEST")
        self.assertNotIn("<html>", str(error))

    def test_malformed_key_does_not_reach_google(self):
        for key in ('*', 'x', '"test-key-with-at-least-20-characters"', 'test-key-with-at-least-20-characters\\', 'two words with at least twenty characters', 'key\nvalue-with-at-least-twenty-characters'):
            with self.subTest(key=key), patch.dict(os.environ, {"GEMINI_API_KEY": key}), patch("gemini.requests.post") as post:
                with self.assertRaises(gemini.GeminiError):
                    gemini.ask("test", {}, "doc")
                post.assert_not_called()

    def test_launcher_replaces_incomplete_key_and_tests_before_start(self):
        import iniciar_gemini
        with patch.dict(os.environ, {"GEMINI_API_KEY": "*"}), \
             patch("sys.argv", ["iniciar_gemini.py"]), \
             patch("iniciar_gemini.socket.socket"), \
             patch("iniciar_gemini.prompt_key", return_value="test-key-with-at-least-20-characters") as prompt, \
             patch("ferramentas.diagnosticar_gemini.main", return_value=0) as diagnostic, \
             patch("server.main") as start, patch("builtins.print"):
            self.assertEqual(iniciar_gemini.main(), 0)
            prompt.assert_called_once()
            diagnostic.assert_called_once_with(documents=True)
            start.assert_called_once()
            self.assertEqual(os.environ["HOST"], "127.0.0.1")
            self.assertEqual(os.environ["PORT"], "8766")

    def test_launcher_does_not_start_when_live_check_fails(self):
        import iniciar_gemini
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), \
             patch("sys.argv", ["iniciar_gemini.py"]), patch("iniciar_gemini.socket.socket"), \
             patch("ferramentas.diagnosticar_gemini.main", return_value=1), \
             patch("server.main") as start, patch("builtins.print"):
            self.assertEqual(iniciar_gemini.main(), 1)
            start.assert_not_called()

    def test_disabled_does_not_call_network(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "0"}), patch("gemini.requests.post") as post:
            server.process_extract("teste.txt", b"Certificado de curso de Python, carga horaria 20 horas.", "")
            post.assert_not_called()

    def test_http_failure_does_not_expose_key_or_response(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=Mock(status_code=403)):
            with self.assertRaisesRegex(gemini.GeminiError, "HTTP 403") as caught:
                gemini.ask("test", {}, "doc")
            self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception))

    def test_transport_and_json(self):
        response = Mock(status_code=200)
        response.json.return_value = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": '{"item":"artigo"}'}]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=response) as post:
            self.assertEqual(gemini.classify("documento", {"artigo": "Artigo"}), "artigo")
            self.assertNotIn("test-key-with-at-least-20-characters", post.call_args.args[0])
            self.assertEqual(post.call_args.kwargs["headers"]["x-goog-api-key"], "test-key-with-at-least-20-characters")

    def test_fields_reject_unknown_unproven_invalid_option(self):
        rows = [{"campo": "f_ano", "valor": "2026", "trecho": "Evento em 2026"},
                {"campo": "f_nme_evento", "valor": "Inventado", "trecho": "trecho ausente"},
                {"campo": "F_FORMA", "valor": "Inválido", "trecho": "Evento em 2026"},
                {"campo": "evil", "valor": "x", "trecho": "Evento em 2026"}]
        with patch("gemini.ask", return_value={"campos": rows}):
            values, evidence = gemini.fields("Evento em 2026", especificacao("participacao_evento"), "único")
            self.assertEqual(values, {"f_ano": "2026"})
            self.assertEqual(len(evidence), 1)

    def test_failure_keeps_local_form(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1"}), patch("gemini.fields", side_effect=gemini.GeminiError("Falha simulada")):
            result = server.interpretar("participacao_evento", "Participou do Congresso em 2026.", "", "")
            self.assertIn("Falha simulada", result["generico"]["notas"])
            self.assertIn("extracted", result)

    def test_success_updates_fields_and_required_fields(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1"}), patch("gemini.fields", return_value=(
                {"f_nme_evento": "Congresso de Biologia", "f_ano": "2026"}, ["Trecho comprovado"])):
            result = server.interpretar("participacao_evento", "Documento de participação.", "", "")
            self.assertEqual(result["extracted"]["ano"], "2026")
            self.assertEqual(result["extracted"]["titulo"], "Congresso de Biologia")
            self.assertNotIn("Ano", result["generico"]["faltam_obrigatorios"])
            self.assertIn("Trecho comprovado", result["generico"]["notas"])

    def test_incomplete_output_falls_back(self):
        response = Mock(status_code=200)
        response.json.return_value = {"candidates": [{"finishReason": "MAX_TOKENS"}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=response):
            with self.assertRaises(gemini.GeminiError):
                gemini.ask("test", {}, "doc")

    def test_missing_key_and_limits_do_not_send_request(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}), patch("gemini.requests.post") as post:
            with self.assertRaises(gemini.GeminiError):
                gemini.ask("test", {}, "doc")
            post.assert_not_called()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post") as post:
            with self.assertRaises(gemini.GeminiError):
                gemini.ask("test", {}, "a" * 60001)
            with self.assertRaises(gemini.GeminiError):
                gemini.transcribe(b"a" * (10 * 1024 * 1024 + 1), "image/png")
            post.assert_not_called()

    def test_disagreement_requires_confirmation(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1"}), patch("gemini.classify", return_value="participacao_evento"):
            result = server.responder_evidencia(server.candidato_fixo("artigo", "local"), "Documento", "", "")
            self.assertEqual(result["classificacao"]["decisao"], "confirmar")
            self.assertNotIn("generico", result)

    def test_image_without_ocr_uses_transcription(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1"}), \
             patch("server.extract_text_from_image_bytes", return_value={"text": ""}), \
             patch("gemini.transcribe", return_value="Certificado de participação em 2026") as transcribe, \
             patch("gemini.classify", return_value="nenhum"), \
             patch("gemini.fields", return_value=({}, [])):
            result = server.process_extract("foto.png", b"image", "")
            transcribe.assert_called_once_with(b"image", "image/png")
            self.assertIn("transcrito", result["ia_aviso"])
            self.assertIn("Certificado", result["_leitura"]["texto"])


if __name__ == "__main__":
    unittest.main()

