import sqlite3

db_path = "tasks.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

task_types = [
    "Tema POO",
    "Tema SO",
    "Tema AA",
    "Tema PCLP",
    "Tema SDA",
    "Test POO",
    "Test SO",
    "Test AA",
    "Test PCLP",
    "Test SDA"
]

for task_type in task_types:
    try:
        cursor.execute("INSERT INTO task_types (name) VALUES (?);", (task_type,))
    except sqlite3.IntegrityError:
        print(f"Tipul de task '{task_type}' există deja în tabel.")

connection.commit()
connection.close()

print("Tabelul task_types a fost populat!")
