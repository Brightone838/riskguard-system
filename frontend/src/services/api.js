const API_BASE = "http://127.0.0.1:8000";

// REST API calls
export const analyzeActivity = async (data) => {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });
  return response.json();
};

export const getActivities = async () => {
  const response = await fetch(`${API_BASE}/activities`);
  return response.json();
};

export const getDashboard = async () => {
  const response = await fetch(`${API_BASE}/dashboard`);
  return response.json();
};

export const getAlerts = async () => {
  const response = await fetch(`${API_BASE}/alerts`);
  return response.json();
};

export const getSystemStats = async () => {
  const response = await fetch(`${API_BASE}/stats/system`);
  return response.json();
};

export const getTimeSeries = async () => {
  const response = await fetch(`${API_BASE}/dashboard/time-series`);
  return response.json();
};

// WebSocket connection
export class RiskGuardWebSocket {
  constructor(onMessage, onConnect, onDisconnect) {
    this.ws = null;
    this.onMessage = onMessage;
    this.onConnect = onConnect;
    this.onDisconnect = onDisconnect;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = `ws://127.0.0.1:8000/ws`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
      if (this.onConnect) this.onConnect();
      
      // Send ping every 30 seconds to keep connection alive
      setInterval(() => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000);
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📡 WebSocket message:', data.type);
      if (this.onMessage) this.onMessage(data);
    };

    this.ws.onclose = () => {
      console.log('❌ WebSocket disconnected');
      if (this.onDisconnect) this.onDisconnect();
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => this.connect(), 3000);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    }
  }
}