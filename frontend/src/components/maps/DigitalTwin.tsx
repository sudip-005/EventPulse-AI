"use client";

import { useEffect, useState } from "react";
import { 
    MapContainer, 
    TileLayer, 
    GeoJSON, 
    CircleMarker, 
    Popup, 
    Polyline, 
    Marker, 
    useMapEvents 
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import HeatmapLayer from "./HeatmapLayer";
import type { Event, Hotspot } from "@/lib/types";

// Fix default marker icons for Next.js Leaflet rendering
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

interface DigitalTwinProps {
    center: [number, number];
    zoom: number;
    events?: Event[];
    hotspots?: Hotspot[];
    roadNetwork?: any; // GeoJSON road network
    roadForecasts?: any[]; // Congestion scores per road
    primaryRoute?: [number, number][];
    alternativeRoutes?: [number, number][][];
    onMapClick?: (lat: number, lon: number) => void;
    originPoint?: [number, number] | null;
    destinationPoint?: [number, number] | null;
    resources?: any[];
}

function MapClickManager({ onMapClick }: { onMapClick?: (lat: number, lon: number) => void }) {
    useMapEvents({
        click(e) {
            if (onMapClick) {
                onMapClick(e.latlng.lat, e.latlng.lng);
            }
        }
    });
    return null;
}

export default function DigitalTwin({
    center,
    zoom,
    events = [],
    hotspots = [],
    roadNetwork = null,
    roadForecasts = [],
    primaryRoute = [],
    alternativeRoutes = [],
    onMapClick,
    originPoint = null,
    destinationPoint = null,
    resources = []
}: DigitalTwinProps) {
    const [pulseRadius, setPulseRadius] = useState(12);
    const [layers, setLayers] = useState({
        events: true,
        hotspots: true,
        heatmap: false,
        roads: true,
        routes: true,
        resources: true,
    });

    const toggleLayer = (key: keyof typeof layers) =>
        setLayers(prev => ({ ...prev, [key]: !prev[key] }));

    // Pulse effect animation for hotspots
    useEffect(() => {
        const interval = setInterval(() => {
            setPulseRadius((prev) => (prev === 12 ? 18 : 12));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    // Helper to get congestion color
    const getCongestionColor = (score: number) => {
        if (score >= 70) return "#EF4444"; // Severe red
        if (score >= 40) return "#F59E0B"; // Moderate orange
        return "#10B981"; // Clear green
    };

    // Helper to style road features based on simulated or real congestion forecast
    const getRoadStyle = (feature: any) => {
        const roadId = feature.properties?.road_id;
        const forecast = roadForecasts.find((f) => f.road_id === roadId);
        const score = forecast ? forecast.congestion_score : 15; // default low baseline
        return {
            color: getCongestionColor(score),
            weight: forecast && forecast.congestion_score > 40 ? 5 : 3,
            opacity: 0.85
        };
    };

    return (
        <div className="w-full h-full relative">
            <MapContainer
                center={center}
                zoom={zoom}
                className="w-full h-[600px] rounded-2xl overflow-hidden border border-slate-800 bg-slate-950"
                zoomControl={true}
            >
                {/* Futuristic Dark Matter CartoDB Basemap */}
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                />

                <MapClickManager onMapClick={onMapClick} />

                {/* Road Network Layer */}
                {roadNetwork && (
                    <GeoJSON 
                        data={roadNetwork} 
                        style={getRoadStyle}
                        onEachFeature={(feature, layer) => {
                            const roadId = feature.properties?.road_id;
                            const roadName = feature.properties?.name || "Unnamed Road";
                            const forecast = roadForecasts.find((f) => f.road_id === roadId);
                            const score = forecast ? forecast.congestion_score.toFixed(0) : "15";
                            const speed = forecast ? forecast.predicted_speed.toFixed(0) : "50";
                            const density = forecast?.vehicle_density != null ? forecast.vehicle_density.toFixed(0) : "N/A";
                            layer.bindPopup(
                                `<div class="text-xs text-slate-800">
                                    <b>${roadName}</b><br/>
                                    Congestion: <b>${score}%</b><br/>
                                    Current Speed: <b>${speed} km/h</b><br/>
                                    Vehicle Density: <b>${density} veh/km</b>
                                 </div>`
                            );
                        }}
                    />
                )}

                {/* Primary Route Diversion (Vibrant Green) */}
                {primaryRoute.length > 0 && (
                    <Polyline 
                        positions={primaryRoute} 
                        color="#10B981" 
                        weight={6} 
                        opacity={0.9} 
                        dashArray="2, 6"
                        className="animate-[dash_2s_linear_infinite]"
                    >
                        <Popup><b className="text-slate-800">Primary Route</b></Popup>
                    </Polyline>
                )}

                {/* Alternative Routes (Vibrant Orange / Cyan) */}
                {alternativeRoutes.map((route, idx) => (
                    <Polyline 
                        key={idx} 
                        positions={route} 
                        color={idx === 0 ? "#3B82F6" : "#EC4899"} // Cyan / Pink
                        weight={5} 
                        opacity={0.8}
                        dashArray="10, 10"
                    >
                        <Popup><b className="text-slate-800">Alternative Route {idx + 1}</b></Popup>
                    </Polyline>
                ))}

                {/* Origin Marker */}
                {originPoint && (
                    <CircleMarker 
                        center={originPoint} 
                        radius={8} 
                        pathOptions={{ color: "#3B82F6", fillColor: "#3B82F6", fillOpacity: 0.9 }}
                    >
                        <Popup><span className="text-slate-800">Routing Origin</span></Popup>
                    </CircleMarker>
                )}

                {/* Destination Marker */}
                {destinationPoint && (
                    <CircleMarker 
                        center={destinationPoint} 
                        radius={8} 
                        pathOptions={{ color: "#10B981", fillColor: "#10B981", fillOpacity: 0.9 }}
                    >
                        <Popup><span className="text-slate-800">Routing Destination</span></Popup>
                    </CircleMarker>
                )}

                {/* Heatmap Layer (Canvas-rendered intensity) */}
                {layers.heatmap && hotspots.length > 0 && (
                    <HeatmapLayer
                        points={hotspots.map(h => ({
                            lat: h.center[0],
                            lon: h.center[1],
                            intensity: h.avg_congestion / 100
                        }))}
                        radius={40}
                        blur={18}
                    />
                )}

                {/* Hotspots (Pulsing glowing circles) */}
                {layers.hotspots && hotspots.map((h) => (
                    <CircleMarker
                        key={h.id || h.cluster_id}
                        center={[h.center[0], h.center[1]]}
                        radius={h.severity * 5 + pulseRadius}
                        pathOptions={{
                            color: h.severity >= 4 ? "#EF4444" : "#F59E0B",
                            fillColor: h.severity >= 4 ? "#EF4444" : "#F59E0B",
                            fillOpacity: 0.25,
                            weight: 1
                        }}
                    >
                        <Popup>
                            <div className="text-xs text-slate-800">
                                <b>Traffic Hotspot</b><br />
                                Severity: <b>{h.severity}/5</b><br />
                                Congestion: <b>{h.avg_congestion.toFixed(0)}%</b><br />
                                Impact Radius: <b>{h.radius_meters.toFixed(0)}m</b>
                            </div>
                        </Popup>
                    </CircleMarker>
                ))}

                {/* Event Markers */}
                {layers.events && events.map((ev) => (
                    <CircleMarker
                        key={ev.id}
                        center={[ev.location.coordinates[1], ev.location.coordinates[0]]}
                        radius={14}
                        pathOptions={{ 
                            color: ev.risk_score >= 70 ? "#EF4444" : "#3B82F6", 
                            fillColor: ev.risk_score >= 70 ? "#EF4444" : "#3B82F6", 
                            fillOpacity: 0.7,
                            weight: 2
                        }}
                    >
                        <Popup>
                            <div className="text-xs text-slate-800">
                                <b className="text-sm">{ev.name}</b><br />
                                Type: <b>{ev.event_type}</b><br />
                                Attendance: <b>{ev.estimated_attendance?.toLocaleString()}</b><br />
                                Risk: <b>{ev.risk_score.toFixed(0)}%</b><br />
                                Impact: <b>{ev.impact_score.toFixed(0)}%</b>
                            </div>
                        </Popup>
                    </CircleMarker>
                ))}

                {/* Resource Deployment Markers */}
                {layers.resources && resources.map((r, idx) => (
                    <CircleMarker
                        key={idx}
                        center={r.location}
                        radius={6}
                        pathOptions={{
                            color: "#8B5CF6", // Purple for resources
                            fillColor: "#8B5CF6",
                            fillOpacity: 0.9,
                            weight: 1
                        }}
                    >
                        <Popup>
                            <div className="text-xs text-slate-800">
                                <b>Deploy Resource</b><br />
                                Resource: <b>{r.resource_type}</b><br />
                                Count: <b>{r.count}</b><br />
                                Reason: <i>{r.reasoning}</i>
                            </div>
                        </Popup>
                    </CircleMarker>
                ))}
            </MapContainer>

            {/* Layer Toggle Controls - Top Left */}
            <div className="absolute top-4 left-4 bg-slate-950/85 border border-slate-800 rounded-xl p-3 backdrop-blur-md z-[1000] text-[10px] space-y-1.5">
                <div className="font-bold text-slate-400 uppercase tracking-wider text-[9px] mb-2">Layer Controls</div>
                {([
                    ["events", "Events", "#3B82F6"],
                    ["hotspots", "Hotspots", "#EF4444"],
                    ["heatmap", "Heatmap", "#F59E0B"],
                    ["roads", "Roads", "#6B7280"],
                    ["routes", "Routes", "#10B981"],
                    ["resources", "Resources", "#8B5CF6"],
                ] as [keyof typeof layers, string, string][]).map(([key, label, color]) => (
                    <button
                        key={key}
                        onClick={() => toggleLayer(key)}
                        className={`w-full flex items-center gap-2 px-2 py-1 rounded-lg text-left transition-all ${
                            layers[key]
                                ? "bg-slate-800/80 text-slate-200"
                                : "text-slate-600 hover:text-slate-400"
                        }`}
                    >
                        <div
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{ backgroundColor: layers[key] ? color : "#374151" }}
                        />
                        {label}
                    </button>
                ))}
            </div>

            {/* Map Overlay Custom Legend - Bottom Right */}
            <div className="absolute bottom-4 right-4 bg-slate-950/80 border border-slate-800 rounded-xl p-3 backdrop-blur-md z-[1000] text-[10px] space-y-2 max-w-[190px]">
                <div className="font-bold text-slate-400 uppercase tracking-wider text-[9px] mb-1">Traffic Forecast Legend</div>
                <div className="flex items-center gap-2">
                    <div className="w-3.5 h-1 rounded bg-[#EF4444]" />
                    <span className="text-slate-300">Severe Congestion (&gt;70%)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3.5 h-1 rounded bg-[#F59E0B]" />
                    <span className="text-slate-300">Moderate Traffic (40-70%)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3.5 h-1 rounded bg-[#10B981]" />
                    <span className="text-slate-300">Clear Flow (&lt;40%)</span>
                </div>
                <div className="h-px bg-slate-800 my-1" />
                <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/30 border border-red-500" />
                    <span className="text-slate-300">Hotspot Radius (Pulsing)</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-blue-500 border border-white" />
                    <span className="text-slate-300">Event epicenter</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3.5 h-1 bg-emerald-500 border-t border-dashed" />
                    <span className="text-slate-300">Primary Diversion</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3.5 h-1 bg-blue-500 border-t border-dashed" />
                    <span className="text-slate-300">Alternative Route</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-purple-500" />
                    <span className="text-slate-300">Resource / Ambulance</span>
                </div>
            </div>
        </div>
    );
}