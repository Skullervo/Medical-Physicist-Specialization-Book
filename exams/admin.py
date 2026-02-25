from django.contrib import admin
from .models import ExamTemplate, ExamTemplateQuestion, ExamSession, ExamSessionAnswer


class ExamTemplateQuestionInline(admin.TabularInline):
    model = ExamTemplateQuestion
    extra = 1


@admin.register(ExamTemplate)
class ExamTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'year', 'semester', 'is_active']
    list_filter = ['exam_type', 'year', 'is_active']
    inlines = [ExamTemplateQuestionInline]
    filter_horizontal = ['specialties', 'epa_cards']


@admin.register(ExamTemplateQuestion)
class ExamTemplateQuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'question_number', 'max_points', 'epa']
    list_filter = ['exam']
    filter_horizontal = ['learning_objectives']


class ExamSessionAnswerInline(admin.TabularInline):
    model = ExamSessionAnswer
    extra = 0
    readonly_fields = ['ai_score', 'ai_feedback', 'ai_evaluated_at']


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'status', 'total_score', 'passed', 'started_at']
    list_filter = ['status', 'passed']
    inlines = [ExamSessionAnswerInline]
