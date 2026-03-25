"""Handler for /start command."""


async def handle_start(user_name: str | None = None) -> str:
    """Handle the /start command.

    Args:
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
