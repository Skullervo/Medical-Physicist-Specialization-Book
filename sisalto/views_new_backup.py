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
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Max
from django.shortcuts import render, get_object_or_404
from .models import Section, EPA, Specialty
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# =============================================================================
# GENERAL PAGE VIEWS
# =============================================================================

def frontpage_view(request):
	"""Main landing page view"""
	try:
		from .models import FrontPage, Specialty
		page = FrontPage.objects.first()
		specialties = Specialty.objects.all()
	except:
		page = None
		specialties = []
	# Use new template for testing
	return render(request, 'sisalto/frontpage_new.html', {'page': page, 'specialties': specialties})

def specialty_list_view(request):
	"""List all medical specialties"""
	specialties = Specialty.objects.all()
	return render(request, 'sisalto/specialty_list.html', {'specialties': specialties})

def specialty_detail_view(request, specialty_id):
	"""Show details for a specific specialty"""
	specialty = get_object_or_404(Specialty, id=specialty_id)
	return render(request, 'sisalto/specialty_detail.html', {'specialty': specialty})

def epa_detail_view(request, epa_id):
	"""Show details for a specific EPA"""
	epa = get_object_or_404(EPA, id=epa_id)
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/epa_detail.html', {'epa': epa, 'sections': sections})

def examquestion_list_view(request):
	"""List exam questions"""
	try:
		from .models import ExamQuestion
		questions = ExamQuestion.objects.all().order_by('-year', 'exam_date', 'question_number')
		
		# Lisätään tilastotietoja
		subject_areas = ExamQuestion.objects.values_list('subject_area', flat=True).distinct()
		years_range = ExamQuestion.objects.values_list('year', flat=True).distinct().order_by('year')
		years_range = [year for year in years_range if year is not None]
		
		context = {
			'questions': questions,
			'subject_areas_count': len(subject_areas),
			'years_range': f"{min(years_range)}-{max(years_range)}" if years_range else "N/A"
		}
	except:
		context = {
			'questions': [],
			'subject_areas_count': 0,
			'years_range': "N/A"
		}
	return render(request, 'sisalto/examquestion_list.html', context)

def table_questions_view(request):
	"""Modern table view for exam questions"""
	try:
		from .models import ExamQuestion
		questions = ExamQuestion.objects.all().order_by('-year', 'exam_date', 'question_number')
	except:
		questions = []
	
	return render(request, 'sisalto/table_questions.html', {'questions': questions})

def exam_practice_view(request):
	"""Tenttikysymysten harjoittelusivu"""
	from .models import ExamQuestion
	
	# Haetaan kaikki vuodet dropdown-valikkoa varten
	years = ExamQuestion.objects.values_list('year', flat=True).distinct().order_by('-year')
	years = [year for year in years if year is not None]
	
	context = {
		'page_title': 'Tenttikysymysten harjoittelu',
		'years': years
	}
	return render(request, 'sisalto/exam_practice.html', context)

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

def epas_view(request):
	"""Main EPAs overview page"""
	return render(request, 'sisalto/epas.html', {'page_title': 'EPA:t'})

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
		'page_title': 'Annostelu ja radiofarmasiatoiminta',
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
	# if request.method == "POST":
	# 	data = json.loads(request.body)
	# 	title = data.get("title")
	# 	content = data.get("content")
	# 	epa_id = data.get("epa_id")
	# 	proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
	# 	after_section_id = data.get("after_section_id")
		
	# 	if title and epa_id:
	# 		epa = EPA.objects.filter(id=epa_id).first()
	# 		if epa:
	# 			if after_section_id:
	# 				# Find the section after which to insert
	# 				after_section = Section.objects.filter(id=after_section_id, epa=epa).first()
	# 				if after_section:
	# 					# Update order of subsequent sections
	# 					Section.objects.filter(epa=epa, order__gt=after_section.order).update(order=F('order') + 1)
	# 					order = after_section.order + 1
	# 				else:
	# 					# If section not found, add to end
	# 					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
	# 					order = (last_section.order + 1) if last_section else 1
	# 			else:
	# 				# No specific position, add to end
	# 				last_section = Section.objects.filter(epa=epa).order_by('-order').first()
	# 				order = (last_section.order + 1) if last_section else 1
				
	# 			Section.objects.create(
	# 				epa=epa, 
	# 				title=title, 
	# 				content=content, 
	# 				order=order,
	# 				proficiency_level=proficiency_level
	# 			)
	# 			return JsonResponse({"success": True})
	# return JsonResponse({"success": False})

