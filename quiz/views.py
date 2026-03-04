import json
import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from sisalto.models import Specialty, EPA
from quiz.models import Question, Choice


def _persist_quiz_progress(user, question, is_correct, selected_ids):
    """Save quiz attempt and update SR card + daily stats for authenticated users."""
    from progress.models import (
        UserQuizAttempt, SpacedRepetitionCard, DailyStats, EPAProgress
    )

    # 1. Create UserQuizAttempt
    attempt = UserQuizAttempt.objects.create(
        user=user,
        question=question,
        is_correct=is_correct,
        score=1.0 if is_correct else 0.0,
    )
    attempt.selected_choices.set(selected_ids)

    # 2. Update or create SpacedRepetitionCard
    card, created = SpacedRepetitionCard.objects.get_or_create(
        user=user, question=question
    )
    quality = 5 if is_correct else 1
    card.update_after_review(quality)

    # 3. Update DailyStats
    today = timezone.now().date()
    stats, _ = DailyStats.objects.get_or_create(user=user, date=today)
    stats.questions_answered += 1
    if is_correct:
        stats.questions_correct += 1
    stats.xp_earned += 10 if is_correct else 2
    stats.save()

    # 4. Update EPAProgress counters
    epa_progress, _ = EPAProgress.objects.get_or_create(
        user=user, epa=question.epa
    )
    epa_progress.a_level_questions_answered += 1
    if is_correct:
        epa_progress.a_level_questions_correct += 1
    epa_progress.last_activity = timezone.now()
    epa_progress.save()


def quiz_home(request):
    """Quiz home page - select topics and start practicing."""
    specialties = Specialty.objects.prefetch_related('epas').order_by('order')

    # Count questions per EPA, with difficulty breakdown
    epa_question_counts = {}
    for epa in EPA.objects.all():
        qs = Question.objects.filter(epa=epa, is_active=True)
        epa_question_counts[epa.id] = {
            'all': qs.count(),
            'easy': qs.filter(difficulty__in=[1, 2]).count(),
            'medium': qs.filter(difficulty=3).count(),
            'hard': qs.filter(difficulty__in=[4, 5]).count(),
        }

    return render(request, 'quiz/quiz_home.html', {
        'specialties': specialties,
        'epa_question_counts': json.dumps(epa_question_counts),
    })


def quiz_practice(request):
    """Start a quiz practice session. POST with selected EPA IDs."""
    if request.method == 'POST':
        epa_ids = request.POST.getlist('epa_ids')
        if not epa_ids:
            return render(request, 'quiz/quiz_home.html', {
                'specialties': Specialty.objects.prefetch_related('epas').order_by('order'),
                'epa_question_counts': json.dumps({}),
                'error': 'Valitse vahintaan yksi aihealue.',
            })

        # Store selected EPAs, difficulty and question types in session
        epa_ids = [int(x) for x in epa_ids]
        difficulty = request.POST.get('difficulty', 'all')
        question_types = request.POST.getlist('question_types')
        # If 'all' selected or nothing selected, treat as all types
        if 'all' in question_types or not question_types:
            question_types = []
        request.session['quiz_epa_ids'] = epa_ids
        request.session['quiz_difficulty'] = difficulty
        request.session['quiz_question_types'] = question_types
        request.session['quiz_score'] = 0
        request.session['quiz_total'] = 0
        request.session['quiz_answered'] = []

        qs = Question.objects.filter(epa_id__in=epa_ids, is_active=True)
        if difficulty == 'easy':
            qs = qs.filter(difficulty__in=[1, 2])
        elif difficulty == 'medium':
            qs = qs.filter(difficulty=3)
        elif difficulty == 'hard':
            qs = qs.filter(difficulty__in=[4, 5])
        if question_types:
            qs = qs.filter(question_type__in=question_types)
        total_questions = qs.count()

        difficulty_labels = {
            'all': 'Kaikki tasot',
            'easy': 'Helppo (1-2)',
            'medium': 'Haastava (3)',
            'hard': 'Tenttitaso (4-5)',
        }

        epa_names = list(
            EPA.objects.filter(id__in=epa_ids).values_list('title', flat=True)
        )

        return render(request, 'quiz/quiz_practice.html', {
            'epa_ids': epa_ids,
            'epa_names': epa_names,
            'total_available': total_questions,
            'difficulty': difficulty,
            'difficulty_label': difficulty_labels.get(difficulty, 'Kaikki tasot'),
        })

    # GET redirect to home
    return render(request, 'quiz/quiz_home.html', {
        'specialties': Specialty.objects.prefetch_related('epas').order_by('order'),
        'epa_question_counts': json.dumps({}),
    })


