"""Custom exceptions for the acmsg package."""


class AcmsgError(Exception):
    """Base exception for all acmsg errors."""

    pass


class ApiError(AcmsgError):
    """Error occurred during API communication."""

    pass


class GitError(AcmsgError):
    """Error occurred during git operations."""

    pass


class ConfigError(AcmsgError):
    """Error occurred related to configuration."""

    pass
