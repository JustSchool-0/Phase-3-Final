# lib/helpers.py

from os import system, name


def helper_1():
    print("Performing useful function#1.")


def exit_program():
    print("Goodbye!")
    exit()


def clear_console():
    # for windows
    if name == "nt":
        _ = system("cls")

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")
