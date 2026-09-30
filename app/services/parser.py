from dataclasses import dataclass
from typing import Optional


VALID_LEVELS = frozenset({
    "DEBUG",
    "INFO",
    "WARN",
    "ERROR",
    "FATAL"
})


@dataclass(frozen=True)
class ParsedLog:
    date: str
    time: str
    level: str
    service: str
    message: str


def parse_line(line: str) -> Optional[ParsedLog]:
    """
    Parse one log line.

    Expected format:

    date time LEVEL service message

    Example:

    2026-09-18 10:23:45 ERROR payment-service Connection refused
    """

    line = line.rstrip("\r\n")

    if not line.strip():
        return None

    parts = line.split(" ", 4)

    if len(parts) != 5:
        return None

    date, time, level, service, message = parts

    # Validate date: YYYY-MM-DD
    if (
        len(date) != 10
        or date[4] != "-"
        or date[7] != "-"
        or not date[:4].isdigit()
        or not date[5:7].isdigit()
        or not date[8:10].isdigit()
    ):
        return None

    # Validate time: HH:MM:SS
    if (
        len(time) != 8
        or time[2] != ":"
        or time[5] != ":"
        or not time[:2].isdigit()
        or not time[3:5].isdigit()
        or not time[6:8].isdigit()
    ):
        return None

    if level not in VALID_LEVELS:
        return None

    if not service.strip():
        return None

    if not message.strip():
        return None

    return ParsedLog(
        date=date,
        time=time,
        level=level,
        service=service,
        message=message
    )