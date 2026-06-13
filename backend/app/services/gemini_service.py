import google.generativeai as genai
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import asyncio

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # In 2026, gemini-2.5-flash is the stable efficient model.
        # gemini-1.5-flash is deprecated/removed.
        self.model_name = 'gemini-2.5-flash'
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_content(self, prompt: str) -> str:
        try:
            logger.info(f"Sending request to Gemini AI using model: {self.model_name}...")
            
            # Use run_in_executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            )
            
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                raise Exception("AI returned empty response")
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            # If 404, it's definitely the model name
            if "404" in str(e):
                logger.error(f"Model {self.model_name} not found. Please verify available models.")
            raise
