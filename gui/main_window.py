import sqlite3

import requests
from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QFrame, QCalendarWidget, QStackedWidget, QTableWidget, QTableWidgetItem, QDateEdit, QSpacerItem, \
    QSizePolicy, QSplitter, QCheckBox, QGroupBox

from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QTimer, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPixmap
from fastapi_cli import logging

from controller.controller import Controller
from controller.auth import check_credentials, register_user
from functools import partial

class TaskUPApp(QWidget):
    def __init__(self, db_path):
        super().__init__()
        print("Initializing TaskUPApp")
        self.db_path = db_path
        self.setWindowTitle("TaskUP")
        self.setGeometry(100, 100, 1024, 768)
        self.controller = Controller(db_path)

        self.setup_styles()
        self.create_main_layout()
        self.create_sidebar()
        self.create_main_content()
        self.show_login_view()

        self.calendar_widget = None
        self.tasks_layout = QVBoxLayout()

    def setup_styles(self):
        """Apply styles to the app"""
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-family: 'Arial', sans-serif;
            color: #333;

            /* Stiluri pentru tabel */
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 4px;
            }

            QTableWidget::item {
                padding: 8px;
                font-size: 14px;
                border-bottom: 1px solid #eee;
            }

            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }

            QTableWidget::horizontalHeader {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                font-weight: bold;
                color: #333;
            }

            QTableWidget::verticalHeader {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                color: #333;
            }

            /* Stil pentru butoane */
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 200px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            /* Stiluri pentru etichete (label) */
            QLabel {
                font-size: 18px;
                color: #444;
                margin-bottom: 10px;
            }
        """)

    def create_main_layout(self):
        """Create the main layout for the window"""
        if self.layout() is not None:
            logging.debug("Removing existing layout")
            self.layout().deleteLater()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_sidebar(self):
        """Create the sidebar for navigation"""
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_frame.setStyleSheet("background-color: #0078D7;")
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_frame.setLayout(self.sidebar_layout)

        self.add_sidebar_button("Home", self.show_home_view)
        self.add_sidebar_button("Dashboard", self.show_dashboard_view)
        self.add_sidebar_button("Add Task", self.show_add_task_form)
        self.add_sidebar_button("View Tasks", self.show_task_list_view)
        self.add_sidebar_button("Calendar", self.show_calendar_view)
        self.add_sidebar_button("Logout", self.logout)

        self.main_layout.addWidget(self.sidebar_frame)
        self.sidebar_frame.hide()

    def add_sidebar_button(self, text, command):
        """Helper to create a sidebar button"""
        button = QPushButton(text)
        button.setStyleSheet(
            "border-radius: 15px; background-color: #0057A5; color: white; padding: 10px; margin: 5px;")
        button.clicked.connect(command)
        self.sidebar_layout.addWidget(button)

    def create_main_content(self):
        """Create the main content area"""
        self.main_content_frame = QFrame(self)
        self.main_content_frame.setStyleSheet("background-color: #ffffff;")
        self.main_content_layout = QVBoxLayout(self.main_content_frame)
        self.main_content_layout.setSpacing(20)

        self.stacked_widget = QStackedWidget(self.main_content_frame)
        self.main_content_layout.addWidget(self.stacked_widget)

        self.main_layout.addWidget(self.main_content_frame)

    def show_login_view(self):
        """Display the login screen in a centered frame with a minimalist and elegant design"""
        self.clear_main_content()

        # Create frame for login
        login_frame = QFrame()
        login_frame.setFrameShape(QFrame.StyledPanel)
        login_frame.setFrameShadow(QFrame.Raised)

        # frame styles
        login_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
            }
        """)

        # Login layout
        login_layout = QVBoxLayout()
        login_layout.setAlignment(QtCore.Qt.AlignTop)
        login_layout.setSpacing(5)
        login_layout.setContentsMargins(0, 0, 0, 0)

        # Username label and entry
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet("font-size: 13px; color: #333; margin-bottom: 2px;")
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter your username")
        self.username_entry.setFixedSize(250, 30) # Mai lungi și mai compacte

        # Password label and entry
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet("font-size: 13px; color: #333; margin-bottom: 2px;")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.setFixedSize(250, 30)

        # Butoane Login și Register
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004682;
            }
        """)
        self.login_button.setFixedHeight(35)
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #00A2E8;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0077b3;
            }
            QPushButton:pressed {
                background-color: #006094;
            }
        """)
        self.register_button.setFixedHeight(35)
        self.register_button.clicked.connect(self.register)

        # Adaugă widget-urile la layout
        login_layout.addWidget(self.username_label, alignment=QtCore.Qt.AlignLeft)
        login_layout.addWidget(self.username_entry, alignment=QtCore.Qt.AlignCenter)

        login_layout.addWidget(self.password_label, alignment=QtCore.Qt.AlignLeft)
        login_layout.addWidget(self.password_entry, alignment=QtCore.Qt.AlignCenter)

        login_layout.addSpacing(55)  # Spațiu între câmpuri și butoane
        login_layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignCenter)
        login_layout.addWidget(self.register_button, alignment=QtCore.Qt.AlignCenter)

        self.username_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        self.password_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        login_frame.setLayout(login_layout)

        login_frame.setFixedWidth(370)
        login_frame.setFixedHeight(400)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(login_frame, alignment=QtCore.Qt.AlignCenter)
        container.setStyleSheet("QWidget { background-color: #f7f7f7; }")

        layout = QVBoxLayout(self)
        layout.addWidget(container)
        self.setLayout(layout)

        self.stacked_widget.addWidget(container)
        self.stacked_widget.setCurrentWidget(container)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty!")
            return

        if check_credentials(username, password):
            self.username = username  # Setează username după autentificare
            self.current_user_id = self.controller.db.get_user(username)[0]
            QMessageBox.information(self, "Success", "Login successful!")
            # debug
            print(f"User logged in: {self.username}")
            print(f"Logged in as {username}, user_id={self.current_user_id}")

            self.show_home_view()
            # Show sidebar
            self.sidebar_frame.show()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")

    def validate_password(self, password):
        # password must contain at least 8 characters and at least a special one
        if len(password) < 8:
            return "Password must be at least 8 characters long!"
        if not any(char.isdigit() for char in password):
            return "Password must contain at least one digit!"
        if not any(char in "!@#$%^&*()-_+=<>?/|\\{}[]~`" for char in password):
            return "Password must contain at least one special character!"
        return None

    def register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty!")
            return

        password_error = self.validate_password(password)
        if password_error:
            QMessageBox.warning(self, "Error", password_error)
            return

        if register_user(username, password):
            QMessageBox.information(self, "Success", "User registered successfully!")
            self.show_registration_success_page()
        else:
            QMessageBox.warning(self, "Error", "Username already exists!")

    def show_registration_success_page(self):
        print("Navigating to registration success page...")

    def show_home_view(self):
        """Display the Home screen with animation"""
        self.clear_main_content()
        home_widget = QWidget()
        home_layout = QVBoxLayout()

        self.animated_label = QLabel()
        pixmap = QPixmap("/Users/taniapirvu/Downloads/TaskUP_WIP_St_final/gui/taskup_logo.png")
        scaled_pixmap = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.animated_label.setPixmap(scaled_pixmap)
        self.animated_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(self.animated_label)

        home_widget.setLayout(home_layout)
        self.stacked_widget.addWidget(home_widget)
        self.stacked_widget.setCurrentWidget(home_widget)

        # Start animation
        self.start_animation()

    def start_animation(self):
        """Animate the initial image and switch to the Dashboard"""
        animation = QPropertyAnimation(self.animated_label, b"windowOpacity")
        animation.setDuration(1000)  # 2 seconds
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

        # Redirect to the dashboard after the animation
        QTimer.singleShot(1000, self.show_dashboard_view)

    def show_dashboard_view(self):
        """Display the Dashboard screen"""
        self.clear_main_content()

        # Create the dashboard widget and layout
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setSpacing(15)  # Spacing between widgets for better separation

        # Create a welcome message with the username and current date
        welcome_message = QLabel(f"Welcome, {self.username}!")
        welcome_message.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #1E90FF; text-align: center; margin-bottom: 15px;"
            "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        date_today = QDate.currentDate().toString("dddd, MMMM d, yyyy")
        stats_intro_message = QLabel(f"These are your stats for today, {date_today}:")
        stats_intro_message.setStyleSheet(
            "font-size: 18px; font-weight: normal; color: #333333; text-align: center; margin-bottom: 25px;"
            "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        # Get the weather information (using wttr.in API)
        try:
            weather_response = requests.get("https://wttr.in/Bucharest?format=%C+%t+%w+%w+%h+%T")
            weather_info = weather_response.text.strip().split(" ")

            if len(weather_info) >= 5:
                weather_description = weather_info[0]  # Weather condition
                temperature = weather_info[1]  # Temperature
                wind = weather_info[2]  # Wind
                humidity = weather_info[4]  # Humidity
                time_of_update = weather_info[5]  # Last update time

                # Format the weather time to just display hour and minute
                time_parts = time_of_update.split(":")
                formatted_time = f"{time_parts[0]}:{time_parts[1]}"  # Display only hour and minute

                weather_display = f"<b>{weather_description}</b>\n" \
                                  f"<i>Temp:</i> {temperature}\n" \
                                  f"<i>Wind:</i> {wind}\n" \
                                  f"<i>Humidity:</i> {humidity}\n" \
                                  f"<i>Last updated:</i> {formatted_time}"
            else:
                weather_display = "Unable to fetch weather information correctly. Please try again later."

        except requests.RequestException as e:
            weather_display = "Unable to fetch weather information"

        # Display the weather information in a nice format
        weather_label = QLabel(f"<h3>Weather in Bucharest</h3>\n{weather_display}")
        weather_label.setStyleSheet(
            "font-size: 16px; color: #333333; text-align: center; margin-top: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        # Add the welcome message and stats intro to the layout
        dashboard_layout.addWidget(welcome_message)
        dashboard_layout.addWidget(stats_intro_message)

        # Add the weather information after the stats intro
        dashboard_layout.addWidget(weather_label)

        # Create a QGroupBox to group statistics and make them look compact
        stats_groupbox = QGroupBox()
        stats_groupbox.setStyleSheet("background-color: #f9f9f9; border-radius: 12px; padding: 20px;")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(10)

        # Statistics calculations
        total_tasks = self.get_total_tasks()
        avg_duration = self.get_avg_task_duration()
        total_duration = self.get_total_task_duration()

        # Labels for statistics
        total_tasks_label = QLabel(f"<b>Total Tasks:</b> {total_tasks}")
        total_tasks_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 10px;"
                                        "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        avg_duration_label = QLabel(f"<b>Average Task Duration:</b> {avg_duration:.2f} hours")
        avg_duration_label.setStyleSheet("font-size: 16px; color: #333333; margin-bottom: 10px;"
                                         "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        total_duration_label = QLabel(f"<b>Total Estimated Duration:</b> {total_duration:.2f} hours")
        total_duration_label.setStyleSheet("font-size: 16px; color: #333333; margin-bottom: 20px;"
                                           "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        # Encouragement text
        if total_duration > 0:
            hours_per_day = 8  # Assuming 8-hour days
            days_needed = max(1, total_duration // hours_per_day + (
                1 if total_duration % hours_per_day > 0 else 0))
            encouragement_label = QLabel(
                f"<i>You should work on these tasks {hours_per_day} hours per day. "
                f"If you start today, you'll be ready in <b>{days_needed} days</b>.</i>"
            )
        else:
            encouragement_label = QLabel("<i>Start working on your tasks to see the progress!</i>")

        encouragement_label.setStyleSheet("font-size: 16px; font-style: italic; color: #666666; margin-top: 15px;"
                                          "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;")

        # Add labels to the statistics layout
        stats_layout.addWidget(total_tasks_label)
        stats_layout.addWidget(avg_duration_label)
        stats_layout.addWidget(total_duration_label)
        stats_layout.addWidget(encouragement_label)

        stats_groupbox.setLayout(stats_layout)

        # Add the statistics QGroupBox to the dashboard layout
        dashboard_layout.addWidget(stats_groupbox)

        # Set the layout for the dashboard widget
        dashboard_widget.setLayout(dashboard_layout)

        # Set the dashboard widget to be displayed
        self.stacked_widget.addWidget(dashboard_widget)
        self.stacked_widget.setCurrentWidget(dashboard_widget)

    def get_task_type_by_id(self, task_id):
        """Obtain task type form database by task id"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM tasks WHERE id = ?", (task_id,))
        task_type = cursor.fetchone()[0]
        conn.close()
        return task_type

    def get_task_difficulty_by_id(self, task_id):
        """Obțain the difficulty of the task by task id"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT difficulty FROM tasks WHERE id = ?", (task_id,))
        difficulty = cursor.fetchone()[0]
        conn.close()
        return difficulty

    def get_total_tasks(self):
        """Returns the total number of tasks for the current user"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (self.current_user_id,))
        total_tasks = cursor.fetchone()[0]
        conn.close()
        return total_tasks

    def get_avg_task_duration(self):
        """Average task duration for the current user"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE user_id = ?", (self.current_user_id,))
        tasks = cursor.fetchall()

        total_duration = 0
        total_tasks = len(tasks)

        for task in tasks:
            task_id = task[0]
            task_type = self.get_task_type_by_id(task_id)
            difficulty = self.get_task_difficulty_by_id(task_id)

            estimated_duration = self.controller.estimate_task_duration(task_type, difficulty)

            total_duration += estimated_duration
        conn.close()

        avg_duration = total_duration / total_tasks if total_tasks > 0 else 0
        return avg_duration

    def get_total_task_duration(self):
        """Returns the total estimated duration for all tasks for the current user"""
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE user_id = ?", (self.current_user_id,))
        tasks = cursor.fetchall()

        total_duration = 0
        for task in tasks:
            task_id = task[0]
            task_type = self.get_task_type_by_id(task_id)
            difficulty = self.get_task_difficulty_by_id(task_id)

            estimated_duration = self.controller.estimate_task_duration(task_type, difficulty)

            total_duration += estimated_duration
        conn.close()

        return total_duration

    def clear_main_content(self):
        """Clear the main content area before adding a new view"""
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            widget.deleteLater()

    def logout(self):
        """Logout the user"""
        self.sidebar_frame.hide()
        self.show_login_view()

    def show_add_task_form(self):
        """Display the form to add a task"""
        self.clear_main_content()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        task_form_widget = QWidget()
        task_form_layout = QVBoxLayout()
        task_form_layout.setAlignment(Qt.AlignCenter)
        self.create_task_form_widgets(task_form_layout)

        task_form_widget.setMaximumWidth(400)
        task_form_widget.setLayout(task_form_layout)

        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(task_form_widget)
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.stacked_widget.addWidget(central_widget)
        self.stacked_widget.setCurrentWidget(central_widget)

    def create_task_form_widgets(self, layout):
        """Helper to create task form widgets"""
        title_label = QLabel("Add New Task")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        # Title field
        title_field_label = QLabel("Title:")
        self.title_entry = QLineEdit()

        # Description field
        description_field_label = QLabel("Description:")
        self.description_entry = QLineEdit()

        # Deadline field
        deadline_field_label = QLabel("Deadline:")
        self.deadline_entry = QDateEdit()
        self.deadline_entry.setCalendarPopup(True)  # Enable calendar popup
        self.deadline_entry.setDisplayFormat("yyyy-MM-dd")
        self.deadline_entry.setDate(QDate.currentDate())  # Set current date as default

        # Difficulty field
        difficulty_field_label = QLabel("Difficulty (1-5):")
        self.difficulty_entry = QLineEdit()

        # Save button
        save_button = QPushButton("Save Task")
        save_button.setFixedWidth(100)
        save_button.setStyleSheet("""
            QPushButton {
                border-radius: 10px; 
                background-color: #0078D7; 
                color: white; 
                padding: 8px;  /* Adjust padding to keep proportions */
                font-size: 12px;  /* Slightly larger font for readability */
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        save_button.clicked.connect(self.save_task)

        # Add widgets to layout with proper labels
        layout.addWidget(title_label)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        layout.addWidget(title_field_label)
        layout.addWidget(self.title_entry)

        layout.addWidget(description_field_label)
        layout.addWidget(self.description_entry)

        layout.addWidget(deadline_field_label)
        layout.addWidget(self.deadline_entry)

        layout.addWidget(difficulty_field_label)
        layout.addWidget(self.difficulty_entry)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # Center the button
        save_button_layout = QHBoxLayout()
        save_button_layout.setAlignment(Qt.AlignCenter)
        save_button_layout.addWidget(save_button)

        layout.addLayout(save_button_layout)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def save_task(self):
        title = self.title_entry.text()
        description = self.description_entry.text()
        deadline = self.deadline_entry.text()
        difficulty = self.difficulty_entry.text()

        try:
            difficulty = int(self.difficulty_entry.text())
            if difficulty < 1 or difficulty > 5:  # Validate input range (1-5)
                raise ValueError("Difficulty must be between 1 and 5.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a difficulty between 1 and 5.")
            return
        user_id = self.controller.db.get_user(self.username)[0]  # take user id

        # inserting the task into the db
        self.controller.add_task(user_id, title, description, deadline, difficulty)
        QMessageBox.information(self, "Success", "Task saved successfully!")

    def show_task_list_view(self):
        """Display all tasks for the user in a table"""
        self.clear_main_content()
        task_list_widget = QWidget()
        task_list_layout = QVBoxLayout()

        # Create a table for displaying tasks
        self.task_table = QTableWidget()

        # Get tasks from the database
        tasks = self.controller.get_tasks(self.controller.db.get_user(self.username)[0])

        if not tasks:
            QMessageBox.information(self, "No Tasks", "No tasks available.")
        else:

            self.task_table.setColumnCount(7)

            self.task_table.setHorizontalHeaderLabels(
                ["Title", "Description", "Deadline", "Difficulty", "Actions", "Predict", "Done"])

            self.task_table.setRowCount(len(tasks))

            for row, task in enumerate(tasks):
                self.task_table.setItem(row, 0, QTableWidgetItem(task[1]))  # Title
                self.task_table.setItem(row, 1, QTableWidgetItem(task[2]))  # Description
                self.task_table.setItem(row, 2, QTableWidgetItem(str(task[3])))  # Deadline
                self.task_table.setItem(row, 3, QTableWidgetItem(str(task[4])))  # Difficulty

                # Add actions column (button for delete)
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(self.create_delete_callback(row))  # Use the helper method
                self.task_table.setCellWidget(row, 4, delete_button)  # Position delete button in the "Actions" column

                # Add predict button in the last column
                predict_button = QPushButton("Predict")
                predict_button.clicked.connect(
                    partial(self.on_predict_button_clicked, row=row))  # Pass row to the handler
                self.task_table.setCellWidget(row, 5, predict_button)  # Position predict button in the "Predict" column

                # Add a checkbox in the "Completed" column
                completed_checkbox = QCheckBox()
                completed_checkbox.stateChanged.connect(partial(self.on_task_completed_checked, row))  # Track changes
                self.task_table.setCellWidget(row, 6, completed_checkbox)

        task_list_layout.addWidget(self.task_table)
        task_list_widget.setLayout(task_list_layout)
        self.stacked_widget.addWidget(task_list_widget)
        self.stacked_widget.setCurrentWidget(task_list_widget)


    def on_task_completed_checked(self, row, state):
        """Handle the event when a task is marked as completed or uncompleted"""
        if state == Qt.Checked:
            # Change the color of the row to green
            for column in range(self.task_table.columnCount()):
                item = self.task_table.item(row, column)
                if item:
                    item.setBackground(QColor("lightgreen"))
        else:
            # Revert the color to default
            for column in range(self.task_table.columnCount()):
                item = self.task_table.item(row, column)
                if item:
                    item.setBackground(QColor("white"))

    def create_edit_callback(self, row):
        """Return a callback function that opens the edit form for the task."""

        def callback():
            self.edit_task(row)

        return callback

    def edit_task(self, row):
        """Edit a task when the 'Edit' button is clicked"""
        self.clear_main_content()
        task_edit_widget = QWidget()
        task_edit_layout = QVBoxLayout()

        # Get the task data to populate the form
        task_id = self.controller.get_tasks(self.controller.db.get_user(self.username)[0])[row][0]
        task = self.controller.get_task_by_id(task_id)

        self.title_entry = QLineEdit(str(task[1] if task[1] is not None else ""))
        self.description_entry = QLineEdit(
            str(task[2] if task[2] is not None else ""))
        self.deadline_entry = QLineEdit(str(task[3] if task[3] is not None else ""))
        self.difficulty_entry = QLineEdit(
            str(task[4] if task[4] is not None else ""))

        save_button = QPushButton("Save Changes")
        save_button.setStyleSheet("border-radius: 10px; background-color: #0078D7; color: white; padding: 10px;")
        save_button.clicked.connect(lambda: self.save_edited_task(task_id))

        task_edit_layout.addWidget(self.title_entry)
        task_edit_layout.addWidget(self.description_entry)
        task_edit_layout.addWidget(self.deadline_entry)
        task_edit_layout.addWidget(self.difficulty_entry)
        task_edit_layout.addWidget(save_button)

        task_edit_widget.setLayout(task_edit_layout)
        self.stacked_widget.addWidget(task_edit_widget)
        self.stacked_widget.setCurrentWidget(task_edit_widget)

    def save_edited_task(self, task_id):
        """Save the edited task to the database"""
        title = self.title_entry.text()
        description = self.description_entry.text()
        deadline = self.deadline_entry.text()
        difficulty = self.difficulty_entry.text()

        self.controller.update_task(task_id, title, description, deadline, difficulty)
        QMessageBox.information(self, "Success", "Task updated successfully!")
        self.show_task_list_view()

    def save_edited_task(self, task_id):
        """Save the edited task to the database"""
        title = self.title_entry.text()
        description = self.description_entry.text()
        deadline = self.deadline_entry.text()
        difficulty = self.difficulty_entry.text()

        self.controller.update_task(task_id, title, description, deadline, difficulty)
        QMessageBox.information(self, "Success", "Task updated successfully!")
        self.show_task_list_view()

    def create_delete_callback(self, row):
        """Return a callback function that deletes the task when the delete button is clicked."""
        def callback():
            self.delete_task(row)
        return callback

    def delete_task(self, row):
        """Delete the task from the database with confirmation"""
        reply = QMessageBox.question(self, "Delete Task",
                                     "Are you sure you want to delete this task?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            task_id = self.controller.get_tasks(self.controller.db.get_user(self.username)[0])[row][0]
            self.controller.delete_task(task_id)
            QMessageBox.information(self, "Success", "Task deleted successfully!")
            self.show_task_list_view()
        else:
            print("Task deletion cancelled.")

    def show_calendar_view(self):
        """Display the calendar view with tasks for a selected day"""
        self.clear_main_content()

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.clicked.connect(self.on_day_selected)

        main_layout = QHBoxLayout()

        calendar_container = QWidget()
        calendar_layout = QVBoxLayout()
        calendar_layout.addWidget(self.calendar_widget)
        calendar_container.setLayout(calendar_layout)

        tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout()
        tasks_container.setLayout(self.tasks_layout)

        main_layout.addWidget(calendar_container)
        main_layout.addWidget(tasks_container)

        container_widget = QWidget()
        container_widget.setLayout(main_layout)

        self.stacked_widget.addWidget(container_widget)
        self.stacked_widget.setCurrentWidget(container_widget)

        self.calendar_widget.show()

    def on_day_selected(self, date):
        """Handle the event when a day is selected from the calendar."""
        selected_date = date.toString("yyyy-MM-dd")
        print(f"Selected date: {selected_date}")
        self.show_tasks_for_date(selected_date)

    def show_tasks_for_date(self, selected_date):
        """Display tasks for the selected date and current user."""
        # Clear previous task list
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not hasattr(self, "current_user_id") or not self.current_user_id:
            self.tasks_layout.addWidget(QLabel("User not logged in."))
            return

        tasks = self.controller.get_tasks_by_date(selected_date, self.current_user_id)

        if not tasks:
            self.tasks_layout.addWidget(QLabel(f"No tasks on {selected_date}"))
            return

        # Create a table to display tasks
        task_table = QTableWidget()
        task_table.setColumnCount(3)
        task_table.setHorizontalHeaderLabels(["Title", "Description", "Difficulty"])
        task_table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            task_table.setItem(row, 0, QTableWidgetItem(task[2]))  # Title
            task_table.setItem(row, 1, QTableWidgetItem(task[3]))  # Description
            task_table.setItem(row, 2, QTableWidgetItem(str(task[5])))  # Difficulty

        self.tasks_layout.addWidget(task_table)

    def predict_task_duration_gui(self):
        """Handles task duration prediction from the GUI."""
        try:
            task_type = self.task_type_input.text()
            difficulty = int(self.difficulty_input.text())

            duration = self.controller.estimate_task_duration(task_type, difficulty)

            QMessageBox.information(self, "Estimated Duration", f"Estimated time duration for this task: {duration:.2f} hours")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Prediction error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def on_estimate_duration_button_clicked(self):
        task_type = self.task_type_input.text()
        difficulty = int(self.difficulty_input.text())
        try:
            duration = self.controller.estimate_task_duration(task_type, difficulty)
            duration = int(duration)
            QMessageBox.information(self, "Estimated Duration", f"Estimated time duration for this task: {duration:.2f} hours")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Prediction error: {e}")

    def on_predict_button_clicked(self, row):
        """Handle the click of the Predict button for the task at the given row"""
        # Extract task data from the row
        task_type = self.task_table.item(row, 0).text()
        difficulty = int(self.task_table.item(row, 3).text())

        try:
            duration = self.controller.estimate_task_duration(task_type, difficulty)
            duration = int(duration)
            QMessageBox.information(self, "Estimated Duration", f"Estimated time duration for this task: {duration:.2f} hours")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Prediction error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

