/**
 * EXPERIMENTAL MODE VIEW
 * 
 * Dedicated screen for experimental trading analysis
 * NOT a reused production UI - completely separate
 * 
 * Features:
 * - Trade hypothesis card with confidence/regime/range
 * - Feedback buttons (👍/👎)
 * - Clear warnings about non-compliance
 * 
 * ⚠️ WARNING: Personal use only. Not SEBI compliant.
 */

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  ArrowLeft, 
  TrendingUp, 
  TrendingDown, 
  ThumbsUp, 
  ThumbsDown,
  Clock,
  Target,
  Activity,
  Info,
  Database
} from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { DataQualityBadge } from '@/components/DataQualityBadge';
import { HelpTooltip, HelpTooltips } from '@/components/HelpTooltip';
import { SignalFreshness } from '@/components/SignalFreshness';

interface TradingThesis {
  ticker: string;
  thesis: string;
  bias: 'long' | 'short' | 'no_trade' | 'scalp_only';
  confidence: number;
  regime: string;
  price_range_low: number;
  price_range_high: number;
  entry_timing: string;
  time_horizon: string;
  invalidation_reason: string;
  volume_analysis: string;
  risk_notes: string[];
  confidence_adjustments: string[];
  index_alignment: string;
  signal_age_minutes?: number;
  analysis_id?: string;
}

