from config import logger
from apiconfigload import APIConfigLoader

# Example usage:
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run the application with specified logging level.')
    parser.add_argument('--log-level', default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    args = parser.parse_args()

    # Set the logging level based on the command-line argument
    logger.setLevel(args.log_level.upper())

    loader = APIConfigLoader()
    config = loader.load_config('exampleConfig.yaml')
    if config:
        #logger.info(f"Loaded configuration: {config}")
        logger.info(f"monitor: {config.monitor}")
    else:
        logger.error("Failed to load configuration.")