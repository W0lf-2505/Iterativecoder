from app.executor.executor import Executor
from app.executor.validator import validate_action
from app.agent.planner import Planner
from app.agent.state import AgentState
from app.agent.replanner import Replanner
from app.agent.step_executor import StepExecutorLLM
from app.agent.debugger import DebuggerLLM
from app.agent.summarizer import SummarizerLLM
from app.executor.parser import parse_action
from datetime import datetime
import json


class Controller:

    def __init__(self):
        self.executor = Executor()
        self.planner = Planner()
        self.state = AgentState()
        self.replanner = Replanner()
        self.step_llm = StepExecutorLLM()
        self.debuggerllm = DebuggerLLM()
        self.summaryllm = SummarizerLLM()
        self.retry_count = 0

        # NEW: persistence
        if not hasattr(self.state, "goal_history"):
            self.state.goal_history = []

    def is_repeating(self, action):
        history = self.state.execution_history

        if len(history) < 1:
            return False

        last = history[-1]

        last_action = last["action"]["action"]
        last_input = last["action"].get("input", {})
        last_result = last["result"].get("output", {}).get("stdout", "")

        curr_action = action.get("action")
        curr_input = action.get("input", {})

        # same tool?
        if last_action != curr_action:
            return False

        # ---- FILE READ CASE ----
        if curr_action == "read_from_file":
            return last_input.get("file_path") == curr_input.get("file_path")

        # ---- DIRECTORY LIST CASE ----
        if curr_action == "list_files_in_directory":
            return last_result == "[]"  # repeating empty listing

        # ---- COMMAND CASE ----
        if curr_action == "run_command":
            return last_input.get("command") == curr_input.get("command")

        # ---- DEFAULT ----
        return last_input == curr_input

    def enforce_tool_priority(self, step_desc, action):
        desc = step_desc.lower()
        tool = action.get("action")

        if tool == "run_command":
            if any(word in desc for word in [
                "read", "write", "create", "update", "modify", "file"
            ]):
                # Auto-correct instead of breaking
                if "read" in desc:
                    action["action"] = "read_from_file"
                else:
                    action["action"] = "write_to_file"

        return action
        # ------------------------
    # INIT PROJECT (PERSISTENT)
    # ------------------------
    def _init_project(self):
        if not self.state.project:
            now = datetime.now()
            self.state.project = f"demo_project_{now.strftime('%Y%m%d_%H%M%S_%f')}"

    # ------------------------
    # ROUTING
    # ------------------------
    def route_input(self, goal: str) -> str:
        goal_lower = goal.lower()

        if any(word in goal_lower for word in [
            "create", "build", "write", "run", "fix", "implement", "add", "modify"
        ]):
            return "agent"

        if any(word in goal_lower for word in [
            "what is", "explain", "who is", "search", "find"
        ]):
            return "search"

        return "agent"

    def route(self, goal):
        route = self.route_input(goal)
        return "reasoning" if route == "search" else "planning"

    # ------------------------
    # MAIN RUN (PERSISTENT SESSION)
    # ------------------------
    def run(self, goal: str, max_retries=5, callback=None):

        # Persist goals
        self.state.current_goal = goal
        self.state.goal_history.append(goal)

        # Ensure project exists
        self._init_project()
        self.retry_count = 0

        def log(msg):
            print(msg)
            if callback:
                callback(msg)

        route = self.route(goal)

        # ======================
        # PLANNING FLOW
        # ======================
        if route == "planning":

            plan = self.planner.create_plan(goal, self.state)
            log(f"PLAN: {json.dumps({'plan': plan['plan']})}")

            while True:
                success_flag = True
                try:
                    for step in plan["plan"]:

                        description = step["description"]
                        log(f"STEP: {description}")

                        for _ in range(5):

                            # Generate action
                            action = self.generate_valid_action(description)
                            if action["action"] == "finish_step":
                                log("NEXT STEP")
                                break
                            if self.is_repeating(action):
                                log("Detected repeated action → forcing step completion")
                                break

                            # Inject project
                            if not action["input"].get("project"):
                                action["input"]["project"] = self.state.project

                            # Keep project updated
                            self.state.project = action["input"]["project"]

                            if isinstance(action, list):
                                raise ValueError("Multiple actions returned — invalid")

                            # Validate
                            validated = validate_action(action)

                            # Inject previous outputs
                            input_data = action.get("input", {})

                            if input_data.get("data") in ["USE_PREVIOUS_STDOUT", "<use previous stdout>"]:
                                input_data["data"] = self.state.last_output

                            if input_data.get("data") in ["USE_PREVIOUS_STDERR", "<use previous stderr>"]:
                                input_data["data"] = self.state.last_error
                            self.state.last_error = None
                            # Execute
                            result = self.executor.execute(validated)

                            log(f"RESULT: {json.dumps(result)}")

                            # Store step
                            self.state.add_step(
                                step_description=description,
                                action=action,
                                result=result
                            )
                            # Handle failure
                            if result["status"] == "error":
                                print(result)
                                if result["error"]["type"] == "TypeError":
                                    self.state.last_error = result["error"]["message"]

                                else:
                                    if self.retry_count >= max_retries:
                                        log("Max retries reached")
                                        return

                                    self.retry_count += 1

                                    log("Step failed → Replanning...")

                                    new_plan = self.replanner.replan(
                                        goal=self.state.current_goal,
                                        state=self.state,
                                        failed_step=description,
                                        error=result["error"]["message"]
                                    )

                                    plan = new_plan
                                    log(f"NEW PLAN: {json.dumps({'plan': plan['plan']})}")
                                    success_flag = False
                                    raise Exception("step_failed")

                            # else:
                            #     break    
                

                        
                
                    if success_flag:
                        log("PLAN COMPLETED")
                        return
                
                except Exception as e:
                    print("AFSDADDDDDDDDDDDDDDDDDDD")
                    print(e)
                    if str(e) == "step_failed":
                        log("Step failed → Replanning...")
                        break


        # ======================
        # REASONING FLOW
        # ======================
        if route == "reasoning":

            # Direct tool call (no planner)
            action = {
                "action": "search_web",
                "input": {
                    "project": self.state.project,
                    "query": goal,
                }
            }

            validated = validate_action(action)
            result = self.executor.execute(validated)

            # If tool failed → fallback summarizer
            if result["status"] == "error":
                try:
                    summary = self.summaryllm.generate_action(
                        goal,
                        result["input"].get("results", "")
                    )
                    log(f"Summary: {summary}")
                except Exception as e:
                    log(f"Summary failed: {str(e)}")

            else:
                log(f"Summary: {json.dumps(result)}")

    # ------------------------
    # ACTION GENERATION
    # ------------------------
    def generate_valid_action(self, description):

        for _ in range(2):
            llm_output = self.step_llm.generate_action(
                goal=self.state.current_goal,
                step=description,
                state=self.state
            )

            try:
                return parse_action(llm_output)
            except Exception as e:
                print("Retry due to bad LLM output:", e)

        raise ValueError("Failed to get valid action from LLM")

    # ------------------------
    # DEBUGGING
    # ------------------------
    def analyze_error(self, error_message: str):
        return self.debuggerllm.generate(error_message)