import pytest
import requests
from unittest.mock import patch, MagicMock
from acmsg.open_router import OpenRouter

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        yield mock_post, mock_get

def test_post_api_request_success(mock_requests):
    mock_post, mock_get = mock_requests
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "test commit message"}}]
    }
    mock_post.return_value = mock_response

    mock_get.return_value.text = "spec content"

    response = OpenRouter.post_api_request(
        "test-token",
        ["M file1.txt"],
        "test diff",
        "test-model"
    )

    assert response.ok
    assert response.json()["choices"][0]["message"]["content"] == "test commit message"

def test_post_api_request_failure(mock_requests):
    mock_post, mock_get = mock_requests
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.json.return_value = {"error": "API error"}
    mock_post.return_value = mock_response

    mock_get.return_value.text = "spec content"

    with pytest.raises(Exception) as exc_info:
        OpenRouter.post_api_request(
            "test-token",
            ["M file1.txt"],
            "test diff",
            "test-model"
        )
    assert str(exc_info.value) == "API request failed: API error"
