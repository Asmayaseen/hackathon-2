'use client';

import { useTranslation } from '@/lib/i18n';

interface ProgressBarProps {
  completed: number;
  total: number;
}

export default function ProgressBar({ completed, total }: ProgressBarProps) {
  const { t } = useTranslation();
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  if (total === 0) {
    return null;
  }

  return (
    <div className="relative bg-card/80 backdrop-blur-sm p-4 sm:p-6 rounded-2xl border-2 border-cyan-500/20">
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm text-muted-foreground uppercase tracking-wide">{t('progress.missionProgress')}</span>
        <span className="text-sm font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-400 bg-clip-text text-transparent">
          {percentage}%
        </span>
      </div>

      <div className="h-4 bg-background/50 rounded-full overflow-hidden border border-cyan-500/20">
        <div
          className="h-full bg-gradient-to-r from-cyan-500 via-fuchsia-500 to-purple-500 rounded-full transition-all duration-700 ease-out relative"
          style={{ width: `${percentage}%` }}
        >
          {/* Animated shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
        </div>
      </div>

      <div className="flex justify-between items-center mt-3">
        <p className="text-xs text-muted-foreground">
          <span className="text-cyan-400 font-semibold">{completed}</span> of{' '}
          <span className="text-fuchsia-400 font-semibold">{total}</span> {t('progress.tasksCompleted')}
        </p>
        {percentage === 100 && (
          <span className="text-xs text-green-400 font-medium uppercase tracking-wide animate-pulse">
            {t('progress.allClear')}
          </span>
        )}
      </div>
    </div>
  );
}
