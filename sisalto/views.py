"""
Django Views for Sairaalafyysikko Erikoistuminen Application

This file contains all view functions organized by functionality:
1. Main page views (frontpage, specialty lists, etc.)
2. Radiologia views and section management endpoints
3. Sadehoito views and section management endpoints  
4. Isotooppi views and section management endpoints
5. KNF views and section management endpoints
6. Fysiologia views and section management endpoints
"""

# =============================================================================
# IMPORTS
# =============================================================================
from django.contrib.auth import login
from django.db import models as db_models
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Max, Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Section, EPA, Specialty, ExamQuestion, TheoryImage, TheoryContent
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def register_view(request):
    """User registration page."""
    from .forms import RegistrationForm

    if request.user.is_authenticated:
        return redirect('frontpage')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('frontpage')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def search_view(request):
    """Full-text search across EPA sections and exam questions."""
    import re
    from django.utils.html import strip_tags

    query = request.GET.get('q', '').strip()
    sections = []
    exam_questions = []

    if query and len(query) >= 2:
        sections = list(
            Section.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('epa', 'epa__specialty').order_by(
                'epa__specialty__order', 'epa__order'
            )[:50]
        )
        exam_questions = list(
            ExamQuestion.objects.filter(
                Q(question_text__icontains=query) | Q(model_answer__icontains=query)
            ).order_by('-year')[:50]
        )

        # Build snippets for sections
        for section in sections:
            plain = strip_tags(section.content)
            pos = plain.lower().find(query.lower())
            if pos >= 0:
                start = max(0, pos - 80)
                end = min(len(plain), pos + len(query) + 120)
                snippet = ('...' if start > 0 else '') + plain[start:end] + ('...' if end < len(plain) else '')
                snippet = re.sub(
                    re.escape(query), lambda m: f'<mark>{m.group()}</mark>', snippet, flags=re.IGNORECASE
                )
            else:
                snippet = plain[:200] + ('...' if len(plain) > 200 else '')
            section.snippet = snippet

    return render(request, 'sisalto/search_results.html', {
        'query': query,
        'sections': sections,
        'exam_questions': exam_questions,
        'total': len(sections) + len(exam_questions),
    })


# =============================================================================
# GENERAL PAGE VIEWS
# =============================================================================

def frontpage_view(request):
	"""Main landing page view with statistics and navigation"""
	from quiz.models import Question

	# Statistics
	epa_count = EPA.objects.exclude(
		specialty__name__in=['Yleinen', 'Yleiset', 'raportoi_ongelma']
	).count()
	exam_question_count = ExamQuestion.objects.count()
	model_answer_count = ExamQuestion.objects.exclude(model_answer='').count()
	quiz_question_count = Question.objects.count()

	# Specialties with EPA counts and colors
	specialty_data = []
	color_map = {
		'Radiologia': '#60a5fa',
		'Sädehoito': '#34d399',
		'Isotooppilääketiede': '#a78bfa',
		'Isotooppi': '#a78bfa',
		'KNF': '#fb923c',
		'Fysiologia': '#f87171',
	}
	icon_map = {
		'Radiologia': 'fa-x-ray',
		'Sädehoito': 'fa-radiation',
		'Isotooppilääketiede': 'fa-atom',
		'Isotooppi': 'fa-atom',
		'KNF': 'fa-brain',
		'Fysiologia': 'fa-heartbeat',
	}
	slug_map = {
		'Radiologia': 'radiologia',
		'Sädehoito': 'sadehoito',
		'Isotooppilääketiede': 'isotooppikuvantaminen',
		'Isotooppi': 'isotooppikuvantaminen',
		'KNF': 'knf',
		'Fysiologia': 'fysiologia',
	}
	exclude_names = ['Yleinen', 'Yleiset', 'raportoi_ongelma', 'Isotooppi']
	for spec in Specialty.objects.exclude(name__in=exclude_names).order_by('order'):
		epa_in_spec = EPA.objects.filter(specialty=spec).count()
		if epa_in_spec > 0:
			specialty_data.append({
				'name': spec.name,
				'epa_count': epa_in_spec,
				'color': color_map.get(spec.name, '#60a5fa'),
				'icon': icon_map.get(spec.name, 'fa-book'),
				'slug': slug_map.get(spec.name, spec.slug),
			})

	return render(request, 'sisalto/frontpage_new.html', {
		'page_title': 'Etusivu',
		'epa_count': epa_count,
		'exam_question_count': exam_question_count,
		'model_answer_count': model_answer_count,
		'quiz_question_count': quiz_question_count,
		'specialty_count': len(specialty_data),
		'specialties': specialty_data,
	})

def modaliteetit_view(request):
	"""Modalities theory listing page"""
	modalities = [
		{
			'name': 'Radiologia',
			'description': 'Natiivikuvantaminen, TT, MRI, läpivalaisu, mammografia, ultraääni, näytöt, hammas, säteilysuojelu',
			'count': 9,
			'url': '/modaliteetit/radiologia/',
			'color': '#60a5fa',
			'icon': 'fa-x-ray',
			'available': True,
		},
		{
			'name': 'Sädehoito',
			'description': 'Peruskäsitteet, kuvantaminen, ulkoinen, sisäinen, dosimetria, laitteet, säteilybiologia',
			'count': 7,
			'url': '/modaliteetit/sadehoito/',
			'color': '#34d399',
			'icon': 'fa-radiation',
			'available': True,
		},
		{
			'name': 'Isotooppilääketiede',
			'description': 'Gammakamera, PET, radiofarmasia, SPET, radionuklidihoidot, säteilysuojelu',
			'count': 7,
			'url': '/modaliteetit/isotooppi/',
			'color': '#a78bfa',
			'icon': 'fa-atom',
			'available': True,
		},
		{
			'name': 'Kliininen neurofysiologia',
			'description': 'EEG, herätepotentiaali, ENMG, TMS, uni, IOM',
			'count': 6,
			'url': '/modaliteetit/knf/',
			'color': '#fb923c',
			'icon': 'fa-brain',
			'available': True,
		},
		{
			'name': 'Kliininen fysiologia',
			'description': 'EKG, verenkierto, keuhkofunktio, GI-kanava, DXA',
			'count': 5,
			'url': '/modaliteetit/fysiologia/',
			'color': '#f87171',
			'icon': 'fa-heartbeat',
			'available': True,
		},
	]
	return render(request, 'sisalto/modaliteetit/index.html', {
		'page_title': 'Modaliteetit',
		'modalities': modalities,
	})


# =============================================================================
# THEORY <-> QUESTION CROSS-REFERENCE UTILITY
# =============================================================================

# Maps specialty name patterns to modality slugs and tab_id -> EPA title prefix
_MODALITY_TAB_MAP = {
	'Radiolog': {
		'slug': 'radiologia',
		'tabs': {
			'natiivi': 'Natiivikuvantaminen',
			'tt': 'Tietokonetomografia',
			'mri': 'Magneettikuvaus',
			'lapivalaisu': 'Läpivalaisu',
			'mammografia': 'Mammografia',
			'ultraaani': 'Ultraääni',
			'naytot': 'Kuvankatselunäytöt',
			'hammas': 'Hammaskuvantaminen',
			'sateilysuojelu': 'Säteilybiologia',
		}
	},
	'dehoito': {
		'slug': 'sadehoito',
		'tabs': {
			'peruskasitteet': 'Peruskäsitteet',
			'kuvantaminen': 'Kuvantaminen',
			'ulkoinen': 'Ulkoinen',
			'sisainen': 'Sisäinen',
			'dosimetria': 'Dosimetria',
			'laitteet': 'Laitteet',
			'sateilybiologia': 'Säteilybiologia',
		}
	},
	'isotooppi': {
		'slug': 'isotooppi',
		'tabs': {
			'gammakamera': 'Gammakamera',
			'pet': 'PET-kamera',
			'radiofarmasia': 'Annostelu',
			'spet': 'Gammakuvaus',
			'pet-tutkimukset': 'PET-tutkimukset',
			'radionuklidihoidot': 'Radionuklidi',
			'sateilybiologia': 'Säteilybiologia',
		}
	},
	'fysiolog': {
		'slug': 'fysiologia',
		'tabs': {
			'ekg': 'EKG',
			'verenkierto': 'Verenkierto',
			'keuhkofunktio': 'Keuhkofunktio',
			'gi': 'GI-kanavan',
			'dxa': 'Luuston',
		}
	},
	'KNF': {
		'slug': 'knf',
		'tabs': {
			'eeg': 'EEG',
			'heratepotentiaali': 'Herätepotentiaali',
			'iom': 'IOM',
			'uni': 'Uni',
			'tms': 'Sarja-TMS',
			'laiteturvallisuus': 'Laite-',
		}
	},
}


def get_theory_link_for_epa(epa) -> dict | None:
	"""Return {'url': '/modaliteetit/radiologia/#natiivi', 'epa_title': '...'} or None."""
	specialty_name = epa.specialty.name if epa.specialty else ''

	for pattern, config in _MODALITY_TAB_MAP.items():
		if pattern in specialty_name or specialty_name == pattern:
			for tab_id, title_prefix in config['tabs'].items():
				if epa.title.startswith(title_prefix):
					return {
						'url': f"/modaliteetit/{config['slug']}/#{tab_id}",
						'epa_title': epa.title,
					}
	return None


