import { HelpCircle } from 'lucide-react';
import { useState } from 'react';

interface HelpTooltipProps {
  content: string;
  title?: string;
  className?: string;
}

export function HelpTooltip({ content, title, className = '' }: HelpTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onClick={() => setIsVisible(!isVisible)}
        className="text-muted-foreground hover:text-primary transition-colors"
        aria-label="Help"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      {isVisible && (
        <div className="absolute z-50 w-64 p-3 mt-2 bg-popover text-popover-foreground border border-border rounded-lg shadow-lg left-1/2 -translate-x-1/2">
          {title && (
            <div className="font-semibold text-sm mb-1">{title}</div>
          )}
          <div className="text-xs leading-relaxed">{content}</div>
        </div>
      )}
    </div>
  );
}

// Predefined tooltips for common features
export const HelpTooltips = {
  signalType: (
    <HelpTooltip
      title="Signal Types"
      content="Strong Buy/Sell: High conviction signals. Buy/Sell: Moderate conviction. Hold: Wait for better entry or exit. Signals are probability-based, not guarantees."
    />
  ),

  marketRegime: (
    <HelpTooltip
      title="Market Regime"
      content="Describes current market conditions: Index-led (broad market move), Pre-market volatility (high fluctuation), Low liquidity (thin trading), Sector correlation (industry-wide trend)."
    />
  ),

  confidence: (
    <HelpTooltip
      title="Confidence Score"
      content="Based on data quality and source availability. High: Multiple reliable sources. Medium: Limited sources. Low: Fallback data or incomplete information."
    />
  ),

  mcpContext: (
    <HelpTooltip
      title="Market Context"
      content="MCP (Market Context Protocol) provides supporting news and data AFTER the signal is generated. It explains WHY the signal matters but doesn't create it."
    />
  ),



  dataQuality: (
    <HelpTooltip
      title="Data Quality"
      content="LIVE: Real-time data. DEMO: Delayed or sample data. STALE: Outdated data - refresh recommended. FALLBACK: Backup source in use due to primary unavailability."
    />
  ),

  intradayFreshness: (
    <HelpTooltip
      title="Signal Freshness"
      content="Intraday signals lose relevance quickly. Signals >15 minutes old may not reflect current market conditions. Consider refreshing for active trading."
    />
  )
};
