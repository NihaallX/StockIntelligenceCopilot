import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

interface ConfidenceBadgeProps {
  level: 'high' | 'medium' | 'low';
  className?: string;
}

export function ConfidenceBadge({ level, className = '' }: ConfidenceBadgeProps) {
  const config = {
    high: {
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800',
      icon: CheckCircle2,
      label: 'High confidence',
      description: '2+ independent sources'
    },
    medium: {
      color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
      icon: AlertCircle,
      label: 'Medium confidence',
      description: '1 source'
    },
    low: {
      color: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800',
      icon: XCircle,
      label: 'Low confidence',
      description: 'No direct sources'
    }
  };

  const { color, icon: Icon, label, description } = config[level];

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${color} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
      <span className="opacity-60 ml-0.5">({description})</span>
    </div>
  );
}