@csrf_exempt
def edit_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Edit existing section in Radiologia Läpivalaisu ja angiografia EPA"""
	return edit_section_view(request)
	# if request.method == "POST":
	# 	try:
	# 		# Try JSON first for compatibility with old code
	# 		data = json.loads(request.body)
	# 		section_id = data.get("section_id")
	# 		title = data.get("title")
	# 		content = data.get("content")
	# 		proficiency_level = data.get("proficiency_level")
	# 		action = data.get("action")
	# 	except:
	# 		# Fall back to POST data for new form-based requests
	# 		section_id = request.POST.get("section_id")
	# 		title = request.POST.get("title", "").strip()
	# 		content = request.POST.get("content", "")
	# 		proficiency_level = request.POST.get("proficiency_level")
	# 		action = request.POST.get("action")
		
	# 	if section_id:
	# 		section = Section.objects.filter(id=section_id).first()
	# 		if section:
	# 			# Handle proficiency level update specifically
	# 			if action == 'update_proficiency' and proficiency_level:
	# 				section.proficiency_level = proficiency_level
	# 				section.save()
	# 				return JsonResponse({"success": True})
	# 			# Handle full section edit
	# 			elif title:
	# 				section.title = title
	# 				section.content = content
	# 				if proficiency_level:
	# 					section.proficiency_level = proficiency_level
	# 				section.save()
	# 				return JsonResponse({"success": True})
	# return JsonResponse({"success": False})

@csrf_exempt
def delete_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Delete section from Radiologia Läpivalaisu ja angiografia EPA"""
	return delete_section_view(request)
	# if request.method == "POST":
	# 	data = json.loads(request.body)
	# 	section_id = data.get("section_id")
		
	# 	if section_id:
	# 		section = Section.objects.filter(id=section_id).first()
	# 		if section:
	# 			section.delete()
	# 			return JsonResponse({"success": True})
	# return JsonResponse({"success": False})


@csrf_exempt
def update_radiologia_lapivalaisu_angiografia_proficiency_view(request):
	"""Update proficiency level for Läpivalaisu ja angiografia section"""
	return update_proficiency_view(request)
	# if request.method == "POST":
	# 	try:
	# 		data = json.loads(request.body)
	# 		section_id = data.get("section_id")
	# 		proficiency_level = data.get("proficiency_level")
			
	# 		if section_id and proficiency_level:
	# 			section = Section.objects.filter(id=section_id).first()
	# 			if section:
	# 				section.proficiency_level = int(proficiency_level)
	# 				section.save()
	# 				return JsonResponse({"success": True})
	# 	except Exception as e:
	# 		print(f"Proficiency update error: {e}")
	# return JsonResponse({"success": False})


# Magneettikuvaus section endpoints
@csrf_exempt
def add_magneettikuvaus_section_view(request):
	"""Add new section to Magneettikuvaus EPA"""
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
def edit_magneettikuvaus_section_view(request):
	"""Edit existing section in Magneettikuvaus EPA"""
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
def delete_magneettikuvaus_section_view(request):
	"""Delete section from Radiologia Magneettikuvaus EPA"""
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
def update_magneettikuvaus_proficiency_view(request):
	"""Update proficiency level for Magneettikuvaus section"""
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


# Mammografia section endpoints
@csrf_exempt
def add_mammografia_section_view(request):
	"""Add new section to Mammografia EPA"""
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
def edit_mammografia_section_view(request):
	"""Edit existing section in Mammografia EPA"""
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
def delete_mammografia_section_view(request):
	"""Delete section from Mammografia EPA"""
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
def update_mammografia_proficiency_view(request):
	"""Update proficiency level for Mammografia section"""
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

