// API client for Stock Intelligence Copilot backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  risk_profile?: {
    risk_tolerance: string;
    max_position_size_usd: number;
    max_drawdown_percent: number;
  };
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

export interface PortfolioPosition {
  id: string;
  ticker: string;
  quantity: string;
  entry_price: string;
  cost_basis: string;
  current_price?: string;
  unrealized_pnl?: string;
  unrealized_pnl_percent?: string;
  entry_date: string;
}

export interface PortfolioSummary {
  total_positions: number;
  total_value: string;
  total_cost_basis: string;
  total_unrealized_pnl: string;
  total_unrealized_pnl_percent: string;
  largest_position_ticker: string;
  largest_position_percent: string;
}

export interface CitationSource {
  title: string;
  publisher: string;
  url: string;
  published_at?: string;
}

export interface SupportingPoint {
  claim: string;
  sources: CitationSource[];
  confidence: 'high' | 'medium' | 'low';
  relevance_score: number;
}

export interface MarketContext {
  context_summary: string;
  supporting_points: SupportingPoint[];
  data_sources_used: string[];
  mcp_status: 'success' | 'partial' | 'failed' | 'disabled';
  disclaimer: string;
}

export interface EnhancedAnalysis {
  technical_insight: any;
  fundamental_score?: {
    overall_score: number;
    overall_assessment: string;
    valuation_score: number;
    growth_score: number;
    profitability_score: number;
    financial_health_score: number;
  };
  scenario_analysis?: {
    best_case: {
      expected_return_percent: string;
      probability: string;
    };
    base_case: {
      expected_return_percent: string;
      probability: string;
    };
    worst_case: {
      expected_return_percent: string;
      probability: string;
    };
    expected_return_weighted: string;
    risk_reward_ratio: string;
  };
  combined_score: string;
  recommendation: string;
  market_context?: MarketContext;
  ai_explanation?: AIExplanation;
}

export interface AIExplanation {
  explanation: string;
  what_went_right: string[];
  what_could_go_wrong: string[];
  confidence_label: 'high' | 'medium' | 'low';
  fallback: boolean;
  disclaimer: string;
}

export interface IndexBias {
  name: string;
  bias: string;
  change_percent?: number;
}

export interface MarketPulse {
  regime: string;
  index_bias: IndexBias[];
  liquidity: string;
  summary: string;
  worth_trading: boolean;
  timestamp: string;
  session_time: string;
}

export type ErrorCategory = 'auth' | 'network' | 'server' | 'validation' | 'unknown';

class ApiError extends Error {
  public readonly category: ErrorCategory;
  public readonly isRetryable: boolean;
  
  constructor(
    public status: number, 
    message: string,
    public originalError?: any
  ) {
    super(message);
    this.name = 'ApiError';
    
    // Categorize error
    if (status === 401 || status === 403) {
      this.category = 'auth';
      this.isRetryable = false;
    } else if (status >= 500) {
      this.category = 'server';
      this.isRetryable = true;
    } else if (status === 408 || status === 0) {
      this.category = 'network';
      this.isRetryable = true;
    } else if (status >= 400 && status < 500) {
      this.category = 'validation';
      this.isRetryable = false;
    } else {
      this.category = 'unknown';
      this.isRetryable = false;
    }
  }
  
  getUserMessage(): string {
    switch (this.category) {
      case 'auth':
        return 'Your session has expired. Please sign in again to continue.';
      case 'server':
        return 'Our service is temporarily unavailable. Please try again in a few moments.';
      case 'network':
        return 'Connection timed out. Please check your network and try again.';
      case 'validation':
        return this.message; // Use specific validation message
      default:
        return 'An unexpected issue occurred. Please try again.';
    }
  }
}

// Timeout wrapper for fetch requests
function fetchWithTimeout(url: string, options: RequestInit, timeout = 30000): Promise<Response> {
  return Promise.race([
    fetch(url, options),
    new Promise<Response>((_, reject) =>
      setTimeout(() => reject(new ApiError(408, 'Request timed out')), timeout)
    ),
  ]);
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    
    // Check for auth expiry
    if (response.status === 401) {
      // Clear stored tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('user');
        localStorage.removeItem('tokens');
      }
    }
    
    throw new ApiError(response.status, error.detail || 'Request failed', error);
  }
  
  // Handle 204 No Content responses
  if (response.status === 204) {
    return {} as T;
  }
  
  try {
    return await response.json();
  } catch (e) {
    throw new ApiError(500, 'Invalid response from server', e);
  }
}

// Auth endpoints
export async function register(email: string, password: string, fullName: string) {
  const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
      terms_accepted: true,
      risk_acknowledged: true,
    }),
  });
  return handleResponse<LoginResponse>(response);
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<LoginResponse>(response);
}

// Portfolio endpoints
export async function getPortfolioPositions(token: string) {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/portfolio/positions`, {
    headers: { Authorization: `Bearer ${token}` },
  }, 10000);
  return handleResponse<PortfolioPosition[]>(response);
}

export async function getPortfolioSummary(token: string) {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/portfolio/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  }, 10000); // 10s timeout for summary
  return handleResponse<PortfolioSummary>(response);
}

export async function addPortfolioPosition(
  token: string,
  ticker: string,
  quantity: number,
  entryPrice: number,
  entryDate: string,
  notes?: string
) {
  const response = await fetch(`${API_BASE}/api/v1/portfolio/positions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ticker,
      quantity,
      entry_price: entryPrice,
      entry_date: entryDate,
      notes,
    }),
  });
  return handleResponse<PortfolioPosition>(response);
}

