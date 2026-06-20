"use client";

import { useState } from "react";
import { 
    ResponsiveContainer, 
    AreaChart, 
    Area, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip, 
    BarChart, 
    Bar, 
    LineChart, 
    Line, 
    Legend 
} from "recharts";
import { 
    TrendingUp, 
    Activity, 
    Shield, 
    BarChart2, 
    Clock, 
    CheckCircle 
} from "lucide-react";

// Mock historical dataset for dashboard analytics
const speedDistributionData = [
    { hour: "00:00", baseline: 48, eventDay: 45 },
    { hour: "02:00", baseline: 50, eventDay: 48 },
    { hour: "04:00", baseline: 52, eventDay: 50 },
    { hour: "06:00", baseline: 46, eventDay: 42 },
    { hour: "08:00", baseline: 30, eventDay: 18 }, // morning peak
    { hour: "10:00", baseline: 35, eventDay: 24 },
    { hour: "12:00", baseline: 38, eventDay: 28 },
    { hour: "14:00", baseline: 37, eventDay: 26 },
    { hour: "16:00", baseline: 34, eventDay: 20 },
    { hour: "18:00", baseline: 25, eventDay: 10 }, // evening peak
    { hour: "20:00", baseline: 29, eventDay: 15 },
    { hour: "22:00", baseline: 42, eventDay: 35 }
];

const eventRiskProfileData = [
    { type: "Concert", lowRisk: 10, medRisk: 25, highRisk: 15 },
    { type: "Sports Match", lowRisk: 5, medRisk: 30, highRisk: 20 },
    { type: "Festival", lowRisk: 3, medRisk: 15, highRisk: 28 },
    { type: "Protest", lowRisk: 1, medRisk: 10, highRisk: 35 },
    { type: "Accident", lowRisk: 20, medRisk: 15, highRisk: 5 },
    { type: "Construction", lowRisk: 12, medRisk: 24, highRisk: 10 }
];

const modelRetrainingAccuracy = [
    { run: "Run 1", mae: 54.2, rmse: 68.1 },
    { run: "Run 2", mae: 51.5, rmse: 65.4 },
    { run: "Run 3", mae: 49.7, rmse: 62.9 },
    { run: "Run 4", mae: 47.8, rmse: 60.2 },
    { run: "Run 5", mae: 46.1, rmse: 57.8 }
];

