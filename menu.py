from apiconfigload import APIConfigLoader
from config import logger

def display_menu():
    print("Menu:")
    for index, config in enumerate(configs, start=1):
        print(f"{index}. {config.nazev}")
    print(f"{len(configs) + 1}. Reload configurations")
    print(f"{len(configs) + 2}. Exit")

def volbaOperaci(config):
    print("Vyber operaci nebo sekvenci:")
    if config.jednotlive>0:
        print("Vyčet operací:")
        for index, operace in enumerate(config.jednotlive, start=1):
            print(f"{index}). {operace.nazev}")
    if config.sekvence>0:
        print("Vyčet sekvencí:")
        for index, sekvence in enumerate(config.sekvence, start=1):
            print(f"{index}). {sekvence.nazev}")

def get_user_choice():
    choice = input(f"Enter your choice (1-{len(configs) + 2}): ")
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
                print(f"Selected configuration: {selected_config.nazev}")
                volbaOperaci(selected_config)
                # Process the selected configuration
            elif choice == len(configs) + 1:
                print("Reloading configurations...")
                configs = loader.load_all_configs()
            elif choice == len(configs) + 2:
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    loader = APIConfigLoader()
    configs = loader.load_all_configs()
    main()
