"""Handler for /health command."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LmsClient


async def handle_health(lms_client: "LmsClient" | None = None) -> str:
    """Handle the /health command.

    Args:
        lms_client: Optional LMS client for backend integration.

    Returns:
        Health status message.
    """
    if lms_client is None:
        return (
            "🏥 *Health Status*\n\n"
            "Bot: ✅ Running\n"
            "Backend: ⏳ Not checked\n\n"
            "Use /start to begin or /help for commands."
        )

    try:
        items = await lms_client.get_items()
        item_count = len(items) if items else 0
        return (
            f"🏥 *Health Status*\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ✅ Healthy\n"
            f"Items available: {item_count}"
        )
    except httpx.ConnectError as e:
        return (
            f"🏥 *Health Status*\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ Unreachable\n\n"
            f"Error: connection refused ({lms_client.base_url}). "
            f"Check that the services are running."
        )
    except httpx.HTTPStatusError as e:
        return (
            f"🏥 *Health Status*\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ Error\n\n"
            f"Error: HTTP {e.response.status_code} {e.response.reason_phrase}. "
            f"The backend service may be down."
        )
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return (
                f"🏥 *Health Status*\n\n"
                f"Bot: ✅ Running\n"
                f"Backend: ❌ Unreachable\n\n"
                f"Error: connection refused ({lms_client.base_url}). "
                f"Check that the services are running."
            )
        return (
            f"🏥 *Health Status*\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ Error\n\n"
            f"Error: {error_msg}"
        )


# Import httpx at module level for error handling
import httpx
