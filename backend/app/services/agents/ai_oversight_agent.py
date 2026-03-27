from typing import Dict, Any, List
from datetime import datetime
import re

class AIOversightAgent:
    """
    Agent 3: Monitors and validates AI decisions (YOUR UNIQUE FEATURE!)
    This addresses the critical weakness in CyberSentry AI
    """
    def __init__(self):
        self.ai_decisions_log = []
        self.risky_patterns = [
            (r'disable.*security', 50, "AI trying to disable security"),
            (r'bypass.*verification', 45, "AI attempting to bypass verification"),
            (r'grant.*admin.*access', 40, "AI granting admin access"),
            (r'expose.*(data|api)', 35, "AI exposing data"),
            (r'ignore.*alert', 30, "AI ignoring security alerts"),
            (r'allow.*all', 25, "AI allowing unrestricted access"),
            (r'quick.*fix', 15, "AI suggesting quick fix without verification"),
        ]
    
    def validate_ai_decision(self, ai_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI decision before execution"""
        risk_score = 0
        risk_factors = []
        requires_verification = False
        
        # Check for risky patterns
        for pattern, score, description in self.risky_patterns:
            if re.search(pattern, ai_output.lower()):
                risk_score += score
                risk_factors.append(description)
        
        # Additional checks
        if "export" in ai_output.lower() and "all" in ai_output.lower():
            risk_score += 20
            risk_factors.append("Attempting to export all data")
        
        if "public" in ai_output.lower():
            risk_score += 25
            risk_factors.append("Suggesting public exposure")
        
        # Determine action
        if risk_score >= 70:
            action = "BLOCK"
            requires_verification = True
            requires_approval = 2
        elif risk_score >= 40:
            action = "REQUIRE_VERIFICATION"
            requires_verification = True
            requires_approval = 1
        elif risk_score >= 20:
            action = "FLAG"
            requires_verification = False
            requires_approval = 0
        else:
            action = "ALLOW"
            requires_verification = False
            requires_approval = 0
        
        # Log decision
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "ai_output": ai_output[:200],
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "action": action,
            "requires_verification": requires_verification,
            "requires_approval": requires_approval
        }
        self.ai_decisions_log.append(decision_log)
        
        return {
            "validated": True,
            "risk_score": risk_score,
            "risk_level": "CRITICAL" if risk_score >= 70 else "HIGH" if risk_score >= 40 else "MEDIUM" if risk_score >= 20 else "LOW",
            "risk_factors": risk_factors,
            "action": action,
            "requires_verification": requires_verification,
            "requires_approval": requires_approval,
            "recommendations": self._get_recommendations(risk_score)
        }
    
    def _get_recommendations(self, risk_score: int) -> List[str]:
        """Get recommendations based on risk score"""
        recommendations = []
        if risk_score >= 70:
            recommendations.append("🚨 IMMEDIATE BLOCK: AI decision requires 2+ approvals")
            recommendations.append("📢 Send alert to security team")
            recommendations.append("🔒 Lock AI agent for review")
        elif risk_score >= 40:
            recommendations.append("⚠️ Require human verification before execution")
            recommendations.append("📝 Log for security audit")
        elif risk_score >= 20:
            recommendations.append("👁️ Flag for review")
        return recommendations
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get AI decision audit log"""
        return self.ai_decisions_log[-limit:]

ai_oversight_agent = AIOversightAgent()