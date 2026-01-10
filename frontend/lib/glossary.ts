/**
 * Technical Glossary for Stock Intelligence Copilot
 * Provides beginner-friendly explanations for technical terms
 */

export interface GlossaryTerm {
  term: string;
  fullName?: string;
  definition: string;
  example: string;
  category: 'technical' | 'fundamental' | 'risk' | 'general';
  relatedTerms?: string[];
}

export const TECHNICAL_GLOSSARY: Record<string, GlossaryTerm> = {
  // Core technical indicators (specified by user)
  VWAP: {
    term: 'VWAP',
    fullName: 'Volume Weighted Average Price',
    definition: 'Average price weighted by volume traded throughout the day. Shows where most trading activity occurred.',
    example: 'If VWAP is ₹2,550 and current price is ₹2,500, that suggests selling pressure dominated recent trades.',
    category: 'technical',
    relatedTerms: ['Volume', 'Support', 'Resistance']
  },
  
  RSI: {
    term: 'RSI',
    fullName: 'Relative Strength Index',
    definition: 'Momentum indicator measuring overbought/oversold conditions on a 0-100 scale. Values below 30 suggest oversold, above 70 suggest overbought.',
    example: 'RSI at 28 indicates oversold conditions – price may have fallen too far, too fast.',
    category: 'technical',
    relatedTerms: ['Momentum', 'Overbought', 'Oversold']
  },
  
  Support: {
    term: 'Support',
    definition: 'Price level where buying interest tends to emerge, preventing further declines. Acts like a "floor" under the price.',
    example: 'If TCS bounces off ₹3,500 three times, that level becomes a support zone where buyers step in.',
    category: 'technical',
    relatedTerms: ['Resistance', 'Range', 'Bounce']
  },
  
  Resistance: {
    term: 'Resistance',
    definition: 'Price level where selling pressure tends to emerge, preventing further gains. Acts like a "ceiling" above the price.',
    example: 'If RELIANCE struggles to break ₹2,700 repeatedly, that becomes a resistance level where sellers dominate.',
    category: 'technical',
    relatedTerms: ['Support', 'Breakout', 'Range']
  },
  
  Volume: {
    term: 'Volume',
    definition: 'Number of shares traded in a given period. High volume indicates strong interest (buying or selling), low volume suggests indecision.',
    example: 'Volume of 5 million shares (3x average) on an up day suggests strong buying conviction.',
    category: 'technical',
    relatedTerms: ['VWAP', 'Liquidity', 'Breakout']
  },
  
  // Related terms for comprehensive understanding
  Momentum: {
    term: 'Momentum',
    definition: 'Rate of price change. Strong momentum means prices are moving quickly in one direction.',
    example: 'A stock gaining 5% in three consecutive days shows bullish momentum.',
    category: 'technical',
    relatedTerms: ['RSI', 'Trend']
  },
  
  Overbought: {
    term: 'Overbought',
    definition: 'Condition where prices have risen too far, too fast. Often precedes a pullback or consolidation.',
    example: 'RSI above 70 combined with rapid gains suggests the stock may be overbought and due for a pause.',
    category: 'technical',
    relatedTerms: ['RSI', 'Oversold', 'Momentum']
  },
  
  Oversold: {
    term: 'Oversold',
    definition: 'Condition where prices have fallen too far, too fast. Often precedes a bounce or stabilization.',
    example: 'RSI below 30 after a sharp drop suggests the stock may be oversold and due for a rebound.',
    category: 'technical',
    relatedTerms: ['RSI', 'Overbought', 'Support']
  },
  
  Breakout: {
    term: 'Breakout',
    definition: 'Price movement above resistance or below support, often signaling the start of a new trend.',
    example: 'If ITC breaks above ₹450 resistance on high volume, that breakout suggests further upside potential.',
    category: 'technical',
    relatedTerms: ['Resistance', 'Support', 'Volume']
  },
  
  Range: {
    term: 'Range',
    definition: 'Price area between support and resistance where a stock trades sideways. Also called consolidation.',
    example: 'TCS trading between ₹3,500 (support) and ₹3,700 (resistance) for two weeks is range-bound.',
    category: 'technical',
    relatedTerms: ['Support', 'Resistance', 'Consolidation']
  },
  
  Trend: {
    term: 'Trend',
    definition: 'General direction of price movement over time. Uptrend = higher highs and higher lows. Downtrend = lower highs and lower lows.',
    example: 'A stock making three consecutive higher highs and higher lows is in an uptrend.',
    category: 'technical',
    relatedTerms: ['Momentum', 'Support', 'Resistance']
  },
  
  // Risk-related terms
  StopLoss: {
    term: 'Stop Loss',
    fullName: 'Stop Loss',
    definition: 'Predetermined price level where you exit a position to limit losses. Risk management tool.',
    example: 'Buying at ₹2,500 with a stop loss at ₹2,450 limits your risk to 2% (₹50 loss).',
    category: 'risk',
    relatedTerms: ['RiskReward', 'PositionSizing']
  },
  
  RiskReward: {
    term: 'Risk/Reward',
    fullName: 'Risk-to-Reward Ratio',
    definition: 'Comparison of potential loss (risk) to potential gain (reward). A 3:1 ratio means you risk ₹1 to potentially gain ₹3.',
    example: 'Entry at ₹2,500, stop at ₹2,450 (₹50 risk), target at ₹2,650 (₹150 reward) = 3:1 risk/reward.',
    category: 'risk',
    relatedTerms: ['StopLoss', 'Target', 'PositionSizing']
  },
  
  PositionSizing: {
    term: 'Position Sizing',
    fullName: 'Position Sizing',
    definition: 'Determining how much capital to allocate to a single trade. Usually expressed as a percentage of portfolio.',
    example: 'A 3% position size on a ₹10 lakh portfolio means investing ₹30,000 in that stock.',
    category: 'risk',
    relatedTerms: ['RiskReward', 'Diversification']
  },
  
  Volatility: {
    term: 'Volatility',
    definition: 'Measure of price fluctuation. High volatility = large price swings. Low volatility = stable prices.',
    example: 'A stock moving ±5% daily has high volatility. One moving ±0.5% has low volatility.',
    category: 'risk',
    relatedTerms: ['Risk', 'Range']
  },
  
  // Fundamental terms
  MarketCap: {
    term: 'Market Cap',
    fullName: 'Market Capitalization',
    definition: 'Total value of a company\'s outstanding shares. Large-cap (>₹20,000 cr), Mid-cap (₹5,000-20,000 cr), Small-cap (<₹5,000 cr).',
    example: 'RELIANCE with 6.8 billion shares at ₹2,500 = ₹17 lakh crore market cap (large-cap).',
    category: 'fundamental',
    relatedTerms: ['LargeCap', 'MidCap', 'SmallCap']
  },
  
  PERatio: {
    term: 'P/E Ratio',
    fullName: 'Price-to-Earnings Ratio',
    definition: 'Stock price divided by earnings per share. Shows how much investors pay for ₹1 of earnings. Lower P/E may indicate undervaluation.',
    example: 'TCS at ₹3,500 with EPS of ₹125 = P/E of 28. Compares to sector average of 25.',
    category: 'fundamental',
    relatedTerms: ['Valuation', 'EPS', 'MarketCap']
  },
  
  Sector: {
    term: 'Sector',
    definition: 'Industry group a stock belongs to. Examples: IT, Banking, Auto, Pharma, FMCG.',
    example: 'TCS, Infosys, and Wipro are all in the IT sector. They often move together based on sector trends.',
    category: 'general',
    relatedTerms: ['Diversification', 'Correlation']
  },
};

