from typing import Any, Dict, List
import sys


class VerificationFormatter:
    SUCCESS_SYMBOL = "✅"
    FAILURE_SYMBOL = "🔴"
    WARNING_SYMBOL = "⚠️"
    INFO_SYMBOL = "🔍"
    DEBUG_SYMBOL = "📊"
    CRITICAL_SYMBOL = "💥"
    SUCCESS_FINAL_SYMBOL = "🎉"

    INDENT_UNIT = "    "
    SECTION_SEPARATOR = "=" * 60
    SUBSECTION_SEPARATOR = "-" * 50

    def __init__(self, output_stream=None):
        self.output_stream = output_stream or sys.stdout

    def format_section_header(self, title: str, symbol: str = INFO_SYMBOL) -> str:
        return f"\n{self.SECTION_SEPARATOR}\n{symbol} {title.upper()}\n{self.SECTION_SEPARATOR}"

    def format_subsection_header(self, title: str) -> str:
        return f"\n{self.DEBUG_SYMBOL} {title}\n{self.SUBSECTION_SEPARATOR}"

    def format_success_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.SUCCESS_SYMBOL} {message}"

    def format_failure_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.FAILURE_SYMBOL} {message}"

    def format_warning_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.WARNING_SYMBOL} {message}"

    def format_critical_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.CRITICAL_SYMBOL} {message}"

    def format_final_success_message(self, message: str) -> str:
        return f"\n{self.SUCCESS_FINAL_SYMBOL} {message}"

    def format_info_line(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{message}"

    def format_summary_stats(self, stats: Dict[str, Any], indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        lines = []
        for key, value in stats.items():
            lines.append(f"{indent}{key}: {value}")
        return "\n".join(lines)

    def format_item_result(
        self, item_name: str, success: bool, message: str, indent_level: int = 0
    ) -> str:
        symbol = self.SUCCESS_SYMBOL if success else self.FAILURE_SYMBOL
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{item_name}: {symbol} {message}"

    def format_suggestions_list(
        self, suggestions: List[str], indent_level: int = 1
    ) -> str:
        if not suggestions:
            return ""

        indent = self.INDENT_UNIT * indent_level
        lines = [f"{indent}Suggestions:"]
        for suggestion in suggestions:
            lines.append(f"{indent}• {suggestion}")
        return "\n".join(lines)

    def format_detailed_issues_list(
        self, issues: List[Dict[str, Any]], indent_level: int = 1
    ) -> str:
        if not issues:
            return ""

        indent = self.INDENT_UNIT * indent_level
        lines = [f"{indent}Detailed Issues:"]
        for issue in issues:
            subplot = issue.get("subplot", "Unknown")
            reason = issue.get("reason", "No reason provided")
            lines.append(f"{indent}• Subplot {subplot}: {reason}")
        return "\n".join(lines)

    def print_section_header(self, title: str, symbol: str = INFO_SYMBOL) -> None:
        self.output_stream.write(self.format_section_header(title, symbol))
        self.output_stream.flush()

    def print_subsection_header(self, title: str) -> None:
        self.output_stream.write(self.format_subsection_header(title))
        self.output_stream.flush()

    def print_success(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_success_message(message, indent_level))
        self.output_stream.flush()

    def print_failure(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_failure_message(message, indent_level))
        self.output_stream.flush()

    def print_warning(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_warning_message(message, indent_level))
        self.output_stream.flush()

    def print_critical(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_critical_message(message, indent_level))
        self.output_stream.flush()

    def print_final_success(self, message: str) -> None:
        self.output_stream.write(self.format_final_success_message(message))
        self.output_stream.flush()

    def print_info(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_info_line(message, indent_level))
        self.output_stream.flush()

    def print_summary_stats(self, stats: Dict[str, Any], indent_level: int = 0) -> None:
        self.output_stream.write(self.format_summary_stats(stats, indent_level))
        self.output_stream.flush()

    def print_item_result(
        self, item_name: str, success: bool, message: str, indent_level: int = 0
    ) -> None:
        self.output_stream.write(
            self.format_item_result(item_name, success, message, indent_level)
        )
        self.output_stream.flush()

    def print_suggestions(self, suggestions: List[str], indent_level: int = 1) -> None:
        formatted = self.format_suggestions_list(suggestions, indent_level)
        if formatted:
            self.output_stream.write(f"\n{formatted}")
            self.output_stream.flush()

    def print_detailed_issues(
        self, issues: List[Dict[str, Any]], indent_level: int = 1
    ) -> None:
        formatted = self.format_detailed_issues_list(issues, indent_level)
        if formatted:
            self.output_stream.write(f"\n{formatted}")
            self.output_stream.flush()


_default_formatter = VerificationFormatter()


def get_default_formatter() -> VerificationFormatter:
    return _default_formatter


def set_default_formatter(formatter: VerificationFormatter) -> None:
    global _default_formatter
    _default_formatter = formatter


def print_section_header(
    title: str, symbol: str = VerificationFormatter.INFO_SYMBOL
) -> None:
    _default_formatter.print_section_header(title, symbol)


def print_subsection_header(title: str) -> None:
    _default_formatter.print_subsection_header(title)


def print_success(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_success(message, indent_level)


def print_failure(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_failure(message, indent_level)


def print_warning(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_warning(message, indent_level)


def print_critical(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_critical(message, indent_level)


def print_final_success(message: str) -> None:
    _default_formatter.print_final_success(message)


def print_info(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_info(message, indent_level)


def print_summary_stats(stats: Dict[str, Any], indent_level: int = 0) -> None:
    _default_formatter.print_summary_stats(stats, indent_level)


def print_item_result(
    item_name: str, success: bool, message: str, indent_level: int = 0
) -> None:
    _default_formatter.print_item_result(item_name, success, message, indent_level)


def print_suggestions(suggestions: List[str], indent_level: int = 1) -> None:
    _default_formatter.print_suggestions(suggestions, indent_level)


def print_detailed_issues(issues: List[Dict[str, Any]], indent_level: int = 1) -> None:
    _default_formatter.print_detailed_issues(issues, indent_level)
