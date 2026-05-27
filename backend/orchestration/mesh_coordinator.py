import asyncio
import time
from typing import Any, Dict, List
from aurora.orchestration.event_broker import EventBroker
from aurora.agents.observer import ObserverAgent
from aurora.agents.security import SecurityAgent
from aurora.agents.autopsy import AutopsyAgent
from aurora.agents.retrieval import RetrievalAgent
from aurora.agents.repair import RepairAgent
from aurora.agents.validation import ValidationAgent
from aurora.agents.drift import DriftAgent
from aurora.agents.governance import GovernanceAgent

class MeshCoordinator:
    def __init__(self):
        self.broker = EventBroker()
        
        # Instantiate all agents
        self.observer = ObserverAgent()
        self.security = SecurityAgent()
        self.autopsy = AutopsyAgent()
        self.retrieval = RetrievalAgent()
        self.repair = RepairAgent()
        self.validation = ValidationAgent()
        self.drift = DriftAgent()
        self.governance = GovernanceAgent()

        self._setup_subscribers()

    def _setup_subscribers(self):
        """Wires agent topic chains: raw-ingestion -> raw-logs -> security-alerts -> diagnosed-incidents -> enriched-incidents -> remediation-tasks -> validated-remediations -> drift-reports -> final-compliance-reports"""
        self.broker.clear_subscribers()
        
        # Helper to route callbacks asynchronously
        def make_handler(agent, next_topic):
            async def handle(event):
                # Measure latency and run agent processing
                start_time = time.time()
                result = await agent.process(event)
                latency = time.time() - start_time
                
                if result:
                    # Enrich payload with agent tracing metadata
                    result["agent_trace"] = event.get("agent_trace", []) + [{
                        "agent": agent.name,
                        "latency_ms": int(latency * 1000),
                        "timestamp": time.time()
                    }]
                    await self.broker.publish(next_topic, result)
            return handle

        # Setup standard sequential pipeline
        self.broker.subscribe("raw-ingestion", make_handler(self.observer, "raw-logs"))
        self.broker.subscribe("raw-logs", make_handler(self.security, "security-alerts"))
        self.broker.subscribe("security-alerts", make_handler(self.autopsy, "diagnosed-incidents"))
        self.broker.subscribe("diagnosed-incidents", make_handler(self.retrieval, "enriched-incidents"))
        self.broker.subscribe("enriched-incidents", make_handler(self.repair, "remediation-tasks"))
        self.broker.subscribe("remediation-tasks", make_handler(self.validation, "validated-remediations"))
        self.broker.subscribe("validated-remediations", make_handler(self.drift, "drift-reports"))
        self.broker.subscribe("drift-reports", make_handler(self.governance, "final-compliance-reports"))

    async def ingest_failure(self, description: str, model: str = "GPT-REPORTER-PRO", incident_id: str = None) -> Dict[str, Any]:
        """Entrypoint to submit a failure vector into the agentic reliability mesh."""
        payload = {
            "description": description,
            "model": model,
            "timestamp": time.time()
        }
        if incident_id:
            payload["incident_id"] = incident_id

        # Publish starting event
        await self.broker.publish("raw-ingestion", payload)
        
        # A short sleep to allow the async chain to process completely
        await asyncio.sleep(0.5)
        
        # Find the final audit report in broker history
        history = self.broker.get_history(20)
        for event in reversed(history):
            if event.get("topic") == "final-compliance-reports" and (incident_id is None or event.get("incident_id") == incident_id):
                return event
        return {}
