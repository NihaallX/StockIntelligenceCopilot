"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getEnhancedAnalysis, getPortfolioPositions, EnhancedAnalysis, PortfolioPosition } from "@/lib/api";
import { motion } from "framer-motion";
import { Search, TrendingUp, TrendingDown, AlertCircle, Shield, AlertTriangle, Clock, Briefcase, ExternalLink, Info, Scale } from "lucide-react";
import { searchStocks, type StockSuggestion } from "@/lib/indian-stocks";
import { CitationsPanel } from "@/components/CitationsPanel";
import { ContextVerifiedBadge } from "@/components/ContextVerifiedBadge";
import Link from "next/link";

// Parse recommendation into structured parts
function parseRecommendation(rec: string) {
  const match = rec.match(/^(HOLD|AVOID|BUY|SELL|NO ACTION|WEAK BUY|STRONG BUY|STRONG SELL)(?:\s*-\s*(.+))?$/i);
  if (match) {
    return {
      action: match[1].toUpperCase(),
      reasoning: match[2] || ""
    };
  }
  return { action: rec, reasoning: "" };
}

function isInactionRecommendation(action: string) {
  return ['HOLD', 'AVOID', 'NO ACTION', 'MONITOR'].some(word => 
    action.toUpperCase().includes(word)
  );
}

// Validate data integrity and detect conflicts
function validateAnalysisIntegrity(analysis: EnhancedAnalysis): string | null {
  const score = parseInt(analysis.combined_score);
  const rec = parseRecommendation(analysis.recommendation);
  
  // Check for impossible score/recommendation combinations
  if (score > 70 && rec.action.includes('AVOID')) {
    return 'Data integrity issue: High score conflicts with AVOID recommendation. Analysis suspended.';
  }
  if (score < 30 && rec.action.includes('BUY')) {
    return 'Data integrity issue: Low score conflicts with BUY signal. Analysis suspended.';
  }
  
  // Check for technical vs fundamental conflicts
  if (analysis.fundamental_score) {
    const fundAssessment = analysis.fundamental_score.overall_assessment;
    const isBullishRec = rec.action.includes('BUY');
    const isBearishRec = rec.action.includes('SELL') || rec.action.includes('AVOID');
    
    if (fundAssessment === 'POOR' && isBullishRec && !rec.reasoning.toLowerCase().includes('fundamental')) {
      return null; // Conflict acknowledged in reasoning
    }
    if (fundAssessment === 'STRONG' && isBearishRec && !rec.reasoning.toLowerCase().includes('fundamental')) {
      return null; // Conflict acknowledged in reasoning
    }
  }
  
  return null; // Data integrity OK
}

// Detect conflicting signals between technical and fundamental analysis
function detectConflictingSignals(analysis: EnhancedAnalysis): string | null {
  if (!analysis.fundamental_score) return null;
  
  const rec = parseRecommendation(analysis.recommendation);
  const fundAssessment = analysis.fundamental_score.overall_assessment;
  const fundScore = analysis.fundamental_score.overall_score;
  
  // Technical bullish + fundamentals bearish
  if (rec.action.includes('BUY') && fundAssessment === 'POOR') {
    return 'Technical indicators suggest buying, but fundamental analysis shows weakness. This creates uncertainty — consider your investment time horizon and risk tolerance.';
  }
  
  // Technical bearish + fundamentals bullish
  if ((rec.action.includes('HOLD') || rec.action.includes('AVOID')) && fundAssessment === 'STRONG' && fundScore > 70) {
    return 'Strong fundamental profile but technical signals advise caution. May be suitable for long-term investors willing to wait for better entry points.';
  }
  
  // Scenario analysis conflicts
  if (analysis.scenario_analysis) {
    const expectedReturn = parseFloat(analysis.scenario_analysis.expected_return_weighted);
    if (rec.action.includes('BUY') && expectedReturn < 0) {
      return 'Recommendation is positive but probability-weighted expected return is negative. This indicates high uncertainty in our models.';
    }
  }
  
  return null;
}

