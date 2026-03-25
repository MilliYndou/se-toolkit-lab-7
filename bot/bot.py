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
from services.intent_router import IntentRouter
from services.lms_client import LmsClient


async def run_test_mode(command: str) -> None:
    """Run a command in test mode and print the result.

    Args:
        command: The command to test (e.g., "/start", "/help", "what labs are available")
    """
    # Initialize clients
    lms_client = LmsClient(settings)
    intent_router = IntentRouter(settings, lms_client)

    # Parse the command
    command = command.strip()
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    # Check if it's a slash command or natural language
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
        # Use intent router for natural language queries
        response = await intent_router.route(command)

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
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Initialize clients
    lms_client = LmsClient(settings)
    intent_router = IntentRouter(settings, lms_client)

    # Create inline keyboard for /start
    def get_start_keyboard() -> InlineKeyboardMarkup:
        """Create inline keyboard with quick actions."""
        keyboard = [
            [
                InlineKeyboardButton(text="📋 Available Labs", callback_data="labs"),
                InlineKeyboardButton(text="🏥 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="📊 Lab Scores", callback_data="scores_lab-01"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
            [
                InlineKeyboardButton(text="🤖 Top Learners", callback_data="top_learners"),
                InlineKeyboardButton(text="📈 Completion Rate", callback_data="completion"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        response = await handle_start(lms_client, message.from_user.first_name)
        await message.answer(response, reply_markup=get_start_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = await handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        response = await handle_health(lms_client)
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = await handle_labs(lms_client)
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = await handle_scores(lms_client, lab_name)
        await message.answer(response)

    # Handle callback queries from inline keyboard
    @dp.callback_query(lambda c: c.data)
    async def process_callback_query(callback_query: types.CallbackQuery):
        """Handle inline keyboard button clicks."""
        data = callback_query.data

        if data == "labs":
            response = await handle_labs(lms_client)
        elif data == "health":
            response = await handle_health(lms_client)
        elif data == "help":
            response = await handle_help()
        elif data.startswith("scores_"):
            lab_name = data.replace("scores_", "")
            response = await handle_scores(lms_client, lab_name)
        elif data == "top_learners":
            response = await intent_router.route("Show me the top 5 learners in lab-01")
        elif data == "completion":
            response = await intent_router.route("What is the completion rate for lab-01")
        else:
            response = "Unknown action. Use /help for available commands."

        await callback_query.message.answer(response)
        await callback_query.answer()

    # Handle all other messages with intent router
    @dp.message()
    async def handle_message(message: types.Message):
        """Handle natural language messages with intent routing."""
        if not message.text:
            return

        # Show typing indicator
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        try:
            response = await intent_router.route(message.text)
            await message.answer(response)
        except Exception as e:
            print(f"[error] Message handling error: {e}", file=sys.stderr)
            await message.answer(
                "I encountered an error processing your message. Please try again or use /help for commands."
            )

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