@never_cache
def modaliteetit_radiologia_view(request):
	"""Radiologia theory page with tabs for each sub-modality"""
	import random as _random  # noqa: F811
	spec = Specialty.objects.filter(name__icontains='Radiolog').first()
	tab_epa_map = {}
	if spec:
		epas = EPA.objects.filter(specialty=spec)
		TAB_TITLES = {
			'natiivi': 'Natiivikuvantaminen',
			'tt': 'Tietokonetomografia',
			'mri': 'Magneettikuvaus',
			'lapivalaisu': 'Läpivalaisu',
			'mammografia': 'Mammografia',
			'ultraaani': 'Ultraääni',
			'naytot': 'Kuvankatselunäytöt',
			'hammas': 'Hammaskuvantaminen',
			'sateilysuojelu': 'Säteilybiologia',
		}
		for tab_id, title_prefix in TAB_TITLES.items():
			epa = epas.filter(title__istartswith=title_prefix).first()
			if epa:
				tab_epa_map[tab_id] = epa.id
	# Question counts per tab
	from quiz.models import Question
	tab_question_counts = {}
	for tab_id, epa_id in tab_epa_map.items():
		tab_question_counts[tab_id] = Question.objects.filter(epa_id=epa_id, is_active=True).count()

	return render(request, 'sisalto/modaliteetit/radiologia.html', {
		'page_title': 'Radiologian teoria',
		'tab_epa_map': json.dumps(tab_epa_map),
		'tab_question_counts': json.dumps(tab_question_counts),
		'modality_id': 'radiologia',
		'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
	})


@never_cache
def modaliteetit_sadehoito_view(request):
	"""Sädehoito theory page with tabs for each sub-modality"""
	spec = Specialty.objects.filter(name__icontains='dehoito').first()
	tab_epa_map = {}
	if spec:
		epas = EPA.objects.filter(specialty=spec)
		TAB_TITLES = {
			'peruskasitteet': 'Peruskäsitteet',
			'kuvantaminen': 'Kuvantaminen',
			'ulkoinen': 'Ulkoinen',
			'sisainen': 'Sisäinen',
			'dosimetria': 'Dosimetria',
			'laitteet': 'Laitteet',
			'sateilybiologia': 'Säteilybiologia',
		}
		for tab_id, title_prefix in TAB_TITLES.items():
			epa = epas.filter(title__istartswith=title_prefix).first()
			if epa:
				tab_epa_map[tab_id] = epa.id

	from quiz.models import Question
	tab_question_counts = {}
	for tab_id, epa_id in tab_epa_map.items():
		tab_question_counts[tab_id] = Question.objects.filter(epa_id=epa_id, is_active=True).count()

	return render(request, 'sisalto/modaliteetit/sadehoito.html', {
		'page_title': 'Sädehoidon teoria',
		'tab_epa_map': json.dumps(tab_epa_map),
		'tab_question_counts': json.dumps(tab_question_counts),
		'modality_id': 'sadehoito',
		'is_superuser': request.user.is_superuser,
	})


@never_cache
def modaliteetit_isotooppi_view(request):
	"""Isotooppilääketiede theory page with tabs for each sub-modality"""
	spec = Specialty.objects.filter(name__icontains='isotooppi').first()
	tab_epa_map = {}
	if spec:
		epas = EPA.objects.filter(specialty=spec)
		TAB_TITLES = {
			'gammakamera': 'Gammakamera',
			'pet': 'PET-kamera',
			'radiofarmasia': 'Annostelu',
			'spet': 'Gammakuvaus',
			'pet-tutkimukset': 'PET-tutkimukset',
			'radionuklidihoidot': 'Radionuklidi',
			'sateilybiologia': 'Säteilybiologia',
		}
		for tab_id, title_prefix in TAB_TITLES.items():
			epa = epas.filter(title__istartswith=title_prefix).first()
			if epa:
				tab_epa_map[tab_id] = epa.id

	from quiz.models import Question
	tab_question_counts = {}
	for tab_id, epa_id in tab_epa_map.items():
		tab_question_counts[tab_id] = Question.objects.filter(epa_id=epa_id, is_active=True).count()

	return render(request, 'sisalto/modaliteetit/isotooppi.html', {
		'page_title': 'Isotooppilääketieteen teoria',
		'tab_epa_map': json.dumps(tab_epa_map),
		'tab_question_counts': json.dumps(tab_question_counts),
		'modality_id': 'isotooppi',
		'is_superuser': request.user.is_superuser,
	})


@never_cache
def modaliteetit_fysiologia_view(request):
	"""Kliininen fysiologia theory page with tabs for each sub-modality"""
	spec = Specialty.objects.filter(name__icontains='fysiolog').first()
	tab_epa_map = {}
	if spec:
		epas = EPA.objects.filter(specialty=spec)
		TAB_TITLES = {
			'ekg': 'EKG',
			'verenkierto': 'Verenkierto',
			'keuhkofunktio': 'Keuhkofunktio',
			'gi': 'GI-kanavan',
			'dxa': 'Luuston',
		}
		for tab_id, title_prefix in TAB_TITLES.items():
			epa = epas.filter(title__istartswith=title_prefix).first()
			if epa:
				tab_epa_map[tab_id] = epa.id

	from quiz.models import Question
	tab_question_counts = {}
	for tab_id, epa_id in tab_epa_map.items():
		tab_question_counts[tab_id] = Question.objects.filter(epa_id=epa_id, is_active=True).count()

	return render(request, 'sisalto/modaliteetit/fysiologia.html', {
		'page_title': 'Kliinisen fysiologian teoria',
		'tab_epa_map': json.dumps(tab_epa_map),
		'tab_question_counts': json.dumps(tab_question_counts),
		'modality_id': 'fysiologia',
		'is_superuser': request.user.is_superuser,
	})


@never_cache
def modaliteetit_knf_view(request):
	"""Kliininen neurofysiologia theory page with tabs for each sub-modality"""
	spec = Specialty.objects.filter(name='KNF').first()
	tab_epa_map = {}
	if spec:
		epas = EPA.objects.filter(specialty=spec)
		TAB_TITLES = {
			'eeg': 'EEG',
			'heratepotentiaali': 'Herätepotentiaali',
			'iom': 'IOM',
			'uni': 'Uni',
			'tms': 'Sarja-TMS',
			'laiteturvallisuus': 'Laite-',
		}
		for tab_id, title_prefix in TAB_TITLES.items():
			epa = epas.filter(title__istartswith=title_prefix).first()
			if epa:
				tab_epa_map[tab_id] = epa.id

	from quiz.models import Question
	tab_question_counts = {}
	for tab_id, epa_id in tab_epa_map.items():
		tab_question_counts[tab_id] = Question.objects.filter(epa_id=epa_id, is_active=True).count()

	return render(request, 'sisalto/modaliteetit/knf.html', {
		'page_title': 'Kliinisen neurofysiologian teoria',
		'tab_epa_map': json.dumps(tab_epa_map),
		'tab_question_counts': json.dumps(tab_question_counts),
		'modality_id': 'knf',
		'is_superuser': request.user.is_superuser,
	})


# =============================================================================
# THEORY QUIZ API (inline quiz on theory pages)
# =============================================================================

@require_GET
def theory_quiz_question(request, epa_id):
	"""Return a random question for the given EPA. Supports all question types."""
	import random
	from quiz.models import Question

	# Accept ?types=multiple_choice,true_false,calculation,matching,cloze
	ALLOWED_TYPES = ['multiple_choice', 'multi_select', 'true_false', 'calculation', 'matching', 'cloze']
	types_param = request.GET.get('types', '')
	if types_param:
		requested_types = [t.strip() for t in types_param.split(',') if t.strip() in ALLOWED_TYPES]
	else:
		requested_types = ALLOWED_TYPES

	questions = Question.objects.filter(
		epa_id=epa_id,
		question_type__in=requested_types,
		is_active=True,
	)
	# Exclude already-answered questions (session-based)
	types_suffix = '_'.join(sorted(requested_types))
	session_key = f'theory_quiz_answered_{epa_id}_{types_suffix}'
	answered = request.session.get(session_key, [])
	pool = questions.exclude(id__in=answered)
	if not pool.exists():
		request.session[session_key] = []
		answered = []
		pool = questions

	question = pool.order_by('?').first()
	if not question:
		return JsonResponse({'error': 'Ei kysymyksiä valituilla tyypeillä'}, status=404)

	response_data = {
		'question_id': question.id,
		'question_type': question.question_type,
		'text': question.text,
		'total_available': questions.count(),
		'answered_count': len(answered),
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
		from quiz.views import _parse_cloze_text
		segments, _ = _parse_cloze_text(question.text)
		response_data['text'] = ''
		response_data['choices'] = []
		response_data['cloze_segments'] = segments
	else:
		# multiple_choice, multi_select, true_false
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
def theory_quiz_answer(request):
	"""Check the user's answer and return results. Supports all question types."""
	from quiz.models import Question

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

	is_correct = False
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
					'right': p['right'],
					'user_right': matching_answers.get(p['left'], ''),
					'pair_correct': matching_answers.get(p['left']) == p['right'],
				}
				for p in question.matching_pairs
			]

	elif question.question_type == 'cloze':
		from quiz.views import _grade_cloze
		is_correct, choice_results = _grade_cloze(question, data)

	else:
		# multiple_choice, multi_select, true_false
		selected_ids = data.get('selected_ids', [])
		if not selected_ids:
			return JsonResponse({'error': 'Missing selected_ids'}, status=400)
		choices = question.choices.all()
		correct_ids = set(choices.filter(is_correct=True).values_list('id', flat=True))
		selected_set = set(int(x) for x in selected_ids)
		is_correct = (selected_set == correct_ids)
		choice_results = [{
			'id': c.id,
			'text': c.text,
			'is_correct': c.is_correct,
			'was_selected': c.id in selected_set,
			'explanation': c.explanation or '',
		} for c in choices]

	# Track in session (match all possible type suffixes)
	for suffix_key in request.session.keys():
		if suffix_key.startswith(f'theory_quiz_answered_{question.epa_id}_'):
			answered = request.session.get(suffix_key, [])
			if question_id not in answered:
				answered.append(question_id)
				request.session[suffix_key] = answered
	request.session.modified = True

	# Update question stats
	question.times_answered += 1
	if is_correct:
		question.times_correct += 1
	question.save(update_fields=['times_answered', 'times_correct'])

	return JsonResponse({
		'is_correct': is_correct,
		'question_type': question.question_type,
		'explanation': question.explanation or '',
		'choices': choice_results,
	})


