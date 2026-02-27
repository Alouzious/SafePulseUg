import { NavLink }        from 'react-router-dom';
import {
    LayoutDashboard,
    ShieldAlert,
    Upload,
    BrainCircuit,
    MessageSquareText,
    FileBarChart2,
    LogOut,
    ShieldCheck,
} from 'lucide-react';
import useAuthStore from '../../store/authStore';

const navItems = [
    { path: '/dashboard',     label: 'Dashboard',     icon: LayoutDashboard   },
    { path: '/crimes',        label: 'Crime Reports', icon: ShieldAlert,  end: true },
    { path: '/crimes/upload', label: 'Upload Crimes', icon: Upload         },
    { path: '/analysis',      label: 'AI Analysis',   icon: BrainCircuit   },
    { path: '/chat',          label: 'AI Chat',        icon: MessageSquareText },
    { path: '/reports',       label: 'Reports',        icon: FileBarChart2  },
];

const Sidebar = () => {
    const officer = useAuthStore((s) => s.officer);
    const logout  = useAuthStore((s) => s.logout);

    return (
        <aside className="w-60 min-h-screen bg-[#0f2744] flex flex-col flex-shrink-0 shadow-2xl">

            {/* ── Logo ─────────────────────────────── */}
            <div className="flex items-center gap-3 px-5 py-6 border-b border-white/10">
                <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <ShieldCheck className="text-blue-400" size={22} />
                </div>
                <div>
                    <p className="text-white font-bold text-[15px] leading-tight">SafePulse UG</p>
                    <p className="text-white/40 text-[11px] leading-tight mt-0.5">Uganda Police Force</p>
                </div>
            </div>

            {/* ── Nav Links ────────────────────────── */}
            <nav className="flex-1 px-3 py-4 space-y-0.5">
                {navItems.map(({ path, label, icon: Icon, end }) => (
                    <NavLink
                        key={path}
                        to={path}
                        end={end}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group
                            ${isActive
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/40'
                                : 'text-white/60 hover:text-white hover:bg-white/8'
                            }`
                        }
                    >
                        {({ isActive }) => (
                            <>
                                <Icon
                                    size={18}
                                    className={isActive ? 'text-white' : 'text-white/50 group-hover:text-white/80 transition-colors'}
                                />
                                {label}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* ── Officer Info & Logout ─────────────── */}
            <div className="px-3 py-4 border-t border-white/10 space-y-3">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500/30 flex items-center justify-center text-blue-300 text-xs font-bold flex-shrink-0">
                        {officer?.full_name?.[0]?.toUpperCase() || 'O'}
                    </div>
                    <div className="min-w-0">
                        <p className="text-white text-[13px] font-semibold truncate leading-tight">
                            {officer?.full_name || 'Officer'}
                        </p>
                        <p className="text-white/40 text-[11px] truncate mt-0.5">
                            {officer?.badge_number} · {officer?.rank}
                        </p>
                    </div>
                </div>

                <button
                    onClick={logout}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
                               bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300
                               border border-red-500/20 hover:border-red-500/30
                               text-sm font-medium transition-all duration-150"
                >
                    <LogOut size={15} />
                    Logout
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;