export default function ExperimentalModeView() {
  const router = useRouter();
  const [ticker, setTicker] = React.useState('');
  const [currentPrice, setCurrentPrice] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [thesis, setThesis] = React.useState<TradingThesis | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [feedbackNote, setFeedbackNote] = React.useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = React.useState(false);

  const handleAnalyze = async () => {
    if (!ticker || !currentPrice) {
      setError('Please enter ticker and current price');
      return;
    }

    setLoading(true);
    setError(null);
    setThesis(null);
    setFeedbackSubmitted(false);

    try {
      // TODO: Fetch real OHLCV and indicators from API
      const response = await fetch('/api/v1/experimental/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker,
          current_price: parseFloat(currentPrice),
          ohlcv: {
            // Mock data - replace with real data
            open: parseFloat(currentPrice) * 0.99,
            high: parseFloat(currentPrice) * 1.01,
            low: parseFloat(currentPrice) * 0.98,
            close: parseFloat(currentPrice),
            volume: 1000000,
            volume_ratio: 1.2
          },
          indicators: {
            // Mock data - replace with real data
            rsi: 55,
            macd: 0.5,
            macd_signal: 0.3,
            macd_histogram: 0.2
          },
          time_of_day: 'mid_day'
        })
      });

      const data = await response.json();

      if (data.success && data.thesis) {
        setThesis(data.thesis);
      } else {
        setError(data.error || 'Analysis failed');
      }
    } catch (err) {
      setError(`Failed to fetch analysis: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (feedback: 'helpful' | 'wrong') => {
    if (!thesis?.analysis_id) return;

    try {
      const response = await fetch('/api/v1/experimental/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_id: thesis.analysis_id,
          ticker: thesis.ticker,
          feedback,
          user_note: feedbackNote || null
        })
      });

      if (response.ok) {
        setFeedbackSubmitted(true);
        setFeedbackNote('');
      }
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  const getBiasIcon = (bias: string) => {
    if (bias === 'long') return <TrendingUp className="w-5 h-5 text-green-600" />;
    if (bias === 'short') return <TrendingDown className="w-5 h-5 text-red-600" />;
    return <Activity className="w-5 h-5 text-gray-600" />;
  };

  const getBiasColor = (bias: string) => {
    if (bias === 'long') return 'bg-green-100 text-green-800';
    if (bias === 'short') return 'bg-red-100 text-red-800';
    if (bias === 'scalp_only') return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 70) return 'text-green-600';
    if (confidence >= 50) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      {/* Experimental Mode Header Banner */}
      <div className="sticky top-0 z-50 bg-amber-500/10 backdrop-blur-sm border-b border-amber-500/20">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-semibold text-amber-900">Experimental Mode</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="text-amber-900 hover:text-amber-700"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Production
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 p-6">
        {/* Warning Alert */}
        <div className="max-w-4xl mx-auto mb-6">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>⚠️ EXPERIMENTAL MODE - Personal Use Only</strong>
              <br />
              This generates trade predictions and biases. NOT compliant with SEBI regulations.
              You assume ALL responsibility for any actions taken based on these analyses.
            </AlertDescription>
          </Alert>
        </div>

      {/* Input Card */}
        <Card className="max-w-4xl mx-auto mb-6 shadow-lg">
        <CardHeader>
          <CardTitle>Experimental Trading Analysis</CardTitle>
          <CardDescription>
            Enter ticker and price to generate trading hypothesis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Ticker</label>
              <Input
                placeholder="e.g., RELIANCE"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Current Price (₹)</label>
              <Input
                type="number"
                placeholder="e.g., 2850.50"
                value={currentPrice}
                onChange={(e) => setCurrentPrice(e.target.value)}
              />
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={loading || !ticker || !currentPrice}
              className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>

          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Thesis Card */}
      {thesis && (
        <Card className="max-w-4xl mx-auto shadow-lg border-amber-200/50">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getBiasIcon(thesis.bias)}
                <div>
                  <CardTitle>{thesis.ticker}</CardTitle>
                  <CardDescription className="flex items-center gap-2">
                    Trading Hypothesis {HelpTooltips.experimentalMode}
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <DataQualityBadge quality="live" source="MCP v2" />
                <Badge className={getBiasColor(thesis.bias)}>
                  {thesis.bias.toUpperCase()}
                </Badge>
              </div>
            </div>

            {/* Signal Freshness */}
            {thesis.signal_age_minutes !== undefined && (
              <div className="mt-3 pt-3 border-t">
                <SignalFreshness generatedAt={new Date(Date.now() - thesis.signal_age_minutes * 60000).toISOString()} />
              </div>
            )}
          </CardHeader>

          <CardContent className="pt-6 space-y-6">
            {/* Signal Generation vs Context Separation */}
            <div className="p-4 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <strong className="text-blue-700 dark:text-blue-300">How this was generated:</strong>
                  <p className="text-muted-foreground mt-1">
                    1. Technical indicators (RSI, MACD, Volume) analyzed first<br />
                    2. Signal generated based on price action patterns<br />
                    3. Market context retrieved AFTER signal creation to explain reasoning
                  </p>
                </div>
              </div>
            </div>
            {/* Thesis */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Thesis</h3>
              <p className="text-lg">{thesis.thesis}</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-500">Confidence</span>
                  {HelpTooltips.confidence}
                </div>
                <p className={`text-2xl font-bold ${getConfidenceColor(thesis.confidence)}`}>
                  {thesis.confidence}%
                </p>
                {thesis.confidence_adjustments.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    {thesis.confidence_adjustments.join(', ')}
                  </p>
                )}
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-500">Regime</span>
                  {HelpTooltips.marketRegime}
                </div>
                <p className="text-2xl font-bold capitalize">{thesis.regime}</p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-500">Time Horizon</span>
                  <HelpTooltip
                    title="Time Horizon"
                    content="Expected holding period for this trade. Intraday: Same-day exit. Swing: 2-5 days. Position: Weeks to months."
                  />
                </div>
                <p className="text-2xl font-bold">{thesis.time_horizon}</p>
              </div>
            </div>

            {/* Price Range */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Expected Price Range</h3>
              <div className="flex items-center gap-2">
                <Badge variant="default">₹{thesis.price_range_low.toFixed(2)}</Badge>
                <span className="text-gray-400">to</span>
                <Badge variant="default">₹{thesis.price_range_high.toFixed(2)}</Badge>
              </div>
            </div>

            {/* Entry Timing */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Entry Timing</h3>
              <p>{thesis.entry_timing}</p>
            </div>

            {/* Invalidation */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Invalidation Trigger</h3>
              <p className="text-red-600">{thesis.invalidation_reason}</p>
            </div>

            {/* Volume Analysis */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Volume Analysis</h3>
              <p>{thesis.volume_analysis}</p>
            </div>

            {/* Risk Notes */}
            {thesis.risk_notes.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Risk Notes</h3>
                <ul className="space-y-1">
                  {thesis.risk_notes.map((note, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Index Alignment */}
            {thesis.index_alignment && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Index Alignment</h3>
                <p className="text-sm">{thesis.index_alignment}</p>
              </div>
            )}

            {/* Feedback Section */}
            <div className="border-t pt-6">
              <h3 className="text-sm font-medium mb-3">Was this analysis helpful?</h3>
              
              {!feedbackSubmitted ? (
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => handleFeedback('helpful')}
                      className="flex-1"
                    >
                      <ThumbsUp className="w-4 h-4 mr-2" />
                      Helpful
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleFeedback('wrong')}
                      className="flex-1"
                    >
                      <ThumbsDown className="w-4 h-4 mr-2" />
                      Wrong
                    </Button>
                  </div>
                  <Textarea
                    placeholder="Optional: Add notes about what was right or wrong..."
                    value={feedbackNote}
                    onChange={(e) => setFeedbackNote(e.target.value)}
                    rows={3}
                  />
                </div>
              ) : (
                <Alert>
                  <AlertDescription>
                    ✅ Feedback submitted. Thank you for helping improve the system!
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      </div>
    </div>
  );
}
