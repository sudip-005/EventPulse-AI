import { ReactNode } from "react";

interface ButtonProps {
    children: ReactNode;
    onClick?: () => void;
    variant?: "primary" | "secondary" | "danger";
    className?: string;
    disabled?: boolean;
}

export default function Button({
    children,
    onClick,
    variant = "primary",
    className = "",
    disabled = false,
}: ButtonProps) {
    const base =
        "px-4 py-2 rounded font-medium transition-colors disabled:opacity-50";
    const variants = {
        primary: "bg-blue-600 hover:bg-blue-700 text-white",
        secondary: "bg-slate-600 hover:bg-slate-700 text-white",
        danger: "bg-red-600 hover:bg-red-700 text-white",
    };
    return (
        <button
            className={`${base} ${variants[variant]} ${className}`}
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
}