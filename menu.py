from apiconfigload import APIConfigLoader
from config import logger
from  utils import clear_screen, ft

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
    option_number = 1
    options = {}

    if config.jednotlive:
        print(ft("Vyčet operací:"))
        for operace in config.jednotlive:
            print(f"ft({option_number}) {operace.nazev} ){operace.url}")
            options[option_number] = operace
            option_number += 1

    if config.sekvence:
        print(ft("Vyčet sekvencí:"))
        for sekvence in config.sekvence:
            print(ft(f"{option_number}) {sekvence.nazev}"))
            for krok in sekvence.kroky:
                print(f"{option_number}.{krok.id}) {krok.url}")
            options[option_number] = sekvence
            option_number += 1
    print (f"Ostatni:")
    print(f"{option_number}). Zpět do hlavního menu")
    options[option_number] = "exit"

    choice = input(f"Enter your choice (1-{option_number} or 'exit'): ").strip().lower()
    if choice.isdigit():
        choice = int(choice)
        if choice in options:
            if options[choice] == "exit":
                return
            else:
                selected_option = options[choice]
                print(f"Selected option: {selected_option.nazev}")
                # Process the selected option
        else:
            print("Invalid choice. Please try again.")
    elif choice == "exit":
        return
    else:
        print("Invalid input. Please enter a number or 'back'.")

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
                print(f"Selected configuration: {selected_config.nazev}")
                volbaOperaci(selected_config)
                # Process the selected configuration
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
