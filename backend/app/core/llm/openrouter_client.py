"""
OpenRouter LLM Client
=====================

Lightweight async HTTP client for OpenRouter API.
Supports GPT-4o-Mini and other free-tier models.

Features:
- Async HTTP with httpx
- Token counting and rate limiting
- Automatic retries with exponential backoff
- Error handling and fallback
"""

import logging
import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Async client for OpenRouter API
    
    Usage:
        client = OpenRouterClient(api_key="your_key", model="gpt-4o-mini")
        response = await client.complete(prompt="Explain this signal...", max_tokens=300)
    """
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(
        self,
        api_key: str,
        model: str = "xiaomi/mimo-v2-flash:free",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        
        # Rate limiting (simple in-memory)
        self._request_times: list[datetime] = []
        self._rate_limit_window = timedelta(minutes=1)
        self._max_requests_per_window = 20
        
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 400,
        temperature: float = 0.3,
        system_message: Optional[str] = None
    ) -> Optional[str]:
        """
        Send completion request to OpenRouter
        
        Args:
            prompt: User prompt
            max_tokens: Max response tokens (keep low for cost)
            temperature: Sampling temperature (0.3 = more deterministic)
            system_message: Optional system message
            
        Returns:
            Completion text or None if failed
        """
        try:
            # Check rate limit
            await self._check_rate_limit()
            
            # Build messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Make request with retries
            for attempt in range(self.max_retries):
                try:
                    response = await self._make_request(messages, max_tokens, temperature)
                    if response:
                        return response
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"OpenRouter request failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"OpenRouter request failed after {self.max_retries} attempts: {e}")
                        raise
            
            return None
            
        except Exception as e:
            logger.error(f"OpenRouter completion error: {e}")
            return None
    
    async def _make_request(
        self,
        messages: list[Dict[str, str]],
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        """Make HTTP request to OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/stock-intelligence",  # Update with your repo
            "X-Title": "Stock Intelligence Copilot"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        response = await self.client.post(
            self.BASE_URL,
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract completion
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            self._record_request()
            return content.strip()
        
        return None
    
    async def _check_rate_limit(self):
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Remove old requests outside window
        self._request_times = [
            t for t in self._request_times
            if now - t < self._rate_limit_window
        ]
        
        # Check limit
        if len(self._request_times) >= self._max_requests_per_window:
            oldest = self._request_times[0]
            wait_time = (oldest + self._rate_limit_window - now).total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
    
    def _record_request(self):
        """Record successful request for rate limiting"""
        self._request_times.append(datetime.now())
    
    async def cleanup(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        return len(text) // 4
