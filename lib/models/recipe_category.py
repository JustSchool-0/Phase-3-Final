class RecipeCategory:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_category(self, name):
        """Add a new recipe category."""
        with self.db_manager.connection:
            self.db_manager.connection.execute(
                "INSERT INTO recipe_categories (name) VALUES (?)", (name,)
            )

    def get_categories(self):
        """Retrieve all recipe categories."""
        with self.db_manager.connection:
            return self.db_manager.connection.execute(
                "SELECT id, name FROM recipe_categories"
            ).fetchall()
