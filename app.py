import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort

# letakkan DB di folder yang sama dengan app.py (menghindari masalah cwd)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "todo.db")

app = Flask(__name__)

def init_db():
    """Buat file todo.db & tabel jika belum ada."""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Database todo.db berhasil dibuat di:", DB_PATH)
    else:
        print("ℹ️ Database sudah ada di:", DB_PATH)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, task FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    tasks = [dict(r) for r in rows]
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task", "").strip()
    if task:
        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    conn = get_db_connection()
    row = conn.execute("SELECT id, task FROM tasks WHERE id=?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        abort(404)
    if request.method == "POST":
        new_task = request.form.get("task", "").strip()
        if new_task:
            conn.execute("UPDATE tasks SET task=? WHERE id=?", (new_task, task_id))
            conn.commit()
        conn.close()
        return redirect(url_for("index"))
    task = dict(row)
    conn.close()
    return render_template("edit.html", task=task)

@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    # untuk development saja; kalau mau diakses jaringan, ganti host ke "0.0.0.0"
    app.run(debug=True)

