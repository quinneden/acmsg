import pytest
from unittest.mock import patch, MagicMock

from acmsg.core.generation import CommitMessageGenerator, format_message
from acmsg.exceptions import AcmsgError


class TestCommitMessageGenerator:
    """Tests for the CommitMessageGenerator class."""

    def test_init(self):
        """Test initialization of the CommitMessageGenerator."""
        generator = CommitMessageGenerator("test_token", "test_model")
        assert generator._model == "test_model"
        assert hasattr(generator, "_api_client")

    def test_init_no_token(self):
        """Test initialization with no API token."""
        with pytest.raises(AcmsgError) as exc_info:
            CommitMessageGenerator("", "test_model")

        assert "API token is required" in str(exc_info.value)

    def test_generate(self):
        """Test generating a commit message."""
        # Mock the requests module to prevent actual API calls
        with patch("requests.post") as mock_post:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "feat: add new feature"}}]
            }
            mock_post.return_value = mock_response

            # Mock renderer methods
            with patch(
                "acmsg.templates.renderer.renderer.render_system_prompt"
            ) as mock_render_system:
                with patch(
                    "acmsg.templates.renderer.renderer.render_user_prompt"
                ) as mock_render_user:
                    # Setup renderer mocks
                    mock_render_system.return_value = "System prompt content"
                    mock_render_user.return_value = "User prompt content"

                    # Create generator and generate message
                    generator = CommitMessageGenerator("test_token", "test_model")
                    result = generator.generate("M file.py", "diff content")

                    # Verify the result and method calls
                    assert result == "feat: add new feature"

                    # Verify that the renderers were called correctly
                    mock_render_system.assert_called_once()
                    mock_render_user.assert_called_once_with(
                        status="M file.py", diff="diff content"
                    )

                    # Verify the API request was made with correct parameters
                    assert mock_post.called

    def test_generate_api_error(self):
        """Test error handling when API call fails."""
        # Use context manager for patching
        with patch("acmsg.api.openrouter.OpenRouterClient") as mock_client_class:
            # Setup mock to raise an exception
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.generate_completion.side_effect = AcmsgError("API error")

            # Create generator and attempt to generate message
            generator = CommitMessageGenerator("test_token", "test_model")

            # Check that the exception is raised
            with pytest.raises(AcmsgError):
                generator.generate("M file.py", "diff content")


class TestFormatMessage:
    """Tests for the format_message function."""

    def test_format_message_short_lines(self):
        """Test formatting message with short lines."""
        msg = "Line 1\nLine 2\nLine 3"
        result = format_message(msg)

        assert result == "Line 1\nLine 2\nLine 3"

    def test_format_message_long_lines(self):
        """Test formatting message with long lines that need wrapping."""
        long_line = "This is a very long line that exceeds the 80 character limit and should be wrapped by the format_message function to ensure proper display."
        msg = f"Short line\n{long_line}\nAnother short line"

        result = format_message(msg)

        # Check that the result has more lines than the original
        assert len(result.splitlines()) > len(msg.splitlines())

        # Check that all lines in the result are 80 chars or less
        for line in result.splitlines():
            assert len(line) <= 80

    def test_format_message_empty_input(self):
        """Test formatting an empty message."""
        result = format_message("")
        assert result == ""

    def test_format_message_single_line(self):
        """Test formatting a single line message."""
        msg = "Single line message"
        result = format_message(msg)
        assert result == "Single line message"
