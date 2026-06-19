import { Hotspot } from "@/lib/types";

export default function HotspotList({ hotspots }: { hotspots: Hotspot[] }) {
    if (!hotspots.length) return null;
    return (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <h3 className="font-semibold mb-2">🔥 Hotspots Detected</h3>
            <ul className="space-y-2">
                {hotspots.map((h) => (
                    <li key={h.id} className="text-sm flex justify-between">
                        <span className="text-slate-300">
                            Severity {h.severity}/5 – {h.avg_congestion.toFixed(1)}% congestion
                        </span>
                        <span className="text-slate-500">
                            {h.radius_meters.toFixed(0)}m radius
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
}