"""Fundamental data provider and scoring engine"""

from typing import Optional, Dict
from decimal import Decimal
import logging
from datetime import datetime

from app.models.portfolio_models import FundamentalData, FundamentalScore
from app.core.database import get_service_db

logger = logging.getLogger(__name__)


class FundamentalProvider:
    """Fetches and scores fundamental data"""
    
    @staticmethod
    async def get_fundamentals(ticker: str) -> Optional[FundamentalData]:
        """
        Get fundamental data for a ticker
        
        Currently uses seeded database data.
        TODO: Integrate with real-time data provider (Alpha Vantage, Financial Modeling Prep)
        """
        db = get_service_db()
        
        try:
            result = db.table("fundamental_data").select("*").eq("ticker", ticker).execute()
            
            if not result.data:
                logger.warning(f"No fundamental data found for {ticker}")
                return None
            
            data = result.data[0]
            
            return FundamentalData(
                ticker=data["ticker"],
                company_name=data.get("company_name"),
                market_cap=Decimal(str(data["market_cap"])) if data.get("market_cap") else None,
                pe_ratio=Decimal(str(data["pe_ratio"])) if data.get("pe_ratio") else None,
                pb_ratio=Decimal(str(data["pb_ratio"])) if data.get("pb_ratio") else None,
                dividend_yield=Decimal(str(data["dividend_yield"])) if data.get("dividend_yield") else None,
                revenue_growth_yoy=Decimal(str(data["revenue_growth_yoy"])) if data.get("revenue_growth_yoy") else None,
                earnings_growth_yoy=Decimal(str(data["earnings_growth_yoy"])) if data.get("earnings_growth_yoy") else None,
                revenue_growth_qoq=Decimal(str(data["revenue_growth_qoq"])) if data.get("revenue_growth_qoq") else None,
                profit_margin=Decimal(str(data["profit_margin"])) if data.get("profit_margin") else None,
                operating_margin=Decimal(str(data["operating_margin"])) if data.get("operating_margin") else None,
                roe=Decimal(str(data["roe"])) if data.get("roe") else None,
                roa=Decimal(str(data["roa"])) if data.get("roa") else None,
                debt_to_equity=Decimal(str(data["debt_to_equity"])) if data.get("debt_to_equity") else None,
                current_ratio=Decimal(str(data["current_ratio"])) if data.get("current_ratio") else None,
                quick_ratio=Decimal(str(data["quick_ratio"])) if data.get("quick_ratio") else None,
                last_updated=data.get("last_updated")
            )
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {ticker}: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def score_fundamentals(fundamentals: FundamentalData) -> FundamentalScore:
        """
        Calculate fundamental score (0-100)
        
        Scoring methodology:
        - Valuation (30%): P/E ratio vs sector average
        - Growth (25%): Revenue and earnings growth
        - Profitability (25%): Margins and ROE
        - Financial Health (20%): Debt ratios and liquidity
        """
        
        scores = {}
        
        # Valuation Score (0-30)
        valuation_score = FundamentalProvider._score_valuation(fundamentals)
        scores["valuation"] = valuation_score
        
        # Growth Score (0-25)
        growth_score = FundamentalProvider._score_growth(fundamentals)
        scores["growth"] = growth_score
        
        # Profitability Score (0-25)
        profitability_score = FundamentalProvider._score_profitability(fundamentals)
        scores["profitability"] = profitability_score
        
        # Financial Health Score (0-20)
        health_score = FundamentalProvider._score_financial_health(fundamentals)
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
    
    @staticmethod
    def _score_valuation(fundamentals: FundamentalData) -> float:
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
        
        return min(score, 30)
    
    @staticmethod
    def _score_growth(fundamentals: FundamentalData) -> float:
        """Score growth metrics (0-25)"""
        score = 0.0
        
        # Revenue growth YoY (0-12)
        if fundamentals.revenue_growth_yoy:
            rev_growth = float(fundamentals.revenue_growth_yoy)
            if rev_growth > 20:
                score += 12  # High growth
            elif rev_growth > 10:
                score += 9   # Moderate growth
            elif rev_growth > 5:
                score += 6   # Steady growth
            elif rev_growth > 0:
                score += 3   # Slow growth
            else:
                score += 0   # Declining
        
        # Earnings growth YoY (0-13)
        if fundamentals.earnings_growth_yoy:
            earn_growth = float(fundamentals.earnings_growth_yoy)
            if earn_growth > 25:
                score += 13  # Exceptional growth
            elif earn_growth > 15:
                score += 10  # Strong growth
            elif earn_growth > 10:
                score += 7   # Good growth
            elif earn_growth > 0:
                score += 4   # Positive
            else:
                score += 0   # Declining
        
        return min(score, 25)
    
    @staticmethod
    def _score_profitability(fundamentals: FundamentalData) -> float:
        """Score profitability metrics (0-25)"""
        score = 0.0
        
        # Profit margin (0-8)
        if fundamentals.profit_margin:
            margin = float(fundamentals.profit_margin)
            if margin > 20:
                score += 8
            elif margin > 15:
                score += 6
            elif margin > 10:
                score += 4
            elif margin > 5:
                score += 2
        
        # Operating margin (0-7)
        if fundamentals.operating_margin:
            op_margin = float(fundamentals.operating_margin)
            if op_margin > 25:
                score += 7
            elif op_margin > 15:
                score += 5
            elif op_margin > 10:
                score += 3
            elif op_margin > 5:
                score += 1
        
        # ROE (0-10)
        if fundamentals.roe:
            roe = float(fundamentals.roe)
            if roe > 20:
                score += 10  # Excellent
            elif roe > 15:
                score += 7   # Good
            elif roe > 10:
                score += 4   # Average
            elif roe > 0:
                score += 1   # Weak
        
        return min(score, 25)
    
    @staticmethod
    def _score_financial_health(fundamentals: FundamentalData) -> float:
        """Score financial health metrics (0-20)"""
        score = 0.0
        
        # Debt to equity (0-10)
        if fundamentals.debt_to_equity:
            dte = float(fundamentals.debt_to_equity)
            if dte < 0.3:
                score += 10  # Very low debt
            elif dte < 0.6:
                score += 8   # Low debt
            elif dte < 1.0:
                score += 5   # Moderate debt
            elif dte < 2.0:
                score += 2   # High debt
            else:
                score += 0   # Very high debt
        
        # Current ratio (0-5)
        if fundamentals.current_ratio:
            cr = float(fundamentals.current_ratio)
            if cr > 2:
                score += 5  # Strong liquidity
            elif cr > 1.5:
                score += 4  # Good liquidity
            elif cr > 1.0:
                score += 2  # Adequate liquidity
            else:
                score += 0  # Poor liquidity
        
        # Quick ratio (0-5)
        if fundamentals.quick_ratio:
            qr = float(fundamentals.quick_ratio)
            if qr > 1.5:
                score += 5  # Excellent
            elif qr > 1.0:
                score += 3  # Good
            elif qr > 0.5:
                score += 1  # Weak
        
        return min(score, 20)
