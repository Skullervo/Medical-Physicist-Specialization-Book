import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, IntegerField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
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

    # Learning paths summary for dashboard widget
    paths_summary = []
    for spec in specialties:
        epas_list = list(spec.epas.order_by('order'))
        total = len(epas_list)
        mastered = sum(
            1 for epa in epas_list
            if (EPAProgress.objects.filter(user=user, epa=epa)
                .values_list('overall_mastery', flat=True).first() or 0) >= 70
        )
        paths_summary.append({
            'name': spec.name,
            'slug': spec.slug,
            'total': total,
            'mastered': mastered,
            'pct': round(mastered / total * 100) if total > 0 else 0,
        })

    # 30-day trend data (for CSS bar chart in template)
    trend_data_list = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        stat = DailyStats.objects.filter(user=user, date=d).first()
        answered = stat.questions_answered if stat else 0
        correct = stat.questions_correct if stat else 0
        day_accuracy = round(correct / answered * 100) if answered > 0 else None
        trend_data_list.append({'date': d.strftime('%d.%m'), 'answered': answered, 'accuracy': day_accuracy})

    # 90-day heatmap data
    heatmap_data = []
    for i in range(89, -1, -1):
        d = today - timedelta(days=i)
        stat = DailyStats.objects.filter(user=user, date=d).first()
        count = stat.questions_answered if stat else 0
        intensity = 0 if count == 0 else (1 if count < 5 else (2 if count < 15 else (3 if count < 30 else 4)))
        heatmap_data.append({'date': d.strftime('%d.%m'), 'count': count, 'intensity': intensity})

    # Hardest questions globally (top 10 lowest accuracy, min 5 answers)
    hard_questions = list(
        Question.objects
        .filter(times_answered__gte=5, is_active=True)
        .exclude(question_type='flashcard')
        .annotate(accuracy=Cast(F('times_correct') * 100 / F('times_answered'), output_field=IntegerField()))
        .order_by('accuracy')[:10]
    )

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
        'trend_data_list': trend_data_list,
        'heatmap_data': heatmap_data,
        'hard_questions': hard_questions,
        'paths_summary': paths_summary,
    }
    return render(request, 'progress/progress_home.html', context)


@login_required
def learning_paths(request):
    """Overview of all learning paths (one per specialty)."""
    specialties = Specialty.objects.prefetch_related('epas').order_by('order')
    paths = []
    for spec in specialties:
        epas = spec.epas.order_by('order')
        total_epas = epas.count()
        mastered_count = 0
        next_epa = None
        for epa in epas:
            progress = EPAProgress.objects.filter(user=request.user, epa=epa).first()
            mastery = progress.overall_mastery if progress else 0
            if mastery >= 70:
                mastered_count += 1
            elif next_epa is None:
                next_epa = epa
        paths.append({
            'specialty': spec,
            'total_epas': total_epas,
            'mastered_count': mastered_count,
            'progress_pct': round(mastered_count / total_epas * 100) if total_epas > 0 else 0,
            'next_epa': next_epa,
        })
    return render(request, 'progress/learning_paths.html', {'paths': paths})


@login_required
def learning_path_detail(request, specialty_slug):
    """Detailed EPA list for one specialty, ordered for progression."""
    specialty = get_object_or_404(Specialty, slug=specialty_slug)
    epas = EPA.objects.filter(specialty=specialty).order_by('order')
    epa_data = []
    for epa in epas:
        progress = EPAProgress.objects.filter(user=request.user, epa=epa).first()
        mastery = round(progress.overall_mastery) if progress else 0
        answered = progress.a_level_questions_answered if progress else 0
        correct = progress.a_level_questions_correct if progress else 0
        q_count = Question.objects.filter(epa=epa, is_active=True).exclude(question_type='flashcard').count()
        status = 'mastered' if mastery >= 70 else ('in_progress' if answered > 0 else 'not_started')
        epa_data.append({
            'epa': epa,
            'mastery': mastery,
            'answered': answered,
            'correct': correct,
            'q_count': q_count,
            'status': status,
        })
    return render(request, 'progress/learning_path_detail.html', {
        'specialty': specialty,
        'epa_data': epa_data,
    })


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
