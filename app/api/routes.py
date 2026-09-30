import logging
import os
import tempfile

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile
)

from app.config import settings
from app.models.schemas import (
    AnalysisResponse,
    JobCreateResponse,
    JobStatusResponse
)
from app.services.job_service import JobService


router = APIRouter()

logger = logging.getLogger(__name__)

job_service = JobService()


@router.get("/health")
async def health_check():

    return {
        "status": "healthy"
    }


@router.post(
    "/jobs",
    response_model=JobCreateResponse,
    status_code=202
)
async def create_analysis_job(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    logger.info(
        "Receiving file: %s",
        file.filename
    )

    os.makedirs(
        settings.TEMP_DIR,
        exist_ok=True
    )

    temp_file = None

    try:

        temp_file = tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            dir=settings.TEMP_DIR,
            suffix=".log"
        )

        temp_path = temp_file.name

        total_bytes = 0

        while True:

            chunk = await file.read(
                settings.CHUNK_SIZE_BYTES
            )

            if not chunk:
                break

            total_bytes += len(chunk)

            if (
                total_bytes
                > settings.MAX_FILE_SIZE_BYTES
            ):

                temp_file.close()

                if os.path.exists(temp_path):
                    os.remove(temp_path)

                raise HTTPException(
                    status_code=413,
                    detail=(
                        f"File is too large. "
                        f"Maximum allowed size is "
                        f"{settings.MAX_FILE_SIZE_MB} MB."
                    )
                )

            temp_file.write(chunk)

        temp_file.close()

        job_id = job_service.create_job(
            file_path=temp_path,
            filename=file.filename
        )

        logger.info(
            "Created job %s for %s",
            job_id,
            file.filename
        )

        return {
            "job_id": job_id,
            "status": "PENDING"
        }

    except HTTPException:
        raise

    except Exception as error:

        logger.exception(
            "Failed to create analysis job"
        )

        if temp_file is not None:

            try:
                temp_file.close()
            except Exception:
                pass

        if (
            temp_file is not None
            and os.path.exists(temp_file.name)
        ):

            try:
                os.remove(temp_file.name)
            except OSError:
                pass

        raise HTTPException(
            status_code=500,
            detail="Failed to create analysis job"
        ) from error

    finally:

        await file.close()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse
)
async def get_analysis_job(
    job_id: str
):

    job = job_service.get_job(
        job_id
    )

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    result = None

    if job["result"] is not None:

        result = AnalysisResponse(
            **job["result"]
        )

    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "filename": job["filename"],
        "result": result,
        "error": job["error"]
    }