def specialty_list_view(request):
	"""List all medical specialties"""
	specialties = Specialty.objects.all()
	return render(request, 'sisalto/specialty_list.html', {'specialties': specialties})

def specialty_detail_view(request, specialty_id):
	"""Show details for a specific specialty"""
	specialty = get_object_or_404(Specialty, id=specialty_id)
	return render(request, 'sisalto/specialty_detail.html', {'specialty': specialty})

_EPA_URL_CACHE = None

def _build_epa_url_cache():
	"""Build EPA (specialty_name, title) → canonical URL mapping from URL config."""
	import inspect, re
	from django.urls import get_resolver, reverse

	cache = {}
	resolver = get_resolver()
	prefixes = ['radiologia', 'sadehoito', 'isotooppi', 'knf', 'fysiologia']
	skip = ['add_', 'edit_', 'delete_', 'update_', '_epas', '_subpages']

	patterns = list(resolver.url_patterns)
	for pattern in patterns:
		if hasattr(pattern, 'url_patterns'):
			patterns.extend(pattern.url_patterns)
			continue
		name = getattr(pattern, 'name', '') or ''
		if not any(name.startswith(p + '_') for p in prefixes):
			continue
		if any(k in name for k in skip):
			continue
		try:
			source = inspect.getsource(pattern.callback)
			spec_m = re.search(r'get_or_create\(name=["\'](.+?)["\']', source)
			title_m = re.search(r'title=["\'](.+?)["\']', source)
			if spec_m and title_m:
				cache[(spec_m.group(1), title_m.group(1))] = reverse(name)
		except Exception:
			pass
	return cache


def epa_detail_view(request, epa_id):
	"""Redirect to specialty-specific EPA page, or render generic template."""
	global _EPA_URL_CACHE
	epa = get_object_or_404(EPA, id=epa_id)

	# Try redirect to canonical specialty URL
	if _EPA_URL_CACHE is None:
		_EPA_URL_CACHE = _build_epa_url_cache()
	canonical = _EPA_URL_CACHE.get((epa.specialty.name, epa.title))
	if canonical:
		return redirect(canonical)

	# Fallback: render generic template
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/epa_detail.html', {
		'page_title': epa.title,
		'epa': epa,
		'sections': sections,
	})


@csrf_exempt
def generic_add_section_view(request, epa_id):
	"""Generic add section endpoint for /epa/<id>/"""
	return add_section_view(request)


@csrf_exempt
def generic_edit_section_view(request, epa_id):
	"""Generic edit section endpoint for /epa/<id>/"""
	return edit_section_view(request)


@csrf_exempt
def generic_delete_section_view(request, epa_id):
	"""Generic delete section endpoint for /epa/<id>/"""
	return delete_section_view(request)


@csrf_exempt
def generic_update_proficiency_view(request, epa_id):
	"""Generic update proficiency endpoint for /epa/<id>/"""
	return update_proficiency_view(request)


def examquestion_list_view(request):
	"""List exam questions grouped by modality."""
	from collections import OrderedDict
	from .models import ExamQuestion

	questions = ExamQuestion.objects.all().order_by('-year', 'exam_date', 'question_number')

	# Group by subject_area
	modality_order = [
		'Radiologia', 'Sädehoito', 'Isotooppilääketiede', 'KNF',
		'Fysiologia', 'Kliininen fysiologia', 'Anatomia',
		'Sädehoito/Kuvantaminen', '',
	]
	modality_icons = {
		'Radiologia': 'fa-x-ray',
		'Sädehoito': 'fa-radiation',
		'Isotooppilääketiede': 'fa-atom',
		'KNF': 'fa-brain',
		'Fysiologia': 'fa-heartbeat',
		'Kliininen fysiologia': 'fa-stethoscope',
		'Anatomia': 'fa-bone',
		'Sädehoito/Kuvantaminen': 'fa-camera',
		'': 'fa-question-circle',
	}
	modality_colors = {
		'Radiologia': '#3498db',
		'Sädehoito': '#e74c3c',
		'Isotooppilääketiede': '#9b59b6',
		'KNF': '#e67e22',
		'Fysiologia': '#2ecc71',
		'Kliininen fysiologia': '#1abc9c',
		'Anatomia': '#f1c40f',
		'Sädehoito/Kuvantaminen': '#e74c3c',
		'': '#7f8c8d',
	}

	grouped = OrderedDict()
	for area in modality_order:
		area_questions = [q for q in questions if q.subject_area == area]
		if area_questions:
			label = area if area else 'Luokittelematon'
			model_answer_count = len([q for q in area_questions if q.model_answer])
			grouped[label] = {
				'questions': area_questions,
				'count': len(area_questions),
				'model_answer_count': model_answer_count,
				'icon': modality_icons.get(area, 'fa-question-circle'),
				'color': modality_colors.get(area, '#7f8c8d'),
			}

	# Stats
	years = [q.year for q in questions if q.year]
	years_range = f"{min(years)}-{max(years)}" if years else "N/A"
	model_answer_count = len([q for q in questions if q.model_answer])

	return render(request, 'sisalto/examquestion_list.html', {
		'grouped': grouped,
		'total_count': questions.count(),
		'modality_count': len(grouped),
		'model_answer_count': model_answer_count,
		'years_range': years_range,
	})

def examquestion_area_view(request, area_slug):
	"""List exam questions for a specific subject area."""
	from .models import ExamQuestion

	# Map slugs to subject areas
	slug_to_area = {
		'radiologia': 'Radiologia',
		'sadehoito': 'Sädehoito',
		'isotooppilaaketiede': 'Isotooppilääketiede',
		'knf': 'KNF',
		'fysiologia': 'Fysiologia',
		'kliininen-fysiologia': 'Kliininen fysiologia',
		'anatomia': 'Anatomia',
		'anatomia-fysiologia': 'Anatomia/Fysiologia',
		'kliininen-neurofysiologia': 'Kliininen neurofysiologia',
	}

	area_name = slug_to_area.get(area_slug)
	if not area_name:
		return render(request, 'sisalto/examquestion_list.html', {
			'error': f'Aihealuetta "{area_slug}" ei loydy',
		})

	# Get questions for this area
	questions = ExamQuestion.objects.filter(
		subject_area=area_name
	).order_by('-year', 'exam_date', 'question_number')

	modality_icons = {
		'Radiologia': 'fa-x-ray',
		'Sädehoito': 'fa-radiation',
		'Isotooppilääketiede': 'fa-atom',
		'KNF': 'fa-brain',
		'Fysiologia': 'fa-heartbeat',
		'Kliininen fysiologia': 'fa-stethoscope',
		'Anatomia': 'fa-bone',
		'Anatomia/Fysiologia': 'fa-bone',
		'Kliininen neurofysiologia': 'fa-brain',
	}
	modality_colors = {
		'Radiologia': '#3498db',
		'Sädehoito': '#e74c3c',
		'Isotooppilääketiede': '#9b59b6',
		'KNF': '#e67e22',
		'Fysiologia': '#2ecc71',
		'Kliininen fysiologia': '#1abc9c',
		'Anatomia': '#f1c40f',
		'Anatomia/Fysiologia': '#f1c40f',
		'Kliininen neurofysiologia': '#e67e22',
	}

	years = [q.year for q in questions if q.year]
	years_range = f"{min(years)}-{max(years)}" if years else "N/A"

	return render(request, 'sisalto/examquestion_area.html', {
		'area_name': area_name,
		'area_slug': area_slug,
		'questions': questions,
		'icon': modality_icons.get(area_name, 'fa-question-circle'),
		'color': modality_colors.get(area_name, '#7f8c8d'),
		'total_count': questions.count(),
		'years_range': years_range,
	})

def table_questions_view(request):
	"""Modern table view for exam questions"""
	try:
		from .models import ExamQuestion
		questions = ExamQuestion.objects.all().order_by('-year', 'exam_date', 'question_number')
	except:
		questions = []
	
	return render(request, 'sisalto/table_questions.html', {'questions': questions})

def exam_practice_view(request):
	"""Tenttikysymysten harjoittelusivu - yksittainen tai satunnainen kysymys."""
	from .models import ExamQuestion

	question_id = request.GET.get('question')
	question = None
	if question_id:
		try:
			question = ExamQuestion.objects.get(id=int(question_id))
		except (ExamQuestion.DoesNotExist, ValueError):
			pass

	# If no specific question, pick a random one
	if not question:
		question = ExamQuestion.objects.order_by('?').first()

	# Get next/prev for navigation
	next_q = None
	prev_q = None
	if question:
		next_q = ExamQuestion.objects.filter(id__gt=question.id).order_by('id').first()
		prev_q = ExamQuestion.objects.filter(id__lt=question.id).order_by('-id').first()

	return render(request, 'sisalto/exam_practice.html', {
		'question': question,
		'next_q': next_q,
		'prev_q': prev_q,
	})

@csrf_exempt
def generate_exam_view(request):
	"""Generoidaan satunnaisia tenttikysymyksiä"""
	if request.method == "POST":
		import json
		import random
		import uuid
		from .models import ExamQuestion
		
		data = json.loads(request.body)
		num_questions = int(data.get('num_questions', 5))
		start_year = data.get('start_year')
		end_year = data.get('end_year')
		
		# Suodatetaan kysymykset vuosien mukaan
		questions = ExamQuestion.objects.all()
		if start_year:
			questions = questions.filter(year__gte=int(start_year))
		if end_year:
			questions = questions.filter(year__lte=int(end_year))
		
		# Arvotaan satunnaiset kysymykset
		if questions.count() >= num_questions:
			selected_questions = random.sample(list(questions), num_questions)
		else:
			selected_questions = list(questions)
		
		# Luodaan uniikki session_id
		session_id = str(uuid.uuid4())
		
		# Palautetaan kysymykset
		questions_data = []
		for q in selected_questions:
			questions_data.append({
				'id': q.id,
				'exam_date': q.exam_date,
				'question_number': q.question_number,
				'question_text': q.question_text,
				'subject_area': q.subject_area,
				'year': q.year
			})
		
		return JsonResponse({
			'success': True,
			'session_id': session_id,
			'questions': questions_data
		})
	
	return JsonResponse({'success': False})

