import datetime as dt
import configparser


def server_print(s: str):
    print(f"[{dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] " + s)

def load_config(path: str) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config
