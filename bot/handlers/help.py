"""Handler for /help command."""


async def handle_help() -> str:
    """Handle the /help command.

    Returns:
        Help message with available commands.
    """
    return (
        "📚 *Available Commands*\n\n"
        "/start - Welcome message and bot introduction\n"
        "/help - Show this help message\n"
        "/health - Check bot and backend status\n"
        "/labs - View available labs from the LMS\n"
        "/scores <lab> - Check pass rates for a specific lab\n\n"
        "Examples:\n"
        "• /scores lab-01\n"
        "• /scores lab-04"
    )
