from typing import Any, Dict, Optional
from aurora.agents.base import BaseAgent

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__("SecurityAgent")

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scans the event for prompt injections, jailbreaks, or safety violations."""
        if event.get("topic") != "raw-logs":
            return None

        description = event.get("description", "")
        if not description:
            return None

        # Check for injection vectors
        desc_lower = description.lower()
        threat_level = "LOW"
        detected_vectors = []
        is_attack = False

        injection_signatures = [
            "ignore previous instructions",
            "system override",
            "you are now a",
            "dan mode",
            "do anything now",
            "bypass safety",
            "devmode",
            "sudo",
            "rm -rf",
            "select * from",
            "<script>"
        ]

        for signature in injection_signatures:
            if signature in desc_lower:
                detected_vectors.append(signature)
                is_attack = True

        if is_attack:
            threat_level = "CRITICAL" if len(detected_vectors) > 1 or "override" in desc_lower else "HIGH"

        alert = {
            "topic": "security-alerts",
            "incident_id": event.get("incident_id"),
            "description": description,
            "is_attack": is_attack,
            "threat_level": threat_level,
            "detected_vectors": detected_vectors,
            "model": event.get("model", "Core-LLM-v4"),
            "timestamp": event.get("timestamp")
        }
        
        self.logger.info(f"Scan complete. Threat Level: {threat_level}. Attack: {is_attack}")
        return alert
