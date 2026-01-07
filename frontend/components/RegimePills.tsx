import { Activity, AlertTriangle, Droplets, Network } from 'lucide-react';

export type RegimeType = 
  | 'index-led' 
  | 'pre-market-volatility' 
  | 'low-liquidity' 
  | 'sector-correlation'
  | 'high-volume'
  | 'range-bound';

interface RegimePillProps {
  type: RegimeType;
  className?: string;
}

export function RegimePill({ type, className = '' }: RegimePillProps) {
  const config = {
    'index-led': {
      label: 'Index-led move',
      color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-700',
      icon: Activity
    },
    'pre-market-volatility': {
      label: 'Pre-market volatility',
      color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-700',
      icon: AlertTriangle
    },
    'low-liquidity': {
      label: 'Low liquidity zone',
      color: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-700',
      icon: Droplets
    },
    'sector-correlation': {
      label: 'Sector correlation detected',
      color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-700',
      icon: Network
    },
    'high-volume': {
      label: 'High volume',
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-700',
      icon: Activity
    },
    'range-bound': {
      label: 'Range-bound',
      color: 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700',
      icon: Activity
    }
  };
  
  const { label, color, icon: Icon } = config[type];
  
  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium ${color} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
    </div>
  );
}

interface RegimePillsContainerProps {
  regimes: RegimeType[];
  className?: string;
}

export function RegimePillsContainer({ regimes, className = '' }: RegimePillsContainerProps) {
  if (!regimes || regimes.length === 0) return null;
  
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {regimes.map((regime, index) => (
        <RegimePill key={index} type={regime} />
      ))}
    </div>
  );
}
