/**
 * Priority Badge Component
 *
 * Task: T027
 * Spec: specs/1-phase2-advanced-features/spec.md (US1)
 */
'use client';

interface PriorityBadgeProps {
  priority: 'high' | 'medium' | 'low' | 'none';
  size?: 'sm' | 'md' | 'lg';
}

const priorityConfig = {
  high: {
    label: 'High',
    color: 'bg-red-500 text-white',
    icon: '🔴',
  },
  medium: {
    label: 'Medium',
    color: 'bg-amber-500 text-white',
    icon: '🟡',
  },
  low: {
    label: 'Low',
    color: 'bg-green-500 text-white',
    icon: '🟢',
  },
  none: {
    label: 'None',
    color: 'bg-gray-500 text-white',
    icon: '⚪',
  },
};

export function PriorityBadge({ priority, size = 'sm' }: PriorityBadgeProps) {
  const config = priorityConfig[priority];

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  if (priority === 'none') return null;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${config.color} ${sizeClasses[size]}`}
    >
      <span>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
}
