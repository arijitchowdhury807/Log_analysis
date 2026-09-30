import os
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException

from app.config import settings
from app.services.worker import LogWorker
from app.storage.job_store import JobStore


class JobService:

    def __init__(self):

        self.store = JobStore()

        self.executor = ThreadPoolExecutor(
            max_workers=settings.MAX_WORKERS
        )

        self.worker = LogWorker(
            self.store
        )

    def create_job(
        self,
        file_path: str,
        filename: str
    ) -> str:

        active_jobs = self.store.active_jobs()

        if active_jobs >= settings.MAX_ACTIVE_JOBS:

            raise HTTPException(
                status_code=429,
                detail=(
                    "Too many active analysis jobs. "
                    "Please try again later."
                )
            )

        job_id = str(uuid.uuid4())

        self.store.create(
            job_id,
            {
                "job_id": job_id,
                "filename": filename,
                "file_path": file_path,
                "status": "PENDING",
                "result": None,
                "error": None
            }
        )

        self.executor.submit(
            self.worker.process,
            job_id,
            file_path
        )

        return job_id

    def get_job(self, job_id: str):

        return self.store.get(
            job_id
        )