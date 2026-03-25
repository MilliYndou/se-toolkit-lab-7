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
        "/labs - View available labs\n"
        "/scores <lab> - Check your scores for a specific lab\n\n"
        "You can also ask me questions in natural language, like:\n"
        "• 'what labs are available?'\n"
        "• 'show my scores for lab-01'\n"
        "• 'how am I doing in the course?'"
    )
