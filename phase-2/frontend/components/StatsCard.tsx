'use client';

interface StatsCardProps {
  label: string;
  value: number;
  icon: 'total' | 'pending' | 'completed';
  color: 'cyan' | 'fuchsia' | 'green';
}

export default function StatsCard({ label, value, icon, color }: StatsCardProps) {
  const colorConfig = {
    cyan: {
      border: 'border-cyan-500/30 hover:border-cyan-400',
      text: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      shadow: 'hover:shadow-[0_0_30px_rgba(0,217,255,0.2)]',
      gradient: 'from-cyan-500 to-cyan-600',
    },
    fuchsia: {
      border: 'border-fuchsia-500/30 hover:border-fuchsia-400',
      text: 'text-fuchsia-400',
      bg: 'bg-fuchsia-500/10',
      shadow: 'hover:shadow-[0_0_30px_rgba(217,70,239,0.2)]',
      gradient: 'from-fuchsia-500 to-fuchsia-600',
    },
    green: {
      border: 'border-green-500/30 hover:border-green-400',
      text: 'text-green-400',
      bg: 'bg-green-500/10',
      shadow: 'hover:shadow-[0_0_30px_rgba(34,197,94,0.2)]',
      gradient: 'from-green-500 to-green-600',
    },
  };

  const icons = {
    total: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    pending: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    completed: (
      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  };

  const config = colorConfig[color];

  return (
    <div className={`
      relative bg-card/80 backdrop-blur-sm p-4 sm:p-6 rounded-2xl border-2
      ${config.border} ${config.shadow}
      transition-all duration-300 card-hover
    `}>
      <div className="flex items-center gap-3 sm:gap-4">
        <div className={`
          w-12 h-12 sm:w-14 sm:h-14 rounded-xl
          bg-gradient-to-br ${config.gradient}
          flex items-center justify-center
          shadow-lg
        `}>
          {icons[icon]}
        </div>
        <div>
          <p className="text-xs sm:text-sm text-muted-foreground uppercase tracking-wide">{label}</p>
          <p className={`text-2xl sm:text-3xl font-bold ${config.text}`}>
            {value}
          </p>
        </div>
      </div>
    </div>
  );
}
