import json
import random
import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from sisalto.models import Specialty, EPA
from quiz.models import Question, Choice


_CLOZE_PATTERN = re.compile(r'\{\{(c\d+)::([^:}]+?)(?:::([^}]*?))?\}\}')


def _parse_cloze_text(text: str):
    """Parse cloze template text like 'Foo {{c1::answer::hint}} bar {{c2::answer2}}'.

    Returns (segments, items):
      segments: [{'type':'text','value':'...'}, {'type':'blank','id':'c1','hint':'...','length':N}, ...]
      items:    [{'id':'c1','answer':'answer','hint':'hint'}, ...]
    """
    items = []
    segments = []
    last_end = 0

    for match in _CLOZE_PATTERN.finditer(text):
        if match.start() > last_end:
            segments.append({'type': 'text', 'value': text[last_end:match.start()]})
        cloze_id = match.group(1)
        answer = match.group(2)
        hint = match.group(3) or ''
        items.append({'id': cloze_id, 'answer': answer, 'hint': hint})
        segments.append({'type': 'blank', 'id': cloze_id, 'hint': hint, 'length': len(answer)})
        last_end = match.end()

    if last_end < len(text):
        segments.append({'type': 'text', 'value': text[last_end:]})

    return segments, items


def _grade_cloze(question, data: dict):
    """Grade a cloze question. Returns (is_correct, choice_results)."""
    cloze_answers = data.get('cloze_answers', {})
    _, cloze_items = _parse_cloze_text(question.text)
    correct_count = 0
    choice_results = []
    for item in cloze_items:
        user_answer = cloze_answers.get(item['id'], '').strip().lower()
        correct_answer = item['answer'].strip().lower()
        pair_correct = user_answer == correct_answer
        if pair_correct:
            correct_count += 1
        choice_results.append({
            'id': item['id'],
            'correct_answer': item['answer'],
            'user_answer': cloze_answers.get(item['id'], ''),
            'hint': item['hint'],
            'is_correct': pair_correct,
        })
    is_correct = correct_count == len(cloze_items) and len(cloze_items) > 0
    return is_correct, choice_results


def _compute_difficulty_target(user) -> int:
    """Compute target difficulty level (1-5) from user's last 20 quiz attempts.

    Maps accuracy to difficulty using: target = clamp(round(1 + (accuracy - 0.5) * 8), 1, 5)
    Sweet spot: 75% accuracy → difficulty 3, 85% → 4, 50% → 1
    Returns 0 if not enough data (< 5 attempts).
    """
    try:
        from progress.models import UserQuizAttempt
        recent = UserQuizAttempt.objects.filter(
            user=user, is_correct__isnull=False
        ).order_by('-attempted_at').values_list('is_correct', flat=True)[:20]

        attempts = list(recent)
        if len(attempts) < 5:
            return 0  # not enough data

        accuracy = sum(1 for x in attempts if x) / len(attempts)
        target = round(1 + (accuracy - 0.5) * 8)
        return max(1, min(5, target))
    except Exception:
        return 0


