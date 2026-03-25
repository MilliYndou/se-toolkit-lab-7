#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Supports two modes:
1. Telegram mode: Connects to Telegram API and handles messages
2. Test mode (--test): Calls handlers directly for offline testing

Usage:
    uv run bot.py                  # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print handler response
"""

import asyncio
import sys
from pathlib import Path

# Add the directory containing bot.py to the path for imports
BOT_DIR = Path(__file__).parent
sys.path.insert(0, str(BOT_DIR))

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)
from services.llm_client import LlmClient
from services.lms_client import LmsClient


async def run_test_mode(command: str) -> None:
    """Run a command in test mode and print the result.

    Args:
        command: The command to test (e.g., "/start", "/help", "what labs are available")
    """
    # Initialize clients
    lms_client = LmsClient(settings)
    llm_client = LlmClient(settings)

    # Parse the command
    command = command.strip()
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    # Handle commands
    if cmd in ["/start", "start"]:
        response = await handle_start(lms_client)
    elif cmd in ["/help", "help"]:
        response = await handle_help()
    elif cmd in ["/health", "health"]:
        response = await handle_health(lms_client)
    elif cmd in ["/labs", "labs"]:
        response = await handle_labs(lms_client)
    elif cmd in ["/scores", "scores"]:
        response = await handle_scores(lms_client, arg)
    else:
        # Try intent recognition for natural language
        intent = await llm_client.recognize_intent(command)

        if intent == "start":
            response = await handle_start(lms_client)
        elif intent == "help":
            response = await handle_help()
        elif intent == "health":
            response = await handle_health(lms_client)
        elif intent == "labs":
            response = await handle_labs(lms_client)
        elif intent == "scores":
            # Extract lab name from message
            lab_name = arg
            response = await handle_scores(lms_client, lab_name)
        else:
            response = (
                "I didn't understand that command. Try:\n"
                "/start - Welcome message\n"
                "/help - Available commands\n"
                "/labs - View labs\n"
                "/scores <lab> - Check scores"
            )

    print(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode."""
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set. Cannot start Telegram bot.")
        print("Set BOT_TOKEN in .env.bot.secret or use --test mode for testing.")
        sys.exit(1)

    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        response = await handle_start(message.from_user.first_name)
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = await handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        backend_healthy = await lms_client.health_check()
        status = "✅ Running" if backend_healthy else "❌ Unreachable"
        response = f"🏥 *Health Status*\n\nBot: ✅ Running\nBackend: {status}"
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = await handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = await handle_scores(lab_name)
        await message.answer(response)

    # Start polling
    print("Starting Telegram bot...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test <command>")
            print("Example: uv run bot.py --test '/start'")
            sys.exit(1)

        command = " ".join(sys.argv[2:])
        asyncio.run(run_test_mode(command))
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
