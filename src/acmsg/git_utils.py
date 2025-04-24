import subprocess
import colorama
from colorama import Fore

colorama.init(autoreset=True)


class GitUtils:
    def __init__(self):
        self.is_git_repo()
        self.files_status = self.get_git_status()
        self.diff = self.get_git_diff()

    def is_git_repo(self):
        try:
            output = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                check=True,
            )
            return output.stdout.strip()
        except subprocess.CalledProcessError:
            print(Fore.RED + "Not a git repository")

    def get_git_status(self):
        output = subprocess.run(
            ["git", "diff", "--cached", "--name-status"], capture_output=True, text=True
        )
        if output.returncode != 0:
            raise Exception(output.stderr)
        else:
            return output.stdout.strip().replace("\t", " ")

    def get_git_diff(self):
        output = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True
        )
        if output.returncode != 0:
            raise Exception(output.stderr)
        else:
            return output.stdout.strip()

    def git_commit(message):
        commit = subprocess.run(
            ["git", "commit", "-m", message], capture_output=True, text=True
        )
        if commit.returncode != 0:
            raise Exception(commit.stdout)
        else:
            return commit.stdout.strip()
