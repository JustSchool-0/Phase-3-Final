import sqlite3


class DatabaseManager:
    def __init__(self, db_name="recipes.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables if they don't already exist."""
        with self.connection:
            # Create recipe_categories table
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recipe_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """
            )

            # Create recipes table
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES recipe_categories (id)
                )
            """
            )
