import json
import ast
import re

# Define the Function to Parse the LLM Output

# def parse_extraction_result(result_str: str) -> dict:
#     """
#     Extract the dictionary from the LLM output.
#     First, find the substring between the first '{' and the last '}'.
#     Then try to parse that substring as JSON.
#     If that fails (for example, due to single quotes), fall back to ast.literal_eval.
#     """
#     start = result_str.find('{')
#     end = result_str.rfind('}') + 1
#     if start == -1 or end == -1:
#         raise ValueError("No JSON object found in the output.")
#     json_str = result_str[start:end]
#     try:
#         return json.loads(json_str)
#     except Exception:
#         try:
#             return ast.literal_eval(json_str)
#         except Exception as e2:
#             raise ValueError(f"Error parsing extraction result: {e2}")




# import re
# import json

def clean_and_parse(raw: str) -> dict:
    # 1) Strip any markdown fences (``` or ```json)
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", raw)
    cleaned = re.sub(r"\n?```", "", cleaned)

    # 2) Now isolate the first {...} block in the remaining text
    match = re.search(r"\{[\s\S]*?\}", cleaned)
    if not match:
        raise ValueError(f"No JSON object found in LLM output:\n{raw!r}")
    js = match.group(0)

    # 3) Cleanup common issues:
    #    - trailing commas before a closing brace/bracket
    #    - percent signs
    #    - underscores in numbers
    js = re.sub(r",\s*([\}\]])", r"\1", js)
    js = js.replace("%", "")
    js = re.sub(r"(?<=\d)_(?=\d)", "", js)

    # 4) Finally, parse
    # return json.loads(js)
    try:
        return json.loads(js)
    except Exception:
        try:
            return ast.literal_eval(js)
        except Exception as e2:
            raise ValueError(f"Error parsing extraction result: {e2}")