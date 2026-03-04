import subprocess
import sys
from pathlib import Path

print("\n🚀 Starting AI Reliability Pipeline\n")

steps = [
    "ai_failure_autopsy/core_rag/rag_service.py",
    "ai_failure_autopsy/failure_classifier/classifier.py",
    "ai_failure_autopsy/observer/drift_monitor.py"
]

for step in steps:
    print(f"▶ Running {Path(step).resolve()}")
    subprocess.run([sys.executable, step], check=False)


print("\n✅ Pipeline completed successfully")
