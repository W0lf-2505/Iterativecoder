import json
from app.llm.agent_llm import AgentLLM


class Replanner:

    def __init__(self):
        self.llm = AgentLLM("planner.txt")

    
    def extract_json(self,text: str):
        """
        Extract the FIRST valid JSON object from LLM output safely
        """

        start = text.find("{")
        if start == -1:
            raise ValueError(f"No JSON start found:\n{text}")

        brace_count = 0

        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1

            if brace_count == 0:
                json_str = text[start:i+1]
                return json.loads(json_str)

        raise ValueError(f"Incomplete JSON in output:\n{text}")

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

        return self.extract_json(output)