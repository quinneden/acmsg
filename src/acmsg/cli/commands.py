"""CLI command handlers for acmsg."""

import os
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Union

import colorama
from colorama import Fore, Style

from ..core.config import Config
from ..core.git import GitUtils
from ..core.generation import CommitMessageGenerator, format_message
from ..exceptions import AcmsgError, GitError, ApiError, ConfigError

colorama.init()


def spinner(stop_event: threading.Event) -> None:
    """Display a spinner animation while processing.

    Args:
        stop_event: Event to signal when to stop the spinner
    """
    spinner_chars = [".  ", ".. ", "...", "   "]
    i = 0

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while not stop_event.is_set():
            sys.stdout.write(
                f"\r{Fore.LIGHTBLACK_EX}Generating commit message {spinner_chars[i % len(spinner_chars)]}{Style.RESET_ALL}\r"
            )
            sys.stdout.flush()
            time.sleep(0.7)
            i += 1
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def edit_message(msg: str) -> str:
    """Open the default editor to edit the commit message.

    Args:
        msg: Initial message to edit

    Returns:
        Edited message
    """
    editor = os.environ.get("EDITOR", "nano")
    temp = tempfile.NamedTemporaryFile(prefix="acmsg_", delete=False, mode="w")

    temp.write(msg)
    temp.close()

    subprocess.run([editor, temp.name])

    with open(temp.name, "r") as temp_file:
        return temp_file.read()


def print_message(message: str) -> None:
    """Print a formatted commit message.

    Args:
        message: Commit message to print
    """
    print(f"\n{Fore.LIGHTBLACK_EX}Commit message:{Style.RESET_ALL}\n")

    lines = message.splitlines()

    for line in lines:
        print(f"  {line}")
    print()


def prompt_for_action(message: str) -> Union[bool, str]:
    """Prompt the user for action on the commit message.

    Args:
        message: Commit message to act on

    Returns:
        True if user wants to commit, False to cancel, or edited message
    """
    prompt = (
        Fore.LIGHTBLACK_EX
        + "Commit with this message? ([y]es/[n]o/[e]dit): "
        + Style.RESET_ALL
    )

    while True:
        opt = input(prompt).lower().strip()
        match opt:
            case "e" | "edit":
                message = edit_message(message)
                formatted_message = format_message(message)
                print_message(formatted_message)
                return formatted_message
            case "n" | "no":
                return False
            case "y" | "yes":
                return True
            case _:
                if opt != "":
                    print(f"{Fore.RED}Invalid option: {opt}{Style.RESET_ALL}")
                else:
                    print(
                        f"{Fore.MAGENTA}Please specify one of: [y]es, [n]o, "
                        f"[e]dit. {Style.RESET_ALL}"
                    )


def handle_commit(args: Any) -> None:
    """Handle the commit command.

    Args:
        args: Command line arguments
    """
    try:
        cfg = Config()
        api_token = cfg.api_token
        model = args.model or cfg.model

        if not api_token:
            print(f"{Fore.RED}Error: API token not configured.{Style.RESET_ALL}")
            print("Run 'acmsg config set api_token <your_token>' to configure.")
            sys.exit(1)

        repo = GitUtils()

        if not repo.files_status or not repo.diff:
            print(Fore.YELLOW + "Nothing to commit." + Style.RESET_ALL)
            sys.exit(1)

        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
        spinner_thread.start()

        try:
            generator = CommitMessageGenerator(api_token, model)
            message = generator.generate(repo.files_status, repo.diff)
        finally:
            stop_spinner.set()
            spinner_thread.join()
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

        formatted_message = format_message(message)
        print_message(formatted_message)

        while True:
            user_input = prompt_for_action(formatted_message)

            if user_input is False:
                print("Commit cancelled")
                break
            elif isinstance(user_input, str):
                formatted_message = user_input
            else:
                try:
                    GitUtils.git_commit(formatted_message)
                    print(f"{Fore.GREEN}Commit successful!{Style.RESET_ALL}")
                except GitError as e:
                    print(f"{Fore.RED}Error committing:{Style.RESET_ALL} {e}")
                break
    except (AcmsgError, GitError, ApiError) as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)


def handle_config(args: Any) -> None:
    """Handle the config command.

    Args:
        args: Command line arguments
    """
    try:
        cfg = Config()

        if args.config_subcommand == "set":
            cfg.set_parameter(args.parameter, args.value)
            print(f"{Fore.GREEN}{args.parameter} configuration saved.{Style.RESET_ALL}")
        elif args.config_subcommand == "get":
            parameter_value = cfg.get_parameter(args.parameter)
            if parameter_value:
                print(parameter_value)
            else:
                print(f"{Fore.YELLOW}{args.parameter} is not set.{Style.RESET_ALL}")
    except ConfigError as e:
        print(f"{Fore.RED}Configuration error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)
