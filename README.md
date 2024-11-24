# CLI Recipe Management App

Users may view, add, update, delete, & categorize recipes as they wish. All of this can be done with zero hassle in a clean, readable CLI.

## How to Run

- Clone from GitHub
- cd to project root
- Run `python lib/cli.py`

## Project Requirements

Below are code snippets from this project demonstrating each requirement that has been met.

### ORM Requirements

- The application must include a database created and modified with Python ORM methods that you write.

  ```py
  def run():
      # Connect to SQLite database
      connection: Connection = sqlite3.connect("recipes.db")
  ```

- The data model must include at least 2 model classes.

  ```
  Category
  Recipe
  ```

- The data model must include at least 1 one-to-many relationship.

  ```
  One Category to many Recipes
  ```

- Property methods should be defined to add appropriate constraints to each model class.

  ```py
  class Recipe:

  def __init__(self, name: str, ingredients: str, category, recipe_id: int = -1):
      self._name = name
      self._ingredients = ingredients
      self._category = category
      self._id = recipe_id

  @property
  def name(self):
      return self._name

  @name.setter
  def name(self, value):
      if not isinstance(value, str):
          raise TypeError("name must be a string")
      self._name = value
  ```

- Each model class should include ORM methods (create, delete, get all, and find by id at minimum).

  ```py
    # Create & update in one method!
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
  def get_by_id(category_id: int):
      """
      Retrieves a category by its ID from the database, along with its associated recipes.
      """
      if not isinstance(category_id, int):
          raise TypeError("category_id must be an integer")

      return Category._fetch_category_with_recipes(category_id=category_id)
  ```

### CLI Requirements

No code snippets can be shown for most these as they are not specifically related to code.

- The CLI must display menus with which a user may interact.
- The CLI should use loops as needed to keep the user in the application until they choose to exit.
- For EACH class in the data model, the CLI must include options: to create an object, delete an object, display all objects, view related objects, and find an object by attribute.
- The CLI should validate user input and object creations/deletions, providing informative errors to the user.

  ```py
    choice: str = input("> ")
    if choice == "0":  # Back to main menu
        menu_main()
    elif choice == "1":
        menu_add_recipe()  # To add recipe menu
    elif choice == "2":
        menu_delete_category(categories)  # To delete category menu
    else:
        try:
            # Validate user input
            selected: int = int(choice)
            if selected >= (len(categories) + option_count):
                raise IndexError

            i: int = selected - option_count
            category: Category = categories[i]
            menu_recipes(category)
        except IndexError:
            menu_categories()
  ```

- The project code should follow OOP best practices.
- Pipfile contains all needed dependencies and no unneeded dependencies.

  ```
  [[source]]
  url = "https://pypi.org/simple"
  verify_ssl = true
  name = "pypi"

  [requires]
  python_version = "3.8.13"

  ```

- Imports are used in files only where necessary.
- Project folders, files, and modules should be organized and follow appropriate naming conventions.
- The project should include a README.md that describes the application.
