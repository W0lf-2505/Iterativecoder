# app/agent/planner.py

from app.llm.agent_llm import AgentLLM
import json

import re
import json


def extract_json(text: str):
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

class Planner:

    def __init__(self):
        self.llm = AgentLLM("planner.txt")

    def create_plan(self, goal: str, state):
        context = f"""
        Goal:
        {goal}

        Previous execution history:
        {state.get_history_text()}
        """

        output = self.llm.generate_action(context)

        return extract_json(output)