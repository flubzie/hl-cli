from typing import Any

from colorama import init, Fore, Style
init(autoreset=True)


def hprint(msg: str, color: str) -> None:
    colors = {
        'GREEN': Fore.LIGHTGREEN_EX,
        'RED': Fore.LIGHTRED_EX,
        'YELLOW': Fore.YELLOW,
        'BLUE': Fore.BLUE,
        'MAGENTA': Fore.MAGENTA,
        'CYAN': Fore.CYAN,
        'WHITE': Fore.WHITE,
    }
    print(f'{colors[color]}{msg}{Fore.RESET}')

def get_element_by_value(data: list, key: str, value: Any) -> None:
    return next(
        (item for item in data if item.get(key) == value),
        None
    )
        
def help(cli, arg):
    if arg:
        print('Unknown command:', arg)
        print('Type "help" for a list of available commands.')
    else:
        print("Available commands:")
        
        # Get the list of method names
        method_names = cli.get_names()
        
        # Filter and print the commands
        commands = [name[3:] for name in method_names if name.startswith('do_')]
        for command in commands:
            print(f"  {command}")
        
        print("Type '<command> --help' for detailed argument information.")