# Natiivikuvantaminen section endpoints
@csrf_exempt
def add_natiivikuvantaminen_section_view(request):
	"""Add new section to Natiivikuvantaminen EPA"""
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
def edit_natiivikuvantaminen_section_view(request):
	"""Edit existing section in Natiivikuvantaminen EPA"""
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
def delete_natiivikuvantaminen_section_view(request):
	"""Delete section from Natiivikuvantaminen EPA"""
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
def update_natiivikuvantaminen_proficiency_view(request):
	"""Update proficiency level for Natiivikuvantaminen section"""
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


# Tietokonetomografia section endpoints
@csrf_exempt
def add_tietokonetomografia_section_view(request):
	"""Add new section to Tietokonetomografia EPA"""
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
def edit_tietokonetomografia_section_view(request):
	"""Edit existing section in Tietokonetomografia EPA"""
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
def delete_tietokonetomografia_section_view(request):
	"""Delete section from Tietokonetomografia EPA"""
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
def update_tietokonetomografia_proficiency_view(request):
	"""Update proficiency level for Tietokonetomografia section"""
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

# Ultraaani section endpoints
@csrf_exempt
def add_ultraaani_section_view(request):
	"""Add new section to Ultraaani EPA"""
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
def edit_ultraaani_section_view(request):
	"""Edit existing section in Ultraaani EPA"""
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
def delete_ultraaani_section_view(request):
	"""Delete section from Ultraaani EPA"""
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
def update_ultraaani_proficiency_view(request):
	"""Update proficiency level for Ultraaani section"""
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

# Kuvankatselunaytot section endpoints
@csrf_exempt
def add_kuvankatselunaytot_section_view(request):
	"""Add new section to Kuvankatselunaytot EPA"""
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
def edit_kuvankatselunaytot_section_view(request):
	"""Edit existing section in Kuvankatselunaytot EPA"""
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
def delete_kuvankatselunaytot_section_view(request):
	"""Delete section from Kuvankatselunaytot EPA"""
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
def update_kuvankatselunaytot_proficiency_view(request):
	"""Update proficiency level for Kuvankatselunaytot section"""
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

# Hammaskuvantaminen section endpoints
@csrf_exempt
def add_hammaskuvantaminen_section_view(request):
	"""Add new section to Hammaskuvantaminen EPA"""
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
def edit_hammaskuvantaminen_section_view(request):
	"""Edit existing section in Hammaskuvantaminen EPA"""
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
def delete_hammaskuvantaminen_section_view(request):
	"""Delete section from Hammaskuvantaminen EPA"""
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
def update_hammaskuvantaminen_proficiency_view(request):
	"""Update proficiency level for Hammaskuvantaminen section"""
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

# Radiologia Sateilybiologia-suojelu section endpoints  
@csrf_exempt
def add_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Add new section to Sateilybiologia-suojelu EPA"""
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
def edit_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Sateilybiologia-suojelu EPA"""
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
def delete_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Sateilybiologia-suojelu EPA"""
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
def update_radiologia_sateilybiologia_suojelu_proficiency_view(request):
	"""Update proficiency level for Sateilybiologia-suojelu section"""
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
# SADEHOITO SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Peruskäsitteet section endpoints
@csrf_exempt
def add_sadehoito_peruskasitteet_section_view(request):
	"""Add new section to Sädehoidon peruskäsitteet EPA"""
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
def edit_sadehoito_peruskasitteet_section_view(request):
	"""Edit existing section in Sädehoidon peruskäsitteet EPA"""
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
def delete_sadehoito_peruskasitteet_section_view(request):
	"""Delete section from Sädehoidon peruskäsitteet EPA"""
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
def update_sadehoito_peruskasitteet_proficiency_view(request):
	"""Update proficiency level for Sädehoidon peruskäsitteet section"""
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

# Kuvantaminen ja suunnittelu section endpoints
@csrf_exempt
def add_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Add new section to Kuvantaminen ja suunnittelu EPA"""
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
def edit_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Edit existing section in Kuvantaminen ja suunnittelu EPA"""
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
def delete_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Delete section from Kuvantaminen ja suunnittelu EPA"""
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
def update_sadehoito_kuvantaminen_suunnittelu_proficiency_view(request):
	"""Update proficiency level for Kuvantaminen ja suunnittelu section"""
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


