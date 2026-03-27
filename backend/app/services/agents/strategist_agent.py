from typing import Dict, Any, List
from datetime import datetime, timedelta

class StrategistAgent:
    """
    Agent 6: Analyzes patterns and suggests improvements
    """
    def __init__(self):
        self.learning_log = []
        self.threat_patterns = {}
    
    def analyze_patterns(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns and suggest improvements"""
        insights = []
        
        # Group by user
        user_activity = {}
        for activity in activities:
            user_id = activity.get("user_id")
            if user_id not in user_activity:
                user_activity[user_id] = []
            user_activity[user_id].append(activity)
        
        # Find high-risk users
        for user_id, acts in user_activity.items():
            risky_acts = [a for a in acts if self._is_risky(a)]
            if len(risky_acts) > 3:
                insights.append({
                    "type": "HIGH_RISK_USER",
                    "user_id": user_id,
                    "risky_activities": len(risky_acts),
                    "recommendation": "Review user access permissions"
                })
        
        # Time-based patterns
        night_activities = [a for a in activities if a.get("hour", 12) < 6 or a.get("hour", 12) > 22]
        if len(night_activities) > len(activities) * 0.3:
            insights.append({
                "type": "UNUSUAL_PATTERN",
                "description": f"High night activity: {len(night_activities)} activities",
                "recommendation": "Implement time-based access controls"
            })
        
        return {
            "insights": insights,
            "total_analyzed": len(activities),
            "timestamp": datetime.now().isoformat()
        }
    
    def _is_risky(self, activity: Dict[str, Any]) -> bool:
        """Determine if activity is risky"""
        return (
            activity.get("login_attempts", 0) > 3 or
            activity.get("records_accessed", 0) > 100 or
            activity.get("authenticated") is False
        )
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights"""
        return {
            "threat_patterns": self.threat_patterns,
            "recommendations": [
                "Enable multi-factor authentication for high-risk users",
                "Review night-time access patterns",
                "Implement automated response for critical threats"
            ]
        }

strategist_agent = StrategistAgent()