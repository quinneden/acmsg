"""Automatic git commit message generator using AI models & the OpenRouter API."""

from importlib.metadata import version as _version

__version__ = _version(__name__)

from .core.config import Config
from .core.git import GitUtils
from .core.generation import CommitMessageGenerator, format_message
from .api.openrouter import OpenRouterClient
from .exceptions import AcmsgError, ApiError, GitError, ConfigError

__all__ = [
    "Config",
    "GitUtils",
    "CommitMessageGenerator",
    "format_message",
    "OpenRouterClient",
    "AcmsgError",
    "ApiError",
    "GitError",
    "ConfigError",
]
