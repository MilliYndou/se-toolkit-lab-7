"""Command handlers - pure functions that process commands and return responses.

These handlers are transport-agnostic: they don't know about Telegram, HTTP,
or any specific interface. This enables unit testing and CLI test mode.
"""

from .start import handle_start
from .help import handle_help
from .health import handle_health
from .labs import handle_labs
from .scores import handle_scores
from .natural_language import handle_natural_language

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_natural_language",
]
