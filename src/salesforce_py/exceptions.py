"""Exceptions for salesforce-py."""


class SalesforcePyError(Exception):
    """Base exception for all salesforce-py errors."""


class CLINotFoundError(SalesforcePyError):
    """Raised when the `sf` binary is not found on PATH."""

    def __init__(self) -> None:
        super().__init__(
            "The `sf` CLI was not found on PATH. "
            "Install it from https://developer.salesforce.com/tools/salesforcecli"
        )


class CLIError(SalesforcePyError):
    """Raised when the `sf` CLI exits with a non-zero return code."""

    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            f"`sf` exited with code {returncode}.\n"
            f"stdout: {stdout!r}\n"
            f"stderr: {stderr!r}"
        )


class AuthError(SalesforcePyError):
    """Raised when authentication against a Salesforce org fails."""
