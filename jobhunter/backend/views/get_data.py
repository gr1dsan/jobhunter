import json
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services.url_builder.url_builder import build_url as build_search_url
from ..services.scraper.scraper import scrape_data
from ..services.data_cleaner.cleaner import clean_jobs
from ..models import *


@csrf_exempt
async def search_jobs(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if "jobs" in body:
        return await save_jobs(request)

    try:
        url = build_search_url(
            keyword=body.get("keyword"),
            cities=body.get("cities"),
            categories=body.get("categories"),
            min_salary=body.get("min_salary"),
            working_hours=body.get("working_hours"),
        )

        raw = await scrape_data(url)

        jobs = raw.get("jobs", [])

        if not jobs:
            return JsonResponse({"jobs": []}, status=200)

        df = pd.DataFrame(jobs)
        df = clean_jobs(df)

        return JsonResponse(
            {"jobs": df.to_dict(orient="records")},
            safe=False
        )

    except Exception as e:
        return JsonResponse(
            {"error": "Pipeline failed", "details": str(e)},
            status=500
        )


@csrf_exempt
async def save_jobs(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    jobs = body.get("jobs", [])
    seeker_id = body.get("seeker_id")

    saved_count = 0

    for job_data in jobs:
        title = job_data.get("title", "").strip()
        company = job_data.get("company", "").strip()
        location = job_data.get("location", [])

        if not title or not company:
            continue

        location_str = ", ".join(location) if isinstance(location, list) else str(location)

        query = Job.objects.filter(
            title=title,
            company=company,
        )

        if seeker_id:
            query = query.filter(seeker_id=seeker_id)

        existing = await query.afirst()
        if existing:
            existing_locs = await existing.locations.avalues_list('name', flat=True)
            if location_str in existing_locs or all(loc in existing_locs for loc in location):
                continue

        job = await Job.objects.acreate(
            title=title,
            company=company,
            details=job_data.get("details", ""),
            url=job_data.get("url", ""),
            min_salary=job_data.get("min_salary"),
            max_salary=job_data.get("max_salary"),
            is_net=job_data.get("is_net", False),
            is_gross=job_data.get("is_gross", False),
            is_full_time=job_data.get("is_full_time", False),
            is_part_time=job_data.get("is_part_time", False),
            seeker_id=seeker_id,
        )

        for loc_name in job_data.get("location", []):
            if loc_name:
                loc, _ = await Location.objects.aget_or_create(name=loc_name)
                await job.locations.aadd(loc)

        for skill_name in job_data.get("soft_skills", []):
            if skill_name:
                skill, _ = await SoftSkill.objects.aget_or_create(name=skill_name)
                await job.soft_skills.aadd(skill)

        for skill_name in job_data.get("hard_skills", []):
            if skill_name:
                skill, _ = await HardSkill.objects.aget_or_create(name=skill_name)
                await job.hard_skills.aadd(skill)

        saved_count += 1

    return JsonResponse({"saved": saved_count}, status=201)
