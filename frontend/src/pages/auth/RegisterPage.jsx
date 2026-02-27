import { useState }           from 'react';
import { useNavigate, Link }  from 'react-router-dom';
import toast                  from 'react-hot-toast';
import { ShieldCheck, BadgeCheck, Mail, Phone, Lock, User, Building2, MapPin, Loader2 } from 'lucide-react';
import authApi                from '../../api/authApi';
import useAuthStore           from '../../store/authStore';

const RANKS = ['constable','corporal','sergeant','inspector','superintendent','commissioner'];
const ROLES = ['officer','detective','analyst','superintendent','admin'];

const RegisterPage = () => {
    const navigate = useNavigate();
    const setAuth  = useAuthStore((s) => s.setAuth);

    const [form, setForm] = useState({
        badge_number: '', email: '', first_name: '', last_name: '',
        password: '', password2: '', rank: 'constable', role: 'officer',
        station: '', district: '', phone_number: '',
    });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) =>
        setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (form.password !== form.password2) {
            toast.error('Passwords do not match.');
            return;
        }
        setLoading(true);
        try {
            const res = await authApi.register(form);
            setAuth(res.data.officer, res.data.tokens);
            toast.success('Account created successfully!');
            navigate('/dashboard');
        } catch (err) {
            const errors = err.response?.data;
            if (errors) {
                const firstError = Object.values(errors)[0];
                toast.error(Array.isArray(firstError) ? firstError[0] : firstError);
            } else {
                toast.error('Registration failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0f2744] via-[#1a3a5c] to-blue-700 flex items-center justify-center p-5">

            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-blue-800/20 blur-3xl" />
            </div>

            <div className="relative bg-white rounded-2xl p-8 w-full max-w-xl shadow-2xl my-6">

                {/* Header */}
                <div className="text-center mb-7">
                    <div className="w-14 h-14 rounded-2xl bg-[#0f2744] flex items-center justify-center mx-auto mb-3 shadow-lg">
                        <ShieldCheck className="text-blue-400" size={28} />
                    </div>
                    <h1 className="text-xl font-bold text-[#0f2744]">Officer Registration</h1>
                    <p className="text-slate-500 text-sm mt-0.5">SafePulse UG — Uganda Police Force</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">

                    {/* Row 1 — Names */}
                    <div className="grid grid-cols-2 gap-3">
                        <Field label="First Name" name="first_name" value={form.first_name} onChange={handleChange} placeholder="John"   icon={User} />
                        <Field label="Last Name"  name="last_name"  value={form.last_name}  onChange={handleChange} placeholder="Doe"    icon={User} />
                    </div>

                    {/* Row 2 — Badge + Phone */}
                    <div className="grid grid-cols-2 gap-3">
                        <Field label="Badge Number" name="badge_number" value={form.badge_number} onChange={handleChange} placeholder="UPF-001"  icon={BadgeCheck} />
                        <Field label="Phone Number" name="phone_number" value={form.phone_number} onChange={handleChange} placeholder="+256..."   icon={Phone} />
                    </div>

                    {/* Email */}
                    <Field label="Email" name="email" type="email" value={form.email} onChange={handleChange} placeholder="officer@upf.go.ug" icon={Mail} />

                    {/* Row 3 — Rank + Role */}
                    <div className="grid grid-cols-2 gap-3">
                        <SelectField label="Rank" name="rank" value={form.rank} onChange={handleChange} options={RANKS} />
                        <SelectField label="Role" name="role" value={form.role} onChange={handleChange} options={ROLES} />
                    </div>

                    {/* Row 4 — Station + District */}
                    <div className="grid grid-cols-2 gap-3">
                        <Field label="Station"  name="station"  value={form.station}  onChange={handleChange} placeholder="Kampala Central" icon={Building2} />
                        <Field label="District" name="district" value={form.district} onChange={handleChange} placeholder="Kampala"          icon={MapPin} />
                    </div>

                    {/* Passwords */}
                    <div className="grid grid-cols-2 gap-3">
                        <Field label="Password"         name="password"  type="password" value={form.password}  onChange={handleChange} placeholder="Min 8 chars"   icon={Lock} />
                        <Field label="Confirm Password" name="password2" type="password" value={form.password2} onChange={handleChange} placeholder="Repeat password" icon={Lock} />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed mt-1"
                    >
                        {loading
                            ? <><Loader2 size={16} className="animate-spin" /> Creating account...</>
                            : <><ShieldCheck size={16} /> Create Account</>
                        }
                    </button>
                </form>

                <p className="text-center mt-5 text-sm text-slate-500">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 font-semibold hover:underline">
                        Login here
                    </Link>
                </p>
            </div>
        </div>
    );
};

/* ── Reusable Field ───────────────────────────────────── */
const Field = ({ label, name, type = 'text', value, onChange, placeholder, icon: Icon }) => (
    <div>
        <label className="block text-xs font-semibold text-slate-700 mb-1">{label}</label>
        <div className="relative">
            {Icon && <Icon className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />}
            <input
                name={name}
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="w-full pl-8 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
        </div>
    </div>
);

const SelectField = ({ label, name, value, onChange, options }) => (
    <div>
        <label className="block text-xs font-semibold text-slate-700 mb-1">{label}</label>
        <select
            name={name}
            value={value}
            onChange={onChange}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition bg-white"
        >
            {options.map((r) => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
            ))}
        </select>
    </div>
);

export default RegisterPage;