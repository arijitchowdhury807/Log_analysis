import threading
from typing import Optional


class JobStore:

    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, data: dict) -> None:

        with self._lock:
            self._jobs[job_id] = data

    def get(self, job_id: str) -> Optional[dict]:

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                return None

            return job.copy()

    def update(
        self,
        job_id: str,
        **updates
    ) -> None:

        with self._lock:

            if job_id not in self._jobs:
                return

            self._jobs[job_id].update(updates)

    def active_jobs(self) -> int:

        with self._lock:

            return sum(
                1
                for job in self._jobs.values()
                if job["status"] in {
                    "PENDING",
                    "PROCESSING"
                }
            )