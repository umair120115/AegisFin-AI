import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, ShieldCheck, Activity, Network, FileText, 
  AlertTriangle, RefreshCw, Smartphone, PhoneCall, Radio, CheckCircle2,
  Lock, ArrowRight, Zap, Users
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState('INTERCEPTOR'); // 'INTERCEPTOR' | 'GRAPH' | 'BENCHMARK'
  const [currentDecision, setCurrentDecision] = useState(null);
  const [recentFeed, setRecentFeed] = useState([]);
  const [loading, setLoading] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [sarModal, setSarModal] = useState({ open: false, narrative: '' });

  // Simulate on mount
  useEffect(() => {
    simulateScenario('WEDDING_LEGIT');
    fetchGraph();
  }, []);

  const simulateScenario = async (scenarioId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v2/fintech/simulate/${scenarioId}`, { method: 'POST' });
      const data = await res.json();
      setCurrentDecision(data);
      setRecentFeed(prev => [data, ...prev.slice(0, 19)]);
      fetchGraph();
    } catch (err) {
      console.error("Simulation error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchGraph = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v2/fintech/graph-topology`);
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      console.error("Graph fetch error:", err);
    }
  };

  const runBenchmark = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v2/fintech/benchmark-csv`, { method: 'POST' });
      const data = await res.json();
      setBenchmarkData(data);
    } catch (err) {
      console.error("Benchmark error:", err);
    } finally {
      setLoading(false);
    }
  };

  const triggerSarGeneration = async (alertData) => {
    try {
      const res = await fetch(`${API_BASE}/api/v2/fintech/generate-sar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertData)
      });
      const data = await res.json();
      setSarModal({ open: true, narrative: data.sar_narrative_markdown });
    } catch (err) {
      console.error("SAR Generation error:", err);
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'CRITICAL':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded bg-red-950/80 border border-red-500/50 text-red-400 flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5" /> CRITICAL (HALTED)</span>;
      case 'HIGH':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded bg-amber-950/80 border border-amber-500/50 text-amber-400 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> HIGH (CAUTION)</span>;
      case 'MEDIUM':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded bg-yellow-950/80 border border-yellow-500/50 text-yellow-400 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> MEDIUM (STEP-UP)</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-950/80 border border-emerald-500/50 text-emerald-400 flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5" /> LOW (ALLOW)</span>;
    }
  };

  return (
    <div className="min-h-screen bg-[#080C14] text-slate-100 flex flex-col font-sans">
      {/* Top Cockpit Header */}
      <header className="border-b border-slate-800 bg-[#0B111E] px-6 py-3.5 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-600/20 border border-blue-500/30 text-blue-400">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2 font-mono">
              AEGISFIN-CORE <span className="text-xs px-2 py-0.5 rounded bg-blue-950 border border-blue-500/40 text-blue-400 font-sans">v2.0 Middleware Shield</span>
            </h1>
            <p className="text-xs text-slate-400">Request-Level Bi-Directional AI Security & AML Engine • Sub-25ms SLA</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('INTERCEPTOR')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'INTERCEPTOR' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-3.5 h-3.5" /> Live Interceptor
          </button>
          <button
            onClick={() => { setActiveTab('GRAPH'); fetchGraph(); }}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'GRAPH' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Network className="w-3.5 h-3.5" /> Temporal AML Graph
          </button>
          <button
            onClick={() => { setActiveTab('BENCHMARK'); if(!benchmarkData) runBenchmark(); }}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'BENCHMARK' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> 5k Benchmark & Ablation
          </button>
        </div>
      </header>

      {/* Preset Scenario Simulator Bar */}
      <div className="bg-[#0D1527] border-b border-slate-800/80 px-6 py-2.5 flex items-center gap-2 overflow-x-auto">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mr-2">
          <Zap className="w-3.5 h-3.5 text-amber-400" /> Scenarios:
        </span>
        <button
          onClick={() => simulateScenario('WEDDING_LEGIT')}
          disabled={loading}
          className="px-3 py-1.5 text-xs rounded-md bg-slate-800/80 hover:bg-emerald-950/40 hover:border-emerald-500/40 border border-slate-700/60 text-slate-200 transition-all font-mono"
        >
          💍 Wedding Gold ₹4.5L (Legit FD)
        </button>
        <button
          onClick={() => simulateScenario('FAMILY_SPLIT_LEGIT')}
          disabled={loading}
          className="px-3 py-1.5 text-xs rounded-md bg-slate-800/80 hover:bg-emerald-950/40 hover:border-emerald-500/40 border border-slate-700/60 text-slate-200 transition-all font-mono"
        >
          🏥 Family Hospital Split ₹95k (BSSID Legit)
        </button>
        <button
          onClick={() => simulateScenario('ELDER_VISHING_SCAM')}
          disabled={loading}
          className="px-3 py-1.5 text-xs rounded-md bg-slate-800/80 hover:bg-red-950/40 hover:border-red-500/40 border border-slate-700/60 text-slate-200 transition-all font-mono"
        >
          ⚡ Elder Electricity Vishing ₹48.5k (Active Call)
        </button>
        <button
          onClick={() => simulateScenario('AML_SMURFING')}
          disabled={loading}
          className="px-3 py-1.5 text-xs rounded-md bg-slate-800/80 hover:bg-red-950/40 hover:border-red-500/40 border border-slate-700/60 text-slate-200 transition-all font-mono"
        >
          🔪 AML Smurfing ₹49.5k (PAN Threshold)
        </button>
        <button
          onClick={() => simulateScenario('CIRCULAR_AML_LOOP')}
          disabled={loading}
          className="px-3 py-1.5 text-xs rounded-md bg-slate-800/80 hover:bg-red-950/40 hover:border-red-500/40 border border-slate-700/60 text-slate-200 transition-all font-mono"
        >
          🔄 Circular Round-Trip ₹3.4L (A→B→C→A)
        </button>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 p-6 overflow-y-auto">
        {activeTab === 'INTERCEPTOR' && currentDecision && (
          <div className="grid grid-cols-12 gap-6">
            {/* Left Column: Intercept Decision & Vernacular Shield Alert */}
            <div className="col-span-12 lg:col-span-4 space-y-6">
              {/* Verdict Summary Card */}
              <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 shadow-xl">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Pre-Settlement Intercept</span>
                  {getTierBadge(currentDecision.risk_tier)}
                </div>

                <div className="flex items-baseline justify-between mb-4">
                  <div>
                    <span className="text-xs text-slate-400">Composite Risk Score</span>
                    <div className="text-4xl font-extrabold font-mono tracking-tight text-white mt-1">
                      {currentDecision.composite_risk_score}
                      <span className="text-sm font-normal text-slate-500"> / 100</span>
                    </div>
                  </div>
                  <div className="text-right font-mono">
                    <span className="text-xs text-slate-400">Inference SLA</span>
                    <div className="text-lg font-bold text-emerald-400 mt-1 flex items-center gap-1 justify-end">
                      <Zap className="w-4 h-4" /> {currentDecision.latency_ms} ms
                    </div>
                  </div>
                </div>

                {/* Vernacular Warning Alert Banner */}
                {currentDecision.vernacular_user_message && (
                  <div className="p-3.5 rounded-lg bg-red-950/60 border border-red-500/40 text-red-200 text-xs mb-4">
                    <div className="flex items-center gap-2 font-semibold text-red-300 mb-1">
                      <PhoneCall className="w-4 h-4 text-red-400 animate-bounce" /> Voice / Push Intercept Triggered
                    </div>
                    <p className="leading-relaxed">{currentDecision.vernacular_user_message}</p>
                  </div>
                )}

                {/* Sub-score Pillars */}
                <div className="space-y-2 pt-2 border-t border-slate-800 text-xs">
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Receiver Mule History (35%):</span>
                    <span className="font-mono text-slate-200">{currentDecision.sub_scores.receiver_history_score} pts</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Graph AML Topology (30%):</span>
                    <span className="font-mono text-slate-200">{currentDecision.sub_scores.graph_aml_score} pts</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Sender ML Supervised (20%):</span>
                    <span className="font-mono text-slate-200">{currentDecision.sub_scores.sender_supervised_score} pts</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Telemetry & Life Modifier:</span>
                    <span className={`font-mono ${currentDecision.sub_scores.app_log_modifier_pts < 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {currentDecision.sub_scores.app_log_modifier_pts > 0 ? '+' : ''}{currentDecision.sub_scores.app_log_modifier_pts} pts
                    </span>
                  </div>
                </div>

                {/* Auto SAR Trigger */}
                {currentDecision.fiu_ind_sar_ready && (
                  <button
                    onClick={() => triggerSarGeneration(currentDecision)}
                    className="w-full mt-4 py-2 px-3 bg-red-600/90 hover:bg-red-500 text-white rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2 shadow-lg"
                  >
                    <FileText className="w-4 h-4" /> Generate FIU-IND SAR Report
                  </button>
                )}
              </div>

              {/* Transaction Context Card */}
              <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 shadow-xl font-mono text-xs space-y-2.5">
                <span className="text-slate-400 uppercase tracking-wider font-semibold block mb-2 font-sans">Payment Header</span>
                <div className="flex justify-between">
                  <span className="text-slate-500">TX ID:</span>
                  <span className="text-blue-400">{currentDecision.tx_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Action:</span>
                  <span className="text-white font-bold">{currentDecision.enforcement_action}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Typology:</span>
                  <span className="text-amber-400">{currentDecision.aml_typology_detected}</span>
                </div>
              </div>
            </div>

            {/* Right Column: TreeSHAP Waterfall Chart & Recent Intercepts Feed */}
            <div className="col-span-12 lg:col-span-8 space-y-6">
              {/* TreeSHAP Local Feature Attributions */}
              <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 shadow-xl">
                <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Activity className="w-4 h-4 text-blue-400" /> Explainable AI (TreeSHAP Risk Waterfall)
                    </h3>
                    <p className="text-xs text-slate-400">Additive feature contribution pushing risk above / below baseline</p>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={currentDecision.xai_waterfall}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                    >
                      <XAxis type="number" stroke="#64748B" fontSize={11} />
                      <YAxis type="category" dataKey="feature" stroke="#94A3B8" fontSize={10} width={130} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0B111E', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                        formatter={(val) => [`${val > 0 ? '+' : ''}${val} pts`, 'Risk Contribution']}
                      />
                      <ReferenceLine x={0} stroke="#475569" strokeDasharray="3 3" />
                      <Bar dataKey="impact_pts" radius={[4, 4, 4, 4]}>
                        {currentDecision.xai_waterfall.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.impact_pts > 0 ? '#EF4444' : '#10B981'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Human-Readable Factor Explanations */}
                <div className="mt-4 space-y-2 border-t border-slate-800 pt-3">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Auditor Explanations:</span>
                  {currentDecision.xai_waterfall.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      <span className={`font-mono font-bold px-1.5 py-0.5 rounded text-[10px] ${f.impact_pts > 0 ? 'bg-red-950 text-red-400 border border-red-500/30' : 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'}`}>
                        {f.impact_pts > 0 ? `+${f.impact_pts}` : f.impact_pts} pts
                      </span>
                      <span className="text-slate-300">{f.reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Live Sliding-Window Feed */}
              <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 shadow-xl">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-400" /> Real-Time Decision Stream (Last 20 Requests)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left font-mono">
                    <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">TX ID</th>
                        <th className="py-2.5 px-3">Risk Score</th>
                        <th className="py-2.5 px-3">Tier</th>
                        <th className="py-2.5 px-3">Action</th>
                        <th className="py-2.5 px-3">Latency</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {recentFeed.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-all">
                          <td className="py-2 px-3 text-blue-400">{item.tx_id}</td>
                          <td className="py-2 px-3 font-bold text-white">{item.composite_risk_score}</td>
                          <td className="py-2 px-3">{getTierBadge(item.risk_tier)}</td>
                          <td className="py-2 px-3 text-slate-300">{item.enforcement_action}</td>
                          <td className="py-2 px-3 text-emerald-400">{item.latency_ms} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Temporal AML Graph View */}
        {activeTab === 'GRAPH' && (
          <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <Network className="w-5 h-5 text-blue-400" /> Temporal In-Memory AML Topology
                </h3>
                <p className="text-xs text-slate-400">Real-time directed multi-graph tracking circular cycles & mule fan-in / fan-out sweeps</p>
              </div>
              <button
                onClick={fetchGraph}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-mono text-slate-200 flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh Graph
              </button>
            </div>

            {/* SVG Interactive Topology Canvas */}
            <div className="h-96 w-full bg-[#080C14] border border-slate-800/80 rounded-lg relative overflow-hidden flex items-center justify-center p-4">
              <svg className="w-full h-full">
                {/* Simulated Visual Nodes and Edges */}
                {graphData.edges.map((e, idx) => {
                  const x1 = 120 + (idx * 50) % 600;
                  const y1 = 80 + (idx * 30) % 250;
                  const x2 = 250 + (idx * 60) % 550;
                  const y2 = 180 + (idx * 40) % 200;
                  return (
                    <g key={idx}>
                      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#334155" strokeWidth="2" strokeDasharray="4 2" />
                      <text x={(x1 + x2)/2} y={(y1 + y2)/2 - 5} fill="#64748B" fontSize="9" fontFamily="monospace">
                        ₹{e.amount ? e.amount.toLocaleString() : '50k'}
                      </text>
                    </g>
                  );
                })}
                {graphData.nodes.map((n, idx) => {
                  const cx = 150 + (idx * 70) % 650;
                  const cy = 100 + (idx * 45) % 260;
                  const isMule = n.id.toLowerCase().includes('mule') || n.id.toLowerCase().includes('shell') || n.id.toLowerCase().includes('ebill');
                  return (
                    <g key={idx} className="cursor-pointer group">
                      <circle cx={cx} cy={cy} r={16} fill={isMule ? '#991B1B' : '#1E3A8A'} stroke={isMule ? '#EF4444' : '#3B82F6'} strokeWidth="2" />
                      <text x={cx} y={cy + 25} textAnchor="middle" fill="#CBD5E1" fontSize="10" fontFamily="monospace">
                        {n.id.length > 18 ? n.id.substring(0, 15) + '...' : n.id}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        )}

        {/* 5k Benchmark & Ablation Study View */}
        {activeTab === 'BENCHMARK' && (
          <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-400" /> Scientific Benchmark & Ablation Study (5,000 Transactions)
                </h3>
                <p className="text-xs text-slate-400">Comparing Traditional Sender-Only Rule/ML vs. AegisFin Bi-Directional Request Middleware</p>
              </div>
              <button
                onClick={runBenchmark}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-semibold text-white flex items-center gap-2 shadow"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Run Live 5k Evaluation
              </button>
            </div>

            {benchmarkData && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Legacy Sender-Only System Card */}
                <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs font-bold text-red-400 uppercase tracking-wider block mb-3">Legacy Sender-Only ML</span>
                  <div className="space-y-3 font-mono text-xs">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">Precision:</span>
                      <span className="text-slate-200">{(benchmarkData.baseline_sender_only.precision * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">Recall:</span>
                      <span className="text-slate-200">{(benchmarkData.baseline_sender_only.recall * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">F1-Score:</span>
                      <span className="text-slate-200">{benchmarkData.baseline_sender_only.f1_score}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2 text-red-400 font-bold">
                      <span>Wedding False-Positive Rate:</span>
                      <span>{benchmarkData.baseline_sender_only.wedding_false_positive_rate} (Falsely Blocked!)</span>
                    </div>
                    <div className="flex justify-between text-red-400 font-bold">
                      <span>Elder Vishing Catch Rate:</span>
                      <span>{benchmarkData.baseline_sender_only.elder_vishing_detection_rate} (Missed!)</span>
                    </div>
                  </div>
                </div>

                {/* AegisFin Bi-Directional Middleware Card */}
                <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-500/40 shadow-lg">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-3">AegisFin-Core Bi-Directional Shield</span>
                  <div className="space-y-3 font-mono text-xs">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">Precision:</span>
                      <span className="text-emerald-400 font-bold">{(benchmarkData.aegisfin_bidirectional_middleware.precision * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">Recall:</span>
                      <span className="text-emerald-400 font-bold">{(benchmarkData.aegisfin_bidirectional_middleware.recall * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400">F1-Score:</span>
                      <span className="text-emerald-400 font-bold">{benchmarkData.aegisfin_bidirectional_middleware.f1_score}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2 text-emerald-400 font-bold">
                      <span>Wedding False-Positive Rate:</span>
                      <span>{benchmarkData.aegisfin_bidirectional_middleware.wedding_false_positive_rate} (Seamlessly Allowed)</span>
                    </div>
                    <div className="flex justify-between text-emerald-400 font-bold">
                      <span>Elder Vishing Detection Rate:</span>
                      <span>{benchmarkData.aegisfin_bidirectional_middleware.elder_vishing_detection_rate} (100% Intercepted)</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Regulatory SAR Markdown Modal */}
      {sarModal.open && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-[#0F172A] border border-slate-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-red-400" /> FIU-IND Suspicious Activity Report (SAR / STR)
              </h3>
              <button
                onClick={() => setSarModal({ open: false, narrative: '' })}
                className="text-slate-400 hover:text-white text-xs font-mono"
              >
                ✕ Close
              </button>
            </div>
            <div className="bg-[#080C14] border border-slate-800 p-4 rounded-lg font-mono text-xs text-slate-300 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
              {sarModal.narrative}
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => navigator.clipboard.writeText(sarModal.narrative)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-mono rounded text-slate-200"
              >
                Copy Markdown
              </button>
              <button
                onClick={() => setSarModal({ open: false, narrative: '' })}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-xs font-semibold rounded text-white"
              >
                Approve & Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
