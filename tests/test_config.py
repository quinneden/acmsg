import os
import pytest

import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from acmsg.core.config import Config
from acmsg.constants import DEFAULT_MODEL
from acmsg.exceptions import ConfigError


class TestConfig:
    """Tests for the Config class."""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="api_token: test_token\nmodel: test_model",
    )
    def test_init_config_file_existing(self, mock_file, mock_mkdir, mock_exists):
        """Test initialization with an existing config file."""
        mock_exists.return_value = True

        config = Config()

        # Path.exists() should be called at least once
        assert mock_exists.call_count >= 1
        mock_mkdir.assert_not_called()

        assert config.api_token == "test_token"
        assert config.model == "test_model"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("acmsg.templates.renderer.renderer.render_config_template")
    def test_init_config_file_create_new(
        self, mock_render, mock_file, mock_mkdir, mock_exists
    ):
        """Test initialization that creates a new config file."""
        mock_exists.return_value = False
        mock_render.return_value = "api_token: \nmodel: "

        config = Config()

        # Path.exists() should be called at least once
        assert mock_exists.call_count >= 1
        mock_mkdir.assert_called_once()
        mock_render.assert_called_once()
        mock_file().write.assert_called_once_with("api_token: \nmodel: ")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="api_token: test_token\nmodel: custom_model",
    )
    def test_get_config_values(self, mock_file):
        """Test getting configuration values."""
        config = Config()

        assert config.api_token == "test_token"
        assert config.model == "custom_model"
        assert isinstance(config.config_file, Path)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="api_token: test_token",
    )
    def test_fallback_to_default_model(self, mock_file):
        """Test fallback to default model when not provided in config."""
        config = Config()

        assert config.api_token == "test_token"
        assert config.model == DEFAULT_MODEL

    @patch("builtins.open", new_callable=mock_open, read_data="invalid yaml")
    def test_load_config_error(self, mock_file):
        """Test error handling when loading config fails."""
        with pytest.raises(ConfigError):
            Config()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="api_token: test_token\nmodel: test_model",
    )
    @patch("yaml.dump")
    def test_set_parameter(self, mock_dump, mock_file):
        """Test setting a configuration parameter."""
        config = Config()
        config.set_parameter("model", "new_model")

        mock_dump.assert_called_once()
        assert config.model == "new_model"

    def test_set_parameter_error(self):
        """Test error handling when setting parameter fails."""
        config = Config()

        # Mock open specifically for set_parameter to raise an error
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(ConfigError):
                config.set_parameter("model", "new_model")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="api_token: test_token\nmodel: test_model",
    )
    def test_get_parameter(self, mock_file):
        """Test getting a specific parameter."""
        config = Config()

        assert config.get_parameter("api_token") == "test_token"
        assert config.get_parameter("model") == "test_model"
        assert config.get_parameter("nonexistent") is None

    def test_get_parameter_error(self):
        """Test error handling when getting parameter fails."""
        config = Config()

        # Mock open specifically for get_parameter to raise an error
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with pytest.raises(ConfigError):
                config.get_parameter("model")
