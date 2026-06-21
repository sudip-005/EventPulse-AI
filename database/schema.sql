CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name VARCHAR(255) NOT NULL,
  event_type VARCHAR(50) NOT NULL, description TEXT, location JSONB NOT NULL,
  address VARCHAR(255), estimated_attendance INTEGER, start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL, impact_score DOUBLE PRECISION, risk_score DOUBLE PRECISION,
  status VARCHAR(20) DEFAULT 'scheduled', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS roads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), road_id VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255), geometry JSONB NOT NULL, length_meters DOUBLE PRECISION,
  speed_limit_kmh INTEGER, capacity INTEGER, lanes INTEGER DEFAULT 2, road_type VARCHAR(50),
  one_way BOOLEAN DEFAULT FALSE, from_node VARCHAR(100), to_node VARCHAR(100), created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS traffic_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), road_id VARCHAR(100) NOT NULL,
  event_id UUID REFERENCES events(id) ON DELETE SET NULL, observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  congestion_score DOUBLE PRECISION NOT NULL DEFAULT 0, vehicle_density DOUBLE PRECISION,
  average_speed_kmh DOUBLE PRECISION, delay_minutes DOUBLE PRECISION, vehicle_count INTEGER,
  is_incident BOOLEAN DEFAULT FALSE, is_road_closed BOOLEAN DEFAULT FALSE,
  source VARCHAR(50) DEFAULT 'forecast', created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  prediction_timestamp TIMESTAMPTZ NOT NULL, forecast_timestamp TIMESTAMPTZ NOT NULL,
  impact_score DOUBLE PRECISION, impact_level VARCHAR(20), expected_duration_minutes DOUBLE PRECISION,
  closure_probability DOUBLE PRECISION, risk_score DOUBLE PRECISION, confidence DOUBLE PRECISION,
  top_factor_1 VARCHAR(100), top_factor_2 VARCHAR(100), top_factor_3 VARCHAR(100),
  model_version VARCHAR(50), features_used JSONB, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS hotspots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  cluster_id VARCHAR(100), center JSONB NOT NULL, severity INTEGER, affected_roads JSONB,
  radius_meters DOUBLE PRECISION, congestion_score DOUBLE PRECISION, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS simulations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  name VARCHAR(255), scenario_params JSONB NOT NULL, predicted_congestion JSONB, predicted_hotspots JSONB,
  recommendations JSONB, status VARCHAR(20) DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT NOW(), completed_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  simulation_id UUID REFERENCES simulations(id) ON DELETE SET NULL, resource_type VARCHAR(50),
  resource_count INTEGER, location JSONB, reasoning TEXT, priority INTEGER, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS learning_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  prediction_id UUID, predicted_impact DOUBLE PRECISION, actual_impact DOUBLE PRECISION, error DOUBLE PRECISION,
  mae DOUBLE PRECISION, rmse DOUBLE PRECISION, resource_effectiveness DOUBLE PRECISION,
  model_version VARCHAR(50), retraining_triggered BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS risk_assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  impact_score DOUBLE PRECISION NOT NULL, impact_level VARCHAR(20) NOT NULL, risk_score DOUBLE PRECISION NOT NULL,
  expected_duration_minutes DOUBLE PRECISION NOT NULL, closure_probability DOUBLE PRECISION NOT NULL,
  top_factor_1 VARCHAR(100), top_factor_2 VARCHAR(100), top_factor_3 VARCHAR(100), model_version VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_events_start_time ON events(start_time);
CREATE INDEX IF NOT EXISTS ix_traffic_data_road_id ON traffic_data(road_id);
CREATE INDEX IF NOT EXISTS ix_traffic_data_event_id ON traffic_data(event_id);
CREATE INDEX IF NOT EXISTS ix_predictions_event_id ON predictions(event_id);
CREATE INDEX IF NOT EXISTS ix_hotspots_event_id ON hotspots(event_id);
CREATE INDEX IF NOT EXISTS ix_recommendations_event_id ON recommendations(event_id);
CREATE INDEX IF NOT EXISTS ix_learning_records_event_id ON learning_records(event_id);
