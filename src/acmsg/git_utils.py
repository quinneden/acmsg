import subprocess


class GitUtils:
    def is_git_repo():
        output = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True)
        return output.stdout.strip()

    def git_status():
        git_status = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True, text=True)
        if git_status.returncode != 0:
            raise Exception(f"Git status failed:\n{git_status.stderr}")
        else:
            return git_status.stdout.strip().replace('\t', ' ').split('\n')

    def git_diff():
        diff = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True)
        return diff.stdout.strip()

    def git_commit(message):
        commit = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True)
        if commit.returncode != 0:
            raise Exception(commit.stderr)
        else:
            return commit.stdout.strip()
