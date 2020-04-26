import yaml as yl
import os


class Config:

    def __init__(self, file_name: str) -> None:
        self.data = self.load_config(file_name)

    @staticmethod
    def load_config(file_name) -> dict:
        """Get Configuration.

        This function will retrieve the configuration dict from yaml file.

        :return None
        """
        file_np = os.getcwd() + '/' + file_name
        with open(file_np, 'r') as config_file:
            return yl.safe_load(config_file)
