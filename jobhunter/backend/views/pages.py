from django.shortcuts import render

def home(request):
    return render(request, "index.html")


def seeker_page(request):
    return render(request, "api/seeker.html")