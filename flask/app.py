import sqlite3
import os
import json
import requests
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "../db/jobhunter.db"))
AIRFLOW_URL = os.environ.get("AIRFLOW_URL", "http://airflow:8080")
AIRFLOW_USER = os.environ.get("AIRFLOW_USER", "admin")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_PASSWORD", "admin")


def get_dag_status():
    try:
        resp = requests.get(
            f"{AIRFLOW_URL}/api/v1/dags/seekers",
            auth=(AIRFLOW_USER, AIRFLOW_PASSWORD),
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json().get("is_paused", True)
        return None
    except Exception: 
        return None


def create_parameters_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parameters (
            id INTEGER PRIMARY KEY,
            keyword TEXT,
            cities TEXT,
            categories TEXT,
            working_hours TEXT,
            min_salary INTEGER
        )
    """)
    conn.commit()
    conn.close()  


def get_saved_filters():
    create_parameters_table()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM parameters LIMIT 1").fetchone()
    conn.close()
    if not row:
        return {"keyword": "", "cities": [], "categories": [], "working_hours": [], "min_salary": ""}
    return {
        "keyword": row["keyword"] or "",
        "cities": json.loads(row["cities"] or "[]"),
        "categories": json.loads(row["categories"] or "[]"),
        "working_hours": json.loads(row["working_hours"] or "[]"),
        "min_salary": row["min_salary"] or ""
    }


def get_profile():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT type, value FROM profile").fetchall()
        return {
            "titles": [r["value"] for r in rows if r["type"] == "title"],
            "skills": [r["value"] for r in rows if r["type"] == "skill"]
        }
    except Exception:
        return {"titles": [], "skills": []}
    finally:
        conn.close()


def get_jobs():
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
        jobs = cursor.fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return []

    result = []
    for job in jobs:
        job = dict(job)

        cursor.execute("""
            SELECT s.skill FROM soft_skills s
            JOIN job_soft_skills js ON js.skill_id = s.id
            WHERE js.job_id = ?
        """, (job["id"],))
        job["soft_skills"] = [r["skill"] for r in cursor.fetchall()]

        cursor.execute("""
            SELECT s.skill FROM hard_skills s
            JOIN job_hard_skills js ON js.skill_id = s.id
            WHERE js.job_id = ?
        """, (job["id"],))
        job["hard_skills"] = [r["skill"] for r in cursor.fetchall()]

        cursor.execute("""
            SELECT c.name FROM cities c
            JOIN job_cities jc ON jc.city_id = c.id
            WHERE jc.job_id = ?
        """, (job["id"],))
        job["location"] = ", ".join([r["name"] for r in cursor.fetchall()])

        result.append(job)

    conn.close()
    return result


@app.route("/toggle_dag", methods=["POST"])
def toggle_dag():
    is_paused = get_dag_status()
    if is_paused is None:
        return redirect("/")
    try:
        requests.patch(
            f"{AIRFLOW_URL}/api/v1/dags/seekers",
            json={"is_paused": not is_paused},
            auth=(AIRFLOW_USER, AIRFLOW_PASSWORD),
            timeout=5
        )
    except Exception:
        pass
    return redirect("/")


@app.route("/save_filters", methods=["POST"])
def save_parameters():
    keyword = request.form.get("keyword", "")
    cities = request.form.getlist("cities")
    categories = request.form.getlist("categories")
    working_hours = request.form.getlist("working_hours")
    min_salary = request.form.get("min_salary")

    create_parameters_table()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM parameters")
    conn.execute(
        "INSERT INTO parameters (keyword, cities, categories, working_hours, min_salary) VALUES (?, ?, ?, ?, ?)",
        (keyword, json.dumps(cities), json.dumps(categories), json.dumps(working_hours), min_salary)
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/add_title", methods=["POST"])
def add_title():
    title = request.form.get("title", "").strip()
    if title:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, type TEXT, value TEXT UNIQUE)")
        conn.execute("INSERT OR IGNORE INTO profile (type, value) VALUES ('title', ?)", (title,))
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/remove_title", methods=["POST"])
def remove_title():
    title = request.form.get("title", "").strip()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM profile WHERE type = 'title' AND value = ?", (title,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/add_skill", methods=["POST"])
def add_skill():
    skill = request.form.get("skill", "").strip()
    if skill:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, type TEXT, value TEXT UNIQUE)")
        conn.execute("INSERT OR IGNORE INTO profile (type, value) VALUES ('skill', ?)", (skill,))
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/remove_skill", methods=["POST"])
def remove_skill():
    skill = request.form.get("skill", "").strip()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM profile WHERE type = 'skill' AND value = ?", (skill,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/")
def index():
    jobs = get_jobs()
    filters = get_saved_filters()
    profile = get_profile()
    dag_paused = get_dag_status()
    return render_template("index.html", jobs=jobs, filters=filters, profile=profile, dag_paused=dag_paused)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)