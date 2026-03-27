"""
RISK FORMULA EXPLANATION

Risk Score = (Login Attempts × 10) + (Records Accessed × 0.5) + (Failed Auth × 50) + (Time Anomaly × 20)

Where:
- Login Attempts: Number of failed login attempts (max 10)
- Records Accessed: Number of records accessed in one session
- Failed Auth: 1 if authentication failed, 0 if successful
- Time Anomaly: 1 if hour is outside 6-22, 0 if within normal hours

Example Calculation:
Input: login_attempts=6, records_accessed=120, authenticated=false, hour=2

Risk Score = (6 × 10) + (120 × 0.5) + (1 × 50) + (1 × 20)
          = 60 + 60 + 50 + 20
          = 190 (capped at 200)

Risk Levels:
- 0-19: NORMAL
- 20-39: LOW RISK
- 40-69: MEDIUM RISK
- 70-99: HIGH RISK
- 100-200: CRITICAL RISK
"""

def calculate_risk_score(login_attempts: int, records_accessed: int, authenticated: bool, hour: int) -> dict:
    """
    Calculate risk score with full explanation
    """
    # Individual components
    login_component = min(login_attempts * 10, 100)  # Max 100
    records_component = min(records_accessed * 0.5, 80)  # Max 80
    auth_component = 50 if not authenticated else 0
    time_component = 20 if (hour < 6 or hour > 22) else 0
    
    # Total score (capped at 200)
    total_score = min(login_component + records_component + auth_component + time_component, 200)
    
    # Determine risk level
    if total_score >= 100:
        risk_level = "CRITICAL"
    elif total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
        risk_level = "MEDIUM"
    elif total_score >= 20:
        risk_level = "LOW"
    else:
        risk_level = "NORMAL"
    
    return {
        "risk_score": total_score,
        "risk_level": risk_level,
        "breakdown": {
            "login_attempts": f"{login_attempts} × 10 = {login_component}",
            "records_accessed": f"{records_accessed} × 0.5 = {records_component}",
            "authentication_failure": f"{'Yes' if not authenticated else 'No'} = {auth_component}",
            "unusual_hour": f"{'Yes' if time_component > 0 else 'No'} = {time_component}"
        },
        "formula": "Risk = (Login × 10) + (Records × 0.5) + (Failed Auth × 50) + (Night Time × 20)"
    }