# lib/helpers.py

from os import system, name


def exit_program():
    clear_console()
    print("Goodbye!")
    exit()


def clear_console():
    # for windows
    if name == "nt":
        _ = system("cls")

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")
