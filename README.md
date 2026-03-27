kdown
# 🛡️ RiskGuard System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org)
[![WebSocket](https://img.shields.io/badge/WebSocket-Ready-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

**An Advanced Security Monitoring System with 6 AI Agents**  
*Detecting Insider Threats & Validating AI Decisions Before Execution*

[Features](#-features) • [Demo](#-demo) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack)

</div>

---

## 🎯 The Problem This Solves

> **"The biggest security risks already have a badge and a password."**

In 2024, a major tech company faced a security breach when an AI agent gave flawed advice that an employee followed, exposing sensitive data for two hours. Traditional security systems trusted both the AI and the user blindly.

**RiskGuard solves this by:**
- ✅ **Monitoring** both human AND AI actions
- ✅ **Validating** AI decisions before execution
- ✅ **Auto-blocking** critical threats in real-time
- ✅ **Creating** immutable proof of all actions

---

## 🚀 Features

### 🤖 6 AI Agents Working Together

| Agent | Function | Innovation |
|-------|----------|------------|
| **🔍 MONITOR** | Tracks all user activities | Real-time session tracking |
| **📊 ANALYZER** | Detects anomalies using ML-like logic | Behavioral baselines |
| **🤖 AI OVERSIGHT** | **Validates AI decisions** | **YOUR UNIQUE FEATURE!** |
| **⚡ RESPONDER** | Auto-blocks threats | 1-second response time |
| **📜 AUDITOR** | Creates immutable proof | Blockchain-ready audit |
| **🧠 STRATEGIST** | Continuous learning | Adaptive improvement |

### 🔐 Security Features

- **JWT Authentication** with bcrypt hashing
- **Real-time Risk Scoring** (0-200 scale)
- **Auto-Response**: Automatically blocks CRITICAL risks
- **Multi-Layer Verification**: Requires 2+ approvals for dangerous actions
- **Session Locking** & IP Blocking

### 📊 Dashboard & Monitoring

- **Live WebSocket Updates** - No page refresh needed
- **Interactive Charts** - Risk trends, distribution, activity timeline
- **Real-time Alerts** with severity levels (Critical/High/Medium/Low)
- **Blocked Users Panel** - See who's automatically blocked

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────────┐
│ RISKGUARD SYSTEM │
├─────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ FRONTEND │ │ BACKEND │ │ DATABASE │ │
│ │ React + │◄──►│ FastAPI │◄──►│ SQLite │ │
│ │ Vite │ │ WebSocket │ │ │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 6 AI AGENTS │ │
│ ├────────────┬────────────┬────────────┬────────────┬─────────┤ │
│ │ MONITOR │ ANALYZER │AI OVERSIGHT│ RESPONDER │ AUDITOR │ │
│ └────────────┴────────────┴────────────┴────────────┴─────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ AUTO-RESPONSE ENGINE │ │
│ │ LOW → Allow | MEDIUM → Flag | HIGH → Alert | CRITICAL → Block │
│ └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

text

---

## 📊 Risk Scoring Formula
Risk Score = (Login × 10) + (Records × 0.5) + (Failed Auth × 50) + (Night Time × 20)

text

| Score Range | Risk Level | Auto-Response |
|-------------|------------|---------------|
| 0-19 | NORMAL | Allow, monitor |
| 20-39 | LOW RISK | Log only |
| 40-69 | MEDIUM RISK | Flag, notify |
| 70-99 | HIGH RISK | Alert, monitor closely |
| 100-200 | CRITICAL RISK | 🔒 **BLOCK & LOCK** |

**Example:** 6 login attempts + 120 records + failed auth + 2 AM = **CRITICAL (190)**

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.10+  |  Node.js 18+  |  Git
