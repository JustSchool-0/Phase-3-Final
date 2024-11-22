# lib/cli.py

from helpers import exit_program, helper_1, clear_console

from models import DatabaseManager, RecipeCategory, Recipe

db_manager = DatabaseManager()
category_model = RecipeCategory(db_manager)
recipe_model = Recipe(db_manager)


def setup():
    try:
        recipe_model.add_recipe("Chicken Noodle", category_name="Soups")
        recipe_model.add_recipe("Carrot", category_name="Soups")
        recipe_model.add_recipe("Lentil", category_name="Soups")

        recipe_model.add_recipe("Fish", category_name="Meats")
        recipe_model.add_recipe("Steak", category_name="Meats")
        recipe_model.add_recipe("Bacon", category_name="Meats")

        recipe_model.add_recipe("Pancake", category_name="Breakfast")
        recipe_model.add_recipe("Waffle", category_name="Breakfast")
        recipe_model.add_recipe("Oatmeal", category_name="Breakfast")

        recipe_model.add_recipe("Pumpkin Pie", category_name="Desserts")
        recipe_model.add_recipe("Brownie", category_name="Desserts")
    except ValueError as e:
        print(e)


def main():
    setup()
    menu()


def menu():
    clear_console()
    print("Please select an option:")
    print("0. Exit the program")
    print("1. View recipes")

    choice = input("> ")
    if (choice == "0"):
        exit_program()
    elif (choice == "1"):
        category_menu()


def category_menu():
    clear_console()
    print("Please select an option:")
    print("0. Go back")
    print("1. Add recipe")

    # for each of all categories, print(f"{index}. {category_name}")
    # start at index 2 to account for other available actions
    category_dict = {}
    index = 2
    for category_id, category_name in category_model.get_categories():
        category_dict.update({f"{index}": category_name})
        print(f"{index}. {category_name}")
        index += 1

    def callback(choice):
        if (choice == "1"):
            add_recipe_menu(None)
        else:
            name = category_dict.get(choice)
            recipe_menu(category_name=name)

    await_input(menu, callback, index)


def recipe_menu(category_name):
    clear_console()
    print("Please select an option:")
    print("0. Go back")
    print("1. Add recipe")

    # for each recipe in category, print(f"{index}. {recipe_name}")
    # start at index 2 to account for other available actions
    recipe_dict = {}
    index = 2
    for recipe in recipe_model.get_recipes_by_category_name(category_name):
        recipe_name = recipe[1]
        recipe_obj = {"id": recipe[0], "name": recipe_name, "ingredients": recipe[2]}
        recipe_dict.update({f"{index}": recipe_obj})
        print(f"{index}. {recipe_name}")
        index += 1

    def callback(choice):
        if (choice == "1"):
            add_recipe_menu(category_name)
        else:
            recipe = recipe_dict.get(choice)
            recipe_info(recipe["id"], recipe["name"], recipe["ingredients"], category_name)

    await_input(category_menu, callback, index)


def recipe_info(id, name, ingredients, category_name):
    clear_console()
    print("Please select an option:")
    print("0. Go back")
    print("1. Update recipe")
    print("2. Delete recipe")
    print(f"Name: {name}")
    print(f"Ingredients: {ingredients}")
    print(f"Category: {category_name}")

    def else_callback(choice):
        if (choice == "1"):
            print("Please enter a new recipe name: ")
            temp_name = input("> ")
            print("Please enter new recipe ingredients: ")
            temp_ingredients = input("> ")

            updated_name = name if not temp_name else temp_name
            updated_ingredients = (
                ingredients if not temp_ingredients else temp_ingredients
            )

            recipe_model.update_recipe(id, updated_name, updated_ingredients)
            recipe_info(id, updated_name, updated_ingredients, category_name)
        if (choice == "2"):
            recipe_model.delete_recipe(id)
            # Take the user all the way back the category manu to
            # account for the possibility that this recipe's category 
            # was also deleted
            category_menu()

    def back_callback():
        recipe_menu(category_name)

    await_input(back_callback, else_callback, 3)

def add_recipe_menu(category_name):
    clear_console()

    # Name
    name = ""
    while not name:
        print("Please enter recipe name: ")
        name = input("> ")

    # Ingredients
    ingredients = ""
    while not ingredients:
        print("Please enter recipe ingredients: ")
        ingredients = input("> ")

    # Category
    category = category_name
    while not category:
        print("Please enter recipe category: ")
        category = input("> ")

    recipe_model.add_recipe(name, category, ingredients)
    if (not category_name):
        category_menu()
    else:
        recipe_menu(category_name)


def await_input(back_callback, else_callback, option_count):
    choice = input("> ")
    if (choice == "0"):
        back_callback()
    elif (int(choice) < 0) or (int(choice) >= option_count):
        print("Invalid input!")
        await_input(back_callback, else_callback, option_count)
    else:
        else_callback(choice)


if __name__ == "__main__":
    main()
