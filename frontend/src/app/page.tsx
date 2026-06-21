"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import dynamic from "next/dynamic";
import { 
    Activity, 
    Brain, 
    Layers, 
    Shield, 
    Sliders, 
    Cpu, 
    TrendingUp, 
    ArrowRight, 
    AlertTriangle,
    Map
} from "lucide-react";

// Dynamic import for Leaflet-based map (SSR-safe)
const DigitalTwin = dynamic(() => import("@/components/maps/DigitalTwin"), { 
    ssr: false,
    loading: () => (
        <div className="w-full h-[400px] rounded-2xl bg-slate-900/50 border border-slate-800 flex items-center justify-center text-slate-500">
            Loading live map preview...
        </div>
    )
});

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 overflow-x-hidden selection:bg-blue-500 selection:text-white relative">
            {/* Background glowing gradients */}
            <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-violet-600/10 rounded-full blur-[150px] pointer-events-none" />
            <div className="absolute bottom-10 left-1/3 w-[400px] h-[400px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

            {/* Navigation Header */}
            <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/70 border-b border-slate-900 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Activity className="w-5 h-5 text-white animate-pulse" />
                        </div>
                        <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                            EventPulse AI
                        </span>
                    </div>
                    <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
                        <Link href="#features" className="hover:text-blue-400 transition-colors">Features</Link>
                        <Link href="#impact" className="hover:text-blue-400 transition-colors">Problem & Solution</Link>
                        <Link href="#preview" className="hover:text-blue-400 transition-colors">Live Preview</Link>
                    </nav>
                    <div className="flex items-center gap-4">
                        <Link href="/command-center">
                            <button className="px-5 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-lg shadow-blue-500/10 hover:shadow-blue-500/25 transition-all flex items-center gap-2 group">
                                Launch Command Center
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </Link>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="relative max-w-7xl mx-auto px-6 pt-20 pb-32 flex flex-col items-center text-center">
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-8"
                >
                    <Cpu className="w-3.5 h-3.5" /> Next-Generation AI-Driven City Mobility
                </motion.div>

                <motion.h1 
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.1 }}
                    className="text-5xl md:text-7xl font-black tracking-tight leading-[1.1] mb-8 max-w-4xl"
                >
                    Predict Traffic Congestion <br />
                    <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">
                        Before It Happens
                    </span>
                </motion.h1>

                <motion.p 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="text-lg md:text-xl text-slate-400 max-w-2xl font-light leading-relaxed mb-12"
                >
                    Transform city-wide traffic management from reactive to predictive. Grounded in geospatial intelligence, machine learning, and interactive digital twins.
                </motion.p>

                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.3 }}
                    className="flex flex-wrap items-center justify-center gap-4"
                >
                    <Link href="/command-center">
                        <button className="px-8 py-4 rounded-xl text-base font-bold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-xl shadow-blue-500/20 transition-all flex items-center gap-2 group">
                            Enter Operations Center
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </Link>
                    <Link href="/simulator">
                        <button className="px-8 py-4 rounded-xl text-base font-bold bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 transition-all">
                            Simulate What-If Scenarios
                        </button>
                    </Link>
                </motion.div>

                {/* Animated Map Graphic / Dashboard Preview */}
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95, y: 40 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ duration: 1, delay: 0.4 }}
                    className="mt-20 w-full max-w-5xl rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-xl shadow-2xl relative group overflow-hidden"
                >
                    {/* Glass glare effect */}
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-blue-500/5 to-transparent pointer-events-none" />
                    
                    {/* Mock Map / Flow Graphic */}
                    <div className="w-full aspect-[16/9] bg-slate-950 rounded-xl relative overflow-hidden flex items-center justify-center border border-slate-800">
                        {/* City Grid Lines */}
                        <div className="absolute inset-0 grid grid-cols-12 gap-1.5 opacity-20 pointer-events-none">
                            {Array.from({ length: 12 }).map((_, i) => (
                                <div key={i} className="border-r border-slate-800 h-full" />
                            ))}
                        </div>
                        <div className="absolute inset-0 grid grid-rows-6 gap-1.5 opacity-20 pointer-events-none">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div key={i} className="border-b border-slate-800 w-full" />
                            ))}
                        </div>

                        {/* Pulsing hotspots in mockup */}
                        <div className="absolute top-1/3 left-1/4 w-32 h-32 rounded-full bg-red-500/10 border border-red-500/20 animate-ping pointer-events-none" />
                        <div className="absolute top-1/2 left-2/3 w-20 h-20 rounded-full bg-amber-500/10 border border-amber-500/20 animate-ping pointer-events-none" />
                        
                        <div className="absolute z-10 flex flex-col items-center gap-3">
                            <span className="text-sm font-semibold tracking-wider text-slate-500 uppercase">Interactive Digital Twin Preview</span>
                            <div className="flex items-center gap-6">
                                <div className="flex flex-col items-center">
                                    <span className="text-4xl font-extrabold text-blue-400">100+</span>
                                    <span className="text-[10px] text-slate-500 font-medium">Mapped Junctions</span>
                                </div>
                                <div className="h-10 w-px bg-slate-800" />
                                <div className="flex flex-col items-center">
                                    <span className="text-4xl font-extrabold text-red-500">83%</span>
                                    <span className="text-[10px] text-slate-500 font-medium">Forecast Accuracy</span>
                                </div>
                                <div className="h-10 w-px bg-slate-800" />
                                <div className="flex flex-col items-center">
                                    <span className="text-4xl font-extrabold text-emerald-400">20m</span>
                                    <span className="text-[10px] text-slate-500 font-medium">Avg Delay Saved</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </section>

            {/* Core Value / Problem Statement Section */}
            <section id="impact" className="py-24 border-t border-slate-900 bg-slate-900/10 relative">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
                        <div>
                            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-500 mb-3">The Smart City Crisis</h2>
                            <h3 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-6">
                                Reactive Traffic Control is Failing Our Cities.
                            </h3>
                            <p className="text-slate-400 leading-relaxed font-light mb-8">
                                Most municipalities discover congestion only after it blocks major corridors. Large public events—like concerts, sports, protests, or construction—shatter traffic flow unpredictably. EventPulse AI intercepts this by modeling spatial dynamics and scheduling operational logic days before bottlenecks happen.
                            </p>
                            <div className="space-y-4">
                                {[
                                    { text: "Predict event-related shock waves across adjacent roads", icon: Shield },
                                    { text: "Recommend exact manpower, marshals, and barricade grids", icon: Sliders },
                                    { text: "Route traffic dynamically avoiding DBSCAN-detected hotspots", icon: Layers }
                                ].map((item, idx) => (
                                    <div key={idx} className="flex items-start gap-3">
                                        <div className="w-5 h-5 rounded-md bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mt-0.5">
                                            <item.icon className="w-3 h-3 text-blue-400" />
                                        </div>
                                        <span className="text-sm font-medium text-slate-300">{item.text}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-8 backdrop-blur-xl space-y-6">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-6 h-6 text-amber-500" />
                                <span className="text-base font-bold">Continuous Post-Event Learning Loop</span>
                            </div>
                            <div className="h-px bg-slate-800" />
                            <p className="text-sm text-slate-400 font-light leading-relaxed">
                                Most platforms are black boxes that don't learn from error. EventPulse AI logs outcomes in database records, checks deviations between predicted and actual traffic, tracks resource efficiency, and retrains the XGBoost predictive models automatically.
                            </p>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                                    <div className="text-xs text-slate-500 font-semibold mb-1">XGBoost Forecast</div>
                                    <div className="text-lg font-bold text-slate-200">Continuous</div>
                                </div>
                                <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                                    <div className="text-xs text-slate-500 font-semibold mb-1">Feedback Metric</div>
                                    <div className="text-lg font-bold text-slate-200">MAE / RMSE</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Modules Grid */}
            <section id="features" className="py-24 border-t border-slate-900">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-xs font-bold uppercase tracking-wider text-blue-500 mb-3">Engineered Modules</h2>
                        <h3 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
                            Powerful Analytics at Your Fingertips
                        </h3>
                        <p className="text-slate-400 font-light leading-relaxed">
                            Eight tightly integrated subsystems mapping and mitigating urban congestion.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                            { title: "Event Intelligence", desc: "Calculate risk and event impact scores dynamically based on attendance and road closure requisites.", icon: Brain, color: "from-blue-600/20 to-cyan-500/10" },
                            { title: "Traffic Forecasting", desc: "Our trained XGBoost model outputs road-level congestion percentages, speeds, and estimated delays.", icon: Cpu, color: "from-purple-600/20 to-pink-500/10" },
                            { title: "Hotspot Clustering", desc: "Identify multi-point spatial congestion hotspots using density-based DBSCAN/HDBSCAN algorithms.", icon: AlertTriangle, color: "from-amber-600/20 to-orange-500/10" },
                            { title: "Smart Diversions", desc: "Solve graph shortest paths with NetworkX A* routing, automatically routing around severe hotspots.", icon: Layers, color: "from-emerald-600/20 to-teal-500/10" },
                            { title: "What-If Simulation", desc: "Re-project flows in real-time adjusting attendance, weather, or closing roads completely.", icon: Sliders, color: "from-indigo-600/20 to-blue-500/10" },
                            { title: "Resource Allocation", desc: "Estimate officer, marshal, and barricade needs with clear, explainable AI rationales.", icon: Shield, color: "from-red-600/20 to-rose-500/10" }
                        ].map((module, idx) => (
                            <div 
                                key={idx} 
                                className="bg-slate-900/40 border border-slate-800/80 hover:border-slate-700/80 rounded-2xl p-6 backdrop-blur-xl transition-all hover:-translate-y-1 relative group"
                            >
                                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-6`}>
                                    <module.icon className="w-6 h-6 text-slate-300" />
                                </div>
                                <h4 className="text-lg font-bold mb-3">{module.title}</h4>
                                <p className="text-sm text-slate-400 font-light leading-relaxed">{module.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Interactive Live Map Preview Section */}
            <section id="preview" className="py-24 border-t border-slate-900 bg-slate-950 relative">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center max-w-3xl mx-auto mb-12">
                        <h2 className="text-xs font-bold uppercase tracking-wider text-cyan-500 mb-3">Live Digital Twin</h2>
                        <h3 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
                            See the City. In Real Time.
                        </h3>
                        <p className="text-slate-400 font-light leading-relaxed">
                            An interactive map showing Mumbai's road network, event epicenters, and traffic hotspots. Click any road to view congestion metrics. This is the same Digital Twin that powers the Command Center.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                        {[
                            { label: "XGBoost Accuracy", value: "94%", sub: "Impact Classification F1", color: "text-blue-400" },
                            { label: "Avg. Delay Saved", value: "~71 min", sub: "Per Managed Event", color: "text-emerald-400" },
                            { label: "Hotspot Recall", value: "DBSCAN", sub: "Spatially Clustered Congestion", color: "text-amber-400" },
                        ].map((stat, i) => (
                            <div key={i} className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-xl text-center">
                                <div className={`text-2xl font-black ${stat.color}`}>{stat.value}</div>
                                <div className="text-xs font-bold text-slate-300 mt-1">{stat.label}</div>
                                <div className="text-[10px] text-slate-600 mt-0.5">{stat.sub}</div>
                            </div>
                        ))}
                    </div>

                    {/* Real Leaflet map with mock event epicenter */}
                    <div className="rounded-3xl overflow-hidden border border-slate-800/80 bg-slate-900/40 backdrop-blur-xl p-2 shadow-2xl shadow-blue-500/5">
                        <DigitalTwin
                            center={[19.0760, 72.8777]}
                            zoom={13}
                            events={[
                                {
                                    id: "preview-1",
                                    name: "IPL Match — Wankhede Stadium",
                                    event_type: "sports",
                                    location: { type: "Point", coordinates: [72.8254, 18.9388] },
                                    estimated_attendance: 33000,
                                    start_time: new Date().toISOString(),
                                    end_time: new Date().toISOString(),
                                    impact_score: 78,
                                    risk_score: 72,
                                    status: "scheduled",
                                    created_at: new Date().toISOString(),
                                    updated_at: new Date().toISOString()
                                },
                                {
                                    id: "preview-2",
                                    name: "Bandra-Worli Protest March",
                                    event_type: "protest",
                                    location: { type: "Point", coordinates: [72.8255, 19.0460] },
                                    estimated_attendance: 8000,
                                    start_time: new Date().toISOString(),
                                    end_time: new Date().toISOString(),
                                    impact_score: 55,
                                    risk_score: 60,
                                    status: "scheduled",
                                    created_at: new Date().toISOString(),
                                    updated_at: new Date().toISOString()
                                }
                            ]}
                            hotspots={[
                                {
                                    id: "hs-1", cluster_id: "c1",
                                    center: [19.0220, 72.8340] as [number, number],
                                    severity: 5, point_count: 12,
                                    radius_meters: 600, avg_congestion: 88, max_congestion: 92,
                                    affected_roads: []
                                },
                                {
                                    id: "hs-2", cluster_id: "c2",
                                    center: [19.0760, 72.8777] as [number, number],
                                    severity: 3, point_count: 7,
                                    radius_meters: 400, avg_congestion: 55, max_congestion: 68,
                                    affected_roads: []
                                }
                            ]}
                        />
                    </div>
                    <p className="text-center text-[10px] text-slate-600 mt-3">Preview data — click the Layer Controls to toggle events, hotspots, and heatmap</p>
                </div>
            </section>

            {/* Bottom Call to Action */}
            <section className="py-24 border-t border-slate-900 bg-slate-950 relative">
                <div className="max-w-4xl mx-auto px-6 text-center">
                    <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-8">
                        Ready to Transform City Traffic Operations?
                    </h2>
                    <div className="flex flex-wrap items-center justify-center gap-6">
                        <Link href="/command-center">
                            <button className="px-8 py-4 rounded-xl text-base font-bold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-xl shadow-blue-500/20 transition-all flex items-center gap-2 group">
                                Open Command Center
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </Link>
                        <Link href="/dashboard">
                            <button className="px-8 py-4 rounded-xl text-base font-bold bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 transition-all">
                                View Analytics & ML Performance
                            </button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-slate-900 py-8 px-6 text-center text-xs text-slate-600">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                    <span>&copy; {new Date().getFullYear()} EventPulse AI. All rights reserved.</span>
                    <span>Smart City Traffic Intelligence Control</span>
                </div>
            </footer>
        </div>
    );
}