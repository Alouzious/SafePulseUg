import { useState, useEffect }  from 'react';
import toast                    from 'react-hot-toast';
import {
    Globe, Search, Lightbulb, History, BrainCircuit,
    Play, Loader2, CheckCircle2, XCircle, Clock,
    MessageSquare, ChevronRight,
} from 'lucide-react';
import analysisApi              from '../../api/analysisApi';
import LoadingSpinner           from '../../components/common/LoadingSpinner';
import { formatDateTime }       from '../../utils/helpers';

const AnalysisPage = () => {
    const [results,   setResults]   = useState([]);
    const [loading,   setLoading]   = useState(true);
    const [running,   setRunning]   = useState(false);
    const [prompt,    setPrompt]    = useState('');
    const [caseNo,    setCaseNo]    = useState('');
    const [activeTab, setActiveTab] = useState('general');
    const [selected,  setSelected]  = useState(null);

    useEffect(() => { fetchResults(); }, []);

    const fetchResults = async () => {
        try {
            const res = await analysisApi.getResults();
            setResults(res.data.results);
        } catch {
            toast.error('Failed to load analysis results.');
        } finally {
            setLoading(false);
        }
    };

    const handleGeneral = async () => {
        setRunning(true);
        try {
            const res = await analysisApi.generalAnalysis(prompt);
            toast.success('General analysis completed!');
            setSelected(res.data.analysis);
            await fetchResults();
        } catch {
            toast.error('Analysis failed. Check your Gemini API key.');
        } finally {
            setRunning(false);
        }
    };

    const handleCaseAnalysis = async () => {
        if (!caseNo.trim()) { toast.error('Please enter a case number.'); return; }
        setRunning(true);
        try {
            const res = await analysisApi.analyzeReport(caseNo.trim());
            toast.success('Case analysis completed!');
            setSelected(res.data.analysis);
            await fetchResults();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Analysis failed.');
        } finally {
            setRunning(false);
        }
    };

    const QUICK_PROMPTS = [
        'What are the top crime hotspots?',
        'Show crime trends for the last 30 days',
        'Which crime types are increasing?',
        'What are the most common modus operandi?',
        'List all unsolved high severity cases',
    ];

    const statusIcon  = { completed: CheckCircle2, failed: XCircle, pending: Clock };
    const statusColor = { completed: 'text-green-600 bg-green-50', failed: 'text-red-600 bg-red-50', pending: 'text-yellow-600 bg-yellow-50' };

    return (
        <div className="space-y-5">

            {/* ── Header ───────────────────────────────── */}
            <div>
                <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                    <BrainCircuit size={24} className="text-blue-600" />
                    AI Crime Analysis
                </h1>
                <p className="text-slate-500 text-sm mt-0.5">
                    Powered by Google Gemini — Analyze crime patterns & generate insights
                </p>
            </div>

            <div className="grid grid-cols-5 gap-4">

                {/* ── Left Panel ───────────────────────── */}
                <div className="col-span-2 space-y-4">

                    {/* Tabs */}
                    <div className="flex bg-slate-100 rounded-xl p-1 gap-1">
                        {[
                            { key: 'general', label: 'General',  icon: Globe   },
                            { key: 'case',    label: 'By Case',  icon: Search  },
                        ].map(({ key, label, icon: Icon }) => (
                            <button
                                key={key}
                                onClick={() => setActiveTab(key)}
                                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-semibold transition-all
                                    ${activeTab === key
                                        ? 'bg-white text-[#0f2744] shadow-sm'
                                        : 'text-slate-500 hover:text-slate-700'
                                    }`}
                            >
                                <Icon size={14} />
                                {label}
                            </button>
                        ))}
                    </div>

                    {/* General Analysis */}
                    {activeTab === 'general' && (
                        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
                            <div className="flex items-center gap-2 mb-1">
                                <Globe size={16} className="text-[#0f2744]" />
                                <h3 className="text-sm font-bold text-[#0f2744]">General Crime Analysis</h3>
                            </div>
                            <p className="text-xs text-slate-500 mb-3">
                                Analyze all crime data for patterns, hotspots, and trends. Leave prompt empty for full auto analysis.
                            </p>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="Optional: Ask something specific e.g. 'What are the most dangerous areas in Kampala this month?'"
                                rows={4}
                                className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm resize-vertical focus:outline-none focus:ring-2 focus:ring-blue-500 transition mb-3"
                            />
                            <button
                                onClick={handleGeneral}
                                disabled={running}
                                className="w-full py-2.5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60 transition"
                            >
                                {running
                                    ? <><Loader2 size={15} className="animate-spin" /> Analyzing...</>
                                    : <><Play size={15} /> Run General Analysis</>
                                }
                            </button>
                        </div>
                    )}

                    {/* Case Analysis */}
                    {activeTab === 'case' && (
                        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
                            <div className="flex items-center gap-2 mb-1">
                                <Search size={16} className="text-[#0f2744]" />
                                <h3 className="text-sm font-bold text-[#0f2744]">Analyze Specific Case</h3>
                            </div>
                            <p className="text-xs text-slate-500 mb-3">
                                Enter a case number to get a deep AI analysis of that specific crime report.
                            </p>
                            <input
                                value={caseNo}
                                onChange={(e) => setCaseNo(e.target.value)}
                                placeholder="e.g. UPF-CASE-00001"
                                className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition mb-3"
                            />
                            <button
                                onClick={handleCaseAnalysis}
                                disabled={running}
                                className="w-full py-2.5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60 transition"
                            >
                                {running
                                    ? <><Loader2 size={15} className="animate-spin" /> Analyzing...</>
                                    : <><Search size={15} /> Analyze Case</>
                                }
                            </button>
                        </div>
                    )}

                    {/* Quick Prompts */}
                    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                            <Lightbulb size={16} className="text-[#0f2744]" />
                            <h3 className="text-sm font-bold text-[#0f2744]">Quick Analysis Prompts</h3>
                        </div>
                        <div className="space-y-1.5">
                            {QUICK_PROMPTS.map((p) => (
                                <button
                                    key={p}
                                    onClick={() => { setPrompt(p); setActiveTab('general'); }}
                                    className="w-full flex items-center gap-2 px-3 py-2 bg-slate-50 hover:bg-blue-50 hover:border-blue-200 border border-slate-100 rounded-lg text-xs text-slate-700 text-left transition group"
                                >
                                    <MessageSquare size={12} className="text-slate-400 group-hover:text-blue-500 flex-shrink-0" />
                                    {p}
                                    <ChevronRight size={12} className="ml-auto text-slate-300 group-hover:text-blue-400" />
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* History */}
                    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                            <History size={16} className="text-[#0f2744]" />
                            <h3 className="text-sm font-bold text-[#0f2744]">
                                Analysis History
                                <span className="ml-1.5 text-xs font-normal text-slate-400">({results.length})</span>
                            </h3>
                        </div>
                        {loading ? <LoadingSpinner /> : (
                            <div className="space-y-1.5 max-h-64 overflow-y-auto">
                                {results.length === 0 ? (
                                    <p className="text-xs text-slate-400 text-center py-5">No analyses yet</p>
                                ) : results.map((r) => {
                                    const StatusIcon = statusIcon[r.status] || Clock;
                                    return (
                                        <button
                                            key={r.id}
                                            onClick={() => setSelected(r)}
                                            className={`w-full text-left px-3 py-2.5 rounded-lg border transition
                                                ${selected?.id === r.id
                                                    ? 'bg-blue-50 border-blue-300'
                                                    : 'bg-slate-50 border-slate-100 hover:bg-slate-100'
                                                }`}
                                        >
                                            <div className="flex items-center justify-between gap-2">
                                                <span className="text-xs font-semibold text-[#0f2744] truncate">
                                                    {r.case_number || 'General Analysis'}
                                                </span>
                                                <span className={`flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full flex-shrink-0 ${statusColor[r.status]}`}>
                                                    <StatusIcon size={10} />
                                                    {r.status}
                                                </span>
                                            </div>
                                            <p className="text-[11px] text-slate-400 mt-0.5">
                                                {formatDateTime(r.created_at)}
                                            </p>
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>

                {/* ── Right Panel — Result Viewer ──────── */}
                <div className="col-span-3 bg-white rounded-2xl border border-slate-100 shadow-sm min-h-[600px] flex flex-col">
                    {running ? (
                        <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8">
                            <div className="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center">
                                <BrainCircuit size={32} className="text-blue-600 animate-pulse" />
                            </div>
                            <p className="text-[#0f2744] font-bold text-lg">AI Agent is analyzing...</p>
                            <p className="text-slate-500 text-sm text-center max-w-sm">
                                The Gemini AI agent is querying your crime database and generating insights. This may take a few seconds.
                            </p>
                            <LoadingSpinner message="Processing crime data..." />
                        </div>
                    ) : selected ? (
                        <div className="p-6 flex flex-col flex-1">
                            {/* Result header */}
                            <div className="flex items-start justify-between mb-4 pb-4 border-b border-slate-100">
                                <div>
                                    <h3 className="text-base font-bold text-[#0f2744]">
                                        {selected.case_number ? `Case: ${selected.case_number}` : 'General Analysis'}
                                    </h3>
                                    <p className="text-xs text-slate-400 mt-0.5">
                                        {formatDateTime(selected.created_at)} · by {selected.requested_by_name}
                                    </p>
                                </div>
                                <span className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${statusColor[selected.status]}`}>
                                    {selected.status === 'completed'
                                        ? <CheckCircle2 size={12} />
                                        : <XCircle size={12} />
                                    }
                                    {selected.status}
                                </span>
                            </div>

                            {/* Result content */}
                            <div className="flex-1 bg-slate-50 rounded-xl p-4 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap overflow-y-auto max-h-[520px]">
                                {selected.ai_summary || selected.error_message || 'No content available.'}
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400 p-8">
                            <div className="w-16 h-16 rounded-2xl bg-slate-50 flex items-center justify-center">
                                <BrainCircuit size={32} className="text-slate-300" />
                            </div>
                            <p className="text-base font-semibold text-slate-500">No analysis selected</p>
                            <p className="text-sm text-center text-slate-400">
                                Run a new analysis or select one from history
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AnalysisPage;