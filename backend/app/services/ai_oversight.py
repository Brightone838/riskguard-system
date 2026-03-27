from typing import Dict, Any, List
from datetime import datetime
import re

class AIOversightService:
    def __init__(self):
        self.ai_action_log = []
        self.sensitive_patterns = [
            r'export.*data',
            r'share.*credentials',
            r'grant.*access',
            r'delete.*record',
            r'modify.*permission',
            r'bypass.*security',
            r'disable.*monitoring',
            r'expose.*api',
            r'bulk.*download',
            r'backup.*all'
        ]
        
        self.critical_keywords = [
            'admin', 'root', 'all users', 'everyone',
            'public', 'unrestricted', 'full access',
            'disable', 'bypass', 'override'
        ]
    
    def analyze_ai_output(self, ai_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = 0
        risk_factors = []
        sensitive_matches = []
        
        for pattern in self.sensitive_patterns:
            if re.search(pattern, ai_output.lower()):
                risk_score += 20
                risk_factors.append(f"Sensitive action suggested: {pattern}")
                sensitive_matches.append(pattern)
        
        for keyword in self.critical_keywords:
            if keyword.lower() in ai_output.lower():
                risk_score += 15
                risk_factors.append(f"Critical keyword detected: {keyword}")
        
        if risk_score >= 70:
            risk_level = "CRITICAL"
            action = "BLOCK_IMMEDIATELY"
        elif risk_score >= 40:
            risk_level = "HIGH"
            action = "REQUIRE_VERIFICATION"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
            action = "FLAG_FOR_REVIEW"
        else:
            risk_level = "LOW"
            action = "ALLOW"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ai_output": ai_output[:200],
            "context": context,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "action_taken": action
        }
        self.ai_action_log.append(log_entry)
        
        return {
            "ai_output_analyzed": True,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "sensitive_patterns_detected": sensitive_matches,
            "recommended_action": action,
            "requires_human_review": risk_score >= 40,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_ai_audit_log(self, limit: int = 50) -> List[Dict]:
        return self.ai_action_log[-limit:]

ai_oversight = AIOversightService()