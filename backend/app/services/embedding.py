import logging
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = None

    def _get_model(self) -> TextEmbedding:
        if self.model is None:
            logger.info("Initializing FastEmbed TextEmbedding model (BAAI/bge-small-en-v1.5)...")
            # This will download the model automatically on first call
            self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("FastEmbed model initialized successfully.")
        return self.model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            model = self._get_model()
            embeddings_gen = model.embed(texts)
            return [emb.tolist() for emb in embeddings_gen]
        except Exception as e:
            logger.error(f"Error generating embeddings for texts: {str(e)}")
            raise e

    def embed_query(self, query: str) -> list[float]:
        try:
            model = self._get_model()
            embeddings_gen = model.embed([query])
            embeddings = list(embeddings_gen)
            if embeddings:
                return embeddings[0].tolist()
            else:
                raise ValueError("No embedding generated for query")
        except Exception as e:
            logger.error(f"Error generating embedding for query: {str(e)}")
            raise e

embedding_service = EmbeddingService()
