import json
from app.llm.agent_llm import AgentLLM


class Replanner:

    def __init__(self):
        self.llm = AgentLLM("planner.txt")

    def replan(self, goal: str, state, failed_step: str, error: str):
        """
        Generate a new plan based on failure + history
        """

        context = f"""
Goal:
{goal}

Execution history:
{state.get_history_text()}

Failed step:
{failed_step}

Error:
{error}

Your task:
- Analyze why the step failed
- Fix the issue
- Provide a new plan starting from current state

Return ONLY JSON:

{{
  "plan": [
    {{
      "step": 1,
      "description": "..."
    }}
  ]
}}
"""

        output = self.llm.generate_action(context)

        return json.loads(output)