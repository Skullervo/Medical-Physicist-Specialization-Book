from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.progress_home, name='home'),
    path('achievements/', views.achievements, name='achievements'),
    path('paths/', views.learning_paths, name='learning_paths'),
    path('paths/<slug:specialty_slug>/', views.learning_path_detail, name='learning_path_detail'),
]
