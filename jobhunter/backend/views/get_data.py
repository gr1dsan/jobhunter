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

    try:
        #build url
        url = build_search_url(
            keyword=body.get("keyword"),
            cities=body.get("cities"),
            categories=body.get("categories"),
            min_salary=body.get("min_salary"),
            working_hours=body.get("working_hours"),
        )

        #scrape
        raw = await scrape_data(url)

        jobs = raw.get("jobs", [])

        if not jobs:
            return JsonResponse({"jobs": []}, status=200)

        #clean
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
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    jobs = body.get("jobs", [])

    for job_data in jobs:
        job = await Job.objects.acreate(
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            details=job_data.get("details", ""),
            url=job_data.get("url", ""),
            min_salary=job_data.get("min_salary"),
            max_salary=job_data.get("max_salary"),
            is_net=job_data.get("is_net", False),
            is_gross=job_data.get("is_gross", False),
            is_full_time=job_data.get("is_full_time", False),
            is_part_time=job_data.get("is_part_time", False),
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

    return JsonResponse({"saved": len(jobs)}, status=201)