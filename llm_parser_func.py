import json
import ast


# Define the Function to Parse the LLM Output

def parse_extraction_result(result_str: str) -> dict:
    """
    Extract the dictionary from the LLM output.
    First, find the substring between the first '{' and the last '}'.
    Then try to parse that substring as JSON.
    If that fails (for example, due to single quotes), fall back to ast.literal_eval.
    """
    start = result_str.find('{')
    end = result_str.rfind('}') + 1
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in the output.")
    json_str = result_str[start:end]
    try:
        return json.loads(json_str)
    except Exception:
        try:
            return ast.literal_eval(json_str)
        except Exception as e2:
            raise ValueError(f"Error parsing extraction result: {e2}")
