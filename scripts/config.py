import os
import yaml


def load_config(config_path="/home/yinxiaoran/data/PhoneAgent/OurAgent/Smartphone-Agent-world-model/config.yaml"):
    configs = dict(os.environ)
    with open(config_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    configs.update(yaml_data)
    return configs
