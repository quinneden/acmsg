"""Message generation functionality for acmsg."""

from ..api.openrouter import OpenRouterClient
from ..exceptions import AcmsgError
from ..templates import renderer


class CommitMessageGenerator:
    """Generate commit messages from git changes."""

    def __init__(self, api_token: str, model: str):
        """Initialize the commit message generator.

        Args:
            api_token: OpenRouter API token
            model: Model ID to use for generation
        """
        if not api_token:
            raise AcmsgError("API token is required")

        self._api_client = OpenRouterClient(api_token)
        self._model = model

    def generate(self, git_status: str, git_diff: str) -> str:
        """Generate a commit message from git status and diff.

        Args:
            git_status: Output of git status command
            git_diff: Output of git diff command

        Returns:
            Generated commit message

        Raises:
            AcmsgError: If the generation fails
        """
        system_prompt = renderer.render_system_prompt()
        user_prompt = renderer.render_user_prompt(status=git_status, diff=git_diff)

        return self._api_client.generate_completion(
            model=self._model, system_prompt=system_prompt, user_prompt=user_prompt
        )


def format_message(msg: str) -> str:
    """Format a commit message for display.

    Args:
        msg: Raw commit message

    Returns:
        Formatted commit message with lines wrapped
    """
    import textwrap

    lines = msg.splitlines()
    formatted_lines = []

    for line in lines:
        if len(line) > 80:
            wrapped = textwrap.wrap(line, 80)
            formatted_lines.extend(wrapped)
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)
