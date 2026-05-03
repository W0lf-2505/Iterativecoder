from app.llm.agent_llm import AgentLLM
from app.executor.parser import parse_action
from app.executor.validator import validate_action
from app.executor.executor import Executor

llm = AgentLLM("coder.txt")
executor = Executor()

user_input = "create a python file that prints hello"

# 1. LLM → JSON string
llm_output = llm.generate_action(user_input)

print("LLM RAW:", llm_output)

# 2. Parse
action = parse_action(llm_output)

# 3. Validate
validated = validate_action(action)

# 4. Execute
result = executor.execute(validated)

print("RESULT:", result)