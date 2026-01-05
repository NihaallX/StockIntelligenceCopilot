"""
Fundamental Provider - Cascading adapter system

Strategy:
1. Try FMP (primary, real-time)
2. Fall back to Database (cached)
3. Return unavailable if all fail

Handles partial data gracefully.
"""

import logging
from typing import Optional
from datetime import datetime

from app.models.portfolio_models import FundamentalData, FundamentalScore
from app.config import settings
from .adapters import FMPAdapter, DatabaseAdapter, FundamentalDataResult, DataSource

logger = logging.getLogger(__name__)


class FundamentalProviderV2:
    """
    Fundamental data provider with cascading adapters
    
    Tries providers in order:
    1. FMP (if API key available)
    2. Database (cached data)
    3. Return unavailable
    """
    
    def __init__(self):
        self.fmp = FMPAdapter(api_key=settings.FMP_API_KEY)
        self.database = DatabaseAdapter()
    
    async def get_fundamentals(self, ticker: str) -> Optional[FundamentalData]:
        """
        Get fundamental data with cascading fallbacks
        
        Returns:
            FundamentalData if ANY provider succeeds (even partial data)
            None if ALL providers fail
        """
        logger.info(f"Fetching fundamentals for {ticker} (cascading strategy)")
        
        # Try FMP first (real-time data)
        fmp_result = await self.fmp.fetch_fundamentals(ticker)
        
        if fmp_result.available:
            logger.info(
                f"✅ FMP success for {ticker}: "
                f"{fmp_result.completeness_percent:.0f}% complete"
            )
            return self._convert_to_model(fmp_result)
        
        logger.warning(f"FMP unavailable for {ticker}, trying database...")
        
        # Fall back to database
        db_result = await self.database.fetch_fundamentals(ticker)
        
        if db_result.available:
            logger.info(
                f"✅ Database fallback for {ticker}: "
                f"{db_result.completeness_percent:.0f}% complete, "
                f"age={db_result.data_age_hours}h"
            )
            return self._convert_to_model(db_result)
        
        # All failed
        logger.warning(f"❌ No fundamental data available for {ticker} (all providers failed)")
        return None
    
    def _convert_to_model(self, result: FundamentalDataResult) -> FundamentalData:
        """Convert adapter result to FundamentalData model"""
        return FundamentalData(
            ticker=result.ticker,
            company_name=result.company_name,
            market_cap=result.market_cap,
            pe_ratio=result.pe_ratio,
            pb_ratio=result.pb_ratio,
            dividend_yield=result.dividend_yield,
            revenue_growth_yoy=result.revenue_growth_yoy,
            earnings_growth_yoy=result.earnings_growth_yoy,
            revenue_growth_qoq=result.revenue_growth_qoq,
            profit_margin=result.profit_margin,
            operating_margin=result.operating_margin,
            roe=result.roe,
            roa=result.roa,
            debt_to_equity=result.debt_to_equity,
            current_ratio=result.current_ratio,
            quick_ratio=result.quick_ratio,
            last_updated=result.last_updated.isoformat() if result.last_updated else None
        )
    
    async def score_fundamentals(self, fundamentals: FundamentalData) -> FundamentalScore:
        """
        Calculate fundamental score (0-100)
        
        Same scoring logic as before, now works with real data from FMP.
        """
        scores = {}
        
        # Valuation Score (0-30)
        valuation_score = self._score_valuation(fundamentals)
        scores["valuation"] = valuation_score
        
        # Growth Score (0-25)
        growth_score = self._score_growth(fundamentals)
        scores["growth"] = growth_score
        
        # Profitability Score (0-25)
        profitability_score = self._score_profitability(fundamentals)
        scores["profitability"] = profitability_score
        
        # Financial Health Score (0-20)
        health_score = self._score_financial_health(fundamentals)
        scores["financial_health"] = health_score
        
        total_score = sum(scores.values())
        
        # Overall assessment
        if total_score >= 80:
            assessment = "STRONG"
        elif total_score >= 60:
            assessment = "MODERATE"
        elif total_score >= 40:
            assessment = "WEAK"
        else:
            assessment = "POOR"
        
        return FundamentalScore(
            ticker=fundamentals.ticker,
            overall_score=int(total_score),
            valuation_score=int(valuation_score),
            growth_score=int(growth_score),
            profitability_score=int(profitability_score),
            financial_health_score=int(health_score),
            overall_assessment=assessment,
            score_details=scores,
            scored_at=datetime.utcnow()
        )
    
    def _score_valuation(self, fundamentals: FundamentalData) -> float:
        """Score valuation metrics (0-30)"""
        score = 0.0
        
        # P/E ratio scoring (0-15)
        if fundamentals.pe_ratio:
            pe = float(fundamentals.pe_ratio)
            if 0 < pe < 15:
                score += 15  # Undervalued
            elif 15 <= pe < 25:
                score += 12  # Fair value
            elif 25 <= pe < 35:
                score += 8   # Slightly expensive
            elif 35 <= pe < 50:
                score += 4   # Expensive
            else:
                score += 2   # Very expensive or negative earnings
        
        # P/B ratio scoring (0-10)
        if fundamentals.pb_ratio:
            pb = float(fundamentals.pb_ratio)
            if 0 < pb < 1:
                score += 10  # Trading below book value
            elif 1 <= pb < 3:
                score += 8   # Reasonable
            elif 3 <= pb < 5:
                score += 5   # Premium
            else:
                score += 2   # Very expensive
        
        # Dividend yield bonus (0-5)
        if fundamentals.dividend_yield:
            div_yield = float(fundamentals.dividend_yield)
            if div_yield > 4:
                score += 5
            elif div_yield > 2:
                score += 3
            elif div_yield > 0:
                score += 1
        
        return score
    
    def _score_growth(self, fundamentals: FundamentalData) -> float:
        """Score growth metrics (0-25)"""
        score = 0.0
        
        # Revenue growth YoY (0-15)
        if fundamentals.revenue_growth_yoy:
            rev_growth = float(fundamentals.revenue_growth_yoy)
            if rev_growth > 20:
                score += 15  # High growth
            elif rev_growth > 10:
                score += 12  # Good growth
            elif rev_growth > 5:
                score += 8   # Moderate growth
            elif rev_growth > 0:
                score += 4   # Slow growth
            else:
                score += 0   # Declining
        
        # Earnings growth YoY (0-10)
        if fundamentals.earnings_growth_yoy:
            earn_growth = float(fundamentals.earnings_growth_yoy)
            if earn_growth > 25:
                score += 10
            elif earn_growth > 15:
                score += 8
            elif earn_growth > 5:
                score += 5
            elif earn_growth > 0:
                score += 2
        
        return score
    
    def _score_profitability(self, fundamentals: FundamentalData) -> float:
        """Score profitability metrics (0-25)"""
        score = 0.0
        
        # Profit margin (0-10)
        if fundamentals.profit_margin:
            margin = float(fundamentals.profit_margin)
            if margin > 20:
                score += 10
            elif margin > 15:
                score += 8
            elif margin > 10:
                score += 6
            elif margin > 5:
                score += 3
        
        # ROE (0-10)
        if fundamentals.roe:
            roe = float(fundamentals.roe)
            if roe > 20:
                score += 10
            elif roe > 15:
                score += 8
            elif roe > 10:
                score += 5
            elif roe > 5:
                score += 2
        
        # Operating margin (0-5)
        if fundamentals.operating_margin:
            op_margin = float(fundamentals.operating_margin)
            if op_margin > 20:
                score += 5
            elif op_margin > 10:
                score += 3
            elif op_margin > 5:
                score += 1
        
        return score
    
    def _score_financial_health(self, fundamentals: FundamentalData) -> float:
        """Score financial health metrics (0-20)"""
        score = 0.0
        
        # Debt-to-equity (0-10)
        if fundamentals.debt_to_equity:
            de = float(fundamentals.debt_to_equity)
            if de < 0.5:
                score += 10  # Conservative leverage
            elif de < 1.0:
                score += 8   # Moderate leverage
            elif de < 2.0:
                score += 5   # Elevated leverage
            else:
                score += 2   # High leverage
        
        # Current ratio (0-5)
        if fundamentals.current_ratio:
            cr = float(fundamentals.current_ratio)
            if cr > 2:
                score += 5
            elif cr > 1.5:
                score += 4
            elif cr > 1:
                score += 2
        
        # Quick ratio (0-5)
        if fundamentals.quick_ratio:
            qr = float(fundamentals.quick_ratio)
            if qr > 1.5:
                score += 5
            elif qr > 1:
                score += 3
            elif qr > 0.5:
                score += 1
        
        return score


# Singleton instance (backward compatibility)
_provider_instance = None

def get_fundamental_provider() -> FundamentalProviderV2:
    """Get singleton fundamental provider instance"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = FundamentalProviderV2()
    return _provider_instance
