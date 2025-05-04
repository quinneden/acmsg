import argparse
import os
import subprocess
import sys
import tempfile
import textwrap
import threading
import time

import colorama
from colorama import Fore, Style

from .config import Config
from .git_utils import GitUtils
from .open_router import gen_completion

colorama.init()


def spinner(stop_event):
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


def edit_message(msg):
    editor = os.environ.get("EDITOR", "nano")
    temp = tempfile.NamedTemporaryFile(prefix="acmsg_", delete=False, mode="w")

    temp.write(msg)
    temp.close()

    subprocess.run([editor, temp.name])

    with open(temp.name, "r") as temp:
        return temp.read()


def format_message(msg):
    lines = msg.splitlines()
    formatted_lines = []

    for line in lines:
        if len(line) > 80:
            wrapped = textwrap.wrap(line, 80)
            formatted_lines.extend(wrapped)
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)


def print_message(message):
    print(f"\n{Fore.LIGHTBLACK_EX}Commit message:{Style.RESET_ALL}\n")

    lines = message.splitlines()

    for line in lines:
        print(f"  {line}")
    print()


def prompt_for_action(message):
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
                        f"{Fore.MAGENTA}Please specify one of; [y]es, [n]o, [e]dit.{Style.RESET_ALL}"
                    )


def handle_commit(args):
    cfg = Config()
    api_token = cfg.api_token
    model = args.model if args.model else cfg.model

    repo = GitUtils()

    if not repo.files_status or not repo.diff:
        print(Fore.YELLOW + "Nothing to commit" + Style.RESET_ALL)
        exit(1)

    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
    spinner_thread.start()

    try:
        message = gen_completion(api_token, repo.files_status, repo.diff, model)
    finally:
        stop_spinner.set()
        spinner_thread.join()
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    try:
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
                    print("Commit successful!")
                except Exception as e:
                    print(f"Error committing: {e}")
                    return False
                break
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


def handle_config(args):
    cfg = Config()

    if hasattr(args, "token") and args.token:
        cfg.set_parameter(parameter="api_token", value=args.token)
        print("API token configuration saved.")
        return True

    if hasattr(args, "model") and args.model:
        cfg.set_parameter(parameter="model", value=args.model)
        print("Model configuration saved.")
        return True

    if hasattr(args, "_") and args._:
        print("Error: invalid configuration parameter")
        return False


def main():
    parser = argparse.ArgumentParser(
        prog="acmsg",
        description="Automated commit message generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    commit_parser = subparsers.add_parser(
        "commit",
        help="Generate a commit message using AI",
        description="Analyze your staged changes and generate a suitable commit message",
    )
    commit_parser.add_argument(
        "--model",
        type=str,
        help="Specify the AI model used for generation (overrides config)",
    )

    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration settings",
        description="Modify or display configuration parameters",
    )

    config_subparsers = config_parser.add_subparsers(dest="config_subcommand")

    config_set = config_subparsers.add_parser(
        "set",
        help="Set a configuration parameter",
        description="Set the value of a parameter in your config file.",
    )
    config_set.add_argument(
        "parameter",
        choices=["api_token", "model"],
        help="Parameter name",
    )
    config_set.add_argument("value", type=str, help="Value")

    config_get = config_subparsers.add_parser(
        "get",
        help="Display a configuration parameter",
        description="Show the current value of a configuration parameter.",
    )
    config_get.add_argument(
        "parameter",
        choices=["api_token", "model"],
        help="Parameter name",
    )

    subparsers.add_parser("help", help="Show help")

    args = parser.parse_args()

    if args.command == "help" or not args.command:
        parser.print_help()
        exit(0)

    if args.command == "commit":
        handle_commit(args)
    elif args.command == "config":
        if args.config_subcommand == "set":
            if args.parameter == "api_token":
                args.token = args.value
            elif args.parameter == "model":
                args.model = args.value
            handle_config(args)
        elif args.config_subcommand == "get":
            cfg = Config()
            if args.parameter == "api_token":
                parameter_value = cfg.get_parameter("api_token")
            elif args.parameter == "model":
                parameter_value = cfg.get_parameter("model")
            print(parameter_value)


if __name__ == "__main__":
    main()
    exit(0)
