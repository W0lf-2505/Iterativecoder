import os
from app.llm.ollama_client import OllamaClient


class AgentLLM:

    def __init__(self, prompt_file: str):
        self.client = OllamaClient()

        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            prompt_file
        )

        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    def generate_action(self, user_input: str) -> str:
        prompt = f"""
{self.system_prompt}

{user_input}
"""
        return self.client.generate(prompt)