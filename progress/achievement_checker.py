"""Achievement trigger logic — checks conditions and awards new achievements."""
from datetime import timedelta

from django.utils import timezone

from progress.models import (
    Achievement, UserAchievement, UserQuizAttempt, DailyStats, EPAProgress,
)


def check_achievements(user) -> list[Achievement]:
    """
    Check all achievements for a user and award any newly earned ones.
    Returns list of newly earned Achievement objects.
    """
    earned_codes = set(
        UserAchievement.objects.filter(user=user).values_list(
            'achievement__code', flat=True
        )
    )

    newly_earned = []
    for achievement in Achievement.objects.all():
        if achievement.code in earned_codes:
            continue
        if _check_condition(user, achievement):
            UserAchievement.objects.create(user=user, achievement=achievement)
            newly_earned.append(achievement)

    return newly_earned


def _check_condition(user, achievement) -> bool:
    ctype = achievement.condition_type
    cval = achievement.condition_value

    if ctype == 'questions':
        return UserQuizAttempt.objects.filter(user=user).count() >= cval

    elif ctype == 'streak':
        return _calculate_streak(user) >= cval

    elif ctype == 'correct_streak':
        return _get_current_correct_streak(user) >= cval

    elif ctype == 'exam_pass':
        from sisalto.models import ExamAnswer
        return (
            ExamAnswer.objects.filter(user=user, ai_score__isnull=False)
            .values('session_id').distinct().count()
        ) >= cval

    elif ctype == 'mastery':
        return EPAProgress.objects.filter(
            user=user, overall_mastery__gte=cval
        ).exists()

    return False


def _calculate_streak(user) -> int:
    today = timezone.now().date()
    streak = 0
    check_date = today
    while True:
        if DailyStats.objects.filter(
            user=user, date=check_date, questions_answered__gt=0
        ).exists():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak


def _get_current_correct_streak(user) -> int:
    recent = UserQuizAttempt.objects.filter(
        user=user
    ).order_by('-attempted_at').values_list('is_correct', flat=True)[:50]
    streak = 0
    for is_correct in recent:
        if is_correct:
            streak += 1
        else:
            break
    return streak