@require_GET
def api_get_question(request):
    """Return a random question from the selected EPAs as JSON."""
    epa_ids = request.session.get('quiz_epa_ids', [])
    answered = request.session.get('quiz_answered', [])
    difficulty = request.session.get('quiz_difficulty', 'all')
    question_types = request.session.get('quiz_question_types', [])

    if not epa_ids:
        return JsonResponse({'error': 'No EPAs selected'}, status=400)

    # Build base filter with optional difficulty and question types
    base_filter = {'epa_id__in': epa_ids, 'is_active': True}
    if difficulty == 'easy':
        base_filter['difficulty__in'] = [1, 2]
    elif difficulty == 'medium':
        base_filter['difficulty'] = 3
    elif difficulty == 'hard':
        base_filter['difficulty__in'] = [4, 5]
    if question_types:
        base_filter['question_type__in'] = question_types

    # Get unanswered questions from selected EPAs
    questions = Question.objects.filter(**base_filter).exclude(id__in=answered)

    if not questions.exists():
        # All questions answered - reset pool
        request.session['quiz_answered'] = []
        questions = Question.objects.filter(**base_filter)

    if not questions.exists():
        return JsonResponse({'error': 'No questions available'}, status=404)

    # Smart question selection: prioritize previously wrong answers
    question_id = None
    if request.user.is_authenticated:
        from progress.models import SpacedRepetitionCard
        # Find SR cards with low ease_factor (struggled questions) that are in the pool
        pool_ids = set(questions.values_list('id', flat=True))
        weak_cards = SpacedRepetitionCard.objects.filter(
            user=request.user,
            question_id__in=pool_ids,
            ease_factor__lt=2.2,  # Below default 2.5 = struggled
        ).order_by('ease_factor').values_list('question_id', flat=True)[:20]

        if weak_cards and random.random() < 0.35:
            # 35% chance to pick a weak question
            question_id = random.choice(list(weak_cards))

    if question_id is None:
        question_id = random.choice(list(questions.values_list('id', flat=True)))

    question = Question.objects.get(id=question_id)

    response_data = {
        'question_id': question.id,
        'question_type': question.question_type,
        'difficulty': question.difficulty,
        'text': question.text,
        'epa_title': question.epa.title,
        'score': request.session.get('quiz_score', 0),
        'total': request.session.get('quiz_total', 0),
    }

    if question.question_type == 'calculation':
        response_data['choices'] = []
        response_data['calculation_unit'] = question.calculation_unit or ''
        response_data['calculation_tolerance'] = question.calculation_tolerance or 5.0
    elif question.question_type == 'matching' and question.matching_pairs:
        rights = [p['right'] for p in question.matching_pairs]
        random.shuffle(rights)
        response_data['choices'] = []
        response_data['matching_pairs'] = question.matching_pairs
        response_data['matching_rights'] = rights
    else:
        choices = list(question.choices.all().values('id', 'text', 'order'))
        random.shuffle(choices)
        response_data['choices'] = choices

    return JsonResponse(response_data)


