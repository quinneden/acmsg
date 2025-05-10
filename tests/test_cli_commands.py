from unittest.mock import patch, MagicMock
from io import StringIO

from acmsg.cli.commands import (
    spinner,
    edit_message,
    print_message,
    format_message,
    prompt_for_action,
    handle_commit,
    handle_config,
)
from acmsg.exceptions import ConfigError


class TestCliCommands:
    """Tests for CLI command functions."""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("time.sleep")
    def test_spinner(self, mock_sleep, mock_stdout):
        """Test the spinner animation."""
        import threading

        # Create a stop event and immediately set it to stop the spinner
        stop_event = threading.Event()
        stop_event.set()

        spinner(stop_event)

        # Verify that some output was written to stdout
        assert mock_stdout.getvalue() != ""

        # Verify that cursor visibility was restored
        assert "\033[?25h" in mock_stdout.getvalue()

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    def test_edit_message(self, mock_temp_file, mock_run):
        """Test editing a message with an editor."""
        # Setup mock temporary file
        mock_file = MagicMock()
        mock_temp_file.return_value = mock_file
        mock_file.name = "/tmp/mock_file"

        # Setup reading the edited file
        mock_file_content = "Edited message"
        mock_open_obj = MagicMock()
        mock_open_obj.__enter__.return_value = mock_open_obj
        mock_open_obj.read.return_value = mock_file_content

        with patch("builtins.open", return_value=mock_open_obj):
            result = edit_message("Original message")

        # Verify the message was written to the temp file
        mock_file.write.assert_called_once_with("Original message")

        # Verify the editor was called
        mock_run.assert_called_once()
        assert "/tmp/mock_file" in mock_run.call_args[0][0]

        # Verify the result is the edited message
        assert result == mock_file_content

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_message(self, mock_stdout):
        """Test printing a formatted commit message."""
        print_message("Line 1\nLine 2\nLine 3")

        output = mock_stdout.getvalue()
        assert "Line 1" in output
        assert "Line 2" in output
        assert "Line 3" in output

    def test_format_message(self):
        """Test formatting a message."""
        long_line = "This is a very long line that should be wrapped to multiple lines because it exceeds 80 characters."
        msg = f"Short line\n{long_line}\nAnother line"

        result = format_message(msg)

        # Check that all lines are 80 chars or less
        assert all(len(line) <= 80 for line in result.splitlines())
        assert "Short line" in result
        assert "Another line" in result

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_prompt_for_action_yes(self, mock_stdout, mock_input):
        """Test prompt with 'yes' response."""
        mock_input.return_value = "y"
        result = prompt_for_action("Test message")

        assert result is True
        mock_input.assert_called_once()

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_prompt_for_action_no(self, mock_stdout, mock_input):
        """Test prompt with 'no' response."""
        mock_input.return_value = "n"
        result = prompt_for_action("Test message")

        assert result is False
        mock_input.assert_called_once()

    @patch("acmsg.cli.commands.edit_message")
    @patch("acmsg.cli.commands.format_message")
    @patch("acmsg.cli.commands.print_message")
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_prompt_for_action_edit(
        self, mock_stdout, mock_input, mock_print, mock_format, mock_edit
    ):
        """Test prompt with 'edit' response."""
        mock_input.return_value = "e"
        mock_edit.return_value = "Edited message"
        mock_format.return_value = "Formatted edited message"

        result = prompt_for_action("Original message")

        assert result == "Formatted edited message"
        mock_edit.assert_called_once_with("Original message")
        mock_format.assert_called_once_with("Edited message")
        mock_print.assert_called_once()

    @patch("acmsg.cli.commands.Config")
    @patch("acmsg.cli.commands.GitUtils")
    @patch("acmsg.cli.commands.CommitMessageGenerator")
    @patch("threading.Thread")
    @patch("acmsg.cli.commands.format_message")
    @patch("acmsg.cli.commands.print_message")
    @patch("acmsg.cli.commands.prompt_for_action")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_commit_success(
        self,
        mock_stdout,
        mock_prompt,
        mock_print,
        mock_format,
        mock_thread,
        mock_generator,
        mock_git,
        mock_config,
    ):
        """Test successful commit handling."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.model = None

        mock_config_instance = MagicMock()
        mock_config_instance.api_token = "test_token"
        mock_config_instance.model = "default_model"
        mock_config.return_value = mock_config_instance

        mock_git_instance = MagicMock()
        mock_git_instance.files_status = "M file.py"
        mock_git_instance.diff = "diff content"
        mock_git.return_value = mock_git_instance

        mock_generator_instance = MagicMock()
        mock_generator_instance.generate.return_value = "feat: add new feature"
        mock_generator.return_value = mock_generator_instance

        mock_format.return_value = "formatted message"
        mock_prompt.return_value = True  # User confirms the commit

        # Call the function
        handle_commit(mock_args)

        # Verify the correct calls were made
        mock_config.assert_called_once()
        mock_git.assert_called_once()
        mock_generator.assert_called_once_with("test_token", "default_model")
        mock_generator_instance.generate.assert_called_once_with(
            "M file.py", "diff content"
        )
        mock_format.assert_called_once_with("feat: add new feature")
        mock_print.assert_called_once_with("formatted message")
        mock_prompt.assert_called_once_with("formatted message")
        mock_git.git_commit.assert_called_once_with("formatted message")

    @patch("acmsg.cli.commands.Config")
    @patch("acmsg.cli.commands.GitUtils")
    @patch("sys.exit")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_commit_no_staged_changes(
        self, mock_stdout, mock_exit, mock_git, mock_config
    ):
        """Test handling commit with no staged changes."""
        # Setup mocks
        mock_args = MagicMock()

        mock_config_instance = MagicMock()
        mock_config_instance.api_token = "test_token"
        mock_config.return_value = mock_config_instance

        mock_git_instance = MagicMock()
        mock_git_instance.files_status = ""  # No staged changes
        mock_git_instance.diff = ""
        mock_git.return_value = mock_git_instance

        # Call the function
        handle_commit(mock_args)

        # Verify exit was called with code 1
        assert mock_exit.call_count >= 1
        assert mock_exit.call_args.args[0] == 1
        assert "Nothing to commit" in mock_stdout.getvalue()
        # Verify the message was printed
        assert "Nothing to commit" in mock_stdout.getvalue()

    @patch("acmsg.cli.commands.Config")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_config_set(self, mock_stdout, mock_config):
        """Test handling config set command."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.config_subcommand = "set"
        mock_args.parameter = "model"
        mock_args.value = "new_model"

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Call the function
        handle_config(mock_args)

        # Verify the configuration was updated
        mock_config_instance.set_parameter.assert_called_once_with("model", "new_model")
        assert "configuration saved" in mock_stdout.getvalue()

    @patch("acmsg.cli.commands.Config")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_config_get(self, mock_stdout, mock_config):
        """Test handling config get command."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.config_subcommand = "get"
        mock_args.parameter = "model"

        mock_config_instance = MagicMock()
        mock_config_instance.get_parameter.return_value = "test_model"
        mock_config.return_value = mock_config_instance

        # Call the function
        handle_config(mock_args)

        # Verify the configuration was retrieved
        mock_config_instance.get_parameter.assert_called_once_with("model")
        assert "test_model" in mock_stdout.getvalue()

    @patch("acmsg.cli.commands.Config")
    @patch("sys.exit")
    @patch("sys.stdout", new_callable=StringIO)
    def test_handle_config_error(self, mock_stdout, mock_exit, mock_config):
        """Test error handling in config command."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.config_subcommand = "set"
        mock_args.parameter = "model"
        mock_args.value = "new_model"

        mock_config_instance = MagicMock()
        mock_config_instance.set_parameter.side_effect = ConfigError(
            "Configuration error"
        )
        mock_config.return_value = mock_config_instance

        # Call the function
        handle_config(mock_args)

        # Verify exit was called with code 1
        mock_exit.assert_called_once_with(1)
        # Verify the error message was printed
        assert "Configuration error" in mock_stdout.getvalue()
