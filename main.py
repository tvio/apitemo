from config import logger
from apiconfigload import APIConfigLoader
from apilogic import APILogicController
import os

# Example usage:
if __name__ == "__main__":
    
     # Create an instance of APIConfigLoader
    loader = APIConfigLoader()

    # Load all configurations
    configs = loader.load_all_configs()
    controller = APILogicController(configs)    

    # Now you have all configurations stored in the configs array
    # You can access them as needed
    # for config in configs:
    #     logger.info(f"Configuration: {config}")