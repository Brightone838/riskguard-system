from typing import Dict, Any, List
from datetime import datetime
import json

class ResponderAgent:
    """
    Agent 4: Takes automated actions based on risk level
    Complete Auto-Response System
    """
    def __init__(self):
        self.actions_taken = []
        self.blocked_users = []
        self.locked_sessions = []
        self.blocked_ips = []
        self.alert_log = []
    
    def respond_to_threat(self, analysis: Dict[str, Any], activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take automated response based on risk level
        Risk Levels:
        - LOW (0-19): Allow, monitor
        - MEDIUM (20-39): Warn, flag
        - HIGH (40-69): Alert, monitor closely
        - CRITICAL (70-100): Block, lock, notify
        """
        risk_score = analysis.get("risk_score", 0)
        user_id = activity.get("user_id")
        ip_address = activity.get("ip_address", "unknown")
        action_type = activity.get("action", "unknown")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
            auto_action = "BLOCK_AND_LOCK"
        elif risk_score >= 40:
            risk_level = "HIGH"
            auto_action = "ALERT_AND_MONITOR"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
            auto_action = "WARN_AND_FLAG"
        else:
            risk_level = "LOW"
            auto_action = "ALLOW"
        
        # Build response
        response = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "ip_address": ip_address,
            "action": action_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "auto_action": auto_action,
            "actions_taken": [],
            "requires_admin_review": False
        }
        
        # ==================== AUTO-RESPONSE LOGIC ====================
        
        # CRITICAL RISK: Block user and lock session
        if risk_score >= 70:
            # Block user
            if user_id and user_id not in self.blocked_users:
                self.blocked_users.append(user_id)
                response["actions_taken"].append({
                    "type": "BLOCK_USER",
                    "message": f"User {user_id} automatically blocked due to CRITICAL risk",
                    "details": f"Risk score: {risk_score}, Action: {action_type}"
                })
            
            # Lock session
            if user_id and user_id not in self.locked_sessions:
                self.locked_sessions.append(user_id)
                response["actions_taken"].append({
                    "type": "LOCK_SESSION",
                    "message": f"Session for {user_id} locked",
                    "requires_login": True
                })
            
            # Block IP
            if ip_address and ip_address != "unknown" and ip_address not in self.blocked_ips:
                self.blocked_ips.append(ip_address)
                response["actions_taken"].append({
                    "type": "BLOCK_IP",
                    "message": f"IP {ip_address} blocked",
                    "duration": "24 hours"
                })
            
            # Require admin review
            response["requires_admin_review"] = True
            response["admin_action_required"] = "IMMEDIATE ADMIN REVIEW REQUIRED"
            
            # Generate security alert
            self._log_alert("CRITICAL", user_id, f"CRITICAL threat detected - User blocked", risk_score)
        
        # HIGH RISK: Alert and monitor
        elif risk_score >= 40:
            # Flag for monitoring
            response["actions_taken"].append({
                "type": "FLAG_FOR_MONITORING",
                "message": f"User {user_id} flagged for increased monitoring",
                "monitoring_duration": "24 hours"
            })
            
            # Send alert
            self._log_alert("HIGH", user_id, f"HIGH risk activity detected", risk_score)
            
            # Require admin review (non-urgent)
            response["requires_admin_review"] = True
            response["admin_action_required"] = "REVIEW REQUIRED"
        
        # MEDIUM RISK: Warn and flag
        elif risk_score >= 20:
            response["actions_taken"].append({
                "type": "WARN_USER",
                "message": f"Warning: Suspicious activity detected",
                "severity": "MEDIUM"
            })
            
            response["actions_taken"].append({
                "type": "FLAG_ACTIVITY",
                "message": f"Activity flagged for review",
                "flag_reason": "Medium risk threshold exceeded"
            })
        
        # LOW RISK: Allow, but log
        else:
            response["actions_taken"].append({
                "type": "ALLOW",
                "message": f"Activity allowed - Low risk",
                "note": "Normal monitoring continues"
            })
        
        # Record the response
        self.actions_taken.append(response)
        
        return response
    
    def _log_alert(self, severity: str, user_id: str, message: str, risk_score: int):
        """Log alert for security team"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "user_id": user_id,
            "message": message,
            "risk_score": risk_score
        }
        self.alert_log.append(alert)
        # Keep only last 100 alerts
        if len(self.alert_log) > 100:
            self.alert_log = self.alert_log[-100:]
    
    def get_blocked_users(self) -> List[str]:
        """Get list of blocked users"""
        return self.blocked_users
    
    def get_locked_sessions(self) -> List[str]:
        """Get list of locked sessions"""
        return self.locked_sessions
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return self.blocked_ips
    
    def unblock_user(self, user_id: str, admin: str = None) -> Dict[str, Any]:
        """Unblock a user (admin action)"""
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            if user_id in self.locked_sessions:
                self.locked_sessions.remove(user_id)
            return {
                "status": "unblocked",
                "user_id": user_id,
                "unblocked_by": admin or "system",
                "timestamp": datetime.now().isoformat()
            }
        return {"status": "not_found", "user_id": user_id}
    
    def unblock_ip(self, ip_address: str, admin: str = None) -> Dict[str, Any]:
        """Unblock an IP (admin action)"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            return {
                "status": "unblocked",
                "ip_address": ip_address,
                "unblocked_by": admin or "system",
                "timestamp": datetime.now().isoformat()
            }
        return {"status": "not_found", "ip_address": ip_address}
    
    def get_alerts(self, severity: str = None, limit: int = 50) -> List[Dict]:
        """Get security alerts"""
        alerts = self.alert_log[::-1]  # Newest first
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        return alerts[:limit]
    
    def clear_alerts(self) -> Dict[str, Any]:
        """Clear all alerts"""
        count = len(self.alert_log)
        self.alert_log = []
        return {"cleared": count, "message": f"Cleared {count} alerts"}
    
    def get_response_summary(self) -> Dict[str, Any]:
        """Get summary of all responses"""
        return {
            "total_actions": len(self.actions_taken),
            "blocked_users": self.blocked_users,
            "locked_sessions": self.locked_sessions,
            "blocked_ips": self.blocked_ips,
            "active_alerts": len(self.alert_log),
            "last_response": self.actions_taken[-1] if self.actions_taken else None
        }

responder_agent = ResponderAgent()