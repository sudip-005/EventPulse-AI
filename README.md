# 🚦 EventPulse AI

## AI-Powered Event-Driven Traffic Intelligence Platform

Predict traffic congestion before it happens and recommend operational actions for city authorities.

### 🎯 Features

- ✅ Event intelligence (impact & risk scoring)
- ✅ Traffic forecasting with XGBoost
- ✅ Congestion hotspot detection (DBSCAN/HDBSCAN)
- ✅ Route diversion engine (A*)
- ✅ What-if scenario simulator
- ✅ Resource recommendations (police, barricades, marshals)
- ✅ Interactive digital twin map
- ✅ Post-event learning & model retraining

### 🏗️ Architecture

- **Frontend**: Next.js 14, React, TypeScript, Tailwind, Leaflet
- **Backend**: FastAPI, Python, XGBoost, NetworkX, GeoPandas
- **Database**: PostgreSQL 15 + PostGIS
- **Deployment**: Docker, Railway/Render

### 🚀 Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd eventpulse-ai

# Start with Docker Compose
cd infrastructure/docker
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs