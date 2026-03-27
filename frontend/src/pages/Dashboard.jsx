import { useEffect, useState, useRef } from "react";
import { getActivities, getDashboard, getAlerts, RiskGuardWebSocket } from "../services/api";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import "./Dashboard.css";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

export default function Dashboard() {
  const [activities, setActivities] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [blockedUsers, setBlockedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [wsConnected, setWsConnected] = useState(false);
  const [realtimeData, setRealtimeData] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState({ timestamps: [], risk_scores: [], activity_counts: [] });
  const wsRef = useRef(null);

  // Calculate risk score for an activity
  const calculateRiskScore = (activity) => {
    let score = 0;
    if (activity.login_attempts > 5) score += 50;
    if (!activity.authenticated) score += 30;
    if (activity.records_accessed > 100) score += 40;
    if (activity.hour < 6 || activity.hour > 22) score += 20;
    return score;
  };

  // Calculate risk metrics from activities
  const getRiskMetrics = () => {
    let totalRisk = 0;
    let criticalCount = 0;
    let highCount = 0;
    let mediumCount = 0;
    let lowCount = 0;
    let normalCount = 0;
    
    activities.forEach(activity => {
      const score = calculateRiskScore(activity);
      totalRisk += score;
      
      if (score >= 100) criticalCount++;
      else if (score >= 70) highCount++;
      else if (score >= 40) mediumCount++;
      else if (score >= 20) lowCount++;
      else normalCount++;
    });
    
    return {
      avgRisk: activities.length > 0 ? Math.round(totalRisk / activities.length) : 0,
      criticalCount,
      highCount,
      mediumCount,
      lowCount,
      normalCount,
      totalRisk
    };
  };

  // Load blocked users
  const loadBlockedUsers = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/responder/blocked-users');
      const data = await response.json();
      setBlockedUsers(data.blocked_users || []);
    } catch (error) {
      console.error('Failed to load blocked users:', error);
    }
  };

  // Load initial data
  const loadAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [activitiesData, dashboardData, alertsData, timeSeries] = await Promise.all([
        getActivities(),
        getDashboard(),
        getAlerts(),
        fetch('http://127.0.0.1:8000/dashboard/time-series').then(res => res.json())
      ]);
      
      setActivities(activitiesData.activities || []);
      setDashboard(dashboardData);
      setAlerts(alertsData.alerts || []);
      setTimeSeriesData(timeSeries);
      setLastRefresh(new Date());
      await loadBlockedUsers();
    } catch (error) {
      console.error("Error loading data:", error);
      setError("Failed to connect to backend. Make sure the server is running on port 8000");
    }
    setLoading(false);
  };

  // Show browser notification
  const showNotification = (alert) => {
    if (!("Notification" in window)) return;
    
    if (Notification.permission === "granted") {
      new Notification(`🚨 ${alert.severity} Risk Alert`, {
        body: alert.message,
        icon: "/vite.svg"
      });
    } else if (Notification.permission !== "denied") {
      Notification.requestPermission();
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = (data) => {
    if (data.type === 'new_activity') {
      console.log('New activity detected!', data.data);
      setRealtimeData(data.data);
      loadAllData();
      
      if (data.data.analysis.risk_score >= 70) {
        showNotification({
          severity: data.data.analysis.risk_level,
          message: `High risk activity from ${data.data.activity.user_id}: ${data.data.analysis.risk_score} score`
        });
      }
    } else if (data.type === 'stats') {
      setRealtimeData(data.data);
    }
  };

  // WebSocket connection handlers
  const handleWebSocketConnect = () => {
    setWsConnected(true);
    console.log('WebSocket connected - live updates enabled');
  };

  const handleWebSocketDisconnect = () => {
    setWsConnected(false);
  };

  // Initialize WebSocket
  useEffect(() => {
    loadAllData();
    
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
    
    wsRef.current = new RiskGuardWebSocket(
      handleWebSocketMessage,
      handleWebSocketConnect,
      handleWebSocketDisconnect
    );
    wsRef.current.connect();
    
    const interval = setInterval(loadAllData, 30000);
    
    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, []);

  // Format hour correctly
  const formatHour = (hour) => {
    if (hour === undefined || hour === null) return "?";
    if (hour >= 0 && hour <= 23) return `${hour}:00`;
    if (hour === 200) return "2:00";
    return `${hour % 24}:00`;
  };

  // Get risk label
  const getRiskLabel = (score) => {
    if (score >= 100) return "CRITICAL";
    if (score >= 70) return "HIGH";
    if (score >= 40) return "MEDIUM";
    if (score >= 20) return "LOW";
    return "NORMAL";
  };

  // Get risk color
  const getRiskColor = (score) => {
    if (score >= 100) return "#dc3545";
    if (score >= 70) return "#fd7e14";
    if (score >= 40) return "#ffc107";
    if (score >= 20) return "#28a745";
    return "#17a2b8";
  };

  // Get alert class
  const getAlertClass = (severity) => {
    if (!severity) return "alert-medium";
    switch(severity.toUpperCase()) {
      case "CRITICAL": return "alert-critical";
      case "HIGH": return "alert-high";
      case "MEDIUM": return "alert-medium";
      case "LOW": return "alert-low";
      default: return "alert-medium";
    }
  };

  // Get risk metrics
  const riskMetrics = getRiskMetrics();
  const hasActiveThreats = riskMetrics.criticalCount > 0 || riskMetrics.highCount > 0;

  // Prepare Risk Trend Chart Data
  const riskTrendData = {
    labels: timeSeriesData.timestamps?.slice(-24).map(t => {
      const date = new Date(t);
      return `${date.getHours()}:00`;
    }) || [],
    datasets: [
      {
        label: 'Risk Score',
        data: timeSeriesData.risk_scores?.slice(-24) || [],
        borderColor: '#dc3545',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Activity Count',
        data: timeSeriesData.activity_counts?.slice(-24) || [],
        borderColor: '#17a2b8',
        backgroundColor: 'rgba(23, 162, 184, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 6,
        yAxisID: 'y1',
      }
    ]
  };

  // Prepare Risk Distribution Chart Data
  const riskDistributionData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Normal'],
    datasets: [
      {
        data: [
          riskMetrics.criticalCount,
          riskMetrics.highCount,
          riskMetrics.mediumCount,
          riskMetrics.lowCount,
          riskMetrics.normalCount
        ],
        backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#17a2b8'],
        borderWidth: 0,
      }
    ]
  };

  // Prepare Activity Timeline Chart Data
  const timelineData = {
    labels: timeSeriesData.timestamps?.slice(-12).map(t => {
      const date = new Date(t);
      return `${date.getHours()}:00`;
    }) || [],
    datasets: [
      {
        label: 'Activities',
        data: timeSeriesData.activity_counts?.slice(-12) || [],
        backgroundColor: '#667eea',
        borderRadius: 8,
      }
    ]
  };

  const riskTrendOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        title: { display: true, text: 'Risk Score', color: '#dc3545' },
        min: 0,
        max: 200,
      },
      y1: {
        position: 'right',
        title: { display: true, text: 'Activity Count', color: '#17a2b8' },
        grid: { drawOnChartArea: false },
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'bottom' },
      tooltip: { callbacks: { label: (context) => `${context.label}: ${context.raw} activities` } }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top' },
    },
    scales: {
      y: { title: { display: true, text: 'Number of Activities' }, beginAtZero: true }
    }
  };

  if (loading && !dashboard) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <h2>🔄 Loading RiskGuard System...</h2>
        <p>Connecting to backend at http://127.0.0.1:8000</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>❌ Connection Error</h2>
        <p>{error}</p>
        <button className="refresh-btn" onClick={loadAllData} style={{ marginTop: "20px" }}>
          🔄 Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="header">
        <h1>🛡️ RiskGuard Security Dashboard</h1>
        <p>Real-time Threat Detection & Auto-Response System</p>
        <div>
          <span className={`status-badge ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '🔴 LIVE Updates Active' : '📡 Live Updates Disconnected'}
          </span>
          <span className="status-badge" style={{ marginLeft: "10px", background: "#e9ecef", color: "#495057" }}>
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
        {realtimeData && (
          <div className="live-banner">
            ⚡ Live Activity Detected!
          </div>
        )}
      </div>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">📊 Total Activities</div>
          <div className="metric-value">{activities.length}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">👥 Active Users</div>
          <div className="metric-value">{dashboard?.metrics?.unique_users || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">⚠️ High Risk (24h)</div>
          <div className="metric-value" style={{ color: "#fd7e14" }}>
            {riskMetrics.highCount}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-title">🔥 Critical Risk</div>
          <div className="metric-value" style={{ color: "#dc3545" }}>
            {riskMetrics.criticalCount}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-title">🎯 Avg Risk Score</div>
          <div className="metric-value">{riskMetrics.avgRisk}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">🚨 Blocked Users</div>
          <div className="metric-value">{blockedUsers.length}</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        <div className="chart-container">
          <div className="chart-title">📈 Risk Trend Analysis (Last 24 Hours)</div>
          <Line data={riskTrendData} options={riskTrendOptions} height={80} />
        </div>
      </div>

      <div className="charts-row two-columns">
        <div className="chart-container">
          <div className="chart-title">🥧 Risk Distribution</div>
          <Pie data={riskDistributionData} options={pieOptions} height={200} />
        </div>
        <div className="chart-container">
          <div className="chart-title">📊 Activity Timeline (Last 12 Hours)</div>
          <Bar data={timelineData} options={barOptions} height={200} />
        </div>
      </div>

      {/* Recent Activities Table */}
      <div className="table-container">
        <h2>📋 Recent Activities</h2>
        {activities.length === 0 ? (
          <p style={{ textAlign: "center", padding: "20px" }}>
            No activities found. Use POST /analyze in Swagger UI to create some!
          </p>
        ) : (
          <table className="activity-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Action</th>
                <th>Login Attempts</th>
                <th>Records</th>
                <th>Hour</th>
                <th>Authenticated</th>
                <th>Risk Level</th>
                <th>Auto-Response</th>
              </tr>
            </thead>
            <tbody>
              {activities.slice(0, 10).map((activity, index) => {
                const riskScore = calculateRiskScore(activity);
                const isBlocked = blockedUsers.includes(activity.user_id);
                return (
                  <tr key={index} style={isBlocked ? { background: '#fff5f5' } : {}}>
                    <td><strong>{activity.user_id}</strong>{isBlocked && <span className="blocked-badge"> BLOCKED</span>}</td>
                    <td>{activity.action}</td>
                    <td>{activity.login_attempts}</td>
                    <td>{activity.records_accessed}</td>
                    <td>{formatHour(activity.hour)}</td>
                    <td>{activity.authenticated ? "✅ Yes" : "❌ No"}</td>
                    <td>
                      <span 
                        className="risk-badge"
                        style={{ backgroundColor: getRiskColor(riskScore) }}
                      >
                        {getRiskLabel(riskScore)} ({riskScore})
                      </span>
                    </td>
                    <td>
                      {riskScore >= 100 ? "🔒 BLOCKED" : riskScore >= 70 ? "⚠️ FLAGGED" : "✅ ALLOWED"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Alerts Panel with Active Threats Logic */}
      <div className="alerts-container">
        <h2>🚨 Security Alerts {wsConnected && <span className="live-badge">LIVE</span>}</h2>
        
        {hasActiveThreats ? (
          <>
            <div className="active-threats-banner">
              🚨 ACTIVE THREATS DETECTED! {riskMetrics.criticalCount} Critical, {riskMetrics.highCount} High
            </div>
            {alerts.length === 0 ? (
              <p>⚠️ Threats detected but alerts pending. Check responder agent for details.</p>
            ) : (
              alerts.slice(0, 10).map((alert, index) => (
                <div key={index} className={`alert ${getAlertClass(alert.severity)}`}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong>[{alert.severity || 'INFO'}]</strong>
                    <span style={{ fontSize: "11px", color: "#666" }}>
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ marginTop: "8px" }}>
                    {alert.message || 'Alert detected'}
                  </div>
                  {alert.actions && alert.actions.length > 0 && (
                    <div style={{ marginTop: "8px", fontSize: "12px", color: "#666" }}>
                      📋 Actions Taken: {alert.actions.map(a => a.message).join(", ")}
                    </div>
                  )}
                  {alert.user_id && (
                    <div style={{ marginTop: "5px", fontSize: "11px", color: "#999" }}>
                      👤 User: {alert.user_id} | Risk Score: {alert.risk_score}
                    </div>
                  )}
                </div>
              ))
            )}
          </>
        ) : (
          <p>✅ No active threats. System is secure!</p>
        )}
      </div>

      {/* Footer */}
      <div className="footer">
        <button className="refresh-btn" onClick={loadAllData}>
          🔄 Refresh Data
        </button>
      </div>
    </div>
  );
}