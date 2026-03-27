from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.activity import Activity

class ThreatIntelligenceService:

    def __init__(self):
        self.user_history = {}

    def analyze_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = 0
        risk_factors = []

        # Login attempts
        if data.get("login_attempts", 0) > 5:
            risk_score += 50
            risk_factors.append("Multiple login attempts")

        # Failed auth
        if not data.get("authenticated", True):
            risk_score += 30
            risk_factors.append("Failed authentication")

        # High data access
        if data.get("records_accessed", 0) > 100:
            risk_score += 40
            risk_factors.append("High data access")

        # Unusual hour
        hour = data.get("hour", 12)
        if hour < 6 or hour > 22:
            risk_score += 20
            risk_factors.append("Unusual access time")

        # Location anomaly
        if data.get("location") and data.get("usual_location"):
            if data["location"] != data["usual_location"]:
                risk_score += 25
                risk_factors.append("Location mismatch")

        # Data sensitivity
        sensitivity = data.get("data_sensitivity", "low")
        if sensitivity == "high":
            risk_score += 30
            risk_factors.append("Accessing sensitive data")
        elif sensitivity == "medium":
            risk_score += 15

        # Risk level
        if risk_score >= 100:
            level = "CRITICAL RISK"
        elif risk_score >= 70:
            level = "HIGH RISK"
        elif risk_score >= 40:
            level = "MEDIUM RISK"
        elif risk_score >= 20:
            level = "LOW RISK"
        else:
            level = "NORMAL"

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "risk_factors": risk_factors,
            "timestamp": datetime.now().isoformat()
        }

    def get_user_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        activities = db.query(Activity).filter(Activity.user_id == user_id).all()
        
        if not activities:
            return {"error": "User not found"}
        
        total_activities = len(activities)
        high_risk_count = 0
        total_records = 0
        
        for activity in activities:
            # Analyze each activity to get risk score
            data = {
                "user_id": activity.user_id,
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            analysis = self.analyze_activity(data)
            if analysis["risk_level"] in ["HIGH RISK", "CRITICAL RISK"]:
                high_risk_count += 1
            total_records += activity.records_accessed
        
        return {
            "user_id": user_id,
            "total_activities": total_activities,
            "high_risk_activities": high_risk_count,
            "risk_percentage": (high_risk_count / total_activities * 100) if total_activities > 0 else 0,
            "total_records_accessed": total_records,
            "average_records_per_session": total_records / total_activities if total_activities > 0 else 0
        }
    
    def get_system_stats(self, db: Session) -> Dict[str, Any]:
        """Get overall system statistics"""
        from sqlalchemy import func, distinct
        
        total_activities = db.query(Activity).count()
        unique_users = db.query(func.count(distinct(Activity.user_id))).scalar()
        
        # Get high risk activities
        high_risk_count = 0
        activities = db.query(Activity).all()
        
        for activity in activities:
            data = {
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            analysis = self.analyze_activity(data)
            if analysis["risk_level"] in ["HIGH RISK", "CRITICAL RISK"]:
                high_risk_count += 1
        
        return {
            "total_activities": total_activities,
            "unique_users": unique_users,
            "high_risk_activities": high_risk_count,
            "risk_percentage": (high_risk_count / total_activities * 100) if total_activities > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

threat_intelligence = ThreatIntelligenceService()

def analyze_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    return threat_intelligence.analyze_activity(data)