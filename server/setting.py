import yaml
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / 'config' / 'app.yaml'

def get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config

config = get_config(config_path)