# Ulkoinen sädehoito section endpoints
@csrf_exempt
def add_sadehoito_ulkoinen_section_view(request):
	"""Add new section to Ulkoinen EPA"""
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
def edit_sadehoito_ulkoinen_section_view(request):
	"""Edit existing section in Ulkoinen EPA"""
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
def delete_sadehoito_ulkoinen_section_view(request):
	"""Delete section from Ulkoinen EPA"""
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
def update_sadehoito_ulkoinen_proficiency_view(request):
	"""Update proficiency level for Ulkoinen section"""
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


# Sisäinen sädehoito section endpoints
@csrf_exempt
def add_sadehoito_sisainen_section_view(request):
	"""Add new section to Sisäinen sädehoito EPA"""
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
def edit_sadehoito_sisainen_section_view(request):
	"""Edit existing section in Sisäinen sädehoito EPA"""
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
def delete_sadehoito_sisainen_section_view(request):
	"""Delete section from Sisäinen sädehoito EPA"""
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
def update_sadehoito_sisainen_proficiency_view(request):
	"""Update proficiency level for Sisäinen sädehoito section"""
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


# Dosimetria section endpoints
@csrf_exempt
def add_sadehoito_dosimetria_section_view(request):
	"""Add new section to Dosimetria EPA"""
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
def edit_sadehoito_dosimetria_section_view(request):
	"""Edit existing section in Dosimetria EPA"""
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
def delete_sadehoito_dosimetria_section_view(request):
	"""Delete section from Dosimetria EPA"""
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
def update_sadehoito_dosimetria_proficiency_view(request):
	"""Update proficiency level for Dosimetria section"""
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

# Laitteet section endpoints
@csrf_exempt
def add_sadehoito_laitteet_section_view(request):
	"""Add new section to Laitteet EPA"""
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
def edit_sadehoito_laitteet_section_view(request):
	"""Edit existing section in Laitteet EPA"""
	if request.method == "POST":
		try:
			# Try JSON first for compatibility with old code
			data = json.loads(request.body)
			section_id = data.get("section_id")
			title = data.get("title")
			content = data.get("content")
			proficiency_level = data.get("proficiency_level")
			action = data.get("action")
		except json.JSONDecodeError:
			# Fall back to POST data for new form-based requests
			try:
				section_id = request.POST.get("section_id")
				title = request.POST.get("title", "").strip()
				content = request.POST.get("content", "")
				proficiency_level = request.POST.get("proficiency_level")
				action = request.POST.get("action")
			except Exception as e:
				return JsonResponse({
					"success": False, 
					"error": f"Data processing error: {str(e)}"
				})
		except Exception as e:
			# Handle RequestDataTooBig and other exceptions
			from django.core.exceptions import RequestDataTooBig
			if isinstance(e, RequestDataTooBig):
				return JsonResponse({
					"success": False, 
					"error": "Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE. Please reduce content size or increase Django memory limits."
				})
			return JsonResponse({
				"success": False, 
				"error": f"Request processing error: {str(e)}"
			})
		
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
def delete_sadehoito_laitteet_section_view(request):
	"""Delete section from Laitteet EPA"""
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
def update_sadehoito_laitteet_proficiency_view(request):
	"""Update proficiency level for Laitteet section"""
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


