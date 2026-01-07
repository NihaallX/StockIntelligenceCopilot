import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';

export type DataQuality = 'live' | 'demo' | 'stale' | 'fallback';

interface DataQualityBadgeProps {
  quality: DataQuality;
  source?: string;
  className?: string;
}

export function DataQualityBadge({ quality, source, className = '' }: DataQualityBadgeProps) {
  const config = {
    live: {
      label: 'LIVE',
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700',
      icon: CheckCircle,
      description: 'Real-time market data'
    },
    demo: {
      label: 'DEMO',
      color: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700',
      icon: AlertCircle,
      description: 'Delayed or sample data'
    },
    stale: {
      label: 'STALE',
      color: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700',
      icon: XCircle,
      description: 'Outdated data - use caution'
    },
    fallback: {
      label: 'FALLBACK',
      color: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700',
      icon: Clock,
      description: 'Backup data source in use'
    }
  };
  
  const { label, color, icon: Icon, description } = config[quality];
  
  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-semibold ${color} ${className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
      {source && <span className="text-[10px] opacity-70">• {source}</span>}
    </div>
  );
}

interface DataSourceInfoProps {
  dataSource: string;
  confidence?: number;
  fallbackUsed?: boolean;
  className?: string;
}

export function DataSourceInfo({ dataSource, confidence, fallbackUsed, className = '' }: DataSourceInfoProps) {
  let quality: DataQuality = 'live';
  
  // Determine quality based on data source and fallback status
  if (fallbackUsed) {
    quality = 'fallback';
  } else if (confidence && confidence < 0.7) {
    quality = 'demo';
  }
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <DataQualityBadge quality={quality} source={dataSource} />
      {confidence !== undefined && (
        <div className="text-xs text-muted-foreground">
          Confidence: {(confidence * 100).toFixed(0)}%
        </div>
      )}
    </div>
  );
}
