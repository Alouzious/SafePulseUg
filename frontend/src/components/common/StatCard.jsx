const colorMap = {
    blue:   { bg: 'bg-blue-50',   icon: 'bg-blue-100',   text: 'text-blue-700',   value: 'text-[#0f2744]' },
    red:    { bg: 'bg-red-50',    icon: 'bg-red-100',    text: 'text-red-600',    value: 'text-red-700'   },
    green:  { bg: 'bg-green-50',  icon: 'bg-green-100',  text: 'text-green-600',  value: 'text-green-700' },
    yellow: { bg: 'bg-yellow-50', icon: 'bg-yellow-100', text: 'text-yellow-600', value: 'text-yellow-700'},
    purple: { bg: 'bg-purple-50', icon: 'bg-purple-100', text: 'text-purple-600', value: 'text-purple-700'},
};

const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue' }) => {
    const c = colorMap[color] || colorMap.blue;

    return (
        <div className={`rounded-2xl p-5 border border-slate-100 shadow-sm flex items-center gap-4 bg-white`}>
            {/* Icon */}
            <div className={`w-13 h-13 rounded-xl ${c.icon} flex items-center justify-center flex-shrink-0 p-3`}>
                {Icon && <Icon size={24} className={c.text} />}
            </div>

            {/* Text */}
            <div>
                <p className="text-slate-500 text-xs font-medium uppercase tracking-wide">{title}</p>
                <p className={`text-3xl font-bold leading-tight mt-0.5 ${c.value}`}>{value}</p>
                {subtitle && (
                    <p className="text-slate-400 text-xs mt-1">{subtitle}</p>
                )}
            </div>
        </div>
    );
};

export default StatCard;