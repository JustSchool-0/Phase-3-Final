class Recipe:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_category_id_by_name(self, category_name):
        """Retrieve the category ID by its name."""
        with self.db_manager.connection:
            result = self.db_manager.connection.execute(
                "SELECT id FROM recipe_categories WHERE name = ?", (category_name,)
            ).fetchone()
            return result[0] if result else None

    def add_recipe(self, title, category_name=None, ingredients="Tasty Stuffs"):
        """Add a new recipe, ensuring the title is unique (fails softly)."""
        # Check if the recipe title already exists
        with self.db_manager.connection:
            existing_recipe = self.db_manager.connection.execute(
                "SELECT id FROM recipes WHERE title = ?", (title,)
            ).fetchone()
        
        if existing_recipe:
            #print(f"Recipe '{title}' already exists. Skipping insertion.")
            return  # Soft fail by skipping the insert if the title already exists
        
        category_id = None
        if category_name:
            # Check if the category exists
            category_id = self.get_category_id_by_name(category_name)
            
            if category_id is None:
                # Create the category if it doesn't exist
                with self.db_manager.connection:
                    self.db_manager.connection.execute(
                        "INSERT INTO recipe_categories (name) VALUES (?)",
                        (category_name,)
                    )
                    # Get the ID of the newly created category
                    category_id = self.get_category_id_by_name(category_name)
                    #print(f"Category '{category_name}' created with ID {category_id}.")

        # Insert the recipe with the ingredients
        with self.db_manager.connection:
            self.db_manager.connection.execute(
                """
                INSERT INTO recipes (title, category_id, ingredients)
                VALUES (?, ?, ?)
                """,
                (title, category_id, ingredients),
            )
            #print(f"Recipe '{title}' added to category '{category_name}'.")

    def get_recipes(self):
        """Retrieve all recipes with their categories and ingredients."""
        with self.db_manager.connection:
            return self.db_manager.connection.execute(
                """
                SELECT recipes.id, recipes.title,
                       recipe_categories.name as category, recipes.ingredients
                FROM recipes
                LEFT JOIN recipe_categories
                ON recipes.category_id = recipe_categories.id
                """
            ).fetchall()

    def get_recipes_by_category_name(self, category_name):
        """Retrieve all recipes belonging to a specific category by category name."""
        category_id = self.get_category_id_by_name(category_name)
        if category_id is None:
            raise ValueError(f"Category '{category_name}' does not exist.")
        
        with self.db_manager.connection:
            return self.db_manager.connection.execute(
                """
                SELECT recipes.id, recipes.title, recipes.ingredients
                FROM recipes
                WHERE category_id = ?
                """,
                (category_id,)
            ).fetchall()

    def delete_recipe(self, recipe_id):
        """Delete a recipe by its ID and delete the category if it's empty."""
        with self.db_manager.connection:
            # Get the category ID of the recipe to be deleted
            recipe = self.db_manager.connection.execute(
                "SELECT category_id FROM recipes WHERE id = ?", (recipe_id,)
            ).fetchone()

            if not recipe:
                #print(f"Recipe with ID {recipe_id} not found.")
                return

            category_id = recipe[0]

            # Delete the recipe
            self.db_manager.connection.execute(
                "DELETE FROM recipes WHERE id = ?", (recipe_id,)
            )
            #print(f"Recipe with ID {recipe_id} deleted.")

            # Check if there are any remaining recipes in the same category
            remaining_recipes = self.db_manager.connection.execute(
                "SELECT id FROM recipes WHERE category_id = ?", (category_id,)
            ).fetchall()

            if not remaining_recipes:
                # If no recipes are left in the category, delete the category
                self.db_manager.connection.execute(
                    "DELETE FROM recipe_categories WHERE id = ?", (category_id,)
                )
                #print(f"Category with ID {category_id} deleted because it is empty.")

    def update_recipe(self, recipe_id, new_title, new_ingredients):
        """Update the title and ingredients of an existing recipe."""
        with self.db_manager.connection:
            # Check if the recipe exists
            existing_recipe = self.db_manager.connection.execute(
                "SELECT id FROM recipes WHERE id = ?", (recipe_id,)
            ).fetchone()

            if not existing_recipe:
                #print(f"Recipe with ID {recipe_id} not found.")
                return

            # Update the recipe with the new title and ingredients
            self.db_manager.connection.execute(
                """
                UPDATE recipes
                SET title = ?, ingredients = ?
                WHERE id = ?
                """,
                (new_title, new_ingredients, recipe_id)
            )
            #print(f"Recipe with ID {recipe_id} updated to '{new_title}' with ingredients '{new_ingredients}'.")
