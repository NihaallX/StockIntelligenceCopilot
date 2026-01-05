"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  ChevronRight,
  Clock,
  Activity
} from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getNotableSignals, NotableSignal, MarketContext } from "@/lib/api";
import { ContextVerifiedBadge } from "@/components/ContextVerifiedBadge";

/**
 * Today's Situations Component
 * 
 * Displays 3-5 notable signals from user's portfolio with calm, non-urgent tone.
 * Clicking a signal opens full analysis with MCP context.
 * 
 * Design Principles:
 * - Calm language (no urgency, no commands)
 * - Informative (why it matters, what changed)
 * - Actionable (click to see full analysis)
 * - Limited display (3-5 max, prevents overwhelm)
 */

interface TodaysSituationsProps {
  userId?: string;
  maxSignals?: number;
}

export default function TodaysSituations({ 
  userId, 
  maxSignals = 5 
}: TodaysSituationsProps) {
  const { tokens } = useAuth();
  const [signals, setSignals] = useState<NotableSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!tokens?.access_token) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError("");

    getNotableSignals(tokens.access_token, maxSignals)
      .then((response) => {
        setSignals(response.signals);
      })
      .catch((err: any) => {
        console.error("Failed to fetch notable signals:", err);
        setError(err.getUserMessage?.() || "Unable to load signals");
        
        // Fallback to mock data in development
        if (process.env.NODE_ENV === 'development') {
          const mockSignals: NotableSignal[] = [
            {
              ticker: "RELIANCE.NS",
              company_name: "Reliance Industries",
              signal_type: "BUY",
              signal_strength: "STRONG",
              confidence: 0.82,
              headline: "Technical setup suggests potential upside",
              summary: "RSI indicates oversold conditions while price holds above key support. Volume patterns show accumulation.",
              key_reasons: [
                "RSI oversold (29.4) with positive divergence",
                "Price above 50-day moving average",
                "Volume 23% above average"
              ],
              timestamp: new Date().toISOString(),
              is_new: true
            },
            {
              ticker: "TCS.NS",
              company_name: "Tata Consultancy Services",
              signal_type: "NEUTRAL",
              signal_strength: "WEAK",
              confidence: 0.45,
              headline: "Range-bound activity continues",
              summary: "Price consolidating between support and resistance. No clear directional bias at current levels.",
              key_reasons: [
                "Trading within 2% of 20-day range",
                "Volume below average (quiet period)",
                "Momentum indicators neutral"
              ],
              timestamp: new Date().toISOString(),
              is_new: false
            },
            {
              ticker: "HDFCBANK.NS",
              company_name: "HDFC Bank",
              signal_type: "SELL",
              signal_strength: "MODERATE",
              confidence: 0.68,
              headline: "Weakness signal detected",
              summary: "Price testing support with declining momentum. Recent breakdown below moving average suggests caution.",
              key_reasons: [
                "Broke below 50-day moving average",
                "RSI trending lower (42.1)",
                "Volume spike on down days"
              ],
              timestamp: new Date().toISOString(),
              is_new: true
            }
          ];
          setSignals(mockSignals.slice(0, maxSignals));
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [tokens, userId, maxSignals]);

  const getSignalIcon = (type: string) => {
    switch (type) {
      case "BUY": return <TrendingUp className="w-5 h-5" />;
      case "SELL": return <TrendingDown className="w-5 h-5" />;
      default: return <Minus className="w-5 h-5" />;
    }
  };

  const getSignalColor = (type: string) => {
    switch (type) {
      case "BUY": return {
        bg: "bg-green-50 dark:bg-green-900/10",
        border: "border-green-200 dark:border-green-800",
        icon: "text-green-600 dark:text-green-400",
        text: "text-green-700 dark:text-green-300",
        badge: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
      };
      case "SELL": return {
        bg: "bg-red-50 dark:bg-red-900/10",
        border: "border-red-200 dark:border-red-800",
        icon: "text-red-600 dark:text-red-400",
        text: "text-red-700 dark:text-red-300",
        badge: "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
      };
      default: return {
        bg: "bg-gray-50 dark:bg-gray-900/10",
        border: "border-gray-200 dark:border-gray-800",
        icon: "text-gray-600 dark:text-gray-400",
        text: "text-gray-700 dark:text-gray-300",
        badge: "bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300"
      };
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Today's Situations</h2>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Today's Situations</h2>
        </div>
        <p className="text-sm text-muted-foreground">{error}</p>
      </div>
    );
  }

  if (signals.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Today's Situations</h2>
        </div>
        <p className="text-sm text-muted-foreground">
          No notable signals at the moment. Market conditions appear stable across your holdings.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-border rounded-xl p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Today's Situations</h2>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>Updated just now</span>
        </div>
      </div>

      {/* Signal Cards */}
      <div className="space-y-3">
        <AnimatePresence>
          {signals.map((signal, index) => {
            const colors = getSignalColor(signal.signal_type);
            const SignalIcon = getSignalIcon(signal.signal_type);

            return (
              <motion.div
                key={signal.ticker}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
              >
                <Link
                  href={`/dashboard/analysis?ticker=${signal.ticker}`}
                  className={`
                    block p-4 rounded-lg border transition-all
                    ${colors.bg} ${colors.border}
                    hover:shadow-md hover:scale-[1.02]
                  `}
                >
                  {/* Header Row */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${colors.badge}`}>
                        <div className={colors.icon}>
                          {SignalIcon}
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-foreground">
                            {signal.ticker.replace('.NS', '').replace('.BO', '')}
                          </h3>
                          {signal.is_new && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                              New
                            </span>
                          )}
                        </div>
                        {signal.company_name && (
                          <p className="text-xs text-muted-foreground">
                            {signal.company_name}
                          </p>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  </div>

                  {/* Headline */}
                  <h4 className="text-sm font-medium text-foreground mb-2">
                    {signal.headline}
                  </h4>

                  {/* Summary */}
                  <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
                    {signal.summary}
                  </p>

                  {/* Key Reasons */}
                  <div className="space-y-1">
                    {signal.key_reasons.slice(0, 2).map((reason, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-xs text-muted-foreground mt-0.5">•</span>
                        <span className="text-xs text-muted-foreground flex-1">
                          {reason}
                        </span>
                      </div>
                    ))}
                    {signal.key_reasons.length > 2 && (
                      <p className="text-xs text-muted-foreground ml-4">
                        +{signal.key_reasons.length - 2} more reason{signal.key_reasons.length - 2 !== 1 ? 's' : ''}
                      </p>
                    )}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/50">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium ${colors.text}`}>
                        {signal.signal_type}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        •
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {Math.round(signal.confidence * 100)}% confidence
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatTimestamp(signal.timestamp)}
                    </span>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Footer Note */}
      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground text-center">
          These signals are based on technical and fundamental analysis. 
          Click any card for detailed analysis and supporting context.
        </p>
      </div>
    </motion.div>
  );
}
