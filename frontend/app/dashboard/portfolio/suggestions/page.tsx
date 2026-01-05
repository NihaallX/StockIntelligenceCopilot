"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { getPortfolioPositions, getPortfolioAISuggestions, PortfolioPosition, PortfolioNudge, PortfolioAISuggestionsResponse } from "@/lib/api";
import { motion } from "framer-motion";
import { Sparkles, AlertCircle, TrendingUp, Loader2, Info, Shield } from "lucide-react";

export default function PortfolioSuggestionsPage() {
  const { tokens } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [analysis, setAnalysis] = useState<PortfolioAISuggestionsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPositions();
  }, [tokens]);

  const loadPositions = async () => {
    if (!tokens?.access_token) return;
    
    try {
      const data = await getPortfolioPositions(tokens.access_token);
      setPositions(data);
    } catch (error: any) {
      console.error("Failed to load positions:", error);
    }
  };

  const generateSuggestions = async () => {
    if (!tokens?.access_token || positions.length === 0) return;

    setIsLoading(true);
    setError("");

    try {
      const result = await getPortfolioAISuggestions(tokens.access_token, positions);
      setAnalysis(result);
    } catch (error: any) {
      setError(error.message || "Failed to generate suggestions");
    } finally {
      setIsLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    if (health === "HEALTHY") return "text-green-500";
    if (health === "NEEDS_ATTENTION") return "text-yellow-500";
    return "text-red-500";
  };

  const getPriorityColor = (priority: string) => {
    if (priority === "HIGH") return "border-l-red-500 bg-red-500/5";
    if (priority === "MEDIUM") return "border-l-yellow-500 bg-yellow-500/5";
    return "border-l-blue-500 bg-blue-500/5";
  };

  const getPriorityBadge = (priority: string) => {
    if (priority === "HIGH") return "bg-red-500/10 text-red-500";
    if (priority === "MEDIUM") return "bg-yellow-500/10 text-yellow-500";
    return "bg-blue-500/10 text-blue-500";
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-primary" />
              Portfolio AI Suggestions
            </h1>
            <p className="text-muted-foreground mt-2">
              Non-directive opportunity nudges to help you understand trade-offs
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-muted/50 border border-border rounded-xl p-4 mb-6 flex items-start gap-3">
          <Shield className="w-5 h-5 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div className="text-sm text-muted-foreground">
            <strong>Important:</strong> These are conditional suggestions, not commands. We do NOT tell you to buy or sell. 
            We help you understand risk/reward trade-offs so you can make informed decisions. Doing nothing is often the wisest choice.
          </div>
        </div>

        {positions.length === 0 ? (
          <div className="bg-card border border-border rounded-xl p-12 text-center">
            <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Positions Yet</h3>
            <p className="text-muted-foreground">
              Add stocks to your portfolio first to get AI-powered suggestions.
            </p>
          </div>
        ) : !analysis ? (
          <div className="bg-card border border-border rounded-xl p-12 text-center">
            <Sparkles className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Ready to Analyze</h3>
            <p className="text-muted-foreground mb-6">
              You have {positions.length} position{positions.length !== 1 ? 's' : ''} in your portfolio.
              Click below to get AI-powered opportunity nudges.
            </p>
            <button
              onClick={generateSuggestions}
              disabled={isLoading}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
            >
              {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
              {isLoading ? "Analyzing Portfolio..." : "Generate Suggestions"}
            </button>
            {error && (
              <p className="text-destructive mt-4">{error}</p>
            )}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Portfolio Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="text-sm text-muted-foreground mb-1">Portfolio Score</div>
                <div className="text-2xl font-bold">{analysis.portfolio_score}/100</div>
                <div className={`text-sm mt-1 ${getHealthColor(analysis.portfolio_health)}`}>
                  {analysis.portfolio_health.replace('_', ' ')}
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="text-sm text-muted-foreground mb-1">Total P&L</div>
                <div className={`text-2xl font-bold ${analysis.total_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {analysis.total_pnl >= 0 ? '+' : ''}₹{analysis.total_pnl.toLocaleString('en-IN')}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {analysis.total_pnl_percent >= 0 ? '+' : ''}{analysis.total_pnl_percent.toFixed(2)}%
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="text-sm text-muted-foreground mb-1">Diversification</div>
                <div className="text-2xl font-bold">{analysis.diversification_score}/100</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {analysis.diversification_score >= 70 ? 'Well diversified' : 'Room to diversify'}
                </div>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="text-sm text-muted-foreground mb-1">Risk Assessment</div>
                <div className="text-sm font-medium mt-2">
                  {analysis.risk_assessment}
                </div>
              </div>
            </div>

            {/* AI Suggestions */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  Opportunity Nudges
                </h2>
                <button
                  onClick={generateSuggestions}
                  disabled={isLoading}
                  className="px-4 py-2 bg-muted hover:bg-accent text-foreground rounded-lg transition-colors text-sm flex items-center gap-2"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
                  Refresh
                </button>
              </div>

              <div className="space-y-4">
                {analysis.suggestions.map((nudge: PortfolioNudge, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`border-l-4 rounded-lg p-4 ${getPriorityColor(nudge.priority)}`}
                  >
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <p className="text-foreground font-medium flex-1">{nudge.nudge}</p>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getPriorityBadge(nudge.priority)}`}>
                        {nudge.priority}
                      </span>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-3 mb-3">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-muted-foreground">{nudge.context}</p>
                      </div>
                    </div>
                    {nudge.applies_to.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs text-muted-foreground">Applies to:</span>
                        {nudge.applies_to.map((ticker) => (
                          <span key={ticker} className="px-2 py-0.5 bg-muted text-xs font-mono rounded">
                            {ticker}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-border">
                <p className="text-xs text-muted-foreground text-center">
                  Analysis completed in {analysis.processing_time_ms}ms • These are conditional suggestions, not financial advice
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
