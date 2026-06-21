"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Event = { id: string; name: string };

export default function ForecastCenter() {
  const [events, setEvents] = useState<Event[]>([]);
  const [eventId, setEventId] = useState("");
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/v1/events").then((r) => r.json()).then((data) => {
      setEvents(data);
      if (data[0]) setEventId(data[0].id);
    }).catch(console.error);
  }, []);

  async function generate() {
    if (!eventId) return;
    setLoading(true);
    try {
      const response = await fetch("/api/v1/forecast", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: eventId, horizon_hours: 6, include_roads: true }),
      });
      if (!response.ok) throw new Error("Forecast request failed");
      setForecast(await response.json());
    } finally { setLoading(false); }
  }

  return <main className="min-h-screen bg-slate-950 text-white p-8">
    <div className="mx-auto max-w-5xl space-y-8">
      <nav className="flex justify-between"><Link href="/" className="font-bold">EventPulse AI</Link><Link href="/command-center" className="text-cyan-400">Command Center</Link></nav>
      <section><p className="text-cyan-400 uppercase tracking-widest text-xs">Predictive operations</p><h1 className="text-4xl font-black mt-2">Forecast Center</h1><p className="text-slate-400 mt-3">Run the deployed XGBoost models against any scheduled event.</p></section>
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 flex gap-3">
        <select className="flex-1 rounded-lg bg-slate-950 border border-slate-700 p-3" value={eventId} onChange={(e) => setEventId(e.target.value)}>
          <option value="">Select an event</option>{events.map((event) => <option key={event.id} value={event.id}>{event.name}</option>)}
        </select>
        <button className="rounded-lg bg-cyan-500 px-6 font-bold text-slate-950 disabled:opacity-50" disabled={!eventId || loading} onClick={generate}>{loading ? "Forecasting…" : "Generate"}</button>
      </section>
      {forecast && <section className="grid md:grid-cols-4 gap-4">{[
        ["Impact", forecast.impact_score?.toFixed(1)], ["Level", forecast.impact_level],
        ["Risk", forecast.risk_score?.toFixed(1)], ["Duration", `${forecast.expected_duration_minutes?.toFixed(0)} min`]
      ].map(([label, value]) => <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-slate-500 text-xs uppercase">{label}</p><p className="text-2xl font-black mt-2">{value}</p></div>)}</section>}
    </div>
  </main>;
}
