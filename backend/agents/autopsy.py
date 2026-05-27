import json
import re
from typing import Any, Dict, Optional
from aurora.agents.base import BaseAgent

SEVERITY_SCORE_MAP = {
    "Hallucination": 5,
    "Data Drift": 4,
    "Retrieval Failure": 3,
    "Prompt Design Failure": 2,
    "Tool Misuse": 1
}

class AutopsyAgent(BaseAgent):
    def __init__(self):
        super().__init__("AutopsyAgent")

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Diagnoses failure type and generates structural failure analysis."""
        if event.get("topic") not in ["raw-logs", "security-alerts"]:
            return None

        # If it's a security alert and flagged as attack, classify as Tool Misuse/Security failure immediately
        is_attack = event.get("is_attack", False)
        description = event.get("description", "")
        incident_id = event.get("incident_id")
        
        if is_attack:
            return {
                "topic": "diagnosed-incidents",
                "incident_id": incident_id,
                "failure_type": "Tool Misuse",
                "severity_score": 5,
                "confidence": 0.99,
                "recommended_fix": f"ALERT: Prompt Injection detected! Block user input. Attack signature: {', '.join(event.get('detected_vectors', []))}",
                "description": description,
                "model": event.get("model"),
                "timestamp": event.get("timestamp")
            }

        # Otherwise, run LLM classification or fallback
        prompt = f"""
        Classify this AI failure description into JSON with fields 'failure_type', 'confidence', 'recommended_fix'.
        Types: Hallucination, Data Drift, Retrieval Failure, Prompt Design Failure, Tool Misuse.
        Input failure description: {description}
        """
        
        response = self.run_llm(prompt, system_prompt="You are an expert AI reliability engineer. Respond ONLY in valid JSON.")
        
        # Parse JSON
        parsed = {}
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
        except Exception:
            parsed = {}

        # Fallback to rule-based parser if LLM output fails
        if not parsed or "failure_type" not in parsed:
            desc_lower = description.lower()
            if any(w in desc_lower for w in ["hallucin", "phantom", "fabricat", "invent", "made up", "doesn't exist"]):
                failure_type = "Hallucination"
                confidence = 0.91
                fix = "Deploy grounding filters and fact-verification layers before response delivery."
            elif any(w in desc_lower for w in ["drift", "shift", "semantic", "embedding", "distribut", "covariate"]):
                failure_type = "Data Drift"
                confidence = 0.87
                fix = "Re-index the vector store with recent data. Schedule weekly embedding drift checks."
            elif any(w in desc_lower for w in ["retriev", "latency", "timeout", "fetch", "vector", "index", "search"]):
                failure_type = "Retrieval Failure"
                confidence = 0.85
                fix = "Rebuild the vector index and add query caching."
            elif any(w in desc_lower for w in ["prompt", "instruct", "loopback", "repeat", "template", "format", "sql", "query"]):
                failure_type = "Prompt Design Failure"
                confidence = 0.83
                fix = "Refactor prompt templates to include explicit output format constraints."
            elif any(w in desc_lower for w in ["tool", "function", "call", "schema", "json", "api", "misuse", "delete", "invalid"]):
                failure_type = "Tool Misuse"
                confidence = 0.82
                fix = "Enforce strict JSON schema validation on all tool inputs."
            else:
                failure_type = "Hallucination"
                confidence = 0.75
                fix = "Review model grounding, strengthen context injection, and add output validation guardrails."

            parsed = {
                "failure_type": failure_type,
                "confidence": confidence,
                "recommended_fix": fix
            }

        # Enrich and output
        parsed.update({
            "topic": "diagnosed-incidents",
            "incident_id": incident_id,
            "description": description,
            "model": event.get("model"),
            "timestamp": event.get("timestamp"),
            "severity_score": SEVERITY_SCORE_MAP.get(parsed.get("failure_type", "Hallucination"), 3)
        })

        self.logger.info(f"Diagnosis completed: {parsed['failure_type']} (Severity: {parsed['severity_score']})")
        return parsed
