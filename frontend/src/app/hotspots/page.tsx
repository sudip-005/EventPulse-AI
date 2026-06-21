"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Event = { id: string; name: string };

export default function HotspotExplorer() {
  const [events, setEvents] = useState<Event[]>([]);
  const [eventId, setEventId] = useState("");
  const [hotspots, setHotspots] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/v1/events").then((r) => r.json()).then((data) => { setEvents(data); if (data[0]) setEventId(data[0].id); }).catch(console.error);
  }, []);

  async function detect() {
    const response = await fetch("/api/v1/hotspots/detect", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_id: eventId, algorithm: "dbscan", eps: 200, min_samples: 5 }),
    });
    if (!response.ok) throw new Error("Hotspot detection failed");
    setHotspots(await response.json());
  }

  return <main className="min-h-screen bg-slate-950 text-white p-8"><div className="mx-auto max-w-5xl space-y-8">
    <nav className="flex justify-between"><Link href="/" className="font-bold">EventPulse AI</Link><Link href="/command-center" className="text-amber-400">Command Center</Link></nav>
    <section><p className="text-amber-400 uppercase tracking-widest text-xs">Spatial intelligence</p><h1 className="text-4xl font-black mt-2">Hotspot Explorer</h1><p className="text-slate-400 mt-3">Detect and inspect event-driven congestion clusters.</p></section>
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 flex gap-3"><select className="flex-1 rounded-lg bg-slate-950 border border-slate-700 p-3" value={eventId} onChange={(e) => setEventId(e.target.value)}><option value="">Select an event</option>{events.map((event) => <option key={event.id} value={event.id}>{event.name}</option>)}</select><button disabled={!eventId} onClick={detect} className="rounded-lg bg-amber-400 px-6 font-bold text-slate-950 disabled:opacity-50">Detect</button></section>
    <section className="grid md:grid-cols-3 gap-4">{hotspots.length === 0 ? <p className="text-slate-500">No hotspots detected yet.</p> : hotspots.map((hotspot) => <article key={hotspot.id} className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-xs uppercase text-slate-500">{hotspot.cluster_id}</p><p className="text-2xl font-black mt-2">Severity {hotspot.severity}</p><p className="text-amber-400 mt-2">{hotspot.avg_congestion?.toFixed(1)}% congestion</p></article>)}</section>
  </div></main>;
}
