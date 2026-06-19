"use client";

import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import type { Event, Hotspot } from "@/lib/types";

// Fix default marker icons
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
    trafficData?: any[];
}

export default function DigitalTwin({
    center,
    zoom,
    events = [],
    hotspots = [],
    trafficData = [],
}: DigitalTwinProps) {
    return (
        <MapContainer
            center={center}
            zoom={zoom}
            className="w-full h-[500px] rounded-lg"
            zoomControl={false}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; OpenStreetMap contributors'
            />
            {/* Events */}
            {events.map((ev) => (
                <CircleMarker
                    key={ev.id}
                    center={[ev.location.coordinates[1], ev.location.coordinates[0]]}
                    radius={12}
                    pathOptions={{ color: "#FF4444", fillColor: "#FF4444", fillOpacity: 0.6 }}
                >
                    <Popup>
                        <b>{ev.name}</b><br />
                        Type: {ev.event_type}<br />
                        Attendance: {ev.estimated_attendance?.toLocaleString()}<br />
                        Impact: {ev.impact_score.toFixed(1)}%
                    </Popup>
                </CircleMarker>
            ))}
            {/* Hotspots */}
            {hotspots.map((h) => (
                <CircleMarker
                    key={h.id}
                    center={[h.center[0], h.center[1]]}
                    radius={h.severity * 3 + 5}
                    pathOptions={{
                        color: "#FF9800",
                        fillColor: "#FF9800",
                        fillOpacity: 0.3,
                    }}
                >
                    <Popup>
                        <b>Hotspot</b><br />
                        Severity: {h.severity}/5<br />
                        Congestion: {h.avg_congestion.toFixed(1)}%
                    </Popup>
                </CircleMarker>
            ))}
        </MapContainer>
    );
}