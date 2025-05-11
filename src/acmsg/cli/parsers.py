"""CLI argument parsers for acmsg."""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser for acmsg.

    Returns:
        Main argument parser
    """
    parser = argparse.ArgumentParser(
        prog="acmsg",
        description="Automated commit message generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="display the program version and exit",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Commit command parser
    commit_parser = subparsers.add_parser(
        "commit",
        help="generate a commit message",
        description="Analyzes your staged changes and generate a suitable commit message using the configured AI model",
    )
    commit_parser.add_argument(
        "--model",
        type=str,
        help="specify the AI model used for generation (overrides config)",
    )
    commit_parser.add_argument(
        "--temperature",
        type=float,
        help="specify the temperature for the AI model (overrides config)",
    )

    # Config command parser
    config_parser = subparsers.add_parser(
        "config",
        help="manage configuration settings",
        description="Modify or display configuration parameters",
    )

    config_subparsers = config_parser.add_subparsers(dest="config_subcommand")

    # Config subcommand `set`
    config_set = config_subparsers.add_parser(
        "set",
        help="set a configuration parameter",
        description="Set the value of a parameter in your config file.",
    )
    config_set.add_argument(
        "parameter",
        choices=["api_token", "model", "temperature"],
        help="parameter name",
    )
    config_set.add_argument("value", type=str, help="Value")

    # Config subcommand `get`
    config_get = config_subparsers.add_parser(
        "get",
        help="display a configuration parameter",
        description="Show the current value of a configuration parameter.",
    )
    config_get.add_argument(
        "parameter",
        choices=["api_token", "model", "temperature"],
        help="parameter name",
    )

    return parser
