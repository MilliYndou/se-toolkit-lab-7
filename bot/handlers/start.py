"""Handler for /start command."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LmsClient


async def handle_start(lms_client: "LmsClient" | None = None, user_name: str | None = None) -> str:
    """Handle the /start command.

    Args:
        lms_client: Optional LMS client for backend integration.
        user_name: Optional name of the user for personalization.

    Returns:
        Welcome message text.
    """
    greeting = f"Hello{', {user_name}' if user_name else ''}! " if user_name else "Hello! "
    return (
        f"{greeting}Welcome to the LMS Bot! 🎓\n\n"
        "I can help you with:\n"
        "• Checking your lab scores\n"
        "• Viewing available labs\n"
        "• Getting help with commands\n\n"
        "Use /help to see all available commands."
    )
