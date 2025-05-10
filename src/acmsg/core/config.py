"""Configuration management for acmsg."""

import os
import yaml
from pathlib import Path
from typing import Optional, Any

from ..constants import DEFAULT_MODEL, CONFIG_FILENAME, CONFIG_DIR
from ..exceptions import ConfigError
from ..templates import renderer


class Config:
    """Configuration handler for acmsg."""

    def __init__(self):
        """Initialize the Config instance with configuration values."""
        self._default_model = DEFAULT_MODEL
        self._config_file = self._init_config_file()
        self._load_config()

    def _init_config_file(self) -> Path:
        """Create or locate the configuration file.

        Returns:
            Path to the configuration file
        """
        user_config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        acmsg_config_dir = Path(user_config_home) / CONFIG_DIR
        acmsg_config_file = acmsg_config_dir / CONFIG_FILENAME

        if not acmsg_config_file.exists():
            acmsg_config_dir.mkdir(parents=True, exist_ok=True)
            content = renderer.render_config_template()
            with open(acmsg_config_file, "w") as f:
                f.write(content)

        return acmsg_config_file

    def _load_config(self) -> None:
        """Load configuration values from the config file."""
        try:
            with open(self._config_file, "r") as f:
                data = yaml.safe_load(f) or {}

            self._model = data.get("model") or self._default_model
            self._api_token = data.get("api_token")
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}")

    @property
    def model(self) -> str:
        """Get the configured model.

        Returns:
            Model ID string
        """
        return self._model

    @property
    def api_token(self) -> Optional[str]:
        """Get the configured API token.

        Returns:
            API token string or None if not configured
        """
        return self._api_token

    @property
    def config_file(self) -> Path:
        """Get the path to the configuration file.

        Returns:
            Path to the configuration file
        """
        return self._config_file

    def set_parameter(self, parameter: str, value: Any) -> None:
        """Set a configuration parameter.

        Args:
            parameter: Parameter name
            value: Parameter value

        Raises:
            ConfigError: If the parameter cannot be set
        """
        try:
            with open(self._config_file, "r") as f:
                data = yaml.safe_load(f) or {}

            data[parameter] = value

            with open(self._config_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False)

            if parameter == "model":
                self._model = value
            elif parameter == "api_token":
                self._api_token = value
        except Exception as e:
            raise ConfigError(f"Failed to set parameter '{parameter}': {e}")

    def get_parameter(self, parameter: str) -> Any:
        """Get a configuration parameter value.

        Args:
            parameter: Parameter name

        Returns:
            Parameter value or None if not set

        Raises:
            ConfigError: If the parameter cannot be retrieved
        """
        try:
            with open(self._config_file, "r") as f:
                data = yaml.safe_load(f) or {}

            return data.get(parameter)
        except Exception as e:
            raise ConfigError(f"Failed to get parameter '{parameter}': {e}")
