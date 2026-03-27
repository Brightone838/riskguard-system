from typing import Dict, Any, List
from datetime import datetime
import json

class MonitorAgent:
    """
    Agent 1: Monitors all user activities and system events
    """
    def __init__(self):
        self.activity_stream = []
        self.user_sessions = {}
    
    def track_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Track and record user activity"""
        tracked_activity = {
            "timestamp": datetime.now().isoformat(),
            "user_id": activity.get("user_id"),
            "action": activity.get("action"),
            "login_attempts": activity.get("login_attempts", 0),
            "records_accessed": activity.get("records_accessed", 0),
            "authenticated": activity.get("authenticated", True),
            "hour": activity.get("hour", datetime.now().hour),
            "session_id": self._get_or_create_session(activity.get("user_id"))
        }
        
        self.activity_stream.append(tracked_activity)
        
        # Keep only last 10,000 activities
        if len(self.activity_stream) > 10000:
            self.activity_stream = self.activity_stream[-10000:]
        
        return tracked_activity
    
    def _get_or_create_session(self, user_id: str) -> str:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "session_id": f"session_{user_id}_{datetime.now().timestamp()}",
                "start_time": datetime.now().isoformat(),
                "activity_count": 0
            }
        
        self.user_sessions[user_id]["activity_count"] += 1
        return self.user_sessions[user_id]["session_id"]
    
    def get_user_behavior(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user behavior history"""
        return [a for a in self.activity_stream if a["user_id"] == user_id][-limit:]

monitor_agent = MonitorAgent()