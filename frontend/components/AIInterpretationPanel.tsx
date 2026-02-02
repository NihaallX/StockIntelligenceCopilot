import { Brain, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { AIExplanation } from '@/lib/api';

interface AIInterpretationPanelProps {
  explanation: AIExplanation;
  className?: string;
}

export function AIInterpretationPanel({ explanation, className = '' }: AIInterpretationPanelProps) {
  const confidenceConfig = {
    high: {
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-50 dark:bg-green-900/10',
      border: 'border-green-200 dark:border-green-800',
      icon: CheckCircle
    },
    medium: {
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-900/10',
      border: 'border-amber-200 dark:border-amber-800',
      icon: Info
    },
    low: {
      color: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-50 dark:bg-red-900/10',
      border: 'border-red-200 dark:border-red-800',
      icon: AlertTriangle
    }
  };

  const config = confidenceConfig[explanation.confidence_label];
  const ConfidenceIcon = config.icon;

  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-purple-600" />
        <h3 className="text-xl font-semibold">Interpretation by AI</h3>
        {explanation.fallback && (
          <span className="text-xs text-muted-foreground ml-auto">
            (Basic explanation - LLM temporarily unavailable)
          </span>
        )}
      </div>

      {/* Main Explanation */}
      <div className={`p-4 rounded-lg ${config.bg} border ${config.border} mb-4`}>
        <div className="flex items-start gap-2">
          <ConfidenceIcon className={`w-5 h-5 ${config.color} flex-shrink-0 mt-0.5`} />
          <div>
            <p className="text-sm leading-relaxed">{explanation.explanation}</p>
            <div className="mt-2 text-xs text-muted-foreground flex items-center gap-1">
              <span>Confidence:</span>
              <span className={`font-semibold ${config.color}`}>
                {explanation.confidence_label.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* What Went Right */}
      {explanation.what_went_right.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-2">
            ✓ What Went Right
          </h4>
          <ul className="space-y-1">
            {explanation.what_went_right.map((point, index) => (
              <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-green-600">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* What Could Go Wrong */}
      {explanation.what_could_go_wrong.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-amber-600 dark:text-amber-400 mb-2">
            ⚠ What Could Go Wrong
          </h4>
          <ul className="space-y-1">
            {explanation.what_could_go_wrong.map((point, index) => (
              <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-amber-600">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}


    </div>
  );
}

interface AIInterpretationErrorProps {
  error?: string;
  className?: string;
}

export function AIInterpretationError({ error, className = '' }: AIInterpretationErrorProps) {
  return (
    <div className={`bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <Info className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
            AI Explanation Temporarily Unavailable
          </p>
          <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
            {error || "The AI explanation service is currently unavailable. The deterministic analysis above is still valid and complete."}
          </p>
        </div>
      </div>
    </div>
  );
}
