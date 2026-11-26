import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import gemini
import server
from itens import especificacao, ids_especificados


def _interaction_ok(payload_obj, *, in_tokens=500, out_tokens=100):
    resp = Mock(status_code=200)
    resp.json.return_value = {
        "id": "v1_test_123",
        "status": "completed",
        "steps": [
            {"type": "thought", "content": [{"type": "text", "text": "raciocínio interno"}]},
            {"type": "model_output", "content": [{"type": "text", "text": json.dumps(payload_obj, ensure_ascii=False)}]},
        ],
        "usage": {
            "total_input_tokens": in_tokens,
            "total_output_tokens": out_tokens,
        },
    }
    return resp


class GeminiTests(unittest.TestCase):
    def setUp(self):
        gemini.clear_cache()
        gemini.reset_usage()
    def test_transient_overload_retries_then_succeeds(self):
        busy = Mock(status_code=503)
        success = _interaction_ok({"item": "artigo"})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), \
             patch("gemini.requests.post", side_effect=[busy, success]) as post, patch("gemini.time.sleep") as sleep:
            self.assertEqual(gemini.classify("doc", {"artigo": "Artigo"}), "artigo")
            self.assertEqual(post.call_count, 2)
            sleep.assert_called_once_with(1)

    def test_overload_has_bounded_retries_and_fallback(self):
        response = Mock(status_code=503, headers={}, text="")
        response.json.return_value = {"error": {"message": "High demand"}}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters", "GEMINI_MODEL": "gemini-3.5-flash-lite"}), \
             patch("gemini.requests.post", return_value=response) as post, patch("gemini.time.sleep"):
            with self.assertRaisesRegex(gemini.GeminiError, "MODEL_BUSY"):
                gemini.ask("test", {}, "doc")
            # 3 tentativas por modelo na cadeia de fallback (3 modelos = 9 chamadas)
            self.assertEqual(post.call_count, 3 * len(gemini.FALLBACK_MODELS))

    def test_google_error_reason_and_secret_redaction(self):
        response = Mock(status_code=400, headers={}, text="API key not valid: test-key-with-at-least-20-characters")
        response.json.return_value = {"error": {"message": "API key not valid: test-key-with-at-least-20-characters", "details": [
            {"reason": "API_KEY_INVALID", "metadata": {"key": "test-key-with-at-least-20-characters"}}]}}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=response):
            with self.assertRaises(gemini.GeminiError) as caught:
                gemini.ask("test", {}, "doc")
        self.assertIn("API_KEY_INVALID", str(caught.exception))
        self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception))
        self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception.diagnostic))

    def test_bad_schema_is_distinct_from_invalid_key(self):
        response = Mock(status_code=400, headers={}, text="")
        response.json.return_value = {"error": {"message": "Invalid response_format.schema"}}
        error = gemini.api_error(response, "secret")
        self.assertEqual(error.diagnostic["motivo"], "JSON_SCHEMA")

    def test_non_json_error_preserves_fallback(self):
        response = Mock(status_code=503, headers={}, text="")
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

    def test_deprecated_model_is_substituted(self):
        model, substituted = gemini.resolve_model("gemini-2.5-flash")
        self.assertEqual(model, "gemini-4-hydrogen")
        self.assertTrue(substituted)
        model2, substituted2 = gemini.resolve_model("gemini-3.5-flash-lite")
        self.assertEqual(model2, "gemini-3.5-flash-lite")
        self.assertFalse(substituted2)

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
        resp = Mock(status_code=403, headers={}, text="Forbidden")
        resp.json.return_value = {"error": {"message": "Forbidden"}}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters"}), patch("gemini.requests.post", return_value=resp):
            with self.assertRaisesRegex(gemini.GeminiError, "HTTP 403") as caught:
                gemini.ask("test", {}, "doc")
            self.assertNotIn("test-key-with-at-least-20-characters", str(caught.exception))

    def test_transport_interactions_v1_and_store_false(self):
        response = _interaction_ok({"item": "artigo"})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters", "GEMINI_MODEL": "gemini-3.5-flash-lite"}), \
             patch("gemini.requests.post", return_value=response) as post:
            self.assertEqual(gemini.classify("documento", {"artigo": "Artigo"}), "artigo")
            url = post.call_args.args[0]
            self.assertEqual(url, gemini.INTERACTIONS_URL)
            self.assertNotIn("test-key-with-at-least-20-characters", url)
            self.assertEqual(post.call_args.kwargs["headers"]["x-goog-api-key"], "test-key-with-at-least-20-characters")
            body = post.call_args.kwargs["json"]
            self.assertIs(body["store"], False)
            self.assertEqual(body["model"], "gemini-3.5-flash-lite")
            self.assertEqual(body["input"][0]["type"], "user_input")
            self.assertEqual(body["input"][0]["content"][0]["type"], "text")
            self.assertEqual(body["response_format"]["mime_type"], "application/json")

    def test_all_64_specs_have_allowed_fields(self):
        """Garante que nenhum dos 64 itens fique com lista vazia de campos no Gemini."""
        specs = ids_especificados()
        self.assertGreaterEqual(len(specs), 60)
        for item_id in specs:
            spec = especificacao(item_id)
            var0 = spec["variantes"][0]
            allowed = gemini._select_allowed_fields(var0["campos"])
            self.assertGreater(len(allowed), 0, f"Item {item_id} sem campos habilitados para o Gemini")

    def test_fields_reject_unknown_unproven_invalid_option(self):
        rows = [{"campo": "f_ano", "valor": "2026", "trecho": "Evento em 2026"},
                {"campo": "f_nme_evento", "valor": "Inventado", "trecho": "trecho ausente"},
                {"campo": "F_FORMA", "valor": "Inválido", "trecho": "Evento em 2026"},
                {"campo": "evil", "valor": "x", "trecho": "Evento em 2026"}]
        with patch("gemini.ask", return_value={"campos": rows}):
            values, evidence = gemini.fields("Evento em 2026", especificacao("participacao_evento"), "único")
            self.assertEqual(values, {"f_ano": "2026"})
            self.assertEqual(len(evidence), 1)

    def test_fields_extract_artigo_and_grades_with_compact_prompt(self):
        doc_text = (
            "Artigo publicado na revista Nature Medicine em 2025. "
            "Título: Biomarcadores inflamatórios na COVID-19. "
            "Autores: Maria Silva, João Pedro Souza. "
            "Idioma: Português. Palavras-chave: inflamação, imunologia."
        )
        fake_response = {
            "campos": [
                {"campo": "f_titulo", "valor": "Biomarcadores inflamatórios na COVID-19", "trecho": "Biomarcadores inflamatórios na COVID-19"},
                {"campo": "f_ano", "valor": "2025", "trecho": "Nature Medicine em 2025"},
                {"campo": "F_IDIOMA", "valor": "portugues", "trecho": "Idioma: Português"},
            ],
            "autores": [
                {"nome": "Maria Silva", "trecho": "Maria Silva"},
                {"nome": "João Pedro Souza", "trecho": "João Pedro Souza"},
            ],
            "palavras_chave": ["inflamação", "imunologia"],
            "areas": ["Imunologia"],
        }
        with patch("gemini.ask", return_value=fake_response) as ask_mock:
            values, evidence = gemini.fields(doc_text, especificacao("artigo"), "Artigo completo publicado em periódico")
            # Prompt não despeja os 152 idiomas inteiros
            prompt_sent = ask_mock.call_args.args[0]
            self.assertNotIn("Abhkazian", prompt_sent)
            self.assertEqual(values["f_titulo"], "Biomarcadores inflamatórios na COVID-19")
            self.assertEqual(values["f_ano"], "2025")
            self.assertEqual(values["F_IDIOMA"], "Português")  # casado sem acento/caixa
            self.assertEqual(len(values["grade:autores"]), 2)
            self.assertEqual(values["grade:autores"][0]["citacao"], "SILVA, M.")
            self.assertEqual(values["grade:palavras_chave"], ["inflamação", "imunologia"])
            self.assertIn("Imunologia", values["grade:areas"])
            self.assertGreaterEqual(len(evidence), 5)

    def test_failure_keeps_local_form(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "completo"}), \
             patch("gemini.fields", side_effect=gemini.GeminiError("Falha simulada")):
            result = server.interpretar("participacao_evento", "Participou do Congresso em 2026.", "", "")
            self.assertIn("Falha simulada", result["generico"]["notas"])
            self.assertIn("extracted", result)

    def test_hybrid_mode_skips_fields_when_local_already_complete(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "hibrido"}), \
             patch("gemini.fields") as fields_mock:
            result = server.interpretar("participacao_evento", "Participou do Congresso em 2026.", "", "")
            fields_mock.assert_not_called()
            self.assertEqual(result["extracted"]["ano"], "2026")

    def test_success_updates_fields_and_required_fields(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "completo"}), patch("gemini.fields", return_value=(
                {"f_nme_evento": "Congresso de Biologia", "f_ano": "2026"}, ["Trecho comprovado"])):
            result = server.interpretar("participacao_evento", "Documento de participação.", "", "")
            self.assertEqual(result["extracted"]["ano"], "2026")
            self.assertEqual(result["extracted"]["titulo"], "Congresso de Biologia")
            self.assertNotIn("Ano", result["generico"]["faltam_obrigatorios"])
            self.assertIn("Trecho comprovado", result["generico"]["notas"])

    def test_deterministic_doi_is_not_overwritten_by_ai(self):
        merged = server._mescla_gemini(
            {"f_cod_doi": "10.1371/journal.pmed.0020124", "f_titulo": ""},
            {"f_cod_doi": "10.9999/errado", "f_titulo": "Título via Gemini"},
            preferir_ia=True,
        )
        self.assertEqual(merged["f_cod_doi"], "10.1371/journal.pmed.0020124")
        self.assertEqual(merged["f_titulo"], "Título via Gemini")

    def test_incomplete_output_falls_back(self):
        response = Mock(status_code=200)
        response.json.return_value = {"status": "incomplete", "steps": []}
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

    def test_completo_mode_disagreement_requires_confirmation(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "completo"}), \
             patch("gemini.classify", return_value="participacao_evento"):
            result = server.responder_evidencia(server.candidato_fixo("artigo", "local"), "Documento", "", "")
            self.assertEqual(result["classificacao"]["decisao"], "confirmar")
            self.assertEqual(result["classificacao"]["candidatos"][0]["id"], "artigo")
            self.assertNotIn("generico", result)

    def test_hybrid_mode_skips_classify_when_local_already_confident(self):
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "hibrido"}), \
             patch("gemini.classify") as classify_mock, \
             patch("gemini.fields", return_value=({}, [])):
            result = server.responder_evidencia(server.candidato_fixo("artigo", "local"), "Documento", "", "")
            classify_mock.assert_not_called()
            self.assertEqual(result["classificacao"]["decisao"], "avancar")

    def test_confirmar_preserves_both_local_candidates_when_gemini_suggests_one(self):
        cls_local = {
            "decisao": "confirmar",
            "motivo_decisao": "há mais de uma possibilidade plausível",
            "candidatos": [
                {"id": "apresentacao", "item": "Apresentação de trabalho e palestra", "secao": "Produções", "confianca": 0.8, "motivos": ["comunicação oral"], "implementado": True},
                {"id": "anais", "item": "Trabalhos publicados em anais de eventos", "secao": "Produções", "confianca": 0.76, "motivos": ["anais"], "implementado": True},
            ],
            "tambem_pode_gerar": [],
        }
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "hibrido"}), \
             patch("gemini.classify", return_value="anais"):
            result = server.responder_evidencia(cls_local, "Modalidade: Comunicação Oral. Título dos Anais do Evento.", "", "")
            ids = [c["id"] for c in result["classificacao"]["candidatos"]]
            self.assertEqual(ids, ["apresentacao", "anais"])
            self.assertIn("também sugerido pelo Gemini", result["classificacao"]["candidatos"][1]["motivos"])

    def test_429_quota_falls_back_to_next_model(self):
        quota = Mock(status_code=429, headers={}, text="Quota exceeded")
        quota.json.return_value = {"error": {"message": "Quota exceeded"}}
        ok = _interaction_ok({"item": "anais"})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters", "GEMINI_MODEL": "gemini-3.5-flash-lite"}), \
             patch("gemini.requests.post", side_effect=[quota, ok]) as post:
            self.assertEqual(gemini.classify("Anais", {"anais": "Anais"}), "anais")
            self.assertEqual(post.call_count, 2)
            self.assertEqual(post.call_args_list[1].kwargs["json"]["model"], "gemini-3.1-flash-lite")

    def test_image_uses_unified_transcribe_and_classify_without_second_classify_call(self):
        tc_out = {
            "texto": "Certificado de participação como ouvinte no Congresso em 2026",
            "item": "participacao_evento",
            "segundo_item": "nenhum",
            "motivo": "certificado de ouvinte em congresso",
        }
        with patch.dict(os.environ, {"GEMINI_ENABLED": "1", "GEMINI_MODE": "hibrido"}), \
             patch("server.extract_text_from_image_bytes") as local_ocr, \
             patch("gemini.transcribe_and_classify", return_value=tc_out) as tc_mock, \
             patch("gemini.classify") as classify_mock, \
             patch("gemini.fields", return_value=({}, [])):
            result = server.process_extract("foto.png", b"image", "Maria Silva")
            tc_mock.assert_called_once()
            self.assertEqual(tc_mock.call_args.kwargs["usuario"], "Maria Silva")
            local_ocr.assert_not_called()
            classify_mock.assert_not_called()
            self.assertIn("visualmente pelo Gemini", result["ia_aviso"])
            self.assertIn("Certificado", result["_leitura"]["texto"])

    def test_cache_and_usage_tracker_avoid_duplicate_api_calls(self):
        response = _interaction_ok({"item": "artigo"}, in_tokens=2000, out_tokens=400)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters", "GEMINI_MODEL": "gemini-3.5-flash-lite"}), \
             patch("gemini.requests.post", return_value=response) as post:
            r1 = gemini.classify("Artigo científico DOI 10.1000/abc", {"artigo": "Artigo"}, usuario="Maria Silva")
            r2 = gemini.classify("Artigo científico DOI 10.1000/abc", {"artigo": "Artigo"}, usuario="Maria Silva")
            self.assertEqual(r1, "artigo")
            self.assertEqual(r2, "artigo")
            self.assertEqual(post.call_count, 1)
            # Contexto do pesquisador foi incluído no system_instruction
            self.assertIn("Maria Silva", post.call_args.kwargs["json"]["system_instruction"])
            u = gemini.usage_stats()
            self.assertEqual(u["calls"], 1)
            self.assertEqual(u["cache_hits"], 1)
            self.assertEqual(u["input_tokens"], 2000)
            self.assertEqual(u["output_tokens"], 400)
            self.assertGreater(u["estimated_usd"], 0)

    def test_semantic_merge_refines_short_generic_local_field(self):
        merged = server._mescla_gemini(
            {"f_curso": "Psicologia", "f_cod_doi": "10.1000/abc"},
            {"f_curso": "Liga Acadêmica de Neuropsicologia – LANPSI", "f_cod_doi": "10.9999/outro"},
            preferir_ia=False,
        )
        self.assertEqual(merged["f_curso"], "Liga Acadêmica de Neuropsicologia – LANPSI")
        self.assertEqual(merged["f_cod_doi"], "10.1000/abc")

    def test_researcher_mini_profile_and_curriculum_evaluation_with_cache(self):
        cur = {
            "nome": "Aramys Silva dos Reis",
            "atualizacao": "2026-11-20",
            "perfil": {
                "areas": ["Imunologia", "Farmacologia"],
                "resumo": "Doutor em Biotecnologia pela UFMA.",
            },
            "itens": [
                {"categoria": "formacao_academica", "titulo": "Doutorado em Biotecnologia", "ano": "2018", "instituicao": "UFMA"},
                {"categoria": "atuacao_profissional", "titulo": "Professor Adjunto", "ano": "2020", "instituicao": "UFMA"},
                {"categoria": "artigo", "titulo": "Estudo sobre citocinas", "ano": "2024", "veiculo": "Nature", "doi": "10.1000/abc"},
            ],
        }
        ctx = gemini.build_researcher_context(cur)
        self.assertIn("Aramys Silva dos Reis", ctx)
        self.assertIn("UFMA", ctx)
        self.assertIn("Imunologia", ctx)
        self.assertLess(len(ctx), 400)

        fake_eval = _interaction_ok({
            "nota_geral": 86,
            "resumo_executivo": "Currículo bem estruturado com produção recente.",
            "pontos_fortes": ["Doutorado concluído", "Artigo com DOI"],
            "itens_secao_errada": [],
            "duplicatas_semanticas": [],
            "lacunas_estrategicas": [{"prioridade": "alta", "tema": "Orientações", "acao": "Registrar orientações concluídas."}],
            "sugestao_texto_inicial": "Pesquisador doutor em Biotecnologia pela UFMA com atuação em Imunologia e Farmacologia.",
        }, in_tokens=3000, out_tokens=500)

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-with-at-least-20-characters", "GEMINI_MODEL": "gemini-3.5-flash-lite"}), \
             patch("gemini.requests.post", return_value=fake_eval) as post:
            r1 = gemini.evaluate_curriculum(cur)
            r2 = gemini.evaluate_curriculum(cur)
            self.assertEqual(post.call_count, 1)
            self.assertFalse(r1["cached"])
            self.assertTrue(r2["cached"])
            self.assertEqual(r1["avaliacao"]["nota_geral"], 86)
            self.assertIn("Biotecnologia", r1["avaliacao"]["sugestao_texto_inicial"])
            self.assertEqual(r2["usage"]["cache_hits"], 1)

    def test_configure_dotenv_status_and_clear_never_expose_key(self):
        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.dict(os.environ, {}, clear=False):
            for k in ("GEMINI_API_KEY", "GEMINI_ENABLED", "GEMINI_MODEL", "GEMINI_MODE", "RENDER"):
                os.environ.pop(k, None)
            secret = "AIzaTestKeySecretValue1234567890"
            st = gemini.configure(
                api_key=secret,
                is_enabled=True,
                model="gemini-4-hydrogen",
                mode="hibrido",
                save_local=True,
                base_dir=tmpdir,
            )
            self.assertTrue(st["configured"])
            self.assertTrue(st["enabled"])
            self.assertEqual(st["key_hint"], "AIza…7890")
            self.assertNotIn(secret, json.dumps(st))
            self.assertTrue((Path(tmpdir) / ".env").is_file())

            # Limpa env e testa recarga pelo .env
            for k in ("GEMINI_API_KEY", "GEMINI_ENABLED", "GEMINI_MODEL", "GEMINI_MODE"):
                os.environ.pop(k, None)
            self.assertTrue(gemini.load_dotenv_file(tmpdir))
            self.assertEqual(os.environ["GEMINI_API_KEY"], secret)
            self.assertEqual(gemini.current_model(), "gemini-4-hydrogen")

            # Remove chave
            st2 = gemini.clear_key(remove_local=True, base_dir=tmpdir)
            self.assertFalse(st2["configured"])
            self.assertFalse(st2["enabled"])
            self.assertNotIn(secret, (Path(tmpdir) / ".env").read_text(encoding="utf-8"))

    def test_http_ia_endpoints_auth_config_test_complete_and_clear(self):
        import http.client
        import threading
        import time

        orig_code = server.ACCESS_CODE
        server.ACCESS_CODE = "codigo-teste-seguro-123"
        srv = server.ServidorUnico(("127.0.0.1", 0), server.LattesHandler)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        base = f"http://127.0.0.1:{port}"
        tok = "sess_test_token_ia_123456"
        server.SESSIONS[tok] = time.time() + 300
        hdrs = {"Cookie": f"lf_sess={tok}", "Origin": base, "Content-Type": "application/json"}
        secret = "AIzaTestEndToEndKeyValue99887766"

        def req(method, path, body=None, headers=None):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            try:
                raw = json.dumps(body).encode("utf-8") if body is not None else None
                conn.request(method, path, body=raw, headers=headers or {})
                resp = conn.getresponse()
                txt = resp.read().decode("utf-8")
                return resp.status, txt, (json.loads(txt) if txt.startswith("{") else {})
            finally:
                conn.close()

        try:
            with patch.dict(os.environ, {}, clear=False):
                for k in ("GEMINI_API_KEY", "GEMINI_ENABLED", "GEMINI_MODEL", "GEMINI_MODE"):
                    os.environ.pop(k, None)

                # Sem autenticação -> 401
                st0, _, _ = req("GET", "/api/ia/status")
                self.assertEqual(st0, 401)

                # Status autenticado
                st1, _, j1 = req("GET", "/api/ia/status", headers=hdrs)
                self.assertEqual(st1, 200)
                self.assertFalse(j1["configured"])

                # Configura chave apenas em memória (save_local=False)
                st2, txt2, j2 = req(
                    "POST",
                    "/api/ia/config",
                    body={"api_key": secret, "enabled": True, "model": "gemini-3.5-flash-lite", "mode": "hibrido", "save_local": False},
                    headers=hdrs,
                )
                self.assertEqual(st2, 200)
                self.assertTrue(j2["configured"])
                self.assertTrue(j2["enabled"])
                self.assertNotIn(secret, txt2)

                # Testa conexão
                with patch("gemini.requests.post", return_value=_interaction_ok({"item": "participacao_evento"})):
                    st3, _, j3 = req("POST", "/api/ia/testar", body={}, headers=hdrs)
                    self.assertEqual(st3, 200)
                    self.assertTrue(j3["ok"])

                # Completa campos sob demanda (preservando DOI local + extraindo autores)
                fake_fields = _interaction_ok({
                    "campos": [
                        {"campo": "f_titulo", "valor": "Estudo sobre Imunologia", "trecho": "Estudo sobre Imunologia"},
                        {"campo": "f_ano", "valor": "2026", "trecho": "em 2026"},
                    ],
                    "autores": [{"nome": "Maria Silva", "trecho": "Maria Silva"}],
                })
                with patch("gemini.requests.post", return_value=fake_fields):
                    st4, _, j4 = req(
                        "POST",
                        "/api/ia/completar",
                        body={
                            "item": "artigo",
                            "variante": "Artigo completo publicado em periódico",
                            "texto": "Artigo Estudo sobre Imunologia publicado em 2026 por Maria Silva.",
                            "valores_atuais": {"f_cod_doi": "10.1000/xyz"},
                        },
                        headers=hdrs,
                    )
                    self.assertEqual(st4, 200)
                    self.assertTrue(j4["ok"])
                    self.assertEqual(j4["generico"]["valores"]["f_titulo"], "Estudo sobre Imunologia")
                    self.assertEqual(j4["generico"]["valores"]["f_cod_doi"], "10.1000/xyz")
                    self.assertEqual(len(j4["generico"]["valores"]["grade:autores"]), 1)

                # Avalia currículo carregado na sessão (/api/ia/avaliar-curriculo)
                import hashlib
                sess_tag = hashlib.sha256(tok.encode()).hexdigest()[:16]
                server.XML_SESSAO[sess_tag] = {
                    "ts": time.time(),
                    "snap": "abc123def456",
                    "cur": {
                        "nome": "Maria Silva",
                        "perfil": {"areas": ["Imunologia"], "resumo": "Pesquisadora."},
                        "itens": [{"categoria": "artigo", "titulo": "Estudo X", "ano": "2025"}],
                    },
                }
                fake_cv = _interaction_ok({
                    "nota_geral": 80,
                    "resumo_executivo": "Boa base inicial.",
                    "pontos_fortes": ["Artigo recente"],
                    "itens_secao_errada": [],
                    "duplicatas_semanticas": [],
                    "lacunas_estrategicas": [],
                    "sugestao_texto_inicial": "Pesquisadora na área de Imunologia.",
                })
                with patch("gemini.requests.post", return_value=fake_cv):
                    st_cv, _, j_cv = req("POST", "/api/ia/avaliar-curriculo", body={}, headers=hdrs)
                    self.assertEqual(st_cv, 200)
                    self.assertTrue(j_cv["ok"])
                    self.assertEqual(j_cv["avaliacao"]["nota_geral"], 80)
                server.XML_SESSAO.pop(sess_tag, None)

                # Remove chave
                st5, _, j5 = req("DELETE", "/api/ia/chave?local=0", headers=hdrs)
                self.assertEqual(st5, 200)
                self.assertFalse(j5["configured"])
        finally:
            server.SESSIONS.pop(tok, None)
            server.ACCESS_CODE = orig_code
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
