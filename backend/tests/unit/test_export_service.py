"""Unit tests for ExportService."""

import pytest
import csv
import io
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from app.services.export_service import ExportService


class TestExportService:
    """Test suite for ExportService."""

    @pytest.fixture
    def sample_backtest_result(self):
        """Sample backtest result data for export testing."""
        return {
            "id": str(uuid4()),
            "config": {
                "name": "Buy and Hold BBCA",
                "ticker": "BBCA.JK",
                "initial_capital": Decimal("100000000.00"),
                "position_sizing_type": "FIXED_AMOUNT",
                "position_size_value": Decimal("100000000.00"),
                "date_range_start": date(2020, 1, 2),
                "date_range_end": date(2024, 12, 30),
            },
            "metrics": {
                "total_pnl": Decimal("45000000.00"),
                "total_return_pct": Decimal("45.00"),
                "win_rate": Decimal("100.00"),
                "total_trades": 1,
                "max_drawdown": Decimal("5000000.00"),
                "max_drawdown_pct": Decimal("5.00"),
                "sharpe_ratio": Decimal("1.25"),
            },
            "trades": [
                {
                    "entry_date": date(2020, 1, 2),
                    "entry_price": Decimal("7000.00"),
                    "exit_date": date(2024, 12, 30),
                    "exit_price": Decimal("10150.00"),
                    "position_size": 14285,
                    "position_type": "LONG",
                    "pnl": Decimal("45009750.00"),
                    "pnl_pct": Decimal("45.00"),
                    "exit_reason": "END_OF_DATA",
                }
            ],
        }

    def test_generate_csv_summary_section(self, sample_backtest_result):
        """Test CSV contains summary header section."""
        service = ExportService()
        csv_content = service.generate_csv(sample_backtest_result)

        # Parse CSV
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # First row should be BACKTEST SUMMARY
        assert rows[0][0] == "BACKTEST SUMMARY"
        
        # Should have summary data
        summary_labels = [row[0] for row in rows[:10]]
        assert "Strategy Name" in summary_labels
        assert "Ticker" in summary_labels
        assert "Initial Capital" in summary_labels
        assert "Total Return (%)" in summary_labels
        assert "Total P&L" in summary_labels
        assert "Win Rate (%)" in summary_labels
        assert "Max Drawdown (%)" in summary_labels
        assert "Sharpe Ratio" in summary_labels

    def test_generate_csv_trades_section(self, sample_backtest_result):
        """Test CSV contains trades detail section."""
        service = ExportService()
        csv_content = service.generate_csv(sample_backtest_result)

        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # Find TRADES DETAIL section
        trade_section_idx = None
        for i, row in enumerate(rows):
            if row and row[0] == "TRADES DETAIL":
                trade_section_idx = i
                break
        
        assert trade_section_idx is not None
        
        # Next row should be headers
        headers = rows[trade_section_idx + 1]
        assert "Entry Date" in headers
        assert "Entry Price" in headers
        assert "Exit Date" in headers
        assert "Exit Price" in headers
        assert "Position Size" in headers
        assert "P&L" in headers
        assert "P&L (%)" in headers
        assert "Exit Reason" in headers

    def test_generate_csv_trade_data(self, sample_backtest_result):
        """Test CSV contains correct trade data."""
        service = ExportService()
        csv_content = service.generate_csv(sample_backtest_result)

        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # Find TRADES DETAIL section and get data rows
        trade_data_start = None
        for i, row in enumerate(rows):
            if row and row[0] == "Entry Date":
                trade_data_start = i + 1
                break
        
        assert trade_data_start is not None
        
        # Check trade data
        trade_row = rows[trade_data_start]
        assert trade_row[0] == "2020-01-02"  # Entry Date
        assert trade_row[1] == "7000.00"      # Entry Price
        assert trade_row[2] == "2024-12-30"   # Exit Date
        assert trade_row[3] == "10150.00"     # Exit Price
        assert trade_row[4] == "14285"        # Position Size
        assert trade_row[6] == "45.00"        # P&L %
        assert trade_row[7] == "END_OF_DATA"  # Exit Reason

    def test_generate_csv_empty_trades(self):
        """Test CSV generation with no trades."""
        result = {
            "id": str(uuid4()),
            "config": {
                "name": "No Trades Test",
                "ticker": "TEST.JK",
                "initial_capital": Decimal("100000000.00"),
                "position_sizing_type": "FIXED_AMOUNT",
                "position_size_value": Decimal("100000000.00"),
                "date_range_start": date(2020, 1, 2),
                "date_range_end": date(2024, 12, 30),
            },
            "metrics": {
                "total_pnl": Decimal("0.00"),
                "total_return_pct": Decimal("0.00"),
                "win_rate": Decimal("0.00"),
                "total_trades": 0,
                "max_drawdown": Decimal("0.00"),
                "max_drawdown_pct": Decimal("0.00"),
                "sharpe_ratio": Decimal("0.00"),
            },
            "trades": [],
        }

        service = ExportService()
        csv_content = service.generate_csv(result)

        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # Should still have summary
        assert rows[0][0] == "BACKTEST SUMMARY"
        
        # Should have trades section with "No trades" message
        trade_section_idx = None
        for i, row in enumerate(rows):
            if row and row[0] == "TRADES DETAIL":
                trade_section_idx = i
                break
        
        assert trade_section_idx is not None
        
        # Next row should indicate no trades
        assert "No trades" in str(rows[trade_section_idx + 1])

    def test_generate_csv_multiple_trades(self):
        """Test CSV with multiple trades."""
        result = {
            "id": str(uuid4()),
            "config": {
                "name": "Multi Trade Test",
                "ticker": "BBRI.JK",
                "initial_capital": Decimal("100000000.00"),
                "position_sizing_type": "FIXED_AMOUNT",
                "position_size_value": Decimal("50000000.00"),
                "date_range_start": date(2020, 1, 2),
                "date_range_end": date(2024, 12, 30),
            },
            "metrics": {
                "total_pnl": Decimal("25000000.00"),
                "total_return_pct": Decimal("25.00"),
                "win_rate": Decimal("66.67"),
                "total_trades": 3,
                "max_drawdown": Decimal("8000000.00"),
                "max_drawdown_pct": Decimal("8.00"),
                "sharpe_ratio": Decimal("0.85"),
            },
            "trades": [
                {
                    "entry_date": date(2020, 1, 2),
                    "entry_price": Decimal("4000.00"),
                    "exit_date": date(2020, 6, 1),
                    "exit_price": Decimal("4500.00"),
                    "position_size": 12500,
                    "position_type": "LONG",
                    "pnl": Decimal("6250000.00"),
                    "pnl_pct": Decimal("12.50"),
                    "exit_reason": "TAKE_PROFIT",
                },
                {
                    "entry_date": date(2020, 6, 2),
                    "entry_price": Decimal("4600.00"),
                    "exit_date": date(2020, 9, 1),
                    "exit_price": Decimal("4100.00"),
                    "position_size": 10869,
                    "position_type": "LONG",
                    "pnl": Decimal("-5434500.00"),
                    "pnl_pct": Decimal("-10.87"),
                    "exit_reason": "STOP_LOSS",
                },
                {
                    "entry_date": date(2020, 9, 2),
                    "entry_price": Decimal("4200.00"),
                    "exit_date": date(2024, 12, 30),
                    "exit_price": Decimal("6500.00"),
                    "position_size": 11904,
                    "position_type": "LONG",
                    "pnl": Decimal("27379200.00"),
                    "pnl_pct": Decimal("54.76"),
                    "exit_reason": "END_OF_DATA",
                },
            ],
        }

        service = ExportService()
        csv_content = service.generate_csv(result)

        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)

        # Find trade data
        trade_data_start = None
        for i, row in enumerate(rows):
            if row and row[0] == "Entry Date":
                trade_data_start = i + 1
                break
        
        assert trade_data_start is not None
        
        # Should have 3 trade rows
        trade_rows = []
        for row in rows[trade_data_start:]:
            if row and row[0] and not row[0].startswith("BACKTEST"):
                trade_rows.append(row)
        
        assert len(trade_rows) == 3
        
        # Check first trade
        assert trade_rows[0][0] == "2020-01-02"
        assert trade_rows[0][3] == "4500.00"
        assert trade_rows[0][7] == "TAKE_PROFIT"
        
        # Check second trade (loss)
        assert trade_rows[1][5] == "-5434500.00"
        assert trade_rows[1][6] == "-10.87"
        assert trade_rows[1][7] == "STOP_LOSS"

    def test_csv_filename_generation(self):
        """Test CSV filename generation."""
        service = ExportService()
        
        result = {
            "config": {
                "ticker": "BBCA.JK",
                "date_range_start": date(2020, 1, 2),
                "date_range_end": date(2024, 12, 30),
            }
        }
        
        filename = service.generate_filename(result)
        
        assert "backtest" in filename
        assert "BBCA" in filename
        assert "20200102" in filename
        assert "20241230" in filename
        assert filename.endswith(".csv")

    def test_csv_content_type(self):
        """Test CSV content type is correct."""
        service = ExportService()
        
        result = {
            "id": str(uuid4()),
            "config": {
                "name": "Test",
                "ticker": "TEST.JK",
                "initial_capital": Decimal("100000000.00"),
                "position_sizing_type": "FIXED_AMOUNT",
                "position_size_value": Decimal("100000000.00"),
                "date_range_start": date(2020, 1, 2),
                "date_range_end": date(2024, 12, 30),
            },
            "metrics": {
                "total_pnl": Decimal("0.00"),
                "total_return_pct": Decimal("0.00"),
                "win_rate": Decimal("0.00"),
                "total_trades": 0,
                "max_drawdown": Decimal("0.00"),
                "max_drawdown_pct": Decimal("0.00"),
                "sharpe_ratio": Decimal("0.00"),
            },
            "trades": [],
        }
        
        content_type = service.get_content_type("csv")
        assert content_type == "text/csv"
