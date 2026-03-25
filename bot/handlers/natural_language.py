"""Handler for natural language queries using LLM intent routing."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.intent_router import IntentRouter


async def handle_natural_language(
    intent_router: "IntentRouter" | None = None,
    message: str = "",
) -> str:
    """Handle natural language queries using LLM intent routing.

    Args:
        intent_router: Intent router for LLM-based query processing.
        message: User's natural language message.

    Returns:
        Response from the intent router.
    """
    if intent_router is None or not message:
        return (
            "I can help you with questions about your labs and scores!\n\n"
            "Try asking:\n"
            "• 'what labs are available?'\n"
            "• 'show me scores for lab-01'\n"
            "• 'which lab has the lowest pass rate?'\n"
            "• 'who are the top 5 students?'"
        )

    return await intent_router.route(message)
