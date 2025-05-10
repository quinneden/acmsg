import pytest
from unittest.mock import patch, MagicMock
import subprocess

from acmsg.core.git import GitUtils
from acmsg.exceptions import GitError


class TestGitUtils:
    """Tests for the GitUtils class."""

    @patch("subprocess.run")
    def test_check_git_repo_success(self, mock_run):
        """Test successful git repo check."""
        mock_run.return_value.stdout = "true"
        mock_run.return_value.returncode = 0

        # This should not raise an exception
        GitUtils()

        # Verify that subprocess.run was called at least once
        assert mock_run.called

        # Check for the specific call to git rev-parse
        found_rev_parse_call = False
        for call in mock_run.call_args_list:
            args, kwargs = call
            if (
                args
                and len(args[0]) >= 3
                and args[0][0] == "git"
                and args[0][1] == "rev-parse"
            ):
                found_rev_parse_call = True
                break

        assert found_rev_parse_call, "No call to git rev-parse was made"

    @patch("subprocess.run")
    def test_check_git_repo_failure(self, mock_run):
        """Test failed git repo check."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "rev-parse", "--is-inside-work-tree"],
            stderr="fatal: not a git repository",
        )

        with pytest.raises(GitError):
            GitUtils()

    @patch("subprocess.run")
    def test_get_git_status(self, mock_run):
        """Test getting git status."""
        mock_run.return_value.stdout = "M file.py\nA new.py"
        mock_run.return_value.returncode = 0

        with patch.object(GitUtils, "_check_git_repo"):
            repo = GitUtils()
            assert repo.files_status == "M file.py\nA new.py"

            # Verify subprocess.run was called with correct arguments
            mock_run.assert_any_call(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                check=True,
            )

    @patch("subprocess.run")
    def test_get_git_status_error(self, mock_run):
        """Test error handling when getting git status fails."""
        mock_run.side_effect = [
            MagicMock(),  # First call for _check_git_repo
            subprocess.CalledProcessError(  # Second call for _get_git_status
                returncode=1,
                cmd=["git", "diff", "--cached", "--name-status"],
                stderr="error message",
            ),
        ]

        with pytest.raises(GitError):
            with patch.object(GitUtils, "_check_git_repo"):
                GitUtils()

    @patch("subprocess.run")
    def test_get_git_diff(self, mock_run):
        """Test getting git diff."""
        mock_run.return_value.stdout = "diff --git a/file.py b/file.py\n..."
        mock_run.return_value.returncode = 0

        with patch.object(GitUtils, "_check_git_repo"):
            with patch.object(GitUtils, "_get_git_status"):
                repo = GitUtils()
                repo._diff = "diff --git a/file.py b/file.py\n..."
                assert repo.diff == "diff --git a/file.py b/file.py\n..."

                # Verify subprocess.run was called with correct arguments
                mock_run.assert_any_call(
                    ["git", "diff", "--cached"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

    def test_get_git_diff_error(self):
        """Test error handling when getting git diff fails."""
        # Mock the _check_git_repo method to do nothing
        with patch.object(GitUtils, "_check_git_repo"):
            # Mock the _get_git_status method to return a value
            with patch.object(GitUtils, "_get_git_status", return_value="M file.py"):
                # Mock the subprocess call for git diff to raise an error
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = subprocess.CalledProcessError(
                        returncode=1,
                        cmd=["git", "diff", "--cached"],
                        stderr="error message",
                    )

                    # This should raise a GitError
                    with pytest.raises(GitError):
                        git_utils = GitUtils()
                        # Force calling _get_git_diff
                        git_utils._get_git_diff()

    @patch("subprocess.run")
    def test_git_commit_success(self, mock_run):
        """Test successful git commit."""
        mock_run.return_value.stdout = "1 file changed"
        mock_run.return_value.returncode = 0

        result = GitUtils.git_commit("feat: add new feature")

        assert result == "1 file changed"
        mock_run.assert_called_with(
            ["git", "commit", "-m", "feat: add new feature"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_git_commit_error(self, mock_run):
        """Test error handling when git commit fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "commit", "-m", "message"],
            stderr="nothing to commit",
        )

        with pytest.raises(GitError):
            GitUtils.git_commit("feat: add new feature")