export async function validateTicker(token: string, ticker: string) {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/portfolio/validate-ticker/${encodeURIComponent(ticker)}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
    8000  // 8 second timeout for validation
  );
  return handleResponse<{ valid: boolean; ticker: string; message: string }>(response);
}

export async function getHistoricalPrice(token: string, ticker: string, date: string) {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/portfolio/historical-price/${encodeURIComponent(ticker)}/${date}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
    8000
  );
  return handleResponse<{ ticker: string; date: string; price: number }>(response);
}

export async function deletePortfolioPosition(
  token: string,
  positionId: string
) {
  const response = await fetch(`${API_BASE}/api/v1/portfolio/positions/${positionId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return handleResponse<{ message: string }>(response);
}

// Analysis endpoints
export async function getEnhancedAnalysis(token: string, ticker: string) {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/analysis/enhanced`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ticker }),
    },
    30000 // 30s timeout for analysis (complex operation)
  );
  return handleResponse<EnhancedAnalysis>(response);
}

// Portfolio AI Suggestions
export interface PortfolioNudge {
  nudge: string;
  context: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  applies_to: string[];
}

export interface PortfolioAISuggestionsResponse {
  success: boolean;
  portfolio_score: number;
  portfolio_health: string;
  total_value: number;
  total_pnl: number;
  total_pnl_percent: number;
  suggestions: PortfolioNudge[];
  risk_assessment: string;
  diversification_score: number;
  processing_time_ms: number;
}

export async function getPortfolioAISuggestions(
  token: string,
  positions: PortfolioPosition[],
  riskTolerance: 'conservative' | 'moderate' | 'aggressive' = 'moderate',
  timeHorizon: 'short_term' | 'medium_term' | 'long_term' = 'medium_term'
) {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/portfolio/ai-suggestions`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        positions,
        risk_tolerance: riskTolerance,
        time_horizon: timeHorizon
      }),
    },
    45000 // 45s timeout - analyzing entire portfolio
  );
  return handleResponse<PortfolioAISuggestionsResponse>(response);
}

// Notable Signals (Today's Situations)
export interface NotableSignal {
  ticker: string;
  company_name?: string;
  signal_type: "BUY" | "SELL" | "HOLD" | "NEUTRAL";
  signal_strength: "STRONG" | "MODERATE" | "WEAK";
  confidence: number;
  headline: string;
  summary: string;
  key_reasons: string[];
  timestamp: string;
  is_new: boolean;
  market_context?: MarketContext;
}

export interface NotableSignalsResponse {
  signals: NotableSignal[];
  total_portfolio_stocks: number;
  last_updated: string;
}

export async function getNotableSignals(
  token: string,
  maxSignals: number = 5
) {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/portfolio/notable-signals?max_signals=${maxSignals}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    },
    15000 // 15s timeout
  );
  return handleResponse<NotableSignalsResponse>(response);
}

// LLM Explanation Service
export interface ExplainVWAPRequest {
  ticker: string;
  signal: {
    bias: string;
    confidence: number;
    method: string;
    keyLevels?: {
      VWAP?: number;
      invalidation?: number;
    };
  };
  mcp_context?: {
    regime?: string;
    indexAlignment?: string;
    volumeState?: string;
    sessionTime?: string;
  };
  price_data?: {
    current?: number;
    vwap?: number;
  };
}

export async function explainVWAPSignal(
  token: string,
  request: ExplainVWAPRequest
): Promise<AIExplanation> {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/explain/vwap`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    },
    10000 // 10s timeout
  );
  return handleResponse<AIExplanation>(response);
}

// Market Pulse
export async function getMarketPulse(token: string): Promise<MarketPulse> {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/market/pulse`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
    10000 // 10s timeout
  );
  return handleResponse<MarketPulse>(response);
}

// Opportunities Feed
export interface OpportunityMCPContext {
  price_vs_vwap: string;
  volume_ratio: number;
  index_alignment: string;
  regime: string;
  news_status: "none" | "positive" | "negative" | "mixed";
}

export interface Opportunity {
  ticker: string;
  setup_type: "vwap_bounce" | "vwap_rejection" | "breakout" | "breakdown" | "consolidation";
  confidence: number;
  time_sensitivity: "immediate" | "today" | "this_week";
  summary: string;
  mcp_context: OpportunityMCPContext;
  current_price: number;
  target_price?: number;
  stop_loss?: number;
  bias: "bullish" | "bearish" | "neutral";
  timestamp: string;
}

export interface OpportunitiesFeed {
  opportunities: Opportunity[];
  market_regime: string;
  total_scanned: number;
  filtered_by_confidence: number;
  filtered_by_regime: number;
  timestamp: string;
}

export async function getOpportunitiesFeed(token: string): Promise<OpportunitiesFeed> {
  const response = await fetchWithTimeout(
    `${API_BASE}/api/v1/opportunities/feed`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
    15000 // 15s timeout for scanning
  );
  return handleResponse<OpportunitiesFeed>(response);
}

export { ApiError };
