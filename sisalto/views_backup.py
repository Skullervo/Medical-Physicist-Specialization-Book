from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# MAMMOGRAFIA ENDPOINTIT
@csrf_exempt
def add_mammografia_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title", "")
		content = data.get("content", "")
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
def edit_mammografia_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title", "")
		content = data.get("content", "")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_mammografia_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

def radiologia_mammografia_view(request):
	# Haetaan tai luodaan EPA-objekti
	from .models import Specialty, EPA, Section
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Mammografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_mammografia.html', {
		'page_title': 'Mammografia',
		'epa': epa,
		'sections': sections
	})
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def edit_natiivikuvantaminen_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title", "")
		content = data.get("content", "")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_natiivikuvantaminen_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def edit_magneettikuvaus_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title", "")
		content = data.get("content", "")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_magneettikuvaus_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})
def add_magneettikuvaus_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title", "")
		content = data.get("content", "")
		epa_id = data.get("epa_id")
		print(f"DEBUG: title={title}, content={content[:30]}, epa_id={epa_id}")
		if title and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			print(f"DEBUG: epa={epa}")
			if epa:
				last_section = Section.objects.filter(epa=epa).order_by('-order').first()
				order = (last_section.order + 1) if last_section else 1
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				print("DEBUG: Section created!")
				return JsonResponse({"success": True})
			else:
				print("DEBUG: EPA not found!")
		else:
			print("DEBUG: title or epa_id missing!")
	return JsonResponse({"success": False})
from django.http import HttpResponse

# Apunäkymä: Luo Radiologia-specialty ja Natiivikuvantaminen-EPA
def create_radiologia_epa(request):
	from .models import Specialty, EPA
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, created = EPA.objects.get_or_create(specialty=specialty, title="Natiivikuvantaminen")
	if created:
		msg = "EPA luotu!"
	else:
		msg = "EPA löytyi jo."
	return HttpResponse(f"Specialty: {specialty.name} (id={specialty.id})<br>EPA: {epa.title} (id={epa.id})<br>{msg}")
def add_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title", "")
		content = data.get("content", "")
		epa_id = data.get("epa_id")
		position = data.get("position")  # Uusi parametri järjestyksen määrittämiseen
		print(f"DEBUG: title={title}, content={content[:30]}, epa_id={epa_id}, position={position}")
		
		# EPA ID mapping - käsitellään sekä numerot että merkkijonot
		actual_epa_id = epa_id
		if isinstance(epa_id, str):
			epa_mapping = {
				"epa17": 1,  # Natiivikuvantaminen
				"epa19": 4,  # Ultraääni (juuri luotu)
				"epa15": 2,  # Magneettikuvaus
				"epa16": 3,  # Mammografia
			}
			actual_epa_id = epa_mapping.get(epa_id, epa_id)
		
		print(f"DEBUG: mapped epa_id {epa_id} -> {actual_epa_id}")
		
		if title and actual_epa_id:
			epa = EPA.objects.filter(id=actual_epa_id).first()
			print(f"DEBUG: epa={epa}")
			if epa:
				if position is not None:
					# Lisää tiettyyn kohtaan - järjestele muut osiot
					sections_to_reorder = Section.objects.filter(epa=epa, order__gte=position).order_by('order')
					for section in sections_to_reorder:
						section.order += 1
						section.save()
					order = position
				else:
					# Lisää loppuun (vanha toiminnallisuus)
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				Section.objects.create(epa=epa, title=title, content=content, order=order)
				print("DEBUG: Section created!")
				return JsonResponse({"success": True})
			else:
				print("DEBUG: EPA not found!")
		else:
			print("DEBUG: title or epa_id missing!")
	return JsonResponse({"success": False})
from django.views.decorators.csrf import csrf_exempt
# Radiologian alisivujen näkymät
def radiologia_lapivalaisu_angiografia_view(request):
	return render(request, 'sisalto/radiologia_lapivalaisu_angiografia.html', {'page_title': 'Läpivalaisu ja angiografia (ml kardiologia)'})

def radiologia_magneettikuvaus_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Magneettikuvaus")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_magneettikuvaus.html', {
		'page_title': 'Magneettikuvaus',
		'epa': epa,
		'sections': sections
	})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Section

def radiologia_natiivikuvantaminen_view(request):
	# Haetaan EPA-objekti
	epa = EPA.objects.filter(title__iexact='Natiivikuvantaminen', specialty__name__iexact='Radiologia').first()
	sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
	return render(request, 'sisalto/radiologia_natiivikuvantaminen.html', {
		'page_title': 'Natiivikuvantaminen',
		'epa': epa,
		'sections': sections
	})

@csrf_exempt
def save_natiivikuvantaminen_content(request):
	import json
	if request.method == "POST":
		data = json.loads(request.body)
		content = data.get("content", "")
		epa = EPA.objects.filter(title__iexact='Natiivikuvantaminen', specialty__name__iexact='Radiologia').first()
		if epa:
			epa.natiivikuvantaminen_content = content
			epa.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

def radiologia_tietokonetomografia_view(request):
	return render(request, 'sisalto/radiologia_tietokonetomografia.html', {'page_title': 'Tietokonetomografia'})

def radiologia_ultraaani_view(request):
	# Haetaan EPA-objekti
	epa = EPA.objects.filter(title__iexact='Ultraääni', specialty__name__iexact='Radiologia').first()
	sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
	return render(request, 'sisalto/radiologia_ultraaani.html', {
		'page_title': 'Ultraääni',
		'epa': epa,
		'sections': sections
	})

@csrf_exempt
def edit_ultraaani_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		title = data.get("title", "")
		content = data.get("content", "")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.title = title
			section.content = content
			section.save()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def delete_ultraaani_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

