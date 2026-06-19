"use client";

import { useState } from "react";
import Button from "./ui/button";
import Input from "./ui/input";

export default function SimulationControls() {
    const [eventId, setEventId] = useState("");
    const [attendanceMult, setAttendanceMult] = useState(1.2);
    const [rain, setRain] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    const runSimulation = async () => {
        if (!eventId) return alert("Enter event ID");
        setLoading(true);
        try {
            const res = await fetch("/api/v1/simulation/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    event_id: eventId,
                    scenario_params: {
                        attendance_multiplier: attendanceMult,
                        weather: rain ? { condition: "rain" } : {},
                    },
                }),
            });
            const data = await res.json();
            setResult(data);
        } catch (err) {
            alert("Error running simulation");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800 space-y-4">
            <h3 className="font-semibold">What-If Simulator</h3>
            <Input
                placeholder="Event ID"
                value={eventId}
                onChange={(e) => setEventId(e.target.value)}
            />
            <div>
                <label className="text-sm">Attendance Multiplier</label>
                <Input
                    type="number"
                    step="0.1"
                    value={attendanceMult}
                    onChange={(e) => setAttendanceMult(Number(e.target.value))}
                />
            </div>
            <label className="flex items-center gap-2 text-sm">
                <input
                    type="checkbox"
                    checked={rain}
                    onChange={() => setRain(!rain)}
                />
                Rain?
            </label>
            <Button onClick={runSimulation} disabled={loading}>
                {loading ? "Running..." : "Run Simulation"}
            </Button>
            {result && (
                <div className="mt-2 bg-slate-800 p-2 rounded text-xs">
                    <p>Modified Impact: {result.modified_event.impact_score.toFixed(1)}%</p>
                    <p>Hotspots: {result.hotspots?.length || 0} detected</p>
                </div>
            )}
        </div>
    );
}