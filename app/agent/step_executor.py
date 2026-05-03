import os
from app.llm.agent_llm import AgentLLM


class StepExecutorLLM:

    def __init__(self):
        self.llm = AgentLLM("step_executor.txt")

        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "llm",
            "prompts",
            "step_executor.txt"
        )

        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    def generate_action(self, goal: str, step: str, state):

        context = f"""
{self.system_prompt}

Goal:
{goal}

Current Step:
{step}

Execution History:
{state.get_history_text()}
"""

        return self.llm.generate_action(context)