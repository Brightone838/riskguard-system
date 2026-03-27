from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import asyncio
import threading
import time

class RealtimeMonitor:
    def __init__(self, max_history=1000):
        self.activity_stream = deque(maxlen=max_history)
        self.risk_stream = deque(maxlen=max_history)
        self.anomaly_stream = deque(maxlen=max_history)
        self.subscribers = []
        self.is_monitoring = True
        self.monitor_thread = None
    
    def add_activity(self, activity: Dict[str, Any], analysis: Dict[str, Any]):
        """Add activity to real-time stream"""
        timestamp = datetime.now().isoformat()
        
        stream_data = {
            "timestamp": timestamp,
            "activity": activity,
            "analysis": analysis
        }
        
        self.activity_stream.append(stream_data)
        self.risk_stream.append({
            "timestamp": timestamp,
            "risk_score": analysis.get("risk_score", 0),
            "risk_level": analysis.get("risk_level", "NORMAL")
        })
        
        # Check for anomalies
        if analysis.get("anomalies_detected"):
            self.anomaly_stream.append(stream_data)
        
        # Notify subscribers
        self._notify_subscribers(stream_data)
    
    def subscribe(self, callback):
        """Subscribe to real-time updates"""
        self.subscribers.append(callback)
        return lambda: self.subscribers.remove(callback)
    
    def _notify_subscribers(self, data):
        """Notify all subscribers of new activity"""
        for callback in self.subscribers:
            try:
                callback(data)
            except Exception as e:
                print(f"Subscriber error: {e}")
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get current live statistics"""
        if not self.activity_stream:
            return {"status": "No data yet"}
        
        last_60_seconds = []
        current_time = datetime.now()
        
        for item in self.activity_stream:
            item_time = datetime.fromisoformat(item["timestamp"])
            if (current_time - item_time).total_seconds() <= 60:
                last_60_seconds.append(item)
        
        high_risk_count = len([
            a for a in last_60_seconds 
            if a["analysis"].get("risk_score", 0) >= 70
        ])
        
        return {
            "timestamp": current_time.isoformat(),
            "activities_last_minute": len(last_60_seconds),
            "high_risk_last_minute": high_risk_count,
            "risk_percentage": (high_risk_count / len(last_60_seconds) * 100) if last_60_seconds else 0,
            "total_today": len(self.activity_stream),
            "current_risk_trend": self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate current risk trend"""
        if len(self.risk_stream) < 10:
            return "stable"
        
        recent_scores = [r["risk_score"] for r in list(self.risk_stream)[-10:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        older_scores = [r["risk_score"] for r in list(self.risk_stream)[-20:-10]]
        if older_scores:
            avg_older = sum(older_scores) / len(older_scores)
            if avg_recent > avg_older * 1.2:
                return "increasing"
            elif avg_recent < avg_older * 0.8:
                return "decreasing"
        
        return "stable"
    
    def get_anomaly_alerts(self, minutes: int = 5) -> List[Dict]:
        """Get anomaly alerts from last X minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        alerts = []
        
        for item in self.anomaly_stream:
            item_time = datetime.fromisoformat(item["timestamp"])
            if item_time >= cutoff:
                alerts.append(item)
        
        return alerts

realtime_monitor = RealtimeMonitor()