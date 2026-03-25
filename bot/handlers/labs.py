"""Handler for /labs command."""


async def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available labs.
    """
    return (
        "📋 *Available Labs*\n\n"
        "• lab-01 – Products, Architecture & Roles\n"
        "• lab-02 – Requirements & Use Cases\n"
        "• lab-03 – System Design\n"
        "• lab-04 – Implementation\n\n"
        "Use /scores <lab-name> to check your scores.\n"
        "Example: /scores lab-01"
    )
