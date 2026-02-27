import { useState }    from 'react';
import { useNavigate } from 'react-router-dom';
import toast           from 'react-hot-toast';
import {
    ArrowLeft, ClipboardList, MapPin, Search,
    ShieldAlert, FileCheck, Loader2,
} from 'lucide-react';
import crimesApi from '../../api/crimesApi';

const CATEGORIES = ['theft','assault','homicide','fraud','cybercrime','robbery','burglary','drug_offense','sexual_offense','vandalism','kidnapping','arson','corruption','other'];
const SEVERITIES = ['low','medium','high','critical'];

const SEV_COLORS = {
    low:      'bg-green-100 text-green-700',
    medium:   'bg-yellow-100 text-yellow-700',
    high:     'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700',
};

const AddCrimePage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({
        title: '', category: 'theft', severity: 'medium', description: '',
        location: '', district: '', date_occurred: '', victim_count: 1,
        weapons_used: '', modus_operandi: '', victim_details: '', evidence_notes: '',
    });

    const handleChange = (e) =>
        setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await crimesApi.create(form);
            toast.success(`Case ${res.data.report.case_number} created!`);
            navigate(`/crimes/${res.data.report.id}`);
        } catch (err) {
            const errors = err.response?.data;
            if (errors) {
                const first = Object.values(errors)[0];
                toast.error(Array.isArray(first) ? first[0] : first);
            } else {
                toast.error('Failed to create report.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-5">

            {/* ── Header ───────────────────────────────── */}
            <div>
                <button
                    onClick={() => navigate('/crimes')}
                    className="flex items-center gap-1.5 text-slate-500 hover:text-[#0f2744] text-sm mb-2 transition"
                >
                    <ArrowLeft size={15} /> Back to Crimes
                </button>
                <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                    <ShieldAlert size={22} className="text-blue-600" />
                    New Crime Report
                </h1>
                <p className="text-slate-500 text-sm mt-0.5">Submit a new crime report to the system</p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-3 gap-4">

                    {/* ── Left — Main Info (2 cols) ─────── */}
                    <div className="col-span-2 space-y-4">

                        {/* Basic Info */}
                        <Card title="Basic Information" icon={ClipboardList}>
                            <Field label="Case Title *" name="title" value={form.title} onChange={handleChange} placeholder="Brief title of the crime" required />

                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className={labelCls}>Category *</label>
                                    <select name="category" value={form.category} onChange={handleChange} className={selectCls}>
                                        {CATEGORIES.map((c) => (
                                            <option key={c} value={c}>
                                                {c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className={labelCls}>Severity *</label>
                                    <select name="severity" value={form.severity} onChange={handleChange} className={selectCls}>
                                        {SEVERITIES.map((s) => (
                                            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className={labelCls}>Description *</label>
                                <textarea
                                    name="description"
                                    value={form.description}
                                    onChange={handleChange}
                                    placeholder="Detailed description of the crime..."
                                    required
                                    rows={4}
                                    className={`${inputCls} resize-vertical`}
                                />
                            </div>
                        </Card>

                        {/* Location & Date */}
                        <Card title="Location & Time" icon={MapPin}>
                            <div className="grid grid-cols-2 gap-3">
                                <Field label="Location *"      name="location"      value={form.location}      onChange={handleChange} placeholder="Specific location" required />
                                <Field label="District *"      name="district"      value={form.district}      onChange={handleChange} placeholder="e.g. Kampala"      required />
                                <Field label="Date Occurred *" name="date_occurred" value={form.date_occurred} onChange={handleChange} type="datetime-local"            required />
                                <Field label="Victim Count"    name="victim_count"  value={form.victim_count}  onChange={handleChange} type="number" placeholder="1" />
                            </div>
                        </Card>

                        {/* Additional Details */}
                        <Card title="Additional Details" icon={Search}>
                            <Field label="Weapons Used"   name="weapons_used"   value={form.weapons_used}   onChange={handleChange} placeholder="e.g. Knife, Pistol" />
                            <Field label="Modus Operandi" name="modus_operandi" value={form.modus_operandi} onChange={handleChange} placeholder="How the crime was committed..." />
                            <Field label="Victim Details" name="victim_details" value={form.victim_details} onChange={handleChange} placeholder="Description of victims..." />
                            <div>
                                <label className={labelCls}>Evidence Notes</label>
                                <textarea
                                    name="evidence_notes"
                                    value={form.evidence_notes}
                                    onChange={handleChange}
                                    placeholder="Any evidence found at the scene..."
                                    rows={3}
                                    className={`${inputCls} resize-vertical`}
                                />
                            </div>
                        </Card>
                    </div>

                    {/* ── Right — Submit ────────────────── */}
                    <div className="space-y-4">
                        <Card title="Submit Report" icon={FileCheck}>
                            <p className="text-xs text-slate-500 mb-4">
                                Review your report before submitting. A unique case number will be auto-generated.
                            </p>

                            {/* Live Preview */}
                            <div className="bg-slate-50 rounded-xl p-4 mb-4 space-y-2.5">
                                {[
                                    { label: 'Title',    value: form.title    || '—' },
                                    { label: 'Category', value: form.category.replace(/_/g, ' ') || '—' },
                                    { label: 'District', value: form.district || '—' },
                                ].map((f) => (
                                    <div key={f.label} className="flex justify-between items-center">
                                        <span className="text-xs text-slate-400">{f.label}</span>
                                        <span className="text-xs font-semibold text-[#0f2744] truncate max-w-[140px]">{f.value}</span>
                                    </div>
                                ))}
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-slate-400">Severity</span>
                                    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${SEV_COLORS[form.severity]}`}>
                                        {form.severity.charAt(0).toUpperCase() + form.severity.slice(1)}
                                    </span>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-xl font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60 transition"
                            >
                                {loading
                                    ? <><Loader2 size={15} className="animate-spin" /> Submitting...</>
                                    : <><ShieldAlert size={15} /> Submit Crime Report</>
                                }
                            </button>

                            <button
                                type="button"
                                onClick={() => navigate('/crimes')}
                                className="w-full py-2.5 mt-2 bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-xl font-medium text-sm transition"
                            >
                                Cancel
                            </button>
                        </Card>
                    </div>
                </div>
            </form>
        </div>
    );
};

/* ── Reusable Card ───────────────────────────────────────── */
const Card = ({ title, icon: Icon, children }) => (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm space-y-3">
        <div className="flex items-center gap-2 mb-1">
            {Icon && <Icon size={16} className="text-[#0f2744]" />}
            <h3 className="text-sm font-bold text-[#0f2744]">{title}</h3>
        </div>
        {children}
    </div>
);

/* ── Reusable Field ──────────────────────────────────────── */
const Field = ({ label, name, type = 'text', value, onChange, placeholder, required }) => (
    <div>
        <label className={labelCls}>{label}</label>
        <input
            name={name} type={type} value={value} onChange={onChange}
            placeholder={placeholder} required={required}
            className={inputCls}
        />
    </div>
);

const labelCls  = 'block text-xs font-semibold text-slate-700 mb-1';
const inputCls  = 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition';
const selectCls = 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition bg-white';

export default AddCrimePage;