@csrf_exempt
def submit_exam_answers_view(request):
	"""Käsitellään käyttäjän vastaukset ja pyydä GPT:ltä arviointi"""
	if request.method == "POST":
		import json
		from .models import ExamQuestion, ExamAnswer
		
		data = json.loads(request.body)
		session_id = data.get('session_id')
		answers = data.get('answers', [])
		
		results = []
		
		for answer_data in answers:
			question_id = answer_data.get('question_id')
			user_answer = answer_data.get('answer', '')
			
			try:
				question = ExamQuestion.objects.get(id=question_id)
				
				# Tallennetaan vastaus tietokantaan
				exam_answer = ExamAnswer.objects.create(
					session_id=session_id,
					question=question,
					user_answer=user_answer
				)
				
				# Tässä kutsuttaisiin GPT:tä, toistaiseksi dummy-arviointi
				gpt_evaluation = f"Vastaus kysymykseen '{question.question_text[:50]}...' on {len(user_answer.split())} sanaa pitkä."
				score = min(10, max(0, len(user_answer.split()) / 5))  # Dummy-pistemäärä sanojen määrän perusteella
				
				exam_answer.gpt_evaluation = gpt_evaluation
				exam_answer.score = score
				exam_answer.save()
				
				results.append({
					'question_id': question_id,
					'question_text': question.question_text,
					'user_answer': user_answer,
					'evaluation': gpt_evaluation,
					'score': score
				})
				
			except ExamQuestion.DoesNotExist:
				results.append({
					'question_id': question_id,
					'error': 'Kysymystä ei löytynyt'
				})
		
		return JsonResponse({
			'success': True,
			'results': results
		})
	
	return JsonResponse({'success': False})


@require_POST
def ai_evaluate_exam_answer(request):
    """API endpoint for AI evaluation of a single exam answer."""
    import uuid
    from django.utils import timezone
    from .models import ExamQuestion, ExamAnswer
    from .ai_evaluator import evaluate_exam_answer

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Virheellinen pyyntö.'}, status=400)

    question_id = data.get('question_id')
    user_answer = data.get('answer', '').strip()
    self_score = data.get('self_score')

    if not question_id or not user_answer:
        return JsonResponse({'error': 'Kysymys ja vastaus vaaditaan.'}, status=400)

    if len(user_answer) < 10:
        return JsonResponse({'error': 'Vastaus on liian lyhyt arvioitavaksi.'}, status=400)

    try:
        question = ExamQuestion.objects.get(id=question_id)
    except ExamQuestion.DoesNotExist:
        return JsonResponse({'error': 'Kysymystä ei löydy.'}, status=404)

    if not question.model_answer:
        return JsonResponse({'error': 'Tällä kysymyksellä ei ole mallivastausta.'}, status=400)

    user_id = request.user.id if request.user.is_authenticated else None

    result = evaluate_exam_answer(
        question_text=question.question_text,
        model_answer=question.model_answer,
        user_answer=user_answer,
        subject_area=question.subject_area,
        user_id=user_id,
    )

    if 'error' in result:
        status_code = 429 if result.get('rate_limited') else 500
        return JsonResponse({'error': result['error']}, status=status_code)

    # Save to database — use simulation session_id if provided
    sim_session = request.headers.get('X-Simulation-Session', '')
    answer_session_id = sim_session if sim_session else str(uuid.uuid4())
    ExamAnswer.objects.create(
        session_id=answer_session_id,
        question=question,
        user=request.user if request.user.is_authenticated else None,
        user_answer=user_answer,
        ai_score=result['score'],
        ai_feedback=result['feedback'],
        ai_strengths=result['strengths'],
        ai_weaknesses=result['weaknesses'],
        ai_suggestions=result['suggestions'],
        ai_evaluated_at=timezone.now(),
        self_score=self_score,
    )

    # Check for newly earned achievements
    new_achievements = []
    if request.user.is_authenticated:
        from progress.achievement_checker import check_achievements
        newly_earned = check_achievements(request.user)
        new_achievements = [
            {'name': a.name, 'icon': a.icon, 'xp_reward': a.xp_reward}
            for a in newly_earned
        ]

    response_data = {
        'success': True,
        'score': result['score'],
        'feedback': result['feedback'],
        'strengths': result['strengths'],
        'weaknesses': result['weaknesses'],
        'suggestions': result['suggestions'],
    }
    if new_achievements:
        response_data['new_achievements'] = new_achievements
    return JsonResponse(response_data)


@require_POST
def ai_tutor_chat(request):
    """Server-side AI tutor endpoint. Replaces direct client-side OpenAI calls."""
    import json as _json
    import openai

    try:
        data = _json.loads(request.body)
    except (_json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Virheellinen pyyntö'}, status=400)

    message = data.get('message', '').strip()
    history = data.get('history', [])
    epa_id = data.get('epa_id')

    if not message:
        return JsonResponse({'error': 'Tyhjä viesti'}, status=400)
    if len(message) > 1000:
        return JsonResponse({'error': 'Viesti liian pitkä (max 1000 merkkiä)'}, status=400)

    system_prompt = (
        "Olet asiantunteva AI-tutori, joka auttaa sairaalafyysikon erikoistumiskoulutuksen opiskelijoita. "
        "Erikoisalueesi: Radiologia, Sädehoito, Isotooppilääketiede, Kliininen neurofysiologia, Kliininen fysiologia. "
        "Vastaa aina suomeksi. Ole tarkka, käytännönläheinen ja pedagoginen. "
        "Viittaa tarvittaessa relevantteihin standardeihin (IAEA, STUK, AAPM, ICRU, IEC, Khan). "
        "Jos kysymys ei liity sairaalafysiikkaan, ohjaa opiskelija ystävällisesti takaisin aiheeseen."
    )

    if epa_id:
        from sisalto.models import EPA, Section
        try:
            epa = EPA.objects.get(id=int(epa_id))
            sections = Section.objects.filter(epa=epa).exclude(content='').order_by('order')
            context_parts = [f"EPA-kortti: {epa.title}"]
            total_len = 0
            for s in sections:
                snippet = s.content[:400]
                context_parts.append(f"[{s.title}]: {snippet}")
                total_len += len(snippet)
                if total_len > 3000:
                    break
            system_prompt += "\n\nKonteksti — opiskelija tutkii tätä EPA-korttia:\n" + "\n".join(context_parts)
        except (EPA.DoesNotExist, ValueError, TypeError):
            pass

    trimmed_history = history[-20:] if len(history) > 20 else history
    # Validate history entries to prevent injection
    safe_history = [
        {'role': h['role'], 'content': str(h['content'])[:2000]}
        for h in trimmed_history
        if isinstance(h, dict) and h.get('role') in ('user', 'assistant') and h.get('content')
    ]

    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(safe_history)
    messages.append({'role': 'user', 'content': message})

    import os
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return JsonResponse({'error': 'AI-tutori ei ole käytettävissä tällä hetkellä'}, status=503)

    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'error': 'AI-virhe, yritä uudelleen'}, status=500)


def epas_view(request):
	"""Main EPAs overview page"""
	from sisalto.models import Specialty
	valid_names = ['Radiologia', 'Sädehoito', 'Isotooppilääketiede', 'KNF', 'Fysiologia']
	specialties = Specialty.objects.filter(name__in=valid_names).prefetch_related('epas')
	return render(request, 'sisalto/epas.html', {
		'page_title': 'EPA:t',
		'specialties': specialties
	})

# =============================================================================
# EPA LISTING VIEWS BY SPECIALTY
# =============================================================================

def radiologia_epas_view(request):
	"""List all Radiologia EPAs"""
	specialty = Specialty.objects.filter(name="Radiologia").first()
	epas = EPA.objects.filter(specialty=specialty) if specialty else []
	return render(request, 'sisalto/radiologia_epas.html', {'page_title': 'Radiologia EPA:t', 'epas': epas})

def sadehoito_epas_view(request):
	"""List all Sadehoito EPAs"""
	specialty = Specialty.objects.filter(name="Sädehoito").first()
	epas = EPA.objects.filter(specialty=specialty) if specialty else []
	return render(request, 'sisalto/sadehoito_epas.html', {'page_title': 'Sädehoito EPA:t', 'epas': epas})

def isotooppi_epas_view(request):
	"""List all Isotooppi EPAs"""
	specialty = Specialty.objects.filter(name="Isotooppilääketiede").first()
	epas = EPA.objects.filter(specialty=specialty) if specialty else []
	return render(request, 'sisalto/isotooppi_epas.html', {'page_title': 'Isotooppilääketiede EPA:t', 'epas': epas})

def knf_epas_view(request):
	"""List all KNF EPAs"""
	specialty = Specialty.objects.filter(name="KNF").first()
	epas = EPA.objects.filter(specialty=specialty) if specialty else []
	return render(request, 'sisalto/knf_epas.html', {'page_title': 'KNF EPA:t', 'epas': epas})

def fysiologia_epas_view(request):
	"""List all Fysiologia EPAs"""
	specialty = Specialty.objects.filter(name="Fysiologia").first()
	epas = EPA.objects.filter(specialty=specialty) if specialty else []
	return render(request, 'sisalto/fysiologia_epas.html', {'page_title': 'Fysiologia EPA:t', 'epas': epas})

# =============================================================================
# RADIOLOGIA VIEWS
# =============================================================================

def radiologia_subpages_view(request):
	"""Radiologia overview page with links to sub-specialties"""
	return render(request, 'sisalto/radiologia/radiologia_subpages.html', {'page_title': 'Radiologian alisivut'})

