INSERT INTO events (id, name, event_type, description, location, address, estimated_attendance, start_time, end_time, impact_score, risk_score, status)
VALUES ('11111111-1111-4111-8111-111111111111', 'Mumbai Innovation Festival', 'festival',
  'Demo event for the EventPulse AI Railway deployment', '{"type":"Point","coordinates":[72.8777,19.0760]}'::jsonb,
  'Mumbai, Maharashtra', 12000, NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day 4 hours', 72, 68, 'scheduled')
ON CONFLICT (id) DO NOTHING;

INSERT INTO roads (id, road_id, name, geometry, length_meters, speed_limit_kmh, capacity, lanes, road_type, one_way, from_node, to_node)
VALUES ('22222222-2222-4222-8222-222222222222', 'demo-road-1', 'Innovation Avenue',
  '{"type":"LineString","coordinates":[[72.872,19.073],[72.884,19.081]]}'::jsonb,
  1500, 50, 1800, 2, 'primary', false, 'demo-a', 'demo-b')
ON CONFLICT (road_id) DO NOTHING;
