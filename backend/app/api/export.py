"""Export API routes for backtest results."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.database import get_db
from app.services.backtest_service import BacktestService
from app.services.export_service import ExportService

router = APIRouter(tags=["export"])


@router.get("/backtests/results/{result_id}/export")
async def export_result(
    result_id: UUID,
    format: str = Query("csv", pattern=r"^(csv|json)$"),
    session: AsyncSession = Depends(get_db),
):
    """Export backtest result in CSV or JSON format.

    Args:
        result_id: Backtest result UUID
        format: Export format (csv or json)
        session: Database session

    Returns:
        File download response
    """
    # Get backtest result
    backtest_service = BacktestService(session)
    try:
        result = await backtest_service.get_result(result_id)
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest result not found: {result_id}",
        )

    # Build result data for export
    result_data = {
        "id": result.id,
        "config": {
            "name": result.config.name if result.config else "Unknown",
            "ticker": result.config.ticker if result.config else "Unknown",
            "initial_capital": result.config.initial_capital if result.config else 0,
            "position_sizing_type": result.config.position_sizing_type if result.config else "N/A",
            "position_size_value": result.config.position_size_value if result.config else 0,
            "date_range_start": result.config.date_range_start if result.config else None,
            "date_range_end": result.config.date_range_end if result.config else None,
        },
        "metrics": {
            "total_pnl": result.total_pnl,
            "total_return_pct": result.total_return_pct,
            "win_rate": result.win_rate,
            "total_trades": result.total_trades,
            "max_drawdown": result.max_drawdown,
            "max_drawdown_pct": result.max_drawdown_pct,
            "sharpe_ratio": result.sharpe_ratio,
        },
        "trades": [
            {
                "entry_date": trade.entry_date,
                "entry_price": trade.entry_price,
                "exit_date": trade.exit_date,
                "exit_price": trade.exit_price,
                "position_size": trade.position_size,
                "position_type": trade.position_type,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "exit_reason": trade.exit_reason,
            }
            for trade in result.trades
        ],
    }

    # Generate export
    export_service = ExportService()

    if format == "csv":
        content = export_service.generate_csv(result_data)
        filename = export_service.generate_filename(result_data, "csv")
        content_type = export_service.get_content_type("csv")
    else:  # json
        content = export_service.generate_json(result_data)
        import json
        content = json.dumps(content, indent=2, default=str)
        filename = export_service.generate_filename(result_data, "json")
        content_type = export_service.get_content_type("json")

    logger.info(f"Exported backtest result {result_id} as {format}: {filename}")

    # Return as file download
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }

    return Response(
        content=content,
        media_type=content_type,
        headers=headers,
    )
