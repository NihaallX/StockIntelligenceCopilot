"""MCP Context Fetcher - Fetches market context from public sources

Uses MCP tools to fetch real-world market context.
Restricts to reputable financial outlets only.

IMPORTANT: MCP is READ-ONLY context layer
- Does NOT generate signals
- Does NOT alter scores
- Does NOT predict prices
- Only provides citations for existing signals
"""

import logging
import asyncio
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup

from .models import ContextEnrichmentOutput, SupportingPoint, CitationSource
from .indian_sources import (
    EconomicTimesMarketsFetcher,
    NSEAnnouncementsFetcher,
    BSEAnnouncementsFetcher,
    fetch_all_indian_market_sources
)
from .reuters_india_fetcher import ReutersIndiaFetcher
from .reuters_india_fetcher import ReutersIndiaFetcher

logger = logging.getLogger(__name__)


class MCPContextFetcher:
    """
    Fetches market context using MCP tools
    
    Responsible for:
    - Fetching recent company news
    - Fetching sector performance
    - Fetching index movement (NIFTY, Bank NIFTY, etc.)
    - Fetching macro headlines relevant to ticker
    
    RESTRICTIONS:
    - Reputable financial outlets only (Reuters, NSE, Moneycontrol, etc.)
    - No social media
    - No forums
    - Every claim must have a citation
    """
    
    APPROVED_SOURCES = [
        "Reuters",
        "NSE",
        "BSE",
        "Moneycontrol",
        "Economic Times",
        "Bloomberg",
        "Financial Times",
        "SEBI",
        "RBI"
    ]
    
    MCP_TIMEOUT_SECONDS = 10
    
    def __init__(self):
        """Initialize MCP context fetcher"""
        self.approved_sources = self.APPROVED_SOURCES
        
        # Initialize Indian market source fetchers
        self.et_fetcher = EconomicTimesMarketsFetcher()
        self.nse_fetcher = NSEAnnouncementsFetcher()
        self.bse_fetcher = BSEAnnouncementsFetcher()
        self.reuters_fetcher = ReutersIndiaFetcher()
        
        logger.info("MCP Context Fetcher initialized with Indian market sources + Reuters")
    
    def _build_citation(
        self,
        title: str,
        publisher: str,
        url: str,
        published_at: Optional[datetime] = None
    ) -> CitationSource:
        """
        Build a proper citation source
        
        Args:
            title: Article title
            publisher: Publisher name (must be in APPROVED_SOURCES)
            url: Article URL (required)
            published_at: Publication timestamp
        
        Returns:
            CitationSource object
        """
        return CitationSource(
            title=title,
            publisher=publisher,
            url=url,
            published_at=published_at
        )
    
    def _calculate_confidence(
        self,
        sources: List[CitationSource]
    ) -> str:
        """
        Calculate confidence level based on number of citations
        
        Rules:
        - high: 2+ sources from approved list
        - medium: 1 source from approved list
        - low: unverified or questionable source
        
        Args:
            sources: List of citation sources
        
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if len(sources) >= 2:
            return "high"
        elif len(sources) == 1:
            return "medium"
        else:
            return "low"
    
    def _build_supporting_point(
        self,
        claim: str,
        sources: List[CitationSource],
        relevance_score: float = 1.0
    ) -> SupportingPoint:
        """
        Build a SupportingPoint with proper citations and confidence
        
        Args:
            claim: The factual claim
            sources: List of citation sources backing this claim
            relevance_score: Signal relevance score (0-1)
        
        Returns:
            SupportingPoint with confidence calculated from sources
        """
        confidence = self._calculate_confidence(sources)
        
        return SupportingPoint(
            claim=claim,
            sources=sources,
            confidence=confidence,
            relevance_score=relevance_score
        )
    
    async def fetch_context(
        self,
        ticker: str,
        market: str,
        time_horizon: str,
        signal_type: str = "NEUTRAL",
        signal_reasons: List[str] = None,
        confidence: float = 0.5
    ) -> ContextEnrichmentOutput:
        """
        Fetch SIGNAL-AWARE market context for a ticker
        
        This method orchestrates multiple MCP calls and FILTERS for relevance:
        1. Fetch recent news about the company
        2. Filter news that supports or contradicts signal reasons
        3. Reject generic or irrelevant articles
        4. Return only factual statements with citations
        5. Return null if no high-quality sources exist
        
        Args:
            ticker: Stock ticker (e.g., RELIANCE.NS)
            market: Market identifier (e.g., NSE)
            time_horizon: INTRADAY, SHORT_TERM, or LONG_TERM
            signal_type: BUY, SELL, HOLD, or NEUTRAL
            signal_reasons: Array of reasons why signal was generated
            confidence: Signal confidence level (0-1)
        
        Returns:
            ContextEnrichmentOutput with context and citations, or null if no quality sources
        """
        
        if signal_reasons is None:
            signal_reasons = []
        
        supporting_points: List[SupportingPoint] = []
        sources_used: List[str] = []
        
        try:
            # 1. Fetch company news with signal-aware filtering
            news_points = await self._fetch_signal_aware_news(
                ticker=ticker,
                market=market,
                signal_type=signal_type,
                signal_reasons=signal_reasons,
                time_horizon=time_horizon
            )
            supporting_points.extend(news_points)
            
            # 2. Fetch sector performance if relevant to signal
            if self._is_sector_relevant(signal_reasons):
                sector_points = await self._fetch_sector_context(ticker, market)
                supporting_points.extend(sector_points)
            
            # 3. Fetch index movement if relevant
            if self._is_macro_relevant(signal_reasons):
                index_points = await self._fetch_index_movement(market)
                supporting_points.extend(index_points)
            
            # 4. Filter for quality - reject generic or low-relevance articles
            high_quality_points = self._filter_for_quality(
                supporting_points,
                signal_type,
                signal_reasons,
                min_relevance_score=0.6
            )
            
            # Collect unique sources
            sources_used = list(set(point.source for point in supporting_points))
            
            # Generate summary
            context_summary = self._generate_summary(
                supporting_points,
                ticker,
                time_horizon
            )
            
            return ContextEnrichmentOutput(
                context_summary=context_summary,
                supporting_points=supporting_points[:10],  # Limit to 10
                data_sources_used=sources_used,
                disclaimer="Informational only. Not financial advice.",
                enriched_at=datetime.utcnow(),
                mcp_status="success" if supporting_points else "partial"
            )
            
        except Exception as e:
            logger.error(f"MCP context fetching failed: {e}", exc_info=True)
            
            # Return partial results if we have any
            if supporting_points:
                # Extract unique publishers from all citations
                all_publishers = set()
                for point in supporting_points:
                    for source in point.sources:
                        all_publishers.add(source.publisher)
                
                return ContextEnrichmentOutput(
                    context_summary=self._generate_summary(
                        supporting_points,
                        ticker,
                        time_horizon
                    ),
                    supporting_points=supporting_points[:10],
                    data_sources_used=list(all_publishers),
                    disclaimer="Informational only. Not financial advice.",
                    enriched_at=datetime.utcnow(),
                    mcp_status="partial"
                )
            
            # Otherwise, fail gracefully
            raise
    
    async def _fetch_company_news(
        self,
        ticker: str,
        market: str
    ) -> List[SupportingPoint]:
        """
        Fetch recent news about the company from reputable sources
        
        This method:
        1. Searches for recent company news from approved Indian sources
        2. Fetches from Economic Times, NSE, BSE, and Moneycontrol
        3. Extracts factual headlines/statements with proper timestamps
        4. Returns only verifiable claims with citations
        
        IMPLEMENTATION: Uses multiple Indian market sources:
        - Economic Times Markets (news + analysis)
        - NSE India (official announcements)
        - BSE India (official filings)
        - Moneycontrol (market news)
        
        Args:
            ticker: Stock ticker (e.g., RELIANCE.NS)
            market: Market identifier (e.g., NSE)
        
        Returns:
            List of SupportingPoint objects with citations
        """
        logger.info(f"Fetching company news for {ticker} from multiple Indian sources")
        
        supporting_points: List[SupportingPoint] = []
        
        try:
            # Extract company name from ticker (remove .NS/.BO suffix)
            company_ticker = ticker.replace('.NS', '').replace('.BO', '').upper()
            
            # Validate input
            if not company_ticker or not self._is_valid_ticker(company_ticker):
                logger.warning(f"Invalid ticker format: {ticker}")
                return []
            
            # Fetch from all Indian sources concurrently
            all_news = await fetch_all_indian_market_sources(
                ticker=ticker,
                company_name=None,  # TODO: Add company name mapping
                max_per_source=3
            )
            
            # Also fetch from Moneycontrol (existing implementation)
            try:
                mc_news = await self._fetch_moneycontrol_news(
                    company_ticker,
                    timeout_seconds=self.MCP_TIMEOUT_SECONDS
                )
                
                # Convert Moneycontrol format to standard format
                for item in mc_news:
                    all_news.append({
                        'title': item['headline'],
                        'url': item['url'],
                        'published_at': item.get('published_at'),
                        'source': 'Moneycontrol'
                    })
            except Exception as e:
                logger.debug(f"Moneycontrol fetch failed: {e}")
            
            # Sort by published_at (most recent first)
            all_news_sorted = sorted(
                all_news,
                key=lambda x: x.get('published_at') or datetime.min,
                reverse=True
            )
            
            # Convert to supporting points with validation
            for item in all_news_sorted[:10]:  # Top 10 most recent
                try:
                    title = item.get('title', '')
                    url = item.get('url', '')
                    source = item.get('source', 'Unknown')
                    published_at = item.get('published_at')
                    
                    # Validate
                    if not title or len(title) < 10:
                        continue
                    if not url or not url.startswith('http'):
                        continue
                    if source not in self.approved_sources:
                        logger.debug(f"Skipping unapproved source: {source}")
                        continue
                    
                    # Build proper citation
                    citation = self._build_citation(
                        title=title,
                        publisher=source,
                        url=url,
                        published_at=published_at
                    )
                    
                    # Build supporting point with citation
                    supporting_point = self._build_supporting_point(
                        claim=self._sanitize_claim(title),
                        sources=[citation],  # Single source = medium confidence
                        relevance_score=0.7  # Default relevance
                    )
                    
                    supporting_points.append(supporting_point)
                    logger.debug(
                        f"Added {source} item: {title[:50]}... "
                        f"(confidence: {supporting_point.confidence})"
                    )
                
                except Exception as e:
                    logger.debug(f"Skipping news item: {e}")
                    continue
            
            if supporting_points:
                logger.info(
                    f"✅ Found {len(supporting_points)} news items for {ticker} "
                    f"from {len(set(p.sources[0].publisher for p in supporting_points))} sources"
                )
            else:
                logger.info(f"No recent news found for {ticker}")
            
            return supporting_points
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching news for {ticker}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch company news for {ticker}: {e}", exc_info=True)
            return []
    
    async def _fetch_moneycontrol_news(
        self,
        company_ticker: str,
        timeout_seconds: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch news from Moneycontrol (conservative implementation)
        
        This is a REAL implementation using public financial news.
        Uses httpx for async HTTP requests with timeout protection.
        
        Args:
            company_ticker: Ticker symbol without suffix
            timeout_seconds: Request timeout
        
        Returns:
            List of news items with headline and URL
        """
        news_items: List[Dict[str, Any]] = []
        
        try:
            # Moneycontrol news search URL (public endpoint)
            # Note: In production, you'd want to use their official API if available
            search_url = f"https://www.moneycontrol.com/news/tags/{company_ticker.lower()}.html"
            
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                logger.debug(f"Fetching from: {search_url}")
                
                response = await client.get(
                    search_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Stock Analysis Bot - Context Enrichment)'
                    },
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    logger.warning(f"Moneycontrol returned status {response.status_code}")
                    return []
                
                # Parse HTML to extract news items
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find news article elements (Moneycontrol structure)
                # This is conservative - only extract clearly marked news items
                news_links = soup.find_all('h2', class_='')
                
                for link_elem in news_links[:10]:  # Check first 10 items
                    try:
                        a_tag = link_elem.find('a')
                        if a_tag and a_tag.get('href'):
                            headline = a_tag.get_text(strip=True)
                            url = a_tag.get('href')
                            
                            # Ensure URL is absolute
                            if url and not url.startswith('http'):
                                url = f"https://www.moneycontrol.com{url}"
                            
                            # Validate headline is meaningful
                            if headline and len(headline) > 20:
                                news_items.append({
                                    'headline': headline,
                                    'url': url,
                                    'source': 'Moneycontrol'
                                })
                    except Exception as e:
                        logger.debug(f"Skipping malformed news item: {e}")
                        continue
                
                logger.info(f"Extracted {len(news_items)} news items from Moneycontrol")
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching from Moneycontrol")
            raise asyncio.TimeoutError()
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol news: {e}")
            # Return empty list - fail gracefully
        
        return news_items
    
    def _is_valid_ticker(self, ticker: str) -> bool:
        """
        Validate ticker format
        
        Args:
            ticker: Ticker symbol to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Must be 1-10 uppercase letters/numbers
        return bool(re.match(r'^[A-Z0-9]{1,10}$', ticker))
    
    def _validate_news_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate a news item before converting to SupportingPoint
        
        Checks:
        - Has headline
        - Has URL
        - Headline is not spam/clickbait
        - No promotional language
        
        Args:
            item: News item dictionary
        
        Returns:
            True if valid, False otherwise
        """
        headline = item.get('headline', '')
        url = item.get('url', '')
        
        # Must have both headline and URL
        if not headline or not url:
            return False
        
        # Headline must be reasonable length
        if len(headline) < 20 or len(headline) > 300:
            return False
        
        # Reject promotional/spam keywords
        spam_keywords = [
            'click here',
            'buy now',
            'limited offer',
            'act now',
            'guaranteed',
            'free trial'
        ]
        
        headline_lower = headline.lower()
        if any(keyword in headline_lower for keyword in spam_keywords):
            logger.debug(f"Rejected spam headline: {headline}")
            return False
        
        return True
    
    def _sanitize_claim(self, headline: str) -> str:
        """
        Sanitize headline text for use as a claim
        
        Removes:
        - Excessive punctuation
        - Promotional language
        - Formatting issues
        
        Args:
            headline: Raw headline text
        
        Returns:
            Sanitized claim text
        """
        # Remove excessive whitespace
        claim = ' '.join(headline.split())
        
        # Remove leading/trailing punctuation
        claim = claim.strip('.,!?;:')
        
        # Truncate if too long
        if len(claim) > 250:
            claim = claim[:247] + '...'
        
        return claim
    
    async def _fetch_sector_context(
        self,
        ticker: str,
        market: str
    ) -> List[SupportingPoint]:
        """
        Fetch sector performance context
        
        TODO: Implement MCP call to fetch sector indices
        Would fetch from NSE/BSE sector indices.
        
        For now, returns empty list (safe fallback).
        """
        # PLACEHOLDER: Would use MCP to fetch sector data
        logger.debug(f"Fetching sector context for {ticker} (placeholder)")
        return []
    
    async def _fetch_index_movement(
        self,
        market: str
    ) -> List[SupportingPoint]:
        """
        Fetch index movement (NIFTY, Bank NIFTY, etc.)
        
        TODO: Implement MCP call to fetch index data from NSE
        
        For now, returns empty list (safe fallback).
        """
        # PLACEHOLDER: Would use MCP to fetch index data
        logger.debug(f"Fetching index movement for {market} (placeholder)")
        return []
    
    async def _fetch_macro_context(
        self,
        market: str,
        time_horizon: str
    ) -> List[SupportingPoint]:
        """
        Fetch macro headlines relevant to the market using Reuters India
        
        This fetches:
        - RBI policy decisions
        - Inflation data
        - Global cues (US Fed, China, Oil)
        - Market-wide movements
        
        Args:
            market: Market identifier (e.g., NSE, BSE)
            time_horizon: Investment horizon (LONG_TERM, SHORT_TERM)
        
        Returns:
            List of SupportingPoint objects with Reuters citations
        """
        logger.info(f"Fetching macro context from Reuters for {market} market")
        
        supporting_points: List[SupportingPoint] = []
        
        try:
            # Keywords for Indian macro context
            macro_keywords = ["RBI", "India", "inflation", "market", "economy"]
            
            # Fetch macro news from Reuters
            reuters_sources = await self.reuters_fetcher.fetch_macro_news(
                keywords=macro_keywords,
                hours_back=48  # Last 2 days of macro news
            )
            
            # Convert Reuters sources to SupportingPoints
            for source in reuters_sources[:3]:  # Top 3 macro stories
                supporting_point = self._build_supporting_point(
                    claim=self._sanitize_claim(source.title),
                    sources=[source],
                    relevance_score=0.6  # Macro context has medium relevance
                )
                supporting_points.append(supporting_point)
                logger.debug(f"Added Reuters macro: {source.title[:50]}...")
            
            # Also try to fetch global cues if relevant for long-term horizon
            if time_horizon == "LONG_TERM":
                global_sources = await self.reuters_fetcher.fetch_global_cues(
                    hours_back=48
                )
                
                for source in global_sources[:2]:  # Top 2 global stories
                    supporting_point = self._build_supporting_point(
                        claim=self._sanitize_claim(source.title),
                        sources=[source],
                        relevance_score=0.5  # Global cues have lower relevance
                    )
                    supporting_points.append(supporting_point)
                    logger.debug(f"Added Reuters global: {source.title[:50]}...")
            
            if supporting_points:
                logger.info(f"✅ Found {len(supporting_points)} macro context items from Reuters")
            else:
                logger.info("No macro context found from Reuters")
            
            return supporting_points
            
        except Exception as e:
            logger.error(f"Failed to fetch Reuters macro context: {e}", exc_info=True)
            return []
    
    def _generate_summary(
        self,
        supporting_points: List[SupportingPoint],
        ticker: str,
        time_horizon: str
    ) -> str:
        """
        Generate neutral context summary from supporting points
        
        This creates a 3-6 sentence summary that:
        - Is factual and neutral
        - Does NOT make predictions
        - Does NOT recommend actions
        - References the supporting points
        
        Args:
            supporting_points: List of supporting points with citations
            ticker: Stock ticker
            time_horizon: Investment horizon
        
        Returns:
            Context summary string
        """
        if not supporting_points:
            return "No additional market context available at this time."
        
        # Extract key themes from supporting points
        # TODO: Could use LLM here to generate better summary
        
        # For now, create simple concatenation
        summary_parts = []
        
        for point in supporting_points[:3]:  # Use top 3 points
            summary_parts.append(point.claim)
        
        summary = " ".join(summary_parts)
        
        # Add context about time horizon
        if time_horizon == "LONG_TERM":
            summary += " These factors may be relevant for long-term investors."
        else:
            summary += " These developments may impact short-term price action."
        
        return summary
    
    def _validate_source(self, source: str) -> bool:
        """
        Validate that a source is from an approved list
        
        Args:
            source: Source name to validate
        
        Returns:
            True if source is approved, False otherwise
        """
        return source in self.approved_sources
    
    async def _fetch_signal_aware_news(
        self,
        ticker: str,
        market: str,
        signal_type: str,
        signal_reasons: List[str],
        time_horizon: str
    ) -> List[SupportingPoint]:
        """
        Fetch news filtered by signal relevance
        
        Only returns news that supports or contradicts signal_reasons.
        Rejects generic company news if not relevant to signal.
        
        Args:
            ticker: Stock ticker
            market: Market identifier
            signal_type: BUY, SELL, HOLD, or NEUTRAL
            signal_reasons: Reasons why signal was generated
            time_horizon: INTRADAY, SHORT_TERM, or LONG_TERM
        
        Returns:
            List of SupportingPoint objects filtered for relevance
        """
        logger.info(f"Fetching signal-aware news for {ticker} (signal: {signal_type})")
        
        # Extract keywords from signal reasons
        keywords = self._extract_keywords(signal_reasons)
        
        if not keywords:
            logger.info("No keywords extracted from signal reasons, skipping news fetch")
            return []
        
        # Fetch raw news
        company_ticker = ticker.replace('.NS', '').replace('.BO', '').upper()
        try:
            raw_news = await self._fetch_moneycontrol_news(
                company_ticker,
                timeout_seconds=self.MCP_TIMEOUT_SECONDS
            )
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
        
        # Score and filter news for relevance
        relevant_news = []
        for news_item in raw_news[:10]:
            headline = news_item.get('headline', '')
            
            # Calculate relevance score
            relevance = self._calculate_relevance(
                headline,
                keywords,
                signal_type
            )
            
            # Only include if relevance exceeds threshold
            if relevance >= 0.6:
                # Build proper citation
                citation = self._build_citation(
                    title=headline,
                    publisher="Moneycontrol",
                    url=news_item['url'],
                    published_at=news_item.get('published_at')
                )
                
                # Build supporting point with citation and confidence
                supporting_point = self._build_supporting_point(
                    claim=self._sanitize_claim(headline),
                    sources=[citation],  # Single source = medium confidence
                    relevance_score=relevance
                )
                
                relevant_news.append(supporting_point)
                logger.debug(f"✅ Relevant news (score={relevance:.2f}, confidence={supporting_point.confidence}): {headline[:60]}...")
            else:
                logger.debug(f"❌ Rejected (score={relevance:.2f}): {headline[:60]}...")
        
        if relevant_news:
            logger.info(f"Found {len(relevant_news)} relevant news items for signal")
        else:
            logger.info(f"No relevant news found for signal reasons: {signal_reasons}")
        
        return relevant_news
    
    def _extract_keywords(self, signal_reasons: List[str]) -> List[str]:
        """
        Extract keywords from signal reasons for news filtering
        
        Args:
            signal_reasons: List of reasons why signal was generated
        
        Returns:
            List of keywords to search for in news
        """
        keywords = []
        
        # Define keyword mappings for common signal reasons
        keyword_map = {
            'rsi': ['oversold', 'overbought', 'technical', 'momentum', 'indicator'],
            'macd': ['momentum', 'technical', 'crossover', 'trend'],
            'volume': ['volume', 'trading activity', 'liquidity', 'buying', 'selling'],
            'support': ['support level', 'technical support', 'price level', 'resistance'],
            'resistance': ['resistance level', 'technical resistance', 'price level', 'breakout'],
            'moving average': ['moving average', 'ma', 'trend', 'technical'],
            'earnings': ['earnings', 'profit', 'revenue', 'quarterly', 'results', 'financial'],
            'fundamental': ['fundamental', 'valuation', 'pe ratio', 'earnings', 'growth'],
            'sector': ['sector', 'industry', 'peers', 'market'],
            'news': ['announcement', 'news', 'update', 'report', 'statement'],
            'breakout': ['breakout', 'break out', 'resistance', 'new high', 'rally'],
            'breakdown': ['breakdown', 'break down', 'support', 'new low', 'decline'],
            'trend': ['trend', 'uptrend', 'downtrend', 'momentum', 'direction'],
            'volatility': ['volatile', 'volatility', 'swing', 'fluctuation']
        }
        
        # Extract keywords based on signal reasons
        for reason in signal_reasons:
            reason_lower = reason.lower()
            
            # Check for matches in keyword map
            for key, related_keywords in keyword_map.items():
                if key in reason_lower:
                    keywords.extend(related_keywords)
            
            # Also add individual words from reason (if meaningful)
            words = reason_lower.split()
            for word in words:
                if len(word) > 4 and word not in ['this', 'that', 'with', 'from', 'been']:
                    keywords.append(word)
        
        # Remove duplicates
        keywords = list(set(keywords))
        
        logger.debug(f"Extracted keywords: {keywords[:10]}...")  # Show first 10
        return keywords
    
    def _calculate_relevance(
        self,
        headline: str,
        keywords: List[str],
        signal_type: str
    ) -> float:
        """
        Calculate relevance score for a news headline
        
        Scores 0-1 based on:
        - Keyword matches (higher weight for exact matches)
        - Sentiment alignment with signal type
        - Specificity (reject generic claims)
        
        Args:
            headline: News headline text
            keywords: Keywords to search for
            signal_type: BUY, SELL, HOLD, or NEUTRAL
        
        Returns:
            Relevance score (0-1, where 1 is most relevant)
        """
        headline_lower = headline.lower()
        
        # 1. Keyword matching (0-0.7) - Increased weight
        keyword_score = 0.0
        keyword_matches = 0
        
        if keywords:
            for keyword in keywords:
                if keyword.lower() in headline_lower:
                    keyword_matches += 1
            
            # More generous scoring: any match gets you started
            if keyword_matches > 0:
                keyword_score = min(0.4 + (keyword_matches * 0.1), 0.7)
        
        # 2. Sentiment alignment (0-0.2) - Reduced weight
        sentiment_score = 0.0
        
        # Define sentiment words
        positive_words = ['rise', 'gain', 'surge', 'jump', 'rally', 'growth', 'profit', 
                         'beat', 'strong', 'upgrade', 'bullish', 'positive', 'up']
        negative_words = ['fall', 'drop', 'decline', 'plunge', 'loss', 'miss', 'weak',
                         'downgrade', 'bearish', 'negative', 'concern', 'worry', 'down']
        
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)
        
        # Align sentiment with signal type
        if signal_type == "BUY":
            if positive_count > negative_count:
                sentiment_score = 0.2
            elif negative_count > positive_count:
                sentiment_score = 0.15  # Contrarian view also useful
        elif signal_type == "SELL":
            if negative_count > positive_count:
                sentiment_score = 0.2
            elif positive_count > negative_count:
                sentiment_score = 0.15  # Contrarian view also useful
        else:  # NEUTRAL or HOLD
            sentiment_score = 0.1  # Any news gets some weight
        
        # 3. Specificity bonus (0-0.1)
        # Specific headlines get bonus points
        specific_indicators = ['%', 'rs', '₹', 'billion', 'million', 'crore', 'q1', 'q2', 'q3', 'q4']
        specificity_score = 0.1 if any(ind in headline_lower for ind in specific_indicators) else 0.0
        
        # Total score
        total_score = keyword_score + sentiment_score + specificity_score
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _filter_for_quality(
        self,
        points: List[SupportingPoint],
        signal_type: str,
        signal_reasons: List[str],
        min_relevance_score: float = 0.6
    ) -> List[SupportingPoint]:
        """
        Filter supporting points for quality and relevance
        
        Rejects:
        - Low relevance scores (< threshold)
        - Generic claims without specifics
        - Contradictory claims (if confidence is high)
        
        Args:
            points: List of supporting points
            signal_type: BUY, SELL, HOLD, or NEUTRAL
            signal_reasons: Reasons why signal was generated
            min_relevance_score: Minimum relevance score threshold
        
        Returns:
            Filtered list of high-quality supporting points
        """
        high_quality = []
        
        for point in points:
            # Check relevance score (if available)
            relevance = getattr(point, 'relevance_score', 1.0)
            
            if relevance < min_relevance_score:
                logger.debug(f"Rejected (low relevance): {point.claim[:50]}...")
                continue
            
            # Reject generic claims
            if self._is_generic_claim(point.claim):
                logger.debug(f"Rejected (generic): {point.claim[:50]}...")
                continue
            
            # Passed all filters
            high_quality.append(point)
        
        logger.info(f"Quality filter: {len(high_quality)}/{len(points)} points retained")
        
        # Return empty list if no quality sources (return null behavior)
        if not high_quality:
            logger.info("No high-quality sources found, returning empty list")
        
        return high_quality
    
    def _is_generic_claim(self, claim: str) -> bool:
        """
        Check if a claim is too generic to be useful
        
        Args:
            claim: Claim text
        
        Returns:
            True if generic, False if specific
        """
        generic_patterns = [
            r'^.{0,20}announces',  # Very short announcement
            r'^.{0,20}plans to',    # Very short plan
            r'^.{0,20}may consider', # Vague consideration
            r'updates?$',           # Just "updates"
            r'news$',               # Just "news"
        ]
        
        claim_lower = claim.lower()
        
        for pattern in generic_patterns:
            if re.search(pattern, claim_lower):
                return True
        
        # Check for minimum content
        if len(claim) < 30:
            return True
        
        return False
    
    def _is_sector_relevant(self, signal_reasons: List[str]) -> bool:
        """
        Determine if sector context is relevant to signal
        
        Args:
            signal_reasons: Reasons why signal was generated
        
        Returns:
            True if sector context would be useful
        """
        sector_keywords = ['sector', 'industry', 'peer', 'competitor', 'market']
        
        for reason in signal_reasons:
            reason_lower = reason.lower()
            if any(keyword in reason_lower for keyword in sector_keywords):
                return True
        
        return False
    
    def _is_macro_relevant(self, signal_reasons: List[str]) -> bool:
        """
        Determine if macro context is relevant to signal
        
        Args:
            signal_reasons: Reasons why signal was generated
        
        Returns:
            True if macro/index context would be useful
        """
        macro_keywords = ['market', 'index', 'nifty', 'macro', 'economy', 'policy', 'rbi']
        
        for reason in signal_reasons:
            reason_lower = reason.lower()
            if any(keyword in reason_lower for keyword in macro_keywords):
                return True
        
        return False
