import time
from typing import Any, Dict, List

class SecurityGuardrails:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SecurityGuardrails, cls).__new__(cls, *args, **kwargs)
            cls._instance.blocked_payloads = []
        return cls._instance

    def scan_input(self, user_input: str) -> Dict[str, Any]:
        """Scans the user prompt against known attack signatures and returns a security report."""
        user_input_lower = user_input.lower()
        
        signatures = {
            "jailbreak": [
                "ignore previous instructions",
                "system override",
                "dan mode",
                "bypass safety rules",
                "you are now an unrestricted",
                "do anything now"
            ],
            "injection": [
                "sql inject",
                "select * from",
                "drop table",
                "<script>",
                "javascript:",
                "exec("
            ],
            "api_abuse": [
                "delete_user",
                "admin_escalate",
                "grant_permissions",
                "system_root"
            ]
        }

        matched_signatures = []
        attack_type = "None"
        is_blocked = False
        threat_level = "LOW"
        risk_score = 10

        # Run scans
        for category, list_of_sigs in signatures.items():
            for sig in list_of_sigs:
                if sig in user_input_lower:
                    matched_signatures.append(sig)
                    attack_type = category.upper()
                    is_blocked = True
                    
        if is_blocked:
            risk_score = 75 + (len(matched_signatures) * 5)
            risk_score = min(99, risk_score)
            threat_level = "CRITICAL" if risk_score > 85 else "HIGH"
            
            # Log the blocked attempt
            record = {
                "timestamp": time.time(),
                "payload": user_input[:200] + ("..." if len(user_input) > 200 else ""),
                "attack_type": attack_type,
                "threat_level": threat_level,
                "risk_score": risk_score,
                "blocked_signatures": matched_signatures
            }
            self.blocked_payloads.append(record)
            if len(self.blocked_payloads) > 50:
                self.blocked_payloads.pop(0)

        return {
            "is_blocked": is_blocked,
            "threat_level": threat_level,
            "risk_score": risk_score,
            "attack_type": attack_type,
            "matched_signatures": matched_signatures
        }

    def get_blocked_payloads(self) -> List[Dict[str, Any]]:
        """Returns log history of all blocked attacks."""
        return self.blocked_payloads