def radiologia_lapivalaisu_angiografia_view(request):
	"""Läpivalaisu ja angiografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Läpivalaisu ja angiografia (ml kardiologia)")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_lapivalaisu_angiografia.html', {
		'page_title': 'Läpivalaisu ja angiografia (ml kardiologia)',
		'epa': epa,
		'sections': sections
	})

def radiologia_magneettikuvaus_view(request):
	"""Magneettikuvaus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Magneettikuvaus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_magneettikuvaus.html', {
		'page_title': 'Magneettikuvaus',
		'epa': epa,
		'sections': sections
	})

def radiologia_mammografia_view(request):
	"""Mammografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Mammografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_mammografia.html', {
		'page_title': 'Mammografia',
		'epa': epa,
		'sections': sections
	})

def radiologia_natiivikuvantaminen_view(request):
	"""Natiivikuvantaminen EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Natiivikuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_natiivikuvantaminen.html', {
		'page_title': 'Natiivikuvantaminen',
		'epa': epa,
		'sections': sections
	})

def radiologia_tietokonetomografia_view(request):
	"""Tietokonetomografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Tietokonetomografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_tietokonetomografia.html', {
		'page_title': 'Tietokonetomografia',
		'epa': epa,
		'sections': sections
	})

def radiologia_ultraaani_view(request):
	"""Ultraääni EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ultraääni")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_ultraaani.html', {
		'page_title': 'Ultraääni',
		'epa': epa,
		'sections': sections
	})

def radiologia_kuvankatselunaytot_view(request):
	"""Kuvankatselunäytöt EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvankatselunäytöt")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_kuvankatselunaytot.html', {
		'page_title': 'Kuvankatselunäytöt',
		'epa': epa,
		'sections': sections
	})

def radiologia_hammaskuvantaminen_view(request):
	"""Hammaskuvantaminen EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Hammaskuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_hammaskuvantaminen.html', {
		'page_title': 'Hammaskuvantaminen',
		'epa': epa,
		'sections': sections
	})

def radiologia_sateilybiologia_suojelu_view(request):
	"""Säteilybiologia ja säteilysuojelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja säteilysuojelu radiologiassa")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia/radiologia_sateilybiologia_suojelu.html', {
		'page_title': 'Säteilybiologia ja säteilysuojelu radiologiassa',
		'epa': epa,
		'sections': sections
	})

# =============================================================================
# SADEHOITO VIEWS
# =============================================================================

def sadehoito_peruskasitteet_view(request):
	"""Sädehoidon peruskäsitteet EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Peruskäsitteet")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_peruskasitteet.html', {
		'page_title': 'Sädehoidon peruskäsitteet',
		'epa': epa,
		'sections': sections
	})

def sadehoito_kuvantaminen_suunnittelu_view(request):
	"""Kuvantaminen ja suunnittelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvantaminen ja suunnittelu")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_kuvantaminen_suunnittelu.html', {
		'page_title': 'Kuvantaminen sädehoidon suunnittelua varten',
		'epa': epa,
		'sections': sections
	})

def sadehoito_ulkoinen_view(request):
	"""Ulkoinen sädehoito EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ulkoinen sädehoito")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_ulkoinen.html', {
		'page_title': 'Ulkoinen sädehoito',
		'epa': epa,
		'sections': sections
	})

def sadehoito_sisainen_view(request):
	"""Sisäinen sädehoito EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sisäinen sädehoito")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_sisainen.html', {
		'page_title': 'Sisäinen sädehoito',
		'epa': epa,
		'sections': sections
	})

def sadehoito_dosimetria_view(request):
	"""Sädehoidon dosimetria EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Dosimetria")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_dosimetria.html', {
		'page_title': 'Sädehoidon dosimetria',
		'epa': epa,
		'sections': sections
	})

def sadehoito_laitteet_view(request):
	"""Säteilyä tuottavat laitteet EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laitteet")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_laitteet.html', {
		'page_title': 'Säteilyä tuottavat laitteet sädehoidossa',
		'epa': epa,
		'sections': sections
	})

def sadehoito_sateilybiologia_view(request):
	"""Säteilybiologia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito/sadehoito_sateilybiologia.html', {
		'page_title': 'Säteilybiologia ja säteily­suojelu sädehoidossa',
		'epa': epa,
		'sections': sections
	})

# =============================================================================
# ISOTOOPPI VIEWS  
# =============================================================================

def isotooppi_gammakamera_view(request):
	"""Gammakamerateknologia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Gammakamera")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_gammakamera.html', {
		'page_title': 'Gammakamerateknologia',
		'epa': epa,
		'sections': sections
	})

def isotooppi_pet_kamera_view(request):
	"""PET-kamerateknologia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-kamera")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_petkamera.html', {
		'page_title': 'PET-kamerateknologia',
		'epa': epa,
		'sections': sections
	})

def isotooppi_annostelu_radiofarmasia_view(request):
	"""Annostelu ja radiofarmasia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Annostelu ja radiofarmasia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	
	return render(request, 'sisalto/isotooppi/isotooppi_annostelu_radiofarmasia.html', {
		'page_title': 'Isotooppi: Annostelu ja radiofarmasia',
		'epa': epa,
		'sections': sections
	})

def isotooppi_gammakuvaus_spet_view(request):
	"""Gammakuvaus ja SPET EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Gammakuvaus ja SPET")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_gammakuvaus_spet.html', {
		'page_title': 'Gammakuvaus ja SPET-tutkimukset',
		'epa': epa,
		'sections': sections
	})

def isotooppi_pet_tutkimukset_view(request):
	"""PET-tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_pet_tutkimukset.html', {
		'page_title': 'PET-tutkimukset',
		'epa': epa,
		'sections': sections
	})

def isotooppi_radionuklidihoidot_view(request):
	"""Radionuklidihoidot EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Radionuklidihoidot")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_radionuklidihoidot.html', {
		'page_title': 'Radionuklidihoidot',
		'epa': epa,
		'sections': sections
	})

def isotooppi_sateilybiologia_suojelu_view(request):
	"""Säteilybiologia ja suojelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja suojelu")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi/isotooppi_sateilybiologia_suojelu.html', {
		'page_title': 'Säteilybiologia ja säteily­suojelu isotooppitoiminnassa',
		'epa': epa,
		'sections': sections
	})

# =============================================================================
# KNF VIEWS
# =============================================================================

def knf_eeg_view(request):
	"""EEG EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="EEG")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_eeg.html', {'epa': epa, 'sections': sections})

def knf_heratepotentiaali_enmg_view(request):
	"""Herätepotentiaali ja ENMG EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Herätepotentiaali ja ENMG-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_heratepotentiaali_enmg.html', {'epa': epa, 'sections': sections})

def knf_iom_view(request):
	"""IOM EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="IOM")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_iom.html', {'epa': epa, 'sections': sections})

def knf_laite_sahkoturvallisuus_view(request):
	"""Laite- ja sähköturvallisuus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laite- ja sähköturvallisuus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_laite_sahkoturvallisuus.html', {'epa': epa, 'sections': sections})

def knf_sarja_tms_hoidot_view(request):
	"""Sarja-TMS-hoidot EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sarja-TMS-hoidot ja navigoidut TMS-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_sarja_tms_hoidot.html', {'epa': epa, 'sections': sections})

def knf_uni_view(request):
	"""Uni EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Uni")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf/knf_uni.html', {'epa': epa, 'sections': sections})

# =============================================================================
# FYSIOLOGIA VIEWS
# =============================================================================

def fysiologia_ekg_view(request):
	"""EKG-tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="EKG-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia/fysiologia_ekg.html', {'epa': epa, 'sections': sections})

def fysiologia_gi_kanava_view(request):
	"""GI-kanavan tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="GI-kanavan tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia/fysiologia_gi_kanava.html', {'epa': epa, 'sections': sections})

def fysiologia_keuhkofunktio_view(request):
	"""Keuhkofunktiotutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Keuhkofunktiotutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia/fysiologia_keuhkofunktio.html', {'epa': epa, 'sections': sections})

def fysiologia_luuston_mineraali_view(request):
	"""Luuston mineraalitiheyden mittaus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Luuston mineraalitiheyden mittaus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia/fysiologia_luuston_mineraali.html', {'epa': epa, 'sections': sections})

def fysiologia_verenkierto_view(request):
	"""Verenkiertotutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Verenkiertotutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia/fysiologia_verenkierto.html', {'epa': epa, 'sections': sections})


# =============================================================================
# Helper functions
# =============================================================================
@csrf_exempt
def add_section_view(request):
	"""Add new section to EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_section_view(request):
	"""Edit existing section EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_section_view(request):
	"""Delete section EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})


@csrf_exempt
def update_proficiency_view(request):
	"""Update proficiency level for section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})
# =============================================================================
# RADIOLOGIA SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Lapivalaisu-angiografia section endpoints
@csrf_exempt
def add_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Add new section to Radiologia Läpivalaisu ja angiografia EPA"""
	return add_section_view(request)
	

@csrf_exempt
def edit_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Edit existing section in Radiologia Läpivalaisu ja angiografia EPA"""
	return edit_section_view(request)
	

@csrf_exempt
def delete_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Delete section from Radiologia Läpivalaisu ja angiografia EPA"""
	return delete_section_view(request)


@csrf_exempt
def update_radiologia_lapivalaisu_angiografia_proficiency_view(request):
	"""Update proficiency level for Läpivalaisu ja angiografia section"""
	return update_proficiency_view(request)


# Magneettikuvaus section endpoints
@csrf_exempt
def add_magneettikuvaus_section_view(request):
	"""Add new section to Magneettikuvaus EPA"""
	return add_section_view(request)
	

@csrf_exempt
def edit_magneettikuvaus_section_view(request):
	"""Edit existing section in Magneettikuvaus EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_magneettikuvaus_section_view(request):
	"""Delete section from Radiologia Magneettikuvaus EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_magneettikuvaus_proficiency_view(request):
	"""Update proficiency level for Magneettikuvaus section"""
	return update_proficiency_view(request)


# Mammografia section endpoints
@csrf_exempt
def add_mammografia_section_view(request):
	"""Add new section to Mammografia EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_mammografia_section_view(request):
	"""Edit existing section in Mammografia EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_mammografia_section_view(request):
	"""Delete section from Mammografia EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_mammografia_proficiency_view(request):
	"""Update proficiency level for Mammografia section"""
	return update_proficiency_view(request)

