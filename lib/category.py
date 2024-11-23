from typing import List


class Category:
    connection = None

    def __init__(self, name, recipes=None, category_id: int = -1):
        if recipes is None:
            recipes = []
        self._name = name
        self._recipes = recipes
        self._id = category_id

    @staticmethod
    def set_connection(connection):
        Category.connection = connection

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        self._name = value

    @property
    def recipes(self):
        return self._recipes

    @recipes.setter
    def recipes(self, value: list):
        if not isinstance(value, list):
            raise TypeError("recipes must be a list")
        self._recipes = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise TypeError("id must be a integer and greater than 0")
        self._id = value

    def add_recipe(self, recipe):
        from recipe import Recipe
        if not isinstance(recipe, Recipe):
            raise TypeError("recipe must be a Recipe")
        self._recipes.append(recipe)

    def remove_recipe(self, recipe):
        from recipe import Recipe
        if not isinstance(recipe, Recipe):
            raise TypeError("recipe must be a Recipe")
        self._recipes.remove(recipe)

    def remove_recipe_by_name(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        self._recipes = [recipe for recipe in self._recipes if recipe.name != name]

    def get_associated_recipes(self):
        """
        Retrieves all recipes associated with this category from the database.
        """
        if not Category.connection:
            raise ConnectionError("Database connection is not set.")

        cursor = Category.connection.cursor()
        cursor.execute(
            "SELECT id, name, ingredients FROM recipes WHERE category_id = (SELECT id FROM categories WHERE name = ?)",
            (self._name,)
        )
        rows = cursor.fetchall()

        from recipe import Recipe
        self._recipes = [Recipe(name=row[1], ingredients=row[2], category=self) for row in rows]
        return self._recipes

    def save(self):
        """
        Saves the category to the database. If the category already exists, it updates it.
        Additionally, saves all associated recipes to the database.
        """
        if not Category.connection:
            raise ConnectionError("Database connection is not set.")

        cursor = Category.connection.cursor()

        # Save the category
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            (self._name,)
        )
        # Fetch the category ID (after insertion or if it already exists)
        cursor.execute("SELECT id FROM categories WHERE name = ?", (self._name,))
        category_id = cursor.fetchone()[0]

        # Save each associated recipe
        from recipe import Recipe
        for recipe in self._recipes:
            if not isinstance(recipe, Recipe):
                raise TypeError("All associated recipes must be instances of Recipe.")

            cursor.execute(
                """
                INSERT OR REPLACE INTO recipes (name, ingredients, category_id)
                VALUES (?, ?, ?)
                """,
                (recipe.name, recipe.ingredients, category_id)
            )

        # Commit the changes to the database
        Category.connection.commit()

    def delete(self):
        """
        Deletes the category from the database.
        """
        Category.delete_by_name(self._name)

    @staticmethod
    def get_all():
        """
        Retrieves all categories from the database along with their associated recipes.
        """
        if not Category.connection:
            raise ConnectionError("Database connection is not set.")

        cursor = Category.connection.cursor()

        # Fetch all categories
        cursor.execute("SELECT id, name FROM categories")
        category_rows = cursor.fetchall()

        categories: List[Category] = []
        for category_row in category_rows:
            category: Category = Category._fetch_category_with_recipes(category_id=category_row[0])
            categories.append(category)

        return categories

    @staticmethod
    def get_by_name(category_name: str):
        """
        Retrieves a category by its name from the database, along with its associated recipes.
        """
        if not isinstance(category_name, str):
            raise TypeError("category_name must be a string")

        return Category._fetch_category_with_recipes(category_name=category_name)

    @staticmethod
    def get_by_id(category_id: int):
        """
        Retrieves a category by its ID from the database, along with its associated recipes.
        """
        if not isinstance(category_id, int):
            raise TypeError("category_id must be an integer")

        return Category._fetch_category_with_recipes(category_id=category_id)

    @staticmethod
    def delete_by_name(category_name: str):
        """
        Deletes a category by its name and all its associated recipes from the database.
        """
        if not Category.connection:
            raise ConnectionError("Database connection is not set.")

        if not isinstance(category_name, str):
            raise TypeError("category_name must be a string")

        cursor = Category.connection.cursor()

        # Fetch the category by name to get its ID
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category_row = cursor.fetchone()

        if not category_row:
            raise ValueError("Category not found")

        category_id = category_row[0]

        # Delete all associated recipes
        cursor.execute("DELETE FROM recipes WHERE category_id = ?", (category_id,))

        # Delete the category
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))

        # Commit the changes to the database
        Category.connection.commit()

    @staticmethod
    def _fetch_category_with_recipes(category_id: int = None, category_name: str = None):
        """
        Fetches a category by its ID or name along with its associated recipes.
        Either category_id or category_name must be provided.
        """
        if not Category.connection:
            raise ConnectionError("Database connection is not set.")

        if category_id is None and category_name is None:
            raise ValueError("Either category_id or category_name must be provided")

        cursor = Category.connection.cursor()

        # Fetch the category based on provided argument
        if category_id:
            cursor.execute("SELECT id, name FROM categories WHERE id = ?", (category_id,))
        else:
            cursor.execute("SELECT id, name FROM categories WHERE name = ?", (category_name,))

        category_row = cursor.fetchone()
        if not category_row:
            return None  # Category not found

        category_id, category_name = category_row

        # Fetch associated recipes
        cursor.execute(
            "SELECT id, name, ingredients FROM recipes WHERE category_id = ?",
            (category_id,)
        )
        recipe_rows = cursor.fetchall()

        from recipe import Recipe

        # Create Recipe objects for each associated recipe
        recipes: List[Recipe] = [
            Recipe(name=row[1], ingredients=row[2], category=None) for row in recipe_rows
        ]

        # Create the Category object
        category: Category = Category(name=category_name, recipes=recipes, category_id=category_id)

        # Update each recipe's `category` reference to the new Category object
        for recipe in recipes:
            recipe.category = category

        return category
