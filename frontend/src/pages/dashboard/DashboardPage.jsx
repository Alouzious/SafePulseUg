import { useState, useEffect }  from 'react';
import toast                    from 'react-hot-toast';
import {
    AlertTriangle, CheckCircle2, TrendingUp, Users,
    BrainCircuit, ShieldAlert, Calendar, Clock, Flame,
} from 'lucide-react';
import dashboardApi             from '../../api/dashboardApi';
import StatCard                 from '../../components/common/StatCard';
import LoadingSpinner           from '../../components/common/LoadingSpinner';
import { formatDateTime, getSeverityColor, capitalize } from '../../utils/helpers';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, PieChart, Pie,
    Cell, LineChart, Line,
} from 'recharts';

const DashboardPage = () => {
    const [overview,   setOverview]   = useState(null);
    const [categories, setCategories] = useState([]);
    const [severity,   setSeverity]   = useState([]);
    const [trends,     setTrends]     = useState([]);
    const [hotspots,   setHotspots]   = useState([]);
    const [recent,     setRecent]     = useState([]);
    const [alerts,     setAlerts]     = useState([]);
    const [loading,    setLoading]    = useState(true);

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [ov, cat, sev, tr, hot, rec, alt] = await Promise.all([
                    dashboardApi.getOverview(),
                    dashboardApi.getCrimesByCategory(),
                    dashboardApi.getCrimesBySeverity(),
                    dashboardApi.getMonthlyTrends(),
                    dashboardApi.getHotspots(),
                    dashboardApi.getRecentCrimes(5),
                    dashboardApi.getAlerts(),
                ]);
                setOverview(ov.data);
                setCategories(cat.data.data);
                setSeverity(sev.data.data);
                setTrends(tr.data.data);
                setHotspots(hot.data.data);
                setRecent(rec.data.data);
                setAlerts(alt.data.data);
            } catch {
                toast.error('Failed to load dashboard data.');
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    if (loading) return <LoadingSpinner message="Loading dashboard..." />;

    const riskColor = {
        critical: 'bg-purple-600', high: 'bg-red-600',
        medium:   'bg-orange-500', low:  'bg-green-500',
    };

    return (
        <div className="space-y-5">

            {/* ── Page Header ──────────────────────────── */}
            <div>
                <h1 className="text-2xl font-bold text-[#0f2744]">Dashboard</h1>
                <p className="text-slate-500 text-sm mt-0.5">SafePulse UG — Real-time Crime Analysis Overview</p>
            </div>

            {/* ── Stat Cards ───────────────────────────── */}
            <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
                <StatCard title="Total Crimes"    value={overview?.crimes?.total            ?? 0} icon={ShieldAlert}   color="blue"   subtitle="All time" />
                <StatCard title="This Week"        value={overview?.crimes?.this_week        ?? 0} icon={Calendar}      color="blue"   subtitle="Last 7 days" />
                <StatCard title="High Priority"    value={overview?.crimes?.high_priority    ?? 0} icon={AlertTriangle} color="red"    subtitle="Unsolved critical" />
                <StatCard title="Solve Rate"       value={`${overview?.crimes?.solve_rate_percent ?? 0}%`} icon={CheckCircle2} color="green" subtitle="Cases resolved" />
                <StatCard title="Active Officers"  value={overview?.system?.active_officers  ?? 0} icon={Users}         color="purple" subtitle="Currently active" />
                <StatCard title="AI Analyses"      value={overview?.system?.total_analyses   ?? 0} icon={BrainCircuit}  color="blue"   subtitle="Completed" />
            </div>

            {/* ── Charts Row 1 ─────────────────────────── */}
            <div className="grid grid-cols-2 gap-4">
                <Card title="Monthly Crime Trends" icon={TrendingUp}>
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={trends}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                            <YAxis tick={{ fontSize: 11 }} />
                            <Tooltip />
                            <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} name="Crimes" />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>

                <Card title="Crimes by Severity" icon={AlertTriangle}>
                    <ResponsiveContainer width="100%" height={220}>
                        <PieChart>
                            <Pie data={severity} dataKey="count" nameKey="severity" cx="50%" cy="50%" outerRadius={80}
                                label={({ severity, count }) => `${severity}: ${count}`}>
                                {severity.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* ── Charts Row 2 ─────────────────────────── */}
            <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                    <Card title="Crimes by Category" icon={ShieldAlert}>
                        <ResponsiveContainer width="100%" height={220}>
                            <BarChart data={categories} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis type="number" tick={{ fontSize: 11 }} />
                                <YAxis type="category" dataKey="category" tick={{ fontSize: 11 }} width={90} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#0f2744" radius={[0, 4, 4, 0]} name="Cases" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>
                </div>

                <Card title="Status Breakdown" icon={CheckCircle2}>
                    <div className="space-y-3 mt-2">
                        {[
                            { label: 'Reported',            value: overview?.by_status?.reported,            color: 'bg-blue-500'   },
                            { label: 'Under Investigation', value: overview?.by_status?.under_investigation, color: 'bg-orange-500' },
                            { label: 'Solved',              value: overview?.by_status?.solved,              color: 'bg-green-500'  },
                            { label: 'Cold Cases',          value: overview?.by_status?.cold_cases,          color: 'bg-purple-600' },
                        ].map((item) => (
                            <div key={item.label}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-600">{item.label}</span>
                                    <span className="font-bold text-[#0f2744]">{item.value ?? 0}</span>
                                </div>
                                <div className="bg-slate-100 rounded-full h-1.5">
                                    <div
                                        className={`${item.color} h-1.5 rounded-full transition-all duration-500`}
                                        style={{ width: `${overview?.crimes?.total ? ((item.value / overview.crimes.total) * 100) : 0}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>

            {/* ── Bottom Row ───────────────────────────── */}
            <div className="grid grid-cols-2 gap-4">

                {/* Recent Crimes */}
                <Card title="Recent Crime Reports" icon={Clock}>
                    <div className="space-y-2 mt-2">
                        {recent.map((r) => (
                            <div key={r.id} className="flex items-center gap-3 p-2.5 bg-slate-50 rounded-lg border-l-4"
                                style={{ borderLeftColor: getSeverityColor(r.severity) }}>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between gap-2">
                                        <span className="text-xs font-bold text-[#0f2744] truncate">{r.case_number}</span>
                                        <span className="text-[10px] px-2 py-0.5 rounded-full text-white flex-shrink-0"
                                            style={{ background: getSeverityColor(r.severity) }}>
                                            {r.severity}
                                        </span>
                                    </div>
                                    <p className="text-xs text-slate-600 mt-0.5 truncate">{r.title}</p>
                                    <p className="text-[11px] text-slate-400 mt-0.5">{r.district} · {r.date_reported}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                {/* Hotspots */}
                <Card title="Crime Hotspots" icon={Flame}>
                    <div className="space-y-2 mt-2">
                        {hotspots.map((h, i) => (
                            <div key={i} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg">
                                <div>
                                    <p className="text-sm font-semibold text-[#0f2744]">{h.district}</p>
                                    <p className="text-[11px] text-slate-400 mt-0.5">
                                        {h.unsolved} unsolved · {h.high_severity} high severity
                                    </p>
                                </div>
                                <div className="text-right flex-shrink-0">
                                    <p className="text-xl font-bold text-[#0f2744]">{h.total}</p>
                                    <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${riskColor[h.risk_level] || 'bg-slate-400'}`}>
                                        {h.risk_level}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>

            {/* ── Alerts ───────────────────────────────── */}
            {alerts.length > 0 && (
                <div className="bg-white rounded-2xl p-5 border border-red-100 shadow-sm border-l-4 border-l-red-500">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle size={18} className="text-red-600" />
                        <h3 className="text-base font-bold text-red-600">High Priority Alerts</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                        {alerts.map((a) => (
                            <div key={a.id} className="p-3 bg-red-50 rounded-xl border border-red-100">
                                <div className="flex justify-between mb-1">
                                    <span className="text-xs font-bold text-red-600">{a.case_number}</span>
                                    <span className="text-[11px] text-slate-400">{a.days_open}d open</span>
                                </div>
                                <p className="text-xs text-slate-700 mb-1">{a.title}</p>
                                <p className="text-[11px] text-slate-400">{a.district} · {a.category}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

/* ── Reusable Card wrapper ───────────────────────────── */
const Card = ({ title, icon: Icon, children }) => (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
        <div className="flex items-center gap-2 mb-1">
            {Icon && <Icon size={16} className="text-[#0f2744]" />}
            <h3 className="text-sm font-bold text-[#0f2744]">{title}</h3>
        </div>
        {children}
    </div>
);

export default DashboardPage;