from pathlib import Path
import json
import re
from langchain_ollama import OllamaLLM

# ---------------- LLM ----------------
llm = OllamaLLM(model="llama3")

# ---------------- PATHS ----------------
FAILURE_DIR = Path("data/failures")
OUTPUT_DIR = Path("data/classifications")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- SEVERITY (NUMERIC) ----------------
SEVERITY_SCORE = {
    "Hallucination": 5,
    "Data Drift": 4,
    "Retrieval Failure": 3,
    "Prompt Design Failure": 2,
    "Tool Misuse": 1
}

# ---------------- PROMPT ----------------
SYSTEM_PROMPT = """
You are an AI reliability engineer.

Classify the AI failure into ONE category:
- Hallucination
- Data Drift
- Retrieval Failure
- Prompt Design Failure
- Tool Misuse

Return ONLY valid JSON.
"""

# ---------------- JSON EXTRACTOR ----------------
def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group())

# ---------------- SCHEMA VALIDATION ----------------
REQUIRED_FIELDS = {
    "incident_id": str,
    "failure_type": str,
    "confidence": (int, float),
    "recommended_fix": str
}

def validate_schema(obj: dict):
    for key, t in REQUIRED_FIELDS.items():
        if key not in obj:
            raise ValueError(f"Missing field: {key}")
        if not isinstance(obj[key], t):
            raise ValueError(f"Invalid type for {key}")

# ---------------- MAIN ----------------
for file in FAILURE_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    prompt = f"""
{SYSTEM_PROMPT}

Incident ID: {file.stem}

Failure Description:
{text}

JSON format:
{{
  "incident_id": "{file.stem}",
  "failure_type": "",
  "confidence": 0.0,
  "recommended_fix": ""
}}
"""

    response = llm.invoke(prompt)

    try:
        parsed = extract_json(response)
        validate_schema(parsed)
    except Exception as e:
        print(f"\n⚠️ Skipping {file.stem} — invalid output")
        print(e)
        continue

    # ---------------- ENRICH ----------------
    parsed["severity_score"] = SEVERITY_SCORE.get(parsed["failure_type"], 1)

    output_file = OUTPUT_DIR / f"{file.stem}.json"
    output_file.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

    print(f"\nSaved: {output_file.name}")
