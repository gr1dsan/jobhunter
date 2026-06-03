import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "/opt/airflow/db/jobhunter.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soft_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hard_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            url TEXT UNIQUE,
            min_salary REAL,
            max_salary REAL,
            is_net INTEGER,
            is_gross INTEGER,
            is_full_time INTEGER,
            is_part_time INTEGER,
            details TEXT,
            compatibility INTEGER DEFAULT 0
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_cities (
            job_id INTEGER,
            city_id INTEGER,
            PRIMARY KEY (job_id, city_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (city_id) REFERENCES cities(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_soft_skills (
            job_id INTEGER,
            skill_id INTEGER,
            PRIMARY KEY (job_id, skill_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (skill_id) REFERENCES soft_skills(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_hard_skills (
            job_id INTEGER,
            skill_id INTEGER,
            PRIMARY KEY (job_id, skill_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (skill_id) REFERENCES hard_skills(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            type TEXT,
            value TEXT UNIQUE
        );
    """)

    conn.commit()
    conn.close()


def get_or_create(cursor, table, column, value):
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
    return cursor.lastrowid


def save_jobs(jobs):
    conn = get_connection()
    cursor = conn.cursor()

    for job in jobs:
        cursor.execute("""
            INSERT OR IGNORE INTO jobs 
            (title, company, url, min_salary, max_salary, is_net, is_gross, is_full_time, is_part_time, details, compatibility)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get("title"),
            job.get("company"),
            job.get("url"),
            job.get("min_salary"),
            job.get("max_salary"),
            job.get("is_net"),
            job.get("is_gross"),
            job.get("is_full_time"),
            job.get("is_part_time"),
            job.get("details"),
            job.get("compatibility", 0),
        ))

        cursor.execute("SELECT id FROM jobs WHERE url = ?", (job.get("url"),))
        row = cursor.fetchone()
        if not row:
            continue
        job_id = row[0]

        for city in job.get("cities", []):
            city_id = get_or_create(cursor, "cities", "name", city)
            cursor.execute("INSERT OR IGNORE INTO job_cities (job_id, city_id) VALUES (?, ?)", (job_id, city_id))

        for skill in job.get("soft_skills", []):
            skill_id = get_or_create(cursor, "soft_skills", "skill", skill)
            cursor.execute("INSERT OR IGNORE INTO job_soft_skills (job_id, skill_id) VALUES (?, ?)", (job_id, skill_id))

        for skill in job.get("hard_skills", []):
            skill_id = get_or_create(cursor, "hard_skills", "skill", skill)
            cursor.execute("INSERT OR IGNORE INTO job_hard_skills (job_id, skill_id) VALUES (?, ?)", (job_id, skill_id))

    conn.commit()
    conn.close()


def get_profile():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT type, value FROM profile").fetchall()
    conn.close()
    return {
        "titles": [r["value"] for r in rows if r["type"] == "title"],
        "skills": [r["value"] for r in rows if r["type"] == "skill"]
    }