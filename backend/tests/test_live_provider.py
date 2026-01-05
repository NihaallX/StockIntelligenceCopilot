"""
Tests for Live Market Data Provider (Phase 2C)

Comprehensive test suite for Alpha Vantage integration with rate limiting,
caching, error handling, and data validation.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.core.market_data.live_provider import LiveMarketDataProvider
from app.core.market_data.base import (
    InvalidTickerError,
    RateLimitExceededError,
    DataProviderError,
    StaleDataWarning
)
from app.core.cache import cache_manager


@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test_api_key_12345"


@pytest.fixture
def provider(mock_api_key):
    """Create test provider instance"""
    return LiveMarketDataProvider(api_key=mock_api_key)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    cache_manager.clear()
    yield
    cache_manager.clear()


class TestProviderInitialization:
    """Test provider initialization and configuration"""
    
    def test_initialization_with_valid_key(self, mock_api_key):
        """Should initialize with valid API key"""
        provider = LiveMarketDataProvider(api_key=mock_api_key)
        assert provider.api_key == mock_api_key
        assert provider.base_url == "https://www.alphavantage.co/query"
    
    def test_initialization_with_empty_key(self):
        """Should raise error with empty API key"""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            LiveMarketDataProvider(api_key="")
    
    def test_get_provider_info(self, provider):
        """Should return provider metadata"""
        info = provider.get_provider_info()
        assert info["name"] == "Live Market Data Provider"
        assert info["source"] == "Alpha Vantage API"
        assert info["rate_limit"] == "5 calls per minute"
        assert "api_key_configured" in info


class TestTickerValidation:
    """Test ticker symbol validation"""
    
    def test_valid_ticker_formats(self, provider):
        """Should accept valid ticker symbols"""
        valid_tickers = ["AAPL", "MSFT", "GOOGL", "BRK.A", "BRK.B"]
        for ticker in valid_tickers:
            assert provider.is_valid_ticker(ticker) is True
    
    def test_invalid_ticker_formats(self, provider):
        """Should reject invalid ticker symbols"""
        invalid_tickers = ["", "  ", "123", "ABC123", "A" * 10, "ABC-DEF"]
        for ticker in invalid_tickers:
            assert provider.is_valid_ticker(ticker) is False


class TestRateLimiting:
    """Test rate limiting behavior"""
    
    def test_rate_limit_enforcement(self, provider):
        """Should enforce 5 calls per minute limit"""
        # Simulate 5 quick calls
        for _ in range(5):
            provider._record_api_call()
        
        # 6th call should detect rate limit
        assert provider._check_rate_limit() is False
    
    def test_rate_limit_reset_after_minute(self, provider):
        """Should reset rate limit after 60 seconds"""
        # Simulate 5 calls 61 seconds ago
        old_time = time.time() - 61
        provider.call_timestamps = [old_time] * 5
        
        # Should allow new call
        assert provider._check_rate_limit() is True
    
    def test_wait_for_rate_limit(self, provider):
        """Should calculate correct wait time"""
        # Simulate 5 recent calls
        current_time = time.time()
        provider.call_timestamps = [
            current_time - 50,
            current_time - 40,
            current_time - 30,
            current_time - 20,
            current_time - 10,
        ]
        
        wait_time = provider._wait_for_rate_limit()
        assert 0 < wait_time <= 60


class TestCaching:
    """Test caching behavior"""
    
    @patch('requests.get')
    def test_cache_hit_fresh_data(self, mock_get, provider):
        """Should serve fresh cache without API call"""
        # Pre-populate cache with fresh data
        cache_key = "market_data_AAPL_90"
        mock_data = {"ticker": "AAPL", "data_source": "cache_fresh"}
        cache_manager.set(cache_key, mock_data, ttl_seconds=3600)
        
        # Should not make API call
        result = provider.get_stock_data("AAPL", lookback_days=90)
        assert mock_get.call_count == 0
        assert result["data_source"] == "cache_fresh"
    
    @patch('requests.get')
    def test_cache_hit_stale_data(self, mock_get, provider):
        """Should serve stale cache with warning"""
        # Pre-populate cache with 2-hour old data
        cache_key = "market_data_AAPL_90"
        old_time = datetime.now() - timedelta(hours=2)
        mock_data = {
            "ticker": "AAPL",
            "cached_at": old_time.isoformat()
        }
        cache_manager.set(cache_key, mock_data, ttl_seconds=86400)  # 24h TTL
        
        # Should serve stale cache
        result = provider.get_stock_data("AAPL", lookback_days=90)
        assert mock_get.call_count == 0
        assert result["data_source"] == "cache_stale"
        assert "hours old" in result.get("data_quality_warning", "")
    
    @patch('requests.get')
    def test_cache_miss_makes_api_call(self, mock_get, provider):
        """Should make API call on cache miss"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Meta Data": {"2. Symbol": "AAPL"},
            "Time Series (Daily)": {
                "2024-01-15": {
                    "1. open": "185.00",
                    "2. high": "187.00",
                    "3. low": "184.00",
                    "4. close": "186.00",
                    "5. adjusted close": "186.00",
                    "6. volume": "50000000"
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = provider.get_stock_data("AAPL", lookback_days=30)
        assert mock_get.call_count == 1
        assert result.ticker == "AAPL"


class TestDataValidation:
    """Test data validation logic"""
    
    def test_validate_price_data_valid(self, provider):
        """Should pass validation for valid data"""
        valid_data = {
            "1. open": "185.00",
            "2. high": "187.00",
            "3. low": "184.00",
            "4. close": "186.00",
            "5. adjusted close": "186.00",
            "6. volume": "50000000"
        }
        
        # Should not raise exception
        provider._validate_price_data(valid_data, "2024-01-15")
    
    def test_validate_price_data_negative_price(self, provider):
        """Should reject negative prices"""
        invalid_data = {
            "4. close": "-186.00",
            "5. adjusted close": "-186.00",
            "6. volume": "50000000"
        }
        
        with pytest.raises(DataProviderError, match="Invalid price data"):
            provider._validate_price_data(invalid_data, "2024-01-15")
    
    def test_validate_price_data_high_less_than_low(self, provider):
        """Should reject high < low"""
        invalid_data = {
            "2. high": "184.00",
            "3. low": "187.00",
            "4. close": "186.00",
            "5. adjusted close": "186.00",
            "6. volume": "50000000"
        }
        
        with pytest.raises(DataProviderError, match="high must be >= low"):
            provider._validate_price_data(invalid_data, "2024-01-15")
    
    def test_validate_minimum_data_points(self, provider):
        """Should require minimum 30 days of data"""
        # Simulate API response with only 20 days
        time_series = {
            f"2024-01-{i:02d}": {
                "4. close": "186.00",
                "5. adjusted close": "186.00",
                "6. volume": "50000000"
            }
            for i in range(1, 21)
        }
        
        with pytest.raises(DataProviderError, match="Insufficient data"):
            provider._parse_market_data(time_series, "AAPL")


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('requests.get')
    def test_invalid_ticker_error(self, mock_get, provider):
        """Should raise InvalidTickerError for unknown tickers"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Error Message": "Invalid API call"
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(InvalidTickerError, match="Invalid ticker"):
            provider.get_stock_data("INVALID", lookback_days=90)
    
    @patch('requests.get')
    def test_rate_limit_exceeded_error(self, mock_get, provider):
        """Should raise RateLimitExceededError on 429"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitExceededError):
            provider.get_stock_data("AAPL", lookback_days=90)
    
    @patch('requests.get')
    def test_network_error_fallback_to_cache(self, mock_get, provider):
        """Should fallback to stale cache on network error"""
        # Pre-populate cache with old data
        cache_key = "market_data_AAPL_90"
        old_data = {
            "ticker": "AAPL",
            "cached_at": (datetime.now() - timedelta(hours=12)).isoformat()
        }
        cache_manager.set(cache_key, old_data, ttl_seconds=86400)
        
        # Simulate network error
        mock_get.side_effect = Exception("Network timeout")
        
        result = provider.get_stock_data("AAPL", lookback_days=90)
        assert result["data_source"] == "cache_error_fallback"
        assert "API error" in result.get("data_quality_warning", "")


class TestRetryLogic:
    """Test retry behavior"""
    
    @patch('requests.get')
    @patch('time.sleep')
    def test_retry_on_500_error(self, mock_sleep, mock_get, provider):
        """Should retry on 500 errors with exponential backoff"""
        # First 2 calls fail with 500, 3rd succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "Meta Data": {"2. Symbol": "AAPL"},
            "Time Series (Daily)": {
                "2024-01-15": {
                    "1. open": "185.00",
                    "2. high": "187.00",
                    "3. low": "184.00",
                    "4. close": "186.00",
                    "5. adjusted close": "186.00",
                    "6. volume": "50000000"
                }
            }
        }
        
        mock_get.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]
        
        result = provider.get_stock_data("AAPL", lookback_days=30)
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Slept before retry 2 and 3
        assert result.ticker == "AAPL"


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @patch('requests.get')
    def test_full_successful_flow(self, mock_get, provider):
        """Test complete successful data fetch flow"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Meta Data": {"2. Symbol": "AAPL"},
            "Time Series (Daily)": {
                f"2024-01-{i:02d}": {
                    "1. open": "185.00",
                    "2. high": "187.00",
                    "3. low": "184.00",
                    "4. close": f"{186 + i}.00",
                    "5. adjusted close": f"{186 + i}.00",
                    "6. volume": "50000000"
                }
                for i in range(1, 91)
            }
        }
        mock_get.return_value = mock_response
        
        # Execute
        result = provider.get_stock_data("AAPL", lookback_days=90)
        
        # Verify
        assert result.ticker == "AAPL"
        assert len(result.prices) == 90
        assert result.data_source == "live"
        assert result.data_quality_warning is None
    
    @patch('requests.get')
    def test_degraded_mode_stale_cache(self, mock_get, provider):
        """Test degraded mode with stale cache"""
        # Pre-populate with 5-hour old data
        cache_key = "market_data_AAPL_90"
        old_time = datetime.now() - timedelta(hours=5)
        old_data = {
            "ticker": "AAPL",
            "cached_at": old_time.isoformat(),
            "prices": []
        }
        cache_manager.set(cache_key, old_data, ttl_seconds=86400)
        
        # API call fails
        mock_get.side_effect = Exception("API unavailable")
        
        # Should fallback to stale cache
        result = provider.get_stock_data("AAPL", lookback_days=90)
        assert result["data_source"] == "cache_error_fallback"
        assert "API error" in result["data_quality_warning"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
