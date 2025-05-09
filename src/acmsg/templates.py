import os
from jinja2 import Environment, FileSystemLoader

assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
env = Environment(loader=FileSystemLoader(assets_dir))

config_template = env.get_template("template_config.yaml")
system_prompt_template = env.get_template("system_prompt.md")
user_prompt_template = env.get_template("user_prompt.md")
