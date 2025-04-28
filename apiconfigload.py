from config import logger
import os
from pydantic import ValidationError
from pydantic_yaml import parse_yaml_raw_as
from apimodels import APIConfig

class APIConfigLoader:
    def __init__(self, directory='apiconfigs'):
        self.directory = directory

    def load_config(self, filepath):
        logger.debug(f"Loading configuration file: {filepath}")
        if not os.path.exists(filepath):
            logger.error(f"Configuration file not found: {filepath}")
            return None
        try:
            with open(filepath, 'r') as file:
                yaml_data = file.read()
            config = parse_yaml_raw_as(APIConfig, yaml_data)
            logger.debug(f"Configuration loaded successfully: {config}")
            return config
        except ValidationError as e:
            logger.error(f"Validation error in {filepath}: {e.errors()}")
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration file {filepath}: {e}")
            return None

    def load_all_configs(self):
        configs = []
        for filename in os.listdir(self.directory):
            if filename.endswith('.yaml'):
                filepath = os.path.join(self.directory, filename)
                config = self.load_config(filepath)
                if config:
                    configs.append(config)
                    #logger.info(f"Loaded configuration from file>> {filepath}")
                    #exitlogger.debug(f"Loaded configuration>> {config}")
        return configs
