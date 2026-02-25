from django.contrib import admin
from .models import QuestionCategory, Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'epa']
    list_filter = ['epa__specialty']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'question_type', 'difficulty', 'epa', 'is_active', 'times_answered']
    list_filter = ['question_type', 'difficulty', 'is_active', 'epa__specialty']
    search_fields = ['text']
    inlines = [ChoiceInline]
    filter_horizontal = ['learning_objectives']

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Kysymys'
