from database.db_manager import DatabaseManager
from controller.auth import check_credentials, register_user

class Controller:
    def __init__(self, db_path):
        """Initialize the controller with the database path."""
        self.db = DatabaseManager(db_path)

    # User Management
    def create_user(self, username, password):
        """Create a new user."""
        self.db.add_user(username, password)

    def authenticate_user(self, username, password):
        """Check if a user exists with the given credentials."""
        user = self.db.get_user(username)
        return user and user[1] == password

    # Task Management
    def add_task(self, user_id, title, description, deadline, difficulty):
        """Add a task for a user."""
        self.db.add_task(user_id, title, description, deadline, difficulty)

    def delete_task(self, task_id):
        """Delete a task by ID."""
        self.db.delete_task(task_id)

    def update_task(self, task_id, title, description, deadline, difficulty):
        """Update a task in the database"""
        self.db.update_task(task_id, title, description, deadline, difficulty)

    def get_tasks(self, user_id):
        """Retrieve all tasks for a user."""
        return self.db.get_tasks(user_id)

    def get_task_by_id(self, task_id):
        """Return a task by its ID."""
        task_data = self.db.get_task_by_id(task_id)
        if task_data:
            return task_data
        else:
            raise ValueError(f"Task with ID {task_id} not found.")

    def login(self, username, password):
        """Login method to check user credentials."""
        if self.authenticate_user(username, password):
            print("Autentificare reușită!")
        else:
            print("Autentificare eșuată!")

    def signup(self, username, password):
        """Signup method to register a new user."""
        if self.create_user(username, password):
            print("Înregistrare reușită!")
        else:
            print("Utilizatorul există deja!")

    def get_tasks_by_date(self, date, username):
        """Return tasks that are due on the selected date
        :param username:
        """
        query = """
        SELECT * FROM tasks WHERE deadline = ?
        """
        return self.db.execute_query(query, (date,))

    def estimate_task_duration(self, task_type, difficulty):
        """Estimate task duration using the ML model."""
        from ml.predictor import load_model, prepare_input, predict_task_duration

        model_path = "ml/models/task_duration.pkl"
        model = load_model(model_path)

        # Obtain the model characteristics
        task_types_columns = list(model.feature_names_in_)

        # prepare the input
        input_data = prepare_input(task_type, difficulty, task_types_columns)

        # prediction
        return predict_task_duration(model, input_data)


