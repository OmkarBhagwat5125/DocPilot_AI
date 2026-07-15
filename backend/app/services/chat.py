import logging
from groq import Groq
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        if self.api_key:
            logger.info("Configuring Groq API client...")
            self.client = Groq(api_key=self.api_key)
            logger.info(f"Groq API client configured successfully. Model: {self.model_name}")
        else:
            logger.warning("GROQ_API_KEY is not set. Chat requests will fail.")
            self.client = None

    def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        if not self.client:
            return {
                "answer": "Error: Groq API key is missing. Please add GROQ_API_KEY to your .env file.",
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
            logger.info(f"Sending prompt to Groq API using model '{self.model_name}' for question: '{question[:50]}...'")
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
            )
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
        except Exception as e:
            logger.error(f"Error generating answer from Groq: {str(e)}")
            return {
                "answer": f"An error occurred while contacting the Groq API: {str(e)}",
                "sources": []
            }

chat_service = ChatService()
