import json
import time
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("d:/ai-reliability-project/ai-engineering-hub/ai_failure_autopsy/data/classifications")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEVERITY_SCORE_MAP = {
    "Hallucination": 5,
    "Data Drift": 4,
    "Retrieval Failure": 3,
    "Prompt Design Failure": 2,
    "Tool Misuse": 1
}

TEST_CASES = [
    {
        "failure_type": "Hallucination",
        "confidence": 0.92,
        "recommended_fix": "Implement strict grounding checks against the technical documentation database.",
        "description": "The model is hallucinating technical specifications for a 'Quantum-Core V5' product that doesn't exist."
    },
    {
        "failure_type": "Data Drift",
        "confidence": 0.88,
        "recommended_fix": "Retrain embedding model on recent financial data and adjust similarity thresholds.",
        "description": "Semantic drift monitor shows a 0.7 drop in embedding similarity for finance queries."
    },
    {
        "failure_type": "Retrieval Failure",
        "confidence": 0.95,
        "recommended_fix": "Optimize vector index partitioning and increase timeout for retrieval nodes.",
        "description": "Retrieval latency spiked by 400% after vector index update."
    },
    {
        "failure_type": "Prompt Design Failure",
        "confidence": 0.85,
        "recommended_fix": "Refine system prompt to clearly separate instructions from user input blocks.",
        "description": "Agent is repeating prompt instructions instead of executing SQL query."
    },
    {
        "failure_type": "Tool Misuse",
        "confidence": 0.90,
        "recommended_fix": "Update tool schema validation logic and add pre-invocation JSON parsing filters.",
        "description": "Model attempted to call 'delete_user' tool with raw string input instead of JSON."
    }
]

def seed():
    for i, case in enumerate(TEST_CASES):
        new_id = f"static_case_{i}_{int(time.time())}"
        case.update({
            "incident_id": new_id,
            "model": "STATIC-SEEDER-v1",
            "timestamp": datetime.now().timestamp() - (i * 3600), # staggered timestamps
            "severity_score": SEVERITY_SCORE_MAP.get(case["failure_type"], 3)
        })
        (DATA_DIR / f"{new_id}.json").write_text(json.dumps(case, indent=2))
        print(f"Generated {new_id}.json")

if __name__ == "__main__":
    seed()