# Säteilybiologia section endpoints
@csrf_exempt
def add_sadehoito_sateilybiologia_section_view(request):
	"""Add new section to Säteilybiologia EPA"""
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
def edit_sadehoito_sateilybiologia_section_view(request):
	"""Edit existing section in Säteilybiologia EPA"""
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
def delete_sadehoito_sateilybiologia_section_view(request):
	"""Delete section from Säteilybiologia EPA"""
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
def update_sadehoito_sateilybiologia_proficiency_view(request):
	"""Update proficiency level for Säteilybiologia section"""
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
# ISOTOOPPI SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Gammakamera section endpoints
@csrf_exempt
def add_isotooppi_gammakamera_section_view(request):
	"""Add new section to Gammakamera EPA"""
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
def edit_isotooppi_gammakamera_section_view(request):
	"""Edit existing section in Gammakamera EPA"""
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
def delete_isotooppi_gammakamera_section_view(request):
	"""Delete section from Gammakamera EPA"""
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
def update_isotooppi_gammakamera_proficiency_view(request):
	"""Update proficiency level for Gammakamera section"""
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

# PET-kamera section endpoints
@csrf_exempt
def add_isotooppi_pet_kamera_section_view(request):
	"""Add new section to PET-kamera EPA"""
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
def edit_isotooppi_pet_kamera_section_view(request):
	"""Edit existing section in PET-kamera EPA"""
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
def delete_isotooppi_pet_kamera_section_view(request):
	"""Delete section from PET-kamera EPA"""
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
def update_isotooppi_pet_kamera_proficiency_view(request):
	"""Update proficiency level for PET-kamera section"""
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

# Annostelu ja radiofarmasia section endpoints
@csrf_exempt
def add_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Add new section to Annostelu ja radiofarmasia EPA"""
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
def edit_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Edit existing section in Annostelu ja radiofarmasia EPA"""
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
def delete_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Delete section from Annostelu ja radiofarmasia EPA"""
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
def update_isotooppi_annostelu_radiofarmasia_proficiency_view(request):
	"""Update proficiency level for Annostelu ja radiofarmasia section"""
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

# Gammakuvaus ja SPET section endpoints
@csrf_exempt
def add_isotooppi_gammakuvaus_spet_section_view(request):
	"""Add new section to Gammakuvaus ja SPET EPA"""
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
def edit_isotooppi_gammakuvaus_spet_section_view(request):
	"""Edit existing section in Gammakuvaus ja SPET EPA"""
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
def delete_isotooppi_gammakuvaus_spet_section_view(request):
	"""Delete section from Gammakuvaus ja SPET EPA"""
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
def update_isotooppi_gammakuvaus_spet_proficiency_view(request):
	"""Update proficiency level for Gammakuvaus ja SPET section"""
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

# PET-tutkimukset section endpoints
@csrf_exempt
def add_isotooppi_pet_tutkimukset_section_view(request):
	"""Add new section to PET-tutkimukset EPA"""
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
def edit_isotooppi_pet_tutkimukset_section_view(request):
	"""Edit existing section in PET-tutkimukset EPA"""
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
def delete_isotooppi_pet_tutkimukset_section_view(request):
	"""Delete section from PET-tutkimukset EPA"""
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
def update_isotooppi_pet_tutkimukset_proficiency_view(request):
	"""Update proficiency level for PET-tutkimukset section"""
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

# Radionuklidihoidot section endpoints
@csrf_exempt
def add_isotooppi_radionuklidihoidot_section_view(request):
	"""Add new section to Radionuklidihoidot EPA"""
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
def edit_isotooppi_radionuklidihoidot_section_view(request):
	"""Edit existing section in Radionuklidihoidot EPA"""
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
def delete_isotooppi_radionuklidihoidot_section_view(request):
	"""Delete section from Radionuklidihoidot EPA"""
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
def update_isotooppi_radionuklidihoidot_proficiency_view(request):
	"""Update proficiency level for Radionuklidihoidot section"""
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

# Säteilybiologia ja suojelu section endpoints
@csrf_exempt
def add_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Add new section to Säteilybiologia ja suojelu EPA"""
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
def edit_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Säteilybiologia ja suojelu EPA"""
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
def delete_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Säteilybiologia ja suojelu EPA"""
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
def update_isotooppi_sateilybiologia_suojelu_proficiency_view(request):
	"""Update proficiency level for Säteilybiologia ja suojelu section"""
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
# RAPORTOI ONGELMA SECTION MANAGEMENT
# =============================================================================



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