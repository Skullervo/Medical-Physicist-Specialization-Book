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
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Max
from django.shortcuts import render, get_object_or_404
from .models import Section, EPA, Specialty
import json

# =============================================================================
# GENERAL PAGE VIEWS
# =============================================================================

def frontpage_view(request):
	"""Main landing page view"""
	try:
		from .models import FrontPage
		page = FrontPage.objects.first()
	except:
		page = None
	return render(request, 'sisalto/frontpage.html', {'page': page})

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
	return render(request, 'sisalto/radiologia_subpages.html', {'page_title': 'Radiologian alisivut'})

def radiologia_lapivalaisu_angiografia_view(request):
	"""Läpivalaisu ja angiografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Läpivalaisu ja angiografia (ml kardiologia)")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_lapivalaisu_angiografia.html', {
		'page_title': 'Läpivalaisu ja angiografia (ml kardiologia)',
		'epa': epa,
		'sections': sections
	})

def radiologia_magneettikuvaus_view(request):
	"""Magneettikuvaus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Magneettikuvaus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_magneettikuvaus.html', {
		'page_title': 'Magneettikuvaus',
		'epa': epa,
		'sections': sections
	})

def radiologia_mammografia_view(request):
	"""Mammografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Mammografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_mammografia.html', {
		'page_title': 'Mammografia',
		'epa': epa,
		'sections': sections
	})

def radiologia_natiivikuvantaminen_view(request):
	"""Natiivikuvantaminen EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Natiivikuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_natiivikuvantaminen.html', {
		'page_title': 'Natiivikuvantaminen',
		'epa': epa,
		'sections': sections
	})

def radiologia_tietokonetomografia_view(request):
	"""Tietokonetomografia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Tietokonetomografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_tietokonetomografia.html', {
		'page_title': 'Tietokonetomografia',
		'epa': epa,
		'sections': sections
	})

def radiologia_ultraaani_view(request):
	"""Ultraääni EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ultraääni")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_ultraaani.html', {
		'page_title': 'Ultraääni',
		'epa': epa,
		'sections': sections
	})

def radiologia_kuvankatselunaytot_view(request):
	"""Kuvankatselunäytöt EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvankatselunäytöt")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_kuvankatselunaytot.html', {
		'page_title': 'Kuvankatselunäytöt',
		'epa': epa,
		'sections': sections
	})

def radiologia_hammaskuvantaminen_view(request):
	"""Hammaskuvantaminen EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Hammaskuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_hammaskuvantaminen.html', {
		'page_title': 'Hammaskuvantaminen',
		'epa': epa,
		'sections': sections
	})

def radiologia_sateilybiologia_suojelu_view(request):
	"""Säteilybiologia ja säteilysuojelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja säteilysuojelu radiologiassa")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_sateilybiologia_suojelu.html', {
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
	return render(request, 'sisalto/sadehoito_peruskasitteet.html', {
		'page_title': 'Sädehoidon peruskäsitteet',
		'epa': epa,
		'sections': sections
	})

def sadehoito_kuvantaminen_suunnittelu_view(request):
	"""Kuvantaminen ja suunnittelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvantaminen ja suunnittelu")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_kuvantaminen_suunnittelu.html', {
		'page_title': 'Kuvantaminen sädehoidon suunnittelua varten',
		'epa': epa,
		'sections': sections
	})

def sadehoito_ulkoinen_view(request):
	"""Ulkoinen sädehoito EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ulkoinen sädehoito")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_ulkoinen.html', {
		'page_title': 'Ulkoinen sädehoito',
		'epa': epa,
		'sections': sections
	})

def sadehoito_sisainen_view(request):
	"""Sisäinen sädehoito EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sisäinen sädehoito")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_sisainen.html', {
		'page_title': 'Sisäinen sädehoito',
		'epa': epa,
		'sections': sections
	})

def sadehoito_dosimetria_view(request):
	"""Sädehoidon dosimetria EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Dosimetria")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_dosimetria.html', {
		'page_title': 'Sädehoidon dosimetria',
		'epa': epa,
		'sections': sections
	})

def sadehoito_laitteet_view(request):
	"""Säteilyä tuottavat laitteet EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laitteet")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_laitteet.html', {
		'page_title': 'Säteilyä tuottavat laitteet sädehoidossa',
		'epa': epa,
		'sections': sections
	})