/**
 * Get glossary term by key
 */
export function getGlossaryTerm(term: string): GlossaryTerm | undefined {
  return TECHNICAL_GLOSSARY[term];
}

/**
 * Get all terms in a category
 */
export function getTermsByCategory(category: GlossaryTerm['category']): GlossaryTerm[] {
  return Object.values(TECHNICAL_GLOSSARY).filter(term => term.category === category);
}

/**
 * Search glossary by term or definition
 */
export function searchGlossary(query: string): GlossaryTerm[] {
  const lowerQuery = query.toLowerCase();
  return Object.values(TECHNICAL_GLOSSARY).filter(term => 
    term.term.toLowerCase().includes(lowerQuery) ||
    term.definition.toLowerCase().includes(lowerQuery) ||
    term.example.toLowerCase().includes(lowerQuery) ||
    term.fullName?.toLowerCase().includes(lowerQuery)
  );
}

/**
 * Get related terms for a given term
 */
export function getRelatedTerms(termKey: string): GlossaryTerm[] {
  const term = TECHNICAL_GLOSSARY[termKey];
  if (!term || !term.relatedTerms) return [];
  
  return term.relatedTerms
    .map(relatedKey => TECHNICAL_GLOSSARY[relatedKey])
    .filter(Boolean);
}
