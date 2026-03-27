from typing import Dict, Any, List
from datetime import datetime
import hashlib
import json

class AuditorAgent:
    """
    Agent 5: Creates immutable proof of actions (Blockchain-like)
    """
    def __init__(self):
        self.chain = []
        self.current_block = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "previous_hash": "0",
            "hash": self._calculate_hash(0, [], "0")
        }
        self.chain.append(genesis_block)
    
    def _calculate_hash(self, index: int, actions: List, previous_hash: str) -> str:
        """Calculate SHA-256 hash for a block"""
        block_string = f"{index}{json.dumps(actions)}{previous_hash}".encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def record_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Record an action with proof (immutable)"""
        proof_action = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "proof": hashlib.sha256(json.dumps(action, default=str).encode()).hexdigest()
        }
        
        self.current_block.append(proof_action)
        
        # Create new block every 10 actions
        if len(self.current_block) >= 10:
            self._create_block()
        
        return {
            "recorded": True,
            "proof": proof_action["proof"],
            "block_pending": len(self.current_block)
        }
    
    def _create_block(self) -> Dict[str, Any]:
        """Create a new block in the chain"""
        previous_block = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": datetime.now().isoformat(),
            "actions": self.current_block,
            "previous_hash": previous_block["hash"],
            "hash": self._calculate_hash(len(self.chain), self.current_block, previous_block["hash"])
        }
        self.chain.append(new_block)
        self.current_block = []
        return new_block
    
    def verify_action(self, action_proof: str) -> Dict[str, Any]:
        """Verify if an action exists in the chain"""
        for block in self.chain:
            for action in block.get("actions", []):
                if action.get("proof") == action_proof:
                    return {
                        "verified": True,
                        "action": action,
                        "block_index": block["index"]
                    }
        return {"verified": False, "message": "Action not found in chain"}
    
    def get_audit_trail(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Get audit trail for a user"""
        audit_trail = []
        for block in self.chain:
            for action in block.get("actions", []):
                action_data = action.get("action", {})
                if user_id is None or action_data.get("user_id") == user_id:
                    audit_trail.append({
                        "timestamp": action.get("timestamp"),
                        "action": action_data,
                        "proof": action.get("proof"),
                        "block_index": block["index"]
                    })
        return audit_trail[-limit:]

auditor_agent = AuditorAgent()