def sadehoito_sateilybiologia_view(request):
	"""Säteilybiologia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/sadehoito_sateilybiologia.html', {
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
	return render(request, 'sisalto/isotooppi_gammakamera.html', {
		'page_title': 'Gammakamerateknologia',
		'epa': epa,
		'sections': sections
	})

def isotooppi_petkamera_view(request):
	"""PET-kamerateknologia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-kamera")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_petkamera.html', {
		'page_title': 'PET-kamerateknologia',
		'epa': epa,
		'sections': sections
	})

def isotooppi_annostelu_radiofarmasia_view(request):
	"""Annostelu ja radiofarmasia EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Annostelu ja radiofarmasia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_annostelu_radiofarmasia.html', {
		'page_title': 'Annostelu ja radiofarmasiatoiminta',
		'epa': epa,
		'sections': sections
	})

def isotooppi_gammakuvaus_spet_view(request):
	"""Gammakuvaus ja SPET EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Gammakuvaus ja SPET")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_gammakuvaus_spet.html', {
		'page_title': 'Gammakuvaus ja SPET-tutkimukset',
		'epa': epa,
		'sections': sections
	})

def isotooppi_pet_tutkimukset_view(request):
	"""PET-tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_pet_tutkimukset.html', {
		'page_title': 'PET-tutkimukset',
		'epa': epa,
		'sections': sections
	})

def isotooppi_radionuklidihoidot_view(request):
	"""Radionuklidihoidot EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Radionuklidihoidot")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_radionuklidihoidot.html', {
		'page_title': 'Radionuklidihoidot',
		'epa': epa,
		'sections': sections
	})

def isotooppi_sateilybiologia_suojelu_view(request):
	"""Säteilybiologia ja suojelu EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja suojelu")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/isotooppi_sateilybiologia_suojelu.html', {
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
	return render(request, 'sisalto/knf_eeg.html', {'epa': epa, 'sections': sections})

def knf_heratepotentiaali_enmg_view(request):
	"""Herätepotentiaali ja ENMG EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Herätepotentiaali ja ENMG-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf_heratepotentiaali_enmg.html', {'epa': epa, 'sections': sections})

def knf_iom_view(request):
	"""IOM EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="IOM")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf_iom.html', {'epa': epa, 'sections': sections})

def knf_laite_sahkoturvallisuus_view(request):
	"""Laite- ja sähköturvallisuus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laite- ja sähköturvallisuus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf_laite_sahkoturvallisuus.html', {'epa': epa, 'sections': sections})

def knf_sarja_tms_hoidot_view(request):
	"""Sarja-TMS-hoidot EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sarja-TMS-hoidot ja navigoidut TMS-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf_sarja_tms_hoidot.html', {'epa': epa, 'sections': sections})

def knf_uni_view(request):
	"""Uni EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="KNF")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Uni")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/knf_uni.html', {'epa': epa, 'sections': sections})

# =============================================================================
# FYSIOLOGIA VIEWS
# =============================================================================

def fysiologia_ekg_view(request):
	"""EKG-tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="EKG-tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia_ekg.html', {'epa': epa, 'sections': sections})

def fysiologia_gi_kanava_view(request):
	"""GI-kanavan tutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="GI-kanavan tutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia_gi_kanava.html', {'epa': epa, 'sections': sections})

def fysiologia_keuhkofunktio_view(request):
	"""Keuhkofunktiotutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Keuhkofunktiotutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia_keuhkofunktio.html', {'epa': epa, 'sections': sections})

def fysiologia_luuston_mineraali_view(request):
	"""Luuston mineraalitiheyden mittaus EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Luuston mineraalitiheyden mittaus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia_luuston_mineraali.html', {'epa': epa, 'sections': sections})

def fysiologia_verenkierto_view(request):
	"""Verenkiertotutkimukset EPA page"""
	specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Verenkiertotutkimukset")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/fysiologia_verenkierto.html', {'epa': epa, 'sections': sections})

