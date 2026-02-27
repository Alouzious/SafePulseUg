import { useState, useEffect }    from 'react';
import { useParams, useNavigate }  from 'react-router-dom';
import toast                       from 'react-hot-toast';
import {
    ArrowLeft, FileDown, BrainCircuit, Loader2,
    ClipboardList, FileText, UserX, Eye, Bot,
    CheckCircle2, ShieldAlert,
} from 'lucide-react';
import crimesApi    from '../../api/crimesApi';
import analysisApi  from '../../api/analysisApi';
import reportsApi   from '../../api/reportsApi';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getSeverityColor, getStatusColor, capitalize, formatDateTime, downloadFile } from '../../utils/helpers';

const CrimeDetailPage = () => {
    const { id }    = useParams();
    const navigate  = useNavigate();
    const [crime,        setCrime]        = useState(null);
    const [loading,      setLoading]      = useState(true);
    const [analyzing,    setAnalyzing]    = useState(false);
    const [downloading,  setDownloading]  = useState(false);

    useEffect(() => {
        const fetchCrime = async () => {
            try {
                const res = await crimesApi.getById(id);
                setCrime(res.data);
            } catch {
                toast.error('Crime report not found.');
                navigate('/crimes');
            } finally {
                setLoading(false);
            }
        };
        fetchCrime();
    }, [id]);

    const handleAnalyze = async () => {
        setAnalyzing(true);
        try {
            await analysisApi.analyzeReport(crime.case_number);
            toast.success('AI analysis completed!');
            const res = await crimesApi.getById(id);
            setCrime(res.data);
        } catch {
            toast.error('Analysis failed. Check your Gemini API key.');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleDownloadPdf = async () => {
        setDownloading(true);
        try {
            const res = await reportsApi.downloadCrimePdf(crime.case_number);
            downloadFile(res.data, `${crime.case_number}_report.pdf`);
            toast.success('PDF downloaded!');
        } catch {
            toast.error('Failed to download PDF.');
        } finally {
            setDownloading(false);
        }
    };

    if (loading) return <LoadingSpinner />;
    if (!crime)  return null;

    return (
        <div className="space-y-5">

            {/* ── Header ───────────────────────────────── */}
            <div className="flex items-start justify-between">
                <div>
                    <button
                        onClick={() => navigate('/crimes')}
                        className="flex items-center gap-1.5 text-slate-500 hover:text-[#0f2744] text-sm mb-2 transition"
                    >
                        <ArrowLeft size={15} /> Back to Crimes
                    </button>
                    <h1 className="text-xl font-bold text-[#0f2744]">{crime.case_number}</h1>
                    <p className="text-slate-500 text-sm mt-0.5">{crime.title}</p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                    <button
                        onClick={handleDownloadPdf}
                        disabled={downloading}
                        className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-[#0f2744] hover:bg-slate-50 transition disabled:opacity-60"
                    >
                        {downloading ? <Loader2 size={14} className="animate-spin" /> : <FileDown size={14} />}
                        PDF
                    </button>
                    <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className="flex items-center gap-2 px-4 py-2 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg text-sm font-semibold transition disabled:opacity-60"
                    >
                        {analyzing ? <Loader2 size={14} className="animate-spin" /> : <BrainCircuit size={14} />}
                        {analyzing ? 'Analyzing...' : 'Analyze with AI'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">

                {/* ── Left (2 cols) ─────────────────────── */}
                <div className="col-span-2 space-y-4">

                    {/* Summary */}
                    <Card title="Case Summary" icon={ClipboardList}>
                        <div className="grid grid-cols-2 gap-4 mt-2">
                            {[
                                { label: 'Category',      value: capitalize(crime.category) },
                                { label: 'District',      value: crime.district },
                                { label: 'Location',      value: crime.location },
                                { label: 'Date Occurred', value: formatDateTime(crime.date_occurred) },
                                { label: 'Victim Count',  value: crime.victim_count },
                                { label: 'Reported By',   value: crime.reported_by_name },
                            ].map((f) => (
                                <div key={f.label}>
                                    <p className="text-[11px] text-slate-400">{f.label}</p>
                                    <p className="text-sm font-semibold text-[#0f2744] mt-0.5">{f.value || 'N/A'}</p>
                                </div>
                            ))}
                        </div>

                        {/* Badges */}
                        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-100">
                            <span
                                className="px-3 py-1 rounded-full text-xs font-bold text-white"
                                style={{ background: getSeverityColor(crime.severity) }}
                            >
                                {crime.severity?.toUpperCase()}
                            </span>
                            <span
                                className="px-3 py-1 rounded-full text-xs font-bold"
                                style={{ background: getStatusColor(crime.status) + '22', color: getStatusColor(crime.status) }}
                            >
                                {capitalize(crime.status)}
                            </span>
                            {crime.is_analyzed && (
                                <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-green-50 text-green-600">
                                    <CheckCircle2 size={11} /> AI Analyzed
                                </span>
                            )}
                        </div>
                    </Card>

                    {/* Description */}
                    <Card title="Description" icon={FileText}>
                        <p className="text-sm text-slate-700 leading-relaxed">{crime.description}</p>
                        {crime.weapons_used && (
                            <p className="text-sm text-slate-600 mt-3">
                                <span className="font-semibold text-[#0f2744]">Weapons:</span> {crime.weapons_used}
                            </p>
                        )}
                        {crime.modus_operandi && (
                            <p className="text-sm text-slate-600 mt-1.5">
                                <span className="font-semibold text-[#0f2744]">Modus Operandi:</span> {crime.modus_operandi}
                            </p>
                        )}
                        {crime.evidence_notes && (
                            <p className="text-sm text-slate-600 mt-1.5">
                                <span className="font-semibold text-[#0f2744]">Evidence:</span> {crime.evidence_notes}
                            </p>
                        )}
                    </Card>

                    {/* Suspects */}
                    {crime.suspects?.length > 0 && (
                        <Card title={`Suspects (${crime.suspects.length})`} icon={UserX}>
                            <div className="space-y-2 mt-1">
                                {crime.suspects.map((s) => (
                                    <div key={s.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                                        <p className="font-semibold text-sm text-[#0f2744]">{s.name || 'Unknown'}</p>
                                        <p className="text-xs text-slate-500 mt-1">
                                            Age: {s.age_estimate || 'N/A'} · Gender: {s.gender} ·
                                            Arrested:{' '}
                                            <span className={s.is_arrested ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'}>
                                                {s.is_arrested ? 'Yes' : 'No'}
                                            </span>
                                        </p>
                                        {s.description && <p className="text-xs text-slate-400 mt-1">{s.description}</p>}
                                    </div>
                                ))}
                            </div>
                        </Card>
                    )}

                    {/* Witnesses */}
                    {crime.witnesses?.length > 0 && (
                        <Card title={`Witnesses (${crime.witnesses.length})`} icon={Eye}>
                            <div className="space-y-2 mt-1">
                                {crime.witnesses.map((w) => (
                                    <div key={w.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                                        <p className="font-semibold text-sm text-[#0f2744]">
                                            {w.is_anonymous ? '🔒 Anonymous' : w.name}
                                        </p>
                                        {w.statement && <p className="text-xs text-slate-500 mt-1">{w.statement}</p>}
                                    </div>
                                ))}
                            </div>
                        </Card>
                    )}
                </div>

                {/* ── Right — AI Analysis ───────────────── */}
                <div>
                    <Card title="AI Analysis" icon={Bot}>
                        {crime.analysis_results?.length > 0 ? (
                            <div className="space-y-4 mt-1">
                                {crime.analysis_results.map((a) => (
                                    <div key={a.id}>
                                        <p className="text-[11px] text-slate-400 mb-2">{formatDateTime(a.created_at)}</p>
                                        <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 p-3 rounded-xl">
                                            {a.ai_summary}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 text-slate-400">
                                <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
                                    <BrainCircuit size={24} className="text-slate-300" />
                                </div>
                                <p className="text-sm font-medium text-slate-500">No analysis yet</p>
                                <p className="text-xs text-slate-400 mt-1">Click "Analyze with AI" to start.</p>
                            </div>
                        )}
                    </Card>
                </div>
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

export default CrimeDetailPage;