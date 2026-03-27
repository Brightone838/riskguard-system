from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import asyncio
import os
from pydantic import BaseModel

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.activity import Activity as DBActivity
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityListResponse
from app.services.threat_intelligence import analyze_activity, threat_intelligence
from app.services.advanced_analytics import advanced_analytics
from app.services.alert_system import alert_system
from app.services.dashboard_service import dashboard_service
from app.services.realtime_monitor import realtime_monitor
from app.services.ai_oversight import ai_oversight
from app.services.action_verification import action_verification
from app.services.agents.coordinator import agent_coordinator
from app.services.agents.responder_agent import responder_agent
from app.routes import auth

# ==================== PYDANTIC MODELS FOR REQUESTS ====================

class AIOutputRequest(BaseModel):
    ai_output: str
    context: dict = None

class ValidateAIRequest(BaseModel):
    ai_output: str
    context: dict = None

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RiskGuard System",
    description="Advanced Security Monitoring & Threat Detection System with 6 AI Agents & Auto-Response",
    version="4.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth.router)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Subscribe realtime monitor to broadcast
def broadcast_callback(data):
    """Synchronous callback for broadcast"""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(data))
    except RuntimeError:
        pass

realtime_monitor.subscribe(broadcast_callback)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== ROOT ENDPOINTS ====================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the frontend dashboard info"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RiskGuard System - 6 AI Agents</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .status {
                display: inline-block;
                background: #d4edda;
                color: #155724;
                padding: 5px 15px;
                border-radius: 20px;
                margin: 20px 0;
            }
            .agents {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin: 20px 0;
            }
            .agent-card {
                background: #f8f9fa;
                padding: 10px;
                border-radius: 10px;
                text-align: center;
            }
            .agent-card h4 {
                color: #667eea;
                margin-bottom: 5px;
            }
            .agent-card p {
                font-size: 12px;
                color: #666;
            }
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 8px;
                margin: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ RiskGuard System v4.0</h1>
            <p>6 AI Agents | Auto-Response | AI Oversight</p>
            <div class="status">✅ All Systems Active</div>
            
            <div class="agents">
                <div class="agent-card"><h4>🔍 MONITOR</h4><p>Tracks user activity</p></div>
                <div class="agent-card"><h4>📊 ANALYZER</h4><p>Detects anomalies</p></div>
                <div class="agent-card"><h4>🤖 AI OVERSIGHT</h4><p>Validates AI decisions</p></div>
                <div class="agent-card"><h4>⚡ RESPONDER</h4><p>Auto-blocks threats</p></div>
                <div class="agent-card"><h4>📜 AUDITOR</h4><p>Immutable proof</p></div>
                <div class="agent-card"><h4>🧠 STRATEGIST</h4><p>Continuous learning</p></div>
            </div>
            
            <div>
                <a href="/docs" class="btn">📚 API Docs</a>
                <a href="http://localhost:5173" class="btn">🎨 Frontend</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_websockets": len(manager.active_connections),
        "total_alerts": len(alert_system.get_alerts()),
        "agents": {
            "monitor": "active",
            "analyzer": "active",
            "ai_oversight": "active",
            "responder": "active",
            "auditor": "active",
            "strategist": "active"
        }
    }


# ==================== ANALYSIS ENDPOINTS ====================

