from typing import Dict, Any, List
from datetime import datetime

from app.services.agents.monitor_agent import monitor_agent
from app.services.agents.analyzer_agent import analyzer_agent
from app.services.agents.ai_oversight_agent import ai_oversight_agent
from app.services.agents.responder_agent import responder_agent
from app.services.agents.auditor_agent import auditor_agent
from app.services.agents.strategist_agent import strategist_agent

class AgentCoordinator:
    """
    Coordinates all 6 AI agents to work together
    """
    def __init__(self):
        self.agents = {
            "monitor": monitor_agent,
            "analyzer": analyzer_agent,
            "ai_oversight": ai_oversight_agent,
            "responder": responder_agent,
            "auditor": auditor_agent,
            "strategist": strategist_agent
        }
    
    def process_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity through all agents"""
        
        # Step 1: Monitor Agent - Track activity
        tracked = self.agents["monitor"].track_activity(activity)
        
        # Step 2: Analyzer Agent - Detect anomalies
        analysis = self.agents["analyzer"].analyze_activity(tracked)
        
        # Step 3: Responder Agent - Take action if needed
        response = self.agents["responder"].respond_to_threat(analysis, tracked)
        
        # Step 4: Auditor Agent - Record with proof
        proof = self.agents["auditor"].record_action({
            "user_id": tracked.get("user_id"),
            "action": tracked.get("action"),
            "analysis": analysis,
            "response": response
        })
        
        return {
            "tracked": tracked,
            "analysis": analysis,
            "response": response,
            "proof": proof,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_ai_decision(self, ai_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI decisions using AI Oversight Agent"""
        validation = self.agents["ai_oversight"].validate_ai_decision(ai_output, context)
        
        # If requires verification, also record with auditor
        if validation.get("requires_verification"):
            self.agents["auditor"].record_action({
                "type": "AI_DECISION",
                "ai_output": ai_output[:200],
                "validation": validation
            })
        
        return validation
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get insights from all agents"""
        return {
            "monitor_status": f"Tracking {len(self.agents['monitor'].user_sessions)} active sessions",
            "analyzer_status": f"Baselines for {len(self.agents['analyzer'].user_baselines)} users",
            "responder_status": f"Blocked users: {self.agents['responder'].get_blocked_users()}",
            "auditor_status": f"Blocks in chain: {len(self.agents['auditor'].chain)}",
            "strategist_insights": self.agents["strategist"].get_learning_insights()
        }

agent_coordinator = AgentCoordinator()