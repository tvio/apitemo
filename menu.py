from apiconfigload import APIConfigLoader
from config import logger
from utils import clear_screen, ft
from apilogic import APILogicController
import sys

def display_menu():
    clear_screen()
    print("Menu:")
    for index, config in enumerate(configs, start=1):
        print(f"{index}. {config.nazev}")
    print(f"{len(configs) + 1}. Reload configurations")

def volbaOperaci(config):
    print(ft("Vyber operaci nebo sekvenci API ")+ft(config.nazev, "green"))
    options = {}
    display_number = 1

    if config.jednotlive:
        print(ft("Vyčet operací:"))
        for operace in config.jednotlive:
            print(f"{ft(str(display_number) + ')')} {ft(operace.nazev)} {operace.url}")
            options[display_number] = ('jednotlive', operace)
            logger.debug(f"Added jednotlive operation with id {display_number}")
            display_number += 1
        print()  # Add empty line after jednotlive section

    if config.sekvence:
        print(ft("Vyčet sekvencí:"))
        for sekvence in config.sekvence:
            print(ft(f"{display_number}) {sekvence.nazev} {sekvence.kroky}"))
            options[display_number] = ('sekvence', sekvence)
            logger.debug(f"Added sekvence with id {display_number}")
            display_number += 1

    print(ft("Ostatni:"))
    exit_option = display_number
    print(f"{exit_option}). Zpět do hlavního menu")
    options[exit_option] = ('exit', None)
    
    logger.debug(f"Available options: {options}")

    while True:
        choice = input(f"Enter your choice (1-{exit_option} or 'exit'): ").strip().lower()
        if choice == "exit":
            print("Exiting...")
            sys.exit(0)
        
        try:
            choice = int(choice)
            logger.debug(f"User chose {choice}")
            if choice in options:
                option_type, selected_option = options[choice]
                logger.debug(f"Found option type: {option_type}")
                if option_type == 'exit':
                    return None, None
                else:
                    print(f"Selected {option_type}: {selected_option.nazev}")
                    return option_type, selected_option
            else:
                print("Invalid choice. Please enter a number from the menu.")
        except ValueError:
            print("Invalid input. Please enter a number or 'exit'.")

def get_user_choice():
    choice = input(f"Enter your choice (1-{len(configs) + 1} or 'exit'): ").strip().lower()
    return choice

def main():
    global configs
    while True:
        
        display_menu()
        choice = get_user_choice()
        
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(configs):
                selected_config = configs[choice - 1]
                first_time = True
                apiClient = APILogicController(config=selected_config)
                while True:  # New inner loop for operations menu
                    print()
                    if first_time:
                        print(ft(f"Selected configuration: {selected_config.nazev}", "green"))
                        first_time = False
                    operation_type, selected_operation = volbaOperaci(selected_config)
                    if operation_type and selected_operation:
                        print()
                        print(ft(f"Processing {operation_type}: {selected_operation.nazev}", "green"))
                        
                        
                        if operation_type == 'jednotlive':
                            apiClient.callJednotlive(selected_operation.id)
                            input("\nPress Enter to continue...")
                        elif operation_type == 'sekvence':
                            apiClient.callSekvence(selected_operation)
                            input("\nPress Enter to continue...")
                    else:  # User selected exit or invalid input
                        break  # Return to main menu
            elif choice == len(configs) + 1:
                print("Reloading configurations...")
                configs = loader.load_all_configs()
            else:
                print("Invalid choice. Please try again.")
        elif choice == "exit":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid input. Please enter a number or 'exit'.")



if __name__ == "__main__":
    loader = APIConfigLoader()
    configs = loader.load_all_configs()
    main()
