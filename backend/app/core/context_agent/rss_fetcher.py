"""RSS-Based Context Fetcher for MCP

Production-grade RSS fetching to avoid HTML scraping blocks.
Implements reliable, legal, and testable context fetching.

SOURCES:
1. Moneycontrol RSS (Primary)
2. Reuters India RSS (Secondary)
"""

import logging
import httpx
import feedparser
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import quote

from .models import CitationSource

logger = logging.getLogger(__name__)


class MoneycontrolRSSFetcher:
    """
    Fetch context from Moneycontrol RSS feeds
    
    RSS Feeds Available:
    - Market News: https://www.moneycontrol.com/rss/marketreports.xml
    - Business News: https://www.moneycontrol.com/rss/business.xml
    - Buzzing Stocks: https://www.moneycontrol.com/rss/buzzingstocks.xml
    - Latest News: https://www.moneycontrol.com/rss/latestnews.xml
    """
    
    RSS_FEEDS = {
        'market': 'https://www.moneycontrol.com/rss/marketreports.xml',
        'business': 'https://www.moneycontrol.com/rss/business.xml',
        'buzzing': 'https://www.moneycontrol.com/rss/buzzingstocks.xml',
        'latest': 'https://www.moneycontrol.com/rss/latestnews.xml'
    }
    
    def __init__(self):
        self.timeout = 10.0
        logger.info("Moneycontrol RSS fetcher initialized")
    
    async def fetch_company_news(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        hours_back: int = 48
    ) -> List[CitationSource]:
        """
        Fetch company-specific news from Moneycontrol RSS
        
        Args:
            ticker: Stock ticker (e.g., RELIANCE.NS)
            company_name: Company name for filtering (e.g., "Reliance")
            hours_back: How far back to search (default 48 hours)
        
        Returns:
            List of CitationSource objects
        """
        # Extract company name from ticker if not provided
        if not company_name:
            company_name = ticker.replace('.NS', '').replace('.BO', '').upper()
        
        logger.info(f"Fetching Moneycontrol RSS for {company_name}")
        
        all_sources = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Fetch from relevant feeds
        feeds_to_check = ['buzzing', 'market', 'latest']
        
        for feed_name in feeds_to_check:
            try:
                sources = await self._fetch_and_filter_feed(
                    feed_url=self.RSS_FEEDS[feed_name],
                    keywords=[company_name.lower()],
                    cutoff_time=cutoff_time
                )
                all_sources.extend(sources)
                logger.debug(f"Found {len(sources)} articles from {feed_name} feed")
                
            except Exception as e:
                logger.warning(f"Failed to fetch {feed_name} feed: {e}")
                continue
        
        # Deduplicate by URL
        unique_sources = self._deduplicate_sources(all_sources)
        
        logger.info(f"Moneycontrol: Found {len(unique_sources)} unique articles for {company_name}")
        return unique_sources
    
    async def _fetch_and_filter_feed(
        self,
        feed_url: str,
        keywords: List[str],
        cutoff_time: datetime
    ) -> List[CitationSource]:
        """
        Fetch RSS feed and filter by keywords
        
        Args:
            feed_url: RSS feed URL
            keywords: Keywords to filter (case-insensitive)
            cutoff_time: Only return articles after this time
        
        Returns:
            List of matching CitationSource objects
        """
        sources = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                
                # Parse RSS feed
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries:
                    try:
                        # Extract fields
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '').strip()
                        
                        if not title or not link:
                            continue
                        
                        # Parse published date
                        published_at = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        
                        # Filter by time
                        if published_at and published_at < cutoff_time:
                            continue
                        
                        # Filter by keywords (case-insensitive)
                        title_lower = title.lower()
                        if not any(kw.lower() in title_lower for kw in keywords):
                            continue
                        
                        # Create citation
                        source = CitationSource(
                            title=title,
                            publisher="Moneycontrol",
                            url=link,
                            published_at=published_at
                        )
                        sources.append(source)
                        
                    except Exception as e:
                        logger.debug(f"Failed to parse RSS entry: {e}")
                        continue
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching RSS: {feed_url}")
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching RSS: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed: {e}")
        
        return sources
    
    def _deduplicate_sources(self, sources: List[CitationSource]) -> List[CitationSource]:
        """Remove duplicate sources by URL"""
        seen_urls = set()
        unique = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique.append(source)
        
        return unique


