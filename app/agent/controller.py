# app/agent/controller.py

from app.executor.executor import Executor
from app.executor.validator import validate_action
from app.agent.planner import Planner
from app.agent.state import AgentState
from app.agent.replanner import Replanner
from app.agent.step_executor import StepExecutorLLM
from app.executor.parser import parse_action
from datetime import datetime


class Controller:

    def __init__(self):
        self.executor = Executor()
        self.planner = Planner()
        self.state = AgentState()
        self.replanner = Replanner()
        self.step_llm = StepExecutorLLM()


    def _init_project(self):
        if not self.state.project:
            now = datetime.now()
            self.state.project = f"demo_project_{now.strftime('%Y%m%d_%H%M%S_%f')}"

    def run(self, goal: str, max_retries=5):

        self.state.goal = goal
        self._init_project()
        self.retry_count = 0

        # Step 1: Get plan
        plan = self.planner.create_plan(goal, self.state)

        while True:
            print("PLAN:", plan)
            # Step 2: Execute plan step-by-step
            for step in plan["plan"]:

                description = step["description"]
                print(f"\n➡ STEP: {description}")


                # Parse JSON
                action = self.generate_valid_action(description)
                if "project" not in action["input"] or not action["input"]["project"]:
                    action["input"]["project"] = self.state.project
                
                if "project" in action["input"] or action["input"]["project"]:
                    self.state.project = action["input"]["project"]

                if isinstance(action, list):
                    raise ValueError("Multiple actions returned — invalid step execution")


                # Validate
                validated = validate_action(action)
                
                # Inject previous outputs if needed (e.g.,
                input_data = action.get("input", {})

                if input_data.get("data") == "USE_PREVIOUS_STDOUT":
                    input_data["data"] = self.state.last_output

                if input_data.get("data") == "USE_PREVIOUS_STDERR":
                    input_data["data"] = self.state.last_error

                if "<use previous stdout>" in input_data.get("data", ""):
                    input_data["data"] = self.state.last_output

                # Execute
                result = self.executor.execute(validated)

                print("RESULT:", result)

                if result["status"] == "error" and self.retry_count <= max_retries:
                    print("Step failed → Replanning...")

                    self.retry_count += 1
                    new_plan = self.replanner.replan(
                        goal=self.state.goal,
                        state=self.state,
                        failed_step=description,
                        error=result["error"]["message"]
                    )

                    print("NEW PLAN:", new_plan)

                    plan = new_plan["plan"]
                    break
                    
                else:

                    # Store output in state
                    self.state.add_step(
                        step_description=description,
                        action=action,
                        result=result
                    )

            print("\n Plan completed")
            return

    def generate_valid_action(self, description):

        for _ in range(2):  # retry twice

            llm_output = self.step_llm.generate_action(
                goal=self.state.goal,
                step=description,
                state=self.state
            )

            try:
                print(llm_output)
                return parse_action(llm_output)
            except Exception as e:
                print("Retry due to bad LLM output:", e)

        raise ValueError("Failed to get valid action from LLM")