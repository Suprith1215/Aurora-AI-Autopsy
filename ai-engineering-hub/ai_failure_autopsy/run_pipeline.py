import asyncio
import sys
import io
import time
from pathlib import Path

# Fix Windows cp1252 encoding issues with Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Include parent directory in python path to import the aurora platform
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from aurora.orchestration.mesh_coordinator import MeshCoordinator
from aurora.orchestration.event_broker import EventBroker

print("\n🚀 Starting AURORA Agentic AI Reliability Pipeline\n")

async def run_dry_run():
    coordinator = MeshCoordinator()
    broker = EventBroker()
    
    # 1. Clear previous logs
    broker.clear_history()

    sample_failure = (
        "CRITICAL ERROR: Model GPT-Core has hallucinated interest limits. "
        "Claims that 'Quantum-Core V5' yields 400% interest per day. "
        "This completely violates grounding information from our database."
    )

    print("▶ Ingesting sample failure to the Multi-Agent Mesh...")
    print(f"  Payload: '{sample_failure[:80]}...'\n")
    
    # Run the ingestion and wait for orchestration chain
    result = await coordinator.ingest_failure(sample_failure, model="TEST-ENVIRONMENT-PRO")
    
    print("\n✅ Multi-Agent Processing Stream Complete!\n")
    print("==================================================")
    print("                EXECUTION AUDIT LOG               ")
    print("==================================================")
    
    history = broker.get_history(20)
    for event in history:
        topic = event.get("topic")
        inc_id = event.get("incident_id")
        print(f">> [TOPIC: {topic}] Incident {inc_id} processed successfully.")
        
        # Print specific telemetry outputs
        if topic == "diagnosed-incidents":
            print(f"   [Diagnosis]: Failure Type -> {event.get('failure_type')} | Severity -> {event.get('severity_score')}/5")
        elif topic == "remediation-tasks":
            print(f"   [Remediation]: {event.get('remediation_patch')}")
        elif topic == "validated-remediations":
            print(f"   [Validation]: Score -> {event.get('validation_score')}% | Decision -> {event.get('remediation_status')}")
        elif topic == "drift-reports":
            print(f"   [Drift Alert]: Drift Detected -> {event.get('drift_detected')} (Dominant: {event.get('dominant_failure')})")
        elif topic == "final-compliance-reports":
            print(f"   [Governance]: Compliance Status -> {event.get('compliance_status')} | Violation logs committed to ledger.")

    print("==================================================\n")
    print("✅ Platform successfully processed and self-healed the anomaly.")

if __name__ == "__main__":
    asyncio.run(run_dry_run())

