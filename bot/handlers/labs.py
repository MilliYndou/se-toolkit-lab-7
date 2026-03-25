"""Handler for /labs command."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LmsClient


async def handle_labs(lms_client: "LmsClient" | None = None) -> str:
    """Handle the /labs command.

    Args:
        lms_client: Optional LMS client for backend integration.

    Returns:
        List of available labs.
    """
    if lms_client is None:
        return (
            "📋 *Available Labs*\n\n"
            "• lab-01 – Products, Architecture & Roles\n"
            "• lab-02 — Run, Fix, and Deploy a Backend Service\n"
            "• lab-03 — Backend API: Explore, Debug, Implement, Deploy\n"
            "• lab-04 — Testing, Front-end, and AI Agents\n\n"
            "Use /scores <lab-name> to check your scores.\n"
            "Example: /scores lab-01"
        )

    try:
        items = await lms_client.get_items()
        if not items:
            return (
                "📋 *Available Labs*\n\n"
                "No labs found. The backend may be empty or not synced.\n\n"
                "Run the ETL pipeline: POST /pipeline/sync"
            )

        # Filter only labs (not tasks)
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return (
                "📋 *Available Labs*\n\n"
                "No labs found in the backend."
            )

        lab_list = "\n".join([f"• {lab.get('title', 'Unknown')}" for lab in labs])
        return f"📋 *Available Labs*\n\n{lab_list}\n\nUse /scores <lab-name> to check your scores."

    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return (
                "📋 *Available Labs*\n\n"
                f"Error: connection refused ({lms_client.base_url}). "
                f"Check that the services are running."
            )
        return f"📋 *Available Labs*\n\nError fetching labs: {error_msg}"
