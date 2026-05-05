"""Unit tests for YFinanceClient."""

import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from decimal import Decimal

from app.services.yfinance_client import YFinanceClient


class TestYFinanceClient:
    """Test suite for YFinanceClient."""

    @pytest.fixture
    def client(self):
        """Create a YFinanceClient instance."""
        return YFinanceClient(
            max_retries=2,
            backoff_factor=0.1,
            timeout=10,
        )

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data as DataFrame."""
        dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
        data = {
            "Open": [7500.0, 7600.0, 7550.0, 7700.0, 7800.0],
            "High": [7650.0, 7700.0, 7750.0, 7850.0, 7900.0],
            "Low": [7450.0, 7550.0, 7500.0, 7650.0, 7750.0],
            "Close": [7600.0, 7550.0, 7700.0, 7800.0, 7850.0],
            "Adj Close": [7600.0, 7550.0, 7700.0, 7800.0, 7850.0],
            "Volume": [1000000, 1200000, 900000, 1500000, 1100000],
        }
        return pd.DataFrame(data, index=dates)

    def test_init_default_values(self, client):
        """Test client initializes with correct default values."""
        assert client.max_retries == 2
        assert client.backoff_factor == 0.1
        assert client.timeout == 10

    def test_validate_ticker_valid(self, client):
        """Test valid IDX ticker validation."""
        assert client._validate_ticker("BBCA.JK") is True
        assert client._validate_ticker("BBRI.JK") is True
        assert client._validate_ticker("TLKM.JK") is True

    def test_validate_ticker_invalid(self, client):
        """Test invalid ticker validation."""
        assert client._validate_ticker("BBCA") is False  # Missing .JK
        assert client._validate_ticker("INVALID") is False
        assert client._validate_ticker("") is False

    @patch("yfinance.Ticker")
    def test_fetch_ohlcv_success(self, mock_ticker_class, client, sample_ohlcv_data):
        """Test successful OHLCV data fetch."""
        # Setup mock
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = sample_ohlcv_data
        mock_ticker_class.return_value = mock_ticker
        
        # Call method
        result = client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))
        
        # Verify
        assert len(result) == 5
        assert result[0]["date"] == date(2024, 1, 1)
        assert result[0]["open"] == Decimal("7500.00")
        assert result[0]["high"] == Decimal("7650.00")
        assert result[0]["low"] == Decimal("7450.00")
        assert result[0]["close"] == Decimal("7600.00")
        assert result[0]["volume"] == 1000000
        
        # Verify API call
        mock_ticker.history.assert_called_once()
        call_args = mock_ticker.history.call_args
        assert call_args.kwargs["period"] is None
        assert call_args.kwargs["interval"] == "1d"

    @patch("yfinance.Ticker")
    def test_fetch_ohlcv_empty_data(self, mock_ticker_class, client):
        """Test handling of empty OHLCV data."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker
        
        result = client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))
        
        assert result == []

    @patch("yfinance.Ticker")
    def test_fetch_stock_info_success(self, mock_ticker_class, client):
        """Test successful stock info fetch."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "longName": "Bank Central Asia Tbk",
            "sector": "Financial Services",
            "industry": "Banks",
        }
        mock_ticker_class.return_value = mock_ticker
        
        result = client.fetch_stock_info("BBCA.JK")
        
        assert result["name"] == "Bank Central Asia Tbk"
        assert result["sector"] == "Financial Services"

    @patch("yfinance.Ticker")
    def test_fetch_stock_info_missing_name(self, mock_ticker_class, client):
        """Test stock info fetch with missing longName."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "sector": "Technology",
        }
        mock_ticker_class.return_value = mock_ticker
        
        result = client.fetch_stock_info("BBCA.JK")
        
        assert result["name"] == "BBCA.JK"  # Fallback to ticker
        assert result["sector"] == "Technology"

    def test_fetch_ohlcv_invalid_ticker(self, client):
        """Test fetch with invalid ticker raises exception."""
        with pytest.raises(ValueError, match="Invalid ticker format"):
            client.fetch_ohlcv("INVALID", date(2024, 1, 1), date(2024, 1, 5))

    @patch("yfinance.Ticker")
    def test_fetch_ohlcv_rate_limit_retry(self, mock_ticker_class, client, sample_ohlcv_data):
        """Test retry logic on rate limit."""
        mock_ticker = MagicMock()
        # First call raises rate limit, second succeeds
        mock_ticker.history.side_effect = [
            Exception("Rate limited"),
            sample_ohlcv_data,
        ]
        mock_ticker_class.return_value = mock_ticker
        
        result = client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))
        
        assert len(result) == 5
        assert mock_ticker.history.call_count == 2

    def test_date_conversion_to_string(self, client):
        """Test date conversion to string format."""
        test_date = date(2024, 1, 15)
        result = test_date.strftime("%Y-%m-%d")
        assert result == "2024-01-15"

    def test_decimal_conversion(self, client, sample_ohlcv_data):
        """Test price values are converted to Decimal correctly."""
        with patch("yfinance.Ticker") as mock_ticker_class:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = sample_ohlcv_data
            mock_ticker_class.return_value = mock_ticker
            
            result = client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))
            
            # Check all price fields are Decimal
            for item in result:
                assert isinstance(item["open"], Decimal)
                assert isinstance(item["high"], Decimal)
                assert isinstance(item["low"], Decimal)
                assert isinstance(item["close"], Decimal)
                assert isinstance(item["adj_close"], Decimal)
