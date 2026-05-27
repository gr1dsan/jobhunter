import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import Seeker, Job


def get_seekers(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    seekers = Seeker.objects.all().order_by('-created_at').values('id', 'title', 'created_at')

    return JsonResponse({'seekers': list(seekers)})


@csrf_exempt
def create_seeker(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    body = json.loads(request.body)
    title = body.get('title', '').strip()

    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)

    seeker = Seeker.objects.create(title=title)
    return JsonResponse({'seeker_id': seeker.id}, status=201)


@csrf_exempt
def save_seeker_filters(request, seeker_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    seeker = Seeker.objects.get(id=seeker_id)

    body = json.loads(request.body)

    seeker.keyword = body.get('keyword', '')
    seeker.set_cities(body.get('cities', []))
    seeker.set_categories(body.get('categories', []))
    seeker.set_working_hours(body.get('working_hours', []))
    seeker.min_salary = body.get('min_salary')
    seeker.save()

    return JsonResponse({'success': True})


@csrf_exempt
def get_seeker_filters(request, seeker_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    seeker = Seeker.objects.get(id=seeker_id)

    return JsonResponse({
        'keyword': seeker.keyword,
        'cities': seeker.get_cities(),
        'categories': seeker.get_categories(),
        'working_hours': seeker.get_working_hours(),
        'min_salary': float(seeker.min_salary) if seeker.min_salary else None
    })


def get_seeker_jobs(request, seeker_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    seeker = Seeker.objects.get(id=seeker_id)

    jobs = Job.objects.filter(seeker=seeker).values('id', 'title', 'company', 'url', 'min_salary', 'max_salary')

    return JsonResponse({'jobs': list(jobs)})