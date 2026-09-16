"""Exercise real upload routing without live authentication or external services."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.core.config import settings


class UploadAPITests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

        async def current_user():
            return {"user_id": "user-1"}

        self.storage = Mock()
        self.database = Mock()
        replacements = {
            "backend.app.core.auth": SimpleNamespace(get_current_user=current_user),
            "backend.app.services.storage": SimpleNamespace(object_storage=self.storage),
            "backend.app.services.vector_db": SimpleNamespace(vector_db=self.database),
        }
        source = Path(__file__).resolve().parents[1] / "app" / "api" / "endpoints.py"
        spec = importlib.util.spec_from_file_location("upload_routes_under_test", source)
        self.routes = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", replacements):
            spec.loader.exec_module(self.routes)
        self.routes.embedding_service = Mock()
        self.routes.embedding_service.embed_texts.side_effect = lambda texts: [[0.0] * 384 for _ in texts]
        patcher = patch.object(settings, "UPLOAD_DIR", self.directory.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        app = FastAPI()
        app.include_router(self.routes.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def assert_temp_files_removed(self):
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_upload_streams_original_and_indexes(self):
        contents = b"A small document for testing."

        def capture(user, name, stream):
            self.assertEqual(user, "user-1")
            self.assertEqual(name, "sample.txt")
            self.assertEqual(stream.read(), contents)
            self.assertFalse(isinstance(stream, bytes))

        self.storage.upload_file.side_effect = capture
        response = self.client.post("/api/upload", files={"file": ("sample.txt", contents)})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["chunks_count"], 1)
        self.database.upsert_chunks.assert_called_once()
        self.assert_temp_files_removed()

    def test_empty_document_is_400_and_cleans_up(self):
        response = self.client.post("/api/upload", files={"file": ("empty.txt", b"")})
        self.assertEqual(response.status_code, 400)
        self.database.upsert_chunks.assert_not_called()
        self.assert_temp_files_removed()

    def test_oversized_document_is_413_without_storage_or_indexing(self):
        with patch.object(settings, "MAX_UPLOAD_MB", 1):
            response = self.client.post("/api/upload", files={"file": ("large.txt", b"x" * (1024 * 1024 + 1))})
        self.assertEqual(response.status_code, 413)
        self.storage.upload_file.assert_not_called()
        self.database.upsert_chunks.assert_not_called()
        self.assert_temp_files_removed()

    def test_indexing_failure_closes_page_iterator(self):
        closed = []

        def pages(*args):
            try:
                yield {"text": "x " * 2000, "source": "sample.pdf", "page_number": 1}
            finally:
                closed.append(True)

        self.routes.parser = SimpleNamespace(iter_pages=pages)
        self.database.upsert_chunks.side_effect = RuntimeError("database unavailable")
        response = self.client.post("/api/upload", files={"file": ("sample.pdf", b"fake pdf")})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(closed, [True])
        self.assert_temp_files_removed()


if __name__ == "__main__":
    unittest.main()
