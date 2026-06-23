import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from resume_website_backend.chat.views import ChatProviderError, get_history_key


CHAT_SETTINGS = {
    "ALLOWED_HOSTS": ["testserver", "localhost", "127.0.0.1"],
    "CHAT_PROVIDER": "groq",
    "GROQ_API_KEY": "test-key",
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "CHAT_MAX_MESSAGE_LENGTH": 80,
    "CHAT_MAX_HISTORY_TURNS": 4,
    "CHAT_CACHE_TTL": 3600,
    "CHAT_RATE_LIMIT_MAX_REQUESTS": 10,
    "CHAT_RATE_LIMIT_WINDOW": 60,
}


@override_settings(**CHAT_SETTINGS)
class ChatEndpointTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("resume_website_backend.chat.views.generate_groq_response", return_value="I build production AI systems.")
    def test_success_response_saves_provider_neutral_history(self, mock_generate):
        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "What do you work on?", "session_id": "session-1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["response"], "I build production AI systems.")
        self.assertEqual(payload["session_id"], "session-1")

        messages = mock_generate.call_args.args[0]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[-1], {"role": "user", "content": "What do you work on?"})

        self.assertEqual(cache.get(get_history_key("session-1")), [
            {"role": "user", "content": "What do you work on?"},
            {"role": "assistant", "content": "I build production AI systems."},
        ])

    def test_missing_groq_key_returns_fallback_without_crashing(self):
        with override_settings(GROQ_API_KEY=""):
            response = self.client.post(
                "/api/chat/",
                data=json.dumps({"message": "Tell me about Azizjon", "session_id": "session-2"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "fallback")
        self.assertEqual(payload["reason"], "not_configured")
        self.assertIn("not configured", payload["response"])

    @patch("resume_website_backend.chat.views.generate_groq_response", side_effect=ChatProviderError("quota_reached"))
    def test_quota_error_returns_limit_reached_fallback(self, mock_generate):
        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "What are your best projects?", "session_id": "session-3"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "fallback")
        self.assertEqual(payload["reason"], "quota_reached")
        self.assertIn("limit is currently reached", payload["response"])
        self.assertIsNone(cache.get(get_history_key("session-3")))
        mock_generate.assert_called_once()

    def test_empty_message_returns_400(self):
        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "   ", "session_id": "session-4"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    def test_too_long_message_returns_400(self):
        response = self.client.post(
            "/api/chat/",
            data=json.dumps({"message": "x" * 81, "session_id": "session-5"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    def test_reset_chat_clears_history_key(self):
        cache.set(get_history_key("session-6"), [{"role": "user", "content": "hello"}])

        response = self.client.post(
            "/api/reset/",
            data=json.dumps({"session_id": "session-6"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIsNone(cache.get(get_history_key("session-6")))
