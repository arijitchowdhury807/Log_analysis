import logging
import os
import time

from app.services.analyzer import LogAnalyzer
from app.storage.job_store import JobStore


logger = logging.getLogger(__name__)


class LogWorker:

    def __init__(self, job_store: JobStore):

        self.job_store = job_store

    def process(self, job_id: str, file_path: str) -> None:

        self.job_store.update(
            job_id,
            status="PROCESSING"
        )

        logger.info(
            "Started processing job %s",
            job_id
        )

        analyzer = LogAnalyzer()

        start_time = time.perf_counter()

        try:

            # Binary mode allows us to detect invalid UTF-8
            # ourselves rather than silently replacing it.
            with open(
                file_path,
                "rb",
                buffering=1024 * 1024
            ) as file:

                for raw_line in file:

                    try:

                        line = raw_line.decode(
                            "utf-8"
                        )

                    except UnicodeDecodeError:

                        analyzer.mark_unparseable()

                        continue

                    analyzer.process_line(line)

            processing_time_ms = (
                time.perf_counter()
                - start_time
            ) * 1000

            result = analyzer.get_result()

            result["processing_time_ms"] = round(
                processing_time_ms,
                2
            )

            self.job_store.update(
                job_id,
                status="COMPLETED",
                result=result
            )

            logger.info(
                "Completed job %s in %.2f ms",
                job_id,
                processing_time_ms
            )

        except Exception as error:

            logger.exception(
                "Job %s failed",
                job_id
            )

            self.job_store.update(
                job_id,
                status="FAILED",
                error=str(error)
            )

        finally:

            try:

                if os.path.exists(file_path):
                    os.remove(file_path)

            except OSError:

                logger.exception(
                    "Could not delete temporary file: %s",
                    file_path
                )