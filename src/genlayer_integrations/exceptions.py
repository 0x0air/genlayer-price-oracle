class IntegrationError(Exception):
    """Base exception for all integration-related errors."""
    pass


class APIRateLimitError(IntegrationError):
    """Raised when the external API rate limit is exceeded."""
    pass


class InvalidResponseError(IntegrationError):
    """Raised when the API response is malformed or unexpected."""
    pass


class AuthenticationError(IntegrationError):
    """Raised when API authentication fails."""
    pass
