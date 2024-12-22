import sqlite3
import random

db_path = "tasks.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Configurare date taskuri
task_config = {
    "Tema POO": {"difficulty": (3, 4), "duration": (20, 40)},
    "Tema SO": {"difficulty": (4, 5), "duration": (40, 70)},
    "Tema AA": {"difficulty": (2, 3), "duration": (10, 15)},
    "Tema PCLP": {"difficulty": (2, 2), "duration": (15, 30)},
    "Tema SDA": {"difficulty": (3, 5), "duration": (30, 50)},
    "Test POO": {"difficulty": (3, 4), "duration": (10, 20)},
    "Test SO": {"difficulty": (4, 5), "duration": (20, 30)},
    "Test AA": {"difficulty": (2, 3), "duration": (5, 10)},
    "Test PCLP": {"difficulty": (2, 2), "duration": (2, 5)},
    "Test SDA": {"difficulty": (3, 5), "duration": (10, 15)},
}

num_records_per_task = 20

for task_type, config in task_config.items():
    difficulty_range = config["difficulty"]
    duration_range = config["duration"]

    for _ in range(num_records_per_task):
        difficulty = random.randint(*difficulty_range)
        duration = random.uniform(*duration_range)

        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, deadline, difficulty)
            VALUES (1, ?, ?, '2024-12-31', ?);
        """, (task_type, f"{task_type} description", difficulty))

        task_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO task_completions (task_id, completion_time)
            VALUES (?, ?);
        """, (task_id, duration))

connection.commit()
connection.close()

print("Datele au fost generate cu succes!")



