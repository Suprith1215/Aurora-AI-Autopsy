import os
import time
from typing import Any, Dict, Optional
from pathlib import Path
from aurora.agents.base import BaseAgent

class GovernanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("GovernanceAgent")
        self.ledger_file = Path("data/governance_audit.log")
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)

    async def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verifies policy compliance, performs PII scanning, and appends to the immutable audit log."""
        if event.get("topic") != "drift-reports":
            return None

        description = event.get("description", "")
        remediation = event.get("remediation_patch", "")
        
        # Simulated safety validation and PII check
        has_pii = any(k in description.lower() for k in ["ssn", "password", "credit card", "social security"])
        compliance_status = "COMPLIANT"
        violations = []

        if has_pii:
            compliance_status = "NON-COMPLIANT"
            violations.append("PII Leak Risk Detected in logs")
            
        if len(remediation) < 10:
            compliance_status = "WARNING"
            violations.append("Remediation patch description too short/weak")

        # Commit to audit ledger
        audit_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] INCIDENT: {event.get('incident_id')} | " \
                      f"FAILURE: {event.get('failure_type')} | " \
                      f"SEVERITY: {event.get('severity_score')}/5 | " \
                      f"REMEDIATION: {event.get('remediation_status')} | " \
                      f"COMPLIANCE: {compliance_status} | " \
                      f"VIOLATIONS: {', '.join(violations) if violations else 'None'}\n"
                      
        try:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(audit_entry)
        except Exception as e:
            self.logger.error(f"Failed to append to governance audit ledger: {e}")

        governed_event = dict(event)
        governed_event.update({
            "topic": "final-compliance-reports",
            "compliance_status": compliance_status,
            "compliance_violations": violations
        })

        self.logger.info(f"Audit log committed. Status: {compliance_status}")
        return governed_event
