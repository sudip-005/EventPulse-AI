"use client";

import { useState } from "react";
import DashboardStats from "@/components/DashboardStats";
import DigitalTwin from "@/components/maps/DigitalTwin";
import EventForm from "@/components/EventForm";
import EventList from "@/components/EventList";
import HotspotList from "@/components/HotspotList";
import RecommendationsPanel from "@/components/RecommendationsPanel";
import { Event, Hotspot, Recommendation } from "@/lib/types";

export default function Home() {
    const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
    const [hotspots, setHotspots] = useState<Hotspot[]>([]);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleEventCreated = (event: Event) => {
        setSelectedEvent(event);
        setRefreshTrigger((prev) => prev + 1);
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <header className="border-b border-slate-800 p-4">
                <div className="container mx-auto flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-blue-400">
                        🚦 EventPulse AI
                    </h1>
                    <span className="text-sm text-slate-400">
                        Smart City Traffic Command Center
                    </span>
                </div>
            </header>

            <main className="container mx-auto p-4">
                <div className="grid grid-cols-12 gap-4">
                    {/* Stats Row */}
                    <div className="col-span-12">
                        <DashboardStats />
                    </div>

                    {/* Map */}
                    <div className="col-span-8">
                        <div className="bg-slate-900 rounded-lg p-2 border border-slate-800">
                            <DigitalTwin
                                center={[19.0760, 72.8777]}
                                zoom={12}
                                events={[]}
                                hotspots={hotspots}
                                trafficData={[]}
                            />
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="col-span-4 space-y-4">
                        <EventForm onEventCreated={handleEventCreated} />

                        {selectedEvent && (
                            <>
                                <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                                    <h3 className="font-semibold mb-2">Selected Event</h3>
                                    <p className="text-sm text-slate-300">{selectedEvent.name}</p>
                                    <p className="text-xs text-slate-400">
                                        Impact: {selectedEvent.impact_score.toFixed(1)}% | Risk:{" "}
                                        {selectedEvent.risk_score.toFixed(1)}%
                                    </p>
                                    <button
                                        className="mt-2 text-xs bg-blue-600 px-3 py-1 rounded hover:bg-blue-700"
                                        onClick={async () => {
                                            // Fetch hotspots and recommendations for this event
                                            const res = await fetch(
                                                `/api/v1/hotspots/event/${selectedEvent.id}`
                                            );
                                            const data = await res.json();
                                            setHotspots(data);
                                            const resRec = await fetch(
                                                `/api/v1/recommendations/event/${selectedEvent.id}`
                                            );
                                            const recData = await resRec.json();
                                            setRecommendations(recData);
                                        }}
                                    >
                                        Analyze Event
                                    </button>
                                </div>
                                <HotspotList hotspots={hotspots} />
                                <RecommendationsPanel recommendations={recommendations} />
                            </>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}