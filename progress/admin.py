from django.contrib import admin
from .models import (
    UserQuizAttempt, SpacedRepetitionCard, EPAProgress,
    DailyStats, Achievement, UserAchievement,
)


@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'score', 'attempted_at']
    list_filter = ['is_correct']
    readonly_fields = ['attempted_at']


@admin.register(SpacedRepetitionCard)
class SpacedRepetitionCardAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'ease_factor', 'interval_days', 'repetitions', 'next_review']
    list_filter = ['repetitions']


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
