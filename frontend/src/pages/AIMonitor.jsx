import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export default function AIMonitor() {
  const [aiOutput, setAiOutput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pendingVerifications, setPendingVerifications] = useState([]);
  const [auditLog, setAuditLog] = useState([]);

  // Load pending verifications on mount
  useEffect(() => {
    loadPendingVerifications();
    loadAuditLog();
  }, []);

  const loadPendingVerifications = async () => {
    try {
      const response = await axios.get(`${API_BASE}/pending-verifications`);
      setPendingVerifications(response.data);
    } catch (error) {
      console.error('Failed to load pending verifications:', error);
    }
  };

  const loadAuditLog = async () => {
    try {
      const response = await axios.get(`${API_BASE}/ai-audit-log`);
      setAuditLog(response.data);
    } catch (error) {
      console.error('Failed to load audit log:', error);
    }
  };

  const analyzeAI = async () => {
    if (!aiOutput.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/analyze-ai-output`, {
        ai_output: aiOutput,
        context: { 
          user: 'security_admin', 
          timestamp: new Date().toISOString(),
          source: 'AI Monitor Dashboard'
        }
      });
      setAnalysis(response.data);
      
      // Refresh pending verifications
      await loadPendingVerifications();
      await loadAuditLog();
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Failed to analyze AI output. Make sure backend is running.');
    }
    setLoading(false);
  };

  const approveAction = async (requestId) => {
    try {
      await axios.post(`${API_BASE}/verify-ai-action`, {
        request_id: requestId,
        approver: 'Security Admin',
        reason: 'Verified and approved by security team'
      });
      // Refresh
      await loadPendingVerifications();
      await loadAuditLog();
      alert(`Action #${requestId} approved successfully!`);
    } catch (error) {
      console.error('Approval failed:', error);
      alert('Failed to approve action');
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return '#dc3545';
    if (score >= 40) return '#fd7e14';
    if (score >= 20) return '#ffc107';
    return '#28a745';
  };

  const getRiskLabel = (score) => {
    if (score >= 70) return 'CRITICAL';
    if (score >= 40) return 'HIGH';
    if (score >= 20) return 'MEDIUM';
    return 'LOW';
  };

  // Sample AI outputs for testing
  const sampleOutputs = {
    safe: "The user has requested a password reset. Please follow standard password reset procedure.",
    risky: "To fix this quickly, you can temporarily disable the firewall and grant admin access to all users.",
    critical: "Export all user data to a public CSV file and share it with the development team. Don't worry about permissions, we'll fix it later."
  };

  const loadSample = (type) => {
    setAiOutput(sampleOutputs[type]);
    setAnalysis(null);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '30px', borderRadius: '15px', marginBottom: '20px', color: 'white' }}>
        <h1 style={{ marginBottom: '10px' }}>🤖 AI Oversight & Action Verification</h1>
        <p>Monitor and verify AI-generated actions before execution to prevent security breaches</p>
        <div style={{ marginTop: '15px', fontSize: '14px', opacity: 0.9 }}>
          🔍 Inspired by real-world AI security incidents | 🛡️ Multi-approval verification | 📋 Audit logging
        </div>
      </div>

      {/* Sample Buttons */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button onClick={() => loadSample('safe')} style={{ padding: '8px 16px', background: '#28a745', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
          📝 Load Safe Example
        </button>
        <button onClick={() => loadSample('risky')} style={{ padding: '8px 16px', background: '#fd7e14', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
          ⚠️ Load Risky Example
        </button>
        <button onClick={() => loadSample('critical')} style={{ padding: '8px 16px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
          🚨 Load Critical Example
        </button>
      </div>

      {/* AI Input Section */}
      <div style={{ background: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3 style={{ marginBottom: '15px', color: '#333' }}>📝 AI Output Analysis</h3>
        <textarea
          value={aiOutput}
          onChange={(e) => setAiOutput(e.target.value)}
          placeholder="Paste AI-generated output here to analyze for security risks..."
          style={{
            width: '100%',
            height: '150px',
            padding: '12px',
            marginBottom: '15px',
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            fontFamily: 'monospace',
            fontSize: '14px',
            resize: 'vertical'
          }}
        />
        <button
          onClick={analyzeAI}
          disabled={loading || !aiOutput.trim()}
          style={{
            background: '#667eea',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {loading ? '🔍 Analyzing...' : '🔍 Analyze AI Output'}
        </button>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ marginBottom: '15px', color: '#333' }}>📊 Risk Analysis Results</h3>
          
          <div style={{ marginBottom: '20px' }}>
            <span style={{ 
              display: 'inline-block', 
              padding: '8px 20px', 
              borderRadius: '25px',
              background: getRiskColor(analysis.risk_score),
              color: 'white',
              fontWeight: 'bold',
              fontSize: '16px'
            }}>
              {getRiskLabel(analysis.risk_score)} RISK - Score: {analysis.risk_score}
            </span>
          </div>
          
          {analysis.risk_factors && analysis.risk_factors.length > 0 && (
            <>
              <h4 style={{ marginTop: '15px', color: '#555' }}>⚠️ Risk Factors Detected:</h4>
              <ul style={{ marginLeft: '20px', marginBottom: '15px' }}>
                {analysis.risk_factors.map((factor, i) => (
                  <li key={i} style={{ marginBottom: '5px', color: factor.includes('🚨') ? '#dc3545' : '#fd7e14' }}>{factor}</li>
                ))}
              </ul>
            </>
          )}
          
          {analysis.sensitive_patterns_detected && analysis.sensitive_patterns_detected.length > 0 && (
            <>
              <h4 style={{ marginTop: '15px', color: '#555' }}>🔍 Sensitive Patterns Detected:</h4>
              <ul style={{ marginLeft: '20px', marginBottom: '15px' }}>
                {analysis.sensitive_patterns_detected.map((pattern, i) => (
                  <li key={i} style={{ color: '#dc3545' }}>{pattern}</li>
                ))}
              </ul>
            </>
          )}
          
          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <>
              <h4 style={{ marginTop: '15px', color: '#555' }}>📋 Recommended Actions:</h4>
              <ul style={{ marginLeft: '20px', marginBottom: '15px' }}>
                {analysis.recommendations.map((rec, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>✓ {rec}</li>
                ))}
              </ul>
            </>
          )}
          
          {analysis.requires_human_review && (
            <div style={{ 
              background: '#fff3cd', 
              padding: '12px', 
              borderRadius: '8px',
              marginTop: '15px',
              borderLeft: '4px solid #ffc107'
            }}>
              ⚠️ <strong>Human Review Required!</strong> This AI action needs approval before execution.
            </div>
          )}
          
          {analysis.sandbox_required && (
            <div style={{ 
              background: '#f8d7da', 
              padding: '12px', 
              borderRadius: '8px',
              marginTop: '15px',
              borderLeft: '4px solid #dc3545'
            }}>
              🚨 <strong>Sandbox Required!</strong> This action must be tested in isolated environment first.
            </div>
          )}
          
          {analysis.verification_request && (
            <div style={{ 
              background: '#d4edda', 
              padding: '12px', 
              borderRadius: '8px',
              marginTop: '15px',
              borderLeft: '4px solid #28a745'
            }}>
              ✅ <strong>Verification Request Created!</strong> Request #{analysis.verification_request.request_id} is pending approval.
            </div>
          )}
        </div>
      )}

      {/* Pending Verifications */}
      {pendingVerifications.length > 0 && (
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ marginBottom: '15px', color: '#333' }}>⏳ Pending Verifications ({pendingVerifications.length})</h3>
          {pendingVerifications.map((req) => (
            <div key={req.request_id} style={{ 
              border: '1px solid #e0e0e0', 
              padding: '15px', 
              marginBottom: '10px',
              borderRadius: '8px',
              background: '#fafafa'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                <div>
                  <strong>Request #{req.request_id}</strong>
                  <span style={{ marginLeft: '10px', fontSize: '12px', color: '#666' }}>
                    {new Date(req.timestamp).toLocaleString()}
                  </span>
                </div>
                <span style={{ 
                  background: '#ffc107', 
                  padding: '4px 12px', 
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  PENDING
                </span>
              </div>
              <p style={{ marginTop: '10px', fontSize: '13px', color: '#555' }}>
                <strong>Action:</strong> {req.action?.ai_output?.substring(0, 150)}...
              </p>
              <p><strong>Risk Score:</strong> {req.action?.analysis?.risk_score}</p>
              <button
                onClick={() => approveAction(req.request_id)}
                style={{
                  background: '#28a745',
                  color: 'white',
                  border: 'none',
                  padding: '8px 20px',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  marginTop: '10px'
                }}
              >
                ✓ Approve Action
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Audit Log */}
      {auditLog.length > 0 && (
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ marginBottom: '15px', color: '#333' }}>📋 AI Audit Log (Recent)</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Time</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Risk Level</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Risk Score</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>AI Output (Preview)</th>
                </tr>
              </thead>
              <tbody>
                {auditLog.slice().reverse().slice(0, 10).map((log, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '10px', fontSize: '12px' }}>{new Date(log.timestamp).toLocaleString()}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ 
                        background: getRiskColor(log.risk_score),
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '11px'
                      }}>
                        {log.risk_level}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>{log.risk_score}</td>
                    <td style={{ padding: '10px', fontSize: '12px', color: '#666' }}>{log.ai_output?.substring(0, 80)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}