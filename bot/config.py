"""Bot configuration loaded from environment variables."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env.bot.secret in the same directory as this config file
BOT_DIR = Path(__file__).parent
ENV_FILE = BOT_DIR / ".env.bot.secret"

# Detect if running in Docker
IN_DOCKER = os.path.exists("/.dockerenv")


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = ""
    lms_api_key: str = ""

    # LLM API configuration (optional for intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""

    def model_post_init(self, __context) -> None:
        """Set default values after initialization."""
        # Set LMS API URL based on environment
        if not self.lms_api_base_url:
            if IN_DOCKER:
                self.lms_api_base_url = "http://backend:8000"
            else:
                self.lms_api_base_url = "http://localhost:42002"

        # Set LLM API URL for Docker (host.docker.internal to reach host)
        if self.llm_api_base_url and IN_DOCKER:
            # Replace localhost with host.docker.internal for Docker networking
            self.llm_api_base_url = self.llm_api_base_url.replace(
                "localhost", "host.docker.internal"
            )

    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode (no Telegram connection)."""
        return not self.bot_token

    @property
    def lms_headers(self) -> dict:
        """Get headers for LMS API requests."""
        return {"Authorization": f"Bearer {self.lms_api_key}"}


settings = BotSettings()
