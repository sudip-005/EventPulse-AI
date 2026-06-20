"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { 
    Activity, 
    Sliders, 
    CloudRain, 
    AlertOctagon, 
    CheckSquare, 
    RefreshCw, 
    Home, 
    Play,
    Info
} from "lucide-react";
import type { Event, Hotspot } from "@/lib/types";

// Load Map dynamically to avoid SSR "window is not defined" issues
const DigitalTwin = dynamic(() => import("@/components/maps/DigitalTwin"), { 
    ssr: false,
    loading: () => (
        <div className="w-full h-[500px] rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col items-center justify-center gap-3 text-slate-400">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            <span className="text-sm font-semibold">Initializing simulation twin...</span>
        </div>
    )
});

export default function SimulatorPage() {
    const [events, setEvents] = useState<Event[]>([]);
    const [selectedEventId, setSelectedEventId] = useState("");
    const [attendanceMult, setAttendanceMult] = useState(1.2);
    const [rain, setRain] = useState(false);
    const [closedRoads, setClosedRoads] = useState<string[]>([]);
    const [incidentLat, setIncidentLat] = useState<number | null>(null);
    const [incidentLon, setIncidentLon] = useState<number | null>(null);
    
    const [loading, setLoading] = useState(false);
    const [simulationResult, setSimulationResult] = useState<any>(null);
    const [roadNetwork, setRoadNetwork] = useState<any>(null);

    // Load available events and road network
    useEffect(() => {
        const loadData = async () => {
            try {
                const res = await fetch("/api/v1/events");
                if (res.ok) {
                    const data = await res.json();
                    setEvents(data);
                    if (data.length > 0) {
                        setSelectedEventId(data[0].id);
                    }
                }
                const resRoads = await fetch("/api/v1/routes/road-network");
                if (resRoads.ok) {
                    const data = await resRoads.json();
                    setRoadNetwork(data);
                }
            } catch (err) {
                console.error("Error loading simulator initial data:", err);
            }
        };
        loadData();
    }, []);

    // Handle running simulation
    const handleRunSimulation = async () => {
        if (!selectedEventId) return alert("Select an event model first");
        setLoading(true);
        try {
            const res = await fetch("/api/v1/simulation/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    event_id: selectedEventId,
                    scenario_params: {
                        attendance_multiplier: attendanceMult,
                        weather: rain ? { condition: "rain" } : {},
                        road_closures: closedRoads,
                        incident: incidentLat ? { location: [incidentLat, incidentLon] } : {}
                    }
                })
            });
            if (res.ok) {
                const data = await res.json();
                setSimulationResult(data);
            } else {
                alert("Failed to compute simulation");
            }
        } catch (err) {
            alert("Error connecting to simulation engine");
        } finally {
            setLoading(false);
        }
    };

    // Toggle road closure
    const handleRoadToggle = (roadId: string) => {
        setClosedRoads((prev) => 
            prev.includes(roadId) ? prev.filter(id => id !== roadId) : [...prev, roadId]
        );
    };

    // Handle map click to place incident epicenter
    const handleMapClick = (lat: number, lon: number) => {
        setIncidentLat(lat);
        setIncidentLon(lon);
    };

    // Clear incident
    const clearIncident = () => {
        setIncidentLat(null);
        setIncidentLon(null);
    };

    const activeEventObj = events.find(e => e.id === selectedEventId);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
            {/* Header */}
            <header className="border-b border-slate-900 bg-slate-950 px-6 py-4 flex items-center justify-between z-10">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <Activity className="w-6 h-6 text-blue-500 animate-pulse" />
                        <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                            EventPulse AI
                        </span>
                    </div>
                    <div className="h-4 w-px bg-slate-800" />
                    <span className="text-xs text-slate-400 font-mono uppercase tracking-widest">What-If Simulation Studio</span>
                </div>
                <nav className="flex items-center gap-4 text-sm text-slate-400">
                    <a href="/" className="hover:text-white">Home</a>
                    <a href="/command-center" className="hover:text-white">Command Center</a>
                    <a href="/dashboard" className="hover:text-white">Analytics</a>
                    <a href="/analytics" className="hover:text-white">Post-Event Learning</a>
                </nav>
            </header>

            {/* Content */}
            <main className="flex-1 grid grid-cols-12 gap-6 p-6 overflow-hidden">
                {/* Controls (Left Pane) */}
                <div className="col-span-12 lg:col-span-4 bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 flex flex-col gap-4 backdrop-blur-xl h-[600px] overflow-y-auto scrollbar-thin">
                    <div className="flex items-center gap-2 text-sm font-bold text-slate-300">
                        <Sliders className="w-4.5 h-4.5 text-blue-500" />
                        Scenario Configuration
                    </div>

                    {/* 1. Target Event */}
                    <div className="space-y-1">
                        <label className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Select Baseline Event</label>
                        <select
                            value={selectedEventId}
                            onChange={(e) => setSelectedEventId(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                        >
                            {events.map(e => (
                                <option key={e.id} value={e.id}>{e.name} ({e.event_type})</option>
                            ))}
                        </select>
                    </div>

                    {/* 2. Attendance slider */}
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                            <span>Attendance Adjuster</span>
                            <span className="text-blue-400 font-bold">{(attendanceMult * 100).toFixed(0)}%</span>
                        </div>
                        <input
                            type="range"
                            min="0.5"
                            max="2.0"
                            step="0.1"
                            value={attendanceMult}
                            onChange={(e) => setAttendanceMult(Number(e.target.value))}
                            className="w-full h-1 bg-slate-950 rounded-lg cursor-pointer accent-blue-500"
                        />
                        <div className="flex justify-between text-[8px] text-slate-600 font-mono">
                            <span>-50%</span>
                            <span>Normal (100%)</span>
                            <span>+100%</span>
                        </div>
                    </div>

                    {/* 3. Weather Toggle */}
                    <div className="space-y-1">
                        <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider block">Weather Impact</span>
                        <button
                            onClick={() => setRain(!rain)}
                            className={`w-full py-2.5 rounded-lg border text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                                rain 
                                    ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/10" 
                                    : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900"
                            }`}
                        >
                            <CloudRain className="w-4 h-4" />
                            {rain ? "Simulated Heavy Rain Active" : "Simulate Rain Conditions"}
                        </button>
                    </div>

                    {/* 4. Incident Placer */}
                    <div className="space-y-2 p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                        <span className="text-xs text-slate-400 font-bold block">Simulate Local Road Blockage</span>
                        <p className="text-[10px] text-slate-500 leading-normal">
                            Click anywhere on the map to place an accident or construction site, then execute simulation.
                        </p>
                        {incidentLat ? (
                            <div className="flex items-center justify-between text-[10px] bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
                                <span className="font-mono text-slate-300">Lat: {incidentLat.toFixed(4)}, Lon: {incidentLon?.toFixed(4)}</span>
                                <button onClick={clearIncident} className="text-red-500 hover:text-red-400 font-bold">Clear</button>
                            </div>
                        ) : (
                            <span className="text-[10px] text-slate-600 italic">No blockage coordinates selected</span>
                        )}
                    </div>

                    {/* 5. Road Closures */}
                    <div className="space-y-1 flex-1 flex flex-col min-h-[150px]">
                        <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider block">Barricade & Closure Layout</span>
                        <div className="border border-slate-800 rounded-xl bg-slate-950/60 p-2 space-y-1.5 flex-1 overflow-y-auto max-h-[150px] scrollbar-thin">
                            {Array.from({ length: 10 }).map((_, i) => {
                                const roadId = `road_0_${i}`; // Sample roads
                                const isChecked = closedRoads.includes(roadId);
                                return (
                                    <label key={roadId} className="flex items-center gap-2 text-[10px] text-slate-400 hover:text-slate-200 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={isChecked}
                                            onChange={() => handleRoadToggle(roadId)}
                                            className="rounded bg-slate-950 border-slate-800 text-blue-500 focus:ring-0"
                                        />
                                        Road 0-{i} (Arterial segment)
                                    </label>
                                );
                            })}
                        </div>
                    </div>

                    {/* Execute Trigger */}
                    <button
                        onClick={handleRunSimulation}
                        disabled={loading || !selectedEventId}
                        className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-bold transition-all shadow-xl shadow-blue-500/10 flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                Computing Traffic Shifts...
                            </>
                        ) : (
                            <>
                                <Play className="w-3.5 h-3.5" />
                                Execute What-If Trial
                            </>
                        )}
                    </button>
                </div>

                {/* Map Display & Dynamic Results (Right Pane) */}
                <div className="col-span-12 lg:col-span-8 flex flex-col space-y-4">
                    {/* Comparison KPI blocks */}
                    {simulationResult && activeEventObj && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl">
                                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Simulated Impact Score</span>
                                <div className="text-2xl font-black text-slate-200 mt-1 flex items-baseline gap-2">
                                    {simulationResult.modified_event.impact_score.toFixed(0)}%
                                    <span className="text-xs font-normal text-slate-500">
                                        (Base: {activeEventObj.impact_score.toFixed(0)}%)
                                    </span>
                                </div>
                            </div>
                            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl">
                                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Simulated Hotspots</span>
                                <div className="text-2xl font-black text-amber-500 mt-1">
                                    {simulationResult.predicted_hotspots.length} Clusters
                                </div>
                            </div>
                            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl">
                                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Resource Re-allocation</span>
                                <div className="text-2xl font-black text-purple-400 mt-1">
                                    Actionable Plan Ready
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Simulation Map Container */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-2 flex-1 backdrop-blur-xl relative min-h-[400px]">
                        <div className="absolute top-4 left-4 z-[1000] bg-slate-950/85 border border-slate-800 rounded-xl px-3 py-1.5 backdrop-blur-md text-[10px] flex items-center gap-1.5 text-slate-400">
                            <Info className="w-3.5 h-3.5 text-blue-500" />
                            Interact on the map. Red lines show simulated bottlenecks.
                        </div>

                        <div className="w-full h-full min-h-[420px]">
                            <DigitalTwin 
                                center={[19.0760, 72.8777]}
                                zoom={13}
                                events={activeEventObj ? [activeEventObj] : []}
                                hotspots={simulationResult ? simulationResult.predicted_hotspots : []}
                                roadNetwork={roadNetwork}
                                roadForecasts={simulationResult ? simulationResult.predicted_congestion.forecasts : []}
                                onMapClick={handleMapClick}
                                resources={simulationResult ? [
                                    ...(simulationResult.recommendations.police || []).map((r: any) => ({ ...r, resource_type: "Police" })),
                                    ...(simulationResult.recommendations.barricades || []).map((r: any) => ({ ...r, resource_type: "Barricades" })),
                                    ...(simulationResult.recommendations.marshals || []).map((r: any) => ({ ...r, resource_type: "Marshals" }))
                                ] : []}
                            />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}