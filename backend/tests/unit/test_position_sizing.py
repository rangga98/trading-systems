"""Unit tests for position sizing strategies."""

import pytest
from decimal import Decimal

from app.services.backtest_engine import BacktestEngine


class TestPositionSizing:
    """Test suite for position sizing strategies."""

    @pytest.fixture
    def sample_data(self):
        """Sample OHLCV data."""
        from datetime import date
        return [
            {"date": date(2024, 1, 1), "open": "100.00", "high": "110.00", "low": "95.00", "close": "105.00", "volume": 1000000},
            {"date": date(2024, 1, 2), "open": "105.00", "high": "115.00", "low": "100.00", "close": "110.00", "volume": 1200000},
        ]

    def test_fixed_amount_full_capital(self, sample_data):
        """Test FIXED_AMOUNT with full capital."""
        config = {
            "strategy_name": "Fixed Amount Full",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # Rp 100M / 100 = 1,000,000 shares
        assert trade["position_size"] == 1000000

    def test_fixed_amount_partial_capital(self, sample_data):
        """Test FIXED_AMOUNT with partial capital."""
        config = {
            "strategy_name": "Fixed Amount Partial",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("25000000.00"),  # Rp 25M
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # Rp 25M / 100 = 250,000 shares
        assert trade["position_size"] == 250000

    def test_fixed_amount_exceeds_capital(self, sample_data):
        """Test FIXED_AMOUNT exceeding available capital."""
        config = {
            "strategy_name": "Fixed Amount Exceeds",
            "initial_capital": Decimal("50000000.00"),  # Rp 50M
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("100000000.00"),  # Rp 100M
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        # Should use available capital: Rp 50M / 100 = 500,000 shares
        trade = result["trades"][0]
        assert trade["position_size"] == 500000

    def test_fixed_pct_full(self, sample_data):
        """Test FIXED_PCT with 100%."""
        config = {
            "strategy_name": "Fixed Pct Full",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_PCT",
            "position_size_value": Decimal("100.00"),  # 100%
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # 100% of Rp 100M = Rp 100M / 100 = 1,000,000 shares
        assert trade["position_size"] == 1000000

    def test_fixed_pct_half(self, sample_data):
        """Test FIXED_PCT with 50%."""
        config = {
            "strategy_name": "Fixed Pct Half",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_PCT",
            "position_size_value": Decimal("50.00"),  # 50%
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # 50% of Rp 100M = Rp 50M / 100 = 500,000 shares
        assert trade["position_size"] == 500000

    def test_fixed_pct_quarter(self, sample_data):
        """Test FIXED_PCT with 25%."""
        config = {
            "strategy_name": "Fixed Pct Quarter",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_PCT",
            "position_size_value": Decimal("25.00"),  # 25%
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # 25% of Rp 100M = Rp 25M / 100 = 250,000 shares
        assert trade["position_size"] == 250000

    def test_risk_based_position_size(self, sample_data):
        """Test RISK_BASED position sizing."""
        config = {
            "strategy_name": "Risk Based Test",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "RISK_BASED",
            "position_size_value": Decimal("2.00"),  # Risk 2% of capital
            "stop_loss_pct": 5.0,
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        trade = result["trades"][0]
        # Risk = 2% of Rp 100M = Rp 2M
        # Risk per share = 5% of 100 = 5
        # Position size = Rp 2M / 5 = 400,000 shares
        assert trade["position_size"] == 400000

    def test_risk_based_with_stop_loss(self, sample_data):
        """Test RISK_BASED requires stop loss."""
        config = {
            "strategy_name": "Risk Based No SL",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "RISK_BASED",
            "position_size_value": Decimal("2.00"),
            # No stop_loss_pct - should use default or fail gracefully
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        # Should still execute with default stop loss
        assert len(result["trades"]) == 1

    def test_zero_position_size(self, sample_data):
        """Test backtest with zero position size value."""
        config = {
            "strategy_name": "Zero Size",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": Decimal("0.00"),
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        engine = BacktestEngine(sample_data, config)
        result = engine.run_buy_and_hold()

        # Should not enter any trades
        assert result["trades"] == []

    def test_invalid_position_sizing_type(self, sample_data):
        """Test invalid position sizing type."""
        config = {
            "strategy_name": "Invalid Type",
            "initial_capital": Decimal("100000000.00"),
            "position_sizing_type": "INVALID_TYPE",
            "position_size_value": Decimal("100000000.00"),
            "start_date": sample_data[0]["date"],
            "end_date": sample_data[-1]["date"],
        }
        
        with pytest.raises(ValueError, match="Invalid position sizing type"):
            engine = BacktestEngine(sample_data, config)
            engine.run_buy_and_hold()
