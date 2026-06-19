import { ReactNode } from "react";

export default function Card({
    children,
    className = "",
}: {
    children: ReactNode;
    className?: string;
}) {
    return (
        <div className={`bg-slate-800 rounded-lg p-4 border border-slate-700 ${className}`}>
            {children}
        </div>
    );
}