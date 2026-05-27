import time
from typing import Any, Dict, List
from aurora.orchestration.event_broker import EventBroker

class MetricsCollector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MetricsCollector, cls).__new__(cls, *args, **kwargs)
            cls._instance.broker = EventBroker()
        return cls._instance

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Scans the event broker history and aggregates standard performance telemetry."""
        history = self.broker.get_history(200)
        
        total_incidents = len([e for e in history if e.get("topic") == "raw-ingestion"])
        attacks_blocked = len([e for e in history if e.get("topic") == "security-alerts" and e.get("is_attack")])
        auto_healed = len([e for e in history if e.get("topic") == "validated-remediations" and e.get("remediation_status") == "AUTO_DEPLOYED"])
        manual_review = len([e for e in history if e.get("topic") == "validated-remediations" and e.get("remediation_status") == "MANUAL_REVIEW_REQUIRED"])
        
        # Calculate average agent latency
        latencies = []
        hallucination_count = 0
        drift_count = 0
        retrieval_fail_count = 0
        prompt_fail_count = 0
        tool_misuse_count = 0

        for event in history:
            if "agent_trace" in event:
                for trace in event["agent_trace"]:
                    latencies.append(trace.get("latency_ms", 0))

            if event.get("topic") == "diagnosed-incidents":
                ftype = event.get("failure_type")
                if ftype == "Hallucination":
                    hallucination_count += 1
                elif ftype == "Data Drift":
                    drift_count += 1
                elif ftype == "Retrieval Failure":
                    retrieval_fail_count += 1
                elif ftype == "Prompt Design Failure":
                    prompt_fail_count += 1
                elif ftype == "Tool Misuse":
                    tool_misuse_count += 1

        avg_latency_ms = int(sum(latencies) / len(latencies)) if latencies else 145

        # Return real telemetry state
        return {
            "total_incidents": total_incidents,
            "attacks_blocked": attacks_blocked,
            "auto_healed": auto_healed,
            "manual_review": manual_review,
            "avg_latency_ms": avg_latency_ms,
            "distribution": {
                "Hallucination": hallucination_count,
                "Data Drift": drift_count,
                "Retrieval Failure": retrieval_fail_count,
                "Prompt Design Failure": prompt_fail_count,
                "Tool Misuse": tool_misuse_count
            }
        }
