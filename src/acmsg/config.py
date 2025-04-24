import os
import yaml


class Config:
    def __init__(self):
        self.config_dir = self.create_dir_if_not_exists()
        self.config_file = self.create_file_if_not_exists()
        self.model = self.get_option("model")
        self.api_token = self.get_option("api_token")

    def create_dir_if_not_exists(self):
        home = os.getenv("HOME") or os.path.expanduser("~")
        config_dir = f"{home}/.config/acmsg"
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def create_file_if_not_exists(self):
        config_file = f"{self.config_dir}/config.yaml"
        data = {"api_token": "", "model": "deepseek/deepseek-r1:free"}

        if not os.path.exists(config_file):
            os.makedirs(self.config_dir, exist_ok=True)
            with open(config_file, "w") as f:
                yaml.dump(data, f)

        return config_file

    def set_option(self, option, value):
        config_file = self.config_file
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        data[option] = value

        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    def get_option(self, option):
        config_file = self.config_file
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        return data.get(option)
