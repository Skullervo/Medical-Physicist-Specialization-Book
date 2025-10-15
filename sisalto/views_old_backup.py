from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import F, Max
from django.shortcuts import render, get_object_or_404
from .models import Section, EPA, Specialty
import json

# MAMMOGRAFIA ENDPOINTIT
@csrf_exempt
def add_mammografia_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_mammografia_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
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
		section_id = data.get("section_id")
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

@csrf_exempt
def edit_natiivikuvantaminen_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def add_natiivikuvantaminen_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_magneettikuvaus_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
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
		section_id = data.get("section_id")
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

# TIETOKONETOMOGRAFIA ENDPOINTIT
@csrf_exempt
def add_tietokonetomografia_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_tietokonetomografia_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# ULTRAAANI ENDPOINTIT
@csrf_exempt
def add_ultraaani_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_ultraaani_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# KUVANKATSELUNAYTOT ENDPOINTIT
@csrf_exempt
def add_kuvankatselunaytot_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_kuvankatselunaytot_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# HAMMASKUVANTAMINEN ENDPOINTIT
@csrf_exempt
def add_hammaskuvantaminen_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_hammaskuvantaminen_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# RADIOLOGIA SATEILYBIOLOGIA-SUOJELU ENDPOINTIT
@csrf_exempt
def add_radiologia_sateilybiologia_suojelu_section_view(request):
	import json
	from .models import Section, EPA
	if request.method == "POST":
		data = json.loads(request.body)
		title = data.get("title")
		content = data.get("content")
		epa_id = data.get("epa_id")
		after_order = data.get("after_order")
		
		if title and content and epa_id:
			epa = EPA.objects.filter(id=epa_id).first()
			if epa:
				# Get the next order number
				if after_order is not None:
					order = after_order + 1
					# Shift other sections
					Section.objects.filter(epa=epa, order__gte=order).update(order=F('order') + 1)
				else:
					last_section = Section.objects.filter(epa=epa).order_by('-order').first()
					order = (last_section.order + 1) if last_section else 1
				
				Section.objects.create(title=title, content=content, epa=epa, order=order)
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

@csrf_exempt
def edit_radiologia_sateilybiologia_suojelu_section_view(request):
	import json
	from .models import Section
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
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		section = Section.objects.filter(id=section_id).first()
		if section:
			section.delete()
			return JsonResponse({"success": True})
	return JsonResponse({"success": False})

# =============================================================================
# RADIOLOGIA VIEWS JA ENDPOINTS
# =============================================================================

# Radiologian alisivujen näkymät
def radiologia_lapivalaisu_angiografia_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Läpivalaisu ja angiografia (ml kardiologia)")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_lapivalaisu_angiografia.html', {
		'page_title': 'Läpivalaisu ja angiografia (ml kardiologia)',
		'epa': epa,
		'sections': sections
	})

def add_radiologia_lapivalaisu_angiografia_section_view(request):
	import json
	from .models import Section, EPA, Specialty
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

def edit_radiologia_lapivalaisu_angiografia_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		title = data.get("title", "")
		content = data.get("content", "")
		if section_id and title:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.title = title
				section.content = content
				section.save()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

def delete_radiologia_lapivalaisu_angiografia_section_view(request):
	import json
	from .models import Section
	if request.method == "POST":
		data = json.loads(request.body)
		section_id = data.get("section_id")
		if section_id:
			section = Section.objects.filter(id=section_id).first()
			if section:
				section.delete()
				return JsonResponse({"success": True})
	return JsonResponse({"success": False})

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

def radiologia_natiivikuvantaminen_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Natiivikuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
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
		specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
		epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Natiivikuvantaminen")
		epa.natiivikuvantaminen_content = content
		epa.save()
		return JsonResponse({"success": True})
	return JsonResponse({"success": False})

def radiologia_tietokonetomografia_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Tietokonetomografia")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_tietokonetomografia.html', {
		'page_title': 'Tietokonetomografia',
		'epa': epa,
		'sections': sections
	})

def radiologia_ultraaani_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ultraääni")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_ultraaani.html', {
		'page_title': 'Ultraääni',
		'epa': epa,
		'sections': sections
	})

def radiologia_kuvankatselunaytot_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvankatselunäytöt")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_kuvankatselunaytot.html', {
		'page_title': 'Kuvankatselunäytöt',
		'epa': epa,
		'sections': sections
	})