def _persist_quiz_progress(user, question, is_correct, selected_ids, time_spent_seconds=None):
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
        time_spent_seconds=time_spent_seconds,
    )
    attempt.selected_choices.set(selected_ids)

    # 2. Update or create SpacedRepetitionCard
    card, created = SpacedRepetitionCard.objects.get_or_create(
        user=user, question=question
    )
    rating = 3 if is_correct else 1  # FSRS: Good=3, Again=1
    card.update_after_review(rating)

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
        qs = Question.objects.filter(epa=epa, is_active=True).exclude(question_type='flashcard')
        epa_question_counts[epa.id] = {
            'all': qs.count(),
            'easy': qs.filter(difficulty__in=[1, 2]).count(),
            'medium': qs.filter(difficulty=3).count(),
            'hard': qs.filter(difficulty__in=[4, 5]).count(),
        }

    adaptive_target = 0
    if request.user.is_authenticated:
        adaptive_target = _compute_difficulty_target(request.user)

    return render(request, 'quiz/quiz_home.html', {
        'specialties': specialties,
        'epa_question_counts': json.dumps(epa_question_counts),
        'adaptive_target': adaptive_target,
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
        flagged_only = request.POST.get('flagged_only') == 'on'
        mode = request.POST.get('mode', 'tutor')
        try:
            question_target = int(request.POST.get('question_target', 0))
        except (ValueError, TypeError):
            question_target = 0
        try:
            time_limit_minutes = int(request.POST.get('time_limit_minutes', 0))
        except (ValueError, TypeError):
            time_limit_minutes = 0

        request.session['quiz_epa_ids'] = epa_ids
        request.session['quiz_difficulty'] = difficulty
        request.session['quiz_question_types'] = question_types
        request.session['quiz_flagged_only'] = flagged_only
        request.session['quiz_mode'] = mode
        request.session['quiz_question_target'] = question_target
        request.session['quiz_time_limit_seconds'] = time_limit_minutes * 60
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
            'quiz_mode': mode,
            'quiz_question_target': question_target,
            'quiz_time_limit_seconds': time_limit_minutes * 60,
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

    # Get unanswered questions from selected EPAs (exclude flashcards)
    questions = Question.objects.filter(**base_filter).exclude(
        id__in=answered
    ).exclude(question_type='flashcard')

    # Flagged-only filter
    flagged_only = request.session.get('quiz_flagged_only', False)
    if flagged_only and request.user.is_authenticated:
        from progress.models import FlaggedQuestion
        flagged_ids = list(FlaggedQuestion.objects.filter(
            user=request.user
        ).values_list('question_id', flat=True))
        questions = questions.filter(id__in=flagged_ids)

    # Adaptive difficulty: when user chose 'all', auto-target based on recent performance
    adaptive_target = 0
    if difficulty == 'all' and request.user.is_authenticated:
        adaptive_target = _compute_difficulty_target(request.user)
        if adaptive_target > 0:
            difficulty_range = [max(1, adaptive_target - 1), adaptive_target, min(5, adaptive_target + 1)]
            adaptive_qs = questions.filter(difficulty__in=difficulty_range)
            if adaptive_qs.count() >= 5:
                questions = adaptive_qs

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
        # Find SR cards with high difficulty (struggled questions) that are in the pool
        pool_ids = set(questions.values_list('id', flat=True))
        weak_cards = SpacedRepetitionCard.objects.filter(
            user=request.user,
            question_id__in=pool_ids,
            difficulty__gt=6,  # Above FSRS default 5 = struggled
        ).order_by('-difficulty').values_list('question_id', flat=True)[:20]

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
        'adaptive_target': adaptive_target,
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
    elif question.question_type == 'cloze':
        segments, _ = _parse_cloze_text(question.text)
        response_data['text'] = ''
        response_data['choices'] = []
        response_data['cloze_segments'] = segments
    else:
        choices = list(question.choices.all().values('id', 'text', 'order'))
        random.shuffle(choices)
        response_data['choices'] = choices

    # Include flag/note data for authenticated users
    if request.user.is_authenticated:
        from progress.models import FlaggedQuestion, QuestionNote
        flag = FlaggedQuestion.objects.filter(
            user=request.user, question_id=question.id
        ).first()
        note = QuestionNote.objects.filter(
            user=request.user, question_id=question.id
        ).first()
        response_data['flag_type'] = flag.flag_type if flag else None
        response_data['note_text'] = note.note_text if note else ''

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

    elif question.question_type == 'cloze':
        is_correct, choice_results = _grade_cloze(question, data)

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

    # Parse optional time_spent_seconds from request
    time_spent = None
    raw_time = data.get('time_spent_seconds')
    if raw_time is not None:
        try:
            time_spent = int(raw_time)
            if time_spent < 0 or time_spent > 3600:
                time_spent = None
        except (ValueError, TypeError):
            time_spent = None

    # Persist to database if user is authenticated
    new_achievements = []
    if request.user.is_authenticated:
        _persist_quiz_progress(request.user, question, is_correct, selected_set, time_spent_seconds=time_spent)
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
    # Theory cross-reference link for wrong answers
    if not is_correct:
        from sisalto.views import get_theory_link_for_epa
        theory_link = get_theory_link_for_epa(question.epa)
        if theory_link:
            response_data['theory_link'] = theory_link
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
    ).exclude(
        question__question_type='flashcard'
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
        'stability': round(card.stability, 1),
        'fsrs_difficulty': round(card.difficulty, 1),
        'retrievability': card.get_retrievability(),
        'fsrs_state': card.fsrs_state,
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
    elif question.question_type == 'cloze':
        segments, _ = _parse_cloze_text(question.text)
        response_data['text'] = ''
        response_data['choices'] = []
        response_data['cloze_segments'] = segments
    else:
        choices = list(question.choices.all().values('id', 'text', 'order'))
        random.shuffle(choices)
        response_data['choices'] = choices

    # Include flag/note data (user is always authenticated for SR)
    from progress.models import FlaggedQuestion, QuestionNote
    flag = FlaggedQuestion.objects.filter(
        user=request.user, question_id=question.id
    ).first()
    note = QuestionNote.objects.filter(
        user=request.user, question_id=question.id
    ).first()
    response_data['flag_type'] = flag.flag_type if flag else None
    response_data['note_text'] = note.note_text if note else ''

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

    elif question.question_type == 'cloze':
        is_correct, choice_results = _grade_cloze(question, data)

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

    # Get SR card (don't update yet — user will rate via api_rate_review)
    try:
        card = SpacedRepetitionCard.objects.get(
            user=request.user, question=question
        )
    except SpacedRepetitionCard.DoesNotExist:
        return JsonResponse({'error': 'No SR card found'}, status=404)

    # Compute predicted intervals for all 4 FSRS ratings
    predicted_intervals = card.get_predicted_intervals()

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
        'predicted_intervals': predicted_intervals,
    }
    if new_achievements:
        response_data['new_achievements'] = new_achievements
    # Theory cross-reference link for wrong answers
    if not is_correct:
        from sisalto.views import get_theory_link_for_epa
        theory_link = get_theory_link_for_epa(question.epa)
        if theory_link:
            response_data['theory_link'] = theory_link
    return JsonResponse(response_data)


@require_POST
@login_required
def api_rate_review(request):
    """Apply FSRS rating to SR card after user sees spaced review result.

    Accepts: {question_id: int, rating: int (1-4)}
    Returns: {next_review_days: int, remaining: int}
    """
    import json as json_mod
    from progress.models import SpacedRepetitionCard

    data = json_mod.loads(request.body)
    question_id = data.get('question_id')
    rating = data.get('rating')

    if not question_id or rating not in (1, 2, 3, 4):
        return JsonResponse({'error': 'Invalid question_id or rating'}, status=400)

    try:
        card = SpacedRepetitionCard.objects.get(
            user=request.user, question_id=question_id
        )
    except SpacedRepetitionCard.DoesNotExist:
        return JsonResponse({'error': 'No SR card found'}, status=404)

    card.update_after_review(rating)

    remaining = SpacedRepetitionCard.objects.filter(
        user=request.user, next_review__lte=timezone.now()
    ).count()

    return JsonResponse({
        'next_review_days': card.interval_days,
        'remaining': remaining,
    })


# --- Question Flagging & Notes ---

@require_POST
@login_required
def api_toggle_flag(request):
    """Toggle a flag on a question. POST {question_id, flag_type}."""
    from progress.models import FlaggedQuestion

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question_id = data.get('question_id')
    flag_type = data.get('flag_type')

    if not question_id or flag_type not in ('wrong', 'guess', 'important'):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    try:
        question = Question.objects.get(id=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    existing = FlaggedQuestion.objects.filter(
        user=request.user, question=question
    ).first()

    if existing:
        if existing.flag_type == flag_type:
            existing.delete()
            return JsonResponse({'flagged': False, 'flag_type': None})
        else:
            existing.flag_type = flag_type
            existing.save(update_fields=['flag_type'])
            return JsonResponse({'flagged': True, 'flag_type': flag_type})
    else:
        FlaggedQuestion.objects.create(
            user=request.user, question=question, flag_type=flag_type
        )
        return JsonResponse({'flagged': True, 'flag_type': flag_type})


@require_GET
@login_required
def api_get_flag(request):
    """Get flag status for a question. GET ?question_id=N."""
    from progress.models import FlaggedQuestion

    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    flag = FlaggedQuestion.objects.filter(
        user=request.user, question_id=question_id
    ).first()
    return JsonResponse({
        'flagged': flag is not None,
        'flag_type': flag.flag_type if flag else None,
    })


@require_GET
@login_required
def api_flagged_questions(request):
    """Return list of flagged questions for the current user."""
    from progress.models import FlaggedQuestion

    flag_type = request.GET.get('flag_type')
    qs = FlaggedQuestion.objects.filter(
        user=request.user
    ).select_related('question', 'question__epa')
    if flag_type:
        qs = qs.filter(flag_type=flag_type)

    flags = [{
        'question_id': f.question_id,
        'question_text': f.question.text[:120],
        'flag_type': f.flag_type,
        'epa_title': f.question.epa.title,
        'created_at': f.created_at.isoformat(),
    } for f in qs.order_by('-created_at')]

    return JsonResponse({'flags': flags})


@require_POST
@login_required
def api_save_note(request):
    """Save or update a note on a question. POST {question_id, note_text}."""
    from progress.models import QuestionNote

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question_id = data.get('question_id')
    note_text = data.get('note_text', '').strip()

    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    try:
        question = Question.objects.get(id=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    if note_text:
        note, _ = QuestionNote.objects.update_or_create(
            user=request.user, question=question,
            defaults={'note_text': note_text}
        )
        return JsonResponse({'saved': True, 'note_text': note.note_text})
    else:
        QuestionNote.objects.filter(user=request.user, question=question).delete()
        return JsonResponse({'saved': True, 'note_text': ''})


@require_GET
@login_required
def api_get_note(request):
    """Get note for a question. GET ?question_id=N."""
    from progress.models import QuestionNote

    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    note = QuestionNote.objects.filter(
        user=request.user, question_id=question_id
    ).first()
    return JsonResponse({
        'note_text': note.note_text if note else '',
        'has_note': note is not None,
    })


# ── Flashcard views ─────────────────────────────────────────────────


@login_required
def flashcard_review(request):
    """Flashcard review page with flip-card UX."""
    from progress.models import SpacedRepetitionCard

    # Auto-create SR cards for flashcards the user doesn't have yet
    existing_card_qids = set(
        SpacedRepetitionCard.objects.filter(
            user=request.user,
            question__question_type='flashcard',
        ).values_list('question_id', flat=True)
    )
    missing_questions = Question.objects.filter(
        question_type='flashcard', is_active=True
    ).exclude(id__in=existing_card_qids)

    new_cards = [
        SpacedRepetitionCard(user=request.user, question=q)
        for q in missing_questions
    ]
    if new_cards:
        SpacedRepetitionCard.objects.bulk_create(new_cards, ignore_conflicts=True)

    due_count = SpacedRepetitionCard.objects.filter(
        user=request.user,
        question__question_type='flashcard',
        next_review__lte=timezone.now(),
    ).count()

    total_count = SpacedRepetitionCard.objects.filter(
        user=request.user,
        question__question_type='flashcard',
    ).count()

    return render(request, 'quiz/flashcard_review.html', {
        'due_count': due_count,
        'total_count': total_count,
    })


@require_GET
@login_required
def api_get_flashcard(request):
    """Return next due flashcard as JSON (front only)."""
    from progress.models import SpacedRepetitionCard

    due_cards = SpacedRepetitionCard.objects.filter(
        user=request.user,
        question__question_type='flashcard',
        next_review__lte=timezone.now(),
    ).select_related('question', 'question__epa').order_by('next_review')

    card = due_cards.first()
    if not card:
        return JsonResponse({'done': True, 'remaining': 0})

    question = card.question

    return JsonResponse({
        'done': False,
        'remaining': due_cards.count(),
        'question_id': question.id,
        'front': question.text,
        'epa_title': question.epa.title if question.epa else '',
        'difficulty': question.difficulty,
        'stability': round(card.stability, 1),
        'retrievability': card.get_retrievability(),
        'fsrs_state': card.fsrs_state,
    })


@require_POST
@login_required
def api_reveal_flashcard(request):
    """Reveal the back of a flashcard. Returns explanation + predicted intervals."""
    from progress.models import SpacedRepetitionCard

    data = json.loads(request.body)
    question_id = data.get('question_id')

    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    try:
        card = SpacedRepetitionCard.objects.select_related('question').get(
            user=request.user, question_id=question_id
        )
    except SpacedRepetitionCard.DoesNotExist:
        return JsonResponse({'error': 'No SR card found'}, status=404)

    predicted = card.get_predicted_intervals()

    # Flag/note data
    flag_type = ''
    note_text = ''
    try:
        from progress.models import FlaggedQuestion, QuestionNote
        flag = FlaggedQuestion.objects.filter(
            user=request.user, question_id=question_id
        ).first()
        flag_type = flag.flag_type if flag else ''
        note = QuestionNote.objects.filter(
            user=request.user, question_id=question_id
        ).first()
        note_text = note.note_text if note else ''
    except Exception:
        pass

    return JsonResponse({
        'back': card.question.explanation,
        'predicted_intervals': predicted,
        'flag_type': flag_type,
        'note_text': note_text,
    })


def export_flashcards_anki(request):
    """Export flashcards as Anki .apkg file."""
    import io
    import genanki

    epa_id = request.GET.get('epa_id')
    specialty_slug = request.GET.get('specialty')

    qs = Question.objects.filter(
        question_type='flashcard', is_active=True
    ).select_related('epa__specialty').order_by('epa__specialty__order', 'epa__order')

    if epa_id:
        qs = qs.filter(epa_id=epa_id)
    elif specialty_slug:
        qs = qs.filter(epa__specialty__slug=specialty_slug)

    if not qs.exists():
        return JsonResponse({'error': 'Ei flashcardeja'}, status=404)

    MODEL_ID = 1607392319
    DECK_ID = 2059400110

    model = genanki.Model(
        MODEL_ID,
        'Erikoistuminen Basic',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'EPA'},
        ],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<div style="font-size:1.2em;">{{Front}}</div>'
                    '<div style="color:#888;font-size:0.85em;margin-top:8px;">{{EPA}}</div>',
            'afmt': '{{FrontSide}}<hr id=answer>'
                    '<div style="font-size:1.1em;">{{Back}}</div>',
        }]
    )

    deck = genanki.Deck(DECK_ID, 'Sairaalafyysikon erikoistumiskirja')

    for q in qs:
        tag = q.epa.specialty.name.replace(' ', '_') if q.epa and q.epa.specialty else ''
        note = genanki.Note(
            model=model,
            fields=[
                q.text or '',
                q.explanation or '',
                q.epa.title if q.epa else '',
            ],
            tags=[tag] if tag else [],
        )
        deck.add_note(note)

    tmp = io.BytesIO()
    genanki.Package(deck).write_to_file(tmp)
    tmp.seek(0)

    response = HttpResponse(tmp.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="erikoistuminen_flashcards.apkg"'
    return response


@require_GET
def api_get_comments(request, question_id):
    """Get comments for a question."""
    from progress.models import QuestionComment
    comments = QuestionComment.objects.filter(
        question_id=question_id
    ).select_related('user').order_by('created_at')

    data = []
    for c in comments:
        data.append({
            'id': c.id,
            'username': c.user.username,
            'text': c.text,
            'created_at': c.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_resolved': c.is_resolved,
            'is_own': request.user.is_authenticated and c.user_id == request.user.id,
        })

    return JsonResponse({'comments': data, 'count': len(data)})


@require_POST
@login_required
def api_add_comment(request):
    """Add a comment to a question."""
    import json as _json
    from progress.models import QuestionComment
    try:
        body = _json.loads(request.body)
        question_id = body.get('question_id')
        text = (body.get('text') or '').strip()
    except Exception:
        return JsonResponse({'error': 'Virheellinen pyyntö'}, status=400)

    if not text:
        return JsonResponse({'error': 'Kommentti ei voi olla tyhjä'}, status=400)
    if len(text) > 2000:
        return JsonResponse({'error': 'Kommentti on liian pitkä (max 2000 merkkiä)'}, status=400)

    try:
        question = Question.objects.get(id=question_id, is_active=True)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Kysymystä ei löydy'}, status=404)

    comment = QuestionComment.objects.create(
        question=question,
        user=request.user,
        text=text,
    )

    return JsonResponse({
        'id': comment.id,
        'username': comment.user.username,
        'text': comment.text,
        'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
        'is_resolved': False,
        'is_own': True,
    })


@require_POST
@login_required
def api_resolve_comment(request):
    """Toggle resolved state (superuser only)."""
    import json as _json
    from progress.models import QuestionComment

    if not request.user.is_superuser:
        return JsonResponse({'error': 'Ei oikeuksia'}, status=403)

    try:
        body = _json.loads(request.body)
        comment_id = body.get('comment_id')
    except Exception:
        return JsonResponse({'error': 'Virheellinen pyyntö'}, status=400)

    try:
        comment = QuestionComment.objects.get(id=comment_id)
    except QuestionComment.DoesNotExist:
        return JsonResponse({'error': 'Kommenttia ei löydy'}, status=404)

    comment.is_resolved = not comment.is_resolved
    comment.save(update_fields=['is_resolved'])
    return JsonResponse({'is_resolved': comment.is_resolved})
