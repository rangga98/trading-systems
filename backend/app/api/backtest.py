"""Backtest API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.database import get_db
from app.schemas.backtest import (
    BacktestConfigCreate,
    BacktestConfigList,
    BacktestConfigResponse,
    BacktestConfigUpdate,
    BacktestExecuteResponse,
    BacktestResultDetail,
    BacktestResultList,
    BacktestResultResponse,
)
from app.services.backtest_service import BacktestService

router = APIRouter(tags=["backtest"])


@router.post("/backtests", response_model=BacktestConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    request: BacktestConfigCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new backtest configuration."""
    service = BacktestService(session)
    config = await service.create_config(request.model_dump())
    return config


@router.get("/backtests", response_model=BacktestConfigList)
async def list_configs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List backtest configurations."""
    service = BacktestService(session)
    configs, total = await service.list_configs(limit=limit, offset=offset)
    return BacktestConfigList(
        total=total,
        items=[BacktestConfigResponse.model_validate(c) for c in configs],
    )


@router.get("/backtests/results", response_model=BacktestResultList)
async def list_results(
    config_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List backtest results."""
    service = BacktestService(session)
    results, total = await service.list_results(
        config_id=config_id,
        limit=limit,
        offset=offset,
    )
    return BacktestResultList(
        total=total,
        items=[BacktestResultResponse.model_validate(r) for r in results],
    )


@router.get("/backtests/{config_id}", response_model=BacktestConfigResponse)
async def get_config(
    config_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a backtest configuration by ID."""
    service = BacktestService(session)
    config = await service.get_config(config_id)
    return config


@router.patch("/backtests/{config_id}", response_model=BacktestConfigResponse)
async def update_config(
    config_id: UUID,
    request: BacktestConfigUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update a backtest configuration."""
    service = BacktestService(session)
    config = await service.update_config(config_id, request.model_dump(exclude_unset=True))
    return config


@router.delete("/backtests/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Delete a backtest configuration."""
    service = BacktestService(session)
    await service.delete_config(config_id)
    return None


@router.post("/backtests/{config_id}/execute", response_model=BacktestExecuteResponse)
async def execute_backtest(
    config_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Execute a backtest."""
    service = BacktestService(session)
    
    try:
        result = await service.execute(config_id)
        return BacktestExecuteResponse(
            status=result.status,
            result_id=result.id,
        )
    except NotFoundException as e:
        logger.warning(f"Backtest execution failed: {e}")
        return BacktestExecuteResponse(
            status="FAILED",
            message=str(e),
        )


@router.get("/backtests/results/{result_id}", response_model=BacktestResultDetail)
async def get_result(
    result_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get a backtest result with trades."""
    service = BacktestService(session)
    result = await service.get_result(result_id)
    
    return BacktestResultDetail(
        id=result.id,
        config_id=result.config_id,
        status=result.status,
        total_pnl=str(result.total_pnl) if result.total_pnl else None,
        total_return_pct=result.total_return_pct,
        win_rate=result.win_rate,
        total_trades=result.total_trades,
        max_drawdown=str(result.max_drawdown) if result.max_drawdown else None,
        max_drawdown_pct=result.max_drawdown_pct,
        sharpe_ratio=result.sharpe_ratio,
        equity_curve=result.equity_curve,
        executed_at=result.executed_at,
        completed_at=result.completed_at,
        error_message=result.error_message,
        created_at=result.created_at,
        trades=[
            {
                "id": t.id,
                "entry_date": t.entry_date,
                "entry_price": str(t.entry_price),
                "exit_date": t.exit_date,
                "exit_price": str(t.exit_price) if t.exit_price else None,
                "position_size": t.position_size,
                "position_type": t.position_type,
                "pnl": str(t.pnl) if t.pnl else None,
                "pnl_pct": t.pnl_pct,
                "exit_reason": t.exit_reason,
            }
            for t in result.trades
        ],
    )
