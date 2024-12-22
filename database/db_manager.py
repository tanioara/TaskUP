import os
import sqlite3

class DatabaseManager:

    def __init__(self, db_path):
        """Initialize the database connection."""
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=()):
        """Execute a query and return the results."""
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.fetchall()

    def execute_insert(self, query, params=()):
        """Execute an insert query."""
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid


    def get_tasks(self, user_id):
        """Retrieve tasks for a user by user_id."""
        query = "SELECT id, title, description, deadline, difficulty FROM tasks WHERE user_id = ?"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def close(self):
        """Close the connection to the database."""
        if self.connection:
            self.connection.close()

    def setup_database(self):
        """Set up the database schema by executing the schema.sql file."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file '{schema_path}' not found.")

        with open(schema_path, "r") as schema_file:
            schema_script = schema_file.read()
        try:
            with self.connection:
                self.connection.executescript(schema_script)
        except sqlite3.Error as e:
            raise RuntimeError(f"Error executing schema script: {e}")

    def add_user(self, username, password):
        """Add a new user to the database."""
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?);",
                    (username, password)
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"User '{username}' already exists.")

    def get_user(self, username):
        """Retrieve user information by username."""
        cursor = self.connection.execute(
            "SELECT id, username, password FROM users WHERE username = ?;",
            (username,)
        )
        user = cursor.fetchone()
        return user  # Returns None if user does not exist.

    def add_task(self, user_id, title, description, deadline, difficulty):
        """Add a new task for a user."""
        try:
            with self.connection:
                self.connection.execute('''
                    INSERT INTO tasks (user_id, title, description, deadline, difficulty)
                    VALUES (?, ?, ?, ?, ?);
                ''', (user_id, title, description, deadline, difficulty))
        except sqlite3.Error as e:
            raise RuntimeError(f"Error adding task: {e}")

    def delete_task(self, task_id):
        """Delete a task by its ID."""
        try:
            with self.connection:
                self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        except sqlite3.Error as e:
            raise RuntimeError(f"Error deleting task: {e}")

    def update_task(self, task_id, title, description, deadline, difficulty):
        """Update a task's information."""
        try:
            with self.connection:
                self.cursor.execute("""UPDATE tasks
                                       SET title = ?, description = ?, deadline = ?, difficulty = ?
                                       WHERE id = ?""",
                                     (title, description, deadline, difficulty, task_id))
        except sqlite3.Error as e:
            raise RuntimeError(f"Error updating task: {e}")

    def get_task_by_id(self, task_id):
        """Retrieve a task from the database using its ID."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        return task  # Returnează taskul găsit sau None dacă nu există

def get_tasks_by_date(self, date, user_id):
    query = '''
        SELECT id, title, description, deadline, difficulty 
        FROM tasks 
        WHERE deadline = ? AND user_id = ?
    '''
    tasks = self.execute_query(query, (date, user_id))
    print(f"Tasks fetched for user_id={user_id} and date={date}: {tasks}")
    return tasks

    def get_id(self, name):
        """Retrieve the user ID based on the username."""
        query = "SELECT id FROM users WHERE username = ?"
        result = self.execute_query(query, (name,))
        return result[0][0] if result else None


