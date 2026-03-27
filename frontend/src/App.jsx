import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import AIMonitor from './pages/AIMonitor';
import AgentDashboard from './pages/AgentDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';

function AppRoutes() {
  const { user, logout } = useAuth();

  return (
    <div>
      {user && (
        <div style={{
          background: '#667eea',
          color: 'white',
          padding: '10px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <span>👤 {user.username} {user.is_admin && '(Admin)'}</span>
            <a href="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>📊 Dashboard</a>
            <a href="/ai-monitor" style={{ color: 'white', textDecoration: 'none' }}>🤖 AI Monitor</a>
            <a href="/agents" style={{ color: 'white', textDecoration: 'none', background: '#5a67d8', padding: '5px 12px', borderRadius: '20px' }}>🤖 6 AI Agents</a>
          </div>
          <button 
            onClick={logout}
            style={{
              background: 'white',
              color: '#667eea',
              border: 'none',
              padding: '5px 15px',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      )}
      
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/ai-monitor" element={
          <ProtectedRoute>
            <AIMonitor />
          </ProtectedRoute>
        } />
        <Route path="/agents" element={
          <ProtectedRoute>
            <AgentDashboard />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;