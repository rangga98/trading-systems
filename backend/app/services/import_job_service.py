"""Import job service for tracking async operations."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.import_job import ImportJob


class ImportJobService:
    """Service for import job management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> ImportJob:
        """Create a new import job."""
        job = ImportJob(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            status="PENDING",
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: UUID) -> ImportJob:
        """Get import job by ID."""
        result = await self.session.execute(
            select(ImportJob).where(
                ImportJob.id == job_id,
                ImportJob.deleted_at.is_(None)
            )
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise NotFoundException(f"Import job '{job_id}' not found")
        
        return job

    async def update_status(
        self,
        job_id: UUID,
        status: str,
        records_imported: int = 0,
        records_skipped: int = 0,
        records_updated: int = 0,
        error_message: str | None = None,
    ) -> ImportJob:
        """Update import job status."""
        job = await self.get_by_id(job_id)
        
        job.status = status
        job.records_imported = records_imported
        job.records_skipped = records_skipped
        job.records_updated = records_updated
        if error_message:
            job.error_message = error_message
        
        await self.session.commit()
        await self.session.refresh(job)
        return job
