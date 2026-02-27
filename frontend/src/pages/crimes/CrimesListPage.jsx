import { useState, useEffect } from 'react';
import { useNavigate }         from 'react-router-dom';
import toast                   from 'react-hot-toast';
import { ShieldAlert, Plus, Search, Filter, RotateCcw, Eye } from 'lucide-react';
import crimesApi      from '../../api/crimesApi';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getSeverityColor, getStatusColor, capitalize, truncate } from '../../utils/helpers';

const CATEGORIES = ['','theft','assault','homicide','fraud','cybercrime','robbery','burglary','drug_offense','sexual_offense','vandalism','kidnapping','arson','corruption','other'];
const STATUSES   = ['','reported','under_investigation','solved','closed','cold_case'];
const SEVERITIES = ['','low','medium','high','critical'];

const CrimesListPage = () => {
    const navigate = useNavigate();
    const [crimes,  setCrimes]  = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({ category: '', status: '', severity: '', district: '', search: '' });

    const fetchCrimes = async () => {
        setLoading(true);
        try {
            const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
            const res    = await crimesApi.getAll(params);
            setCrimes(res.data.results);
        } catch {
            toast.error('Failed to load crime reports.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchCrimes(); }, []);

    const handleFilter = (e) =>
        setFilters({ ...filters, [e.target.name]: e.target.value });

    const handleReset = () => {
        setFilters({ category: '', status: '', severity: '', district: '', search: '' });
        fetchCrimes();
    };

    return (
        <div className="space-y-4">

            {/* ── Header ───────────────────────────────── */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                        <ShieldAlert size={22} className="text-blue-600" />
                        Crime Reports
                    </h1>
                    <p className="text-slate-500 text-sm mt-0.5">Manage and view all crime reports</p>
                </div>
                <button
                    onClick={() => navigate('/crimes/add')}
                    className="flex items-center gap-2 px-4 py-2.5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-xl font-semibold text-sm transition"
                >
                    <Plus size={16} /> New Report
                </button>
            </div>

            {/* ── Filters ──────────────────────────────── */}
            <div className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm flex flex-wrap gap-2 items-end">
                <div className="relative flex-1 min-w-[180px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                    <input
                        name="search"
                        value={filters.search}
                        onChange={handleFilter}
                        placeholder="Search case, title..."
                        className="w-full pl-8 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    />
                </div>

                {[
                    { name: 'category', options: CATEGORIES, placeholder: 'All Categories' },
                    { name: 'status',   options: STATUSES,   placeholder: 'All Statuses'   },
                    { name: 'severity', options: SEVERITIES, placeholder: 'All Severities' },
                ].map(({ name, options, placeholder }) => (
                    <select
                        key={name}
                        name={name}
                        value={filters[name]}
                        onChange={handleFilter}
                        className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition bg-white min-w-[140px]"
                    >
                        {options.map((o) => (
                            <option key={o} value={o}>{o ? capitalize(o.replace(/_/g, ' ')) : placeholder}</option>
                        ))}
                    </select>
                ))}

                <input
                    name="district"
                    value={filters.district}
                    onChange={handleFilter}
                    placeholder="District..."
                    className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition w-28"
                />

                <button
                    onClick={fetchCrimes}
                    className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition"
                >
                    <Filter size={13} /> Apply
                </button>
                <button
                    onClick={handleReset}
                    className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm font-medium transition"
                >
                    <RotateCcw size={13} /> Reset
                </button>
            </div>

            {/* ── Table ────────────────────────────────── */}
            {loading ? <LoadingSpinner /> : (
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <div className="px-5 py-3 border-b border-slate-100 text-xs text-slate-400 font-medium">
                        {crimes.length} report{crimes.length !== 1 ? 's' : ''} found
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr className="bg-slate-50">
                                    {['Case No.', 'Title', 'Category', 'Severity', 'Status', 'District', 'Date', 'Action'].map((h) => (
                                        <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 whitespace-nowrap">
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {crimes.length === 0 ? (
                                    <tr>
                                        <td colSpan={8} className="px-4 py-12 text-center text-slate-400 text-sm">
                                            No crime reports found
                                        </td>
                                    </tr>
                                ) : crimes.map((c, i) => (
                                    <tr
                                        key={c.id}
                                        className={`border-b border-slate-50 hover:bg-blue-50/30 transition ${i % 2 === 1 ? 'bg-slate-50/50' : ''}`}
                                    >
                                        <td className="px-4 py-3">
                                            <span className="text-xs font-bold text-[#0f2744]">{c.case_number}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-sm text-slate-700">{truncate(c.title, 35)}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
                                                {capitalize(c.category)}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className="text-[11px] px-2.5 py-1 rounded-full text-white font-bold"
                                                style={{ background: getSeverityColor(c.severity) }}
                                            >
                                                {c.severity?.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className="text-[11px] px-2.5 py-1 rounded-full font-semibold"
                                                style={{ background: getStatusColor(c.status) + '22', color: getStatusColor(c.status) }}
                                            >
                                                {capitalize(c.status?.replace(/_/g, ' '))}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs text-slate-500">{c.district}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs text-slate-400">{c.date_reported?.split('T')[0]}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <button
                                                onClick={() => navigate(`/crimes/${c.id}`)}
                                                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white text-xs font-semibold rounded-lg transition"
                                            >
                                                <Eye size={12} /> View
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CrimesListPage;