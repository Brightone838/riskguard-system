from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.activity import Activity
from app.services.threat_intelligence import analyze_activity
from app.services.advanced_analytics import advanced_analytics
from app.services.alert_system import alert_system
import json

class DashboardService:
    def __init__(self):
        self.dashboard_cache = {}
        self.last_update = None
    
    def get_dashboard_data(self, db: Session) -> Dict[str, Any]:
        """Get complete dashboard data"""
        
        # Time ranges
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Get all activities
        all_activities = db.query(Activity).all()
        recent_activities = db.query(Activity).filter(
            Activity.created_at >= last_24h
        ).all()
        
        # 1. Real-time metrics
        metrics = self._calculate_metrics(db, all_activities, recent_activities)
        
        # 2. Risk distribution
        risk_distribution = self._calculate_risk_distribution(all_activities)
        
        # 3. Time series data (for charts)
        time_series = self._calculate_time_series(db, last_7d)
        
        # 4. Top risky users
        top_risky_users = self._get_top_risky_users(db, all_activities)
        
        # 5. Recent alerts
        recent_alerts = alert_system.get_alerts(limit=20)
        
        # 6. Anomaly detection summary
        anomalies = self._get_anomaly_summary(db, recent_activities)
        
        # 7. Attack patterns
        attack_patterns = advanced_analytics.detect_patterns(db)
        
        # 8. System health
        system_health = self._get_system_health(db, all_activities)
        
        return {
            "timestamp": now.isoformat(),
            "metrics": metrics,
            "risk_distribution": risk_distribution,
            "time_series": time_series,
            "top_risky_users": top_risky_users,
            "recent_alerts": recent_alerts,
            "anomalies": anomalies,
            "attack_patterns": attack_patterns,
            "system_health": system_health
        }
    
    def _calculate_metrics(self, db: Session, all_activities: List, recent_activities: List) -> Dict[str, Any]:
        """Calculate key metrics"""
        
        # Calculate risk scores for recent activities
        high_risk_count = 0
        critical_risk_count = 0
        total_risk_score = 0
        
        for activity in recent_activities:
            data = {
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            analysis = analyze_activity(data)
            risk_score = analysis["risk_score"]
            total_risk_score += risk_score
            
            if risk_score >= 100:
                critical_risk_count += 1
            elif risk_score >= 70:
                high_risk_count += 1
        
        avg_risk_score = total_risk_score / len(recent_activities) if recent_activities else 0
        
        return {
            "total_activities": len(all_activities),
            "activities_24h": len(recent_activities),
            "unique_users": db.query(func.count(func.distinct(Activity.user_id))).scalar(),
            "high_risk_24h": high_risk_count,
            "critical_risk_24h": critical_risk_count,
            "avg_risk_score": round(avg_risk_score, 2),
            "total_alerts": len(alert_system.get_alerts()),
            "anomalies_detected": len([a for a in recent_activities if self._is_anomaly(a)])
        }
    
    def _calculate_risk_distribution(self, activities: List) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "normal": 0
        }
        
        for activity in activities:
            data = {
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            analysis = analyze_activity(data)
            risk_score = analysis["risk_score"]
            
            if risk_score >= 100:
                distribution["critical"] += 1
            elif risk_score >= 70:
                distribution["high"] += 1
            elif risk_score >= 40:
                distribution["medium"] += 1
            elif risk_score >= 20:
                distribution["low"] += 1
            else:
                distribution["normal"] += 1
        
        return distribution
    
    def _calculate_time_series(self, db: Session, last_7d: datetime) -> Dict[str, List]:
        """Calculate time series data for charts"""
        
        time_series = {
            "timestamps": [],
            "risk_scores": [],
            "activity_counts": [],
            "anomaly_counts": []
        }
        
        # Group by hour for last 7 days
        for i in range(168):  # 7 days * 24 hours
            hour_start = last_7d + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            
            activities = db.query(Activity).filter(
                and_(
                    Activity.created_at >= hour_start,
                    Activity.created_at < hour_end
                )
            ).all()
            
            if activities:
                time_series["timestamps"].append(hour_start.isoformat())
                time_series["activity_counts"].append(len(activities))
                
                # Calculate average risk score for this hour
                total_risk = 0
                anomaly_count = 0
                for activity in activities:
                    data = {
                        "login_attempts": activity.login_attempts,
                        "authenticated": activity.authenticated,
                        "records_accessed": activity.records_accessed,
                        "hour": activity.hour
                    }
                    analysis = analyze_activity(data)
                    total_risk += analysis["risk_score"]
                    
                    if self._is_anomaly(activity):
                        anomaly_count += 1
                
                avg_risk = total_risk / len(activities) if activities else 0
                time_series["risk_scores"].append(round(avg_risk, 2))
                time_series["anomaly_counts"].append(anomaly_count)
        
        return time_series
    
    def _get_top_risky_users(self, db: Session, activities: List) -> List[Dict]:
        """Get top 10 risky users"""
        user_risk = {}
        
        for activity in activities:
            user_id = activity.user_id
            data = {
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            analysis = analyze_activity(data)
            
            if user_id not in user_risk:
                user_risk[user_id] = {
                    "total_risk": 0,
                    "activity_count": 0,
                    "high_risk_count": 0
                }
            
            user_risk[user_id]["total_risk"] += analysis["risk_score"]
            user_risk[user_id]["activity_count"] += 1
            
            if analysis["risk_score"] >= 70:
                user_risk[user_id]["high_risk_count"] += 1
        
        # Calculate average risk and sort
        risky_users = []
        for user_id, data in user_risk.items():
            risky_users.append({
                "user_id": user_id,
                "avg_risk_score": round(data["total_risk"] / data["activity_count"], 2),
                "total_activities": data["activity_count"],
                "high_risk_activities": data["high_risk_count"],
                "risk_percentage": round((data["high_risk_count"] / data["activity_count"]) * 100, 2)
            })
        
        risky_users.sort(key=lambda x: x["avg_risk_score"], reverse=True)
        return risky_users[:10]
    
    def _get_anomaly_summary(self, db: Session, recent_activities: List) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        anomalies = []
        
        for activity in recent_activities[:50]:  # Last 50 activities
            data = {
                "user_id": activity.user_id,
                "login_attempts": activity.login_attempts,
                "authenticated": activity.authenticated,
                "records_accessed": activity.records_accessed,
                "hour": activity.hour
            }
            result = advanced_analytics.detect_anomalies(db, data)
            
            if result["anomalies"]:
                anomalies.append({
                    "activity_id": activity.id,
                    "user_id": activity.user_id,
                    "timestamp": activity.created_at.isoformat(),
                    "anomalies": result["anomalies"],
                    "anomaly_score": result["anomaly_score"]
                })
        
        return {
            "total_anomalies": len(anomalies),
            "recent_anomalies": anomalies[:10],
            "severity_breakdown": {
                "high": len([a for a in anomalies if a["anomaly_score"] > 70]),
                "medium": len([a for a in anomalies if 40 <= a["anomaly_score"] <= 70]),
                "low": len([a for a in anomalies if a["anomaly_score"] < 40])
            }
        }
    
    def _get_system_health(self, db: Session, activities: List) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Calculate error rate (failed authentications)
        failed_auth = len([a for a in activities if not a.authenticated])
        error_rate = (failed_auth / len(activities) * 100) if activities else 0
        
        # Calculate average response time (simulated)
        avg_response_time = 0.15  # 150ms average
        
        # Database size
        db_size = len(activities) * 0.5  # Rough estimate in KB
        
        return {
            "status": "healthy",
            "uptime_percentage": 99.95,
            "error_rate": round(error_rate, 2),
            "avg_response_time_ms": avg_response_time,
            "database_records": len(activities),
            "database_size_mb": round(db_size / 1024, 2),
            "active_alerts": len(alert_system.get_alerts()),
            "last_analysis": datetime.now().isoformat()
        }
    
    def _is_anomaly(self, activity: Activity) -> bool:
        """Check if activity is anomalous"""
        data = {
            "user_id": activity.user_id,
            "login_attempts": activity.login_attempts,
            "authenticated": activity.authenticated,
            "records_accessed": activity.records_accessed,
            "hour": activity.hour
        }
        
        # Quick anomaly check (simplified)
        return (
            activity.login_attempts > 3 or
            not activity.authenticated or
            activity.records_accessed > 100 or
            activity.hour < 6 or activity.hour > 22
        )

dashboard_service = DashboardService()