"""Handler for /health command."""


async def handle_health() -> str:
    """Handle the /health command.

    Returns:
        Health status message.
    """
    return (
        "🏥 *Health Status*\n\n"
        "Bot: ✅ Running\n"
        "Backend: ⏳ Checking...\n\n"
        "Use /start to begin or /help for commands."
    )
