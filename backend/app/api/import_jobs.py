"""Import job tracking API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.database import get_db
from app.schemas.ohlcv import ImportJobResponse
from app.services.import_job_service import ImportJobService

router = APIRouter(prefix="/import-jobs", tags=["import-jobs"])


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    """Get import job status by ID."""
    service = ImportJobService(session)
    job = await service.get_by_id(job_id)
    return ImportJobResponse.model_validate(job)
