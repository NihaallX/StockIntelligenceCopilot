/**
 * Integration Guide: Adding Glossary Tooltips to Analysis Page
 * 
 * This document shows where and how to integrate TermTooltip components
 * into the existing analysis page for beginner education.
 */

// STEP 1: Add import at top of analysis/page.tsx
import { TermTooltip, InlineGlossary } from '@/components/TermTooltip';

// STEP 2: Replace existing technical explanations with tooltip-wrapped versions

// Example 1: In recommendation reasoning (around line 420-430)
// BEFORE:
<p className="text-sm text-muted-foreground">
  {rec.reasoning}
</p>

// AFTER:
<p className="text-sm text-muted-foreground">
  <InlineGlossary>{rec.reasoning}</InlineGlossary>
</p>

// Example 2: In scenario analysis explanations (around line 530)
// BEFORE:
<p className="text-sm text-muted-foreground mb-4">
  Probability-weighted outcomes. Even positive signals carry downside risk.
</p>

// AFTER:
<p className="text-sm text-muted-foreground mb-4">
  Probability-weighted outcomes. Even positive signals carry{' '}
  <TermTooltip term="RiskReward">downside risk</TermTooltip>.
</p>

// Example 3: In market context supporting points (around line 620-640)
// When displaying point.headline or point.summary:
// BEFORE:
<p className="text-sm">{point.headline}</p>
<p className="text-sm text-muted-foreground">{point.summary}</p>

// AFTER:
<InlineGlossary className="text-sm">{point.headline}</InlineGlossary>
<InlineGlossary className="text-sm text-muted-foreground">{point.summary}</InlineGlossary>

// Example 4: Add new "Learn the Terms" section after recommendation (around line 460)
{/* Beginner Education: Term Explanations */}
<div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
  <div className="flex items-center gap-2 mb-3">
    <Info className="w-5 h-5 text-blue-600" />
    <h3 className="font-semibold">Learn the Terms</h3>
  </div>
  
  <p className="text-sm text-muted-foreground mb-4">
    New to technical analysis? Hover over or tap these terms for plain English explanations:
  </p>
  
  <div className="flex flex-wrap gap-3 text-sm">
    <TermTooltip term="RSI">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        📊 RSI
      </span>
    </TermTooltip>
    
    <TermTooltip term="VWAP">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        📈 VWAP
      </span>
    </TermTooltip>
    
    <TermTooltip term="Support">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        🛡️ Support
      </span>
    </TermTooltip>
    
    <TermTooltip term="Resistance">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        ⚠️ Resistance
      </span>
    </TermTooltip>
    
    <TermTooltip term="Volume">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        📊 Volume
      </span>
    </TermTooltip>
    
    <TermTooltip term="StopLoss">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        🛑 Stop Loss
      </span>
    </TermTooltip>
    
    <TermTooltip term="RiskReward">
      <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors cursor-help">
        ⚖️ Risk/Reward
      </span>
    </TermTooltip>
  </div>
  
  <p className="text-xs text-muted-foreground mt-4">
    💡 These tooltips appear throughout the analysis when we mention technical terms
  </p>
</div>

// STEP 3: Optional - Wrap fundamental metrics (around line 490-520)
// Example: Market Cap, P/E Ratio explanations
<div className="text-center">
  <div className="text-2xl font-bold mb-1">
    {analysis.fundamental_score.valuation_score}
  </div>
  <div className="text-sm text-muted-foreground">
    <TermTooltip term="PERatio">Valuation</TermTooltip>
  </div>
</div>

// STEP 4: Add tooltip to position sizing recommendations (if showing specific advice)
<p className="text-sm">
  Recommended <TermTooltip term="PositionSizing">position sizing</TermTooltip>: 2-3% of portfolio
</p>

// STEP 5: Wrap volatility warnings (if showing risk metrics)
<p className="text-sm text-muted-foreground">
  <TermTooltip term="Volatility">Volatility</TermTooltip> elevated at 40% above average. 
  Consider reduced position sizing.
</p>

/**
 * INTEGRATION SUMMARY
 * 
 * 1. Import TermTooltip and InlineGlossary components
 * 2. Wrap recommendation reasoning with InlineGlossary
 * 3. Wrap market context summaries with InlineGlossary
 * 4. Add "Learn the Terms" section with clickable term badges
 * 5. Optionally wrap specific metric labels (Valuation, Volatility, etc.)
 * 
 * KEY FILES MODIFIED:
 * - frontend/app/dashboard/analysis/page.tsx (add tooltips)
 * - frontend/lib/glossary.ts (already created - glossary data)
 * - frontend/components/TermTooltip.tsx (already created - tooltip component)
 * - frontend/app/glossary-demo/page.tsx (demo page to show functionality)
 * 
 * TESTING:
 * 1. Run analysis on any ticker
 * 2. Hover over technical terms → See tooltip
 * 3. Visit /glossary-demo → See all terms and examples
 * 4. Test on mobile → Tap to show/hide tooltips
 */

/**
 * MINIMAL INTEGRATION (Quickstart)
 * 
 * If you want the fastest integration, just add these 3 changes:
 */

// 1. Import at top
import { InlineGlossary } from '@/components/TermTooltip';

// 2. Wrap recommendation reasoning (line ~425)
<InlineGlossary>{rec.reasoning}</InlineGlossary>

// 3. Wrap market context headlines and summaries (line ~630)
<InlineGlossary>{point.headline}</InlineGlossary>
<InlineGlossary>{point.summary}</InlineGlossary>

// DONE! Technical terms will now auto-link to tooltips.
