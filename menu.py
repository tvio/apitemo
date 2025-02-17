from apiconfigload import APIConfigLoader
from config import logger
from  utils import clear_screen, ft
from apilogic import APILogicController

def display_menu():
    clear_screen()
    print("Menu:")
    for index, config in enumerate(configs, start=1):
        print(f"{index}. {config.nazev}")
    print(f"{len(configs) + 1}. Reload configurations")
    print(f"{len(configs) + 2}. Exit")

def volbaOperaci(config):
    clear_screen()
    print(ft("Vyber operaci nebo sekvenci API ")+ft(config.nazev, "green"))
    options = {}

    if config.jednotlive:
        print(ft("Vyčet operací:"))
        for operace in config.jednotlive:
            print(f"{ft(str(operace.id) + ')')} {ft(operace.nazev)} {operace.url}")
            options[operace.id] = ('jednotlive', operace)
            print(f"Debug: Added jednotlive operation with id {operace.id}")

    if config.sekvence:
        print(ft("Vyčet sekvencí:"))
        for sekvence in config.sekvence:
            print(ft(f"{sekvence.id}) {sekvence.nazev}"))
            for krok in sekvence.kroky:
                print(f"{sekvence.id}.{krok.id}) {krok.url}")
            options[sekvence.id] = ('sekvence', sekvence)
            print(f"Debug: Added sekvence with id {sekvence.id}")

    print(ft("Ostatni:"))
    exit_option = max(options.keys()) + 1 if options else 1
    print(f"{exit_option}). Zpět do hlavního menu")
    options[exit_option] = ('exit', None)
    
    print(f"Debug: Available options: {options}")

    while True:
        choice = input(f"Enter your choice (1-{exit_option} or 'exit'): ").strip().lower()
        if choice == "exit":
            return None, None
        
        try:
            choice = int(choice)
            print(f"Debug: User chose {choice}")
            if choice in options.keys():
                option_type, selected_option = options[choice]
                print(f"Debug: Found option type: {option_type}")
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
    choice = input(f"Enter your choice (1-{len(configs) + 2} or 'exit'): ").strip().lower()
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
                while True:  # New inner loop for operations menu
                    print(f"Selected configuration: {selected_config.nazev}")
                    operation_type, selected_operation = volbaOperaci(selected_config)
                    if operation_type:
                        print(f"Processing {operation_type}: {selected_operation.nazev}")
                        apiClient = APILogicController(selected_config)
                        if operation_type == 'jednotlive':
                            apiClient.callJednotlive(selected_operation)
                        #elif operation_type == 'sekvence':
                         #   apiClient.callSekvence(selected_operation)
                    else:  # User selected exit or invalid input
                        break  # Return to main menu
            elif choice == len(configs) + 1:
                print("Reloading configurations...")
                configs = loader.load_all_configs()
            elif choice == len(configs) + 2 or choice == "exit":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        elif choice == "exit":
            print("Exiting...")
            break
        else:
            print("Invalid input. Please enter a number or 'exit'.")



if __name__ == "__main__":
    loader = APIConfigLoader()
    configs = loader.load_all_configs()
    main()
