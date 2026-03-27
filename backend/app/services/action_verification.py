from typing import Dict, Any, List
from datetime import datetime

class ActionVerificationService:
    def __init__(self):
        self.verification_requests = []
        self.approved_actions = []
    
    def request_verification(self, action: Dict[str, Any]) -> Dict[str, Any]:
        request = {
            "request_id": len(self.verification_requests) + 1,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": "PENDING",
            "approvals": []
        }
        self.verification_requests.append(request)
        return request
    
    def approve_action(self, request_id: int, approver: str, reason: str = None) -> Dict[str, Any]:
        for request in self.verification_requests:
            if request["request_id"] == request_id:
                request["approvals"].append({
                    "approver": approver,
                    "timestamp": datetime.now().isoformat(),
                    "reason": reason
                })
                if len(request["approvals"]) >= 1:
                    request["status"] = "APPROVED"
                    self.approved_actions.append(request)
                return request
        return {"error": "Request not found"}
    
    def get_pending_verifications(self) -> List[Dict]:
        return [r for r in self.verification_requests if r["status"] == "PENDING"]

action_verification = ActionVerificationService()