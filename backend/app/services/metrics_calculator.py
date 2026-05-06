"""Metrics calculator for backtest results."""

from datetime import date
from decimal import Decimal
from typing import Sequence

from app.models.trade import Trade


class MetricsCalculator:
    """Calculate performance metrics from backtest results."""

    @staticmethod
    def calculate_metrics(
        trades: Sequence[Trade],
        equity_curve: list[dict],
        initial_capital: Decimal,
    ) -> dict:
        """Calculate comprehensive performance metrics.

        Args:
            trades: List of executed trades
            equity_curve: Equity curve data points
            initial_capital: Starting capital

        Returns:
            Dictionary of performance metrics
        """
        if not trades or not equity_curve:
            return {
                "total_pnl": Decimal("0"),
                "total_return_pct": Decimal("0"),
                "win_rate": Decimal("0"),
                "total_trades": 0,
                "max_drawdown": Decimal("0"),
                "max_drawdown_pct": Decimal("0"),
                "sharpe_ratio": Decimal("0"),
            }

        # Total P&L and return
        total_pnl = sum(
            (trade.pnl or Decimal("0")) for trade in trades
        )
        total_return_pct = total_pnl / initial_capital * Decimal("100")

        # Win rate
        winning_trades = sum(
            1 for trade in trades
            if trade.pnl is not None and trade.pnl > 0
        )
        win_rate = (
            Decimal(str(winning_trades)) / Decimal(str(len(trades))) * Decimal("100")
            if trades else Decimal("0")
        )

        # Max drawdown
        max_drawdown, max_drawdown_pct = MetricsCalculator._calculate_max_drawdown(equity_curve)

        # Sharpe ratio (simplified: using daily returns)
        sharpe_ratio = MetricsCalculator._calculate_sharpe_ratio(equity_curve)

        return {
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "win_rate": win_rate,
            "total_trades": len(trades),
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
        }

    @staticmethod
    def _calculate_max_drawdown(equity_curve: list[dict]) -> tuple[Decimal, Decimal]:
        """Calculate maximum drawdown.

        Args:
            equity_curve: List of equity data points

        Returns:
            Tuple of (max_drawdown_value, max_drawdown_pct)
        """
        if not equity_curve:
            return Decimal("0"), Decimal("0")

        peak = equity_curve[0]["equity"]
        max_dd = Decimal("0")
        max_dd_pct = Decimal("0")

        for point in equity_curve:
            equity = point["equity"]
            
            if equity > peak:
                peak = equity
            
            dd = peak - equity
            dd_pct = dd / peak * Decimal("100") if peak > 0 else Decimal("0")
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct

        return max_dd, max_dd_pct

    @staticmethod
    def _calculate_sharpe_ratio(equity_curve: list[dict]) -> Decimal:
        """Calculate simplified Sharpe ratio.

        Uses daily returns and assumes risk-free rate of 0.

        Args:
            equity_curve: List of equity data points

        Returns:
            Sharpe ratio
        """
        if len(equity_curve) < 2:
            return Decimal("0")

        # Calculate daily returns
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i - 1]["equity"]
            curr_equity = equity_curve[i]["equity"]
            
            if prev_equity > 0:
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(float(daily_return))

        if not returns:
            return Decimal("0")

        # Calculate mean and standard deviation
        import statistics
        
        mean_return = statistics.mean(returns)
        
        if len(returns) < 2:
            std_dev = 0
        else:
            std_dev = statistics.stdev(returns)

        if std_dev == 0:
            return Decimal("0")

        # Annualized Sharpe ratio (assuming 252 trading days)
        sharpe = mean_return / std_dev * (252 ** 0.5)
        
        return Decimal(str(sharpe))
