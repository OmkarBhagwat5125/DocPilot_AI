import logging
import google.generativeai as genai
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            logger.info("Configuring Gemini API client...")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Gemini API client configured successfully.")
        else:
            logger.warning("GEMINI_API_KEY is not set. Chat requests will fail.")
            self.model = None

    def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        if not self.model:
            return {
                "answer": "Error: Gemini API key is missing. Please add GEMINI_API_KEY to your .env file.",
                "sources": []
            }
            
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": []
            }

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
        
        prompt = (
            f"{system_instruction}\n\n"
            f"DOCUMENT CONTEXT:\n"
            f"{context_text}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"AI RESPONSE:"
        )
        
        try:
            logger.info(f"Sending prompt to Gemini API for question: '{question[:50]}...'")
            response = self.model.generate_content(prompt)
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
        except Exception as e:
            logger.error(f"Error generating answer from Gemini: {str(e)}")
            return {
                "answer": f"An error occurred while contacting the Gemini API: {str(e)}",
                "sources": []
            }

chat_service = ChatService()
