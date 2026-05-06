"""Backtest service for managing configurations and execution."""

from datetime import date, datetime
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.models.backtest_config import BacktestConfig
from app.models.backtest_result import BacktestResult
from app.models.trade import Trade
from app.services.backtest_engine import BacktestEngine
from app.services.metrics_calculator import MetricsCalculator
from app.services.ohlcv_service import OHLCVService
from app.services.stock_service import StockService


class BacktestService:
    """Service for backtest configuration and execution."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Configuration CRUD
    async def create_config(self, data: dict) -> BacktestConfig:
        """Create a new backtest configuration."""
        config = BacktestConfig(
            name=data["name"],
            ticker=data["ticker"],
            initial_capital=Decimal(str(data["initial_capital"])),
            position_sizing_type=data["position_sizing_type"],
            position_size_value=Decimal(str(data["position_size_value"])),
            stop_loss_pct=Decimal(str(data["stop_loss_pct"])) if data.get("stop_loss_pct") else None,
            take_profit_pct=Decimal(str(data["take_profit_pct"])) if data.get("take_profit_pct") else None,
            entry_rules=data.get("entry_rules", {}),
            exit_rules=data.get("exit_rules", {}),
            date_range_start=data["date_range_start"],
            date_range_end=data["date_range_end"],
        )
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        logger.info(f"Created backtest config: {config.id} - {config.name}")
        return config

    async def list_configs(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[BacktestConfig], int]:
        """List backtest configurations."""
        # Get total count
        count_result = await self.session.execute(
            select(BacktestConfig).where(BacktestConfig.deleted_at.is_(None))
        )
        all_configs = count_result.scalars().all()
        total = len(all_configs)

        # Get paginated results
        result = await self.session.execute(
            select(BacktestConfig)
            .where(BacktestConfig.deleted_at.is_(None))
            .order_by(BacktestConfig.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        configs = result.scalars().all()
        return configs, total

    async def get_config(self, config_id: UUID) -> BacktestConfig:
        """Get a backtest configuration by ID."""
        result = await self.session.execute(
            select(BacktestConfig)
            .where(
                BacktestConfig.id == config_id,
                BacktestConfig.deleted_at.is_(None),
            )
        )
        config = result.scalar_one_or_none()
        if not config:
            raise NotFoundException(f"Backtest config not found: {config_id}")
        return config

    async def update_config(self, config_id: UUID, data: dict) -> BacktestConfig:
        """Update a backtest configuration."""
        config = await self.get_config(config_id)
        
        for field, value in data.items():
            if value is not None and hasattr(config, field):
                if field in ["initial_capital", "position_size_value", "stop_loss_pct", "take_profit_pct"]:
                    setattr(config, field, Decimal(str(value)))
                else:
                    setattr(config, field, value)
        
        config.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(config)
        logger.info(f"Updated backtest config: {config_id}")
        return config

    async def delete_config(self, config_id: UUID) -> None:
        """Soft delete a backtest configuration."""
        config = await self.get_config(config_id)
        config.deleted_at = datetime.now()
        await self.session.commit()
        logger.info(f"Deleted backtest config: {config_id}")

    # Result operations
    async def list_results(
        self,
        config_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[BacktestResult], int]:
        """List backtest results."""
        query = select(BacktestResult).where(BacktestResult.deleted_at.is_(None))
        
        if config_id:
            query = query.where(BacktestResult.config_id == config_id)
        
        # Get total
        count_result = await self.session.execute(query)
        total = len(count_result.scalars().all())
        
        # Get paginated
        result = await self.session.execute(
            query.order_by(BacktestResult.executed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all(), total

    async def get_result(self, result_id: UUID) -> BacktestResult:
        """Get a backtest result with trades."""
        result = await self.session.execute(
            select(BacktestResult)
            .where(
                BacktestResult.id == result_id,
                BacktestResult.deleted_at.is_(None),
            )
        )
        backtest_result = result.scalar_one_or_none()
        if not backtest_result:
            raise NotFoundException(f"Backtest result not found: {result_id}")
        return backtest_result

    # Execution
    async def execute(self, config_id: UUID) -> BacktestResult:
        """Execute a backtest."""
        config = await self.get_config(config_id)
        
        # Create result record
        result = BacktestResult(
            config_id=config_id,
            status="RUNNING",
            executed_at=datetime.now(),
        )
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        
        try:
            # Get stock and OHLCV data
            stock_service = StockService(self.session)
            stock = await stock_service.get_by_ticker(config.ticker)
            
            ohlcv_service = OHLCVService(self.session)
            ohlcv_data = await ohlcv_service.get_data_with_timeframe(
                stock_id=stock.id,
                start_date=config.date_range_start,
                end_date=config.date_range_end,
                timeframe="daily",
                limit=5000,
            )
            
            raw_data = ohlcv_data["data"]
            if not raw_data:
                # No data for period - complete with empty results
                result.status = "COMPLETED"
                result.completed_at = datetime.now()
                result.total_trades = 0
                await self.session.commit()
                return result
            
            # Convert data for engine
            engine_data = [
                {
                    "date": item["date"] if isinstance(item["date"], date) else datetime.strptime(item["date"], "%Y-%m-%d").date(),
                    "open": item["open"],
                    "high": item["high"],
                    "low": item["low"],
                    "close": item["close"],
                    "volume": item["volume"],
                }
                for item in raw_data
            ]
            
            # Prepare config for engine
            engine_config = {
                "strategy_name": config.name,
                "initial_capital": config.initial_capital,
                "position_sizing_type": config.position_sizing_type,
                "position_size_value": config.position_size_value,
                "stop_loss_pct": float(config.stop_loss_pct) if config.stop_loss_pct else None,
                "take_profit_pct": float(config.take_profit_pct) if config.take_profit_pct else None,
                "start_date": config.date_range_start,
                "end_date": config.date_range_end,
            }
            
            # Run backtest
            engine = BacktestEngine(engine_data, engine_config)
            engine_result = engine.run_buy_and_hold()
            
            # Create trades
            trades = []
            for trade_data in engine_result["trades"]:
                trade = Trade(
                    result_id=result.id,
                    entry_date=trade_data["entry_date"],
                    entry_price=trade_data["entry_price"],
                    exit_date=trade_data.get("exit_date"),
                    exit_price=trade_data.get("exit_price"),
                    position_size=trade_data["position_size"],
                    position_type=trade_data["position_type"],
                    pnl=trade_data.get("pnl"),
                    pnl_pct=trade_data.get("pnl_pct"),
                    exit_reason=trade_data.get("exit_reason"),
                )
                trades.append(trade)
                self.session.add(trade)
            
            # Calculate metrics
            equity_curve = engine_result["equity_curve"]
            # Convert date objects to strings for JSON serialization
            equity_curve_serializable = [
                {
                    "date": p["date"].isoformat() if isinstance(p["date"], date) else p["date"],
                    "equity": float(p["equity"]),
                }
                for p in equity_curve
            ]
            metrics = MetricsCalculator.calculate_metrics(
                trades=[t for t in trades],  # Already Trade objects
                equity_curve=equity_curve,
                initial_capital=config.initial_capital,
            )
            
            # Update result
            result.status = "COMPLETED"
            result.completed_at = datetime.now()
            result.total_pnl = metrics["total_pnl"]
            result.total_return_pct = metrics["total_return_pct"]
            result.win_rate = metrics["win_rate"]
            result.total_trades = metrics["total_trades"]
            result.max_drawdown = metrics["max_drawdown"]
            result.max_drawdown_pct = metrics["max_drawdown_pct"]
            result.sharpe_ratio = metrics["sharpe_ratio"]
            result.equity_curve = equity_curve_serializable
            
            await self.session.commit()
            await self.session.refresh(result)
            
            logger.info(
                f"Backtest completed: {result.id} - "
                f"Return: {result.total_return_pct}%, "
                f"Trades: {result.total_trades}"
            )
            
            return result
            
        except Exception as e:
            result.status = "FAILED"
            result.completed_at = datetime.now()
            result.error_message = str(e)
            await self.session.commit()
            logger.error(f"Backtest failed: {result.id} - {e}")
            raise