export default function AnalysisPage() {
  const { tokens } = useAuth();
  const [ticker, setTicker] = useState("");
  const [analysis, setAnalysis] = useState<EnhancedAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSlowLoading, setIsSlowLoading] = useState(false);
  const [error, setError] = useState("");
  const [dataIntegrityIssue, setDataIntegrityIssue] = useState("");
  const [rateLimitCountdown, setRateLimitCountdown] = useState(0);
  const [portfolioStocks, setPortfolioStocks] = useState<PortfolioPosition[]>([]);
  
  // Autocomplete state
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Load portfolio stocks
  useEffect(() => {
    if (tokens?.access_token) {
      getPortfolioPositions(tokens.access_token)
        .then(setPortfolioStocks)
        .catch(console.error);
    }
  }, [tokens]);

  // Countdown timer for rate limits
  useEffect(() => {
    if (rateLimitCountdown > 0) {
      const timer = setTimeout(() => {
        setRateLimitCountdown(rateLimitCountdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (rateLimitCountdown === 0 && error.includes('Rate limit')) {
      // Auto-clear error when countdown reaches 0
      setError("");
    }
  }, [rateLimitCountdown, error]);

  // Handle input change with autocomplete
  const handleInputChange = (value: string) => {
    const upperValue = value.toUpperCase();
    setTicker(upperValue);
    
    // Show suggestions if typing
    if (value.length >= 2) {
      const results = searchStocks(value);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
      setSelectedIndex(-1);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  // Handle suggestion selection
  const selectSuggestion = (suggestion: StockSuggestion) => {
    setTicker(suggestion.ticker);
    setShowSuggestions(false);
    setSuggestions([]);
    inputRef.current?.focus();
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => 
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => 
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      selectSuggestion(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokens?.access_token || !ticker) return;

    setError("");
    setDataIntegrityIssue("");
    setIsLoading(true);
    setIsSlowLoading(false);
    setAnalysis(null);
    
    // Set slow loading indicator after 3 seconds
    const slowLoadingTimer = setTimeout(() => {
      setIsSlowLoading(true);
    }, 3000);

    try {
      const result = await getEnhancedAnalysis(tokens.access_token, ticker.toUpperCase());
      
      // Validate data integrity
      const integrityIssue = validateAnalysisIntegrity(result);
      if (integrityIssue) {
        setDataIntegrityIssue(integrityIssue);
        setAnalysis(null); // Don't show compromised data
      } else {
        setAnalysis(result);
      }
    } catch (err: any) {
      // Use categorized error messages
      if (err.getUserMessage) {
        setError(err.getUserMessage());
      } else {
        setError(err.message || "Analysis failed");
      }
      
      // Start countdown for rate limit errors
      if (err.message && err.message.includes('Rate limit')) {
        setRateLimitCountdown(60);
      }
      
      // If auth error, redirect after showing message
      if (err.category === 'auth') {
        setTimeout(() => window.location.href = '/login', 2000);
      }
    } finally {
      clearTimeout(slowLoadingTimer);
      setIsLoading(false);
      setIsSlowLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Stock Analysis</h1>
        <p className="text-muted-foreground">
          Get comprehensive technical, fundamental, and scenario analysis
        </p>
      </div>

      {/* Portfolio Quick Access */}
      {portfolioStocks.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Briefcase className="w-4 h-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold">Your Portfolio</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {portfolioStocks.map((stock) => (
              <button
                key={stock.id}
                onClick={async (e) => {
                  e.preventDefault();
                  setTicker(stock.ticker);
                  // Wait for state to update, then trigger analysis
                  setTimeout(() => {
                    const form = document.querySelector('form');
                    if (form) {
                      form.requestSubmit();
                    }
                  }, 100);
                }}
                className="px-3 py-1.5 text-sm bg-muted hover:bg-accent rounded-lg transition-colors"
              >
                {stock.ticker}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search Form */}
      <div className="bg-card border border-border rounded-xl p-6">
        <form onSubmit={handleAnalyze} className="flex gap-4">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={ticker}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => {
                if (suggestions.length > 0) setShowSuggestions(true);
              }}
              className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-lg"
              placeholder="Type to search (e.g., Reliance, TCS) or enter ticker (RELIANCE.NS)"
              required
            />
            
            {/* Autocomplete Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute z-50 w-full mt-2 bg-card border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto"
              >
                {suggestions.map((suggestion, index) => (
                  <button
                    key={suggestion.ticker}
                    type="button"
                    onClick={() => selectSuggestion(suggestion)}
                    className={`w-full px-4 py-3 text-left hover:bg-accent transition-colors flex items-center justify-between ${
                      index === selectedIndex ? 'bg-accent' : ''
                    }`}
                  >
                    <div>
                      <div className="font-semibold">{suggestion.name}</div>
                      <div className="text-sm text-muted-foreground">{suggestion.ticker}</div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      suggestion.exchange === 'NSE' 
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' 
                        : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                    }`}>
                      {suggestion.exchange}
                    </span>
                  </button>
                ))}
              </div>
            )}
            
            <p className="mt-2 text-sm text-muted-foreground">
              💡 Works with ALL NSE/BSE stocks - search by name or type ticker directly (e.g., RELIANCE.NS)
            </p>
          </div>
          <button
            type="submit"
            disabled={isLoading || !ticker}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            <Search className="w-5 h-5" />
            {isLoading ? "Analyzing..." : "Analyze"}
          </button>
        </form>
        
        {isSlowLoading && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg text-sm">
            <p className="text-muted-foreground">
              ⏱️ Analysis is taking longer than usual. This can happen with complex data or high server load. 
              Please wait...
            </p>
          </div>
        )}
        
        {dataIntegrityIssue && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/10 border border-red-300 dark:border-red-700 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="font-semibold">Data Integrity Issue</span>
            </div>
            <p className="text-sm text-muted-foreground mb-2">{dataIntegrityIssue}</p>
            <p className="text-xs text-muted-foreground">
              We cannot display this analysis as the data appears inconsistent. 
              This is a protective measure to prevent misleading recommendations.
            </p>
          </div>
        )}
        
        {error && (
          <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-300 dark:border-amber-700 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-5 h-5 text-amber-600" />
              <span className="font-semibold">Analysis Unavailable</span>
              {rateLimitCountdown > 0 && (
                <div className="ml-auto flex items-center gap-2 text-amber-600">
                  <Clock className="w-4 h-4 animate-pulse" />
                  <span className="text-sm font-mono">{rateLimitCountdown}s</span>
                </div>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              {error.includes('risk') || error.includes('limit') || error.includes('exceed')
                ? `\u26a0 ${error}` 
                : `Unable to analyze ${ticker.toUpperCase()}: ${error}`}
            </p>
            {rateLimitCountdown > 0 && (
              <div className="mt-3 w-full bg-amber-200 dark:bg-amber-800 rounded-full h-1.5 overflow-hidden">
                <motion.div
                  className="h-full bg-amber-600"
                  initial={{ width: "100%" }}
                  animate={{ width: "0%" }}
                  transition={{ duration: 60, ease: "linear" }}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Combined Score & Recommendation */}
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-1">Analysis Summary</h2>
                <p className="text-muted-foreground">Probability-based assessment</p>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-muted-foreground mb-2">
                  {analysis.combined_score}/100
                </div>
                <div className="text-sm text-muted-foreground">Combined Rating</div>
                {analysis.fundamental_score ? (
                  <div className="text-xs text-green-600 mt-1">✓ Complete Data</div>
                ) : (
                  <div className="text-xs text-amber-600 mt-1">⚠ Partial Data</div>
                )}
              </div>
            </div>
            
            {(() => {
              const parsed = parseRecommendation(analysis.recommendation);
              const isInaction = isInactionRecommendation(parsed.action);
              
              return (
                <div className={`p-6 rounded-xl border-2 ${
                  isInaction 
                    ? "bg-amber-50 dark:bg-amber-900/10 border-amber-300 dark:border-amber-700"
                    : "bg-muted border-border"
                }`}>
                  <div className="flex items-center gap-3 mb-3">
                    {isInaction && <Shield className="w-6 h-6 text-amber-600" />}
                    <span className="text-2xl font-bold">{parsed.action}</span>
                  </div>
                  {parsed.reasoning && (
                    <p className="text-sm text-muted-foreground mb-4">{parsed.reasoning}</p>
                  )}
                  <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
                    <p>ℹ️ This is a probability-based assessment, not financial advice. All investments carry risk.</p>
                  </div>
                </div>
              );
            })()}
            
            {/* Conflicting Signals Warning */}
            {(() => {
              const conflictWarning = detectConflictingSignals(analysis);
              if (!conflictWarning) return null;
              
              return (
                <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-300 dark:border-amber-700 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-amber-600" />
                    <span className="font-semibold text-sm">Conflicting Signals Detected</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{conflictWarning}</p>
                  <p className="text-xs text-muted-foreground">
                    ⚠️ Increased uncertainty requires extra caution. Consider seeking additional research or professional advice.
                  </p>
                </div>
              );
            })()}
          </div>

          {/* Fundamental Score */}
          {!analysis.fundamental_score && (
            <div className="bg-amber-50 dark:bg-amber-900/10 border border-amber-300 dark:border-amber-700 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold">Limited Fundamental Data</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Fundamental analysis is unavailable for {ticker.toUpperCase()}. 
                This recommendation is based solely on technical indicators and may have reduced reliability.
              </p>
            </div>
          )}
          
          {analysis.fundamental_score && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4">Fundamental Analysis</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold mb-1">
                    {analysis.fundamental_score.overall_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Overall</div>
                  <div className="text-xs font-semibold mt-1">
                    {analysis.fundamental_score.overall_assessment}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold mb-1">
                    {analysis.fundamental_score.valuation_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Valuation</div>
                  <div className="text-xs">of 30</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold mb-1">
                    {analysis.fundamental_score.growth_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Growth</div>
                  <div className="text-xs">of 25</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold mb-1">
                    {analysis.fundamental_score.profitability_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Profitability</div>
                  <div className="text-xs">of 25</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold mb-1">
                    {analysis.fundamental_score.financial_health_score}
                  </div>
                  <div className="text-sm text-muted-foreground">Health</div>
                  <div className="text-xs">of 20</div>
                </div>
              </div>
            </div>
          )}

          {/* Scenario Analysis */}
          {analysis.scenario_analysis && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4">Scenario Analysis</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Probability-weighted outcomes. Even positive signals carry downside risk.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Worst Case - Show First */}
                <div className="p-4 border border-border rounded-lg bg-card">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingDown className="w-5 h-5 text-muted-foreground" />
                    <span className="font-semibold">Worst Case</span>
                  </div>
                  <div className="text-2xl font-bold mb-1">
                    {parseFloat(analysis.scenario_analysis.worst_case.expected_return_percent).toFixed(1)}%
                  </div>
                  <div className="text-base font-medium text-muted-foreground">
                    Probability: {parseFloat(analysis.scenario_analysis.worst_case.probability).toFixed(0)}%
                  </div>
                </div>

                {/* Base Case - Most Likely, Emphasized */}
                <div className="p-4 border-2 border-primary rounded-lg bg-primary/5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-5 h-5 flex items-center justify-center">
                      <div className="w-3 h-3 bg-primary rounded-full" />
                    </div>
                    <span className="font-semibold">Base Case</span>
                    <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded">Most Likely</span>
                  </div>
                  <div className="text-2xl font-bold mb-1">
                    {parseFloat(analysis.scenario_analysis.base_case.expected_return_percent) > 0 ? '+' : ''}
                    {parseFloat(analysis.scenario_analysis.base_case.expected_return_percent).toFixed(1)}%
                  </div>
                  <div className="text-base font-medium text-muted-foreground">
                    Probability: {parseFloat(analysis.scenario_analysis.base_case.probability).toFixed(0)}%
                  </div>
                </div>

                {/* Best Case - Show Last, De-emphasized */}
                <div className="p-4 border border-border rounded-lg bg-card">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-5 h-5 text-muted-foreground" />
                    <span className="font-semibold">Best Case</span>
                  </div>
                  <div className="text-2xl font-bold mb-1">
                    {parseFloat(analysis.scenario_analysis.best_case.expected_return_percent) > 0 ? '+' : ''}
                    {parseFloat(analysis.scenario_analysis.best_case.expected_return_percent).toFixed(1)}%
                  </div>
                  <div className="text-base font-medium text-muted-foreground">
                    Probability: {parseFloat(analysis.scenario_analysis.best_case.probability).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-border grid grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">
                    Expected Return (Weighted)
                  </div>
                  <div className="text-xl font-bold">
                    {parseFloat(analysis.scenario_analysis.expected_return_weighted) > 0 ? '+' : ''}
                    {parseFloat(analysis.scenario_analysis.expected_return_weighted).toFixed(2)}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">
                    Risk/Reward Ratio
                  </div>
                  <div className="text-xl font-bold">
                    {parseFloat(analysis.scenario_analysis.risk_reward_ratio).toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Market Context (Sources) - Only shown if MCP data available */}
          {analysis.market_context && analysis.market_context.supporting_points && analysis.market_context.supporting_points.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-muted-foreground" />
                  <h3 className="text-xl font-semibold">Why The System Thinks This Matters (Sources)</h3>
                </div>
                <ContextVerifiedBadge 
                  mcp_status={analysis.market_context.mcp_status}
                  sources_count={analysis.market_context.data_sources_used?.length || 0}
                />
              </div>
              
              <div className="mb-4 p-4 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong className="text-blue-700 dark:text-blue-300">📊 These sources SUPPORT the signal above.</strong> They did not generate it. 
                  The signal was produced by technical + fundamental analysis, then these news articles were retrieved to provide market context.
                </p>
              </div>

              {/* Citations Panel with confidence badges */}
              <CitationsPanel supportingPoints={analysis.market_context.supporting_points} />

              {/* Warning if MCP failed */}
              {analysis.market_context.mcp_status === 'failed' && (
                <div className="mt-4 p-4 bg-red-50/50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-900 dark:text-red-100">
                        Context data unavailable
                      </p>
                      <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                        The analysis above is based on technical and fundamental indicators only. 
                        Market context could not be retrieved at this time.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Warning if data is stale */}
              {analysis.market_context.mcp_status === 'partial' && (
                <div className="mt-4 p-4 bg-yellow-50/50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                        Partial context available
                      </p>
                      <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                        Some data sources were unavailable. The context shown may be incomplete.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
                <p>
                  📊 Context sources are verified from reputable financial news providers. 
                  This information enriches your analysis but should not be the sole basis for investment decisions.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Legal Disclaimer Banner - Always visible */}
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Scale className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
              Decision-Support Tool • Not Financial Advice
            </h4>
            <p className="text-xs text-blue-800 dark:text-blue-200 leading-relaxed">
              This analysis is for educational and informational purposes only. It is not personalized financial advice. 
              Past performance does not guarantee future results. Always consult a SEBI-registered investment advisor 
              before making investment decisions.{" "}
              <Link 
                href="/legal/disclaimer" 
                className="underline hover:text-blue-600 dark:hover:text-blue-400 font-medium"
              >
                Full Disclaimer
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
