import logging
import logging.config
import yaml

# Load the logging configuration from the YAML file
with open('logging_config.yaml', 'r') as file:
    config = yaml.safe_load(file.read())
    logging.config.dictConfig(config)

# Get the logger specified in the configuration
logger = logging.getLogger('my_logger')


# Example usage
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')