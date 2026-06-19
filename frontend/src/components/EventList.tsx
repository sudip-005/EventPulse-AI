"use client";

import { useEffect, useState } from "react";
import { Event } from "@/lib/types";

export default function EventList() {
    const [events, setEvents] = useState<Event[]>([]);
    useEffect(() => {
        fetch("/api/v1/events")
            .then((res) => res.json())
            .then(setEvents)
            .catch(console.error);
    }, []);
    return (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <h3 className="font-semibold mb-2">Recent Events</h3>
            <ul className="space-y-2">
                {events.slice(0, 5).map((ev) => (
                    <li key={ev.id} className="text-sm text-slate-300">
                        {ev.name} – {ev.event_type} (Impact: {ev.impact_score.toFixed(0)}%)
                    </li>
                ))}
                {events.length === 0 && (
                    <li className="text-slate-500 text-sm">No events yet</li>
                )}
            </ul>
        </div>
    );
}