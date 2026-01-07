import { TrendingUp, TrendingDown, Minus, Shield } from 'lucide-react';

interface SignalTypeBadgeProps {
  recommendation: string;
  className?: string;
}

export function SignalTypeBadge({ recommendation, className = '' }: SignalTypeBadgeProps) {
  // Parse recommendation to extract signal type
  const recLower = recommendation.toLowerCase();
  
  let signalType: string;
  let color: string;
  let icon: typeof TrendingUp;
  
  if (recLower.includes('strong buy') || recLower.includes('strongly buy')) {
    signalType = 'Strong Buy';
    color = 'bg-green-600 text-white';
    icon = TrendingUp;
  } else if (recLower.includes('buy') && !recLower.includes('avoid')) {
    signalType = 'Buy';
    color = 'bg-green-500 text-white';
    icon = TrendingUp;
  } else if (recLower.includes('strong sell') || recLower.includes('strongly sell')) {
    signalType = 'Strong Sell';
    color = 'bg-red-600 text-white';
    icon = TrendingDown;
  } else if (recLower.includes('sell') || recLower.includes('avoid')) {
    signalType = 'Sell';
    color = 'bg-red-500 text-white';
    icon = TrendingDown;
  } else if (recLower.includes('hold') || recLower.includes('wait') || recLower.includes('insufficient')) {
    signalType = 'Hold';
    color = 'bg-amber-500 text-white';
    icon = Shield;
  } else {
    signalType = 'Neutral';
    color = 'bg-gray-500 text-white';
    icon = Minus;
  }
  
  const Icon = icon;
  
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${color} ${className}`}>
      <Icon className="w-4 h-4" />
      <span className="text-sm font-semibold">{signalType}</span>
    </div>
  );
}
