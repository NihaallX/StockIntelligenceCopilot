import { Clock, AlertTriangle } from 'lucide-react';

interface SignalFreshnessProps {
  generatedAt?: string;
  className?: string;
}

export function SignalFreshness({ generatedAt, className = '' }: SignalFreshnessProps) {
  if (!generatedAt) return null;
  
  const now = new Date();
  const signalTime = new Date(generatedAt);
  const minutesAgo = Math.floor((now.getTime() - signalTime.getTime()) / 60000);
  
  // Determine freshness level
  const isStale = minutesAgo > 15;
  const isModerate = minutesAgo > 5 && minutesAgo <= 15;
  
  let color: string;
  let icon: typeof Clock;
  let message: string;
  
  if (isStale) {
    color = 'text-red-600 dark:text-red-400';
    icon = AlertTriangle;
    message = `Generated ${minutesAgo} minutes ago - Consider refreshing`;
  } else if (isModerate) {
    color = 'text-amber-600 dark:text-amber-400';
    icon = Clock;
    message = `Generated ${minutesAgo} minutes ago`;
  } else {
    color = 'text-green-600 dark:text-green-400';
    icon = Clock;
    message = minutesAgo === 0 ? 'Just generated' : `Generated ${minutesAgo} minute${minutesAgo === 1 ? '' : 's'} ago`;
  }
  
  const Icon = icon;
  
  return (
    <div className={`flex items-center gap-1.5 text-xs ${color} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{message}</span>
    </div>
  );
}

interface TimeOfDayContextProps {
  className?: string;
}

export function TimeOfDayContext({ className = '' }: TimeOfDayContextProps) {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const totalMinutes = hours * 60 + minutes;
  
  // Market times in IST (9:15 - 15:30)
  const marketOpen = 9 * 60 + 15;      // 9:15 AM
  const openVolatility = 10 * 60 + 30;  // 10:30 AM
  const lunchStart = 12 * 60 + 30;      // 12:30 PM
  const lunchEnd = 14 * 60;             // 2:00 PM
  const closingStart = 14 * 60 + 30;    // 2:30 PM
  const marketClose = 15 * 60 + 30;     // 3:30 PM
  
  let context: { label: string; color: string; description: string } | null = null;
  
  if (totalMinutes >= marketOpen && totalMinutes < openVolatility) {
    context = {
      label: 'Opening volatility',
      color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-200',
      description: 'High volatility period - signals may fluctuate'
    };
  } else if (totalMinutes >= lunchStart && totalMinutes < lunchEnd) {
    context = {
      label: 'Lunch compression',
      color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200',
      description: 'Low activity period - reduced liquidity'
    };
  } else if (totalMinutes >= closingStart && totalMinutes <= marketClose) {
    context = {
      label: 'Closing expansion',
      color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200',
      description: 'High activity period - position adjustments common'
    };
  } else if (totalMinutes < marketOpen || totalMinutes > marketClose) {
    context = {
      label: 'Pre/Post market',
      color: 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 border-gray-200',
      description: 'Market closed - analysis based on last session data'
    };
  }
  
  if (!context) return null;
  
  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${context.color} ${className}`} title={context.description}>
      <Clock className="w-3.5 h-3.5" />
      <span>{context.label}</span>
    </div>
  );
}
