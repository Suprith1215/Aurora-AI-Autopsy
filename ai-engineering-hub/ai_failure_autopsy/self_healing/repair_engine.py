from pathlib import Path
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

FAILURE_DIR = Path("data/failures")
OUTPUT_DIR = Path("data/repairs")
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPT = """
You are an AI reliability engineer.

Propose a concrete repair to prevent this failure.
Be specific and actionable.
"""

for file in FAILURE_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    response = llm.invoke(f"{PROMPT}\n\n{text}")

    out = OUTPUT_DIR / file.name
    out.write_text(response, encoding="utf-8")

    print("\n==============================")
    print(f"Repair saved for: {file.name}")
    print(response)
