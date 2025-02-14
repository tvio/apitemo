import os

def ft(text, color="black"):
    colors = {
        'black': '90',    # Bright black (gray)
        'red': '91',      # Bright red
        'green': '92',    # Bright green
        'yellow': '93',   # Bright yellow
        'blue': '94',     # Bright blue
        'magenta': '95',  # Bright magenta
        'cyan': '96',     # Bright cyan
        'white': '97'     # Bright white
    }
    
    color_code = colors.get(color.lower(), '97')  # Default to bright white if color not found
    return f"\033[1;{color_code}m{text}\033[0m"

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')

# Example usage:
if __name__ == "__main__":
    print(ft("This is bold green text", "green"))
    print(ft("This is bold blue text", "blue"))
    print(ft("This is bold red text", "red"))
    print(ft("This is bold black text", "black"))
    print(ft("This is bold white text", "white"))
    print(ft("This is bold yellow text", "yellow"))
    print(ft("This is bold magenta text", "magenta"))
    print(ft("This is bold cyan text", "cyan"))
