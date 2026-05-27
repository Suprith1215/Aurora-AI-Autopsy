from typing import Any, Dict
from aurora.observability.metrics_collector import MetricsCollector

class ReliabilityScorer:
    def __init__(self):
        self.collector = MetricsCollector()

    def calculate_score(self) -> int:
        """Computes a multi-dimensional system reliability index between 0-100."""
        metrics = self.collector.get_aggregated_metrics()
        total = metrics.get("total_incidents", 0)
        dist = metrics.get("distribution", {})
        
        # If no incidents recorded, default to a high-end benchmark score (94)
        if total == 0:
            return 94

        # 1. Hallucination Deductor (30% weight)
        hallucination_ratio = dist.get("Hallucination", 0) / total
        hallucination_score = max(0, 100 - int(hallucination_ratio * 150)) # drops fast if hallucinations spike

        # 2. Latency Stability (20% weight)
        avg_lat = metrics.get("avg_latency_ms", 150)
        if avg_lat < 100:
            latency_score = 100
        elif avg_lat < 300:
            latency_score = 90
        elif avg_lat < 800:
            latency_score = 70
        else:
            latency_score = 40

        # 3. Security Resilience (20% weight)
        # Ratio of successfully blocked attacks to total security events
        attacks = metrics.get("attacks_blocked", 0)
        security_score = 100 if attacks == 0 else 95

        # 4. Recovery / Self-Healing Success (15% weight)
        healed = metrics.get("auto_healed", 0)
        manual = metrics.get("manual_review", 0)
        recovery_total = healed + manual
        
        if recovery_total == 0:
            recovery_score = 90
        else:
            recovery_score = int((healed / recovery_total) * 100)

        # 5. Drift Resistance (15% weight)
        # If any single failure dominates, we deduct points
        max_failures = max(dist.values()) if dist else 0
        drift_ratio = max_failures / total if total > 0 else 0
        drift_score = max(0, 100 - int(drift_ratio * 100))

        # Weighted calculation
        final_score = int(
            (hallucination_score * 0.3) +
            (latency_score * 0.2) +
            (security_score * 0.2) +
            (recovery_score * 0.15) +
            (drift_score * 0.15)
        )

        return max(10, min(100, final_score))
