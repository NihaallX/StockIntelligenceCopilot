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
  HelpCircle,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

// Helper to simplify setup types
function simplifySetupType(setupType: string): string {
  const map: Record<string, string> = {
    vwap_bounce: "Bouncing at Fair Price",
    vwap_rejection: "Rejected at Fair Price",
    breakout: "Breaking Above",
    breakdown: "Breaking Down",
    consolidation: "Holding Steady",
  };
  return map[setupType] || setupType;
}

// Helper to get beginner-friendly explanation
function getBeginnerExplanation(opportunity: Opportunity): string {
  const { setup_type, ticker, mcp_context } = opportunity;
  
  if (setup_type === "vwap_bounce") {
    return `${ticker} dropped to its fair price and buyers stepped in. This could be a good entry point if you believe in the stock.`;
  }
  if (setup_type === "vwap_rejection") {
    return `${ticker} tried to go higher but sellers pushed it back down at fair price. Be careful - sellers are in control.`;
  }
  if (setup_type === "breakout") {
    return `${ticker} is breaking above its fair price with ${mcp_context.volume_ratio.toFixed(1)}x volume. Buyers are showing strength.`;
  }
  if (setup_type === "breakdown") {
    return `${ticker} is falling below its fair price with high volume. Sellers are dominating - consider avoiding or exiting.`;
  }
  return `${ticker} is moving sideways near fair price. Wait for a clearer direction before acting.`;
}

// VWAP explainer component
function OpportunitiesExplainer() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mb-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
      >
        <HelpCircle className="h-4 w-4" />
        What are these opportunities?
      </button>
      
      {isOpen && (
        <Card className="mt-2 border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Similar Stocks You Don't Own Yet</h3>
            <div className="text-sm text-blue-900 space-y-2">
              <p>
                Based on your portfolio, we found stocks that are <strong>similar</strong> to what you own 
                (same sector, similar size, similar performance) but you don't own them yet.
              </p>
              
              <p className="pt-2">
                <strong>These are opportunities to consider</strong> if you want to diversify within familiar territory.
              </p>
              
              <div className="space-y-1 ml-4 mt-2">
                <p>• <strong>High confidence (80%+)</strong> → Strong, clear pattern</p>
                <p>• <strong>Medium confidence (65-80%)</strong> → Good pattern, some risk</p>
                <p>• <strong>"Immediate"</strong> → Act soon (hours)</p>
                <p>• <strong>"Today"</strong> → Consider within trading day</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function OpportunitiesPage() {
  const { tokens } = useAuth();
  const router = useRouter();
  const [feed, setFeed] = useState<OpportunitiesFeed | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ignoredTickers, setIgnoredTickers] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!tokens?.access_token) {
      router.push("/login");
      return;
    }

    fetchFeed();

    // Auto-refresh every 5 minutes
    if (autoRefreshEnabled) {
      const interval = setInterval(() => {
        fetchFeed(true); // true = silent refresh
      }, 5 * 60 * 1000); // 5 minutes

      return () => clearInterval(interval);
    }
  }, [tokens, autoRefreshEnabled]);

  const fetchFeed = async (silent = false) => {
    if (!tokens?.access_token) return;

    try {
      if (silent) {
        setRefreshing(true);
      } else {
        setIsLoading(true);
      }
      const data = await getOpportunitiesFeed(tokens.access_token);
      setFeed(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch opportunities");
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    fetchFeed(true);
  };

  const formatLastUpdated = (date: Date | null) => {
    if (!date) return "Never";
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return "Just now";
    if (diffMins === 1) return "1 minute ago";
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return "1 hour ago";
    return `${diffHours} hours ago`;
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
          <Button
            onClick={() => fetchFeed()}
            disabled={isLoading}
            className="w-full"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? 'Retrying...' : 'Try Again'}
          </Button>
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
            <h1 className="text-3xl font-bold">New Stock Ideas</h1>
            <p className="text-muted-foreground">
              {visibleOpportunities.length} stocks similar to your portfolio • {feed.total_scanned} checked
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs text-muted-foreground">
              Last updated: {formatLastUpdated(lastUpdated)}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleManualRefresh}
              disabled={refreshing || isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button
              variant={autoRefreshEnabled ? "default" : "outline"}
              size="sm"
              onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
              title={autoRefreshEnabled ? "Auto-refresh ON (every 5 min)" : "Auto-refresh OFF"}
            >
              {autoRefreshEnabled ? '🔄 Auto' : '⏸️ Manual'}
            </Button>
          </div>
        </div>

        <OpportunitiesExplainer />

        {refreshing && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2 text-blue-700">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span className="text-sm">Updating opportunities...</span>
          </div>
        )}

        {/* Empty State */}
        {visibleOpportunities.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card border border-border rounded-xl p-12 text-center"
          >
            <Inbox className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Clear Opportunities Right Now</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              We couldn't find any strong patterns in similar stocks. Sometimes waiting is the best strategy.
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
                    <p className="text-sm text-muted-foreground">
                      {simplifySetupType(opportunity.setup_type)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleIgnore(opportunity.ticker)}
                  className="text-muted-foreground hover:text-foreground transition"
                  title="Hide this stock"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Beginner-friendly explanation */}
              <div className="bg-blue-50 border-l-2 border-blue-400 p-3 mb-4 rounded">
                <p className="text-sm text-blue-900">
                  {getBeginnerExplanation(opportunity)}
                </p>
              </div>

              {/* Original technical summary (collapsible or secondary) */}
              <details className="mb-4">
                <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                  Technical details
                </summary>
                <p className="text-sm mt-2 text-muted-foreground">{opportunity.summary}</p>
              </details>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className={`px-3 py-2 rounded-lg border ${getConfidenceColor(opportunity.confidence)}`}>
                  <div className="text-xs opacity-75">How Sure Are We?</div>
                  <div className="text-lg font-bold">{opportunity.confidence}%</div>
                </div>
                <div className={`px-3 py-2 rounded-lg border ${getTimeSensitivityColor(opportunity.time_sensitivity)}`}>
                  <div className="text-xs opacity-75 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    When to Act
                  </div>
                  <div className="text-sm font-semibold capitalize">
                    {opportunity.time_sensitivity.replace("_", " ")}
                  </div>
                </div>
              </div>

              {/* MCP Context - Simplified */}
              <div className="space-y-2 mb-4 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Price vs Fair Value</span>
                  <span className="font-medium">{opportunity.mcp_context.price_vs_vwap}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Trading Activity</span>
                  <span className="font-medium">{opportunity.mcp_context.volume_ratio.toFixed(1)}x normal</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Matches Market?</span>
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
