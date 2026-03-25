"""Handler for /scores command."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.lms_client import LmsClient


async def handle_scores(lms_client: "LmsClient" | None = None, lab_name: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lms_client: Optional LMS client for backend integration.
        lab_name: Optional lab name to filter scores.

    Returns:
        Scores information.
    """
    if not lab_name:
        return (
            "📊 *Your Scores*\n\n"
            "Please specify a lab:\n"
            "/scores lab-01\n"
            "/scores lab-02\n\n"
            "Use /labs to see all available labs."
        )

    if lms_client is None:
        return (
            f"📊 *Scores for {lab_name}*\n\n"
            "Status: ⏳ Loading...\n\n"
            "_Real scores will be fetched from the LMS backend._"
        )

    try:
        # Get pass rates for the lab
        pass_rates = await lms_client.get_pass_rates(lab_name)

        if not pass_rates:
            return (
                f"📊 *Scores for {lab_name}*\n\n"
                f"No data found for lab '{lab_name}'.\n\n"
                "Check the lab name with /labs"
            )

        # Format the scores
        lines = [f"📊 *Scores for {lab_name}*\n\nPass rates:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"• {task_name}: {avg_score:.1f}% ({attempts} attempts)")

        return "\n".join(lines)

    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return (
                f"📊 *Scores for {lab_name}*\n\n"
                f"Error: connection refused ({lms_client.base_url}). "
                f"Check that the services are running."
            )
        if "404" in error_msg or "not found" in error_msg.lower():
            return (
                f"📊 *Scores for {lab_name}*\n\n"
                f"No data found for lab '{lab_name}'.\n\n"
                "Check the lab name with /labs"
            )
        return f"📊 *Scores for {lab_name}*\n\nError fetching scores: {error_msg}"
