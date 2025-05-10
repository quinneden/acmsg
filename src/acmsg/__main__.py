"""Entry point for the acmsg CLI."""

import argparse
import importlib.metadata
import sys

from .cli.parsers import create_parser
from .cli.commands import handle_commit, handle_config


def main() -> int:
    """Run the acmsg command-line interface.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        version = importlib.metadata.version("acmsg")
        print(f"acmsg version {version}")
        return 0

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "commit":
        handle_commit(args)
        return 0

    if args.command == "config":
        if not args.config_subcommand:
            # Get the config subparser and print its help
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    action.choices["config"].print_help()
                    break
            return 0

        handle_config(args)
        return 0

    # This shouldn't happen due to argparse, but just in case
    print(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
