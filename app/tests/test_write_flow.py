from app.executor.parser import parse_action
from app.executor.validator import validate_action
from app.executor.executor import Executor

executor = Executor()

llm_output = '''
{
    "action": "write_to_file",
    "input": {
        "file_path": "test.py",
        "data": "print('hello')"
    }
}
'''

try:
    action = parse_action(llm_output)
    validated = validate_action(action)
    result = executor.execute(validated)

    print(result)

except Exception as e:
    print("Agent Error:", str(e))