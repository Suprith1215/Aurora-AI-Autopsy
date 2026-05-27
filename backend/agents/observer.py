import time
from typing import Any, Dict, Optional
from aurora.agents.base import BaseAgent

class ObserverAgent(BaseAgent):
    def __init__(self):
        super().__init__("ObserverAgent")

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ingests raw inputs or simulated failures and parses them into standardized incidents."""
        if event.get("topic") != "raw-ingestion":
            return None

        description = event.get("description", "")
        model = event.get("model", "Core-LLM-v4")
        timestamp = event.get("timestamp", time.time())
        incident_id = event.get("incident_id", f"incid_{int(timestamp)}_{int(time.time() % 1000)}")

        self.logger.info(f"Ingested raw event. Created incident {incident_id}")

        return {
            "topic": "raw-logs",
            "incident_id": incident_id,
            "description": description,
            "model": model,
            "timestamp": timestamp
        }
