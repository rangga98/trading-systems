"""Unit tests for OHLCVService."""

import uuid

import pandas as pd
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ohlcv_service import OHLCVService
from app.models.stock import Stock
from app.models.ohlcv import OHLCVData


def _make_yf_df(rows: list[dict]) -> pd.DataFrame:
    """Helper to create a yfinance-style DataFrame from dict rows."""
    return pd.DataFrame([
        {
            "date": r["date"],
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "adj_close": float(r.get("adj_close", r["close"])),
            "volume": r["volume"],
        }
        for r in rows
    ])


class TestOHLCVService:
    """Test suite for OHLCVService."""

    @pytest.fixture
    async def service(self, test_db_session):
        """Create an OHLCVService instance."""
        svc = OHLCVService(test_db_session)
        return svc

    @pytest.fixture
    def sample_rows(self):
        """Sample OHLCV rows for testing."""
        return [
            {
                "date": date(2024, 1, 15),
                "open": Decimal("7500.00"),
                "high": Decimal("7650.00"),
                "low": Decimal("7480.00"),
                "close": Decimal("7600.00"),
                "adj_close": Decimal("7600.00"),
                "volume": 15000000,
            },
            {
                "date": date(2024, 1, 16),
                "open": Decimal("7600.00"),
                "high": Decimal("7700.00"),
                "low": Decimal("7550.00"),
                "close": Decimal("7650.00"),
                "adj_close": Decimal("7650.00"),
                "volume": 12000000,
            },
        ]

    # ── import_data tests ──────────────────────────────────────────

    async def test_import_data_creates_stock_and_records(self, service, test_db_session, sample_rows):
        """import_data creates the stock if missing and imports all records."""
        df = _make_yf_df(sample_rows)

        with patch.object(service.yf_client, "fetch_ohlcv", return_value=df):
            with patch.object(service.yf_client, "get_stock_info", return_value={
                "ticker": "BBCA.JK", "name": "Bank Central Asia", "sector": "Financial",
            }):
                result = await service.import_data(
                    "BBCA.JK", date(2024, 1, 1), date(2024, 1, 31), on_conflict="skip",
                )

        assert result["ticker"] == "BBCA.JK"
        assert result["records_imported"] == 2
        assert result["records_skipped"] == 0
        assert result["records_updated"] == 0

    async def test_import_data_skip_existing(self, service, test_db_session, sample_rows):
        """import_data skips existing dates when on_conflict='skip'."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="BBRI.JK", name="Bank Rakyat Indonesia")
        test_db_session.add(stock)
        existing = OHLCVData(
            stock_id=stock_id,
            date=date(2024, 1, 15),
            open=Decimal("7500.00"),
            high=Decimal("7650.00"),
            low=Decimal("7480.00"),
            close=Decimal("7600.00"),
            adj_close=Decimal("7600.00"),
            volume=15000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()

        df = _make_yf_df(sample_rows)
        with patch.object(service.yf_client, "fetch_ohlcv", return_value=df):
            result = await service.import_data(
                "BBRI.JK", date(2024, 1, 1), date(2024, 1, 31), on_conflict="skip",
            )

        assert result["records_imported"] == 1
        assert result["records_skipped"] == 1
        assert result["records_updated"] == 0

    async def test_import_data_overwrite(self, service, test_db_session, sample_rows):
        """import_data overwrites existing records when on_conflict='overwrite'."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="TLKM.JK", name="Telkom Indonesia")
        test_db_session.add(stock)
        existing = OHLCVData(
            stock_id=stock_id,
            date=date(2024, 1, 15),
            open=Decimal("4000.00"),
            high=Decimal("4100.00"),
            low=Decimal("3900.00"),
            close=Decimal("4050.00"),
            adj_close=Decimal("4050.00"),
            volume=5000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()

        df = _make_yf_df(sample_rows)
        with patch.object(service.yf_client, "fetch_ohlcv", return_value=df):
            result = await service.import_data(
                "TLKM.JK", date(2024, 1, 1), date(2024, 1, 31), on_conflict="overwrite",
            )

        assert result["records_imported"] == 2
        assert result["records_skipped"] == 0

    async def test_import_data_merge(self, service, test_db_session, sample_rows):
        """import_data merges when on_conflict='merge' — updates changed rows."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="ASII.JK", name="Astra International")
        test_db_session.add(stock)
        existing = OHLCVData(
            stock_id=stock_id,
            date=date(2024, 1, 15),
            open=Decimal("7000.00"),  # different from sample
            high=Decimal("7700.00"),
            low=Decimal("6900.00"),
            close=Decimal("7600.00"),
            adj_close=Decimal("7600.00"),
            volume=15000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()

        df = _make_yf_df(sample_rows)
        with patch.object(service.yf_client, "fetch_ohlcv", return_value=df):
            result = await service.import_data(
                "ASII.JK", date(2024, 1, 1), date(2024, 1, 31), on_conflict="merge",
            )

        assert result["records_imported"] == 1
        assert result["records_updated"] == 1

    async def test_import_data_empty_yf_response(self, service, test_db_session):
        """import_data returns zeros when yfinance returns empty DataFrame."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="UNVR.JK", name="Unilever Indonesia")
        test_db_session.add(stock)
        await test_db_session.commit()

        with patch.object(service.yf_client, "fetch_ohlcv", return_value=pd.DataFrame()):
            result = await service.import_data(
                "UNVR.JK", date(2024, 1, 1), date(2024, 1, 31),
            )

        assert result["records_imported"] == 0
        assert result["records_skipped"] == 0
        assert result["records_updated"] == 0

    # ── get_data tests ─────────────────────────────────────────────

    async def test_get_data_returns_records(self, service, test_db_session, sample_rows):
        """get_data returns OHLCVData records for a stock_id."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="ICBP.JK", name="Indofood CBP")
        test_db_session.add(stock)
        for item in sample_rows:
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                adj_close=item["adj_close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        await test_db_session.commit()

        result = await service.get_data(stock_id)
        assert len(result) == 2
        assert result[0].date == date(2024, 1, 15)
        assert result[1].date == date(2024, 1, 16)

    async def test_get_data_with_date_range(self, service, test_db_session, sample_rows):
        """get_data filters by start_date and end_date."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="PGAS.JK", name="Perusahaan Gas Negara")
        test_db_session.add(stock)
        for item in sample_rows:
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                adj_close=item["adj_close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        await test_db_session.commit()

        result = await service.get_data(
            stock_id, start_date=date(2024, 1, 15), end_date=date(2024, 1, 15),
        )
        assert len(result) == 1
        assert result[0].date == date(2024, 1, 15)

    async def test_get_data_with_limit(self, service, test_db_session, sample_rows):
        """get_data respects the limit parameter."""
        stock_id = uuid.uuid4()
        stock = Stock(id=stock_id, ticker="BMRI.JK", name="Bank Mandiri")
        test_db_session.add(stock)
        for item in sample_rows:
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                adj_close=item["adj_close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        await test_db_session.commit()

        result = await service.get_data(stock_id, limit=1)
        assert len(result) == 1
