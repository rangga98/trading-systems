"""Unit tests for OHLCVService."""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ohlcv_service import OHLCVService
from app.models.stock import Stock
from app.models.ohlcv import OHLCVData


class TestOHLCVService:
    """Test suite for OHLCVService."""

    @pytest.fixture
    def service(self, test_db_session):
        """Create an OHLCVService instance."""
        return OHLCVService(test_db_session)

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Sample OHLCV data for testing."""
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

    async def test_import_data_skip_conflict(self, service, test_db_session, sample_ohlcv_data):
        """Test import with skip conflict resolution."""
        # Create stock first
        stock = Stock(
            id="test-stock-1",
            ticker="BBCA.JK",
            name="Bank Central Asia",
            sector="Financial",
        )
        test_db_session.add(stock)
        await test_db_session.commit()
        
        # Import data
        result = await service.import_data("BBCA.JK", sample_ohlcv_data, "skip")
        
        assert result["imported"] == 2
        assert result["skipped"] == 0
        assert result["updated"] == 0

    async def test_import_data_skip_existing(self, service, test_db_session, sample_ohlcv_data):
        """Test import skips existing data when on_conflict='skip'."""
        # Create stock and existing data
        stock = Stock(
            id="test-stock-2",
            ticker="BBRI.JK",
            name="Bank Rakyat Indonesia",
            sector="Financial",
        )
        test_db_session.add(stock)
        
        existing = OHLCVData(
            stock_id="test-stock-2",
            date=date(2024, 1, 15),
            open=Decimal("7500.00"),
            high=Decimal("7650.00"),
            low=Decimal("7480.00"),
            close=Decimal("7600.00"),
            volume=15000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()
        
        # Try to import same data with skip
        result = await service.import_data("BBRI.JK", sample_ohlcv_data, "skip")
        
        assert result["imported"] == 1  # Only second record
        assert result["skipped"] == 1  # First record skipped
        assert result["updated"] == 0

    async def test_import_data_overwrite(self, service, test_db_session, sample_ohlcv_data):
        """Test import overwrites existing data when on_conflict='overwrite'."""
        # Create stock and existing data
        stock = Stock(
            id="test-stock-3",
            ticker="TLKM.JK",
            name="Telkom Indonesia",
            sector="Telecommunication",
        )
        test_db_session.add(stock)
        
        existing = OHLCVData(
            stock_id="test-stock-3",
            date=date(2024, 1, 15),
            open=Decimal("4000.00"),
            high=Decimal("4100.00"),
            low=Decimal("3900.00"),
            close=Decimal("4050.00"),
            volume=5000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()
        
        # Import with overwrite
        result = await service.import_data("TLKM.JK", sample_ohlcv_data, "overwrite")
        
        assert result["imported"] == 2
        assert result["skipped"] == 0
        # In overwrite mode, we delete all and re-import

    async def test_import_data_merge(self, service, test_db_session, sample_ohlcv_data):
        """Test import merges data when on_conflict='merge'."""
        # Create stock and existing data
        stock = Stock(
            id="test-stock-4",
            ticker="ASII.JK",
            name="Astra International",
            sector="Consumer",
        )
        test_db_session.add(stock)
        
        existing = OHLCVData(
            stock_id="test-stock-4",
            date=date(2024, 1, 15),
            open=Decimal("7000.00"),  # Different value
            high=Decimal("7650.00"),
            low=Decimal("7480.00"),
            close=Decimal("7600.00"),
            volume=15000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()
        
        # Import with merge
        result = await service.import_data("ASII.JK", sample_ohlcv_data, "merge")
        
        assert result["imported"] == 1  # Second record
        assert result["skipped"] == 0
        assert result["updated"] == 1  # First record updated

    async def test_get_data_by_ticker(self, service, test_db_session, sample_ohlcv_data):
        """Test retrieving OHLCV data by ticker."""
        # Create stock and data
        stock = Stock(
            id="test-stock-5",
            ticker="UNVR.JK",
            name="Unilever Indonesia",
            sector="Consumer",
        )
        test_db_session.add(stock)
        
        for item in sample_ohlcv_data:
            ohlcv = OHLCVData(
                stock_id="test-stock-5",
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        
        await test_db_session.commit()
        
        # Retrieve data
        result = await service.get_data_by_ticker("UNVR.JK")
        
        assert len(result) == 2
        assert result[0].date == date(2024, 1, 15)
        assert result[1].date == date(2024, 1, 16)

    async def test_get_data_with_date_range(self, service, test_db_session, sample_ohlcv_data):
        """Test retrieving OHLCV data with date range filter."""
        # Create stock and data
        stock = Stock(
            id="test-stock-6",
            ticker="ICBP.JK",
            name="Indofood CBP",
            sector="Consumer",
        )
        test_db_session.add(stock)
        
        for item in sample_ohlcv_data:
            ohlcv = OHLCVData(
                stock_id="test-stock-6",
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        
        await test_db_session.commit()
        
        # Retrieve with date range
        result = await service.get_data_by_ticker(
            "ICBP.JK",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15),
        )
        
        assert len(result) == 1
        assert result[0].date == date(2024, 1, 15)

    async def test_get_data_stock_not_found(self, service):
        """Test retrieving data for non-existent stock."""
        with pytest.raises(Exception):  # StockNotFoundException
            await service.get_data_by_ticker("INVALID.JK")

    async def test_import_data_invalid_conflict_mode(self, service, test_db_session, sample_ohlcv_data):
        """Test import with invalid conflict mode."""
        stock = Stock(
            id="test-stock-7",
            ticker="BMRI.JK",
            name="Bank Mandiri",
            sector="Financial",
        )
        test_db_session.add(stock)
        await test_db_session.commit()
        
        with pytest.raises(ValueError, match="Invalid on_conflict mode"):
            await service.import_data("BMRI.JK", sample_ohlcv_data, "invalid_mode")

    async def test_get_data_with_limit(self, service, test_db_session, sample_ohlcv_data):
        """Test retrieving OHLCV data with limit."""
        # Create stock and data
        stock = Stock(
            id="test-stock-8",
            ticker="PGAS.JK",
            name="Perusahaan Gas Negara",
            sector="Energy",
        )
        test_db_session.add(stock)
        
        for item in sample_ohlcv_data:
            ohlcv = OHLCVData(
                stock_id="test-stock-8",
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item["volume"],
            )
            test_db_session.add(ohlcv)
        
        await test_db_session.commit()
        
        # Retrieve with limit
        result = await service.get_data_by_ticker("PGAS.JK", limit=1)
        
        assert len(result) == 1
