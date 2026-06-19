"use client";

import { Polyline } from "react-leaflet";
import type { LatLngTuple } from "leaflet";

export default function RouteLayer({ route }: { route: LatLngTuple[] }) {
    return <Polyline positions={route} color="#00FF00" weight={4} opacity={0.8} />;
}