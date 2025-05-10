# import os
# import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from acmsg.templates.renderer import TemplateRenderer, renderer as renderer_instance


class TestTemplateRenderer:
    """Tests for the TemplateRenderer class."""

    def test_init(self):
        """Test initialization of the TemplateRenderer."""
        # Instead of patching Environment, we directly test the attributes
        # of the existing renderer instance
        renderer = TemplateRenderer()

        # Check that the assets_dir is set correctly
        assert isinstance(renderer.assets_dir, Path)
        assert renderer.assets_dir.name == "assets"

        # Verify that templates are properly loaded
        assert hasattr(renderer, "_config_template")
        assert hasattr(renderer, "_system_prompt_template")
        assert hasattr(renderer, "_user_prompt_template")

    def test_render_system_prompt(self):
        """Test rendering the system prompt template."""
        mock_template = MagicMock()
        mock_template.render.return_value = (
            "# IDENTITY AND PURPOSE\n\nYou are an expert..."
        )

        renderer = TemplateRenderer()
        renderer._system_prompt_template = mock_template

        result = renderer.render_system_prompt()

        assert result == "# IDENTITY AND PURPOSE\n\nYou are an expert..."
        mock_template.render.assert_called_once_with()

    def test_render_user_prompt(self):
        """Test rendering the user prompt template."""
        mock_template = MagicMock()
        mock_template.render.return_value = (
            "## USER-SPECIFIED TASK\n\nGenerated content..."
        )

        renderer = TemplateRenderer()
        renderer._user_prompt_template = mock_template

        status = "M file.py"
        diff = "diff --git a/file.py b/file.py\n..."

        result = renderer.render_user_prompt(status=status, diff=diff)

        assert result == "## USER-SPECIFIED TASK\n\nGenerated content..."
        mock_template.render.assert_called_once_with(status=status, diff=diff)

    def test_render_config_template(self):
        """Test rendering the config template."""
        mock_template = MagicMock()
        mock_template.render.return_value = "api_token: \nmodel: default_model"

        renderer = TemplateRenderer()
        renderer._config_template = mock_template

        result = renderer.render_config_template()

        assert result == "api_token: \nmodel: default_model"
        mock_template.render.assert_called_once_with()

    def test_assets_path(self):
        """Test that assets directory path is constructed correctly."""
        # Use the existing renderer instance
        renderer = renderer_instance

        # Test that assets_dir points to the 'assets' subdirectory
        assets_path = renderer.assets_dir
        assert assets_path.name == "assets"
        assert assets_path.parent.name == "templates"