@require_POST
def api_check_answer(request):
    """Check the user's answer and return results."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question_id = data.get('question_id')
    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    try:
        question = Question.objects.get(id=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    # Grade answer based on question type
    selected_set = set()
    choice_results = []

    if question.question_type == 'calculation':
        calc_input = data.get('calculation_input')
        if calc_input is None:
            return JsonResponse({'error': 'Missing calculation_input'}, status=400)
        try:
            user_value = float(calc_input)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid calculation input'}, status=400)
        correct = question.calculation_answer
        tolerance_pct = question.calculation_tolerance or 5.0
        if correct is not None and correct != 0:
            is_correct = abs(user_value - correct) / abs(correct) * 100 <= tolerance_pct
        elif correct == 0:
            is_correct = abs(user_value) < 0.001
        else:
            is_correct = False
        choice_results = [{
            'correct_answer': correct,
            'user_answer': user_value,
            'unit': question.calculation_unit or '',
            'tolerance_pct': tolerance_pct,
        }]

    elif question.question_type == 'matching':
        matching_answers = data.get('matching_answers', {})
        if question.matching_pairs:
            correct_pairs = {p['left']: p['right'] for p in question.matching_pairs}
            is_correct = all(
                matching_answers.get(left) == right
                for left, right in correct_pairs.items()
            )
            choice_results = [
                {
                    'left': p['left'],
                    'correct_right': p['right'],
                    'user_right': matching_answers.get(p['left'], ''),
                    'pair_correct': matching_answers.get(p['left']) == p['right'],
                }
                for p in question.matching_pairs
            ]
        else:
            is_correct = False

    else:
        # multiple_choice, multi_select, true_false — all use Choice model
        selected_ids = data.get('selected_ids', [])
        if not selected_ids:
            return JsonResponse({'error': 'Missing selected_ids'}, status=400)
        choices = question.choices.all()
        correct_ids = set(choices.filter(is_correct=True).values_list('id', flat=True))
        selected_set = set(int(x) for x in selected_ids)
        is_correct = (selected_set == correct_ids)
        for c in choices:
            choice_results.append({
                'id': c.id,
                'text': c.text,
                'is_correct': c.is_correct,
                'was_selected': c.id in selected_set,
                'explanation': c.explanation,
            })

    # Update session stats
    request.session['quiz_total'] = request.session.get('quiz_total', 0) + 1
    if is_correct:
        request.session['quiz_score'] = request.session.get('quiz_score', 0) + 1
    request.session.modified = True

    # Track answered question
    answered = request.session.get('quiz_answered', [])
    if question_id not in answered:
        answered.append(question_id)
        request.session['quiz_answered'] = answered

    # Update question stats
    question.times_answered += 1
    if is_correct:
        question.times_correct += 1
    question.save(update_fields=['times_answered', 'times_correct'])

    # Persist to database if user is authenticated
    new_achievements = []
    if request.user.is_authenticated:
        _persist_quiz_progress(request.user, question, is_correct, selected_set)
        from progress.achievement_checker import check_achievements
        newly_earned = check_achievements(request.user)
        new_achievements = [
            {'name': a.name, 'icon': a.icon, 'xp_reward': a.xp_reward}
            for a in newly_earned
        ]

    response_data = {
        'is_correct': is_correct,
        'explanation': question.explanation,
        'choices': choice_results,
        'score': request.session.get('quiz_score', 0),
        'total': request.session.get('quiz_total', 0),
    }
    if new_achievements:
        response_data['new_achievements'] = new_achievements
    return JsonResponse(response_data)


# --- Spaced Repetition ---

@login_required
def spaced_review(request):
    """Spaced repetition review page."""
    from progress.models import SpacedRepetitionCard

    due_count = SpacedRepetitionCard.objects.filter(
        user=request.user, next_review__lte=timezone.now()
    ).count()
    total_cards = SpacedRepetitionCard.objects.filter(user=request.user).count()

    return render(request, 'quiz/spaced_review.html', {
        'due_count': due_count,
        'total_cards': total_cards,
    })


@require_GET
@login_required
def api_get_review_question(request):
    """Return next due SR card question as JSON."""
    from progress.models import SpacedRepetitionCard

    due_cards = SpacedRepetitionCard.objects.filter(
        user=request.user,
        next_review__lte=timezone.now()
    ).select_related('question', 'question__epa').order_by('next_review')

    card = due_cards.first()
    if not card:
        return JsonResponse({'done': True, 'remaining': 0})

    question = card.question

    response_data = {
        'done': False,
        'remaining': due_cards.count(),
        'card_id': card.id,
        'question_id': question.id,
        'question_type': question.question_type,
        'difficulty': question.difficulty,
        'text': question.text,
        'epa_title': question.epa.title,
        'interval_days': card.interval_days,
        'repetitions': card.repetitions,
    }

    if question.question_type == 'calculation':
        response_data['choices'] = []
        response_data['calculation_unit'] = question.calculation_unit or ''
        response_data['calculation_tolerance'] = question.calculation_tolerance or 5.0
    elif question.question_type == 'matching' and question.matching_pairs:
        rights = [p['right'] for p in question.matching_pairs]
        random.shuffle(rights)
        response_data['choices'] = []
        response_data['matching_pairs'] = question.matching_pairs
        response_data['matching_rights'] = rights
    else:
        choices = list(question.choices.all().values('id', 'text', 'order'))
        random.shuffle(choices)
        response_data['choices'] = choices

    return JsonResponse(response_data)


@require_POST
@login_required
def api_submit_review(request):
    """Check answer and update SR card for spaced repetition."""
    from progress.models import SpacedRepetitionCard, DailyStats

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question_id = data.get('question_id')
    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    try:
        question = Question.objects.get(id=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    # Grade answer based on question type
    selected_set = set()
    choice_results = []

    if question.question_type == 'calculation':
        calc_input = data.get('calculation_input')
        if calc_input is None:
            return JsonResponse({'error': 'Missing calculation_input'}, status=400)
        try:
            user_value = float(calc_input)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid calculation input'}, status=400)
        correct = question.calculation_answer
        tolerance_pct = question.calculation_tolerance or 5.0
        if correct is not None and correct != 0:
            is_correct = abs(user_value - correct) / abs(correct) * 100 <= tolerance_pct
        elif correct == 0:
            is_correct = abs(user_value) < 0.001
        else:
            is_correct = False
        choice_results = [{
            'correct_answer': correct,
            'user_answer': user_value,
            'unit': question.calculation_unit or '',
            'tolerance_pct': tolerance_pct,
        }]

    elif question.question_type == 'matching':
        matching_answers = data.get('matching_answers', {})
        if question.matching_pairs:
            correct_pairs = {p['left']: p['right'] for p in question.matching_pairs}
            is_correct = all(
                matching_answers.get(left) == right
                for left, right in correct_pairs.items()
            )
            choice_results = [
                {
                    'left': p['left'],
                    'correct_right': p['right'],
                    'user_right': matching_answers.get(p['left'], ''),
                    'pair_correct': matching_answers.get(p['left']) == p['right'],
                }
                for p in question.matching_pairs
            ]
        else:
            is_correct = False

    else:
        selected_ids = data.get('selected_ids', [])
        if not selected_ids:
            return JsonResponse({'error': 'Missing selected_ids'}, status=400)
        choices = question.choices.all()
        correct_ids = set(choices.filter(is_correct=True).values_list('id', flat=True))
        selected_set = set(int(x) for x in selected_ids)
        is_correct = (selected_set == correct_ids)
        for c in choices:
            choice_results.append({
                'id': c.id,
                'text': c.text,
                'is_correct': c.is_correct,
                'was_selected': c.id in selected_set,
                'explanation': c.explanation,
            })

    # Update SR card
    try:
        card = SpacedRepetitionCard.objects.get(
            user=request.user, question=question
        )
    except SpacedRepetitionCard.DoesNotExist:
        return JsonResponse({'error': 'No SR card found'}, status=404)

    quality = 5 if is_correct else 1
    card.update_after_review(quality)

    # Update daily stats
    today = timezone.now().date()
    stats, _ = DailyStats.objects.get_or_create(user=request.user, date=today)
    stats.questions_answered += 1
    if is_correct:
        stats.questions_correct += 1
    stats.xp_earned += 10 if is_correct else 2
    stats.save()

    # Update question stats
    question.times_answered += 1
    if is_correct:
        question.times_correct += 1
    question.save(update_fields=['times_answered', 'times_correct'])

    # Check for newly earned achievements
    from progress.achievement_checker import check_achievements
    newly_earned = check_achievements(request.user)
    new_achievements = [
        {'name': a.name, 'icon': a.icon, 'xp_reward': a.xp_reward}
        for a in newly_earned
    ]

    # Count remaining due cards
    remaining = SpacedRepetitionCard.objects.filter(
        user=request.user, next_review__lte=timezone.now()
    ).count()

    response_data = {
        'is_correct': is_correct,
        'explanation': question.explanation,
        'choices': choice_results,
        'remaining': remaining,
        'next_review_days': card.interval_days,
    }
    if new_achievements:
        response_data['new_achievements'] = new_achievements
    return JsonResponse(response_data)
