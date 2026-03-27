from typing import Dict, Any, List
from datetime import datetime

class AlertSystem:
    def __init__(self):
        self.alerts = []
    
    def evaluate_alert(self, analysis: Dict[str, Any], activity: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if alert should be triggered"""
        risk_score = analysis.get("risk_score", 0)
        
        alert = {
            "triggered": False,
            "severity": None,
            "message": None,
            "actions": []
        }
        
        if risk_score >= 100:
            alert["triggered"] = True
            alert["severity"] = "CRITICAL"
            alert["message"] = "🚨 CRITICAL: Security breach in progress!"
            alert["actions"] = [
                "IMMEDIATELY block user access",
                "Send emergency alert to security team",
                "Log full incident details",
                "Trigger automated response"
            ]
        elif risk_score >= 70:
            alert["triggered"] = True
            alert["severity"] = "HIGH"
            alert["message"] = "⚠️ HIGH RISK: Suspicious activity detected"
            alert["actions"] = [
                "Flag user for review",
                "Require additional verification",
                "Monitor real-time activity"
            ]
        elif risk_score >= 40:
            alert["triggered"] = True
            alert["severity"] = "MEDIUM"
            alert["message"] = "📊 MEDIUM RISK: Unusual behavior pattern"
            alert["actions"] = [
                "Log for security review",
                "Increase monitoring frequency"
            ]
        elif risk_score >= 20:
            alert["triggered"] = True
            alert["severity"] = "LOW"
            alert["message"] = "ℹ️ LOW RISK: Minor anomaly detected"
            alert["actions"] = ["Continue monitoring"]
        
        if alert["triggered"]:
            alert_record = {
                "timestamp": datetime.now().isoformat(),
                "user_id": activity.get("user_id"),
                "risk_score": risk_score,
                "severity": alert["severity"],
                "message": alert["message"],
                "actions": alert["actions"]
            }
            self.alerts.append(alert_record)
            
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
        
        return alert
    
    def get_alerts(self, severity: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        alerts = self.alerts[::-1]  # Newest first
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        
        return alerts[:limit]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        return {"message": "All alerts cleared", "cleared_count": len(self.alerts)}

alert_system = AlertSystem()