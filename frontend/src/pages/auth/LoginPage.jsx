import { useState }           from 'react';
import { useNavigate, Link }  from 'react-router-dom';
import toast                  from 'react-hot-toast';
import { ShieldCheck, BadgeCheck, Lock, Loader2 } from 'lucide-react';
import authApi                from '../../api/authApi';
import useAuthStore           from '../../store/authStore';

const LoginPage = () => {
    const navigate = useNavigate();
    const setAuth  = useAuthStore((s) => s.setAuth);

    const [form, setForm]       = useState({ badge_number: '', password: '' });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) =>
        setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await authApi.login(form);
            setAuth(res.data.officer, res.data.tokens);
            toast.success(`Welcome, ${res.data.officer.first_name}!`);
            navigate('/dashboard');
        } catch (err) {
            toast.error(err.response?.data?.non_field_errors?.[0] || 'Login failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0f2744] via-[#1a3a5c] to-blue-700 flex items-center justify-center p-5">

            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-blue-800/20 blur-3xl" />
            </div>

            <div className="relative bg-white rounded-2xl p-10 w-full max-w-md shadow-2xl">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 rounded-2xl bg-[#0f2744] flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <ShieldCheck className="text-blue-400" size={32} />
                    </div>
                    <h1 className="text-2xl font-bold text-[#0f2744]">SafePulse UG</h1>
                    <p className="text-slate-500 text-sm mt-1">Uganda Police Force — Crime Analysis System</p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                            Badge Number
                        </label>
                        <div className="relative">
                            <BadgeCheck className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                            <input
                                name="badge_number"
                                value={form.badge_number}
                                onChange={handleChange}
                                placeholder="e.g. UPF-001"
                                required
                                className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                            Password
                        </label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                            <input
                                name="password"
                                type="password"
                                value={form.password}
                                onChange={handleChange}
                                placeholder="Enter your password"
                                required
                                className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-lg font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed mt-2"
                    >
                        {loading
                            ? <><Loader2 size={16} className="animate-spin" /> Logging in...</>
                            : <><ShieldCheck size={16} /> Login to SafePulse</>
                        }
                    </button>
                </form>

                <p className="text-center mt-6 text-sm text-slate-500">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-blue-600 font-semibold hover:underline">
                        Register here
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;