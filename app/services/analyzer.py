from collections import defaultdict

from app.services.parser import parse_line


class LogAnalyzer:

    def __init__(self):
        self.total_lines = 0
        self.unparseable_lines = 0

        # service -> number of ERROR logs
        self.error_counts = defaultdict(int)

        self.top_offender = None
        self.max_errors = 0

    def process_line(self, line: str) -> None:
        """
        Process exactly one decoded log line.
        """

        self.total_lines += 1

        parsed = parse_line(line)

        if parsed is None:
            self.unparseable_lines += 1
            return

        # Keep service visible even if it has 0 errors.
        if parsed.service not in self.error_counts:
            self.error_counts[parsed.service] = 0

        # INFO/WARN/DEBUG/FATAL are valid logs,
        # but only ERROR contributes to error count.
        if parsed.level != "ERROR":
            return

        self.error_counts[parsed.service] += 1

        current_count = self.error_counts[parsed.service]

       
        if current_count > self.max_errors:
            self.max_errors = current_count
            self.top_offender = parsed.service

    def mark_unparseable(self) -> None:
        """
        Used when raw bytes cannot be decoded as UTF-8.
        """

        self.total_lines += 1
        self.unparseable_lines += 1

    def get_result(self) -> dict:

        return {
            "lines_processed": self.total_lines,
            "unparseable_lines": self.unparseable_lines,
            "error_counts": dict(self.error_counts),
            "top_offender": self.top_offender
        }