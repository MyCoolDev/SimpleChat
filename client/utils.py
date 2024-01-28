import configparser


def load_config(path: str) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config
