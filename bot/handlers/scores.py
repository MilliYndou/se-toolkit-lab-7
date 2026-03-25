"""Handler for /scores command."""


async def handle_scores(lab_name: str | None = None) -> str:
    """Handle the /scores command.

    Args:
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

    return (
        f"📊 *Scores for {lab_name}*\n\n"
        "Status: ⏳ Loading...\n\n"
        "_Real scores will be fetched from the LMS backend._"
    )
