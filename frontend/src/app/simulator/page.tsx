"use client";

import { useState } from "react";
import SimulationControls from "@/components/SimulationControls";

export default function SimulatorPage() {
    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold">Scenario Simulator</h1>
            <SimulationControls />
        </div>
    );
}