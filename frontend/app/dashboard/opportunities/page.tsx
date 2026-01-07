"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { getOpportunitiesFeed, Opportunity, OpportunitiesFeed } from "@/lib/api";
import { motion } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  Clock,
  Target,
  ShieldAlert,
  Eye,
  X,
  AlertCircle,
  Inbox,
} from "lucide-react";

export default function OpportunitiesPage() {
  const { tokens } = useAuth();
  const router = useRouter();
  const [feed, setFeed] = useState<OpportunitiesFeed | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ignoredTickers, setIgnoredTickers] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!tokens?.access_token) {
      router.push("/login");
      return;
    }

    fetchFeed();
  }, [tokens]);

  const fetchFeed = async () => {
    if (!tokens?.access_token) return;

    try {
      setIsLoading(true);
      const data = await getOpportunitiesFeed(tokens.access_token);
      setFeed(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch opportunities");
    } finally {
      setIsLoading(false);
    }
  };

  const handleIgnore = (ticker: string) => {
    setIgnoredTickers((prev) => new Set(prev).add(ticker));
  };

  const handleAnalyze = (ticker: string) => {
    router.push(`/dashboard/analysis?ticker=${ticker}`);
  };

  const getSetupIcon = (setupType: string) => {
    const icons = {
      vwap_bounce: TrendingUp,
      vwap_rejection: TrendingDown,
      breakout: Zap,
      breakdown: TrendingDown,
      consolidation: Activity,
    };
    const Icon = icons[setupType as keyof typeof icons] || Activity;
    return <Icon className="w-5 h-5" />;
  };

  const getSetupColor = (setupType: string) => {
    const colors = {
      vwap_bounce: "text-green-600 dark:text-green-400",
      vwap_rejection: "text-red-600 dark:text-red-400",
      breakout: "text-blue-600 dark:text-blue-400",
      breakdown: "text-red-600 dark:text-red-400",
      consolidation: "text-amber-600 dark:text-amber-400",
    };
    return colors[setupType as keyof typeof colors] || "text-muted-foreground";
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
    if (confidence >= 65) return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
    return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300";
  };

  const getTimeSensitivityColor = (sensitivity: string) => {
    const colors = {
      immediate: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 animate-pulse",
      today: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
      this_week: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    };
    return colors[sensitivity as keyof typeof colors] || colors.today;
  };

  const visibleOpportunities = feed?.opportunities.filter(
    (opp) => !ignoredTickers.has(opp.ticker)
  ) || [];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Scanning opportunities...</p>
        </div>
      </div>
    );
  }

  if (error || !feed) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl p-6 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-center text-red-900 dark:text-red-100 mb-4">
            {error || "Unable to fetch opportunities"}
          </p>
          <button
            onClick={fetchFeed}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto space-y-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Opportunities Feed</h1>
            <p className="text-muted-foreground">
              {visibleOpportunities.length} actionable setups • {feed.total_scanned} tickers scanned
            </p>
          </div>
          <button
            onClick={() => router.push("/dashboard/pulse")}
            className="px-4 py-2 text-sm bg-muted hover:bg-muted/80 rounded-lg transition"
          >
            Back to Pulse
          </button>
        </div>

        {/* Empty State */}
        {visibleOpportunities.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card border border-border rounded-xl p-12 text-center"
          >
            <Inbox className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Clear Opportunities</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              No high-confidence setups match current market conditions. Standing down is a valid strategy.
            </p>
            <button
              onClick={() => router.push("/dashboard/pulse")}
              className="mt-6 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
            >
              Return to Market Pulse
            </button>
          </motion.div>
        )}

        {/* Opportunities Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {visibleOpportunities.map((opportunity, index) => (
            <motion.div
              key={`${opportunity.ticker}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={getSetupColor(opportunity.setup_type)}>
                    {getSetupIcon(opportunity.setup_type)}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">{opportunity.ticker}</h3>
                    <p className="text-sm text-muted-foreground capitalize">
                      {opportunity.setup_type.replace("_", " ")}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleIgnore(opportunity.ticker)}
                  className="text-muted-foreground hover:text-foreground transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Summary */}
              <p className="text-sm mb-4 leading-relaxed">{opportunity.summary}</p>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className={`px-3 py-2 rounded-lg border ${getConfidenceColor(opportunity.confidence)}`}>
                  <div className="text-xs opacity-75">Confidence</div>
                  <div className="text-lg font-bold">{opportunity.confidence}%</div>
                </div>
                <div className={`px-3 py-2 rounded-lg border ${getTimeSensitivityColor(opportunity.time_sensitivity)}`}>
                  <div className="text-xs opacity-75 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Timing
                  </div>
                  <div className="text-sm font-semibold capitalize">
                    {opportunity.time_sensitivity.replace("_", " ")}
                  </div>
                </div>
              </div>

              {/* MCP Context */}
              <div className="space-y-2 mb-4 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Price vs VWAP</span>
                  <span className="font-medium">{opportunity.mcp_context.price_vs_vwap}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Volume</span>
                  <span className="font-medium">{opportunity.mcp_context.volume_ratio.toFixed(1)}x avg</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Index Alignment</span>
                  <span className="font-medium">{opportunity.mcp_context.index_alignment}</span>
                </div>
              </div>

              {/* Targets */}
              {(opportunity.target_price || opportunity.stop_loss) && (
                <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                  {opportunity.target_price && (
                    <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                      <Target className="w-4 h-4" />
                      <span>Target: ₹{opportunity.target_price.toFixed(2)}</span>
                    </div>
                  )}
                  {opportunity.stop_loss && (
                    <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                      <ShieldAlert className="w-4 h-4" />
                      <span>Stop: ₹{opportunity.stop_loss.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleAnalyze(opportunity.ticker)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
                >
                  <Eye className="w-4 h-4" />
                  Analyze
                </button>
                <button
                  onClick={() => handleIgnore(opportunity.ticker)}
                  className="px-4 py-3 bg-muted text-muted-foreground rounded-lg hover:bg-muted/80 transition"
                >
                  Ignore
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer Stats */}
        <div className="bg-muted/50 border border-border rounded-lg p-4 flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-muted-foreground">Market Regime: </span>
              <span className="font-medium capitalize">{feed.market_regime}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Filtered by confidence: </span>
              <span className="font-medium">{feed.filtered_by_confidence}</span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            Updated: {new Date(feed.timestamp).toLocaleTimeString("en-IN")}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
