from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.activity import Activity
import statistics

class AdvancedAnalytics:
    def __init__(self):
        self.baselines = {}
    
    def calculate_user_baseline(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Calculate baseline for a user"""
        activities = db.query(Activity).filter(
            Activity.user_id == user_id
        ).order_by(Activity.created_at.desc()).limit(50).all()
        
        if len(activities) < 3:
            return {"error": "Insufficient data for baseline", "sample_size": len(activities)}
        
        # Calculate metrics
        login_attempts = [a.login_attempts for a in activities]
        records_accessed = [a.records_accessed for a in activities]
        hours = [a.hour for a in activities]
        
        baseline = {
            "user_id": user_id,
            "sample_size": len(activities),
            "avg_login_attempts": sum(login_attempts) / len(login_attempts),
            "avg_records_accessed": sum(records_accessed) / len(records_accessed),
            "typical_hours": max(set(hours), key=hours.count) if hours else 12
        }
        
        self.baselines[user_id] = baseline
        return baseline
    
    def detect_anomalies(self, db: Session, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in activity"""
        user_id = data.get("user_id")
        anomalies = []
        anomaly_score = 0
        
        # Get baseline if available
        baseline = None
        if user_id:
            if user_id not in self.baselines:
                baseline = self.calculate_user_baseline(db, user_id)
            else:
                baseline = self.baselines[user_id]
        
        # Simple anomaly detection (rule-based for now)
        login_attempts = data.get("login_attempts", 0)
        if login_attempts > 5:
            anomalies.append(f"High login attempts: {login_attempts}")
            anomaly_score += 30
        
        records = data.get("records_accessed", 0)
        if records > 100:
            anomalies.append(f"High data access: {records} records")
            anomaly_score += 40
        
        if data.get("authenticated") is False:
            anomalies.append("Failed authentication")
            anomaly_score += 30
        
        hour = data.get("hour", 12)
        if hour < 6 or hour > 22:
            anomalies.append(f"Unusual time: {hour}:00")
            anomaly_score += 20
        
        # Compare with baseline if available and no error
        if baseline and "error" not in baseline:
            # Check if login attempts are significantly higher than baseline
            if login_attempts > baseline.get("avg_login_attempts", 0) * 3:
                anomalies.append(f"Login attempts {login_attempts}x above normal")
                anomaly_score += 25
            
            # Check if records accessed are significantly higher
            if records > baseline.get("avg_records_accessed", 0) * 5:
                anomalies.append(f"Data access spike: {records} records")
                anomaly_score += 35
        
        return {
            "anomalies": anomalies,
            "anomaly_score": min(anomaly_score, 100)
        }
    
    def predict_risk_trend(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Predict risk trend"""
        activities = db.query(Activity).filter(
            Activity.user_id == user_id
        ).order_by(Activity.created_at).all()
        
        if len(activities) < 3:
            return {"error": "Insufficient data for trend prediction"}
        
        return {
            "user_id": user_id,
            "trend": "stable",
            "message": "More data needed for accurate prediction"
        }
    
    def detect_patterns(self, db: Session, user_id: str = None) -> Dict[str, Any]:
        """Detect attack patterns"""
        patterns = {
            "brute_force_attempts": [],
            "data_exfiltration": []
        }
        
        query = db.query(Activity)
        if user_id:
            query = query.filter(Activity.user_id == user_id)
        
        activities = query.all()
        
        # Group by user
        user_activities = {}
        for activity in activities:
            if activity.user_id not in user_activities:
                user_activities[activity.user_id] = []
            user_activities[activity.user_id].append(activity)
        
        # Detect brute force (multiple failed attempts)
        for uid, acts in user_activities.items():
            failed_count = sum(1 for a in acts if not a.authenticated)
            if failed_count >= 3:
                patterns["brute_force_attempts"].append({
                    "user_id": uid,
                    "failed_attempts": failed_count,
                    "timeframe": "historical"
                })
            
            # Detect data exfiltration (high records access)
            high_access = [a for a in acts if a.records_accessed > 100]
            if high_access:
                patterns["data_exfiltration"].append({
                    "user_id": uid,
                    "suspicious_activities": len(high_access),
                    "total_records": sum(a.records_accessed for a in high_access)
                })
        
        return patterns

advanced_analytics = AdvancedAnalytics()