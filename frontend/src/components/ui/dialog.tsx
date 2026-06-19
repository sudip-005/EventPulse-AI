"use client";

import { ReactNode, useState } from "react";

export function Dialog({
    trigger,
    children,
}: {
    trigger: ReactNode;
    children: ReactNode;
}) {
    const [open, setOpen] = useState(false);
    return (
        <>
            <div onClick={() => setOpen(true)}>{trigger}</div>
            {open && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full">
                        <div className="flex justify-end">
                            <button onClick={() => setOpen(false)} className="text-white text-2xl">
                                ×
                            </button>
                        </div>
                        {children}
                    </div>
                </div>
            )}
        </>
    );
}