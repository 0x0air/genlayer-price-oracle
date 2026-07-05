"""
Base integration module for GenLayer Intelligent Contract external API integrations.

This module provides the BaseIntegration class that all GenLayer external
API integrations should inherit from. It provides common functionality
for HTTP requests, caching, and error handling.
"""

import json
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .exceptions import (
    IntegrationError,
    APIRateLimitError,
    InvalidResponseError,
)


class BaseIntegration:
    """
    Base class for all GenLayer external API integrations.

    Provides HTTP request methods and error handling suitable for use
    within GenLayer Intelligent Contracts.
    """

    BASE_URL: str = ""
    DEFAULT_TIMEOUT: int = 15

    def __init__(self, api_key: Optional[str] = None, timeout: int = 15):
        self._api_key = api_key
        self._timeout = timeout

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for API requests."""
        headers = {
            "User-Agent": "GenLayerIntegration/1.0",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Any:
        """
        Make an HTTP request to the external API.

        Args:
            endpoint: API endpoint path (e.g., "/api/v3/simple/price")
            params: Query parameters dictionary
            method: HTTP method (GET, POST, etc.)

        Returns:
            Parsed JSON response

        Raises:
            APIRateLimitError: When rate limited (HTTP 429)
            InvalidResponseError: When response is malformed
            IntegrationError: For other HTTP errors
        """
        import urllib.parse

        url = f"{self.BASE_URL}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)

        req = Request(url, method=method, headers=self._build_headers())

        try:
            with urlopen(req, timeout=self._timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as e:
            if e.code == 429:
                raise APIRateLimitError(
                    f"Rate limit exceeded for {self.BASE_URL}{endpoint}"
                ) from e
            raise IntegrationError(
                f"HTTP {e.code} from {self.BASE_URL}{endpoint}: {e.reason}"
            ) from e
        except (URLError, ConnectionError, TimeoutError) as e:
            raise IntegrationError(
                f"Connection failed for {self.BASE_URL}{endpoint}: {e}"
            ) from e
        except json.JSONDecodeError as e:
            raise InvalidResponseError(
                f"Invalid JSON response from {self.BASE_URL}{endpoint}: {e}"
            ) from e

    def _validate_response(
        self, data: Any, required_keys: Optional[list] = None
    ) -> None:
        """Validate that the response contains expected data."""
        if data is None:
            raise InvalidResponseError("Received null/empty response from API")
        if required_keys:
            for key in required_keys:
                if key not in data:
                    raise InvalidResponseError(
                        f"Missing required key '{key}' in API response"
                    )
