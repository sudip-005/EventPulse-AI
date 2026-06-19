const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export async function apiFetch<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
        ...options,
    });
    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "API error");
    }
    return res.json();
}