class ReutersIndiaRSSFetcher:
    """
    Fetch macro and sector context from Reuters India RSS
    
    RSS Feeds Available:
    - India Business: https://www.reuters.com/rssfeed/INbusinessNews
    - World Business: https://www.reuters.com/rssfeed/businessNews
    """
    
    RSS_FEEDS = {
        'india_business': 'https://www.reuters.com/rssfeed/INbusinessNews',
        'world_business': 'https://www.reuters.com/rssfeed/businessNews'
    }
    
    def __init__(self):
        self.timeout = 10.0
        logger.info("Reuters India RSS fetcher initialized")
    
    async def fetch_macro_news(
        self,
        keywords: List[str],
        hours_back: int = 48
    ) -> List[CitationSource]:
        """
        Fetch macro news from Reuters RSS
        
        Args:
            keywords: Keywords to search (e.g., ["RBI", "inflation", "India"])
            hours_back: How far back to search
        
        Returns:
            List of CitationSource objects
        """
        logger.info(f"Fetching Reuters RSS for keywords: {keywords}")
        
        all_sources = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Fetch from India business feed
        try:
            sources = await self._fetch_and_filter_feed(
                feed_url=self.RSS_FEEDS['india_business'],
                keywords=keywords,
                cutoff_time=cutoff_time
            )
            all_sources.extend(sources)
            logger.debug(f"Found {len(sources)} articles from India business feed")
            
        except Exception as e:
            logger.warning(f"Failed to fetch India business feed: {e}")
        
        # Deduplicate
        unique_sources = self._deduplicate_sources(all_sources)
        
        logger.info(f"Reuters: Found {len(unique_sources)} unique macro articles")
        return unique_sources
    
    async def fetch_sector_news(
        self,
        sector: str,
        hours_back: int = 48
    ) -> List[CitationSource]:
        """
        Fetch sector-specific news from Reuters
        
        Args:
            sector: Sector name (e.g., "Banking", "IT", "Pharma")
            hours_back: How far back to search
        
        Returns:
            List of CitationSource objects
        """
        keywords = [sector, "India", "sector"]
        return await self.fetch_macro_news(keywords, hours_back)
    
    async def _fetch_and_filter_feed(
        self,
        feed_url: str,
        keywords: List[str],
        cutoff_time: datetime
    ) -> List[CitationSource]:
        """Fetch and filter Reuters RSS feed"""
        sources = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries:
                    try:
                        title = entry.get('title', '').strip()
                        link = entry.get('link', '').strip()
                        
                        if not title or not link:
                            continue
                        
                        # Parse published date
                        published_at = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        
                        # Filter by time
                        if published_at and published_at < cutoff_time:
                            continue
                        
                        # Filter by keywords
                        title_lower = title.lower()
                        if not any(kw.lower() in title_lower for kw in keywords):
                            continue
                        
                        source = CitationSource(
                            title=title,
                            publisher="Reuters",
                            url=link,
                            published_at=published_at
                        )
                        sources.append(source)
                        
                    except Exception as e:
                        logger.debug(f"Failed to parse Reuters entry: {e}")
                        continue
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching Reuters RSS: {feed_url}")
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching Reuters RSS: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch Reuters RSS: {e}")
        
        return sources
    
    def _deduplicate_sources(self, sources: List[CitationSource]) -> List[CitationSource]:
        """Remove duplicate sources by URL"""
        seen_urls = set()
        unique = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique.append(source)
        
        return unique


class RSSBasedMCPFetcher:
    """
    Production-grade MCP fetcher using RSS feeds only
    
    This replaces HTML scraping with reliable RSS-based fetching.
    """
    
    def __init__(self):
        self.moneycontrol = MoneycontrolRSSFetcher()
        self.reuters = ReutersIndiaRSSFetcher()
        logger.info("RSS-based MCP fetcher initialized")
    
    async def fetch_context_for_ticker(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        hours_back: int = 48
    ) -> Dict[str, Any]:
        """
        Fetch context for a ticker from all RSS sources
        
        Returns:
            {
                "summary": "...",
                "confidence": "high|medium|low",
                "sources": [...],
                "failure_reason": null | "no_supporting_news" | "rss_unavailable"
            }
        """
        all_sources = []
        
        # Fetch from Moneycontrol RSS
        try:
            mc_sources = await self.moneycontrol.fetch_company_news(
                ticker=ticker,
                company_name=company_name,
                hours_back=hours_back
            )
            all_sources.extend(mc_sources)
        except Exception as e:
            logger.error(f"Moneycontrol RSS failed: {e}")
        
        # Fetch macro context from Reuters RSS
        if company_name:
            try:
                reuters_sources = await self.reuters.fetch_macro_news(
                    keywords=[company_name, "India"],
                    hours_back=hours_back
                )
                all_sources.extend(reuters_sources)
            except Exception as e:
                logger.error(f"Reuters RSS failed: {e}")
        
        # Calculate confidence
        num_sources = len(all_sources)
        if num_sources >= 2:
            confidence = "high"
        elif num_sources == 1:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate summary
        if num_sources > 0:
            summary = self._generate_summary(all_sources, ticker)
            failure_reason = None
        else:
            summary = f"Price moved, but no credible supporting news was found yet for {ticker}."
            failure_reason = "no_supporting_news"
        
        return {
            "summary": summary,
            "confidence": confidence,
            "sources": [
                {
                    "title": s.title,
                    "publisher": s.publisher,
                    "url": s.url,
                    "published_at": s.published_at.isoformat() if s.published_at else None
                }
                for s in all_sources[:5]  # Limit to top 5
            ],
            "failure_reason": failure_reason
        }
    
    def _generate_summary(self, sources: List[CitationSource], ticker: str) -> str:
        """Generate factual summary from sources"""
        if not sources:
            return "No additional market context available at this time."
        
        # Use first source's title as primary context
        primary = sources[0]
        
        if len(sources) == 1:
            return f"Unusual activity detected following recent news: {primary.title}"
        else:
            return f"Market reacting to {len(sources)} recent developments including: {primary.title}"
