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
    path('api/review/rate/', views.api_rate_review, name='api_review_rate'),
    # Flag & Note API
    path('api/flag/toggle/', views.api_toggle_flag, name='api_flag_toggle'),
    path('api/flag/', views.api_get_flag, name='api_get_flag'),
    path('api/flag/list/', views.api_flagged_questions, name='api_flagged_list'),
    path('api/note/save/', views.api_save_note, name='api_save_note'),
    path('api/note/', views.api_get_note, name='api_get_note'),
    # Flashcard review
    path('flashcards/', views.flashcard_review, name='flashcard_review'),
    path('api/flashcard/', views.api_get_flashcard, name='api_get_flashcard'),
    path('api/flashcard/reveal/', views.api_reveal_flashcard, name='api_reveal_flashcard'),
    path('flashcards/export/anki/', views.export_flashcards_anki, name='flashcard_anki_export'),
    # Comments
    path('api/comments/<int:question_id>/', views.api_get_comments, name='api_get_comments'),
    path('api/comments/add/', views.api_add_comment, name='api_add_comment'),
    path('api/comments/resolve/', views.api_resolve_comment, name='api_resolve_comment'),
]
