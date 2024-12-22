-- Table for users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Table for tasks
CREATE TABLE IF NOT EXISTS tasks_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT,
    difficulty INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Copy the old data into the new one
INSERT INTO tasks_new (id, user_id, title, description, deadline, difficulty)
SELECT id, user_id, title, description, deadline, difficulty FROM tasks;

-- Delete the old table
DROP TABLE tasks;

-- remove temporary tables
ALTER TABLE tasks_new RENAME TO tasks;

-- Table for task types
CREATE TABLE IF NOT EXISTS task_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Table for task completions ( ML training)
CREATE TABLE IF NOT EXISTS task_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    completion_time REAL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);