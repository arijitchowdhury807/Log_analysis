import os


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "Production Log Analyzer"
    )

    API_PREFIX = os.getenv(
        "API_PREFIX",
        "/api/v1"
    )

    CHUNK_SIZE_BYTES = int(
        os.getenv(
            "CHUNK_SIZE_BYTES",
            1024 * 1024
        )
    )

    MAX_FILE_SIZE_MB = int(
        os.getenv(
            "MAX_FILE_SIZE_MB",
            1024
        )
    )

    MAX_FILE_SIZE_BYTES = (
        MAX_FILE_SIZE_MB * 1024 * 1024
    )

    # Maximum number of analysis workers
    MAX_WORKERS = int(
        os.getenv(
            "MAX_WORKERS",
            4
        )
    )

    # Maximum number of jobs allowed
    # in PENDING/PROCESSING state.
    MAX_ACTIVE_JOBS = int(
        os.getenv(
            "MAX_ACTIVE_JOBS",
            20
        )
    )

    # Temporary upload directory
    TEMP_DIR = os.getenv(
        "TEMP_DIR",
        "temp_uploads"
    )


settings = Settings()