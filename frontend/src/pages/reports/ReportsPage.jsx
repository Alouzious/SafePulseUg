import { useState, useEffect }  from 'react';
import toast                    from 'react-hot-toast';
import {
    FileBarChart2, FileDown, FileSpreadsheet,
    Search, BrainCircuit, Loader2, Clock,
    Filter,
} from 'lucide-react';
import reportsApi     from '../../api/reportsApi';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { formatDateTime, downloadFile, capitalize } from '../../utils/helpers';

const CATEGORIES = ['','theft','assault','homicide','fraud','cybercrime','robbery','burglary','drug_offense','sexual_offense','vandalism','kidnapping','arson','corruption','other'];
const SEVERITIES = ['','low','medium','high','critical'];
const STATUSES   = ['','reported','under_investigation','solved','closed','cold_case'];

const ReportsPage = () => {
    const [history,    setHistory]    = useState([]);
    const [loading,    setLoading]    = useState(true);
    const [generating, setGenerating] = useState('');
    const [filters,    setFilters]    = useState({ category: '', severity: '', status: '', district: '' });
    const [caseNo,     setCaseNo]     = useState('');
    const [analysisId, setAnalysisId] = useState('');

    useEffect(() => { fetchHistory(); }, []);

    const fetchHistory = async () => {
        try {
            const res = await reportsApi.getHistory();
            setHistory(res.data.results);
        } catch {
            toast.error('Failed to load report history.');
        } finally {
            setLoading(false);
        }
    };

    const handleFilter = (e) =>
        setFilters({ ...filters, [e.target.name]: e.target.value });

    const handleCrimeListPdf = async () => {
        setGenerating('list-pdf');
        try {
            const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
            const res    = await reportsApi.downloadCrimeListPdf(params);
            downloadFile(res.data, `crime_list_${Date.now()}.pdf`);
            toast.success('PDF downloaded!');
            fetchHistory();
        } catch { toast.error('Failed to generate PDF.'); }
        finally  { setGenerating(''); }
    };

    const handleCrimeListExcel = async () => {
        setGenerating('list-excel');
        try {
            const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
            const res    = await reportsApi.downloadCrimeListExcel(params);
            downloadFile(res.data, `crime_list_${Date.now()}.xlsx`);
            toast.success('Excel downloaded!');
            fetchHistory();
        } catch { toast.error('Failed to generate Excel.'); }
        finally  { setGenerating(''); }
    };

    const handleCrimePdf = async () => {
        if (!caseNo.trim()) { toast.error('Enter a case number.'); return; }
        setGenerating('case-pdf');
        try {
            const res = await reportsApi.downloadCrimePdf(caseNo.trim());
            downloadFile(res.data, `${caseNo.trim()}_report.pdf`);
            toast.success('Case PDF downloaded!');
            fetchHistory();
        } catch { toast.error('Case not found or failed to generate PDF.'); }
        finally  { setGenerating(''); }
    };

    const handleAnalysisPdf = async () => {
        if (!analysisId.trim()) { toast.error('Enter an analysis ID.'); return; }
        setGenerating('analysis-pdf');
        try {
            const res = await reportsApi.downloadAnalysisPdf(analysisId.trim());
            downloadFile(res.data, `analysis_${analysisId}_report.pdf`);
            toast.success('Analysis PDF downloaded!');
            fetchHistory();
        } catch { toast.error('Analysis not found or not completed yet.'); }
        finally  { setGenerating(''); }
    };

    return (
        <div className="space-y-5">

            {/* ── Header ───────────────────────────────── */}
            <div>
                <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                    <FileBarChart2 size={22} className="text-blue-600" />
                    Reports
                </h1>
                <p className="text-slate-500 text-sm mt-0.5">Generate and download PDF & Excel reports</p>
            </div>

            <div className="grid grid-cols-2 gap-4">

                {/* ── Crime List Report ─────────────────── */}
                <Card title="Crime List Report" icon={Filter}>
                    <p className="text-xs text-slate-500 mb-4">
                        Generate a report for all crimes. Apply optional filters below.
                    </p>

                    <div className="space-y-2 mb-4">
                        {[
                            { name: 'category', options: CATEGORIES, placeholder: 'All Categories' },
                            { name: 'severity', options: SEVERITIES, placeholder: 'All Severities' },
                            { name: 'status',   options: STATUSES,   placeholder: 'All Statuses'   },
                        ].map(({ name, options, placeholder }) => (
                            <select
                                key={name}
                                name={name}
                                value={filters[name]}
                                onChange={handleFilter}
                                className={inputCls}
                            >
                                {options.map((o) => (
                                    <option key={o} value={o}>
                                        {o ? capitalize(o.replace(/_/g, ' ')) : placeholder}
                                    </option>
                                ))}
                            </select>
                        ))}
                        <input
                            name="district"
                            value={filters.district}
                            onChange={handleFilter}
                            placeholder="Filter by district..."
                            className={inputCls}
                        />
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={handleCrimeListPdf}
                            disabled={!!generating}
                            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-xl text-sm font-semibold disabled:opacity-60 transition"
                        >
                            {generating === 'list-pdf'
                                ? <><Loader2 size={14} className="animate-spin" /> Generating...</>
                                : <><FileDown size={14} /> Download PDF</>
                            }
                        </button>
                        <button
                            onClick={handleCrimeListExcel}
                            disabled={!!generating}
                            className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold disabled:opacity-60 transition"
                        >
                            {generating === 'list-excel'
                                ? <><Loader2 size={14} className="animate-spin" /> Generating...</>
                                : <><FileSpreadsheet size={14} /> Download Excel</>
                            }
                        </button>
                    </div>
                </Card>

                {/* ── Single Case + Analysis ────────────── */}
                <div className="space-y-4">

                    <Card title="Single Case PDF" icon={Search}>
                        <p className="text-xs text-slate-500 mb-3">
                            Download a detailed PDF report for one specific crime case.
                        </p>
                        <div className="flex gap-2">
                            <input
                                value={caseNo}
                                onChange={(e) => setCaseNo(e.target.value)}
                                placeholder="e.g. UPF-CASE-00001"
                                className={`${inputCls} flex-1`}
                            />
                            <button
                                onClick={handleCrimePdf}
                                disabled={!!generating}
                                className="flex items-center gap-1.5 px-4 py-2 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg text-sm font-semibold disabled:opacity-60 transition whitespace-nowrap"
                            >
                                {generating === 'case-pdf'
                                    ? <Loader2 size={14} className="animate-spin" />
                                    : <><FileDown size={14} /> PDF</>
                                }
                            </button>
                        </div>
                    </Card>

                    <Card title="AI Analysis PDF" icon={BrainCircuit}>
                        <p className="text-xs text-slate-500 mb-3">
                            Download a PDF of a completed AI analysis result.
                        </p>
                        <div className="flex gap-2">
                            <input
                                value={analysisId}
                                onChange={(e) => setAnalysisId(e.target.value)}
                                placeholder="Analysis ID (number)"
                                className={`${inputCls} flex-1`}
                            />
                            <button
                                onClick={handleAnalysisPdf}
                                disabled={!!generating}
                                className="flex items-center gap-1.5 px-4 py-2 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg text-sm font-semibold disabled:opacity-60 transition whitespace-nowrap"
                            >
                                {generating === 'analysis-pdf'
                                    ? <Loader2 size={14} className="animate-spin" />
                                    : <><FileDown size={14} /> PDF</>
                                }
                            </button>
                        </div>
                    </Card>
                </div>
            </div>

            {/* ── Report History ────────────────────────── */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-100">
                    <Clock size={16} className="text-[#0f2744]" />
                    <h3 className="text-sm font-bold text-[#0f2744]">Report History</h3>
                </div>
                {loading ? <LoadingSpinner /> : (
                    <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr className="bg-slate-50">
                                    {['Title', 'Type', 'Format', 'Generated By', 'Date'].map((h) => (
                                        <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {history.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="px-4 py-12 text-center text-slate-400 text-sm">
                                            No reports generated yet
                                        </td>
                                    </tr>
                                ) : history.map((r, i) => (
                                    <tr key={r.id} className={`border-b border-slate-50 ${i % 2 === 1 ? 'bg-slate-50/50' : ''}`}>
                                        <td className="px-4 py-3 text-sm font-medium text-slate-700">{r.title}</td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
                                                {capitalize(r.report_type?.replace(/_/g, ' '))}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`text-xs px-2.5 py-1 rounded-full font-bold
                                                ${r.report_format === 'pdf'
                                                    ? 'bg-red-50 text-red-600'
                                                    : 'bg-green-50 text-green-600'
                                                }`}>
                                                {r.report_format?.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-slate-500">{r.generated_by_name}</td>
                                        <td className="px-4 py-3 text-xs text-slate-400">{formatDateTime(r.created_at)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

const Card = ({ title, icon: Icon, children }) => (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
            {Icon && <Icon size={16} className="text-[#0f2744]" />}
            <h3 className="text-sm font-bold text-[#0f2744]">{title}</h3>
        </div>
        {children}
    </div>
);

const inputCls = 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition bg-white';

export default ReportsPage;