def radiologia_hammaskuvantaminen_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Hammaskuvantaminen")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_hammaskuvantaminen.html', {
		'page_title': 'Hammaskuvantaminen',
		'epa': epa,
		'sections': sections
	})

def radiologia_sateilybiologia_suojelu_view(request):
	# Haetaan tai luodaan EPA-objekti
	specialty, _ = Specialty.objects.get_or_create(name="Radiologia")
	epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja säteilysuojelu radiologiassa")
	sections = Section.objects.filter(epa=epa).order_by('order', 'id')
	return render(request, 'sisalto/radiologia_sateilybiologia_suojelu.html', {
		'page_title': 'Säteilybiologia ja säteilysuojelu radiologiassa',
		'epa': epa,
		'sections': sections
	})
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
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Peruskäsitteet")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_peruskasitteet.html', {
        'page_title': 'Sädehoidon peruskäsitteet',
        'epa': epa,
        'sections': sections
    })

def sadehoito_kuvantaminen_suunnittelu_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Kuvantaminen ja suunnittelu")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_kuvantaminen_suunnittelu.html', {
        'page_title': 'Kuvantaminen sädehoidon suunnittelua varten',
        'epa': epa,
        'sections': sections
    })

def sadehoito_ulkoinen_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Ulkoinen sädehoito")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_ulkoinen.html', {
        'page_title': 'Ulkoinen sädehoito',
        'epa': epa,
        'sections': sections
    })

def sadehoito_sisainen_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sisäinen sädehoito")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_sisainen.html', {
        'page_title': 'Sisäinen sädehoito',
        'epa': epa,
        'sections': sections
    })

def sadehoito_dosimetria_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Dosimetria")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_dosimetria.html', {
        'page_title': 'Sädehoidon dosimetria',
        'epa': epa,
        'sections': sections
    })

def sadehoito_laitteet_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laitteet")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_laitteet.html', {
        'page_title': 'Säteilyä tuottavat laitteet sädehoidossa',
        'epa': epa,
        'sections': sections
    })

def sadehoito_sateilybiologia_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Sädehoito")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/sadehoito_sateilybiologia.html', {
        'page_title': 'Säteilybiologia ja säteily­suojelu sädehoidossa',
        'epa': epa,
        'sections': sections
    })

# Sädehoidon section hallinta funktiot
def add_sadehoito_peruskasitteet_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_peruskasitteet_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_peruskasitteet_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def add_sadehoito_kuvantaminen_suunnittelu_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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
            print("DEBUG: Missing title or epa_id!")
    return JsonResponse({"success": False})

def edit_sadehoito_kuvantaminen_suunnittelu_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        print(f"DEBUG: section_id={section_id}, title={title}, content={content[:30]}")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                print("DEBUG: Section updated!")
                return JsonResponse({"success": True})
            else:
                print("DEBUG: Section not found!")
        else:
            print("DEBUG: Missing section_id or title!")
    return JsonResponse({"success": False})

def delete_sadehoito_kuvantaminen_suunnittelu_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        print(f"DEBUG: section_id={section_id}")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                print("DEBUG: Section deleted!")
                return JsonResponse({"success": True})
            else:
                print("DEBUG: Section not found!")
        else:
            print("DEBUG: Missing section_id!")
    return JsonResponse({"success": False})

# Ulkoinen sädehoito
def add_sadehoito_ulkoinen_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_ulkoinen_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_ulkoinen_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Sisäinen sädehoito
def add_sadehoito_sisainen_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_sisainen_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_sisainen_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Dosimetria
def add_sadehoito_dosimetria_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_dosimetria_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_dosimetria_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Laitteet
def add_sadehoito_laitteet_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_laitteet_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_laitteet_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Säteilybiologia
def add_sadehoito_sateilybiologia_section_view(request):
    import json
    from .models import Section, EPA, Specialty
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

def edit_sadehoito_sateilybiologia_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        title = data.get("title", "")
        content = data.get("content", "")
        if section_id and title:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.title = title
                section.content = content
                section.save()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def delete_sadehoito_sateilybiologia_section_view(request):
    import json
    from .models import Section
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("section_id")
        if section_id:
            section = Section.objects.filter(id=section_id).first()
            if section:
                section.delete()
                return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# ISOTOOPPILÄÄKETIETEEN SIVUT

