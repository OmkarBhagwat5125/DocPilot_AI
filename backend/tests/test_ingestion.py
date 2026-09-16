import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.core.config import settings
from backend.app.services.document_parser import DocumentParser
from backend.app.services.embedding import EmbeddingService
from backend.app.services.ingestion import index_pages, save_upload


class IngestionTests(unittest.TestCase):
    def test_batches_preserve_text_metadata_and_write_before_next_embedding(self):
        pages = [{"text": "A sentence about a document. " * 200, "source": "sample.pdf", "page_number": 7}]
        expected = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_text(pages[0]["text"])
        events, saved = [], []

        def embed(texts):
            self.assertLessEqual(len(texts), 4)
            events.append("embed")
            return [[1.0] * 384 for _ in texts]

        def upsert(chunks, vectors, user):
            self.assertEqual(len(chunks), len(vectors))
            self.assertEqual(user, "user-1")
            events.append("write")
            saved.extend(chunks)

        count = index_pages(iter(pages), "user-1", SimpleNamespace(embed_texts=embed),
                            SimpleNamespace(upsert_chunks=upsert), 4)
        self.assertEqual(count, len(expected))
        self.assertEqual([chunk["text"] for chunk in saved], expected)
        self.assertTrue(all(c["page_number"] == 7 and c["source"] == "sample.pdf" for c in saved))
        self.assertEqual(events, ["embed", "write"] * (len(events) // 2))

    def test_empty_pages_do_not_call_model(self):
        embedder, database = Mock(), Mock()
        self.assertEqual(index_pages([], "u", embedder, database, 4), 0)
        embedder.embed_texts.assert_not_called()
        database.upsert_chunks.assert_not_called()

    def test_embedding_explicitly_limits_batch_size(self):
        service = EmbeddingService()
        model = Mock()
        model.embed.return_value = [SimpleNamespace(tolist=lambda: [0.1] * 384)]
        service.model = model
        with patch.object(settings, "EMBEDDING_BATCH_SIZE", 4):
            self.assertEqual(len(service.embed_texts(["hello"])[0]), 384)
        model.embed.assert_called_once_with(["hello"], batch_size=4, parallel=None)
        service.embed_query("question")
        model.embed.assert_called_with(["question"], batch_size=1, parallel=None)

    def test_csv_preserves_quotes_leading_zeros_and_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text('\ufeffcode,note\n001,"hello, world"\n002,\n', encoding="utf-8")
            pages = DocumentParser().parse(str(path), "sample.csv")
        self.assertEqual(pages[0]["text"], "code: 001, note: hello, world code: 002, note:")
        self.assertEqual(pages[0]["page_number"], 1)

    def test_pdf_iteration_preserves_page_numbers(self):
        import fitz
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.pdf"
            with fitz.open() as pdf:
                pdf.new_page().insert_text((72, 72), "First page")
                pdf.new_page()
                pdf.new_page().insert_text((72, 72), "Third page")
                pdf.save(path)
            pages = list(DocumentParser().iter_pages(str(path), "original.pdf"))
        self.assertEqual([p["page_number"] for p in pages], [1, 3])
        self.assertEqual([p["text"] for p in pages], ["First page", "Third page"])
        self.assertTrue(all(p["source"] == "original.pdf" for p in pages))


class UploadLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_copy_uses_bounded_reads(self):
        data = b"a" * (2 * 1024 * 1024 + 17)
        file = UploadFile(io.BytesIO(data))
        original_read = file.read
        sizes = []

        async def read(size=-1):
            sizes.append(size)
            return await original_read(size)

        file.read = read
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "upload.txt"
            await save_upload(file, dest, len(data))
            self.assertEqual(dest.read_bytes(), data)
        self.assertTrue(all(size == 1024 * 1024 for size in sizes))
        await file.close()

    async def test_oversized_upload_rejected_with_or_without_size_metadata(self):
        for declared_size in (None, 11):
            with self.subTest(declared_size=declared_size):
                file = UploadFile(io.BytesIO(b"a" * 11), size=declared_size)
                with tempfile.TemporaryDirectory() as directory:
                    dest = Path(directory) / "upload.txt"
                    with self.assertRaises(HTTPException) as error:
                        await save_upload(file, dest, 10)
                    self.assertEqual(error.exception.status_code, 413)
                await file.close()


if __name__ == "__main__":
    unittest.main()
