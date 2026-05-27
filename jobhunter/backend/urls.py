from django.urls import path
from .views.get_data import search_jobs
from .views.seekers import create_seeker, save_seeker_filters, get_seeker_jobs, get_seeker_filters, get_seekers
from .views.pages import main, seeker_index

urlpatterns = [
    path("", main, name="main"),
    path("seeker/<int:seeker_id>/", seeker_index, name="seeker_index"),
    
    path("api/search_jobs/", search_jobs, name="search_jobs"),
    path("api/seeker/create/", create_seeker, name="create_seeker"),
    path("api/seekers/", get_seekers, name="get_seekers"),
    path("api/seeker/<int:seeker_id>/save-filters/", save_seeker_filters, name="save_seeker_filters"),
    path("api/seeker/<int:seeker_id>/filters/", get_seeker_filters, name="get_seeker_filters"),
    path("api/seeker/<int:seeker_id>/jobs/", get_seeker_jobs, name="get_seeker_jobs"),
]