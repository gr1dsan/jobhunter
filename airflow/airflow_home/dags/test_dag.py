import sys
import os
import asyncio
import json
import sqlite3
import pandas as pd

sys.path.insert(0, "/opt/airflow")

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from services.queries.queries import save_jobs, create_tables
from services.url_builder.url_builder import build_url
from services.scraper.scraper import scrape_data
from services.data_cleaner.cleaner import clean_jobs


DB_PATH = os.environ.get("DB_PATH", "/opt/airflow/db/jobhunter.db")


def get_saved_filters():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM parameters ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not row:
        return {
            "keyword": None,
            "cities": [],
            "categories": [],
            "working_hours": [],
            "min_salary": None
        }
    return {
        "keyword": row["keyword"],
        "cities": json.loads(row["cities"] or "[]"),
        "categories": json.loads(row["categories"] or "[]"),
        "working_hours": json.loads(row["working_hours"] or "[]"),
        "min_salary": row["min_salary"]
    }


def task_build_url(ti):
    filters = get_saved_filters()
    url = build_url(
        keyword=filters["keyword"],
        cities=filters["cities"],
        categories=filters["categories"],
        working_hours=filters["working_hours"],
        min_salary=filters["min_salary"]
    )
    print("built url:", url)
    ti.xcom_push(key="url", value=url)
    return url


def task_scrape_data(ti):
    url = ti.xcom_pull(task_ids="build_url", key="url")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    raw = loop.run_until_complete(scrape_data(url))
    jobs = raw["jobs"]
    ti.xcom_push(key="raw_jobs", value=jobs)

    return jobs


def task_clean_jobs(ti):
    raw = ti.xcom_pull(task_ids="scrape_data", key="raw_jobs")
    df = pd.DataFrame(raw)
    cleaned = clean_jobs(df)
    return cleaned.to_dict(orient="records")


def task_save_jobs(ti):
    jobs = ti.xcom_pull(task_ids="clean_jobs")
    create_tables()
    save_jobs(jobs)


with DAG(
    dag_id="seekers",
    start_date=datetime(2024, 1, 1),
    schedule="*/10 * * * *",
    catchup=False,
) as dag:

    build_url_task = PythonOperator(task_id="build_url", python_callable=task_build_url)
    scrape_data_task = PythonOperator(task_id="scrape_data", python_callable=task_scrape_data)
    clean_jobs_task = PythonOperator(task_id="clean_jobs", python_callable=task_clean_jobs)
    save_jobs_task = PythonOperator(task_id="save_jobs", python_callable=task_save_jobs)

    build_url_task >> scrape_data_task >> clean_jobs_task >> save_jobs_task