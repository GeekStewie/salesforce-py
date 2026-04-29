"""salesforce-py: Python wrapper for Salesforce CLIs and APIs."""

from salesforce_py._version import __version__
from salesforce_py._defaults import DEFAULT_API_VERSION

__all__ = ["__version__", "DEFAULT_API_VERSION", "sf"]


def __getattr__(name: str):  # noqa: ANN202
    if name == "sf":
        from salesforce_py import sf

        return sf
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
