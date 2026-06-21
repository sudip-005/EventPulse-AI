"use client";

import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";

interface HeatmapPoint {
    lat: number;
    lon: number;
    intensity: number; // 0–1
}

interface HeatmapLayerProps {
    points: HeatmapPoint[];
    radius?: number;
    blur?: number;
    maxZoom?: number;
}

/**
 * Leaflet heatmap layer using a pure Canvas 2D rendering approach.
 * Renders a kernel-density-style heatmap without external dependencies.
 */
export default function HeatmapLayer({
    points,
    radius = 30,
    blur = 20,
    maxZoom = 18
}: HeatmapLayerProps) {
    const map = useMap();
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const layerRef = useRef<L.Layer | null>(null);

    useEffect(() => {
        if (!map || points.length === 0) return;

        // Remove existing layer
        if (layerRef.current) {
            map.removeLayer(layerRef.current as L.Layer);
        }

        // Create a custom Leaflet canvas layer
        const HeatLayer = L.Layer.extend({
            initialize() {
                this._canvas = null;
            },
            onAdd(map: L.Map) {
                this._map = map;
                this._canvas = L.DomUtil.create("canvas", "leaflet-heatmap-canvas") as HTMLCanvasElement;
                const size = map.getSize();
                this._canvas.width = size.x;
                this._canvas.height = size.y;
                this._canvas.style.position = "absolute";
                this._canvas.style.top = "0";
                this._canvas.style.left = "0";
                this._canvas.style.pointerEvents = "none";
                this._canvas.style.zIndex = "500";
                this._canvas.style.opacity = "0.75";
                map.getPanes().overlayPane.appendChild(this._canvas);

                map.on("moveend zoomend", this._redraw, this);
                this._redraw();
                return this;
            },
            onRemove(map: L.Map) {
                map.off("moveend zoomend", this._redraw, this);
                if (this._canvas && this._canvas.parentNode) {
                    this._canvas.parentNode.removeChild(this._canvas);
                }
            },
            _redraw() {
                if (!this._canvas) return;
                const canvas = this._canvas as HTMLCanvasElement;
                const size = this._map.getSize();
                canvas.width = size.x;
                canvas.height = size.y;

                const ctx = canvas.getContext("2d");
                if (!ctx) return;
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Create offscreen canvas to draw raw radial gradients
                const offscreen = document.createElement("canvas");
                offscreen.width = size.x;
                offscreen.height = size.y;
                const offCtx = offscreen.getContext("2d");
                if (!offCtx) return;

                // Draw each point as a radial gradient on offscreen canvas
                for (const pt of points) {
                    const projected = this._map.latLngToContainerPoint(L.latLng(pt.lat, pt.lon));
                    const r = Math.max(radius, 15);
                    const gradient = offCtx.createRadialGradient(
                        projected.x, projected.y, 0,
                        projected.x, projected.y, r
                    );
                    const alpha = Math.min(pt.intensity, 1.0);

                    // Smooth radial gradient color map (using softer colors)
                    // High intensity: red/rose, Medium: orange, Low: green/teal
                    if (pt.intensity > 0.7) {
                        gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha})`);
                        gradient.addColorStop(0.3, `rgba(239, 68, 68, ${alpha * 0.4})`);
                    } else if (pt.intensity > 0.4) {
                        gradient.addColorStop(0, `rgba(245, 158, 11, ${alpha})`);
                        gradient.addColorStop(0.3, `rgba(245, 158, 11, ${alpha * 0.4})`);
                    } else {
                        gradient.addColorStop(0, `rgba(16, 185, 129, ${alpha})`);
                        gradient.addColorStop(0.3, `rgba(16, 185, 129, ${alpha * 0.4})`);
                    }
                    gradient.addColorStop(1, "rgba(0,0,0,0)");

                    offCtx.beginPath();
                    offCtx.fillStyle = gradient;
                    offCtx.arc(projected.x, projected.y, r, 0, Math.PI * 2);
                    offCtx.fill();
                }

                // Draw the offscreen canvas onto the main canvas with filter applied
                ctx.save();
                if (blur > 0) {
                    ctx.filter = `blur(${blur}px)`;
                }
                ctx.drawImage(offscreen, 0, 0);
                ctx.restore();

                // Position canvas correctly relative to map origin
                const topLeft = this._map.containerPointToLayerPoint([0, 0]);
                L.DomUtil.setPosition(canvas, topLeft);
            }
        });

        const layer = new (HeatLayer as any)();
        layer.addTo(map);
        layerRef.current = layer;
        canvasRef.current = layer._canvas;

        return () => {
            if (layerRef.current) {
                map.removeLayer(layerRef.current);
                layerRef.current = null;
            }
        };
    }, [map, points, radius, blur]);

    return null;
}
