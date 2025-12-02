import os
import logging
from typing import List, Optional
from .llm import LLMClient

logger = logging.getLogger(__name__)

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except ImportError:
            logger.error("openai package not installed. Please install it with `pip install openai`.")
            raise

    def complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code optimization assistant."},
                    {"role": "user", "content": prompt}
                ],
                stop=stop,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return ""

class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
        except ImportError:
            logger.error("google-generativeai package not installed. Please install it with `pip install google-generativeai`.")
            raise

    def complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            # Gemini's stop_sequences are passed in generation_config
            generation_config = {}
            if stop:
                generation_config["stop_sequences"] = stop
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return ""
