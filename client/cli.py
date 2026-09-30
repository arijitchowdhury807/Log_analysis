import argparse
import os
import time
from pathlib import Path

import requests


SERVER_BASE_URL = os.getenv(
    "LOG_ANALYZER_URL",
    "http://127.0.0.1:8000/api/v1"
)

CREATE_JOB_URL = (
    f"{SERVER_BASE_URL}/jobs"
)

POLL_INTERVAL_SECONDS = 0.5

MAX_POLL_TIME_SECONDS = int(
    os.getenv(
        "MAX_POLL_TIME_SECONDS",
        3600
    )
)


def print_result(result: dict) -> None:

    print()
    print("=" * 65)
    print("                    LOG ANALYSIS RESULT")
    print("=" * 65)

    print(
        f"\nLines processed   : "
        f"{result['lines_processed']}"
    )

    print(
        f"Unparseable lines : "
        f"{result['unparseable_lines']}"
    )

    print()
    print("Service Name                         Error count")
    print("-" * 65)

    error_counts = result["error_counts"]

    if error_counts:

        for service, count in error_counts.items():

            print(
                f"{service:<38} "
                f"{count:>10}"
            )

    else:

        print(
            "No services found"
        )

    print("-" * 65)

    top_offender = result["top_offender"]

    if top_offender:

        top_count = error_counts[
            top_offender
        ]

        print(
            f"\nTop offender      : "
            f"{top_offender}"
        )

        print(
            f"Error count       : "
            f"{top_count}"
        )

    else:

        print(
            "\nTop offender      : None"
        )

    print(
        f"Processing time   : "
        f"{result['processing_time_ms']} ms"
    )

    print("=" * 65)
    print()


def wait_for_result(
    job_id: str
) -> dict:

    url = (
        f"{SERVER_BASE_URL}"
        f"/jobs/{job_id}"
    )

    start_time = time.monotonic()

    last_status = None

    while True:

        if (
            time.monotonic()
            - start_time
            > MAX_POLL_TIME_SECONDS
        ):

            raise TimeoutError(
                "Analysis job timed out."
            )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        job = response.json()

        status = job["status"]

        if status != last_status:

            print(
                f"Job status: {status}"
            )

            last_status = status

        if status == "COMPLETED":

            return job["result"]

        if status == "FAILED":

            error = job.get(
                "error",
                "Unknown processing error"
            )

            raise RuntimeError(
                error
            )

        time.sleep(
            POLL_INTERVAL_SECONDS
        )


def main():

    parser = argparse.ArgumentParser(
        description="Production Log Analyzer CLI"
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to the log file"
    )

    args = parser.parse_args()

    file_path = args.file

    if not file_path:

        file_path = input(
            "Enter log file path: "
        ).strip()

    if not file_path:

        print(
            "Error: No file path provided."
        )

        return

    path = Path(
        file_path
    )

    if not path.exists():

        print(
            f"Error: File does not exist: {path}"
        )

        return

    if not path.is_file():

        print(
            f"Error: Path is not a file: {path}"
        )

        return

    print()
    print(
        f"Uploading: {path}"
    )

    try:

        with path.open("rb") as file:

            response = requests.post(
                CREATE_JOB_URL,
                files={
                    "file": (
                        path.name,
                        file,
                        "text/plain"
                    )
                },
                timeout=3600
            )

        if response.status_code != 202:

            print(
                f"Server error "
                f"({response.status_code}):"
            )

            print(
                response.text
            )

            return

        job = response.json()

        job_id = job["job_id"]

        print()
        print(
            f"Job created: {job_id}"
        )

        print(
            "Waiting for analysis..."
        )

        result = wait_for_result(
            job_id
        )

        print_result(
            result
        )

    except requests.exceptions.ConnectionError:

        print(
            "Error: Could not connect to "
            "the log analyzer server."
        )

        print(
            "Make sure FastAPI is running."
        )

    except requests.exceptions.Timeout:

        print(
            "Error: Request timed out."
        )

    except requests.exceptions.RequestException as error:

        print(
            f"Request failed: {error}"
        )

    except TimeoutError as error:

        print(
            f"Error: {error}"
        )

    except RuntimeError as error:

        print(
            f"Analysis failed: {error}"
        )


if __name__ == "__main__":
    main()