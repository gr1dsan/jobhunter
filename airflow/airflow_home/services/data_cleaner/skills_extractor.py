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
        rows = conn.execute(
            "SELECT type, value FROM profile"
        ).fetchall()

        return {
            "titles": [
                r["value"] for r in rows
                if r["type"] == "title"
            ],
            "skills": [
                r["value"] for r in rows
                if r["type"] == "skill"
            ]
        }

    except Exception:
        return {
            "titles": [],
            "skills": []
        }

    finally:
        conn.close()


def calculate_compatibility(job_skills, user_skills):

    if not job_skills:
        return 1

    user_skills_lower = {
        skill.strip().lower()
        for skill in user_skills
    }

    matches = 0

    for skill in job_skills:
        if skill.strip().lower() in user_skills_lower:
            matches += 1

    ratio = matches / len(job_skills)

    if ratio < 0.20:
        return 1
    elif ratio < 0.40:
        return 2
    elif ratio < 0.60:
        return 3
    elif ratio < 0.80:
        return 4
    else:
        return 5


def extract_skills(text: str):
    profile = get_profile()

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Extract the MOST IMPORTANT skills from the job description.

Rules:
- Return valid JSON only.
- No markdown.
- No explanations.
- Maximum 5 hard skills.
- Maximum 5 soft skills.
- Include only skills explicitly mentioned or clearly required.

Output format:

{{
    "soft_skills": [],
    "hard_skills": []
}}

Job description:

{text}
"""
                }
            ]
        )

        raw = response.choices[0].message.content.strip()

        result = json.loads(raw)

        hard_skills = result.get("hard_skills", [])
        soft_skills = result.get("soft_skills", [])

        compatibility = calculate_compatibility(
            hard_skills,
            profile["skills"]
        )

        return {
            "soft_skills": soft_skills,
            "hard_skills": hard_skills,
            "compatibility": compatibility
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "soft_skills": [],
            "hard_skills": [],
            "compatibility": 0
        }