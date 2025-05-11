# import pytest
import argparse
# from unittest.mock import patch

from acmsg.cli.parsers import create_parser


class TestCliParsers:
    """Tests for the CLI parsers."""

    def test_create_parser(self):
        """Test creating the main argument parser."""
        parser = create_parser()

        # Check parser properties
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "acmsg"

        # Check that required arguments and subparsers are defined
        has_version = False
        has_subparsers = False

        for action in parser._actions:
            if action.dest == "version":
                has_version = True
            elif isinstance(action, argparse._SubParsersAction):
                has_subparsers = True

                # Check that the required subparsers are defined
                subparser_names = set(action.choices.keys())
                assert "commit" in subparser_names
                assert "config" in subparser_names

                # Check commit subparser
                commit_parser = action.choices["commit"]
                has_model_arg = False

                for commit_action in commit_parser._actions:
                    if commit_action.dest == "model":
                        has_model_arg = True
                        assert commit_action.required is False  # model is optional

                assert has_model_arg

                # Check config subparser
                config_parser = action.choices["config"]
                has_config_subparsers = False

                for config_action in config_parser._actions:
                    if isinstance(config_action, argparse._SubParsersAction):
                        has_config_subparsers = True
                        config_subparser_names = set(config_action.choices.keys())
                        assert "set" in config_subparser_names
                        assert "get" in config_subparser_names

                        # Check set subparser
                        set_parser = config_action.choices["set"]
                        has_parameter_arg = False
                        has_value_arg = False

                        for set_action in set_parser._actions:
                            if set_action.dest == "parameter":
                                has_parameter_arg = True
                                assert set_action.required is True
                                assert set_action.choices == [
                                    "api_token",
                                    "model",
                                    "temperature",
                                ]
                            elif set_action.dest == "value":
                                has_value_arg = True
                                assert set_action.required is True

                        assert has_parameter_arg
                        assert has_value_arg

                        # Check get subparser
                        get_parser = config_action.choices["get"]
                        has_parameter_arg = False

                        for get_action in get_parser._actions:
                            if get_action.dest == "parameter":
                                has_parameter_arg = True
                                assert get_action.required is True
                                assert get_action.choices == [
                                    "api_token",
                                    "model",
                                    "temperature",
                                ]

                        assert has_parameter_arg

                assert has_config_subparsers

        assert has_version
        assert has_subparsers

    def test_parser_version_argument(self):
        """Test the version argument."""
        parser = create_parser()
        args = parser.parse_args(["--version"])
        assert args.version is True

    def test_parser_commit_command(self):
        """Test the commit command."""
        parser = create_parser()
        args = parser.parse_args(["commit"])
        assert args.command == "commit"
        assert args.model is None

        # Test with model specified
        args = parser.parse_args(["commit", "--model", "test_model"])
        assert args.command == "commit"
        assert args.model == "test_model"

    def test_parser_config_set_command(self):
        """Test the config set command."""
        parser = create_parser()
        args = parser.parse_args(["config", "set", "api_token", "test_token"])
        assert args.command == "config"
        assert args.config_subcommand == "set"
        assert args.parameter == "api_token"
        assert args.value == "test_token"

        # Test with model parameter
        args = parser.parse_args(["config", "set", "model", "test_model"])
        assert args.command == "config"
        assert args.config_subcommand == "set"
        assert args.parameter == "model"
        assert args.value == "test_model"

    def test_parser_config_get_command(self):
        """Test the config get command."""
        parser = create_parser()
        args = parser.parse_args(["config", "get", "api_token"])
        assert args.command == "config"
        assert args.config_subcommand == "get"
        assert args.parameter == "api_token"

        # Test with model parameter
        args = parser.parse_args(["config", "get", "model"])
        assert args.command == "config"
        assert args.config_subcommand == "get"
        assert args.parameter == "model"

    def test_parser_no_args(self):
        """Test parsing with no arguments."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.command is None
        assert args.version is False
