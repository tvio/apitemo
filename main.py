from config import logger
from apiconfigload import APIConfigLoader
import os

# Example usage:
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run the application with specified logging level.')
    parser.add_argument('--log-level', default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()

    # Set the logging level based on the command-line argument
    logger.setLevel(args.log_level.upper())

    # Create an instance of APIConfigLoader
    loader = APIConfigLoader()

    # Array to store configurations
    configs = []

 # Iterate over all files in the specified directory
    for filename in os.listdir(loader.directory):
        if filename.endswith('.yaml'):
            filepath = os.path.join(loader.directory, filename)
            config = loader.load_config(filepath)
            if config:
                configs.append(config)
                logger.info(f"Loaded configuration from {filepath}: {config}")
                logger.info(f"monitor: {config.monitor}")
            else:
                logger.error(f"Failed to load configuration from {filepath}")

    # Now you have all configurations stored in the configs array
    # You can access them as needed
    for config in configs:
        logger.info(f"Configuration: {config}")