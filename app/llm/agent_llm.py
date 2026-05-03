import os
from app.llm.ollama_client import OllamaClient
from app.tools.registry import ToolRegistry


class AgentLLM:

    def __init__(self, prompt_file: str):
        self.client = OllamaClient()
        self.registry = ToolRegistry()

        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            prompt_file.replace("{{ registered_tools }}",self.registry.get_tools_prompt())
        )

        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    def generate_action(self, user_input: str) -> str:
        prompt = f"""
{self.system_prompt}

{user_input}
"""
        return self.client.generate(prompt)