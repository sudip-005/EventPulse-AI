"use client";

import { useState } from "react";
import Button from "./ui/button";
import Input from "./ui/input";
import { Event } from "@/lib/types";

interface EventFormProps {
    onEventCreated: (event: Event) => void;
}

export default function EventForm({ onEventCreated }: EventFormProps) {
    const [name, setName] = useState("");
    const [type, setType] = useState("concert");
    const [attendance, setAttendance] = useState<number>(1000);
    const [start, setStart] = useState(new Date().toISOString().slice(0, 16));
    const [end, setEnd] = useState(new Date(Date.now() + 3600000 * 2).toISOString().slice(0, 16));
    const [address, setAddress] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        // In real use, geocode address to coordinates. For demo, use fixed coords.
        const payload = {
            name,
            event_type: type,
            estimated_attendance: attendance,
            start_time: new Date(start).toISOString(),
            end_time: new Date(end).toISOString(),
            address,
            location: {
                type: "Point",
                coordinates: [72.8777, 19.0760], // Mumbai center
            },
        };
        try {
            const res = await fetch("/api/v1/events", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                const data = await res.json();
                onEventCreated(data);
                // Reset form
                setName("");
                setAttendance(1000);
                setAddress("");
            } else {
                alert("Failed to create event");
            }
        } catch (err) {
            alert("Error creating event");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <h3 className="font-semibold mb-2">Create Event</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
                <Input
                    placeholder="Event Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
                <select
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                    value={type}
                    onChange={(e) => setType(e.target.value)}
                >
                    <option value="concert">Concert</option>
                    <option value="sports">Sports</option>
                    <option value="festival">Festival</option>
                    <option value="protest">Protest</option>
                    <option value="accident">Accident</option>
                    <option value="construction">Construction</option>
                    <option value="other">Other</option>
                </select>
                <Input
                    type="number"
                    placeholder="Estimated Attendance"
                    value={attendance}
                    onChange={(e) => setAttendance(Number(e.target.value))}
                    required
                />
                <Input
                    type="datetime-local"
                    value={start}
                    onChange={(e) => setStart(e.target.value)}
                    required
                />
                <Input
                    type="datetime-local"
                    value={end}
                    onChange={(e) => setEnd(e.target.value)}
                    required
                />
                <Input
                    placeholder="Address (optional)"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                />
                <Button type="submit" disabled={loading}>
                    {loading ? "Creating..." : "Create Event"}
                </Button>
            </form>
        </div>
    );
}