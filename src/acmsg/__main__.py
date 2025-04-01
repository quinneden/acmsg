import argparse
import os
import subprocess
import tempfile

import colorama
from colorama import Fore, Style

from .config import Config
from .git_utils import GitUtils
from .open_router import OpenRouter

colorama.init()


def yes_no(prompt):
    while True:
        response = input(prompt + " (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")


def edit_message(msg):
    editor = os.environ.get('EDITOR', 'nano')
    temp = tempfile.NamedTemporaryFile(
        prefix='acmsg_', delete=False, mode='w')
    temp.write(msg)
    temp.close()
    subprocess.run([editor, temp.name])
    with open(temp.name, 'r') as temp:
        return temp.read()


def print_message(message):
    print(f"\n{Fore.LIGHTBLACK_EX}Commit message:{Style.RESET_ALL}\n")
    print(f"  {message.replace('\n', '\n  ')}\n")


def prompt_for_action(message):
    prompt = (
        Fore.LIGHTBLACK_EX +
        "Commit with this message? (y/n/e[dit]): " +
        Style.RESET_ALL)
    while True:
        opt = input(prompt).lower().strip()
        match opt:
            case "e" | "edit":
                message = edit_message(message)
                print_message(message)
            case "n" | "no":
                return False
            case "y" | "yes":
                return True
            case _:
                print(f"{Fore.RED}Invalid option: {opt}{Style.RESET_ALL}")


def handle_commit(args):
    if not GitUtils.is_git_repo():
        print(Fore.RED + "Error: not a git repository" + Style.RESET_ALL)
        exit(1)
    cfg = Config()
    api_token = cfg.api_token
    model = args.model if args.model else cfg.model
    git_status = GitUtils.git_status()
    git_diff = GitUtils.git_diff()
    try:
        response = OpenRouter.post_api_request(
            api_token,
            git_status,
            git_diff,
            model
        )
        message = response.json()['choices'][0]['message']['content']
        print_message(message)
        if prompt_for_action(message):
            try:
                GitUtils.git_commit(message)
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
    if args.token:
        cfg.set_param(param='api_token', value=args.token)
        print("API token configuration saved.")
    elif args.model:
        cfg.set_param(param='model', value=args.model)
        print("Model configuration saved.")
    elif args._:
        print("Error: invalid configuration option")
    else:
        return True


def main():
    parser = argparse.ArgumentParser(prog='acmsg')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    commit_parser = subparsers.add_parser(
        'commit', help='Generate commit message')
    commit_parser.add_argument(
        '--model', type=str, help='Model to use for generation')

    config_parser = subparsers.add_parser(
        'config', help='Configuration commands')
    config_subparsers = config_parser.add_subparsers(dest='config_command')

    config_set = config_subparsers.add_parser(
        'set', help='Set configuration values')
    config_set.add_argument('setting', choices=['api_token', 'model'])
    config_set.add_argument('value', type=str)

    config_get = config_subparsers.add_parser(
        'get', help='Get configuration values')
    config_get.add_argument('setting', choices=['api_token', 'model'])

    subparsers.add_parser('help', help='Show help')

    args = parser.parse_args()

    if args.command == 'help' or not args.command:
        parser.print_help()
        exit(0)

    if args.command == 'commit':
        handle_commit(args)
    elif args.command == 'config':
        if args.config_command == 'set':
            if args.setting == 'api_token':
                args.token = args.value
            elif args.setting == 'model':
                args.model = args.value
            handle_config(args)
        elif args.config_command == 'get':
            cfg = Config()
            if args.setting == 'api_token':
                param_value = cfg.get_param('api_token')
            elif args.setting == 'model':
                param_value = cfg.get_param('model')
            print(param_value)


if __name__ == "__main__":
    main()
    exit(0)
