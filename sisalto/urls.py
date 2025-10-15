from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage_view, name='frontpage'),
    path('specialties/', views.specialty_list_view, name='specialty_list'),
    path('specialty/<int:specialty_id>/', views.specialty_detail_view, name='specialty_detail'),
    path('epa/<int:epa_id>/', views.epa_detail_view, name='epa_detail'),
    path('examquestions/', views.examquestion_list_view, name='examquestion_list'),
    path('exam/practice/', views.exam_practice_view, name='exam_practice'),
    path('exam/generate/', views.generate_exam_view, name='generate_exam'),
    path('exam/submit/', views.submit_exam_answers_view, name='submit_exam_answers'),
    path('epas/', views.epas_view, name='epas'),
    
    # EPA sivut
    path('radiologia_epas/', views.radiologia_epas_view, name='radiologia_epas'),
    path('radiologia_subpages/', views.radiologia_subpages_view, name='radiologia_subpages'),
    path('sadehoito_epas/', views.sadehoito_epas_view, name='sadehoito_epas'),
    path('isotooppi_epas/', views.isotooppi_epas_view, name='isotooppi_epas'),
    path('knf_epas/', views.knf_epas_view, name='knf_epas'),
    path('fysiologia_epas/', views.fysiologia_epas_view, name='fysiologia_epas'),
    
    # Radiologia sivut
    path('radiologia/lapivalaisu-angiografia/', views.radiologia_lapivalaisu_angiografia_view, name='radiologia_lapivalaisu_angiografia'),
    path('radiologia/lapivalaisu-angiografia/add_section/', views.add_radiologia_lapivalaisu_angiografia_section_view, name='add_radiologia_lapivalaisu_angiografia_section_view'),
    path('radiologia/lapivalaisu-angiografia/edit_section/', views.edit_radiologia_lapivalaisu_angiografia_section_view, name='edit_radiologia_lapivalaisu_angiografia_section_view'),
    path('radiologia/lapivalaisu-angiografia/delete_section/', views.delete_radiologia_lapivalaisu_angiografia_section_view, name='delete_radiologia_lapivalaisu_angiografia_section_view'),
    
    path('radiologia/magneettikuvaus/', views.radiologia_magneettikuvaus_view, name='radiologia_magneettikuvaus'),
    path('radiologia/magneettikuvaus/add_section/', views.add_magneettikuvaus_section_view, name='add_magneettikuvaus_section_view'),
    path('radiologia/magneettikuvaus/edit_section/', views.edit_magneettikuvaus_section_view, name='edit_magneettikuvaus_section_view'),
    path('radiologia/magneettikuvaus/delete_section/', views.delete_magneettikuvaus_section_view, name='delete_magneettikuvaus_section_view'),
    
    path('radiologia/mammografia/', views.radiologia_mammografia_view, name='radiologia_mammografia'),
    path('radiologia/mammografia/add_section/', views.add_mammografia_section_view, name='add_mammografia_section_view'),
    path('radiologia/mammografia/edit_section/', views.edit_mammografia_section_view, name='edit_mammografia_section_view'),
    path('radiologia/mammografia/delete_section/', views.delete_mammografia_section_view, name='delete_mammografia_section_view'),
    
    path('radiologia/natiivikuvantaminen/', views.radiologia_natiivikuvantaminen_view, name='radiologia_natiivikuvantaminen'),
    path('radiologia/natiivikuvantaminen/add_section/', views.add_natiivikuvantaminen_section_view, name='add_natiivikuvantaminen_section_view'),
    path('radiologia/natiivikuvantaminen/edit_section/', views.edit_natiivikuvantaminen_section_view, name='edit_natiivikuvantaminen_section_view'),
    path('radiologia/natiivikuvantaminen/delete_section/', views.delete_natiivikuvantaminen_section_view, name='delete_natiivikuvantaminen_section_view'),
    
    path('radiologia/tietokonetomografia/', views.radiologia_tietokonetomografia_view, name='radiologia_tietokonetomografia'),
    path('radiologia/tietokonetomografia/add_section/', views.add_tietokonetomografia_section_view, name='add_tietokonetomografia_section_view'),
    path('radiologia/tietokonetomografia/edit_section/', views.edit_tietokonetomografia_section_view, name='edit_tietokonetomografia_section_view'),
    path('radiologia/tietokonetomografia/delete_section/', views.delete_tietokonetomografia_section_view, name='delete_tietokonetomografia_section_view'),
    
    path('radiologia/ultraaani/', views.radiologia_ultraaani_view, name='radiologia_ultraaani'),
    path('radiologia/ultraaani/add_section/', views.add_ultraaani_section_view, name='add_ultraaani_section_view'),
    path('radiologia/ultraaani/edit_section/', views.edit_ultraaani_section_view, name='edit_ultraaani_section_view'),
    path('radiologia/ultraaani/delete_section/', views.delete_ultraaani_section_view, name='delete_ultraaani_section_view'),
    
    path('radiologia/kuvankatselunaytot/', views.radiologia_kuvankatselunaytot_view, name='radiologia_kuvankatselunaytot'),
    path('radiologia/kuvankatselunaytot/add_section/', views.add_kuvankatselunaytot_section_view, name='add_kuvankatselunaytot_section_view'),
    path('radiologia/kuvankatselunaytot/edit_section/', views.edit_kuvankatselunaytot_section_view, name='edit_kuvankatselunaytot_section_view'),
    path('radiologia/kuvankatselunaytot/delete_section/', views.delete_kuvankatselunaytot_section_view, name='delete_kuvankatselunaytot_section_view'),
    
    path('radiologia/hammaskuvantaminen/', views.radiologia_hammaskuvantaminen_view, name='radiologia_hammaskuvantaminen'),
    path('radiologia/hammaskuvantaminen/add_section/', views.add_hammaskuvantaminen_section_view, name='add_hammaskuvantaminen_section_view'),
    path('radiologia/hammaskuvantaminen/edit_section/', views.edit_hammaskuvantaminen_section_view, name='edit_hammaskuvantaminen_section_view'),
    path('radiologia/hammaskuvantaminen/delete_section/', views.delete_hammaskuvantaminen_section_view, name='delete_hammaskuvantaminen_section_view'),
    
    path('radiologia/sateilybiologia-suojelu/', views.radiologia_sateilybiologia_suojelu_view, name='radiologia_sateilybiologia_suojelu'),
    path('radiologia/sateilybiologia-suojelu/add_section/', views.add_radiologia_sateilybiologia_suojelu_section_view, name='add_radiologia_sateilybiologia_suojelu_section_view'),
    path('radiologia/sateilybiologia-suojelu/edit_section/', views.edit_radiologia_sateilybiologia_suojelu_section_view, name='edit_radiologia_sateilybiologia_suojelu_section_view'),
    path('radiologia/sateilybiologia-suojelu/delete_section/', views.delete_radiologia_sateilybiologia_suojelu_section_view, name='delete_radiologia_sateilybiologia_suojelu_section_view'),
    
    # Sädehoito sivut  
    path('sadehoito/peruskasitteet/', views.sadehoito_peruskasitteet_view, name='sadehoito_peruskasitteet'),
    path('sadehoito/peruskasitteet/add_section/', views.add_sadehoito_peruskasitteet_section_view, name='add_sadehoito_peruskasitteet_section_view'),
    path('sadehoito/peruskasitteet/edit_section/', views.edit_sadehoito_peruskasitteet_section_view, name='edit_sadehoito_peruskasitteet_section_view'),
    path('sadehoito/peruskasitteet/delete_section/', views.delete_sadehoito_peruskasitteet_section_view, name='delete_sadehoito_peruskasitteet_section_view'),
    
    path('sadehoito/kuvantaminen_suunnittelu/', views.sadehoito_kuvantaminen_suunnittelu_view, name='sadehoito_kuvantaminen_suunnittelu'),
    path('sadehoito/kuvantaminen_suunnittelu/add_section/', views.add_sadehoito_kuvantaminen_suunnittelu_section_view, name='add_sadehoito_kuvantaminen_suunnittelu_section_view'),
    path('sadehoito/kuvantaminen_suunnittelu/edit_section/', views.edit_sadehoito_kuvantaminen_suunnittelu_section_view, name='edit_sadehoito_kuvantaminen_suunnittelu_section_view'),
    path('sadehoito/kuvantaminen_suunnittelu/delete_section/', views.delete_sadehoito_kuvantaminen_suunnittelu_section_view, name='delete_sadehoito_kuvantaminen_suunnittelu_section_view'),
    
    path('sadehoito/ulkoinen/', views.sadehoito_ulkoinen_view, name='sadehoito_ulkoinen'),
    path('sadehoito/ulkoinen/add_section/', views.add_sadehoito_ulkoinen_section_view, name='add_sadehoito_ulkoinen_section_view'),
    path('sadehoito/ulkoinen/edit_section/', views.edit_sadehoito_ulkoinen_section_view, name='edit_sadehoito_ulkoinen_section_view'),
    path('sadehoito/ulkoinen/delete_section/', views.delete_sadehoito_ulkoinen_section_view, name='delete_sadehoito_ulkoinen_section_view'),
    
    path('sadehoito/sisainen/', views.sadehoito_sisainen_view, name='sadehoito_sisainen'),
    path('sadehoito/sisainen/add_section/', views.add_sadehoito_sisainen_section_view, name='add_sadehoito_sisainen_section_view'),
    path('sadehoito/sisainen/edit_section/', views.edit_sadehoito_sisainen_section_view, name='edit_sadehoito_sisainen_section_view'),
    path('sadehoito/sisainen/delete_section/', views.delete_sadehoito_sisainen_section_view, name='delete_sadehoito_sisainen_section_view'),
    
    path('sadehoito/dosimetria/', views.sadehoito_dosimetria_view, name='sadehoito_dosimetria'),
    path('sadehoito/dosimetria/add_section/', views.add_sadehoito_dosimetria_section_view, name='add_sadehoito_dosimetria_section_view'),
    path('sadehoito/dosimetria/edit_section/', views.edit_sadehoito_dosimetria_section_view, name='edit_sadehoito_dosimetria_section_view'),
    path('sadehoito/dosimetria/delete_section/', views.delete_sadehoito_dosimetria_section_view, name='delete_sadehoito_dosimetria_section_view'),
    
    path('sadehoito/laitteet/', views.sadehoito_laitteet_view, name='sadehoito_laitteet'),
    path('sadehoito/laitteet/add_section/', views.add_sadehoito_laitteet_section_view, name='add_sadehoito_laitteet_section_view'),
    path('sadehoito/laitteet/edit_section/', views.edit_sadehoito_laitteet_section_view, name='edit_sadehoito_laitteet_section_view'),
    path('sadehoito/laitteet/delete_section/', views.delete_sadehoito_laitteet_section_view, name='delete_sadehoito_laitteet_section_view'),
    
    path('sadehoito/sateilybiologia/', views.sadehoito_sateilybiologia_view, name='sadehoito_sateilybiologia'),
    path('sadehoito/sateilybiologia/add_section/', views.add_sadehoito_sateilybiologia_section_view, name='add_sadehoito_sateilybiologia_section_view'),
    path('sadehoito/sateilybiologia/edit_section/', views.edit_sadehoito_sateilybiologia_section_view, name='edit_sadehoito_sateilybiologia_section_view'),
    path('sadehoito/sateilybiologia/delete_section/', views.delete_sadehoito_sateilybiologia_section_view, name='delete_sadehoito_sateilybiologia_section_view'),
    
    # Isotooppi sivut
    path('isotooppi/gammakamera/', views.isotooppi_gammakamera_view, name='isotooppi_gammakamera'),
    path('isotooppi/gammakamera/add_section/', views.add_isotooppi_gammakamera_section_view, name='add_isotooppi_gammakamera_section_view'),
    path('isotooppi/gammakamera/edit_section/', views.edit_isotooppi_gammakamera_section_view, name='edit_isotooppi_gammakamera_section_view'),
    path('isotooppi/gammakamera/delete_section/', views.delete_isotooppi_gammakamera_section_view, name='delete_isotooppi_gammakamera_section_view'),
    
    path('isotooppi/petkamera/', views.isotooppi_petkamera_view, name='isotooppi_petkamera'),
    path('isotooppi/petkamera/add_section/', views.add_isotooppi_petkamera_section_view, name='add_isotooppi_petkamera_section_view'),
    path('isotooppi/petkamera/edit_section/', views.edit_isotooppi_petkamera_section_view, name='edit_isotooppi_petkamera_section_view'),
    path('isotooppi/petkamera/delete_section/', views.delete_isotooppi_petkamera_section_view, name='delete_isotooppi_petkamera_section_view'),
    
    path('isotooppi/annostelu_radiofarmasia/', views.isotooppi_annostelu_radiofarmasia_view, name='isotooppi_annostelu_radiofarmasia'),
    path('isotooppi/annostelu_radiofarmasia/add_section/', views.add_isotooppi_annostelu_radiofarmasia_section_view, name='add_isotooppi_annostelu_radiofarmasia_section_view'),
    path('isotooppi/annostelu_radiofarmasia/edit_section/', views.edit_isotooppi_annostelu_radiofarmasia_section_view, name='edit_isotooppi_annostelu_radiofarmasia_section_view'),
    path('isotooppi/annostelu_radiofarmasia/delete_section/', views.delete_isotooppi_annostelu_radiofarmasia_section_view, name='delete_isotooppi_annostelu_radiofarmasia_section_view'),
    
    path('isotooppi/gammakuvaus_spet/', views.isotooppi_gammakuvaus_spet_view, name='isotooppi_gammakuvaus_spet'),
    path('isotooppi/gammakuvaus_spet/add_section/', views.add_isotooppi_gammakuvaus_spet_section_view, name='add_isotooppi_gammakuvaus_spet_section_view'),
    path('isotooppi/gammakuvaus_spet/edit_section/', views.edit_isotooppi_gammakuvaus_spet_section_view, name='edit_isotooppi_gammakuvaus_spet_section_view'),
    path('isotooppi/gammakuvaus_spet/delete_section/', views.delete_isotooppi_gammakuvaus_spet_section_view, name='delete_isotooppi_gammakuvaus_spet_section_view'),
    
    path('isotooppi/pet_tutkimukset/', views.isotooppi_pet_tutkimukset_view, name='isotooppi_pet_tutkimukset'),
    path('isotooppi/pet_tutkimukset/add_section/', views.add_isotooppi_pet_tutkimukset_section_view, name='add_isotooppi_pet_tutkimukset_section_view'),
    path('isotooppi/pet_tutkimukset/edit_section/', views.edit_isotooppi_pet_tutkimukset_section_view, name='edit_isotooppi_pet_tutkimukset_section_view'),
    path('isotooppi/pet_tutkimukset/delete_section/', views.delete_isotooppi_pet_tutkimukset_section_view, name='delete_isotooppi_pet_tutkimukset_section_view'),
    
    path('isotooppi/radionuklidihoidot/', views.isotooppi_radionuklidihoidot_view, name='isotooppi_radionuklidihoidot'),
    path('isotooppi/radionuklidihoidot/add_section/', views.add_isotooppi_radionuklidihoidot_section_view, name='add_isotooppi_radionuklidihoidot_section_view'),
    path('isotooppi/radionuklidihoidot/edit_section/', views.edit_isotooppi_radionuklidihoidot_section_view, name='edit_isotooppi_radionuklidihoidot_section_view'),
    path('isotooppi/radionuklidihoidot/delete_section/', views.delete_isotooppi_radionuklidihoidot_section_view, name='delete_isotooppi_radionuklidihoidot_section_view'),
    
    path('isotooppi/sateilybiologia_suojelu/', views.isotooppi_sateilybiologia_suojelu_view, name='isotooppi_sateilybiologia_suojelu'),
    path('isotooppi/sateilybiologia_suojelu/add_section/', views.add_isotooppi_sateilybiologia_suojelu_section_view, name='add_isotooppi_sateilybiologia_suojelu_section_view'),
    path('isotooppi/sateilybiologia_suojelu/edit_section/', views.edit_isotooppi_sateilybiologia_suojelu_section_view, name='edit_isotooppi_sateilybiologia_suojelu_section_view'),
    path('isotooppi/sateilybiologia_suojelu/delete_section/', views.delete_isotooppi_sateilybiologia_suojelu_section_view, name='delete_isotooppi_sateilybiologia_suojelu_section_view'),
    
    # KNF sivut
    path('knf/eeg/', views.knf_eeg_view, name='knf_eeg'),
    path('knf/eeg/add_section/', views.add_knf_eeg_section_view, name='add_knf_eeg_section_view'),
    path('knf/eeg/edit_section/', views.edit_knf_eeg_section_view, name='edit_knf_eeg_section_view'),
    path('knf/eeg/delete_section/', views.delete_knf_eeg_section_view, name='delete_knf_eeg_section_view'),
    
    path('knf/heratepotentiaali_enmg/', views.knf_heratepotentiaali_enmg_view, name='knf_heratepotentiaali_enmg'),
    path('knf/heratepotentiaali_enmg/add_section/', views.add_knf_heratepotentiaali_enmg_section_view, name='add_knf_heratepotentiaali_enmg_section_view'),
    path('knf/heratepotentiaali_enmg/edit_section/', views.edit_knf_heratepotentiaali_enmg_section_view, name='edit_knf_heratepotentiaali_enmg_section_view'),
    path('knf/heratepotentiaali_enmg/delete_section/', views.delete_knf_heratepotentiaali_enmg_section_view, name='delete_knf_heratepotentiaali_enmg_section_view'),
    
    path('knf/iom/', views.knf_iom_view, name='knf_iom'),
    path('knf/iom/add_section/', views.add_knf_iom_section_view, name='add_knf_iom_section_view'),
    path('knf/iom/edit_section/', views.edit_knf_iom_section_view, name='edit_knf_iom_section_view'),
    path('knf/iom/delete_section/', views.delete_knf_iom_section_view, name='delete_knf_iom_section_view'),
    
    path('knf/laite_sahkoturvallisuus/', views.knf_laite_sahkoturvallisuus_view, name='knf_laite_sahkoturvallisuus'),
    path('knf/laite_sahkoturvallisuus/add_section/', views.add_knf_laite_sahkoturvallisuus_section_view, name='add_knf_laite_sahkoturvallisuus_section_view'),
    path('knf/laite_sahkoturvallisuus/edit_section/', views.edit_knf_laite_sahkoturvallisuus_section_view, name='edit_knf_laite_sahkoturvallisuus_section_view'),
    path('knf/laite_sahkoturvallisuus/delete_section/', views.delete_knf_laite_sahkoturvallisuus_section_view, name='delete_knf_laite_sahkoturvallisuus_section_view'),
    
    path('knf/sarja_tms_hoidot/', views.knf_sarja_tms_hoidot_view, name='knf_sarja_tms_hoidot'),
    path('knf/sarja_tms_hoidot/add_section/', views.add_knf_sarja_tms_hoidot_section_view, name='add_knf_sarja_tms_hoidot_section_view'),
    path('knf/sarja_tms_hoidot/edit_section/', views.edit_knf_sarja_tms_hoidot_section_view, name='edit_knf_sarja_tms_hoidot_section_view'),
    path('knf/sarja_tms_hoidot/delete_section/', views.delete_knf_sarja_tms_hoidot_section_view, name='delete_knf_sarja_tms_hoidot_section_view'),
    
    path('knf/uni/', views.knf_uni_view, name='knf_uni'),
    path('knf/uni/add_section/', views.add_knf_uni_section_view, name='add_knf_uni_section_view'),
    path('knf/uni/edit_section/', views.edit_knf_uni_section_view, name='edit_knf_uni_section_view'),
    path('knf/uni/delete_section/', views.delete_knf_uni_section_view, name='delete_knf_uni_section_view'),
    
    # Fysiologia sivut
    path('fysiologia/ekg/', views.fysiologia_ekg_view, name='fysiologia_ekg'),
    path('fysiologia/ekg/add_section/', views.add_fysiologia_ekg_section_view, name='add_fysiologia_ekg_section_view'),
    path('fysiologia/ekg/edit_section/', views.edit_fysiologia_ekg_section_view, name='edit_fysiologia_ekg_section_view'),
    path('fysiologia/ekg/delete_section/', views.delete_fysiologia_ekg_section_view, name='delete_fysiologia_ekg_section_view'),
    
    path('fysiologia/gi_kanava/', views.fysiologia_gi_kanava_view, name='fysiologia_gi_kanava'),
    path('fysiologia/gi_kanava/add_section/', views.add_fysiologia_gi_kanava_section_view, name='add_fysiologia_gi_kanava_section_view'),
    path('fysiologia/gi_kanava/edit_section/', views.edit_fysiologia_gi_kanava_section_view, name='edit_fysiologia_gi_kanava_section_view'),
    path('fysiologia/gi_kanava/delete_section/', views.delete_fysiologia_gi_kanava_section_view, name='delete_fysiologia_gi_kanava_section_view'),
    
    # Image upload for CKEditor
    path('upload-image/', views.upload_image_view, name='upload_image'),
]