import pytest
from unittest.mock import patch
from acmsg.git_utils import GitUtils

@pytest.fixture
def mock_subprocess_run():
    with patch('subprocess.run') as mock_run:
        yield mock_run

def test_is_git_repo(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = "true\n"
    mock_subprocess_run.return_value.returncode = 0
    assert GitUtils.is_git_repo()

def test_git_status(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = "M file1.txt\nA file2.txt\n"
    mock_subprocess_run.return_value.returncode = 0
    status = GitUtils.git_status()
    assert len(status) == 2
    assert status[0] == "M file1.txt"
    assert status[1] == "A file2.txt"

def test_git_diff(mock_subprocess_run):
    mock_diff = "diff --git a/file1.txt b/file1.txt\n+new line"
    mock_subprocess_run.return_value.stdout = mock_diff
    mock_subprocess_run.return_value.returncode = 0
    assert GitUtils.git_diff() == mock_diff

def test_git_commit_success(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = "Successfully committed"
    mock_subprocess_run.return_value.returncode = 0
    assert GitUtils.git_commit("test commit") == "Successfully committed"

def test_git_commit_failure(mock_subprocess_run):
    mock_subprocess_run.return_value.stderr = "Error committing"
    mock_subprocess_run.return_value.returncode = 1
    with pytest.raises(Exception) as exc_info:
        GitUtils.git_commit("test commit")
    assert str(exc_info.value) == "Error committing"