export default function AnalyticsDashboard() {
    const [timeRange, setTimeRange] = useState("7d");

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
            {/* Header */}
            <header className="border-b border-slate-900 bg-slate-950 px-6 py-4 flex items-center justify-between z-10">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <Activity className="w-6 h-6 text-blue-500 animate-pulse" />
                        <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                            EventPulse AI
                        </span>
                    </div>
                    <div className="h-4 w-px bg-slate-800" />
                    <span className="text-xs text-slate-400 font-mono uppercase tracking-widest">Mobility & Resource Analytics</span>
                </div>
                <nav className="flex items-center gap-4 text-sm text-slate-400">
                    <a href="/" className="hover:text-white">Home</a>
                    <a href="/command-center" className="hover:text-white">Command Center</a>
                    <a href="/simulator" className="hover:text-white">Simulator</a>
                    <a href="/analytics" className="hover:text-white">Post-Event Learning</a>
                </nav>
            </header>

            {/* Dashboard Content */}
            <main className="flex-1 p-6 space-y-6 overflow-y-auto max-w-7xl mx-auto w-full">
                {/* Title & Filter bar */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight text-slate-100 flex items-center gap-2">
                            <BarChart2 className="w-6 h-6 text-blue-500" />
                            Performance Analytics
                        </h1>
                        <p className="text-xs text-slate-400 mt-1 font-light">
                            Detailed summaries of historical congestion metrics, incident risk ratios, and model performance.
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        {["24h", "7d", "30d"].map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold border transition-colors ${
                                    timeRange === range 
                                        ? "bg-blue-600 border-blue-500 text-white" 
                                        : "bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-850"
                                }`}
                            >
                                {range}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Key stats row */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[
                        { label: "Manpower Deployment Efficiency", value: "94.2%", icon: CheckCircle, color: "text-emerald-400" },
                        { label: "Junction Congestion Mitigation", value: "28.5%", icon: TrendingUp, color: "text-blue-400" },
                        { label: "Average Officer Response Time", value: "3.2m", icon: Clock, color: "text-purple-400" },
                        { label: "Accuracy of Diversion Estimates", value: "88.1%", icon: Shield, color: "text-amber-500" }
                    ].map((item, idx) => (
                        <div key={idx} className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between backdrop-blur-xl">
                            <div>
                                <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">{item.label}</span>
                                <div className="text-2xl font-black text-slate-200 mt-1">{item.value}</div>
                            </div>
                            <item.icon className={`w-6 h-6 ${item.color} opacity-80`} />
                        </div>
                    ))}
                </div>

                {/* Main Charts grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Speed Distribution Chart */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 backdrop-blur-xl space-y-4">
                        <div>
                            <h3 className="text-sm font-bold text-slate-300">Hourly Speed Distribution Comparison</h3>
                            <span className="text-[10px] text-slate-500 font-light">Average travel speeds (km/h) across 100 monitored segments on normal days vs event days.</span>
                        </div>
                        <div className="h-[280px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={speedDistributionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                                    <XAxis dataKey="hour" stroke="#64748B" fontSize={10} tickLine={false} />
                                    <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1E293B", borderRadius: "12px", fontSize: "11px" }} />
                                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                                    <Line type="monotone" dataKey="baseline" name="Baseline (Normal Day)" stroke="#10B981" strokeWidth={3} activeDot={{ r: 8 }} />
                                    <Line type="monotone" dataKey="eventDay" name="Event Impact Day" stroke="#EF4444" strokeWidth={3} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Event Risk Profile Chart */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 backdrop-blur-xl space-y-4">
                        <div>
                            <h3 className="text-sm font-bold text-slate-300">Risk Profile by Event Categories</h3>
                            <span className="text-[10px] text-slate-500 font-light">Distribution of calculated risk classes (Low, Medium, High) mapped from database assessment tables.</span>
                        </div>
                        <div className="h-[280px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={eventRiskProfileData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                                    <XAxis dataKey="type" stroke="#64748B" fontSize={10} tickLine={false} />
                                    <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1E293B", borderRadius: "12px", fontSize: "11px" }} />
                                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                                    <Bar dataKey="lowRisk" name="Low Risk" stackId="a" fill="#10B981" />
                                    <Bar dataKey="medRisk" name="Medium Risk" stackId="a" fill="#F59E0B" />
                                    <Bar dataKey="highRisk" name="High/Critical" stackId="a" fill="#EF4444" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Model retraining accuracy over epochs */}
                    <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 backdrop-blur-xl space-y-4 lg:col-span-2">
                        <div>
                            <h3 className="text-sm font-bold text-slate-300">Retraining Performance Timeline (XGBoost Regressor)</h3>
                            <span className="text-[10px] text-slate-500 font-light">Trace of Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) reduction on successive model retraining loops.</span>
                        </div>
                        <div className="h-[250px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={modelRetrainingAccuracy} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorMae" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                                        </linearGradient>
                                        <linearGradient id="colorRmse" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                                    <XAxis dataKey="run" stroke="#64748B" fontSize={10} tickLine={false} />
                                    <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                                    <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1E293B", borderRadius: "12px", fontSize: "11px" }} />
                                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                                    <Area type="monotone" dataKey="mae" name="Mean Absolute Error (MAE)" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorMae)" />
                                    <Area type="monotone" dataKey="rmse" name="Root Mean Squared Error (RMSE)" stroke="#8B5CF6" strokeWidth={3} fillOpacity={1} fill="url(#colorRmse)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}