# app/agent/state.py

from typing import List, Dict, Any


class AgentState:

    def __init__(self):
        self.goal: str = ""
        self.project: str = None
        self.last_output: str = ""
        self.last_error = "" 

        # 🔥 Core addition
        self.execution_history: List[Dict[str, Any]] = []

    # =========================
    # RECORD STEP
    # =========================

    def add_step(self, step_description: str, action: dict, result: dict):
        self.execution_history.append({
            "step": step_description,
            "action": action,
            "result": result
        })

        # update last output
        output = result.get("output", {})

        self.last_output = output.get("stdout", "") or ""
        self.last_error = output.get("stderr", "") or ""

    # =========================
    # FORMAT HISTORY (FOR LLM)
    # =========================

    def get_history_text(self) -> str:
        history_text = ""

        for i, entry in enumerate(self.execution_history):
            history_text += f"""
Step {i+1}:
Description: {entry['step']}
Action: {entry['action']}
Result: {entry['result']['status']}
Output: {entry['result']['output']['stdout']}
"""

        return history_text.strip()