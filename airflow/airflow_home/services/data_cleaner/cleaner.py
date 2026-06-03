import pandas as pd
import re
from .skills_extractor import extract_skills

def parse_salary(value):
    if pd.isna(value):
        return pd.Series([0, 0])

    text = str(value).lower().replace(",", "")

    m = re.search(r"(\d+)\s*-\s*(\d+)", text)
    if m:
        return pd.Series([int(m.group(1)), int(m.group(2))])

    m = re.search(r"from\s*(\d+)", text)
    if m:
        return pd.Series([int(m.group(1)), 0])

    m = re.search(r"up to\s*(\d+)", text)
    if m:
        return pd.Series([0, int(m.group(1))])

    return pd.Series([0, 0])

def parse_work_type(value):
    if pd.isna(value):
        return None

    text = str(value).lower()

    if "full" in text and "part" in text:
        return "both"
    if "full" in text:
        return "full"
    if "part" in text:
        return "part"

    return None

def parse_salary_type(value):
    if pd.isna(value):
        return None

    text = str(value).lower()

    if "net" in text:
        return "net"
    if "gross" in text:
        return "gross"

    return None


def clean_jobs(df):
    if df.empty:
        return df
    
    df[["min_salary", "max_salary"]] = df["salary"].apply(parse_salary)

    df["salary_type"] = df["salary_type"].apply(parse_salary_type)
    df["is_net"] = (df["salary_type"] == "net").astype(int)
    df["is_gross"] = (df["salary_type"] == "gross").astype(int)

    df["work_type"] = df["work_type"].apply(parse_work_type)
    df["is_full_time"] = df["work_type"].isin(["full", "both"]).astype(int)
    df["is_part_time"] = df["work_type"].isin(["part", "both"]).astype(int)

    skills = df["details"].apply(extract_skills)

    df["soft_skills"] = skills.apply(lambda x: x.get("soft_skills", []))
    df["hard_skills"] = skills.apply(lambda x: x.get("hard_skills", []))

    df["compatibility"] = skills.apply(lambda x: x.get("compatibility", 0))

    df = df.drop(columns=["salary", "salary_type", "work_type"], errors="ignore")

    return df