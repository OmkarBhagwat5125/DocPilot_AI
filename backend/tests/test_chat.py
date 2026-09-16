import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from groq import AsyncGroq

from backend.app.core.config import settings
from backend.app.services.chat import ChatService, ChatServiceError


class ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        with patch.object(settings, "GROQ_API_KEY", ""):
            self.service = ChatService()
        self.chunks = [{"source": "sample.txt", "page_number": 1, "text": "Hello"}]

    async def test_missing_key_is_service_error(self):
        with self.assertRaises(ChatServiceError) as error:
            await self.service.generate_answer("Hello?", self.chunks)
        self.assertEqual(error.exception.status_code, 503)
        self.assertIn("GROQ_API_KEY", str(error.exception))

    async def test_empty_context_needs_no_provider(self):
        result = await self.service.generate_answer("Hello?", [])
        self.assertEqual(result["sources"], [])
        self.assertIn("couldn't find", result["answer"])

    async def test_invalid_key_is_not_retried_or_returned_as_answer(self):
        requests = []

        def reject(request):
            requests.append(request)
            return httpx.Response(401, json={"error": {"message": "private provider detail"}})

        async with AsyncGroq(
            api_key="test-only", max_retries=2,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(reject)),
        ) as client:
            self.service.client = client
            with self.assertRaises(ChatServiceError) as error:
                await self.service.generate_answer("Hello?", self.chunks)
        self.assertEqual(len(requests), 1)
        self.assertEqual(error.exception.status_code, 503)
        self.assertIn("Replace GROQ_API_KEY", str(error.exception))
        self.assertNotIn("private provider detail", str(error.exception))

    async def test_rate_limit_and_provider_failure_statuses(self):
        for provider_status, expected_status in [(429, 429), (500, 502), (400, 502)]:
            with self.subTest(provider_status=provider_status):
                async with AsyncGroq(
                    api_key="test-only", max_retries=0,
                    http_client=httpx.AsyncClient(transport=httpx.MockTransport(
                        lambda request: httpx.Response(provider_status, json={"error": {"message": "failed"}})
                    )),
                ) as client:
                    self.service.client = client
                    with self.assertRaises(ChatServiceError) as error:
                        await self.service.generate_answer("Hello?", self.chunks)
                self.assertEqual(error.exception.status_code, expected_status)

    async def test_success_preserves_answer_and_unique_sources(self):
        self.service.client = object()
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Hello!"))])
        self.service._call_groq_api = AsyncMock(return_value=response)
        result = await self.service.generate_answer("Hello?", self.chunks * 2)
        self.assertEqual(result, {
            "answer": "Hello!",
            "sources": [{"source": "sample.txt", "page_number": 1}],
        })


if __name__ == "__main__":
    unittest.main()
