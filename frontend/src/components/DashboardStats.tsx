"use client";

import { useEffect, useState } from "react";

export default function DashboardStats() {
    const [stats, setStats] = useState({ events: 0, hotspots: 0, alerts: 0 });
    useEffect(() => {
        // Fetch real stats or use dummy
        setStats({ events: 12, hotspots: 3, alerts: 1 });
    }, []);
    return (
        <div className="grid grid-cols-3 gap-4">
            {[
                { label: "Active Events", value: stats.events, color: "blue" },
                { label: "Hotspots", value: stats.hotspots, color: "orange" },
                { label: "Alerts", value: stats.alerts, color: "red" },
            ].map((item) => (
                <div
                    key={item.label}
                    className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-center"
                >
                    <div className={`text-2xl font-bold text-${item.color}-400`}>{item.value}</div>
                    <div className="text-sm text-slate-400">{item.label}</div>
                </div>
            ))}
        </div>
    );
}