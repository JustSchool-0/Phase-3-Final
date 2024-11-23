class Recipe:
    connection = None

    def __init__(self, name: str, ingredients: str, category, recipe_id: int = -1):
        self._name = name
        self._ingredients = ingredients
        self._category = category
        self._id = recipe_id

    @staticmethod
    def set_connection(connection):
        Recipe.connection = connection

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        self._name = value

    @property
    def ingredients(self):
        return self._ingredients

    @ingredients.setter
    def ingredients(self, value):
        if not isinstance(value, str):
            raise TypeError("ingredients must be a string")
        self._ingredients = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        from category import Category
        if not isinstance(value, Category):
            raise TypeError("category must be a Category")
        self._category = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int) or value < 0:
            raise TypeError("id must be a int greater than 0")
        self._id = value

    def save(self):
        """
        Saves the recipe to the database. If the recipe already exists, it updates it.
        """
        if not Recipe.connection:
            raise ConnectionError("Database connection is not set.")

        cursor = Recipe.connection.cursor()

        # Insert or update the recipe
        cursor.execute(
            """
            INSERT OR REPLACE INTO recipes (name, ingredients, category_id)
            VALUES (?, ?, ?)
            """,
            (self._name, self._ingredients, self._category.id)
        )

        # Commit the changes to the database
        Recipe.connection.commit()

    def delete(self):
        """
        Deletes the recipe from the database.
        """
        if not Recipe.connection:
            raise ConnectionError("Database connection is not set.")

        cursor = Recipe.connection.cursor()

        # Delete the recipe by its name
        cursor.execute("DELETE FROM recipes WHERE name = ?", (self._name,))

        # Commit the changes to the database
        Recipe.connection.commit()
