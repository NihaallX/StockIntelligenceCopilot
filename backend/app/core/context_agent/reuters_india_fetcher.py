"""Reuters India Market News Fetcher

Fetches macro events, sector-wide news, and market analysis from Reuters India.
Focus: RBI policy, inflation, oil prices, global cues, sector movements.
"""

import logging
import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from .models import CitationSource

logger = logging.getLogger(__name__)


class ReutersIndiaFetcher:
    """
    Fetch macro and sector news from Reuters India
    
    Focus areas:
    - RBI policy decisions
    - Inflation data (CPI, WPI)
    - Oil prices (impacts Indian economy significantly)
    - Global market cues (US Fed, China, etc.)
    - Sector-wide movements (IT, Banking, Pharma, etc.)
    - Regulatory changes
    
    This is a secondary source for macro context. Primary sources are:
    - Moneycontrol (company-specific)
    - Economic Times (Indian markets)
    - NSE/BSE (official announcements)
    """
    
    BASE_URL = "https://www.reuters.com"
    INDIA_MARKETS_URL = f"{BASE_URL}/markets/asia/india"
    WORLD_MARKETS_URL = f"{BASE_URL}/markets/world"
    
    def __init__(self):
        """Initialize Reuters India fetcher"""
        self.base_url = self.BASE_URL
        logger.info("Reuters India fetcher initialized")
    
    async def fetch_macro_news(
        self,
        keywords: List[str],
        hours_back: int = 24
    ) -> List[CitationSource]:
        """
        Fetch macro news relevant to Indian markets
        
        Args:
            keywords: Search terms (e.g., ["RBI", "inflation", "oil"])
            hours_back: How far back to search (default 24 hours)
        
        Returns:
            List of CitationSource objects
        
        Example usage:
            reuters = ReutersIndiaFetcher()
            sources = await reuters.fetch_macro_news(
                keywords=["RBI", "interest rate", "India"],
                hours_back=48
            )
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.INDIA_MARKETS_URL,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = []
                
                # Parse Reuters article structure
                # Reuters uses various article card formats, try multiple selectors
                article_selectors = [
                    'article.story-card',
                    'article[data-testid="MediaStoryCard"]',
                    'div.story-content',
                    'li.story-collection__story'
                ]
                
                for selector in article_selectors:
                    article_elements = soup.select(selector)
                    if article_elements:
                        logger.info(f"Found {len(article_elements)} articles with selector: {selector}")
                        break
                
                if not article_elements:
                    logger.warning("No articles found with any known selector")
                    return []
                
                for article in article_elements[:10]:  # Limit to top 10
                    try:
                        # Try multiple title selectors
                        title_elem = (
                            article.select_one('h3.story-card__headline') or
                            article.select_one('h3[data-testid="Heading"]') or
                            article.select_one('a.text__text__1FZLe') or
                            article.select_one('h3')
                        )
                        
                        # Try multiple link selectors
                        link_elem = (
                            article.select_one('a[href*="/article/"]') or
                            article.select_one('a[href]')
                        )
                        
                        # Try multiple time selectors
                        time_elem = (
                            article.select_one('time[datetime]') or
                            article.select_one('span.timestamp')
                        )
                        
                        if not all([title_elem, link_elem]):
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = link_elem['href']
                        
                        # Make URL absolute if it's relative
                        if not url.startswith('http'):
                            url = self.BASE_URL + url
                        
                        published_at = None
                        if time_elem and time_elem.get('datetime'):
                            try:
                                published_at = datetime.fromisoformat(
                                    time_elem['datetime'].replace('Z', '+00:00')
                                )
                            except Exception as e:
                                logger.debug(f"Failed to parse datetime: {e}")
                        
                        # Filter by keywords (case-insensitive)
                        title_lower = title.lower()
                        if any(kw.lower() in title_lower for kw in keywords):
                            # Check time filter if we have published_at
                            if published_at:
                                cutoff = datetime.now(published_at.tzinfo) - timedelta(hours=hours_back)
                                if published_at < cutoff:
                                    continue
                            
                            articles.append(CitationSource(
                                title=title,
                                publisher="Reuters",
                                url=url,
                                published_at=published_at
                            ))
                    
                    except Exception as e:
                        logger.debug(f"Failed to parse Reuters article: {e}")
                        continue
                
                logger.info(f"Reuters: Found {len(articles)} relevant articles for keywords: {keywords}")
                return articles
        
        except httpx.TimeoutException:
            logger.warning("Reuters fetch timed out")
            return []
        except httpx.HTTPError as e:
            logger.error(f"Reuters HTTP error: {e}")
            return []
        except Exception as e:
            logger.error(f"Reuters fetch failed: {e}")
            return []
    
    async def fetch_sector_news(
        self,
        sector: str,
        hours_back: int = 24
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
    
    async def fetch_global_cues(
        self,
        hours_back: int = 24
    ) -> List[CitationSource]:
        """
        Fetch global market news that impacts Indian markets
        
        Args:
            hours_back: How far back to search
        
        Returns:
            List of CitationSource objects
        
        Focus on:
        - US Fed decisions
        - China economy
        - Crude oil prices
        - Global inflation
        """
        keywords = [
            "Federal Reserve", "Fed", "US market",
            "China economy", "crude oil", "oil price",
            "global inflation", "dollar", "US dollar"
        ]
        return await self.fetch_macro_news(keywords, hours_back)