@app.post("/analyze")
def analyze(
    activity: ActivityCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enhanced analysis with AI, anomaly detection, and auto-response"""
    data = activity.dict()
    
    # Step 1: Process through all 6 AI agents
    agent_result = agent_coordinator.process_activity(data)
    
    # Step 2: Basic threat intelligence
    threat_analysis = analyze_activity(data)
    
    # Step 3: Combine risk scores
    final_risk_score = min(
        threat_analysis["risk_score"] + agent_result["analysis"].get("anomaly_score", 0), 
        200
    )
    
    # Update risk level based on combined score
    if final_risk_score >= 100:
        final_risk_level = "CRITICAL"
    elif final_risk_score >= 70:
        final_risk_level = "HIGH"
    elif final_risk_score >= 40:
        final_risk_level = "MEDIUM"
    else:
        final_risk_level = threat_analysis["risk_level"]
    
    # Step 4: Generate alert if needed
    alert = alert_system.evaluate_alert(
        {
            "risk_score": final_risk_score, 
            "risk_level": final_risk_level, 
            "risk_factors": threat_analysis["risk_factors"]
        },
        data
    )
    
    # Step 5: Auto-response based on risk level
    auto_response = responder_agent.respond_to_threat(
        {"risk_score": final_risk_score, "risk_level": final_risk_level},
        data
    )
    
    # Step 6: Save to database
    db_activity = DBActivity(
        user_id=data["user_id"],
        action=data["action"],
        login_attempts=data.get("login_attempts", 0),
        records_accessed=data.get("records_accessed", 0),
        authenticated=data.get("authenticated", True),
        hour=data.get("hour", 12)
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Step 7: Push to real-time monitor
    realtime_monitor.add_activity(data, {
        "risk_score": final_risk_score,
        "risk_level": final_risk_level,
        "risk_factors": threat_analysis["risk_factors"],
        "agent_analysis": agent_result["analysis"],
        "auto_response": auto_response
    })
    
    return {
        "input": data,
        "analysis": {
            "risk_score": final_risk_score,
            "risk_level": final_risk_level,
            "risk_factors": threat_analysis["risk_factors"],
            "agent_analysis": agent_result["analysis"]
        },
        "agent_response": agent_result["response"],
        "auto_response": auto_response,
        "proof": agent_result["proof"],
        "alert": alert,
        "saved_id": db_activity.id,
        "timestamp": datetime.now().isoformat()
    }


# ==================== ACTIVITY ENDPOINTS ====================

@app.get("/activities", response_model=ActivityListResponse)
def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DBActivity)
    if user_id:
        query = query.filter(DBActivity.user_id == user_id)
    
    total = query.count()
    activities = query.order_by(DBActivity.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "activities": activities
    }


@app.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(DBActivity).filter(DBActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


# ==================== USER ANALYTICS ENDPOINTS ====================

@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    stats = threat_intelligence.get_user_stats(db, user_id)
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    return stats


@app.get("/users/{user_id}/baseline")
def get_user_baseline(user_id: str, db: Session = Depends(get_db)):
    baseline = advanced_analytics.calculate_user_baseline(db, user_id)
    return baseline


@app.get("/users/{user_id}/trend")
def get_user_trend(user_id: str, db: Session = Depends(get_db)):
    trend = advanced_analytics.predict_risk_trend(db, user_id)
    return trend


# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/analytics/anomalies")
def detect_anomalies(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DBActivity)
    if user_id:
        query = query.filter(DBActivity.user_id == user_id)
    
    recent_activities = query.order_by(DBActivity.created_at.desc()).limit(50).all()
    
    anomalies = []
    for activity in recent_activities:
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
                "timestamp": activity.created_at.isoformat() if activity.created_at else None,
                "anomalies": result["anomalies"],
                "anomaly_score": result["anomaly_score"]
            })
    
    return {"total_anomalies": len(anomalies), "anomalies": anomalies}


@app.get("/analytics/patterns")
def detect_patterns(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    patterns = advanced_analytics.detect_patterns(db, user_id)
    return patterns


# ==================== ALERT ENDPOINTS ====================

@app.get("/alerts")
def get_alerts(severity: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    alerts = alert_system.get_alerts(severity, limit)
    return {"total": len(alerts), "alerts": alerts}


@app.delete("/alerts")
def clear_alerts():
    return alert_system.clear_alerts()


# ==================== STATISTICS ENDPOINTS ====================

@app.get("/stats/system")
def get_system_stats(db: Session = Depends(get_db)):
    stats = threat_intelligence.get_system_stats(db)
    
    alerts = alert_system.get_alerts()
    stats["alerts"] = {
        "total": len(alerts),
        "critical": len([a for a in alerts if a["severity"] == "CRITICAL"]),
        "high": len([a for a in alerts if a["severity"] == "HIGH"]),
        "medium": len([a for a in alerts if a["severity"] == "MEDIUM"])
    }
    
    stats["realtime"] = realtime_monitor.get_live_stats()
    stats["agents"] = agent_coordinator.get_system_insights()
    stats["auto_response"] = responder_agent.get_response_summary()
    
    return stats


# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    data = dashboard_service.get_dashboard_data(db)
    data["agents"] = agent_coordinator.get_system_insights()
    data["auto_response"] = responder_agent.get_response_summary()
    return data


@app.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    data = dashboard_service.get_dashboard_data(db)
    return data["metrics"]


@app.get("/dashboard/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db)):
    data = dashboard_service.get_dashboard_data(db)
    return data["risk_distribution"]


@app.get("/dashboard/time-series")
def get_time_series(db: Session = Depends(get_db)):
    data = dashboard_service.get_dashboard_data(db)
    return data["time_series"]


@app.get("/dashboard/top-users")
def get_top_risky_users(db: Session = Depends(get_db)):
    data = dashboard_service.get_dashboard_data(db)
    return data["top_risky_users"]


# ==================== AUTO-RESPONSE ENDPOINTS ====================

@app.get("/responder/blocked-users")
def get_blocked_users():
    """Get list of blocked users"""
    return {"blocked_users": responder_agent.get_blocked_users()}


@app.get("/responder/blocked-ips")
def get_blocked_ips():
    """Get list of blocked IPs"""
    return {"blocked_ips": responder_agent.get_blocked_ips()}


@app.get("/responder/locked-sessions")
def get_locked_sessions():
    """Get list of locked sessions"""
    return {"locked_sessions": responder_agent.get_locked_sessions()}


@app.post("/responder/unblock-user/{user_id}")
def unblock_user(user_id: str, admin: str = "admin"):
    """Unblock a user (admin action)"""
    return responder_agent.unblock_user(user_id, admin)


@app.get("/responder/alerts")
def get_responder_alerts(severity: str = None, limit: int = 50):
    """Get security alerts from responder agent"""
    return responder_agent.get_alerts(severity, limit)


@app.delete("/responder/alerts")
def clear_responder_alerts():
    """Clear all alerts"""
    return responder_agent.clear_alerts()


@app.get("/responder/summary")
def get_responder_summary():
    """Get summary of all responses"""
    return responder_agent.get_response_summary()


@app.get("/risk-formula")
def get_risk_formula():
    """Get risk formula explanation"""
    return {
        "formula": "Risk = (Login × 10) + (Records × 0.5) + (Failed Auth × 50) + (Night Time × 20)",
        "levels": {
            "0-19": "NORMAL",
            "20-39": "LOW RISK",
            "40-69": "MEDIUM RISK",
            "70-99": "HIGH RISK",
            "100-200": "CRITICAL RISK"
        },
        "example": {
            "input": {"login_attempts": 6, "records_accessed": 120, "authenticated": False, "hour": 2},
            "calculation": "(6 × 10) + (120 × 0.5) + (1 × 50) + (1 × 20) = 60 + 60 + 50 + 20 = 190",
            "result": "CRITICAL RISK"
        }
    }


# ==================== AI AGENT ENDPOINTS ====================

@app.post("/process-with-agents")
def process_with_agents(activity: ActivityCreate):
    """Process activity through all 6 AI agents"""
    result = agent_coordinator.process_activity(activity.dict())
    return result


@app.post("/validate-ai-decision")
def validate_ai_decision(request: ValidateAIRequest):
    """Validate AI decisions using AI Oversight Agent"""
    if request.context is None:
        request.context = {}
    return agent_coordinator.validate_ai_decision(request.ai_output, request.context)


@app.get("/agent-insights")
def get_agent_insights():
    """Get insights from all 6 agents"""
    return agent_coordinator.get_system_insights()


@app.get("/agent-status")
def get_agent_status():
    """Get status of all 6 agents"""
    return {
        "agents": [
            {"name": "MONITOR", "status": "active", "description": "Tracks all user activities"},
            {"name": "ANALYZER", "status": "active", "description": "Detects anomalies using ML-like logic"},
            {"name": "AI OVERSIGHT", "status": "active", "description": "Validates AI decisions before execution"},
            {"name": "RESPONDER", "status": "active", "description": "Auto-blocks threats and flags users"},
            {"name": "AUDITOR", "status": "active", "description": "Creates immutable proof of actions"},
            {"name": "STRATEGIST", "status": "active", "description": "Continuous learning and improvement"}
        ],
        "total_agents": 6,
        "coordinator_status": "running"
    }


# ==================== REAL-TIME MONITORING ENDPOINTS ====================

@app.get("/live-stats")
def get_live_stats():
    return realtime_monitor.get_live_stats()


@app.get("/anomaly-alerts")
def get_anomaly_alerts(minutes: int = 5):
    alerts = realtime_monitor.get_anomaly_alerts(minutes)
    return {"alerts": alerts, "count": len(alerts), "timeframe_minutes": minutes}


@app.get("/ai-audit-log")
def get_ai_audit_log(limit: int = 50):
    return ai_oversight.get_ai_audit_log(limit)


@app.get("/pending-verifications")
def get_pending_verifications():
    return action_verification.get_pending_verifications()


@app.post("/verify-ai-action")
def verify_ai_action(request_id: int, approver: str, reason: str = None):
    result = action_verification.approve_action(request_id, approver, reason)
    return result


@app.post("/analyze-ai-output")
def analyze_ai_output(request: AIOutputRequest):
    """Analyze AI-generated output for security risks"""
    if request.context is None:
        request.context = {}
    return ai_oversight.analyze_ai_output(request.ai_output, request.context)


# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to RiskGuard real-time monitor with 6 AI Agents & Auto-Response",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif data == "get_stats":
                stats = realtime_monitor.get_live_stats()
                stats["agents"] = agent_coordinator.get_system_insights()
                stats["auto_response"] = responder_agent.get_response_summary()
                await websocket.send_json({"type": "stats", "data": stats})
            elif data == "get_agents":
                await websocket.send_json({"type": "agents", "data": agent_coordinator.get_system_insights()})
            else:
                await websocket.send_json({"type": "echo", "data": data})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)