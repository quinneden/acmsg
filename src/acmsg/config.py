import os
import yaml


class Config:
    def __init__(self):
        self.config_dir = self.create_or_return_config_dir()
        self.config_file = self.create_or_return_config_yaml()
        self.model = self.get_parameter("model")
        self.api_token = self.get_parameter("api_token")

    def create_or_return_config_dir(self):
        home_dir = os.getenv("HOME") or os.path.expanduser("~")
        config_dir = f"{home_dir}/.config/acmsg"
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def create_or_return_config_yaml(self):
        config_file = f"{self.config_dir}/config.yaml"
        data = {"api_token": "", "model": "thudm/glm-4-32b:free"}

        if not os.path.exists(config_file):
            os.makedirs(self.config_dir, exist_ok=True)
            with open(config_file, "w") as f:
                yaml.dump(data, f)

        return config_file

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