def isotooppi_gammakamera_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Gammakamera")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_gammakamera.html', {
        'page_title': 'Gammakamerateknologia',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_gammakamera_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_gammakamera_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_petkamera_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-kamera")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_petkamera.html', {
        'page_title': 'PET-kamerateknologia',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_petkamera_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_petkamera_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_annostelu_radiofarmasia_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Annostelu ja radiofarmasia")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_annostelu_radiofarmasia.html', {
        'page_title': 'Annostelu ja radiofarmasiatoiminta',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_annostelu_radiofarmasia_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_annostelu_radiofarmasia_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_gammakuvaus_spet_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Gammakuvaus ja SPET")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_gammakuvaus_spet.html', {
        'page_title': 'Gammakuvaus ja SPET-tutkimukset',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_gammakuvaus_spet_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_gammakuvaus_spet_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_pet_tutkimukset_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="PET-tutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_pet_tutkimukset.html', {
        'page_title': 'PET-tutkimukset',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_pet_tutkimukset_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_pet_tutkimukset_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_radionuklidihoidot_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Radionuklidihoidot")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_radionuklidihoidot.html', {
        'page_title': 'Radionuklidihoidot',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_radionuklidihoidot_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_radionuklidihoidot_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def isotooppi_sateilybiologia_suojelu_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Isotooppilääketiede")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Säteilybiologia ja suojelu")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/isotooppi_sateilybiologia_suojelu.html', {
        'page_title': 'Säteilybiologia ja säteily­suojelu isotooppitoiminnassa',
        'epa': epa,
        'sections': sections
    })

@csrf_exempt
def add_isotooppi_sateilybiologia_suojelu_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_isotooppi_sateilybiologia_suojelu_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# KNF (Kliininen neurofysiologia) sivujen näkymät

def knf_eeg_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="EEG")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_eeg.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_eeg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_eeg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def knf_heratepotentiaali_enmg_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Herätepotentiaali ja ENMG-tutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_heratepotentiaali_enmg.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_heratepotentiaali_enmg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_heratepotentiaali_enmg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def knf_iom_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="IOM")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_iom.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_iom_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_iom_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def knf_laite_sahkoturvallisuus_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Laite- ja sähköturvallisuus")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_laite_sahkoturvallisuus.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_laite_sahkoturvallisuus_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_laite_sahkoturvallisuus_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def knf_sarja_tms_hoidot_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Sarja-TMS-hoidot ja navigoidut TMS-tutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_sarja_tms_hoidot.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_sarja_tms_hoidot_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_sarja_tms_hoidot_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def knf_uni_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="KNF")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Uni")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/knf_uni.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_knf_uni_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_knf_uni_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Fysiologia sivujen näkymät

def fysiologia_ekg_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="EKG-tutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/fysiologia_ekg.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_fysiologia_ekg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_fysiologia_ekg_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def fysiologia_gi_kanava_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="GI-kanavan tutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/fysiologia_gi_kanava.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_fysiologia_gi_kanava_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def delete_fysiologia_gi_kanava_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def fysiologia_keuhkofunktio_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Keuhkofunktiotutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/fysiologia_keuhkofunktio.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_fysiologia_keuhkofunktio_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def edit_fysiologia_keuhkofunktio_section_view(request):
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
def delete_fysiologia_keuhkofunktio_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def fysiologia_luuston_mineraali_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Luuston mineraalitiheyden mittaus")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/fysiologia_luuston_mineraali.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_fysiologia_luuston_mineraali_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def edit_fysiologia_luuston_mineraali_section_view(request):
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
def delete_fysiologia_luuston_mineraali_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def fysiologia_verenkierto_view(request):
    specialty, _ = Specialty.objects.get_or_create(name="Fysiologia")
    epa, _ = EPA.objects.get_or_create(specialty=specialty, title="Verenkiertotutkimukset")
    sections = Section.objects.filter(epa=epa).order_by('order', 'id')
    return render(request, 'sisalto/fysiologia_verenkierto.html', {'epa': epa, 'sections': sections})

@csrf_exempt
def add_fysiologia_verenkierto_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get("title", "")
        content = data.get("content", "")
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
def edit_fysiologia_verenkierto_section_view(request):
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
def delete_fysiologia_verenkierto_section_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        section_id = data.get("id")
        section = Section.objects.filter(id=section_id).first()
        if section:
            section.delete()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})
