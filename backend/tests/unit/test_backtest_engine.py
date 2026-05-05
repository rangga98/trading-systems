"""Unit tests for BacktestEngine."""

import pytest
from datetime import date
from decimal import Decimal

from app.services.backtest_engine import BacktestEngine


class TestBacktestEngine:
    """Test suite for BacktestEngine."""

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Sample OHLCV data for backtesting."""
        return [
            {"date": date(2024, 1, 1), "open": "100.00", "high": "110.00", "low": "95.00", "close": "105.00", "volume": 1000000},
            {"date": date(2024, 1, 2), "open": "105.00", "high": "115.00", "low": "100.00", "close": "110.00", "volume": 1200000},
            {"date": date(2024, 1, 3), "open": "110.00", "high": "120.00", "low": "105.00", "close": "115.00", "volume": 1500000},
            {"date": date(2024, 1, 4), "open": "115.00", "high": "125.00", "low": "110.00", "close": "120.00", "volume": 1100000},
            {"date": date(2024, 1, 5), "open": "120.00", "high": "130.00", "low": "115.00", "close": "125.00", "volume": 1300000},
            {"date": date(2024, 1, 8), "open": "125.00", "high": "135.00", "low": "120.00", "close": "130.00", "volume": 1000000},
            {"date": date(2024, 1, 9), "open": "130.00", "high": "140.00", "low": "125.00", "close": "135.00", "volume": 1100000},
            {"date": date(2024, 1, 10), "open": "135.00", "high": "145.00", "low": "130.00", "close": "140.00", "volume": 1200000},
            {"date": date(2024, 1, 11), "open": "140.00", "high": "150.00", "low": "135.00", "close": "145.00", "volume": 900000},
            {"date": date(2024, 1, 12), "open": "145.00", "high": "155.00", "low": "140.00", "close": "150.00", "volume": 800000},
        ]

    @pytest.fixture
    def basic_config(self):
        """Basic backtest configuration."""
        return {
            "strategy_name": "Buy and Hold Test",
            "initial_capital": Decimal("100000000.00"),  # Rp 100M
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 12),
        }

    def test_buy_and_hold_profit(self, sample_ohlcv_data, basic_config):
        """Test buy-and-hold strategy generates profit in uptrend."""
        engine = BacktestEngine(sample_ohlcv_data, basic_config)
        result = engine.run_buy_and_hold()

        assert result["total_return_pct"] > 0
        assert result["final_equity"] > result["initial_capital"]

    def test_buy_and_hold_entry_price(self, sample_ohlcv_data, basic_config):
        """Test buy-and-hold enters at first day open."""
        engine = BacktestEngine(sample_ohlcv_data, basic_config)
        result = engine.run_buy_and_hold()

        # Should enter on first data point
        assert len(result["trades"]) == 1
        first_trade = result["trades"][0]
        assert first_trade["position_type"] == "LONG"
        assert first_trade["entry_price"] == Decimal("100.00")

    def test_buy_and_hold_exit_at_end(self, sample_ohlcv_data, basic_config):
        """Test buy-and-hold exits at last day close."""
        engine = BacktestEngine(sample_ohlcv_data, basic_config)
        result = engine.run_buy_and_hold()

        assert len(result["trades"]) == 1
        trade = result["trades"][0]
        assert trade["exit_price"] == Decimal("150.00")
        assert trade["exit_reason"] == "END_OF_DATA"

    def test_fixed_amount_position_size(self, sample_ohlcv_data):
        """Test fixed amount position sizing."""
        config = {
            "strategy_name": "Fixed Amount Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("50000000.00"),  # Rp 50M
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 12),
        }
        engine = BacktestEngine(sample_ohlcv_data, config)
        result = engine.run_buy_and_hold()

        # With Rp 50M at price 100, should buy 500,000 shares
        trade = result["trades"][0]
        assert trade["position_size"] == 500000

    def test_fixed_pct_position_size(self, sample_ohlcv_data):
        """Test fixed percentage position sizing."""
        config = {
            "strategy_name": "Fixed Pct Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_PCT",
            "position_size_value": Decimal("50.00"),  # 50%
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 12),
        }
        engine = BacktestEngine(sample_ohlcv_data, config)
        result = engine.run_buy_and_hold()

        # 50% of Rp 100M = Rp 50M at price 100 = 500,000 shares
        trade = result["trades"][0]
        assert trade["position_size"] == 500000

    def test_stop_loss_triggered(self, sample_ohlcv_data):
        """Test stop loss is triggered correctly."""
        # Create data with a drop
        data_with_drop = [
            {"date": date(2024, 1, 1), "open": "100.00", "high": "110.00", "low": "95.00", "close": "105.00", "volume": 1000000},
            {"date": date(2024, 1, 2), "open": "105.00", "high": "106.00", "low": "90.00", "close": "92.00", "volume": 1200000},  # Stop loss hit (95)
            {"date": date(2024, 1, 3), "open": "92.00", "high": "95.00", "low": "88.00", "close": "90.00", "volume": 1500000},
        ]
        
        config = {
            "strategy_name": "Stop Loss Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "stop_loss_pct": 5.0,  # Stop at 95.00
            "take_profit_pct": 10.0,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 3),
        }
        engine = BacktestEngine(data_with_drop, config)
        result = engine.run_buy_and_hold()

        assert len(result["trades"]) == 1
        trade = result["trades"][0]
        assert trade["exit_reason"] == "STOP_LOSS"

    def test_take_profit_triggered(self, sample_ohlcv_data):
        """Test take profit is triggered correctly."""
        # Create data with a rise
        data_with_rise = [
            {"date": date(2024, 1, 1), "open": "100.00", "high": "115.00", "low": "95.00", "close": "110.00", "volume": 1000000},  # TP hit (110)
            {"date": date(2024, 1, 2), "open": "110.00", "high": "120.00", "low": "105.00", "close": "115.00", "volume": 1200000},
        ]
        
        config = {
            "strategy_name": "Take Profit Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,  # TP at 110.00
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 2),
        }
        engine = BacktestEngine(data_with_rise, config)
        result = engine.run_buy_and_hold()

        assert len(result["trades"]) == 1
        trade = result["trades"][0]
        assert trade["exit_reason"] == "TAKE_PROFIT"

    def test_empty_data(self):
        """Test backtest with empty data."""
        config = {
            "strategy_name": "Empty Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 1),
        }
        engine = BacktestEngine([], config)
        result = engine.run_buy_and_hold()

        assert result["trades"] == []
        assert result["total_return_pct"] == 0

    def test_equity_curve_length(self, sample_ohlcv_data, basic_config):
        """Test equity curve has correct number of data points."""
        engine = BacktestEngine(sample_ohlcv_data, basic_config)
        result = engine.run_buy_and_hold()

        assert len(result["equity_curve"]) == len(sample_ohlcv_data)

    def test_deterministic_execution(self, sample_ohlcv_data, basic_config):
        """Test same inputs produce same outputs."""
        engine1 = BacktestEngine(sample_ohlcv_data, basic_config)
        result1 = engine1.run_buy_and_hold()

        engine2 = BacktestEngine(sample_ohlcv_data, basic_config)
        result2 = engine2.run_buy_and_hold()

        assert result1["final_equity"] == result2["final_equity"]
        assert len(result1["trades"]) == len(result2["trades"])
        assert result1["total_return_pct"] == result2["total_return_pct"]

    def test_single_day_data(self):
        """Test backtest with single day of data."""
        data = [
            {"date": date(2024, 1, 1), "open": "100.00", "high": "110.00", "low": "95.00", "close": "105.00", "volume": 1000000},
        ]
        config = {
            "strategy_name": "Single Day Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 1),
        }
        engine = BacktestEngine(data, config)
        result = engine.run_buy_and_hold()

        assert len(result["trades"]) == 1
        assert result["trades"][0]["exit_reason"] == "END_OF_DATA"

    def test_insufficient_capital(self, sample_ohlcv_data):
        """Test backtest with insufficient capital."""
        config = {
            "strategy_name": "No Capital Test",
            "initial_capital": Decimal("10.00"),  # Too small
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100.00"),
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 12),
        }
        engine = BacktestEngine(sample_ohlcv_data, config)
        result = engine.run_buy_and_hold()

        # Should not enter any trades
        assert result["trades"] == []