# Natiivikuvantaminen section endpoints
@csrf_exempt
def add_natiivikuvantaminen_section_view(request):
	"""Add new section to Natiivikuvantaminen EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_natiivikuvantaminen_section_view(request):
	"""Edit existing section in Natiivikuvantaminen EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_natiivikuvantaminen_section_view(request):
	"""Delete section from Natiivikuvantaminen EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_natiivikuvantaminen_proficiency_view(request):
	"""Update proficiency level for Natiivikuvantaminen section"""
	return update_proficiency_view(request)


# Tietokonetomografia section endpoints
@csrf_exempt
def add_tietokonetomografia_section_view(request):
	"""Add new section to Tietokonetomografia EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_tietokonetomografia_section_view(request):
	"""Edit existing section in Tietokonetomografia EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_tietokonetomografia_section_view(request):
	"""Delete section from Tietokonetomografia EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_tietokonetomografia_proficiency_view(request):
	"""Update proficiency level for Tietokonetomografia section"""
	return update_proficiency_view(request)

# Ultraaani section endpoints
@csrf_exempt
def add_ultraaani_section_view(request):
	"""Add new section to Ultraaani EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_ultraaani_section_view(request):
	"""Edit existing section in Ultraaani EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_ultraaani_section_view(request):
	"""Delete section from Ultraaani EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_ultraaani_proficiency_view(request):
	"""Update proficiency level for Ultraaani section"""
	return update_proficiency_view(request)

# Kuvankatselunaytot section endpoints
@csrf_exempt
def add_kuvankatselunaytot_section_view(request):
	"""Add new section to Kuvankatselunaytot EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_kuvankatselunaytot_section_view(request):
	"""Edit existing section in Kuvankatselunaytot EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_kuvankatselunaytot_section_view(request):
	"""Delete section from Kuvankatselunaytot EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_kuvankatselunaytot_proficiency_view(request):
	"""Update proficiency level for Kuvankatselunaytot section"""
	return update_proficiency_view(request)

# Hammaskuvantaminen section endpoints
@csrf_exempt
def add_hammaskuvantaminen_section_view(request):
	"""Add new section to Hammaskuvantaminen EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_hammaskuvantaminen_section_view(request):
	"""Edit existing section in Hammaskuvantaminen EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_hammaskuvantaminen_section_view(request):
	"""Delete section from Hammaskuvantaminen EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_hammaskuvantaminen_proficiency_view(request):
	"""Update proficiency level for Hammaskuvantaminen section"""
	return update_proficiency_view(request)

# Radiologia Sateilybiologia-suojelu section endpoints  
@csrf_exempt
def add_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Add new section to Sateilybiologia-suojelu EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Sateilybiologia-suojelu EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Sateilybiologia-suojelu EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_radiologia_sateilybiologia_suojelu_proficiency_view(request):
	"""Update proficiency level for Sateilybiologia-suojelu section"""
	return update_proficiency_view(request)


# =============================================================================
# SADEHOITO SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Peruskäsitteet section endpoints
@csrf_exempt
def add_sadehoito_peruskasitteet_section_view(request):
	"""Add new section to Sädehoidon peruskäsitteet EPA"""
	return add_section_view(request)


@csrf_exempt
def edit_sadehoito_peruskasitteet_section_view(request):
	"""Edit existing section in Sädehoidon peruskäsitteet EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_peruskasitteet_section_view(request):
	"""Delete section from Sädehoidon peruskäsitteet EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_peruskasitteet_proficiency_view(request):
	"""Update proficiency level for Sädehoidon peruskäsitteet section"""
	return update_proficiency_view(request)

# Kuvantaminen ja suunnittelu section endpoints
@csrf_exempt
def add_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Add new section to Kuvantaminen ja suunnittelu EPA"""
	return add_section_view(request)


@csrf_exempt
def edit_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Edit existing section in Kuvantaminen ja suunnittelu EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Delete section from Kuvantaminen ja suunnittelu EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_kuvantaminen_suunnittelu_proficiency_view(request):
	"""Update proficiency level for Kuvantaminen ja suunnittelu section"""
	return update_proficiency_view(request)

# Ulkoinen sädehoito section endpoints
@csrf_exempt
def add_sadehoito_ulkoinen_section_view(request):
	"""Add new section to Ulkoinen EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_sadehoito_ulkoinen_section_view(request):
	"""Edit existing section in Ulkoinen EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_ulkoinen_section_view(request):
	"""Delete section from Ulkoinen EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_ulkoinen_proficiency_view(request):
	"""Update proficiency level for Ulkoinen section"""
	return update_proficiency_view(request)

# Sisäinen sädehoito section endpoints
@csrf_exempt
def add_sadehoito_sisainen_section_view(request):
	"""Add new section to Sisäinen sädehoito EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_sadehoito_sisainen_section_view(request):
	"""Edit existing section in Sisäinen sädehoito EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_sisainen_section_view(request):
	"""Delete section from Sisäinen sädehoito EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_sisainen_proficiency_view(request):
	"""Update proficiency level for Sisäinen sädehoito section"""
	return update_proficiency_view(request)

# Dosimetria section endpoints
@csrf_exempt
def add_sadehoito_dosimetria_section_view(request):
	"""Add new section to Dosimetria EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_sadehoito_dosimetria_section_view(request):
	"""Edit existing section in Dosimetria EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_dosimetria_section_view(request):
	"""Delete section from Dosimetria EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_dosimetria_proficiency_view(request):
	"""Update proficiency level for Dosimetria section"""
	return update_proficiency_view(request)

# Laitteet section endpoints
@csrf_exempt
def add_sadehoito_laitteet_section_view(request):
	"""Add new section to Laitteet EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_sadehoito_laitteet_section_view(request):
	"""Edit existing section in Laitteet EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_laitteet_section_view(request):
	"""Delete section from Laitteet EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_laitteet_proficiency_view(request):
	"""Update proficiency level for Laitteet section"""
	return update_proficiency_view(request)

# Säteilybiologia section endpoints
@csrf_exempt
def add_sadehoito_sateilybiologia_section_view(request):
	"""Add new section to Säteilybiologia EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_sadehoito_sateilybiologia_section_view(request):
	"""Edit existing section in Säteilybiologia EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_sadehoito_sateilybiologia_section_view(request):
	"""Delete section from Säteilybiologia EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_sadehoito_sateilybiologia_proficiency_view(request):
	"""Update proficiency level for Säteilybiologia section"""
	return update_proficiency_view(request)


# =============================================================================
# ISOTOOPPI SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Gammakamera section endpoints
@csrf_exempt
def add_isotooppi_gammakamera_section_view(request):
	"""Add new section to Gammakamera EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_gammakamera_section_view(request):
	"""Edit existing section in Gammakamera EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_gammakamera_section_view(request):
	"""Delete section from Gammakamera EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_gammakamera_proficiency_view(request):
	"""Update proficiency level for Gammakamera section"""
	return update_proficiency_view(request)

# PET-kamera section endpoints
@csrf_exempt
def add_isotooppi_pet_kamera_section_view(request):
	"""Add new section to PET-kamera EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_pet_kamera_section_view(request):
	"""Edit existing section in PET-kamera EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_pet_kamera_section_view(request):
	"""Delete section from PET-kamera EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_pet_kamera_proficiency_view(request):
	"""Update proficiency level for PET-kamera section"""
	return update_proficiency_view(request)

# Annostelu ja radiofarmasia section endpoints
@csrf_exempt
def add_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Add new section to Annostelu ja radiofarmasia EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Edit existing section in Annostelu ja radiofarmasia EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Delete section from Annostelu ja radiofarmasia EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_annostelu_radiofarmasia_proficiency_view(request):
	"""Update proficiency level for Annostelu ja radiofarmasia section"""
	return update_proficiency_view(request)

# Gammakuvaus ja SPET section endpoints
@csrf_exempt
def add_isotooppi_gammakuvaus_spet_section_view(request):
	"""Add new section to Gammakuvaus ja SPET EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_gammakuvaus_spet_section_view(request):
	"""Edit existing section in Gammakuvaus ja SPET EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_gammakuvaus_spet_section_view(request):
	"""Delete section from Gammakuvaus ja SPET EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_gammakuvaus_spet_proficiency_view(request):
	"""Update proficiency level for Gammakuvaus ja SPET section"""
	return update_proficiency_view(request)

# PET-tutkimukset section endpoints
@csrf_exempt
def add_isotooppi_pet_tutkimukset_section_view(request):
	"""Add new section to PET-tutkimukset EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_pet_tutkimukset_section_view(request):
	"""Edit existing section in PET-tutkimukset EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_pet_tutkimukset_section_view(request):
	"""Delete section from PET-tutkimukset EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_pet_tutkimukset_proficiency_view(request):
	"""Update proficiency level for PET-tutkimukset section"""
	return update_proficiency_view(request)

# Radionuklidihoidot section endpoints
@csrf_exempt
def add_isotooppi_radionuklidihoidot_section_view(request):
	"""Add new section to Radionuklidihoidot EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_radionuklidihoidot_section_view(request):
	"""Edit existing section in Radionuklidihoidot EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_radionuklidihoidot_section_view(request):
	"""Delete section from Radionuklidihoidot EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_radionuklidihoidot_proficiency_view(request):
	"""Update proficiency level for Radionuklidihoidot section"""
	return update_proficiency_view(request)

