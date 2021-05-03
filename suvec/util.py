import json
import os


def read_config():
    conf_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(conf_path) as f:
        conf = json.load(f)
    return conf
