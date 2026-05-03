import requests
from app.llm.base import BaseLLM
from dotenv import load_dotenv
import os

load_dotenv()


class OllamaClient(BaseLLM):

    def __init__(self, model="mistral"):
        self.model = os.getenv("MODEL") or model
        
        self.url = os.getenv("OLLAMA_URL")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]