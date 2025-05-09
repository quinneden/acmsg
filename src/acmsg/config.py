import os
import yaml

from .templates import config_template


class Config:
    def __init__(self):
        self.default_model = "qwen/qwen3-30b-a3b:free"
        self.config_file = self.create_or_path_to_config()
        self.model = self.get_parameter("model") or self.default_model
        self.api_token = self.get_parameter("api_token")

    def create_or_path_to_config(self, create=False):
        user_config_home = os.getenv(
            "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
        )
        acmsg_config_dir = f"{user_config_home}/acmsg"
        acmsg_config_file = f"{acmsg_config_dir}/config.yaml"

        if not os.path.exists(acmsg_config_file):
            os.makedirs(acmsg_config_dir, exist_ok=True)
            content = config_template.render()
            with open(acmsg_config_file, "w") as f:
                f.write(content)

        return acmsg_config_file

    def set_parameter(self, parameter, value):
        config_file = self.config_file
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        data[parameter] = value

        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def get_parameter(self, parameter):
        config_file = self.config_file
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        return data.get(parameter)
