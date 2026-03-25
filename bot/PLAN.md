# Telegram Bot Development Plan

## Overview

This document outlines the development plan for the LMS Telegram Bot, which provides students with convenient access to their learning management system data through natural language conversations and structured commands.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point (`bot.py`)**: Handles both Telegram webhook/polling and CLI test mode. Routes incoming messages to appropriate handlers.

2. **Handlers Layer (`handlers/`)**: Contains pure functions that process commands and return responses. These functions are **transport-agnostic** — they don't know about Telegram, HTTP, or any specific interface. This enables:
   - Unit testing without mocking Telegram
   - CLI test mode (`--test` flag)
   - Future support for other interfaces (Slack, Discord, web chat)

3. **Services Layer (`services/`)**: External API clients abstracted behind interfaces:
   - `LmsClient`: Communicates with the LMS backend API
   - `LlmClient`: Handles natural language understanding via LLM

4. **Configuration (`config.py`)**: Centralized environment variable loading with validation.

## Development Tasks

### Task 1: Scaffold (Current)
Create project structure, dependencies, and test mode infrastructure.

### Task 2: Basic Commands
Implement `/start`, `/help`, `/health` handlers with LMS backend integration.

### Task 3: Intent Routing
Add LLM-based intent recognition for natural language queries like "what labs are available" or "show my scores".

### Task 4: Lab Scores
Implement `/scores <lab>` command to fetch and display student scores.

### Task 5: Deployment
Set up production deployment with proper error handling, logging, and monitoring.

## Testing Strategy

- **Unit tests**: Test handlers in isolation with mocked services
- **Integration tests**: Test full flow with test LMS backend
- **CLI test mode**: Manual verification via `uv run bot.py --test <command>`
- **Telegram testing**: Real-world verification in Telegram

## Dependencies

- `aiogram`: Async Telegram Bot API framework
- `httpx`: Async HTTP client for API calls
- `pydantic-settings`: Configuration management
- `pytest`: Testing framework