def radiologia_kuvankatselunaytot_view(request):
	return render(request, 'sisalto/radiologia_kuvankatselunaytot.html', {'page_title': 'Kuvankatselunäytöt'})

def radiologia_hammaskuvantaminen_view(request):
	return render(request, 'sisalto/radiologia_hammaskuvantaminen.html', {'page_title': 'Hammas­kuvantaminen'})

def radiologia_sateilybiologia_suojelu_view(request):
	return render(request, 'sisalto/radiologia_sateilybiologia_suojelu.html', {'page_title': 'Säteilybiologia ja säteily­suojelu radiologiassa'})
# Radiologian alisivut
def radiologia_subpages_view(request):
	return render(request, 'sisalto/radiologia_subpages.html', {'page_title': 'Radiologian alisivut'})
from django.shortcuts import render, get_object_or_404
from .models import FrontPage, Specialty, EPA, ExamQuestion

def frontpage_view(request):
	page = FrontPage.objects.first()
	return render(request, 'sisalto/frontpage.html', {'page': page})

def specialty_list_view(request):
	specialties = Specialty.objects.all()
	return render(request, 'sisalto/specialty_list.html', {'specialties': specialties})

def specialty_detail_view(request, specialty_id):
	specialty = get_object_or_404(Specialty, id=specialty_id)
	epas = specialty.epas.all()
	return render(request, 'sisalto/specialty_detail.html', {'specialty': specialty, 'epas': epas})

def epa_detail_view(request, epa_id):
	epa = get_object_or_404(EPA, id=epa_id)
	return render(request, 'sisalto/epa_detail.html', {'epa': epa})

def examquestion_list_view(request):
	questions = ExamQuestion.objects.all()
	return render(request, 'sisalto/examquestion_list.html', {'questions': questions})

# Erikoisalojen EPA-listanäkymät
def radiologia_epas_view(request):
	specialty = Specialty.objects.filter(name__iexact='Radiologia').first()
	epas = specialty.epas.all() if specialty else []
	return render(request, 'sisalto/radiologia_epas.html', {'epas': epas, 'page_title': 'Radiologian EPA:t'})

def sadehoito_epas_view(request):
	specialty = Specialty.objects.filter(name__iexact='Sädehoito').first()
	epas = specialty.epas.all() if specialty else []
	return render(request, 'sisalto/sadehoito_epas.html', {'epas': epas, 'page_title': 'Sädehoidon EPA:t'})

def isotooppi_epas_view(request):
	specialty = Specialty.objects.filter(name__iexact='Isotooppilääketiede').first()
	epas = specialty.epas.all() if specialty else []
	return render(request, 'sisalto/isotooppi_epas.html', {'epas': epas, 'page_title': 'Isotooppilääketieteen EPA:t'})

def knf_epas_view(request):
	specialty = Specialty.objects.filter(name__iexact='KNF').first()
	epas = specialty.epas.all() if specialty else []
	return render(request, 'sisalto/knf_epas.html', {'epas': epas, 'page_title': 'KNF:n EPA:t'})

def fysiologia_epas_view(request):
	specialty = Specialty.objects.filter(name__iexact='Fysiologia').first()
	epas = specialty.epas.all() if specialty else []
	return render(request, 'sisalto/fysiologia_epas.html', {'epas': epas, 'page_title': 'Fysiologian EPA:t'})

# Kaikkien EPA:jen näkymä
def epas_view(request):
	specialties = Specialty.objects.all()
	return render(request, 'sisalto/epas.html', {'specialties': specialties, 'page_title': 'Kaikki EPA:t'})
def sadehoito_peruskasitteet_view(request):
    epa = EPA.objects.filter(title__iexact='Sädehoidon peruskasitteet').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_peruskasitteet.html', {
        'page_title': 'Sädehoidon peruskäsitteet',
        'epa': epa,
        'sections': sections
    })

def sadehoito_kuvantaminen_suunnittelu_view(request):
    epa = EPA.objects.filter(title__iexact='Kuvantaminen sädehoidon suunnittelua varten').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_kuvantaminen_suunnittelu.html', {
        'page_title': 'Kuvantaminen sädehoidon suunnittelua varten',
        'epa': epa,
        'sections': sections
    })

def sadehoito_ulkoinen_view(request):
    epa = EPA.objects.filter(title__iexact='Ulkoinen sädehoito').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_ulkoinen.html', {
        'page_title': 'Ulkoinen sädehoito',
        'epa': epa,
        'sections': sections
    })

def sadehoito_sisainen_view(request):
    epa = EPA.objects.filter(title__iexact='Sisäinen sädehoito').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_sisainen.html', {
        'page_title': 'Sisäinen sädehoito',
        'epa': epa,
        'sections': sections
    })

def sadehoito_dosimetria_view(request):
    epa = EPA.objects.filter(title__iexact='Sädehoidon dosimetria').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_dosimetria.html', {
        'page_title': 'Sädehoidon dosimetria',
        'epa': epa,
        'sections': sections
    })

def sadehoito_laitteet_view(request):
    epa = EPA.objects.filter(title__iexact='Säteilyä tuottavat laitteet sädehoidossa').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_laitteet.html', {
        'page_title': 'Säteilyä tuottavat laitteet sädehoidossa',
        'epa': epa,
        'sections': sections
    })

def sadehoito_sateilybiologia_view(request):
    epa = EPA.objects.filter(title__iexact='Säteilybiologia ja säteily­suojelu sädehoidossa').first()
    sections = Section.objects.filter(epa=epa).order_by('order', 'id') if epa else []
    return render(request, 'sisalto/sadehoito_sateilybiologia.html', {
        'page_title': 'Säteilybiologia ja säteily­suojelu sädehoidossa',
        'epa': epa,
        'sections': sections
    })
