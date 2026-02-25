import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ExamTemplate
from sisalto.models import ExamQuestion, ExamAnswer, Specialty


def exams_home(request):
    """Exam templates list page."""
    exams = ExamTemplate.objects.filter(is_active=True).order_by('-year', 'semester')
    return render(request, 'exams/exams_home.html', {
        'exams': exams,
    })


@login_required
def simulation_setup(request):
    """Simulation setup: choose specialty, question count, time limit."""
    specialties = Specialty.objects.order_by('order')

    # Count available questions with model answers per specialty
    spec_data = []
    for spec in specialties:
        count = ExamQuestion.objects.filter(
            subject_area__icontains=spec.name,
            model_answer__gt='',
        ).count()
        if count > 0:
            spec_data.append({
                'id': spec.id,
                'name': spec.name,
                'question_count': count,
            })

    return render(request, 'exams/simulation_setup.html', {
        'specialties': spec_data,
    })


@login_required
@require_POST
def simulation_start(request):
    """Create simulation session and select random questions."""
    specialty_id = request.POST.get('specialty_id')
    question_count = int(request.POST.get('question_count', 5))
    time_limit = int(request.POST.get('time_limit', 60))

    # Clamp values
    question_count = max(3, min(question_count, 10))
    time_limit = max(15, min(time_limit, 180))

    # Select random questions with model answers
    if specialty_id and specialty_id != 'all':
        specialty = Specialty.objects.get(id=specialty_id)
        questions = ExamQuestion.objects.filter(
            subject_area__icontains=specialty.name,
            model_answer__gt='',
        ).order_by('?')[:question_count]
        specialty_name = specialty.name
    else:
        questions = ExamQuestion.objects.filter(
            model_answer__gt='',
        ).order_by('?')[:question_count]
        specialty_name = 'Kaikki erikoisalat'

    if not questions.exists():
        return redirect('exams:simulation_setup')

    session_id = str(uuid.uuid4())
    question_ids = list(questions.values_list('id', flat=True))

    # Store in Django session
    request.session['sim_session_id'] = session_id
    request.session['sim_question_ids'] = question_ids
    request.session['sim_time_limit'] = time_limit
    request.session['sim_specialty'] = specialty_name
    request.session['sim_started_at'] = timezone.now().isoformat()

    return redirect('exams:simulation_active')


@login_required
def simulation_active(request):
    """Active simulation page with questions and timer."""
    session_id = request.session.get('sim_session_id')
    question_ids = request.session.get('sim_question_ids', [])
    time_limit = request.session.get('sim_time_limit', 60)
    specialty_name = request.session.get('sim_specialty', '')

    if not session_id or not question_ids:
        return redirect('exams:simulation_setup')

    questions = ExamQuestion.objects.filter(id__in=question_ids)
    # Preserve the random order from session
    question_map = {q.id: q for q in questions}
    ordered_questions = [question_map[qid] for qid in question_ids if qid in question_map]

    return render(request, 'exams/simulation_active.html', {
        'questions': ordered_questions,
        'session_id': session_id,
        'time_limit': time_limit,
        'specialty_name': specialty_name,
        'question_count': len(ordered_questions),
    })


@login_required
def simulation_results(request, session_id):
    """Show simulation results."""
    answers = ExamAnswer.objects.filter(
        session_id=session_id,
        user=request.user,
        ai_score__isnull=False,
    ).select_related('question').order_by('created_at')

    if not answers.exists():
        return redirect('exams:simulation_setup')

    total_score = sum(a.ai_score for a in answers)
    max_score = len(answers) * 5
    score_pct = round(total_score / max_score * 100) if max_score > 0 else 0
    passed = score_pct >= 50

    specialty_name = request.session.get('sim_specialty', 'Tenttisimulaatio')

    return render(request, 'exams/simulation_results.html', {
        'answers': answers,
        'total_score': total_score,
        'max_score': max_score,
        'score_pct': score_pct,
        'passed': passed,
        'session_id': session_id,
        'specialty_name': specialty_name,
        'question_count': len(answers),
    })
