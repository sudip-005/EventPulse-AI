-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Events Table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    address TEXT,
    estimated_attendance INTEGER,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    impact_score FLOAT,
    risk_score FLOAT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_events_location ON events USING GIST (location);
CREATE INDEX idx_events_time ON events (start_time, end_time);
CREATE INDEX idx_events_type ON events (event_type);

-- Roads Table
CREATE TABLE roads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    road_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    geometry GEOGRAPHY(LINESTRING, 4326) NOT NULL,
    length_meters FLOAT,
    speed_limit_kmh INTEGER,
    capacity INTEGER,
    lanes INTEGER DEFAULT 2,
    road_type VARCHAR(50),
    one_way BOOLEAN DEFAULT FALSE,
    from_node VARCHAR(100),
    to_node VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_roads_geometry ON roads USING GIST (geometry);
CREATE INDEX idx_roads_nodes ON roads (from_node, to_node);

-- Traffic Data
CREATE TABLE traffic_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    road_id VARCHAR(100) REFERENCES roads(road_id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    speed_kmh FLOAT,
    volume INTEGER,
    occupancy FLOAT,
    congestion_level INTEGER,
    weather_condition VARCHAR(50),
    temperature FLOAT,
    precipitation FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_traffic_road_time ON traffic_data (road_id, timestamp DESC);
CREATE INDEX idx_traffic_time ON traffic_data (timestamp DESC);

-- Predictions
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id),
    road_id VARCHAR(100) REFERENCES roads(road_id),
    prediction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    forecast_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    congestion_score FLOAT,
    predicted_speed FLOAT,
    predicted_volume INTEGER,
    delay_minutes INTEGER,
    confidence FLOAT,
    model_version VARCHAR(50),
    features_used JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_predictions_event ON predictions (event_id);
CREATE INDEX idx_predictions_road_time ON predictions (road_id, forecast_timestamp);
CREATE INDEX idx_predictions_forecast ON predictions (forecast_timestamp);

-- Hotspots
CREATE TABLE hotspots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id),
    cluster_id VARCHAR(100),
    center GEOGRAPHY(POINT, 4326),
    severity INTEGER,
    affected_roads JSONB,
    radius_meters FLOAT,
    congestion_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_hotspots_location ON hotspots USING GIST (center);
CREATE INDEX idx_hotspots_event ON hotspots (event_id);

-- Simulations
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id),
    name VARCHAR(255),
    scenario_params JSONB NOT NULL,
    predicted_congestion JSONB,
    predicted_hotspots JSONB,
    recommendations JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id),
    simulation_id UUID REFERENCES simulations(id),
    resource_type VARCHAR(50),
    resource_count INTEGER,
    location GEOGRAPHY(POINT, 4326),
    reasoning TEXT,
    priority INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_recommendations_event ON recommendations (event_id);

-- Learning Records
CREATE TABLE learning_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id),
    prediction_id UUID REFERENCES predictions(id),
    predicted_congestion FLOAT,
    actual_congestion FLOAT,
    error FLOAT,
    mae FLOAT,
    rmse FLOAT,
    resource_effectiveness FLOAT,
    model_version VARCHAR(50),
    retraining_triggered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_learning_event ON learning_records (event_id);