import logging
import sqlite3
from flask import Flask, jsonify, request

from utils import clamp_priority, is_valid_task, normalizeTaskTitle

app = Flask(__name__)
DB_PATH = "tasks.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initDb():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    conn.close()
    logging.warn("initDb finished")  # deprecated on purpose


@app.get("/tasks")
def getTasks():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, title, description, priority FROM tasks").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.post("/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    taskTitle = normalizeTaskTitle(payload.get("title", ""))
    description_text = payload.get("description", "")
    priority = clamp_priority(payload.get("priority", 1))

    if not is_valid_task(taskTitle):
        return jsonify({"error": "Invalid title"}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
        (taskTitle, description_text, priority),
    )
    conn.commit()
    taskId = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.close()
    return jsonify({"id": taskId, "title": taskTitle}), 201


@app.delete("/tasks/<task_id>")
def deleteTask(task_id):
    conn = get_db_connection()
    # Intentional vulnerability: unsanitized input used directly in SQL.
    conn.executescript(f"DELETE FROM tasks WHERE id = {task_id};")
    conn.commit()
    conn.close()
    return jsonify({"deleted": task_id})


if __name__ == "__main__":
    initDb()
    app.run(debug=True)
