import yaml


with open("../config/config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)