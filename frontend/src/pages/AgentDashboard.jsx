import { useEffect, useState } from 'react';
import axios from 'axios';
import './AgentDashboard.css';

const API_BASE = 'http://127.0.0.1:8000';

export default function AgentDashboard() {
  const [agents, setAgents] = useState([]);
  const [agentInsights, setAgentInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [aiInput, setAiInput] = useState('');
  const [aiValidation, setAiValidation] = useState(null);

  useEffect(() => {
    loadAgents();
    loadAgentInsights();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/agent-status`);
      setAgents(response.data.agents);
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  const loadAgentInsights = async () => {
    try {
      const response = await axios.get(`${API_BASE}/agent-insights`);
      setAgentInsights(response.data);
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateAIDecision = async () => {
    if (!aiInput.trim()) return;
    
    try {
      const response = await axios.post(`${API_BASE}/validate-ai-decision`, {
        ai_output: aiInput,
        context: { source: 'Agent Dashboard', user: 'admin' }
      });
      setAiValidation(response.data);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const getAgentIcon = (name) => {
    const icons = {
      'MONITOR': '🔍',
      'ANALYZER': '📊',
      'AI OVERSIGHT': '🤖',
      'RESPONDER': '⚡',
      'AUDITOR': '📜',
      'STRATEGIST': '🧠'
    };
    return icons[name] || '🤖';
  };

  const getAgentColor = (name) => {
    const colors = {
      'MONITOR': '#17a2b8',
      'ANALYZER': '#28a745',
      'AI OVERSIGHT': '#dc3545',
      'RESPONDER': '#fd7e14',
      'AUDITOR': '#6c757d',
      'STRATEGIST': '#6610f2'
    };
    return colors[name] || '#667eea';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <h2>Loading AI Agents...</h2>
      </div>
    );
  }

  return (
    <div className="agent-dashboard">
      <div className="agent-header">
        <h1>🤖 6 AI Agents Dashboard</h1>
        <p>Coordinated Threat Detection & Response System</p>
        <div className="agent-stats">
          <span className="stat-badge">🎯 6 Active Agents</span>
          <span className="stat-badge">⚡ Real-time Monitoring</span>
          <span className="stat-badge">🔗 Coordinated Response</span>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="agents-grid">
        {agents.map((agent, index) => (
          <div 
            key={index} 
            className={`agent-card ${selectedAgent === agent.name ? 'selected' : ''}`}
            onClick={() => setSelectedAgent(agent.name)}
            style={{ borderTopColor: getAgentColor(agent.name) }}
          >
            <div className="agent-icon" style={{ background: getAgentColor(agent.name) }}>
              {getAgentIcon(agent.name)}
            </div>
            <h3>{agent.name}</h3>
            <p>{agent.description}</p>
            <div className="agent-status">
              <span className="status-dot"></span>
              {agent.status}
            </div>
          </div>
        ))}
      </div>

      {/* AI Oversight Section (YOUR UNIQUE FEATURE) */}
      <div className="ai-oversight-section">
        <div className="section-header">
          <h2>🤖 AI Oversight Agent (Your Unique Feature)</h2>
          <p>Validates AI decisions before execution - prevents AI-driven security breaches</p>
        </div>
        
        <div className="ai-validation-area">
          <textarea
            value={aiInput}
            onChange={(e) => setAiInput(e.target.value)}
            placeholder="Paste AI-generated output here to validate..."
            rows={4}
          />
          <button onClick={validateAIDecision} className="validate-btn">
            🔍 Validate AI Decision
          </button>
        </div>

        {aiValidation && (
          <div className={`validation-result ${aiValidation.risk_level?.toLowerCase()}`}>
            <div className="result-header">
              <span className="risk-badge" style={{ background: getRiskColor(aiValidation.risk_score) }}>
                {aiValidation.risk_level} RISK - Score: {aiValidation.risk_score}
              </span>
            </div>
            
            {aiValidation.risk_factors?.length > 0 && (
              <div className="risk-factors">
                <strong>⚠️ Risk Factors:</strong>
                <ul>
                  {aiValidation.risk_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="recommendations">
              <strong>📋 Recommended Actions:</strong>
              <ul>
                {aiValidation.recommendations?.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
            
            {aiValidation.requires_verification && (
              <div className="verification-required">
                ⚠️ VERIFICATION REQUIRED: This AI action needs approval before execution
              </div>
            )}
          </div>
        )}
      </div>

      {/* Agent Insights */}
      {agentInsights && (
        <div className="insights-section">
          <h2>🧠 Strategist Agent Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <h4>📊 Monitor Status</h4>
              <p>{agentInsights.monitor_status || 'Active'}</p>
            </div>
            <div className="insight-card">
              <h4>📈 Analyzer Status</h4>
              <p>{agentInsights.analyzer_status || 'Active'}</p>
            </div>
            <div className="insight-card">
              <h4>⚡ Responder Status</h4>
              <p>{agentInsights.responder_status || 'Active'}</p>
            </div>
            <div className="insight-card">
              <h4>📜 Auditor Status</h4>
              <p>{agentInsights.auditor_status || 'Active'}</p>
            </div>
          </div>
          
          {agentInsights.strategist_insights?.recommendations && (
            <div className="recommendations-box">
              <h4>💡 Learning Recommendations</h4>
              <ul>
                {agentInsights.strategist_insights.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function getRiskColor(score) {
  if (score >= 70) return '#dc3545';
  if (score >= 40) return '#fd7e14';
  if (score >= 20) return '#ffc107';
  return '#28a745';
}