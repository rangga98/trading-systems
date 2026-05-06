"""Backtest engine for simulating trading strategies."""

from datetime import date
from decimal import Decimal
from typing import Literal

PositionSizingType = Literal["FIXED_AMOUNT", "FIXED_PCT", "RISK_BASED"]


class BacktestEngine:
    """Deterministic backtest engine for trading simulation."""

    def __init__(self, ohlcv_data: list[dict], config: dict):
        """Initialize the backtest engine.

        Args:
            ohlcv_data: List of OHLCV data points
            config: Backtest configuration dictionary
        """
        self.data = ohlcv_data
        self.config = config
        self.initial_capital = Decimal(str(config["initial_capital"]))
        self.position_sizing_type = config["position_sizing_type"]
        self.position_size_value = Decimal(str(config["position_size_value"]))
        self.stop_loss_pct = Decimal(str(config.get("stop_loss_pct", 0) or 0))
        self.take_profit_pct = Decimal(str(config.get("take_profit_pct", 0) or 0))

    def run_buy_and_hold(self) -> dict:
        """Run a buy-and-hold strategy simulation.

        Returns:
            Dictionary with trades, equity curve, and metrics
        """
        if not self.data:
            return {
                "trades": [],
                "equity_curve": [],
                "final_equity": self.initial_capital,
                "total_return_pct": Decimal("0"),
            }

        trades = []
        equity_curve = []
        cash = self.initial_capital
        position = None

        for i, row in enumerate(self.data):
            current_date = row["date"]
            current_open = Decimal(str(row["open"]))
            current_high = Decimal(str(row["high"]))
            current_low = Decimal(str(row["low"]))
            current_close = Decimal(str(row["close"]))

            # Calculate position size on first day
            if i == 0 and position is None:
                position_size = self._calculate_position_size(current_open)
                
                if position_size > 0:
                    cost = position_size * current_open
                    if cost <= cash:
                        cash -= cost
                        position = {
                            "entry_date": current_date,
                            "entry_price": current_open,
                            "position_size": position_size,
                            "position_type": "LONG",
                            "stop_loss": current_open * (Decimal("1") - self.stop_loss_pct / Decimal("100")) if self.stop_loss_pct > 0 else None,
                            "take_profit": current_open * (Decimal("1") + self.take_profit_pct / Decimal("100")) if self.take_profit_pct > 0 else None,
                        }

            # Check for exit conditions
            exit_reason = None
            exit_price = None
            
            if position:
                # Check stop loss
                if position["stop_loss"] and current_low <= position["stop_loss"]:
                    exit_reason = "STOP_LOSS"
                    exit_price = position["stop_loss"]
                
                # Check take profit
                elif position["take_profit"] and current_high >= position["take_profit"]:
                    exit_reason = "TAKE_PROFIT"
                    exit_price = position["take_profit"]
                
                # Exit at end of data
                elif i == len(self.data) - 1:
                    exit_reason = "END_OF_DATA"
                    exit_price = current_close

                if exit_reason:
                    # Close position
                    pnl = (exit_price - position["entry_price"]) * position["position_size"]
                    cash += position["entry_price"] * position["position_size"] + pnl
                    
                    trades.append({
                        "entry_date": position["entry_date"],
                        "entry_price": position["entry_price"],
                        "exit_date": current_date,
                        "exit_price": exit_price,
                        "position_size": position["position_size"],
                        "position_type": position["position_type"],
                        "pnl": pnl,
                        "pnl_pct": (exit_price - position["entry_price"]) / position["entry_price"] * Decimal("100"),
                        "exit_reason": exit_reason,
                    })
                    position = None

            # Calculate equity
            equity = cash
            if position:
                equity += position["position_size"] * current_close
            
            equity_curve.append({
                "date": current_date,
                "equity": equity,
            })

        final_equity = equity_curve[-1]["equity"] if equity_curve else self.initial_capital
        total_return_pct = (final_equity - self.initial_capital) / self.initial_capital * Decimal("100")

        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_equity": final_equity,
            "total_return_pct": total_return_pct,
        }

    def _calculate_position_size(self, price: Decimal) -> int:
        """Calculate position size based on sizing strategy.

        Args:
            price: Current price

        Returns:
            Number of shares to buy
        """
        if price <= 0:
            return 0

        if self.position_sizing_type == "FIXED_AMOUNT":
            amount = min(self.position_size_value, self.initial_capital)
            return int(amount // price)

        elif self.position_sizing_type == "FIXED_PCT":
            amount = self.initial_capital * self.position_size_value / Decimal("100")
            amount = min(amount, self.initial_capital)
            return int(amount // price)

        elif self.position_sizing_type == "RISK_BASED":
            # Risk-based: risk X% of capital per trade
            # Position size = (capital * risk_pct) / (price * stop_loss_pct)
            risk_amount = self.initial_capital * self.position_size_value / Decimal("100")
            
            if self.stop_loss_pct > 0:
                risk_per_share = price * self.stop_loss_pct / Decimal("100")
                if risk_per_share > 0:
                    return int(risk_amount // risk_per_share)
            
            # Fallback to fixed amount if no stop loss
            return int(self.initial_capital // price)

        else:
            raise ValueError(f"Invalid position sizing type: {self.position_sizing_type}")
