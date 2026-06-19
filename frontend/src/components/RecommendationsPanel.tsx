import { Recommendation } from "@/lib/types";

export default function RecommendationsPanel({
    recommendations,
}: {
    recommendations: Recommendation[];
}) {
    if (!recommendations.length) return null;
    return (
        <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <h3 className="font-semibold mb-2">📋 Recommendations</h3>
            <ul className="space-y-2">
                {recommendations.map((r) => (
                    <li key={r.id} className="text-sm text-slate-300">
                        <span className="capitalize">{r.resource_type}</span>: {r.count} units
                        <span className="block text-xs text-slate-500">{r.reasoning}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}