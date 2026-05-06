"""Unit tests for YFinanceClient."""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd

from app.services.yfinance_client import YFinanceClient


class TestYFinanceClient:
    """Test suite for YFinanceClient."""

    @pytest.fixture
    def client(self):
        """Create a YFinanceClient instance."""
        return YFinanceClient()

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
        df = pd.DataFrame(data, index=dates)
        df.index.name = "Date"
        return df

    def test_init_reads_settings(self, client):
        """Test client initializes from settings."""
        assert client.delay > 0
        assert client.retries >= 1

    @patch("yfinance.Ticker")
    @patch("time.sleep")
    async def test_fetch_ohlcv_success(self, mock_sleep, mock_ticker_class, client, sample_ohlcv_data):
        """Test successful OHLCV data fetch."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = sample_ohlcv_data
        mock_ticker_class.return_value = mock_ticker

        result = await client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert "date" in result.columns
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns
        mock_ticker.history.assert_called_once()

    @patch("yfinance.Ticker")
    @patch("time.sleep")
    async def test_fetch_ohlcv_empty_data(self, mock_sleep, mock_ticker_class, client):
        """Test handling of empty OHLCV data."""
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker

        result = await client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch("yfinance.Ticker")
    @patch("time.sleep")
    async def test_get_stock_info_success(self, mock_sleep, mock_ticker_class, client):
        """Test successful stock info fetch."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "longName": "Bank Central Asia Tbk",
            "sector": "Financial Services",
        }
        mock_ticker_class.return_value = mock_ticker

        result = await client.get_stock_info("BBCA.JK")

        assert result["name"] == "Bank Central Asia Tbk"
        assert result["sector"] == "Financial Services"

    @patch("yfinance.Ticker")
    @patch("time.sleep")
    async def test_get_stock_info_missing_name(self, mock_sleep, mock_ticker_class, client):
        """Test stock info fetch with missing longName."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "shortName": "BCA",
            "sector": "Technology",
        }
        mock_ticker_class.return_value = mock_ticker

        result = await client.get_stock_info("BBCA.JK")

        assert result["name"] == "BCA"  # Fallback to shortName
        assert result["sector"] == "Technology"

    @patch("yfinance.Ticker")
    @patch("time.sleep")
    async def test_fetch_ohlcv_rate_limit_retry(self, mock_sleep, mock_ticker_class, client, sample_ohlcv_data):
        """Test retry logic on failure."""
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = [
            Exception("Rate limited"),
            sample_ohlcv_data,
        ]
        mock_ticker_class.return_value = mock_ticker

        result = await client.fetch_ohlcv("BBCA.JK", date(2024, 1, 1), date(2024, 1, 5))

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert mock_ticker.history.call_count == 2
