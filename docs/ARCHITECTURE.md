# EventPulse AI Architecture

## High-Level Diagram

(Insert diagram image if needed)

## System Components

### Frontend (Next.js)
- Server-side rendering, optimized for speed
- React components, Tailwind CSS
- Leaflet for interactive maps
- State management via React hooks

### Backend (FastAPI)
- RESTful API endpoints
- Modular services for each domain
- Asynchronous processing
- OpenAPI documentation at `/docs`

### Machine Learning (XGBoost)
- Feature engineering pipeline
- Model trained on historical traffic, weather, events
- Inference service for real-time predictions

### Geospatial
- PostgreSQL + PostGIS for spatial data
- NetworkX for road graph analysis
- DBSCAN/HDBSCAN for hotspot detection

### Simulation Engine
- What-if scenario modification
- Reuses prediction engine
- Outputs updated forecasts and recommendations

### Digital Twin
- Lightweight visualisation of roads, events, traffic
- Leaflet/Mapbox integration
- Real-time updates via API polling

## Data Flow

1. Event Created -> Impact/Risk Scoring
2. Forecast Request -> Feature Vector -> XGBoost Predictions
3. Hotspot Detection -> Clustering on high-congestion points
4. Route Diversion -> Graph search with congestion weights
5. Simulation -> Modify event parameters, regenerate forecasts
6. Recommendations -> Rule-based resource allocation
7. Learning -> Store predictions vs actuals, compute metrics, trigger retraining

## Deployment

Docker Compose for local development. Production uses Railway/Render with environment variables.

## Scalability Considerations

- PostgreSQL indexes for spatial and time queries
- Caching layer (Redis) for repeated predictions
- Asynchronous task queue (Celery) for heavy simulations
- Horizontal scaling via container orchestration