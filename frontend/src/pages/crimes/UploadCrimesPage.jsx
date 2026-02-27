import { useState }    from 'react';
import { useNavigate } from 'react-router-dom';
import toast           from 'react-hot-toast';
import {
    Upload, FileDown, FileSpreadsheet, BrainCircuit,
    CheckCircle2, XCircle, SkipForward, Rows3,
    Loader2, ShieldAlert, BarChart3,
} from 'lucide-react';
import api from '../../api/axios';

const UploadCrimesPage = () => {
    const navigate = useNavigate();
    const [file,      setFile]      = useState(null);
    const [loading,   setLoading]   = useState(false);
    const [result,    setResult]    = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysis,  setAnalysis]  = useState(null);
    const [dragOver,  setDragOver]  = useState(false);

    const handleFile = (selectedFile) => {
        if (!selectedFile) return;
        const ext = selectedFile.name.split('.').pop().toLowerCase();
        if (!['csv', 'xlsx', 'xls'].includes(ext)) {
            toast.error('Only CSV and Excel files are supported.');
            return;
        }
        setFile(selectedFile);
        setResult(null);
        setAnalysis(null);
    };

    const handleUpload = async () => {
        if (!file) { toast.error('Please select a file first.'); return; }
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await api.post('/api/crimes/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setResult(res.data);
            toast.success(`${res.data.summary.created} crimes imported!`);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Upload failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyzeAll = async () => {
        setAnalyzing(true);
        setAnalysis(null);
        try {
            const res = await api.post('/api/analysis/general/', {
                prompt: `I just uploaded ${result?.summary?.created} new crime records. Please analyze ALL crime data in the database and provide: 1. Key patterns and trends 2. Most dangerous districts 3. Most common crime types 4. High priority cases needing attention 5. Recommendations for police deployment`
            });
            setAnalysis(res.data.analysis.ai_summary);
            toast.success('AI analysis complete!');
        } catch {
            toast.error('Analysis failed. Try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleTemplate = async () => {
        try {
            const res  = await api.get('/api/crimes/upload/template/', { responseType: 'blob' });
            const url  = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href  = url;
            link.setAttribute('download', 'crime_upload_template.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
            toast.success('Template downloaded!');
        } catch {
            toast.error('Failed to download template.');
        }
    };

    const COLUMNS = [
        { col: 'title',          req: true,  note: 'Crime title' },
        { col: 'category',       req: true,  note: 'theft, robbery, assault...' },
        { col: 'severity',       req: true,  note: 'low, medium, high, critical' },
        { col: 'description',    req: true,  note: 'What happened' },
        { col: 'location',       req: true,  note: 'Specific place' },
        { col: 'district',       req: true,  note: 'Kampala, Wakiso...' },
        { col: 'date_occurred',  req: true,  note: 'YYYY-MM-DD HH:MM:SS' },
        { col: 'victim_count',   req: false, note: 'Number of victims' },
        { col: 'weapons_used',   req: false, note: 'Optional' },
        { col: 'modus_operandi', req: false, note: 'How crime was done' },
    ];

    return (
        <div className="space-y-5">

            {/* ── Header ───────────────────────────────── */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                        <Upload size={22} className="text-blue-600" />
                        Upload Crime Data
                    </h1>
                    <p className="text-slate-500 text-sm mt-0.5">
                        Bulk import crimes from CSV or Excel — then let AI analyze the patterns
                    </p>
                </div>
                <button
                    onClick={handleTemplate}
                    className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-[#0f2744] hover:bg-slate-50 transition"
                >
                    <FileDown size={15} /> Download CSV Template
                </button>
            </div>

            <div className="grid grid-cols-2 gap-4">

                {/* ── Left ─────────────────────────────── */}
                <div className="space-y-4">

                    {/* Drop Zone Card */}
                    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm space-y-4">
                        <div className="flex items-center gap-2">
                            <FileSpreadsheet size={16} className="text-[#0f2744]" />
                            <h3 className="text-sm font-bold text-[#0f2744]">Select File</h3>
                        </div>
                        <p className="text-xs text-slate-500">
                            Supports <strong>CSV</strong> and <strong>Excel (.xlsx)</strong> files.
                            Download the template above to see the correct format.
                        </p>

                        {/* Drop Zone */}
                        <div
                            onDragOver={(e)  => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={()  => setDragOver(false)}
                            onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
                            onClick={() => document.getElementById('fileInput').click()}
                            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
                                ${dragOver
                                    ? 'border-blue-400 bg-blue-50'
                                    : file
                                        ? 'border-green-300 bg-green-50'
                                        : 'border-slate-200 bg-slate-50 hover:border-blue-300 hover:bg-blue-50/30'
                                }`}
                        >
                            <div className="flex flex-col items-center gap-2">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${file ? 'bg-green-100' : 'bg-slate-100'}`}>
                                    {file
                                        ? <CheckCircle2 size={24} className="text-green-600" />
                                        : <Upload size={24} className="text-slate-400" />
                                    }
                                </div>
                                {file ? (
                                    <>
                                        <p className="font-semibold text-sm text-[#0f2744]">{file.name}</p>
                                        <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB — Click to change</p>
                                    </>
                                ) : (
                                    <>
                                        <p className="font-semibold text-sm text-slate-700">Drag & drop your file here</p>
                                        <p className="text-xs text-slate-400">or click to browse — CSV, XLSX supported</p>
                                    </>
                                )}
                            </div>
                        </div>

                        <input
                            id="fileInput"
                            type="file"
                            accept=".csv,.xlsx,.xls"
                            onChange={(e) => handleFile(e.target.files[0])}
                            className="hidden"
                        />

                        <button
                            onClick={handleUpload}
                            disabled={!file || loading}
                            className="w-full py-3 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-xl font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
                        >
                            {loading
                                ? <><Loader2 size={15} className="animate-spin" /> Uploading...</>
                                : <><Upload size={15} /> Upload & Import Crimes</>
                            }
                        </button>
                    </div>

                    {/* Required Columns */}
                    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                            <Rows3 size={16} className="text-[#0f2744]" />
                            <h3 className="text-sm font-bold text-[#0f2744]">Required CSV Columns</h3>
                        </div>
                        <div className="space-y-1.5">
                            {COLUMNS.map((f) => (
                                <div key={f.col} className="flex items-center gap-2 text-xs">
                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${f.req ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-500'}`}>
                                        {f.req ? 'required' : 'optional'}
                                    </span>
                                    <code className="font-bold text-[#0f2744]">{f.col}</code>
                                    <span className="text-slate-400">— {f.note}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* ── Right — Results ───────────────────── */}
                <div className="space-y-4">

                    {/* Upload Result */}
                    {result && (
                        <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm space-y-4">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 size={16} className="text-green-600" />
                                <h3 className="text-sm font-bold text-[#0f2744]">Upload Result</h3>
                            </div>

                            {/* Stats Grid */}
                            <div className="grid grid-cols-2 gap-3">
                                {[
                                    { label: 'Total Rows', value: result.summary.total_rows, icon: Rows3,       bg: 'bg-blue-50',   text: 'text-blue-700'  },
                                    { label: 'Imported',   value: result.summary.created,    icon: CheckCircle2, bg: 'bg-green-50',  text: 'text-green-700' },
                                    { label: 'Skipped',    value: result.summary.skipped,    icon: SkipForward,  bg: 'bg-orange-50', text: 'text-orange-600'},
                                    { label: 'Errors',     value: result.summary.errors,     icon: XCircle,      bg: 'bg-red-50',    text: 'text-red-600'   },
                                ].map(({ label, value, icon: Icon, bg, text }) => (
                                    <div key={label} className={`${bg} rounded-xl p-3 flex items-center gap-3`}>
                                        <Icon size={18} className={text} />
                                        <div>
                                            <p className={`text-xl font-bold ${text}`}>{value}</p>
                                            <p className={`text-xs ${text} opacity-80`}>{label}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Created cases */}
                            {result.created_cases.length > 0 && (
                                <div className="max-h-40 overflow-y-auto space-y-1">
                                    {result.created_cases.map((c) => (
                                        <div key={c.case_number} className="flex justify-between px-3 py-1.5 bg-slate-50 rounded-lg text-xs">
                                            <span className="font-bold text-[#0f2744]">{c.case_number}</span>
                                            <span className="text-slate-600 truncate mx-2">{c.title?.substring(0, 30)}</span>
                                            <span className="text-slate-400 flex-shrink-0">{c.district}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Error rows */}
                            {result.error_rows.length > 0 && (
                                <div className="bg-red-50 rounded-xl p-3 border border-red-100 space-y-1">
                                    <p className="text-xs font-bold text-red-600 mb-2">Failed Rows:</p>
                                    {result.error_rows.map((e, i) => (
                                        <p key={i} className="text-xs text-red-500">Row {e.row}: {e.error}</p>
                                    ))}
                                </div>
                            )}

                            <button
                                onClick={handleAnalyzeAll}
                                disabled={analyzing}
                                className="w-full py-2.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60 transition"
                            >
                                {analyzing
                                    ? <><Loader2 size={15} className="animate-spin" /> AI is analyzing...</>
                                    : <><BrainCircuit size={15} /> Analyze Imported Data with AI</>
                                }
                            </button>
                        </div>
                    )}

                    {/* AI Analysis Result */}
                    {analyzing && (
                        <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm text-center">
                            <div className="w-14 h-14 rounded-2xl bg-purple-50 flex items-center justify-center mx-auto mb-3">
                                <BrainCircuit size={28} className="text-purple-600 animate-pulse" />
                            </div>
                            <p className="font-bold text-[#0f2744]">AI Agent is analyzing crime patterns...</p>
                            <p className="text-sm text-slate-500 mt-1">Gemini is processing your crime data</p>
                        </div>
                    )}

                    {analysis && (
                        <div className="bg-white rounded-2xl p-5 border border-purple-100 border-l-4 border-l-purple-600 shadow-sm space-y-3">
                            <div className="flex items-center gap-2">
                                <BrainCircuit size={16} className="text-purple-600" />
                                <h3 className="text-sm font-bold text-purple-700">AI Crime Pattern Analysis</h3>
                            </div>
                            <div className="bg-purple-50 rounded-xl p-4 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                                {analysis}
                            </div>
                            <div className="flex gap-2 pt-1">
                                <button
                                    onClick={() => navigate('/crimes')}
                                    className="flex-1 flex items-center justify-center gap-2 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-[#0f2744] hover:bg-slate-50 transition"
                                >
                                    <ShieldAlert size={14} /> View All Crimes
                                </button>
                                <button
                                    onClick={() => navigate('/analysis')}
                                    className="flex-1 flex items-center justify-center gap-2 py-2 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg text-sm font-semibold transition"
                                >
                                    <BarChart3 size={14} /> Full Analysis Page
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Empty State */}
                    {!result && !analyzing && (
                        <div className="bg-white rounded-2xl p-10 border border-slate-100 shadow-sm text-center">
                            <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
                                <BarChart3 size={28} className="text-slate-300" />
                            </div>
                            <p className="font-semibold text-slate-600">Upload a file to get started</p>
                            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                                1. Download the CSV template<br />
                                2. Fill it with your crime data<br />
                                3. Upload and import<br />
                                4. Let AI analyze the patterns
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default UploadCrimesPage;