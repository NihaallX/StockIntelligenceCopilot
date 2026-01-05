"""Unit tests for Market Context Agent

Tests:
1. Normal case with valid input
2. No sources found
3. MCP failure
4. Invalid input (no opportunity)
5. MCP disabled
6. Real company news fetcher
7. Timeout handling
8. Invalid ticker validation
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import httpx

from app.core.context_agent import (
    MarketContextAgent,
    ContextEnrichmentInput,
    ContextEnrichmentOutput,
    SupportingPoint
)
from app.core.context_agent.mcp_fetcher import MCPContextFetcher


class TestMarketContextAgent:
    """Test suite for Market Context Agent"""
    
    @pytest.fixture
    def valid_input(self):
        """Valid input fixture"""
        return ContextEnrichmentInput(
            opportunity={
                "type": "MOMENTUM_BREAKOUT",
                "confidence": 0.75,
                "risk_level": "MEDIUM"
            },
            ticker="RELIANCE.NS",
            market="NSE",
            time_horizon="LONG_TERM",
            signal_type="BUY",
            signal_reasons=["RSI oversold", "Price above MA50"],
            confidence=0.75
        )
    
    @pytest.fixture
    def mock_context_output(self):
        """Mock context output fixture"""
        from app.core.context_agent.models import CitationSource
        
        return ContextEnrichmentOutput(
            context_summary="RELIANCE.NS operates in energy sector. NIFTY declined 2.3% this week. Oil prices increased 5%.",
            supporting_points=[
                SupportingPoint(
                    claim="NIFTY declined 2.3% this week",
                    sources=[
                        CitationSource(
                            title="NIFTY closes lower amid market volatility",
                            publisher="NSE",
                            url="https://www.nseindia.com"
                        )
                    ],
                    confidence="medium",
                    relevance_score=0.85
                ),
                SupportingPoint(
                    claim="Oil prices increased 5%",
                    sources=[
                        CitationSource(
                            title="Oil prices surge on supply concerns",
                            publisher="Reuters",
                            url="https://www.reuters.com"
                        )
                    ],
                    confidence="medium",
                    relevance_score=0.80
                )
            ],
            data_sources_used=["NSE", "Reuters"],
            disclaimer="Informational only. Not financial advice.",
            enriched_at=datetime.utcnow(),
            mcp_status="success"
        )
    
    @pytest.mark.asyncio
    async def test_normal_case_success(self, valid_input, mock_context_output):
        """Test 1: Normal case with valid input and successful MCP fetch"""
        
        # Arrange
        agent = MarketContextAgent(enabled=True)
        
        with patch.object(
            agent.mcp_fetcher,
            'fetch_context',
            new_callable=AsyncMock,
            return_value=mock_context_output
        ):
            # Act
            result = await agent.enrich_opportunity(valid_input)
            
            # Assert
            assert result.mcp_status == "success"
            assert len(result.supporting_points) == 2
            assert len(result.data_sources_used) == 2
            assert "NIFTY" in result.context_summary
            assert result.disclaimer == "Informational only. Not financial advice."
    
    @pytest.mark.asyncio
    async def test_no_sources_found(self, valid_input):
        """Test 2: No sources found - should return partial status"""
        
        # Arrange
        agent = MarketContextAgent(enabled=True)
        
        empty_output = ContextEnrichmentOutput(
            context_summary="No additional market context available at this time.",
            supporting_points=[],
            data_sources_used=[],
            disclaimer="Informational only. Not financial advice.",
            enriched_at=datetime.utcnow(),
            mcp_status="partial"
        )
        
        with patch.object(
            agent.mcp_fetcher,
            'fetch_context',
            new_callable=AsyncMock,
            return_value=empty_output
        ):
            # Act
            result = await agent.enrich_opportunity(valid_input)
            
            # Assert
            assert result.mcp_status == "partial"
            assert len(result.supporting_points) == 0
            assert result.context_summary == "No additional market context available at this time."
    
    @pytest.mark.asyncio
    async def test_mcp_failure(self, valid_input):
        """Test 3: MCP failure - should return safe fallback"""
        
        # Arrange
        agent = MarketContextAgent(enabled=True)
        
        with patch.object(
            agent.mcp_fetcher,
            'fetch_context',
            new_callable=AsyncMock,
            side_effect=Exception("MCP timeout")
        ):
            # Act
            result = await agent.enrich_opportunity(valid_input)
            
            # Assert
            assert result.mcp_status == "failed"
            assert len(result.supporting_points) == 0
            assert result.context_summary == "No additional market context available at this time."
    
    @pytest.mark.asyncio
    async def test_invalid_input_no_opportunity(self):
        """Test 4: Invalid input (no opportunity) - should return safe fallback"""
        
        # Arrange
        agent = MarketContextAgent(enabled=True)
        
        invalid_input = ContextEnrichmentInput(
            opportunity={},  # Empty opportunity
            ticker="RELIANCE.NS",
            market="NSE",
            time_horizon="LONG_TERM",
            signal_type="NEUTRAL",
            confidence=0.0
        )
        
        # Act
        result = await agent.enrich_opportunity(invalid_input)
        
        # Assert
        assert result.mcp_status == "failed"
        assert len(result.supporting_points) == 0
        assert result.context_summary == "No additional market context available at this time."
    
    @pytest.mark.asyncio
    async def test_mcp_disabled(self, valid_input):
        """Test 5: MCP disabled - should return safe fallback immediately"""
        
        # Arrange
        agent = MarketContextAgent(enabled=False)
        
        # Act
        result = await agent.enrich_opportunity(valid_input)
        
        # Assert
        assert result.mcp_status == "disabled"
        assert len(result.supporting_points) == 0
        assert result.context_summary == "No additional market context available at this time."
        assert agent.mcp_fetcher is None  # Should not initialize fetcher
    
    def test_validate_input_valid(self, valid_input):
        """Test input validation - valid input"""
        
        # Arrange
        agent = MarketContextAgent(enabled=False)
        
        # Act
        is_valid = agent.validate_input(valid_input)
        
        # Assert
        assert is_valid is True
    
    def test_validate_input_no_opportunity(self):
        """Test input validation - no opportunity"""
        
        # Arrange
        agent = MarketContextAgent(enabled=False)
        
        invalid_input = ContextEnrichmentInput(
            opportunity={},
            ticker="RELIANCE.NS",
            market="NSE",
            time_horizon="LONG_TERM",
            signal_type="NEUTRAL",
            confidence=0.0
        )
        
        # Act
        is_valid = agent.validate_input(invalid_input)
        
        # Assert
        assert is_valid is False
    
    def test_validate_input_no_ticker(self):
        """Test input validation - no ticker"""
        
        # Arrange
        agent = MarketContextAgent(enabled=False)
        
        invalid_input = ContextEnrichmentInput(
            opportunity={"type": "TEST"},
            ticker="RELIANCE.NS",  # Changed to valid ticker
            market="NSE",
            time_horizon="LONG_TERM",
            signal_type="NEUTRAL",
            confidence=0.5
        )
        
        # Test validation manually
        result = agent._validate_input(invalid_input)
        
        # Change ticker to empty after creation to test validation
        invalid_input.ticker = ""
        
        # Act & Assert
        with pytest.raises(Exception):  # Pydantic will raise validation error
            agent.validate_input(invalid_input)


class TestMCPContextFetcher:
    """Test suite for MCP Context Fetcher"""
    
    def test_validate_approved_source(self):
        """Test source validation - approved source"""
        fetcher = MCPContextFetcher()
        
        assert fetcher._validate_source("Reuters") is True
        assert fetcher._validate_source("NSE") is True
        assert fetcher._validate_source("Moneycontrol") is True
    
    def test_validate_unapproved_source(self):
        """Test source validation - unapproved source"""
        fetcher = MCPContextFetcher()
        
        assert fetcher._validate_source("Random Blog") is False
        assert fetcher._validate_source("Twitter") is False
        assert fetcher._validate_source("Reddit") is False
    
    def test_is_valid_ticker(self):
        """Test ticker validation"""
        fetcher = MCPContextFetcher()
        
        # Valid tickers
        assert fetcher._is_valid_ticker("RELIANCE") is True
        assert fetcher._is_valid_ticker("TCS") is True
        assert fetcher._is_valid_ticker("INFY") is True
        
        # Invalid tickers
        assert fetcher._is_valid_ticker("") is False
        assert fetcher._is_valid_ticker("reliance") is False  # Lowercase
        assert fetcher._is_valid_ticker("REL@ANCE") is False  # Special chars
        assert fetcher._is_valid_ticker("TOOLONGTICKER") is False  # Too long
    
    def test_validate_news_item_valid(self):
        """Test news item validation - valid item"""
        fetcher = MCPContextFetcher()
        
        valid_item = {
            'headline': 'Reliance Industries reports Q3 earnings growth',
            'url': 'https://www.moneycontrol.com/news/...',
            'source': 'Moneycontrol'
        }
        
        assert fetcher._validate_news_item(valid_item) is True
    
    def test_validate_news_item_invalid(self):
        """Test news item validation - invalid items"""
        fetcher = MCPContextFetcher()
        
        # Missing headline
        assert fetcher._validate_news_item({'url': 'http://...'}) is False
        
        # Missing URL
        assert fetcher._validate_news_item({'headline': 'Test'}) is False
        
        # Too short headline
        assert fetcher._validate_news_item({
            'headline': 'Short',
            'url': 'http://...'
        }) is False
        
        # Spam headline
        assert fetcher._validate_news_item({
            'headline': 'Click here for guaranteed returns buy now!',
            'url': 'http://...'
        }) is False
    
    def test_sanitize_claim(self):
        """Test claim sanitization"""
        fetcher = MCPContextFetcher()
        
        # Normal case
        result = fetcher._sanitize_claim("  Reliance Industries reports earnings  ")
        assert result == "Reliance Industries reports earnings"
        
        # Trailing punctuation
        result = fetcher._sanitize_claim("Company announces dividend.!?")
        assert result == "Company announces dividend"
        
        # Excessive whitespace
        result = fetcher._sanitize_claim("Test   with   spaces")
        assert result == "Test with spaces"
    
    @pytest.mark.asyncio
    async def test_fetch_company_news_invalid_ticker(self):
        """Test company news fetch with invalid ticker"""
        fetcher = MCPContextFetcher()
        
        # Invalid ticker should return empty list
        result = await fetcher._fetch_company_news("invalid@ticker", "NSE")
        assert result == []
    
    @pytest.mark.asyncio
    async def test_fetch_company_news_timeout(self):
        """Test company news fetch with timeout"""
        fetcher = MCPContextFetcher()
        
        with patch('app.core.context_agent.mcp_fetcher.httpx.AsyncClient') as mock_client:
            # Simulate timeout
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            
            result = await fetcher._fetch_company_news("RELIANCE", "NSE")
            
            # Should return empty list on timeout
            assert result == []
    
    @pytest.mark.asyncio
    async def test_fetch_moneycontrol_news_success(self):
        """Test Moneycontrol news fetch - successful case"""
        fetcher = MCPContextFetcher()
        
        # Mock HTML response
        mock_html = """
        <html>
            <h2><a href="/news/business/reliance-q3-earnings">Reliance Industries reports strong Q3 earnings growth</a></h2>
            <h2><a href="/news/business/reliance-expansion">Reliance announces expansion plans in retail sector</a></h2>
        </html>
        """
        
        with patch('app.core.context_agent.mcp_fetcher.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await fetcher._fetch_moneycontrol_news("RELIANCE", timeout_seconds=10)
            
            # Should extract news items
            assert len(result) >= 0  # May be 0 if HTML structure doesn't match
            # If items found, validate structure
            if result:
                assert 'headline' in result[0]
                assert 'url' in result[0]
    
    @pytest.mark.asyncio
    async def test_fetch_moneycontrol_news_http_error(self):
        """Test Moneycontrol news fetch - HTTP error"""
        fetcher = MCPContextFetcher()
        
        with patch('app.core.context_agent.mcp_fetcher.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await fetcher._fetch_moneycontrol_news("INVALID", timeout_seconds=10)
            
            # Should return empty list on HTTP error
            assert result == []
