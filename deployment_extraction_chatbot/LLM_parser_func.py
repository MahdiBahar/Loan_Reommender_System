import json
import ast
import re

def clean_and_parse(raw: str) -> dict:
 
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", raw)
    cleaned = re.sub(r"\n?```", "", cleaned)

    match = re.search(r"\{[\s\S]*?\}", cleaned)
    if not match:
        raise ValueError(f"No JSON object found in LLM output:\n{raw!r}")
    js = match.group(0)

    js = re.sub(r",\s*([\}\]])", r"\1", js)
    js = js.replace("%", "")
    js = re.sub(r"(?<=\d)_(?=\d)", "", js)

    try:
        return json.loads(js)
    except Exception:
        try:
            return ast.literal_eval(js)
        except Exception as e2:
            raise ValueError(f"Error parsing extraction result: {e2}")