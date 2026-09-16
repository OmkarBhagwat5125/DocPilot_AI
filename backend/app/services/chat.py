import logging
import google.generativeai as genai
from google.generativeai.types import generation_types
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ChatServiceError(Exception):
    """A safe, actionable error to return to the API caller."""

    def __init__(self, detail: str, status_code: int = 503):
        super().__init__(detail)
        self.status_code = status_code

class ChatService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        if self.api_key:
            logger.info("Configuring Gemini API client...")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini API client configured successfully. Model: {self.model_name}")
        else:
            logger.warning("GEMINI_API_KEY is not set. Chat requests will fail.")
            self.client = None

    async def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": []
            }

        if not self.client:
            raise ChatServiceError(
                "Gemini is not configured. Set GEMINI_API_KEY in the backend environment "
                "(the root .env file for local development), then restart the backend."
            )

        # Build context block
        context_parts = []
        for chunk in context_chunks:
            source = chunk.get("source", "Unknown")
            page = chunk.get("page_number", 1)
            text = chunk.get("text", "")
            context_parts.append(f"--- [Source: {source}, Page: {page}] ---\n{text}")
            
        context_text = "\n\n".join(context_parts)
        
        system_instruction = (
            "You are DocPilot AI, a document intelligence assistant. Answer the user's question using ONLY the provided document context below. Follow these rules strictly:\n"
            "1. Use ONLY the information from the provided context to answer.\n"
            "2. If the answer cannot be determined from the context, say: \"I couldn't find this information in the uploaded documents.\"\n"
            "3. ALWAYS cite your sources in the text using the format: [Source: filename, Page: N]\n"
            "4. Be concise, accurate, and helpful.\n"
            "5. Never make up or hallucinate information."
        )
        
        prompt = f"{system_instruction}\n\nDOCUMENT CONTEXT:\n{context_text}\n\nUSER QUESTION: {question}"
        
        try:
            logger.info(f"Sending API request to Gemini using model '{self.model_name}'...")
            response = await self.client.generate_content_async(prompt)
            answer = response.text if response.text else "No response generated."
            
            # Collate unique sources used in the retrieved context
            unique_sources = []
            seen = set()
            for chunk in context_chunks:
                src = chunk.get("source")
                pg = chunk.get("page_number", 1)
                key = (src, pg)
                if src and key not in seen:
                    seen.add(key)
                    unique_sources.append({
                        "source": src,
                        "page_number": pg
                    })
                    
            return {
                "answer": answer,
                "sources": unique_sources
            }
        except generation_types.BlockedPromptException as e:
            logger.error("Gemini blocked the prompt.")
            raise ChatServiceError("The prompt was blocked by safety settings.", 400) from e
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            if "API_KEY_INVALID" in str(e) or "401" in str(e) or "403" in str(e):
                raise ChatServiceError(
                    "Gemini rejected the backend API key. Replace GEMINI_API_KEY with a valid "
                    "key in the backend environment, then restart.", 401
                ) from e
            if "429" in str(e):
                raise ChatServiceError("Gemini's rate limit was reached. Please try again later.", 429) from e
            raise ChatServiceError("Unable to reach Gemini or complete the request. Please try again shortly.") from e

chat_service = ChatService()
