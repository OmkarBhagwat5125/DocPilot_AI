import logging
from groq import AsyncGroq, APIConnectionError, APIStatusError, AuthenticationError, RateLimitError
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ChatServiceError(Exception):
    """A safe, actionable error to return to the API caller."""

    def __init__(self, detail: str, status_code: int = 503):
        super().__init__(detail)
        self.status_code = status_code

class ChatService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        if self.api_key:
            logger.info("Configuring Groq API client...")
            # The SDK retries transient failures, but never invalid credentials.
            self.client = AsyncGroq(api_key=self.api_key, timeout=30.0, max_retries=2)
            logger.info(f"Groq API client configured successfully. Model: {self.model_name}")
        else:
            logger.warning("GROQ_API_KEY is not set. Chat requests will fail.")
            self.client = None

    async def _call_groq_api(self, messages: list) -> any:
        logger.info(f"Sending API request to Groq using model '{self.model_name}'...")
        return await self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )

    async def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": []
            }

        if not self.client:
            raise ChatServiceError(
                "Groq is not configured. Set GROQ_API_KEY in the backend environment "
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
        
        messages = [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": f"DOCUMENT CONTEXT:\n{context_text}\n\nUSER QUESTION: {question}"
            }
        ]
        
        try:
            response = await self._call_groq_api(messages)
            answer = response.choices[0].message.content if response.choices and response.choices[0].message.content else "No response generated."
            
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
        except AuthenticationError as e:
            logger.error("Groq rejected the configured API key (401).")
            raise ChatServiceError(
                "Groq rejected the backend API key. Replace GROQ_API_KEY with a valid "
                "key in the backend environment (the root .env file locally), then "
                "restart or redeploy the backend."
            ) from e
        except RateLimitError as e:
            raise ChatServiceError("Groq's rate limit was reached. Please try again later.", 429) from e
        except APIConnectionError as e:
            raise ChatServiceError("Unable to reach Groq. Please try again shortly.") from e
        except APIStatusError as e:
            logger.error("Groq request failed with status %s", e.status_code)
            raise ChatServiceError(
                "Groq could not complete the request. Check the backend GROQ_MODEL "
                "setting and provider availability.", 502
            ) from e

chat_service = ChatService()

