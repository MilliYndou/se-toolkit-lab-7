"""LLM API client for natural language understanding."""

import httpx

from config import BotSettings


class LlmClient:
    """Client for the LLM API (intent recognition)."""

    def __init__(self, settings: BotSettings):
        """Initialize the LLM client.

        Args:
            settings: Bot configuration settings.
        """
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url
        self.model = settings.llm_api_model or "coder-model"

    async def recognize_intent(self, message: str) -> str:
        """Recognize the intent of a user message.

        Args:
            message: The user's message text.

        Returns:
            Recognized intent (e.g., 'start', 'help', 'scores', 'unknown').
        """
        if not self.api_key or not self.base_url:
            return self._rule_based_intent(message)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are an intent classifier for an LMS Telegram bot. "
                                    "Classify the user's message into one of: start, help, health, "
                                    "labs, scores, unknown. Respond with ONLY the intent name."
                                ),
                            },
                            {"role": "user", "content": message},
                        ],
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                intent = data["choices"][0]["message"]["content"].strip().lower()
                return intent if intent in ["start", "help", "health", "labs", "scores"] else "unknown"
        except Exception:
            return self._rule_based_intent(message)

    def _rule_based_intent(self, message: str) -> str:
        """Fallback rule-based intent recognition.

        Args:
            message: The user's message text.

        Returns:
            Recognized intent.
        """
        message_lower = message.lower().strip()

        if message_lower in ["/start", "start", "hello", "hi", "hey"]:
            return "start"
        if message_lower in ["/help", "help"]:
            return "help"
        if message_lower in ["/health", "health", "status"]:
            return "health"
        if message_lower in ["/labs", "labs", "list labs", "available labs"]:
            return "labs"
        if "/scores" in message_lower or "score" in message_lower or "grade" in message_lower:
            return "scores"

        return "unknown"
