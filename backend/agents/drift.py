import logging
from typing import Any, Dict, Optional
from aurora.agents.base import BaseAgent

class DriftAgent(BaseAgent):
    def __init__(self):
        super().__init__("DriftAgent")
        self.incident_history = []

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Monitors system-wide distributions of failure vectors to isolate model decay."""
        if event.get("topic") != "validated-remediations":
            return None

        failure_type = event.get("failure_type")
        self.incident_history.append(failure_type)

        # Keep last 20 events for statistical drift monitoring
        if len(self.incident_history) > 20:
            self.incident_history.pop(0)

        # Calculate ratios
        drift_detected = False
        dominant_type = "None"
        ratio = 0.0

        if len(self.incident_history) >= 3:
            counts = {}
            for t in self.incident_history:
                counts[t] = counts.get(t, 0) + 1
            
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            dominant_type, count = sorted_counts[0]
            ratio = count / len(self.incident_history)
            
            if ratio >= 0.6:  # 60% threshold
                drift_detected = True

        drift_payload = dict(event)
        drift_payload.update({
            "topic": "drift-reports",
            "drift_detected": drift_detected,
            "dominant_failure": dominant_type,
            "drift_ratio": ratio,
            "sample_size": len(self.incident_history)
        })

        if drift_detected:
            self.logger.warning(f"DRIFT DETECTED: {dominant_type} dominates ({ratio*100:.1f}%)! Deploying remedial self-healing.")
        else:
            self.logger.info(f"System distribution healthy. Dominant vector: {dominant_type} ({ratio*100:.1f}%)")

        return drift_payload
