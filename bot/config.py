"""Bot configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API configuration (optional for intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""

    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode (no Telegram connection)."""
        return not self.bot_token

    @property
    def lms_headers(self) -> dict:
        """Get headers for LMS API requests."""
        return {"Authorization": f"Bearer {self.lms_api_key}"}


settings = BotSettings()