# =============================================================================
# RADIOLOGIA SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# Lapivalaisu-angiografia section endpoints
@csrf_exempt
def add_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Add new section to Lapivalaisu-angiografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Edit existing section in Lapivalaisu-angiografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_radiologia_lapivalaisu_angiografia_section_view(request):
	"""Delete section from Lapivalaisu-angiografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# Magneettikuvaus section endpoints  
@csrf_exempt
def add_magneettikuvaus_section_view(request):
	"""Add new section to Magneettikuvaus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_magneettikuvaus_section_view(request):
	"""Edit existing section in Magneettikuvaus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_magneettikuvaus_section_view(request):
	"""Delete section from Magneettikuvaus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_mammografia_section_view(request):
	"""Edit existing section in Mammografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_mammografia_section_view(request):
	"""Delete section from Mammografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_natiivikuvantaminen_section_view(request):
	"""Edit existing section in Natiivikuvantaminen EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_natiivikuvantaminen_section_view(request):
	"""Delete section from Natiivikuvantaminen EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_tietokonetomografia_section_view(request):
	"""Edit existing section in Tietokonetomografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_tietokonetomografia_section_view(request):
	"""Delete section from Tietokonetomografia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_ultraaani_section_view(request):
	"""Edit existing section in Ultraaani EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_ultraaani_section_view(request):
	"""Delete section from Ultraaani EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_kuvankatselunaytot_section_view(request):
	"""Edit existing section in Kuvankatselunaytot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_kuvankatselunaytot_section_view(request):
	"""Delete section from Kuvankatselunaytot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_hammaskuvantaminen_section_view(request):
	"""Edit existing section in Hammaskuvantaminen EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_hammaskuvantaminen_section_view(request):
	"""Delete section from Hammaskuvantaminen EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# Radiologia Sateilybiologia-suojelu section endpoints  
@csrf_exempt
def add_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Add new section to Radiologia Sateilybiologia-suojelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					order = after_order + 1
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Radiologia Sateilybiologia-suojelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_radiologia_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Radiologia Sateilybiologia-suojelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
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
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level")
		action = data.get("action")
		
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

