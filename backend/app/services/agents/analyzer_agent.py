from typing import Dict, Any, List
import statistics

class AnalyzerAgent:
    """
    Agent 2: Analyzes behavior and detects anomalies using ML-like logic
    """
    def __init__(self):
        self.user_baselines = {}
        self.anomaly_threshold = 2.0  # Standard deviations
    
    def analyze_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single activity for anomalies"""
        user_id = activity.get("user_id")
        anomaly_score = 0
        anomalies = []
        
        # Get or create baseline
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = {
                "login_attempts": [],
                "records_accessed": [],
                "hours": []
            }
        
        baseline = self.user_baselines[user_id]
        
        # Update baseline with new activity
        baseline["login_attempts"].append(activity.get("login_attempts", 0))
        baseline["records_accessed"].append(activity.get("records_accessed", 0))
        baseline["hours"].append(activity.get("hour", 12))
        
        # Keep only last 100 activities
        for key in baseline:
            if len(baseline[key]) > 100:
                baseline[key] = baseline[key][-100:]
        
        # Check for anomalies
        if len(baseline["login_attempts"]) > 10:
            avg_attempts = statistics.mean(baseline["login_attempts"])
            std_attempts = statistics.stdev(baseline["login_attempts"]) if len(baseline["login_attempts"]) > 1 else 1
            
            if activity.get("login_attempts", 0) > avg_attempts + (std_attempts * self.anomaly_threshold):
                anomaly_score += 30
                anomalies.append(f"Login attempts {activity.get('login_attempts')} above baseline")
        
        if len(baseline["records_accessed"]) > 10:
            avg_records = statistics.mean(baseline["records_accessed"])
            std_records = statistics.stdev(baseline["records_accessed"]) if len(baseline["records_accessed"]) > 1 else 1
            
            if activity.get("records_accessed", 0) > avg_records + (std_records * self.anomaly_threshold):
                anomaly_score += 40
                anomalies.append(f"Records accessed {activity.get('records_accessed')} above baseline")
        
        return {
            "anomaly_score": min(anomaly_score, 100),
            "anomalies": anomalies,
            "requires_investigation": anomaly_score >= 50
        }

analyzer_agent = AnalyzerAgent()