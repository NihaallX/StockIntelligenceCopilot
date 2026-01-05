import { CheckCircle, AlertTriangle, XCircle, Power } from 'lucide-react';

interface ContextVerifiedBadgeProps {
  mcp_status: 'success' | 'partial' | 'failed' | 'disabled';
  sources_count: number;
  className?: string;
}

export function ContextVerifiedBadge({ 
  mcp_status, 
  sources_count, 
  className = '' 
}: ContextVerifiedBadgeProps) {
  const config = {
    success: {
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800',
      icon: CheckCircle,
      label: `Context verified by ${sources_count} source${sources_count !== 1 ? 's' : ''}`,
      visible: true
    },
    partial: {
      color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
      icon: AlertTriangle,
      label: `Partial context (${sources_count} source${sources_count !== 1 ? 's' : ''})`,
      visible: true
    },
    failed: {
      color: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800',
      icon: XCircle,
      label: 'Context unavailable',
      visible: true
    },
    disabled: {
      color: 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-800',
      icon: Power,
      label: 'Context disabled',
      visible: false
    }
  };

  const { color, icon: Icon, label, visible } = config[mcp_status] || config.disabled;

  if (!visible) return null;

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm font-medium ${color} ${className}`}>
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </div>
  );
}
