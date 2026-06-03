import os
import json
import sqlite3
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DB_PATH = os.environ.get("DB_PATH", "/opt/airflow/db/jobhunter.db")

client = Groq(api_key=GROQ_API_KEY)


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


def extract_skills(text: str):
    profile = get_profile()

    profile_context = ""
    if profile["titles"] or profile["skills"]:
        profile_context = (
            f"\nUser profile:\n"
            f"Desired job titles: {', '.join(profile['titles']) or 'not specified'}\n"
            f"User skills: {', '.join(profile['skills']) or 'not specified'}\n"
        )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract skills from the job description below. 5 skills max.\n"
                        "Output must be valid JSON and nothing else. Do not include ``` or comments or any text before or after.\n"
                        '{"soft_skills": [], "hard_skills": [], "compatibility": 0}\n\n'
                        "compatibility is a score from 1 to 5 based on how well the job matches the user profile. "
                        "If no profile is provided, set compatibility to 0.\n"
                        f"{profile_context}"
                        f"Job description:\n{text}"
                    )
                }
            ],
            temperature=0
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)
        return result

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "soft_skills": [],
            "hard_skills": [],
            "compatibility": 0
        }