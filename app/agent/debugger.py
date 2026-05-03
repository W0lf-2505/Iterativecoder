import os
from app.llm.agent_llm import AgentLLM


class DebuggerLLM:

    def __init__(self):
        self.llm = AgentLLM("debugger.txt")

        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "llm",
            "prompts",
            "debugger.txt"
        )

        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    def generate(self, error_message = str):

        prompt = f"""
    Error:
    {error_message}

    """

        return self.llm.generate_action(prompt)