# Kuvantaminen ja suunnittelu section endpoints
@csrf_exempt
def add_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Add new section to Kuvantaminen ja suunnittelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level", "1")
		epa_id = data.get("epa_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				last_section = Section.objects.filter(epa=epa).order_by('-order').first()
				order = (last_section.order + 1) if last_section else 1
				Section.objects.create(
					epa=epa, 
					title=title, 
					content=content, 
					proficiency_level=proficiency_level,
					order=order
				)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_sadehoito_kuvantaminen_suunnittelu_section_view(request):
	"""Edit existing section in Kuvantaminen ja suunnittelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level")
		action = data.get("action")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				# If it's just updating proficiency level
				if action == 'update_proficiency' and proficiency_level:
					section.proficiency_level = proficiency_level
					section.save()
					return JsonResponse({"success": True})
				# If it's updating title and content
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

# Ulkoinen sädehoito section endpoints
@csrf_exempt
def add_sadehoito_ulkoinen_section_view(request):
	"""Add new section to Ulkoinen sädehoito EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		proficiency_level = data.get("proficiency_level", "1")  # Default to level 1
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
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
	"""Edit existing section in Ulkoinen sädehoito EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level")
		action = data.get("action")
		
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
	"""Delete section from Ulkoinen sädehoito EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
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
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
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
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level")
		action = data.get("action")
		
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
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
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
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		proficiency_level = data.get("proficiency_level")
		action = data.get("action")
		
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

# Laitteet section endpoints
@csrf_exempt
def add_sadehoito_laitteet_section_view(request):
	"""Add new section to Laitteet EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				last_section = Section.objects.filter(epa=epa).order_by('-order').first()
				order = (last_section.order + 1) if last_section else 1
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_sadehoito_laitteet_section_view(request):
	"""Edit existing section in Laitteet EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		
		if section_id and title:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.title = title
				section.content = content
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

# Säteilybiologia section endpoints
@csrf_exempt
def add_sadehoito_sateilybiologia_section_view(request):
	"""Add new section to Säteilybiologia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				last_section = Section.objects.filter(epa=epa).order_by('-order').first()
				order = (last_section.order + 1) if last_section else 1
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_sadehoito_sateilybiologia_section_view(request):
	"""Edit existing section in Säteilybiologia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title")
		content = data.get("content")
		
		if section_id and title:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.title = title
				section.content = content
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_gammakamera_section_view(request):
	"""Edit existing section in Gammakamera EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_gammakamera_section_view(request):
	"""Delete section from Gammakamera EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# PET-kamera section endpoints
@csrf_exempt
def add_isotooppi_petkamera_section_view(request):
	"""Add new section to PET-kamera EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_petkamera_section_view(request):
	"""Edit existing section in PET-kamera EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_petkamera_section_view(request):
	"""Delete section from PET-kamera EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Edit existing section in Annostelu ja radiofarmasia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_annostelu_radiofarmasia_section_view(request):
	"""Delete section from Annostelu ja radiofarmasia EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_gammakuvaus_spet_section_view(request):
	"""Edit existing section in Gammakuvaus ja SPET EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_gammakuvaus_spet_section_view(request):
	"""Delete section from Gammakuvaus ja SPET EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_pet_tutkimukset_section_view(request):
	"""Edit existing section in PET-tutkimukset EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_pet_tutkimukset_section_view(request):
	"""Delete section from PET-tutkimukset EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_radionuklidihoidot_section_view(request):
	"""Edit existing section in Radionuklidihoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_radionuklidihoidot_section_view(request):
	"""Delete section from Radionuklidihoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Edit existing section in Säteilybiologia ja suojelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_isotooppi_sateilybiologia_suojelu_section_view(request):
	"""Delete section from Säteilybiologia ja suojelu EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# =============================================================================
# KNF SECTION MANAGEMENT ENDPOINTS
# =============================================================================

# EEG section endpoints
@csrf_exempt
def add_knf_eeg_section_view(request):
	"""Add new section to EEG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_eeg_section_view(request):
	"""Edit existing section in EEG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_eeg_section_view(request):
	"""Delete section from EEG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# Herätepotentiaali ja ENMG section endpoints
@csrf_exempt
def add_knf_heratepotentiaali_enmg_section_view(request):
	"""Add new section to Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_heratepotentiaali_enmg_section_view(request):
	"""Edit existing section in Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_heratepotentiaali_enmg_section_view(request):
	"""Delete section from Herätepotentiaali ja ENMG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# IOM section endpoints
@csrf_exempt
def add_knf_iom_section_view(request):
	"""Add new section to IOM EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_iom_section_view(request):
	"""Edit existing section in IOM EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_iom_section_view(request):
	"""Delete section from IOM EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_laite_sahkoturvallisuus_section_view(request):
	"""Edit existing section in Laite- ja sähköturvallisuus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_laite_sahkoturvallisuus_section_view(request):
	"""Delete section from Laite- ja sähköturvallisuus EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_sarja_tms_hoidot_section_view(request):
	"""Edit existing section in Sarja-TMS-hoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_sarja_tms_hoidot_section_view(request):
	"""Delete section from Sarja-TMS-hoidot EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# Uni section endpoints
@csrf_exempt
def add_knf_uni_section_view(request):
	"""Add new section to Uni EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_knf_uni_section_view(request):
	"""Edit existing section in Uni EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_knf_uni_section_view(request):
	"""Delete section from Uni EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_ekg_section_view(request):
	"""Edit existing section in EKG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_ekg_section_view(request):
	"""Delete section from EKG EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
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
		after_order = data.get("after_order")
		
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				if after_order is not None:
					Section.objects.filter(epa=epa, order__gt=after_order).update(order=F('order') + 1)
					order = after_order + 1
				else:
					max_order = Section.objects.filter(epa=epa).aggregate(max_order=Max('order'))['max_order'] or 0
					order = max_order + 1
				
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_fysiologia_gi_kanava_section_view(request):
	"""Edit existing section in GI-kanava EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title")
		content = data.get("content")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_fysiologia_gi_kanava_section_view(request):
	"""Delete section from GI-kanava EPA"""
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# =============================================================================
# IMAGE UPLOAD FOR CKEDITOR
# =============================================================================

@csrf_exempt
def upload_image_view(request):
	"""Handle image uploads from CKEditor"""
	if request.method == 'POST' and request.FILES.get('upload'):
		import os
		from django.conf import settings
		from django.core.files.storage import default_storage
		from django.core.files.base import ContentFile
		
		upload = request.FILES['upload']
		
		# Validate file type
		allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
		if upload.content_type not in allowed_types:
			return JsonResponse({
				'error': {
					'message': 'Tiedostotyyppi ei ole tuettu. Sallitut tyypit: JPEG, PNG, GIF, WebP'
				}
			})
		
		# Validate file size (max 5MB)
		if upload.size > 5 * 1024 * 1024:
			return JsonResponse({
				'error': {
					'message': 'Tiedosto on liian suuri. Maksimikoko on 5MB.'
				}
			})
		
		try:
			# Create uploads directory if it doesn't exist
			upload_dir = 'uploads/images/'
			
			# Generate unique filename
			import uuid
			extension = os.path.splitext(upload.name)[1]
			filename = f"{uuid.uuid4()}{extension}"
			file_path = os.path.join(upload_dir, filename)
			
			# Save file
			path = default_storage.save(file_path, ContentFile(upload.read()))
			file_url = default_storage.url(path)
			
			return JsonResponse({
				'url': file_url
			})
			
		except Exception as e:
			return JsonResponse({
				'error': {
					'message': f'Virhe tallentaessa tiedostoa: {str(e)}'
				}
			})
	
	return JsonResponse({
		'error': {
			'message': 'Virheellinen pyyntö'
		}
	})