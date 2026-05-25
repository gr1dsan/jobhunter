def serialize_job(job):
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "url": job.url,
        "min_salary": str(job.min_salary),
        "max_salary": str(job.max_salary),
        "have_applied": job.have_applied,
        "is_new": job.is_new,
        "seeker_id": job.seeker_id,
        "locations": list(job.locations.values("id", "city")),
        "skills": list(job.skills.values("id", "name", "skill_type")),
    }


def serialize_seeker(seeker):
    return {
        "id": seeker.id,
        "title": seeker.title,
        "min_salary": str(seeker.min_salary),
        "keyword": seeker.keyword,
        "status": seeker.status,
        "categories": list(seeker.categories.values("id", "name")),
        "work_types": list(seeker.work_types.values("id", "name")),
        "locations": list(seeker.locations.values("id", "city")),
        "skills": list(seeker.skills.values("id", "name", "skill_type")),
    }