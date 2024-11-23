# lib/cli.py

import sqlite3
from sqlite3 import Connection
from typing import List

from category import Category
from helpers import exit_program, clear_console
from recipe import Recipe


def __init__(self):
    self.connection = None


def menu_main():
    clear_console()
    print("MAIN MENU")
    print("Please choose an option:")
    print("0. Exit program")
    print("1. View recipes")

    choice = input("> ")
    if choice == "0":
        exit_program()
    elif choice == "1":
        menu_categories()
    else:
        menu_main()


def menu_categories():
    option_count: int = 3

    clear_console()
    print("CATEGORIES")
    print("Please choose an option:")
    print("0. Go back")
    print("1. Add recipe")
    print("2. Delete category")

    index: int = option_count
    categories: List[Category] = Category.get_all()

    # List all categories
    for c in categories:
        print(f"{index}. {c.name}")
        index += 1

    choice: str = input("> ")
    if choice == "0":  # Back to main menu
        menu_main()
    elif choice == "1":
        menu_add_recipe()  # To add recipe menu
    elif choice == "2":
        menu_delete_category(categories)  # To delete category menu
    else:
        try:
            selected: int = int(choice)
            if selected >= (len(categories) + option_count):
                raise IndexError

            i: int = selected - option_count
            category: Category = categories[i]
            menu_recipes(category)
        except IndexError:
            menu_categories()


def menu_recipes(category: Category):
    option_count: int = 2

    clear_console()
    print(f"{category.name.upper()} RECIPES")
    print("Please choose an option:")
    print("0. Go back")
    print("1. Add recipe")

    index: int = option_count
    recipes: List[Recipe] = category.recipes
    # List all recipes in this category
    for r in recipes:
        print(f"{index}. {r.name}")
        index += 1

    choice: str = input("> ")
    if choice == "0":  # Back to categories menu
        menu_categories()
    elif choice == "1":  # To add recipe menu
        menu_add_recipe(category)
    else:
        try:
            # Account for the indices before we started listing recipes
            i: int = int(choice) - option_count
            recipe: Recipe = recipes[i]
            menu_recipe_details(recipe, category)
        except IndexError:
            menu_recipes(category)


def menu_recipe_details(recipe: Recipe, category: Category):
    clear_console()

    print("RECIPE DETAILS")
    print("Please choose an option:")
    print("0. Go back")
    print("1. Update recipe")
    print("2. Delete recipe")
    print(f"Name: {recipe.name}")
    print(f"Ingredients: {recipe.ingredients}")
    print(f"Category: {recipe.category.name}")

    choice = input("> ")
    if choice == "0":  # Back to categories menu
        menu_recipes(category)
    elif choice == "1":  # To update recipe menu
        menu_update_recipe(recipe, category)
    elif choice == "2":  # Delete this recipe, then back to categories menu
        recipe.delete()
        category.remove_recipe(recipe)
        category.save()
        menu_recipes(category)
    else:
        menu_recipe_details(recipe, category)


def menu_add_recipe(category: Category = None):
    clear_console()

    print("ADDING RECIPE")

    new_name: str = input("Please enter recipe name: ")
    new_ingredients: str = input("Please enter recipe ingredients: ")
    new_category: Category

    # If adding from the category menu
    if not category:
        # Ask user for category name
        c_name: str = ""
        while True:
            c_name = input("Please enter recipe category: ")
            if c_name:
                break
            else:
                print("Category cannot have empty name!")

        # Look for existing category with the given name
        new_category = Category.get_by_name(c_name)

        # If the category the user specified doesn't exist, create it
        if not new_category:
            new_category = Category(c_name)

    # Else adding from the recipe menu
    else:
        new_category = category

    # Create recipe object & add it to the category
    recipe: Recipe = Recipe(new_name, new_ingredients, new_category)
    new_category.add_recipe(recipe)
    new_category.save()

    # Show the details of the recipe we just added
    menu_recipe_details(recipe, new_category)


def menu_update_recipe(recipe: Recipe, category: Category):
    clear_console()

    print(f"UPDATING {recipe.name.upper()} RECIPE")

    new_name: str = input(
        "Please enter recipe name (leave blank to keep original): "
    )
    new_ingredients: str = input(
        "Please enter recipe ingredients (leave blank to keep original): "
    )
    c_name: str = input(
        "Please enter recipe category (leave blank to keep original): "
    )

    if new_name:
        recipe.name = new_name
    if new_ingredients:
        recipe.ingredients = new_ingredients
    if c_name:
        category.remove_recipe(recipe)
        # Check the db for a category with the user
        # provided name, otherwise create a new category
        category = Category.get_by_name(c_name)
        if not category:
            category = Category(c_name)
        recipe.category = category

    recipe.save()

    menu_recipe_details(recipe, category)


def menu_delete_category(categories: List[Category]):
    option_count: int = 1

    clear_console()
    print("DELETE CATEGORY")
    print("Please choose a category to delete or enter 0 to cancel: ")

    index: int = option_count
    for c in categories:
        print(f"{index}. {c.name}")
        index += 1

    choice: str = input("> ")
    if choice == "0":
        menu_categories()
    else:
        try:
            i = int(choice) - 1
            category_to_delete: Category = categories[i]
            if category_to_delete:
                category_to_delete.delete()
        except IndexError:
            menu_delete_category(categories)

        menu_categories()


# Create tables if they don't exist
# noinspection SqlNoDataSourceInspection
def create_tables(connection: Connection):
    create_categories_table = """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """

    create_recipes_table = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        ingredients TEXT NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );
    """

    cursor = connection.cursor()
    cursor.execute(create_categories_table)
    cursor.execute(create_recipes_table)
    connection.commit()


def run():
    # Connect to SQLite database
    connection: Connection = sqlite3.connect("recipes.db")
    try:
        # Create tables if they don't exist
        create_tables(connection)

        Category.set_connection(connection)
        Recipe.set_connection(connection)

        # Create category and add recipe
        category: Category = Category("Sweets")
        category.add_recipe(Recipe("Cake", "Flour, eggs, milk", category))
        category.add_recipe(
            Recipe("Pumpkin Pie", "Flour, eggs, milk, pumpkin", category)
        )
        category.save()
        category: Category = Category("Meats")
        category.add_recipe(Recipe("Bacon", "Pig", category))
        category.add_recipe(Recipe("Steak", "Cow", category))
        category.add_recipe(Recipe("Fried Chicken", "Chicken, breading", category))
        category.save()
        category: Category = Category("Baked Goods")
        category.add_recipe(Recipe("Bread", "Flour, water, yeast", category))
        category.save()
        category: Category = Category("Breakfast")
        category.add_recipe(Recipe("Pancakes", "Flour, sugar, milk", category))
        category.add_recipe(Recipe("Waffles", "Flour, sugar, milk", category))
        category.add_recipe(Recipe("Oatmeal", "Oats, salt, water", category))
        category.save()

        menu_main()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    run()
