import { useState } from "react";
import { apiFetch } from "@/lib/api-client";

export function useForecast() {
    const [forecast, setForecast] = useState<any>(null);
    const generate = async (eventId: string) => {
        const data = await apiFetch("/forecast", {
            method: "POST",
            body: JSON.stringify({ event_id: eventId, horizon_hours: 6 }),
        });
        setForecast(data);
        return data;
    };
    return { forecast, generate };
}