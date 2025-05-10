import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from acmsg.core.config import Config
from acmsg.core.git import GitUtils
from acmsg.api.openrouter import OpenRouterClient
from acmsg.core.generation import CommitMessageGenerator

# Add both the project root and src directory to the path for tests
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(project_root, "src")
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

# Print paths for debugging
print(f"Project root: {project_root}")
print(f"Src directory: {src_dir}")
print(f"Python path: {sys.path}")


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp.write("api_token: test_token\nmodel: test_model")
        temp_path = temp.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_config():
    """Mock Config object."""
    config = MagicMock(spec=Config)
    config.api_token = "test_token"
    config.model = "test_model"
    return config


@pytest.fixture
def mock_git_utils():
    """Mock GitUtils object."""
    git_utils = MagicMock(spec=GitUtils)
    git_utils.files_status = "M README.md\nA new_file.txt"
    git_utils.diff = "diff --git a/README.md b/README.md\n--- a/README.md\n+++ b/README.md\n@@ -1,3 +1,3 @@\n-# Test\n+# Updated Test\n \nSome content"
    return git_utils


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouterClient."""
    client = MagicMock(spec=OpenRouterClient)
    client.generate_completion.return_value = "feat: add new feature"
    return client


@pytest.fixture
def mock_commit_message_generator():
    """Mock CommitMessageGenerator."""
    generator = MagicMock(spec=CommitMessageGenerator)
    generator.generate.return_value = "feat: add new feature"
    return generator


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for Git commands."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Mock output"
        mock_run.return_value.returncode = 0
        yield mock_run


@pytest.fixture
def sample_git_status():
    """Sample git status output."""
    return "M README.md\nA new_file.txt\nD deleted_file.py"


@pytest.fixture
def sample_git_diff():
    """Sample git diff output."""
    return """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,5 +1,5 @@
-# Test Project
+# Updated Project

 This is a test project.
-Some text to remove.
+Some new text.
 More content here."""


@pytest.fixture
def mock_responses():
    """Mock API responses."""
    return {
        "success": {
            "choices": [{"message": {"content": "feat: add new functionality"}}]
        },
        "error": {"error": "API error message"},
    }


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "feat: add new feature"}}]
        }
        yield mock_post


@pytest.fixture
def mock_template_renderer():
    """Mock template renderer."""
    with patch("acmsg.templates.renderer") as mock_renderer:
        mock_renderer.render_system_prompt.return_value = "System prompt content"
        mock_renderer.render_user_prompt.return_value = "User prompt content"
        mock_renderer.render_config_template.return_value = (
            "api_token: \nmodel: default_model"
        )
        yield mock_renderer
