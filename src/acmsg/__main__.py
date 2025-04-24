import argparse
import os
import subprocess
import sys
import tempfile
import textwrap
import threading
import time

import colorama
from colorama import Fore

from .config import Config
from .git_utils import GitUtils
from .open_router import gen_completion

colorama.init(autoreset=True)


def yes_no(prompt):
    while True:
        response = input(prompt + " (y/n): ").lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False

        print("Please enter 'y' or 'n'")


def spinner(stop_event):
    spinner_chars = [".  ", ".. ", "...", "   "]
    i = 0

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        while not stop_event.is_set():
            sys.stdout.write(
                f"\r{Fore.LIGHTBLACK_EX}Generating commit message {spinner_chars[i % len(spinner_chars)]}\r"
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
    print(f"\n{Fore.LIGHTBLACK_EX}Commit message:\n")

    lines = message.splitlines()

    for line in lines:
        print(f"  {line}")
    print()


def prompt_for_action(message):
    prompt = Fore.LIGHTBLACK_EX + "Commit with this message? (y/n/e[dit]): "

    while True:
        opt = input(prompt).lower().strip()
        match opt:
            case "e" | "edit":
                message = edit_message(message)
                formatted_message = format_message(message)
                print_message(formatted_message)
            case "n" | "no":
                return False
            case "y" | "yes":
                return True
            case _:
                print(f"{Fore.RED}Invalid option: {opt}")


def handle_commit(args):
    cfg = Config()
    api_token = cfg.api_token
    model = args.model if args.model else cfg.model

    repo = GitUtils()

    if not repo.files_status or not repo.diff:
        print(Fore.YELLOW + "Nothing to commit")
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

        if prompt_for_action(formatted_message):
            try:
                GitUtils.git_commit(formatted_message)
                print("Commit successful!")
            except Exception as e:
                print(f"Error committing: {e}")
                return False
        else:
            print("Commit cancelled")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


def handle_config(args):
    cfg = Config()

    if hasattr(args, "token") and args.token:
        cfg.set_option(option="api_token", value=args.token)
        print("API token configuration saved.")
        return True

    if hasattr(args, "model") and args.model:
        cfg.set_option(option="model", value=args.model)
        print("Model configuration saved.")
        return True

    if hasattr(args, "_") and args._:
        print("Error: invalid configuration option")
        return False


def main():
    parser = argparse.ArgumentParser(prog="acmsg")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    commit_parser = subparsers.add_parser("commit", help="generate commit message")
    commit_parser.add_argument("--model", type=str, help="model to use for generation")

    config_parser = subparsers.add_parser("config", help="configuration commands")
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    config_set = config_subparsers.add_parser(
        "set", help="set configuration option value"
    )
    config_set.add_argument(
        "option", choices=["api_token", "model"], help="configuration option"
    )
    config_set.add_argument("value", type=str, help="option value")

    config_get = config_subparsers.add_parser(
        "get", help="get value of configuration option"
    )
    config_get.add_argument("option", choices=["api_token", "model"])

    subparsers.add_parser("help", help="Show help")

    args = parser.parse_args()

    if args.command == "help" or not args.command:
        parser.print_help()
        exit(0)

    if args.command == "commit":
        handle_commit(args)
    elif args.command == "config":
        if args.config_command == "set":
            if args.option == "api_token":
                args.token = args.value
            elif args.option == "model":
                args.model = args.value
            handle_config(args)
        elif args.config_command == "get":
            cfg = Config()
            if args.option == "api_token":
                option_value = cfg.get_option("api_token")
            elif args.option == "model":
                option_value = cfg.get_option("model")
            print(option_value)


if __name__ == "__main__":
    main()
    exit(0)
