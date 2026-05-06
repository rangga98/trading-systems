"""Export service for backtest results."""

import csv
import io
from datetime import date
from decimal import Decimal


class ExportService:
    """Service for exporting backtest results to various formats."""

    def generate_csv(self, result: dict) -> str:
        """Generate CSV export from backtest result.

        Format:
            BACKTEST SUMMARY
            Strategy Name,Buy and Hold BBCA
            Ticker,BBCA.JK
            ...

            TRADES DETAIL
            Entry Date,Entry Price,...,Exit Reason
            2020-01-02,7000.00,...,END_OF_DATA

        Args:
            result: Backtest result dictionary with config, metrics, trades

        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        config = result.get("config", {})
        metrics = result.get("metrics", {})
        trades = result.get("trades", [])

        # Summary section
        writer.writerow(["BACKTEST SUMMARY"])
        writer.writerow([])
        writer.writerow(["Strategy Name", config.get("name", "N/A")])
        writer.writerow(["Ticker", config.get("ticker", "N/A")])
        writer.writerow(["Date Range", f"{config.get('date_range_start', 'N/A')} to {config.get('date_range_end', 'N/A')}"])
        writer.writerow(["Initial Capital", f"Rp {self._format_decimal(config.get('initial_capital', 0))}"])
        writer.writerow(["Position Sizing", config.get("position_sizing_type", "N/A")])
        writer.writerow([])
        writer.writerow(["Total Return (%)", self._format_decimal(metrics.get("total_return_pct", 0))])
        writer.writerow(["Total P&L", f"Rp {self._format_decimal(metrics.get('total_pnl', 0))}"])
        writer.writerow(["Win Rate (%)", self._format_decimal(metrics.get("win_rate", 0))])
        writer.writerow(["Total Trades", metrics.get("total_trades", 0)])
        writer.writerow(["Max Drawdown (%)", self._format_decimal(metrics.get("max_drawdown_pct", 0))])
        writer.writerow(["Sharpe Ratio", self._format_decimal(metrics.get("sharpe_ratio", 0))])
        writer.writerow([])

        # Trades section
        writer.writerow(["TRADES DETAIL"])
        writer.writerow([])

        if trades:
            writer.writerow([
                "Entry Date",
                "Entry Price",
                "Exit Date",
                "Exit Price",
                "Position Size",
                "P&L",
                "P&L (%)",
                "Exit Reason",
            ])

            for trade in trades:
                writer.writerow([
                    self._format_date(trade.get("entry_date")),
                    self._format_decimal(trade.get("entry_price", 0)),
                    self._format_date(trade.get("exit_date")),
                    self._format_decimal(trade.get("exit_price", 0)),
                    trade.get("position_size", 0),
                    self._format_decimal(trade.get("pnl", 0)),
                    self._format_decimal(trade.get("pnl_pct", 0)),
                    trade.get("exit_reason", "N/A"),
                ])
        else:
            writer.writerow(["No trades executed during this backtest period"])

        return output.getvalue()

    def generate_json(self, result: dict) -> dict:
        """Generate JSON export from backtest result.

        Args:
            result: Backtest result dictionary

        Returns:
            JSON-compatible dictionary
        """
        return {
            "summary": {
                "strategy_name": result.get("config", {}).get("name"),
                "ticker": result.get("config", {}).get("ticker"),
                "date_range": {
                    "start": self._format_date(result.get("config", {}).get("date_range_start")),
                    "end": self._format_date(result.get("config", {}).get("date_range_end")),
                },
                "initial_capital": self._format_decimal(result.get("config", {}).get("initial_capital", 0)),
                "position_sizing_type": result.get("config", {}).get("position_sizing_type"),
            },
            "metrics": {
                "total_return_pct": self._format_decimal(result.get("metrics", {}).get("total_return_pct", 0)),
                "total_pnl": self._format_decimal(result.get("metrics", {}).get("total_pnl", 0)),
                "win_rate": self._format_decimal(result.get("metrics", {}).get("win_rate", 0)),
                "total_trades": result.get("metrics", {}).get("total_trades", 0),
                "max_drawdown_pct": self._format_decimal(result.get("metrics", {}).get("max_drawdown_pct", 0)),
                "sharpe_ratio": self._format_decimal(result.get("metrics", {}).get("sharpe_ratio", 0)),
            },
            "trades": [
                {
                    "entry_date": self._format_date(trade.get("entry_date")),
                    "entry_price": self._format_decimal(trade.get("entry_price", 0)),
                    "exit_date": self._format_date(trade.get("exit_date")),
                    "exit_price": self._format_decimal(trade.get("exit_price", 0)),
                    "position_size": trade.get("position_size", 0),
                    "pnl": self._format_decimal(trade.get("pnl", 0)),
                    "pnl_pct": self._format_decimal(trade.get("pnl_pct", 0)),
                    "exit_reason": trade.get("exit_reason"),
                }
                for trade in result.get("trades", [])
            ],
        }

    def generate_filename(self, result: dict, format: str = "csv") -> str:
        """Generate export filename.

        Format: backtest_{ticker}_{start_date}_{end_date}.{format}

        Args:
            result: Backtest result dictionary
            format: File format extension

        Returns:
            Filename string
        """
        config = result.get("config", {})
        ticker = config.get("ticker", "unknown").replace(".", "")
        start_date = self._format_date_for_filename(config.get("date_range_start"))
        end_date = self._format_date_for_filename(config.get("date_range_end"))

        return f"backtest_{ticker}_{start_date}_{end_date}.{format}"

    def get_content_type(self, format: str) -> str:
        """Get HTTP content type for export format.

        Args:
            format: Export format (csv, json)

        Returns:
            Content type string
        """
        content_types = {
            "csv": "text/csv",
            "json": "application/json",
        }
        return content_types.get(format, "application/octet-stream")

    def _format_decimal(self, value) -> str:
        """Format decimal value for export."""
        if value is None:
            return "0.00"
        if isinstance(value, Decimal):
            return f"{value:.2f}"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    def _format_date(self, value) -> str:
        """Format date value for export."""
        if value is None:
            return "N/A"
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def _format_date_for_filename(self, value) -> str:
        """Format date for filename (no separators)."""
        if value is None:
            return "unknown"
        if isinstance(value, date):
            return value.strftime("%Y%m%d")
        return str(value).replace("-", "")
