import { useState } from "react";
import { apiFetch } from "@/lib/api-client";

export function useSimulation() {
    const [result, setResult] = useState(null);
    const run = async (eventId: string, params: any) => {
        const data = await apiFetch("/simulation/run", {
            method: "POST",
            body: JSON.stringify({ event_id: eventId, scenario_params: params }),
        });
        setResult(data);
        return data;
    };
    return { result, run };
}