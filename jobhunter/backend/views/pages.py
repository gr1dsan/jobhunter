from django.shortcuts import render
from ..models import Seeker


def main(request):
    seekers = Seeker.objects.all().order_by('-created_at')
    return render(request, 'main.html', {'seekers': seekers})


def seeker_index(request, seeker_id):
    return render(request, 'seeker_index.html')