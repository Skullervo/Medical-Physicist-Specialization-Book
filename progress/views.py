import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from progress.models import (
    UserQuizAttempt, SpacedRepetitionCard, EPAProgress, DailyStats,
    Achievement, UserAchievement
)
from quiz.models import Question
from sisalto.models import Specialty, EPA


def _calculate_streak(user, today):
    """Calculate consecutive days with at least one answer."""
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


@login_required
def progress_home(request):
    """Progress dashboard with real data."""
    user = request.user
    today = timezone.now().date()

    # Overall stats
    total_attempts = UserQuizAttempt.objects.filter(user=user)
    total_answered = total_attempts.count()
    total_correct = total_attempts.filter(is_correct=True).count()
    accuracy = round(total_correct / total_answered * 100) if total_answered > 0 else 0

    # Streak
    streak = _calculate_streak(user, today)

    # Total XP
    total_xp = DailyStats.objects.filter(user=user).aggregate(
        total=Sum('xp_earned')
    )['total'] or 0

    # Weekly stats (last 7 days)
    day_names = ['Ma', 'Ti', 'Ke', 'To', 'Pe', 'La', 'Su']
    weekly_stats = []
    max_daily = 1  # avoid division by zero in chart
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        stats = DailyStats.objects.filter(user=user, date=date).first()
        answered = stats.questions_answered if stats else 0
        correct = stats.questions_correct if stats else 0
        if answered > max_daily:
            max_daily = answered
        weekly_stats.append({
            'date': date.strftime('%d.%m.'),
            'day_name': day_names[date.weekday()],
            'answered': answered,
            'correct': correct,
        })

    # EPA progress by specialty
    specialties = Specialty.objects.prefetch_related('epas').order_by('order')
    specialty_progress = []
    for spec in specialties:
        epas = []
        for epa in spec.epas.all():
            progress = EPAProgress.objects.filter(user=user, epa=epa).first()
            q_count = Question.objects.filter(epa=epa, is_active=True).count()
            answered = progress.a_level_questions_answered if progress else 0
            correct = progress.a_level_questions_correct if progress else 0
            answer_pct = round(correct / answered * 100) if answered > 0 else 0
            epas.append({
                'title': epa.title,
                'mastery': round(progress.overall_mastery) if progress else 0,
                'answered': answered,
                'correct': correct,
                'answer_pct': answer_pct,
                'total_questions': q_count,
            })
        specialty_progress.append({
            'name': spec.name,
            'slug': spec.slug if hasattr(spec, 'slug') else spec.name.lower(),
            'epas': epas,
        })

    # Due SR cards count
    due_cards = SpacedRepetitionCard.objects.filter(
        user=user, next_review__lte=timezone.now()
    ).count()

    # Recent achievements (last 5)
    recent_achievements = UserAchievement.objects.filter(
        user=user
    ).select_related('achievement').order_by('-earned_at')[:5]

    # Weak EPAs — lowest accuracy with at least 5 answers, top 5
    weak_epas = []
    if total_answered >= 20:
        epa_stats = (
            UserQuizAttempt.objects.filter(user=user)
            .values('question__epa__id', 'question__epa__title')
            .annotate(
                total=Count('id'),
                correct=Count('id', filter=Q(is_correct=True)),
            )
            .filter(total__gte=5)
            .order_by()
        )
        for es in epa_stats:
            pct = round(es['correct'] / es['total'] * 100)
            weak_epas.append({
                'epa_id': es['question__epa__id'],
                'title': es['question__epa__title'],
                'accuracy': pct,
                'total': es['total'],
                'correct': es['correct'],
            })
        weak_epas.sort(key=lambda x: x['accuracy'])
        weak_epas = weak_epas[:5]

    # Exam readiness — per specialty accuracy × coverage
    specialty_readiness = []
    total_readiness_score = 0
    total_readiness_weight = 0
    if total_answered >= 20:
        for spec in specialties:
            spec_total = 0
            spec_correct = 0
            spec_q_count = 0
            spec_answered_questions = set()
            for epa in spec.epas.all():
                q_count = Question.objects.filter(epa=epa, is_active=True).count()
                spec_q_count += q_count
                attempts = UserQuizAttempt.objects.filter(user=user, question__epa=epa)
                spec_total += attempts.count()
                spec_correct += attempts.filter(is_correct=True).count()
                spec_answered_questions.update(
                    attempts.values_list('question_id', flat=True).distinct()
                )

            accuracy_pct = round(spec_correct / spec_total * 100) if spec_total > 0 else 0
            coverage_pct = round(len(spec_answered_questions) / spec_q_count * 100) if spec_q_count > 0 else 0
            readiness = round(accuracy_pct * coverage_pct / 100) if coverage_pct > 0 else 0

            specialty_readiness.append({
                'name': spec.name,
                'accuracy': accuracy_pct,
                'coverage': coverage_pct,
                'readiness': readiness,
                'total_answered': spec_total,
                'total_questions': spec_q_count,
            })
            total_readiness_score += readiness * spec_q_count
            total_readiness_weight += spec_q_count

    exam_readiness = round(total_readiness_score / total_readiness_weight) if total_readiness_weight > 0 else 0

    context = {
        'total_answered': total_answered,
        'total_correct': total_correct,
        'accuracy': accuracy,
        'streak': streak,
        'total_xp': total_xp,
        'weekly_stats': weekly_stats,
        'weekly_stats_json': json.dumps(weekly_stats),
        'max_daily': max_daily,
        'specialty_progress': specialty_progress,
        'due_cards': due_cards,
        'recent_achievements': recent_achievements,
        'weak_epas': weak_epas,
        'specialty_readiness': specialty_readiness,
        'exam_readiness': exam_readiness,
    }
    return render(request, 'progress/progress_home.html', context)


@login_required
def achievements(request):
    """Achievements page."""
    user = request.user
    earned = UserAchievement.objects.filter(user=user).select_related('achievement')
    all_achievements = Achievement.objects.all()

    earned_ids = set(ua.achievement_id for ua in earned)

    context = {
        'earned': earned,
        'all_achievements': all_achievements,
        'earned_ids': earned_ids,
    }
    return render(request, 'progress/achievements.html', context)
