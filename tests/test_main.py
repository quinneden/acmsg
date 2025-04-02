import pytest
from unittest.mock import patch, MagicMock
from acmsg.__main__ import format_message, print_message, handle_commit

def test_format_message():
    long_line = "This is a very long line that should be wrapped because it exceeds the maximum length of 80 characters in a single line"
    formatted = format_message(long_line)
    assert all(len(line) <= 80 for line in formatted.split('\n'))

@pytest.mark.parametrize("test_input,expected", [
    ("test\nmessage", 4),  # header + empty line + 2 message lines
    ("single", 3),         # header + empty line + 1 message line
    ("", 1),              # just header line
])
def test_print_message(capsys, test_input, expected):
    print_message(test_input)
    captured = capsys.readouterr()
    actual_lines = captured.out.strip().split('\n')
    assert len(actual_lines) == expected

@patch('acmsg.__main__.GitUtils')
@patch('acmsg.__main__.Config')
def test_handle_commit_no_changes(mock_config, mock_git_utils):
    mock_git_utils.is_git_repo.return_value = True
    mock_git_utils.git_status.return_value = ""

    with pytest.raises(SystemExit) as exc_info:
        handle_commit(MagicMock())
    assert exc_info.value.code == 1
