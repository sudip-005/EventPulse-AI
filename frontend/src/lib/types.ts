export interface Event {
    id: string;
    name: string;
    event_type: string;
    description?: string;
    location: {
        type: "Point";
        coordinates: [number, number]; // [lon, lat]
    };
    address?: string;
    estimated_attendance?: number;
    start_time: string;
    end_time: string;
    impact_score: number;
    risk_score: number;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface Hotspot {
    id: string;
    cluster_id: string;
    center: [number, number]; // [lat, lon]
    severity: number;
    point_count: number;
    radius_meters: number;
    avg_congestion: number;
    max_congestion: number;
    affected_roads: string[];
}

export interface Recommendation {
    id: string;
    resource_type: string;
    count: number;
    location: [number, number];
    reasoning: string;
    priority: number;
}