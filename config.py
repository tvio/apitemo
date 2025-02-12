import logging
import logging.config
import yaml
import argparse

# Load logging configuration from YAML file
with open('loggingConfig.yaml', 'r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

# Get the logger specified in the configuration
logger = logging.getLogger('my_logger')

# Function to set the logging level
def set_logging_level(level_name):
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f'Invalid log level: {level_name}')
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run the application with specified logging level.')
parser.add_argument('--log-level', default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
args = parser.parse_args()

# Set the logging level based on the command-line argument
set_logging_level(args.log_level)
print('Nastaveny log level na >> ' + args.log_level)
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')