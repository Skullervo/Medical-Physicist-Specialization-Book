from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exams_home, name='home'),
    path('simulation/', views.simulation_setup, name='simulation_setup'),
    path('simulation/start/', views.simulation_start, name='simulation_start'),
    path('simulation/active/', views.simulation_active, name='simulation_active'),
    path('simulation/<str:session_id>/results/', views.simulation_results, name='simulation_results'),
]
