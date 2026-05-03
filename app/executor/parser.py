import json
import re


def extract_first_json(text: str):
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON found in:\n{text}")

    brace_count = 0

    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1

        if brace_count == 0:
            json_str = text[start:i+1]
            return json.loads(json_str)

    raise ValueError(f"Incomplete JSON in:\n{text}")


def parse_action(llm_output):
    if isinstance(llm_output, dict):
        if "action" not in llm_output:
            raise ValueError("Missing 'action' key in dict")
        return llm_output

    if isinstance(llm_output, str):
        data = extract_first_json(llm_output)

        if not isinstance(data, dict):
            raise ValueError("Expected single JSON object")

        if "action" not in data:
            raise ValueError("Missing 'action' key")

        return data

    # ❌ Anything else
    raise ValueError(f"Unsupported LLM output type: {type(llm_output)}")