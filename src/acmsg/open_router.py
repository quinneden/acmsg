import json
import os
import requests
from jinja2 import Environment, FileSystemLoader

import colorama
from colorama import Fore, Style

colorama.init()


def gen_completion(api_token, git_status, git_diff, model):
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
    env = Environment(loader=FileSystemLoader(template_dir))
    system_prompt_template = env.get_template("system.md")
    user_prompt_template = env.get_template("user.md")

    system_prompt = system_prompt_template.render()
    user_prompt = user_prompt_template.render(status=git_status, diff=git_diff)

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": model,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": "Parse the following messages as markdown.",
                    },
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        ),
    )
    if not response.ok:
        error_data = response.json()
        raise Exception(
            f"{Fore.RED}API request failed:{Style.RESET_ALL}\n{error_data.get('error', response.text)}"
        )
    else:
        return response
