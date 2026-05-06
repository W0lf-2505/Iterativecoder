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
            
    def format_history(self, history):
        lines = []
        for h in history:
            try:
                lines.append(
                    f"Step: {h['step_description']}\n"
                    f"Action: {h['action']['action']}\n"
                    f"Result: {h['result']['status']}\n"
                )
            except Exception:
                continue
        return "\n".join(lines)

    def generate_action(self, goal: str, step: str, state):
        history = self.format_history(state.execution_history[-5:])
        context = f"""
{self.system_prompt}
Goal: {goal}

Current Project: {state.project}

Previous Goals:
{state.goal_history[-3:]}

Recent Steps:
{history}

Error If any:
{state.last_error}

Current Step:
{step}

Return ONE valid JSON action.
"""

        return self.llm.generate_action(context)