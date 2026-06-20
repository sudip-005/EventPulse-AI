"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { 
    Activity, 
    AlertOctagon, 
    Clock, 
    MapPin, 
    Navigation, 
    Plus, 
    ShieldAlert, 
    Sliders, 
    TrendingUp, 
    Users, 
    RefreshCw, 
    ArrowRight,
    Map
} from "lucide-react";
import type { Event, Hotspot, Recommendation } from "@/lib/types";

// Load Map dynamically to avoid SSR "window is not defined" issues
const DigitalTwin = dynamic(() => import("@/components/maps/DigitalTwin"), { 
    ssr: false,
    loading: () => (
        <div className="w-full h-[600px] rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col items-center justify-center gap-3 text-slate-400">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            <span className="text-sm font-semibold">Initializing digital twin layers...</span>
        </div>
    )
});

export default function CommandCenter() {
    const [events, setEvents] = useState<Event[]>([]);
    const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
    const [hotspots, setHotspots] = useState<Hotspot[]>([]);
    const [roadNetwork, setRoadNetwork] = useState<any>(null);
    const [roadForecasts, setRoadForecasts] = useState<any[]>([]);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    // Event form state
    const [name, setName] = useState("");
    const [type, setType] = useState("concert");
    const [attendance, setAttendance] = useState(15000);
    const [address, setAddress] = useState("Mumbai Hub");
    const [startTime, setStartTime] = useState("");
    const [endTime, setEndTime] = useState("");
    const [latitude, setLatitude] = useState(19.0760);
    const [longitude, setLongitude] = useState(72.8777);

    // Routing state
    const [routingMode, setRoutingMode] = useState<"none" | "origin" | "destination">("none");
    const [originPoint, setOriginPoint] = useState<[number, number] | null>(null);
    const [destinationPoint, setDestinationPoint] = useState<[number, number] | null>(null);
    const [primaryRoute, setPrimaryRoute] = useState<[number, number][]>([]);
    const [alternativeRoutes, setAlternativeRoutes] = useState<[number, number][][]>([]);
    const [routeStats, setRouteStats] = useState<any>(null);

    // Timeline state
    const [forecastHour, setForecastHour] = useState(0);

    // Set default times on mount
    useEffect(() => {
        const now = new Date();
        const start = new Date(now.getTime() + 2 * 24 * 3600 * 1000); // 2 days later
        start.setHours(18, 0, 0, 0);
        const end = new Date(start.getTime() + 4 * 3600 * 1000); // 4 hours duration
        setStartTime(start.toISOString().slice(0, 16));
        setEndTime(end.toISOString().slice(0, 16));
    }, []);

    // Load initial events and road network
    useEffect(() => {
        const loadInitialData = async () => {
            try {
                // Fetch events
                const resEvents = await fetch("/api/v1/events");
                if (resEvents.ok) {
                    const data = await resEvents.json();
                    setEvents(data);
                    if (data.length > 0 && !selectedEvent) {
                        setSelectedEvent(data[0]);
                    }
                }
                // Fetch GeoJSON road network
                const resRoads = await fetch("/api/v1/routes/road-network");
                if (resRoads.ok) {
                    const data = await resRoads.json();
                    setRoadNetwork(data);
                }
            } catch (err) {
                console.error("Error loading initial Command Center data:", err);
            }
        };
        loadInitialData();
    }, [refreshTrigger]);

    // Handle analysis when selectedEvent changes
    useEffect(() => {
        if (!selectedEvent) return;
        const analyzeSelectedEvent = async () => {
            try {
                // 1. Fetch/Generate forecast
                const resForecast = await fetch(`/api/v1/forecast/${selectedEvent.id}`);
                if (resForecast.ok) {
                    const data = await resForecast.json();
                    // If multiple predictions returned, take first
                    const prediction = Array.isArray(data) ? data[0] : data;
                    if (prediction && prediction.roads) {
                        setRoadForecasts(prediction.roads);
                    }
                }
                // 2. Fetch hotspots
                const resHotspots = await fetch(`/api/v1/hotspots/event/${selectedEvent.id}`);
                if (resHotspots.ok) {
                    const data = await resHotspots.json();
                    setHotspots(data);
                }
                // 3. Fetch resource recommendations
                const resRecs = await fetch(`/api/v1/recommendations/event/${selectedEvent.id}`);
                if (resRecs.ok) {
                    const data = await resRecs.json();
                    setRecommendations(data);
                }
            } catch (err) {
                console.error("Error analyzing event:", err);
            }
        };
        analyzeSelectedEvent();
    }, [selectedEvent, refreshTrigger]);

    // Apply timeline slider (simulate traffic shift over hours)
    useEffect(() => {
        if (roadForecasts.length === 0) return;
        // Peak hours multiplier (e.g. rush hour is +2 to +4 hours after start)
        const shiftedForecasts = roadForecasts.map((rf) => {
            // Baseline shift depending on current slider hour
            let mult = 1.0;
            if (forecastHour >= 2 && forecastHour <= 4) {
                mult = 1.35; // Peak congestion hour
            } else if (forecastHour > 6) {
                mult = 0.65; // Traffic clearing
            }
            return {
                ...rf,
                congestion_score: Math.min(rf.congestion_score * mult, 100)
            };
        });
        setRoadForecasts(shiftedForecasts);
    }, [forecastHour]);

    // Handle map click
    const handleMapClick = (lat: number, lon: number) => {
        if (routingMode === "origin") {
            setOriginPoint([lat, lon]);
            setRoutingMode("none");
        } else if (routingMode === "destination") {
            setDestinationPoint([lat, lon]);
            setRoutingMode("none");
        } else {
            // Default: update coordinates in event form
            setLatitude(lat);
            setLongitude(lon);
        }
    };

    // Calculate dynamic routing
    const calculateRoute = async () => {
        if (!originPoint || !destinationPoint) return alert("Select origin and destination first");
        setLoading(true);
        try {
            const res = await fetch("/api/v1/routes/find", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    origin: originPoint,
                    destination: destinationPoint,
                    num_routes: 3,
                    avoid_hotspots: true,
                    event_id: selectedEvent?.id
                })
            });
            if (res.ok) {
                const data = await res.json();
                const routeInfo = data[0];
                if (routeInfo) {
                    setPrimaryRoute(routeInfo.primary.coordinates);
                    setAlternativeRoutes(routeInfo.alternatives.map((alt: any) => alt.coordinates));
                    setRouteStats(routeInfo);
                }
            } else {
                alert("Failed to calculate routes");
            }
        } catch (err) {
            alert("Error connecting to routing service");
        } finally {
            setLoading(false);
        }
    };

    // Reset routing overlay
    const clearRoutes = () => {
        setOriginPoint(null);
        setDestinationPoint(null);
        setPrimaryRoute([]);
        setAlternativeRoutes([]);
        setRouteStats(null);
    };

    // Handle Event Submit
    const handleEventCreateSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        const payload = {
            name,
            event_type: type,
            estimated_attendance: attendance,
            start_time: new Date(startTime).toISOString(),
            end_time: new Date(endTime).toISOString(),
            address,
            location: {
                type: "Point",
                coordinates: [longitude, latitude], // PostGIS uses [lon, lat]
            },
        };
        try {
            const res = await fetch("/api/v1/events", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                const newEv = await res.json();
                setEvents((prev) => [newEv, ...prev]);
                setSelectedEvent(newEv);
                setName("");
                setAddress("Mumbai Hub");
                setRefreshTrigger((prev) => prev + 1);
            } else {
                alert("Error creating event");
            }
        } catch (err) {
            alert("Connection error creating event");
        } finally {
            setLoading(false);
        }
    };

    // Calculate aggregated KPIs for the top bar
    const activeEventsCount = events.filter(e => e.status === "scheduled" || e.status === "active").length;
    const highRiskEventsCount = events.filter(e => e.risk_score >= 60).length;
    const activeHotspotsCount = hotspots.length;
    const avgDelay = roadForecasts.length > 0 
        ? (roadForecasts.reduce((acc, rf) => acc + rf.delay_minutes, 0) / roadForecasts.length * 60).toFixed(0)
        : "0";

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
                    <span className="text-xs text-slate-400 font-mono uppercase tracking-widest">Smart City Ops Room</span>
                </div>
                <div className="flex items-center gap-6 text-sm text-slate-400">
                    <button 
                        onClick={() => setRefreshTrigger(prev => prev + 1)}
                        className="hover:text-white flex items-center gap-2 border border-slate-800 rounded-lg px-3 py-1.5 bg-slate-900/40 hover:bg-slate-900 transition-colors"
                    >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Reload Center
                    </button>
                    <nav className="flex items-center gap-4">
                        <a href="/" className="hover:text-white">Home</a>
                        <a href="/simulator" className="hover:text-white">Simulator</a>
                        <a href="/dashboard" className="hover:text-white">Analytics</a>
                        <a href="/analytics" className="hover:text-white">Post-Event Learning</a>
                    </nav>
                </div>
            </header>

            {/* Main Command Center Grid */}
            <main className="flex-1 grid grid-cols-12 gap-6 p-6 overflow-hidden">
                {/* 1. TOP KPI BAR (Full Width) */}
                <div className="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[
                        { label: "Active Event Monitors", value: activeEventsCount, icon: Users, color: "text-blue-400", border: "border-blue-500/20" },
                        { label: "High Risk Incident Scenarios", value: highRiskEventsCount, icon: ShieldAlert, color: "text-red-500", border: "border-red-500/20" },
                        { label: "Predicted Network Delays", value: `${avgDelay}s`, icon: Clock, color: "text-amber-500", border: "border-amber-500/20" },
                        { label: "Active Congestion Hotspots", value: activeHotspotsCount, icon: AlertOctagon, color: "text-orange-400", border: "border-orange-500/20" }
                    ].map((item, idx) => (
                        <div key={idx} className={`bg-slate-900/40 border ${item.border} rounded-2xl p-4 flex items-center justify-between backdrop-blur-xl`}>
                            <div>
                                <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider">{item.label}</div>
                                <div className="text-2xl font-black mt-1 text-slate-100">{item.value}</div>
                            </div>
                            <item.icon className={`w-8 h-8 ${item.color} opacity-80`} />
                        </div>
                    ))}
                </div>

                {/* 2. LEFT PANE: Event Feed & Form */}
                <div className="col-span-12 lg:col-span-3 space-y-6 flex flex-col h-[600px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800">
                    {/* Event Creator */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl">
                        <div className="flex items-center gap-2 mb-3 text-sm font-bold text-slate-300">
                            <Plus className="w-4 h-4 text-blue-500" />
                            Deploy New Event Monitor
                        </div>
                        <form onSubmit={handleEventCreateSubmit} className="space-y-2.5">
                            <input
                                placeholder="Event Name (e.g. Marathon)"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
                                required
                            />
                            <div className="grid grid-cols-2 gap-2">
                                <select
                                    value={type}
                                    onChange={(e) => setType(e.target.value)}
                                    className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                                >
                                    <option value="concert">Concert</option>
                                    <option value="sports">Sports Match</option>
                                    <option value="festival">Festival</option>
                                    <option value="protest">Protest</option>
                                    <option value="accident">Accident</option>
                                    <option value="construction">Construction</option>
                                </select>
                                <input
                                    type="number"
                                    placeholder="Attendance"
                                    value={attendance}
                                    onChange={(e) => setAttendance(Number(e.target.value))}
                                    className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none"
                                />
                            </div>
                            <input
                                placeholder="Address"
                                value={address}
                                onChange={(e) => setAddress(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200"
                            />
                            <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500">
                                <div>
                                    <label>Start DateTime</label>
                                    <input
                                        type="datetime-local"
                                        value={startTime}
                                        onChange={(e) => setStartTime(e.target.value)}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-1.5 mt-1 text-slate-200 text-xs"
                                    />
                                </div>
                                <div>
                                    <label>End DateTime</label>
                                    <input
                                        type="datetime-local"
                                        value={endTime}
                                        onChange={(e) => setEndTime(e.target.value)}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-1.5 mt-1 text-slate-200 text-xs"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                                <div className="text-[9px] text-slate-500">
                                    Lat: <input type="number" step="0.0001" value={latitude} onChange={(e) => setLatitude(Number(e.target.value))} className="w-full bg-slate-950 border border-slate-800 rounded p-1 text-slate-200 mt-1" />
                                </div>
                                <div className="text-[9px] text-slate-500">
                                    Lon: <input type="number" step="0.0001" value={longitude} onChange={(e) => setLongitude(Number(e.target.value))} className="w-full bg-slate-950 border border-slate-800 rounded p-1 text-slate-200 mt-1" />
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-blue-600 hover:bg-blue-500 text-white rounded-lg py-2 text-xs font-bold transition-colors shadow-lg shadow-blue-500/10"
                            >
                                {loading ? "Registering..." : "Launch Monitor"}
                            </button>
                        </form>
                    </div>

                    {/* Events List Feed */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex-1 flex flex-col backdrop-blur-xl">
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Live Monitor Feed</span>
                        <div className="space-y-2 flex-1 overflow-y-auto max-h-[250px] pr-1">
                            {events.map((e) => {
                                const isSelected = selectedEvent?.id === e.id;
                                return (
                                    <div
                                        key={e.id}
                                        onClick={() => setSelectedEvent(e)}
                                        className={`p-3 rounded-xl border transition-all cursor-pointer ${
                                            isSelected 
                                                ? "bg-blue-500/10 border-blue-500" 
                                                : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
                                        }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-bold text-slate-200 truncate max-w-[150px]">{e.name}</span>
                                            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                                                e.risk_score >= 70 ? "bg-red-500/15 text-red-500" : "bg-blue-500/15 text-blue-400"
                                            }`}>
                                                {e.event_type}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between mt-2 text-[10px] text-slate-500">
                                            <span>Att: {e.estimated_attendance?.toLocaleString()}</span>
                                            <span>Risk: {e.risk_score.toFixed(0)}%</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* 3. CENTER PANE: Massive Digital Twin Map & Timeline */}
                <div className="col-span-12 lg:col-span-6 flex flex-col space-y-4">
                    {/* Map Panel */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-2 relative flex-1 backdrop-blur-xl min-h-[480px]">
                        {/* Selected event info tag on map */}
                        {selectedEvent && (
                            <div className="absolute top-4 left-4 z-[1000] bg-slate-950/85 border border-slate-800 rounded-2xl px-4 py-2.5 backdrop-blur-md text-xs space-y-1">
                                <div className="font-bold text-slate-200 text-sm">{selectedEvent.name}</div>
                                <div className="text-[10px] text-slate-400">
                                    Type: <span className="text-slate-200 font-semibold uppercase">{selectedEvent.event_type}</span> | Risk Score: <span className="text-red-500 font-semibold">{selectedEvent.risk_score.toFixed(0)}%</span>
                                </div>
                            </div>
                        )}

                        {/* Interactive Click-to-Route controls on map */}
                        <div className="absolute top-4 right-4 z-[1000] flex gap-2">
                            <button
                                onClick={() => setRoutingMode("origin")}
                                className={`px-3 py-1.5 rounded-lg text-[10px] font-bold border transition-colors ${
                                    routingMode === "origin" 
                                        ? "bg-blue-600 border-blue-500 text-white" 
                                        : "bg-slate-950/80 border-slate-800 text-slate-300 hover:bg-slate-900"
                                }`}
                            >
                                {originPoint ? "Origin Set ✓" : "Set Origin"}
                            </button>
                            <button
                                onClick={() => setRoutingMode("destination")}
                                className={`px-3 py-1.5 rounded-lg text-[10px] font-bold border transition-colors ${
                                    routingMode === "destination" 
                                        ? "bg-emerald-600 border-emerald-500 text-white" 
                                        : "bg-slate-950/80 border-slate-800 text-slate-300 hover:bg-slate-900"
                                }`}
                            >
                                {destinationPoint ? "Dest Set ✓" : "Set Destination"}
                            </button>
                            {originPoint && destinationPoint && (
                                <button
                                    onClick={calculateRoute}
                                    className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 border border-violet-500 rounded-lg text-[10px] font-bold text-white transition-colors"
                                >
                                    Solve Route
                                </button>
                            )}
                            {(originPoint || destinationPoint) && (
                                <button
                                    onClick={clearRoutes}
                                    className="px-2 py-1.5 bg-red-600/35 hover:bg-red-600 border border-red-500/30 rounded-lg text-[10px] font-bold text-white transition-colors"
                                >
                                    Clear
                                </button>
                            )}
                        </div>

                        {/* Digital Twin Map */}
                        <div className="w-full h-full min-h-[500px]">
                            <DigitalTwin 
                                center={[19.0760, 72.8777]}
                                zoom={13}
                                events={events}
                                hotspots={hotspots}
                                roadNetwork={roadNetwork}
                                roadForecasts={roadForecasts}
                                primaryRoute={primaryRoute}
                                alternativeRoutes={alternativeRoutes}
                                onMapClick={handleMapClick}
                                originPoint={originPoint}
                                destinationPoint={destinationPoint}
                                resources={recommendations.map(r => ({
                                    resource_type: r.resource_type,
                                    count: r.count,
                                    location: r.location,
                                    reasoning: r.reasoning
                                }))}
                            />
                        </div>
                    </div>

                    {/* Timeline Slider */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
                            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-blue-500" /> Forecast Hours Progression</span>
                            <span>+{forecastHour}h from Event Start</span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="12"
                            value={forecastHour}
                            onChange={(e) => setForecastHour(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                        <div className="flex justify-between text-[9px] text-slate-600 mt-1 font-mono">
                            <span>0h (Event Start)</span>
                            <span>2h (Peak Influx)</span>
                            <span>4h (Peak)</span>
                            <span>6h (Dispersal)</span>
                            <span>12h (Cleared)</span>
                        </div>
                    </div>
                </div>

                {/* 4. RIGHT PANE: AI Recommendations & Route statistics */}
                <div className="col-span-12 lg:col-span-3 space-y-6 flex flex-col h-[600px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800">
                    {/* Route statistics overlay details */}
                    {routeStats && (
                        <div className="bg-slate-900/40 border border-blue-500/20 rounded-2xl p-4 backdrop-blur-xl">
                            <div className="flex items-center gap-2 mb-3 text-sm font-bold text-slate-300">
                                <Navigation className="w-4 h-4 text-emerald-500" />
                                Diversion Route Analytics
                            </div>
                            <div className="space-y-2 text-xs">
                                <div className="flex justify-between p-2 bg-slate-950/60 rounded-lg">
                                    <span className="text-slate-500">Primary Travel Time</span>
                                    <span className="font-bold text-emerald-400">{(routeStats.primary.travel_time_seconds / 60).toFixed(1)} mins</span>
                                </div>
                                <div className="flex justify-between p-2 bg-slate-950/60 rounded-lg">
                                    <span className="text-slate-500">Primary Distance</span>
                                    <span className="font-bold text-slate-200">{(routeStats.primary.distance_meters / 1000).toFixed(2)} km</span>
                                </div>
                                
                                {routeStats.alternatives.map((alt: any, idx: number) => {
                                    const diff = routeStats.time_savings[idx];
                                    return (
                                        <div key={idx} className="p-2 border border-slate-800/80 rounded-lg bg-slate-950/20 space-y-1">
                                            <div className="flex justify-between">
                                                <span className="font-semibold text-slate-400">Alternative {idx + 1}</span>
                                                <span className="font-bold text-blue-400">{(alt.travel_time_seconds / 60).toFixed(1)} mins</span>
                                            </div>
                                            <div className="flex justify-between text-[10px]">
                                                <span className="text-slate-600">Delta Delay</span>
                                                <span className={diff <= 0 ? "text-emerald-500 font-medium" : "text-red-500 font-medium"}>
                                                    {diff <= 0 ? "" : "+"}{(diff / 60).toFixed(1)} mins
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* AI Recommendations Panel */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex-1 flex flex-col backdrop-blur-xl">
                        <div className="flex items-center gap-2 mb-3 text-sm font-bold text-slate-300">
                            <Sliders className="w-4 h-4 text-purple-400" />
                            AI Resource Deployment Plan
                        </div>
                        <div className="space-y-3 flex-1 overflow-y-auto max-h-[350px] pr-1">
                            {recommendations.length > 0 ? (
                                recommendations.map((rec) => (
                                    <div key={rec.id} className="p-3 bg-slate-950/60 border border-slate-850 rounded-xl space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-bold text-purple-400 uppercase">{rec.resource_type}</span>
                                            <span className="text-xs font-extrabold bg-purple-500/10 px-2 py-0.5 rounded text-slate-200">
                                                ×{rec.count}
                                            </span>
                                        </div>
                                        <p className="text-[10px] text-slate-400 leading-relaxed font-light">
                                            {rec.reasoning}
                                        </p>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center text-xs text-slate-600 py-10">
                                    No active recommendations. Select an event to compute details.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
