from typing import Dict, List, Optional, Any
from tavily import TavilyClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TavilyService:
    """
    Service for interacting with the Tavily Search API.
    Designed for Stock Intelligence Copilot to fetch real-time market news and data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tavily client.
        
        Args:
            api_key: Optional API key. If not provided, looks for TAVILY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            # Fallback to the one provided in chat if not in env
            # In production, this should always be in env
            self.api_key = api_key or os.getenv("TAVILY_API_KEY")
            
        self.client = TavilyClient(api_key=self.api_key)

    def search_market_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for market news related to a query.
        
        Args:
            query: The search query (e.g., "AAPL stock news")
            max_results: Number of results to return
            
        Returns:
            List of search results with title, content, url, score
        """
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=None,  # Optional: limit to financial news sites if needed
                exclude_domains=None
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error searching Tavily: {e}")
            return []

    def get_stock_context(self, ticker: str) -> str:
        """
        Get a summarized context for a stock ticker from recent news.
        """
        results = self.search_market_news(f"{ticker} stock news analysis", max_results=3)
        if not results:
            return "No recent news found."
            
        context = f"Recent news for {ticker}:\n"
        for res in results:
            context += f"- {res['title']}: {res['content']} ({res['url']})\n"
            
        return context

# Global instance
tavily_service = TavilyService()
