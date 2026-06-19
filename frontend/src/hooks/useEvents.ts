import { useEffect, useState } from "react";
import { Event } from "@/lib/types";
import { apiFetch } from "@/lib/api-client";

export function useEvents() {
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        apiFetch<Event[]>("/events")
            .then(setEvents)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);
    return { events, loading };
}