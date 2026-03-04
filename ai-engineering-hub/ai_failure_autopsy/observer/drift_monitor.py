import json
from pathlib import Path
from collections import Counter
import subprocess
import sys

DATA_DIR = Path("data/classifications")

files = list(DATA_DIR.glob("*.json"))

if not files:
    print("No classification data yet.")
    sys.exit(0)

types = []

for file in files:
    with open(file) as f:
        data = json.load(f)
        types.append(data["failure_type"])

counts = Counter(types)

print("\n==============================")
print("Failure Drift Monitor Report")
print("==============================")

for k, v in counts.items():
    print(f"{k}: {v}")

dominant, dominant_count = counts.most_common(1)[0]
ratio = dominant_count / len(types)

print("\n------------------------------")
print(f"Dominant Failure Type: {dominant}")
print(f"Ratio: {dominant_count}/{len(types)}")

if ratio > 0.6:
    print("⚠️  Drift detected → triggering self-healing")
    subprocess.run(
        [sys.executable, "ai_failure_autopsy/self_healing/repair_engine.py"],
        check=True
    )
else:
    print("✅ No significant drift detected")
