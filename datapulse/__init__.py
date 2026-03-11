"""DataPulse Intelligence Hub."""

from ._runtime import ensure_supported_python

ensure_supported_python()

from .core import DataPulseItem, MediaType, SourceType  # noqa: E402
from .core.logging_config import configure_logging  # noqa: E402
from .reader import DataPulseReader  # noqa: E402

configure_logging()

__all__ = ["DataPulseReader", "DataPulseItem", "SourceType", "MediaType"]
__version__ = "0.8.0"
