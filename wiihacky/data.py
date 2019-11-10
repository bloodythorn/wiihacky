import os
import yaml as yl
import const

DEFAULT_CONFIG = {
    'auth': {
        'user_agent': 'PutAgentNameHere',
        'client_id': 'PutClientIDHere',
        'client_secret': 'PutClientSecretHere',
        'username': 'PutUserNameHere',
        'password': 'PutPasswordHere',
        'admins': ["ListAdmins", "ByUserName", "Here"]}}


def load_config():
    """Get Configuration.

    This function will retrieve the configuration dict from yaml file.

    Returns
    -------
    A dictionary containing all configuration options.

    """
    file_np = "{}/{}".format(os.getcwd(), const.FILE_DEFAULT_CONFIG)
    with open(file_np, 'r') as config_file:
        return yl.safe_load(config_file)


def save_data(scrape: dict):
    """This function will save the given scrape in the proper location."""
