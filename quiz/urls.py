from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_home, name='home'),
    path('practice/', views.quiz_practice, name='practice'),
    path('api/question/', views.api_get_question, name='api_question'),
    path('api/answer/', views.api_check_answer, name='api_answer'),
    path('spaced-review/', views.spaced_review, name='spaced_review'),
    path('api/review/question/', views.api_get_review_question, name='api_review_question'),
    path('api/review/answer/', views.api_submit_review, name='api_review_answer'),
]
