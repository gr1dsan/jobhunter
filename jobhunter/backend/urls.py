from django.urls import path
from .views.get_data import search_jobs
from .views.pages import home

urlpatterns = [
    path("", home, name="home"),
    path("api/search_jobs/", search_jobs, name="search_jobs"),
]