# Säteilybiologia ja suojelu section endpoints
@csrf_exempt
def add_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Add new section to Säteilybiologia ja suojelu EPA"""
	return add_section_view(request)

@csrf_exempt
def edit_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Säteilybiologia ja suojelu EPA"""
	return edit_section_view(request)

@csrf_exempt
def delete_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Säteilybiologia ja suojelu EPA"""
	return delete_section_view(request)

@csrf_exempt
def update_isotooppi_sateilybiologia_suojelu_proficiency_view(request):
	"""Update proficiency level for Säteilybiologia ja suojelu section"""
	return update_proficiency_view(request)

# =============================================================================
# KNF SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# EEG section endpoints
@csrf_exempt
def add_knf_eeg_section_view(request):
	"""Add new section to KNF EEG"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_eeg_section_view(request):
	"""Edit existing section in KNF EEG"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_eeg_section_view(request):
	"""Delete section from KNF EEG"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_eeg_proficiency_view(request):
	"""Update proficiency level for EEG section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

#Herätepotentiaali ja ENMG section endpoints
@csrf_exempt
def add_knf_heratepotentiaali_enmg_section_view(request):
	"""Add new section to Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_heratepotentiaali_enmg_section_view(request):
	"""Edit existing section in Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_heratepotentiaali_enmg_section_view(request):
	"""Delete section from Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_heratepotentiaali_enmg_proficiency_view(request):
	"""Update proficiency level for Herätepotentiaali ja ENMG section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# IOM section endpoints
@csrf_exempt
def add_knf_iom_section_view(request):
	"""Add new section to KNF IOM EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_iom_section_view(request):
	"""Edit existing section in KNF IOM EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_iom_section_view(request):
	"""Delete section from KNF IOM EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_iom_proficiency_view(request):
	"""Update proficiency level for IOM section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# Laite- ja sähköturvallisuus section endpoints
@csrf_exempt
def add_knf_laite_sahkoturvallisuus_section_view(request):
	"""Add new section to Laite- ja sähköturvallisuus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_laite_sahkoturvallisuus_section_view(request):
	"""Edit existing section in Laite- ja sähköturvallisuus EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_laite_sahkoturvallisuus_section_view(request):
	"""Delete section from Laite- ja sähköturvallisuus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_laite_sahkoturvallisuus_proficiency_view(request):
	"""Update proficiency level for Laite- ja sähköturvallisuus section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# Sarja-TMS-hoidot section endpoints
@csrf_exempt
def add_knf_sarja_tms_hoidot_section_view(request):
	"""Add new section to Sarja-TMS-hoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_sarja_tms_hoidot_section_view(request):
	"""Edit existing section in Sarja-TMS-hoidot EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_sarja_tms_hoidot_section_view(request):
	"""Delete section from Sarja-TMS-hoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_sarja_tms_hoidot_proficiency_view(request):
	"""Update proficiency level for Sarja-TMS-hoidot section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# Uni section endpoints
@csrf_exempt
def add_knf_uni_section_view(request):
	"""Add new section to Unitutkimukset EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_uni_section_view(request):
	"""Edit existing section in Unitutkimukset EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_uni_section_view(request):
	"""Delete section from Unitutkimukset EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_knf_uni_proficiency_view(request):
	"""Update proficiency level for Unitutkimukset section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# =============================================================================
# FYSIOLOGIA SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# EKG section endpoints
@csrf_exempt
def add_fysiologia_ekg_section_view(request):
	"""Add new section to EKG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_ekg_section_view(request):
	"""Edit existing section in EKG EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_ekg_section_view(request):
	"""Delete section from EKG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_fysiologia_ekg_proficiency_view(request):
	"""Update proficiency level for EKG section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# GI-kanava section endpoints
@csrf_exempt
def add_fysiologia_gi_kanava_section_view(request):
	"""Add new section to GI-kanava EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_gi_kanava_section_view(request):
	"""Edit existing section in GI-kanava EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_gi_kanava_section_view(request):
	"""Delete section from GI-kanava EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_fysiologia_gi_kanava_proficiency_view(request):
	"""Update proficiency level for GI-kanava section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

#Keuhkofunktio section endpoints
@csrf_exempt
def add_fysiologia_keuhkofunktio_section_view(request):
	"""Add new section to Keuhkofunktio EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_keuhkofunktio_section_view(request):
	"""Edit existing section in Keuhkofunktio EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_keuhkofunktio_section_view(request):
	"""Delete section from Keuhkofunktio EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_fysiologia_keuhkofunktio_proficiency_view(request):
	"""Update proficiency level for Keuhkofunktio section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# Luuston mineraalitiheys section endpoints
@csrf_exempt
def add_fysiologia_luuston_mineraali_section_view(request):
	"""Add new section to Luuston mineraalitiheys EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_luuston_mineraali_section_view(request):
	"""Edit existing section in Luuston mineraalitiheys EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_luuston_mineraali_section_view(request):
	"""Delete section from Luuston mineraalitiheys EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_fysiologia_luuston_mineraali_proficiency_view(request):
	"""Update proficiency level for Luuston mineraalitiheys section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# Verenkierto section endpoints
@csrf_exempt
def add_fysiologia_verenkierto_section_view(request):
	"""Add new section to Verenkierto EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		after_section_id = data.get("after_section_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_section_id:
					# Find the section after which to insert
					after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
					if after_section:
						# Update order of subsequent sections
						Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
						order = after_section.order + 1
					else:
						# If section not found, add to end
						last_section = Section.objects.filter(epa=epa).order_by('-order').first()
						order = (last_section.order + 1) if last_section else 1
				else:
					# No specific position, add to end
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					order=order,
					proficiency_level=proficiency_level
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_verenkierto_section_view(request):
	"""Edit existing section in Verenkierto EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except:
			# Fall back to POST data for new form-based requests
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			proficiency_level = request.POST.get("proficiency_level")
			action = request.POST.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# Handle proficiency level update specifically
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# Handle full section edit
				elif title:
					section.title = title
					section.content = content
					if proficiency_level:
						section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_verenkierto_section_view(request):
	"""Delete section from Verenkierto EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def update_fysiologia_verenkierto_proficiency_view(request):
	"""Update proficiency level for Verenkierto section"""
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			section_id = data.get("section_id")
			proficiency_level = data.get("proficiency_level")
			
			if section_id and proficiency_level:
				section = Section.objects.filter(id=section_id).first()
				if section:
					section.proficiency_level = int(proficiency_level)
					section.save()
					return JsonResponse({"success": True})
		except Exception as e:
			print(f"Proficiency update error: {e}")
	return JsonResponse({"success": False})

# =============================================================================
# RAPORTOI ONGELMASTA SIVU
# =============================================================================

def viitteet_view(request):
    """EPA-korttien viitteet -sivu."""
    return render(request, 'sisalto/viitteet.html')


def raportoi_ongelma_view(request):
    """
    Näyttää "Raportoi ongelmasta" -sivun joka käyttää base_summereditor.html pohjaa
    ja Summernote editoria muokkaukseen. Sisältää samaa section-toiminnallisuutta kuin EPA-sivut.
    """
    # Luodaan erityinen EPA "Raportoi ongelma" sisällölle
    specialty, _ = Specialty.objects.get_or_create(name="Yleiset")
    epa, created = EPA.objects.get_or_create(specialty=specialty, title="Raportoi ongelma")
    
    # Luodaan default-osiot jos EPA on uusi
    if created or not Section.objects.filter(epa=epa).exists():
        default_sections = [
            {
                'title': 'Yleistä tietoa raportoimisesta',
                'content': '''<p>Tämän sivun kautta voit raportoida sivustossa havaitsemistasi ongelmista, virheistä tai puutteista. Voit myös ehdottaa parannuksia sisältöön tai sivuston toiminnallisuuteen.</p>
<p><strong>Mitä voit raportoida:</strong></p>
<ul>
<li>Virheitä sisällössä (kirjoitusvirheet, väärät tiedot)</li>
<li>Teknisiä ongelmia (sivut eivät lataudu, linkit eivät toimi)</li>
<li>Puuttuvia tietoja tai osiota</li>
<li>Ehdotuksia sisällön parantamiseksi</li>
<li>Käytettävyysongelmia</li>
</ul>''',
                'order': 1
            },
            {
                'title': 'Tekniset ongelmat',
                'content': '''<p>Jos kohtaat teknisiä ongelmia sivuston käytössä, kerro meille:</p>
<ul>
<li>Mitä yritit tehdä?</li>
<li>Mitä tapahtui sen sijaan?</li>
<li>Mitä selainta käytät?</li>
<li>Millä laitteella (tietokone, tablet, puhelin)?</li>
</ul>
<p><strong>Esimerkki hyvästä raportista:</strong><br>
"Yritin ladata kuvaa Summernote-editorissa Radiologia &gt; Magneettikuvaus -sivulla, mutta kuva ei latautunut. Käytän Chrome-selainta Windows 10 -tietokoneella."</p>''',
                'order': 2
            },
            {
                'title': 'Sisältöön liittyvät raportit',
                'content': '''<p>Sisältöön liittyvät raportit voivat koskea:</p>
<ul>
<li><strong>Virheitä:</strong> Kirjoitusvirheet, väärät kaavat tai faktat</li>
<li><strong>Puutteita:</strong> Tärkeää tietoa puuttuu jostakin osiosta</li>
<li><strong>Vanhentuneita tietoja:</strong> Tiedot eivät ole ajan tasalla</li>
<li><strong>Epäselviä kohtia:</strong> Jotain on vaikea ymmärtää</li>
</ul>
<p>Kerro aina tarkkaan, mistä osiosta ja sivusta on kyse, jotta voimme korjata ongelmat nopeasti.</p>''',
                'order': 3
            },
            {
                'title': 'Yhteystiedot ja palautteen antaminen',
                'content': '''<p>Voit ottaa yhteyttä seuraavilla tavoilla:</p>
<ul>
<li><strong>Sähköposti:</strong> <a href="mailto:admin@example.com">admin@example.com</a></li>
<li><strong>GitHub Issues:</strong> <a href="#" target="_blank">Luo issue GitHubissa</a></li>
<li><strong>Suora palaute:</strong> Käytä sivuston AI-chat toimintoa</li>
</ul>
<p><strong>Kiitos avustasi!</strong> Jokainen raportti auttaa tekemään sivustosta paremman kaikille käyttäjille.</p>''',
                'order': 4
            }
        ]
        
        for section_data in default_sections:
            Section.objects.create(
                epa=epa,
                title=section_data['title'],
                content=section_data['content'],
                order=section_data['order']
            )
    
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    
    context = {
        'page_title': 'Raportoi ongelmasta - Sairaalafyysikon erikoistumiskirja',
        'page_description': 'Ilmoita sivuston toiminnassa havaitsemistasi ongelmista tai ehdota parannuksia.',
        'epa': epa,
        'sections': sections
    }
    return render(request, 'sisalto/raportoi_ongelma.html', context)

# =============================================================================
# IMAGE UPLOAD FOR CKEDITOR
# =============================================================================

@require_POST
@csrf_protect
def upload_image_view(request):
    """
    Universal image upload for both CKEditor 5 and Summernote
    - CKEditor 5 odottaa kenttää 'upload' ja vastausta { "url": "..." }
    - Summernote odottaa kenttää 'file' ja vastausta { "location": "..." }
    """
    # Try both field names
    f = request.FILES.get('upload') or request.FILES.get('file')
    
    if not f:
        return JsonResponse({ 'error': { 'message': 'No file sent.' } }, status=400)

    # Check file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    import os
    ext = os.path.splitext(f.name)[1].lower()
    
    if ext not in allowed_extensions:
        return JsonResponse({ 'error': { 'message': 'Invalid file type. Only images allowed.' } }, status=400)

    # Create unique name
    import uuid
    name = f"editor/{uuid.uuid4().hex}{ext}"
    
    try:
        saved_path = default_storage.save(name, ContentFile(f.read()))
        file_url = default_storage.url(saved_path)

        # Build absolute URL
        if file_url.startswith('/'):
            absolute_url = request.build_absolute_uri(file_url)
        else:
            absolute_url = file_url

        # Return response for both editors
        return JsonResponse({ 
            'url': absolute_url,      # For CKEditor 5
            'location': absolute_url  # For Summernote
        })
        
    except Exception as e:
        return JsonResponse({ 'error': { 'message': str(e) } }, status=500)


# =============================================================================
# THEORY IMAGE SLOTS API
# =============================================================================

@require_GET
def theory_images_list(request, modality: str):
    """Return all images for a modality as {slot_id: {url, caption, alt_text}}"""
    images = TheoryImage.objects.filter(modality=modality).exclude(image='')
    data = {}
    for img in images:
        if img.image:
            data[img.slot_id] = {
                'url': img.image.url,
                'caption': img.caption,
                'alt_text': img.alt_text,
                'tab_id': img.tab_id,
                'display_size': img.display_size,
            }
    return JsonResponse(data)


@require_POST
@csrf_protect
def theory_image_upload(request):
    """Upload or replace an image in a theory slot. Superuser only."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Ei oikeuksia.'}, status=403)

    modality = request.POST.get('modality', '').strip()
    tab_id = request.POST.get('tab_id', '').strip()
    slot_id = request.POST.get('slot_id', '').strip()
    caption = request.POST.get('caption', '').strip()
    alt_text = request.POST.get('alt_text', '').strip()
    display_size = request.POST.get('display_size', 'medium').strip()
    if display_size not in ('small', 'medium', 'large', 'full'):
        display_size = 'medium'
    image_file = request.FILES.get('image')

    if not all([modality, tab_id, slot_id]):
        return JsonResponse({'error': 'modality, tab_id ja slot_id vaaditaan.'}, status=400)

    obj, created = TheoryImage.objects.get_or_create(
        modality=modality, tab_id=tab_id, slot_id=slot_id,
        defaults={'caption': caption, 'alt_text': alt_text},
    )

    if image_file:
        import os, uuid
        allowed = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in allowed:
            return JsonResponse({'error': 'Sallitut tiedostotyypit: ' + ', '.join(allowed)}, status=400)
        # Delete old file if replacing
        if obj.image:
            try:
                default_storage.delete(obj.image.name)
            except Exception:
                pass
        filename = f"theory/{uuid.uuid4().hex}{ext}"
        saved = default_storage.save(filename, ContentFile(image_file.read()))
        obj.image = saved

    obj.caption = caption
    obj.alt_text = alt_text
    obj.display_size = display_size
    obj.save()

    return JsonResponse({
        'ok': True,
        'url': obj.image.url if obj.image else None,
        'caption': obj.caption,
        'alt_text': obj.alt_text,
        'display_size': obj.display_size,
        'slot_id': obj.slot_id,
    })


@require_POST
@csrf_protect
def theory_image_delete(request):
    """Delete an image from a theory slot. Superuser only."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Ei oikeuksia.'}, status=403)

    data = json.loads(request.body)
    modality = data.get('modality', '').strip()
    tab_id = data.get('tab_id', '').strip()
    slot_id = data.get('slot_id', '').strip()

    try:
        obj = TheoryImage.objects.get(modality=modality, tab_id=tab_id, slot_id=slot_id)
        if obj.image:
            try:
                default_storage.delete(obj.image.name)
            except Exception:
                pass
        obj.delete()
        return JsonResponse({'ok': True})
    except TheoryImage.DoesNotExist:
        return JsonResponse({'error': 'Kuvapaikkaa ei löydy.'}, status=404)


# =============================================================================
# THEORY CONTENT INLINE EDITING
# =============================================================================

@require_POST
def theory_content_save(request):
    """Save inline-edited theory content for a modality tab."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Ei oikeuksia.'}, status=403)
    try:
        data = json.loads(request.body)
        modality = data.get('modality', '').strip()
        tab_id = data.get('tab_id', '').strip()
        content = data.get('content', '')
        if not modality or not tab_id:
            return JsonResponse({'error': 'modality ja tab_id vaaditaan.'}, status=400)
        obj, created = TheoryContent.objects.update_or_create(
            modality=modality,
            tab_id=tab_id,
            defaults={'content': content, 'updated_by': request.user},
        )
        return JsonResponse({'success': True, 'created': created})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def theory_content_get(request, modality: str, tab_id: str):
    """Get saved theory content for a modality tab (or 404 if not saved yet)."""
    try:
        obj = TheoryContent.objects.get(modality=modality, tab_id=tab_id)
        return JsonResponse({'content': obj.content, 'updated_at': obj.updated_at.isoformat()})
    except TheoryContent.DoesNotExist:
        return JsonResponse({'error': 'Ei tallennettua sisältöä.'}, status=404)


# =============================================================================
# RAPORTOI ONGELMA SECTION MANAGEMENT
# =============================================================================

@csrf_exempt
def edit_raportoi_ongelma_section_view(request):
	"""Edit section in Raportoi ongelma page"""
	if request.method == "POST":
		try:
			section_id = request.POST.get("section_id")
			title = request.POST.get("title", "").strip()
			content = request.POST.get("content", "")
			
			if not title:
				return JsonResponse({"success": False, "error": "Otsikko vaaditaan"})
			
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.title = title
				section.content = content
				section.save()
				return JsonResponse({"success": True})
			else:
				return JsonResponse({"success": False, "error": "Osiota ei löytynyt"})
				
		except Exception as e:
			return JsonResponse({"success": False, "error": str(e)})
	
	return JsonResponse({"success": False, "error": "Virheellinen pyyntö"})


# =============================================================================
# TEXT-TO-SPEECH API (OpenAI TTS)
# =============================================================================

@require_POST
@csrf_protect
def tts_generate(request):
    """Generate Finnish TTS audio using OpenAI TTS API.
    Accepts JSON: {text: "..."}
    Returns: audio/mpeg MP3 stream.
    Uses file-based cache to avoid re-generating identical chunks.
    """
    import hashlib, os
    from django.conf import settings

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Virheellinen JSON'}, status=400)

    text = (data.get('text') or '').strip()
    if not text:
        return JsonResponse({'error': 'Teksti puuttuu'}, status=400)
    if len(text) > 4096:
        text = text[:4096]

    allowed_voices = {'echo', 'fable', 'onyx', 'nova', 'shimmer'}
    voice = data.get('voice', 'nova')
    if voice not in allowed_voices:
        voice = 'nova'

    # File-based cache — key includes voice so each voice is cached separately
    cache_dir = os.path.join(settings.BASE_DIR, 'media', 'tts_cache')
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:24]
    cache_path = os.path.join(cache_dir, f'{text_hash}_{voice}.mp3')

    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='audio/mpeg')

    # Generate via OpenAI
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        print('[TTS] ERROR: OPENAI_API_KEY not found in environment')
        return JsonResponse({'error': 'OPENAI_API_KEY ei ole asetettu.'}, status=500)
    print(f'[TTS] Generating audio for {len(text)} chars, api_key starts with {api_key[:8]}...')

    try:
        import openai
        import traceback
        client = openai.OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model='tts-1',
            voice=voice,
            input=text,
            response_format='mp3',
        )
        audio_bytes = response.content

        # Cache to disk
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_path, 'wb') as f:
            f.write(audio_bytes)

        return HttpResponse(audio_bytes, content_type='audio/mpeg')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'TTS-virhe: {str(e)}'}, status=500)


def service_worker_js(request):
    """Serve service worker at root scope /sw.js with no-cache headers."""
    from django.template.loader import render_to_string
    content = render_to_string('sisalto/sw.js', {}, request=request)
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def offline_page(request):
    """Offline fallback page served by service worker."""
    return render(request, 'sisalto/offline.html')