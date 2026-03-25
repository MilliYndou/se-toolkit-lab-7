"""LMS API client for communicating with the backend."""

import httpx

from config import BotSettings


class LmsClient:
    """Client for the LMS backend API."""

    def __init__(self, settings: BotSettings):
        """Initialize the LMS client.

        Args:
            settings: Bot configuration settings.
        """
        self.base_url = settings.lms_api_base_url
        self.headers = settings.lms_headers

    async def health_check(self) -> bool:
        """Check if the LMS backend is healthy.

        Returns:
            True if backend is healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def get_items(self) -> list[dict]:
        """Fetch available labs/items from the LMS.

        Returns:
            List of lab items.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/items/",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_pass_rates(self, lab: str) -> list[dict]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: Lab name (e.g., 'lab-01').

        Returns:
            List of pass rate records with task, avg_score, attempts.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_scores(self, student_id: str | None = None) -> list[dict]:
        """Fetch student scores from the LMS.

        Args:
            student_id: Optional student ID to filter scores.

        Returns:
            List of score records.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/interactions/",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
