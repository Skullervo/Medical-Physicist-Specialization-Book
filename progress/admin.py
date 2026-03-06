from django.contrib import admin
from .models import (
    UserQuizAttempt, SpacedRepetitionCard, EPAProgress,
    DailyStats, Achievement, UserAchievement,
    FlaggedQuestion, QuestionNote, QuestionComment,
)


@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'score', 'attempted_at']
    list_filter = ['is_correct']
    readonly_fields = ['attempted_at']


@admin.register(SpacedRepetitionCard)
class SpacedRepetitionCardAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'question', 'stability', 'difficulty', 'fsrs_state',
        'interval_days', 'repetitions', 'lapses', 'next_review',
    ]
    list_filter = ['fsrs_state', 'repetitions']


@admin.register(EPAProgress)
class EPAProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'epa', 'overall_mastery', 'a_level_mastery', 'b_level_mastery', 'current_streak_days']
    list_filter = ['epa__specialty']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'questions_answered', 'questions_correct', 'xp_earned']
    list_filter = ['date']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'condition_type', 'condition_value', 'xp_reward']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']


@admin.register(FlaggedQuestion)
class FlaggedQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'flag_type', 'created_at']
    list_filter = ['flag_type']


@admin.register(QuestionNote)
class QuestionNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'updated_at']


@admin.register(QuestionComment)
class QuestionCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'text_preview', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    list_editable = ['is_resolved']
    search_fields = ['user__username', 'text']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Kommentti'
