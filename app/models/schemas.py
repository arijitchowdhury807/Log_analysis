from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):

    PENDING = "PENDING"

    PROCESSING = "PROCESSING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"


class AnalysisResponse(BaseModel):

    lines_processed: int = Field(
        ge=0
    )

    unparseable_lines: int = Field(
        ge=0
    )

    error_counts: dict[str, int]

    top_offender: Optional[str] = None

    processing_time_ms: float = Field(
        ge=0
    )


class JobCreateResponse(BaseModel):

    job_id: str

    status: JobStatus


class JobStatusResponse(BaseModel):

    job_id: str

    status: JobStatus

    filename: Optional[str] = None

    result: Optional[AnalysisResponse] = None

    error: Optional[str] = None