"""Git operations and utilities."""

import subprocess

import colorama
from colorama import Fore, Style

from ..exceptions import GitError

colorama.init(autoreset=True)


class GitUtils:
    """Git operations and utilities for version control."""

    def __init__(self):
        """Initialize the GitUtils instance with repository state."""
        self._check_git_repo()
        self._files_status = self._get_git_status()
        self._diff = self._get_git_diff()

    @property
    def files_status(self) -> str:
        """Get the status of files in the git repository.

        Returns:
            Formatted output of git status command
        """
        return self._files_status

    @property
    def diff(self) -> str:
        """Get the diff of staged changes in the git repository.

        Returns:
            Formatted output of git diff command
        """
        return self._diff

    def _check_git_repo(self) -> None:
        """Check if the current directory is a git repository.

        Raises:
            GitError: If the current directory is not a git repository
        """
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            raise GitError(f"{Fore.RED}Not a git repository{Style.RESET_ALL}")

    def _get_git_status(self) -> str:
        """Get the status of files in the git repository.

        Returns:
            Formatted output of git status command

        Raises:
            GitError: If the git command fails
        """
        try:
            output = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                check=True,
            )
            return output.stdout.strip().replace("\t", " ")
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get git status: {e.stderr}")

    def _get_git_diff(self) -> str:
        """Get the diff of staged changes in the git repository.

        Returns:
            Formatted output of git diff command

        Raises:
            GitError: If the git command fails
        """
        try:
            output = subprocess.run(
                ["git", "diff", "--cached"], capture_output=True, text=True, check=True
            )
            return output.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to get git diff: {e.stderr}")

    @staticmethod
    def git_commit(message: str) -> str:
        """Commit staged changes with the provided message.

        Args:
            message: Commit message

        Returns:
            Output of git commit command

        Raises:
            GitError: If the git commit fails
        """
        try:
            commit = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=True,
            )
            return commit.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Failed to commit: {e.stderr}")
