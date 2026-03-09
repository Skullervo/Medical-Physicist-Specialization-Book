from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage_view, name='frontpage'),
    path('specialties/', views.specialty_list_view, name='specialty_list'),
    path('specialty/<int:specialty_id>/', views.specialty_detail_view, name='specialty_detail'),
    path('epa/<int:epa_id>/', views.epa_detail_view, name='epa_detail'),
    path('epa/<int:epa_id>/add_section/', views.generic_add_section_view, name='generic_add_section'),
    path('epa/<int:epa_id>/edit_section/', views.generic_edit_section_view, name='generic_edit_section'),
    path('epa/<int:epa_id>/delete_section/', views.generic_delete_section_view, name='generic_delete_section'),
    path('epa/<int:epa_id>/update_proficiency/', views.generic_update_proficiency_view, name='generic_update_proficiency'),
    path('examquestions/', views.examquestion_list_view, name='examquestion_list'),
    path('examquestions/<str:area_slug>/', views.examquestion_area_view, name='examquestion_area'),
    path('table-questions/', views.table_questions_view, name='table_questions'),
    path('exam/practice/', views.exam_practice_view, name='exam_practice'),
    path('exam/generate/', views.generate_exam_view, name='generate_exam'),
    path('exam/submit/', views.submit_exam_answers_view, name='submit_exam_answers'),
    path('exam/ai-evaluate/', views.ai_evaluate_exam_answer, name='ai_evaluate_exam_answer'),
    path('api/tutor/chat/', views.ai_tutor_chat, name='ai_tutor_chat'),
    path('search/', views.search_view, name='search'),
    path('epas/', views.epas_view, name='epas'),
    path('modaliteetit/', views.modaliteetit_view, name='modaliteetit'),
    path('modaliteetit/radiologia/', views.modaliteetit_radiologia_view, name='modaliteetit_radiologia'),
    path('modaliteetit/sadehoito/', views.modaliteetit_sadehoito_view, name='modaliteetit_sadehoito'),
    path('modaliteetit/isotooppi/', views.modaliteetit_isotooppi_view, name='modaliteetit_isotooppi'),
    path('modaliteetit/fysiologia/', views.modaliteetit_fysiologia_view, name='modaliteetit_fysiologia'),
    path('modaliteetit/knf/', views.modaliteetit_knf_view, name='modaliteetit_knf'),
    path('modaliteetit/api/question/<int:epa_id>/', views.theory_quiz_question, name='theory_quiz_question'),
    path('modaliteetit/api/answer/', views.theory_quiz_answer, name='theory_quiz_answer'),
    
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
    path('radiologia/lapivalaisu-angiografia/update_proficiency/', views.update_radiologia_lapivalaisu_angiografia_proficiency_view, name='update_radiologia_lapivalaisu_angiografia_proficiency_view'),
    
    path('radiologia/magneettikuvaus/', views.radiologia_magneettikuvaus_view, name='radiologia_magneettikuvaus'),
    path('radiologia/magneettikuvaus/add_section/', views.add_magneettikuvaus_section_view, name='add_magneettikuvaus_section_view'),
    path('radiologia/magneettikuvaus/edit_section/', views.edit_magneettikuvaus_section_view, name='edit_magneettikuvaus_section_view'),
    path('radiologia/magneettikuvaus/delete_section/', views.delete_magneettikuvaus_section_view, name='delete_magneettikuvaus_section_view'),
    path('radiologia/magneettikuvaus/update_proficiency/', views.update_magneettikuvaus_proficiency_view, name='update_magneettikuvaus_proficiency_view'),
    
    path('radiologia/mammografia/', views.radiologia_mammografia_view, name='radiologia_mammografia'),
    path('radiologia/mammografia/add_section/', views.add_mammografia_section_view, name='add_mammografia_section_view'),
    path('radiologia/mammografia/edit_section/', views.edit_mammografia_section_view, name='edit_mammografia_section_view'),
    path('radiologia/mammografia/delete_section/', views.delete_mammografia_section_view, name='delete_mammografia_section_view'),
    path('radiologia/mammografia/update_proficiency/', views.update_mammografia_proficiency_view, name='update_mammografia_proficiency_view'),
    
    path('radiologia/natiivikuvantaminen/', views.radiologia_natiivikuvantaminen_view, name='radiologia_natiivikuvantaminen'),
    path('radiologia/natiivikuvantaminen/add_section/', views.add_natiivikuvantaminen_section_view, name='add_natiivikuvantaminen_section_view'),
    path('radiologia/natiivikuvantaminen/edit_section/', views.edit_natiivikuvantaminen_section_view, name='edit_natiivikuvantaminen_section_view'),
    path('radiologia/natiivikuvantaminen/delete_section/', views.delete_natiivikuvantaminen_section_view, name='delete_natiivikuvantaminen_section_view'),
    path('radiologia/natiivikuvantaminen/update_proficiency/', views.update_natiivikuvantaminen_proficiency_view, name='update_natiivikuvantaminen_proficiency_view'),
    
    path('radiologia/tietokonetomografia/', views.radiologia_tietokonetomografia_view, name='radiologia_tietokonetomografia'),
    path('radiologia/tietokonetomografia/add_section/', views.add_tietokonetomografia_section_view, name='add_tietokonetomografia_section_view'),
    path('radiologia/tietokonetomografia/edit_section/', views.edit_tietokonetomografia_section_view, name='edit_tietokonetomografia_section_view'),
    path('radiologia/tietokonetomografia/delete_section/', views.delete_tietokonetomografia_section_view, name='delete_tietokonetomografia_section_view'),
    path('radiologia/tietokonetomografia/update_proficiency/', views.update_tietokonetomografia_proficiency_view, name='update_tietokonetomografia_proficiency_view'),
    
    path('radiologia/ultraaani/', views.radiologia_ultraaani_view, name='radiologia_ultraaani'),
    path('radiologia/ultraaani/add_section/', views.add_ultraaani_section_view, name='add_ultraaani_section_view'),
    path('radiologia/ultraaani/edit_section/', views.edit_ultraaani_section_view, name='edit_ultraaani_section_view'),
    path('radiologia/ultraaani/delete_section/', views.delete_ultraaani_section_view, name='delete_ultraaani_section_view'),
    path('radiologia/ultraaani/update_proficiency/', views.update_ultraaani_proficiency_view, name='update_ultraaani_proficiency_view'),
    
    path('radiologia/kuvankatselunaytot/', views.radiologia_kuvankatselunaytot_view, name='radiologia_kuvankatselunaytot'),
    path('radiologia/kuvankatselunaytot/add_section/', views.add_kuvankatselunaytot_section_view, name='add_kuvankatselunaytot_section_view'),
    path('radiologia/kuvankatselunaytot/edit_section/', views.edit_kuvankatselunaytot_section_view, name='edit_kuvankatselunaytot_section_view'),
    path('radiologia/kuvankatselunaytot/delete_section/', views.delete_kuvankatselunaytot_section_view, name='delete_kuvankatselunaytot_section_view'),
    path('radiologia/kuvankatselunaytot/update_proficiency/', views.update_kuvankatselunaytot_proficiency_view, name='update_kuvankatselunaytot_proficiency_view'),
    
    path('radiologia/hammaskuvantaminen/', views.radiologia_hammaskuvantaminen_view, name='radiologia_hammaskuvantaminen'),
    path('radiologia/hammaskuvantaminen/add_section/', views.add_hammaskuvantaminen_section_view, name='add_hammaskuvantaminen_section_view'),
    path('radiologia/hammaskuvantaminen/edit_section/', views.edit_hammaskuvantaminen_section_view, name='edit_hammaskuvantaminen_section_view'),
    path('radiologia/hammaskuvantaminen/delete_section/', views.delete_hammaskuvantaminen_section_view, name='delete_hammaskuvantaminen_section_view'),
    path('radiologia/hammaskuvantaminen/update_proficiency/', views.update_hammaskuvantaminen_proficiency_view, name='update_hammaskuvantaminen_proficiency_view'),
    
    path('radiologia/sateilybiologia_suojelu/', views.radiologia_sateilybiologia_suojelu_view, name='radiologia_sateilybiologia_suojelu'),
    path('radiologia/sateilybiologia_suojelu/add_section/', views.add_radiologia_sateilybiologia_suojelu_section_view, name='add_radiologia_sateilybiologia_suojelu_section_view'),
    path('radiologia/sateilybiologia_suojelu/edit_section/', views.edit_radiologia_sateilybiologia_suojelu_section_view, name='edit_radiologia_sateilybiologia_suojelu_section_view'),
    path('radiologia/sateilybiologia_suojelu/delete_section/', views.delete_radiologia_sateilybiologia_suojelu_section_view, name='delete_radiologia_sateilybiologia_suojelu_section_view'),
    path('radiologia/sateilybiologia_suojelu/update_proficiency/', views.update_radiologia_sateilybiologia_suojelu_proficiency_view, name='update_radiologia_sateilybiologia_suojelu_proficiency_view'),
    
    # Sädehoito sivut  
    path('sadehoito/peruskasitteet/', views.sadehoito_peruskasitteet_view, name='sadehoito_peruskasitteet'),
    path('sadehoito/peruskasitteet/add_section/', views.add_sadehoito_peruskasitteet_section_view, name='add_sadehoito_peruskasitteet_section_view'),
    path('sadehoito/peruskasitteet/edit_section/', views.edit_sadehoito_peruskasitteet_section_view, name='edit_sadehoito_peruskasitteet_section_view'),
    path('sadehoito/peruskasitteet/delete_section/', views.delete_sadehoito_peruskasitteet_section_view, name='delete_sadehoito_peruskasitteet_section_view'),
    path('sadehoito/peruskasitteet/update_proficiency/', views.update_sadehoito_peruskasitteet_proficiency_view, name='update_sadehoito_peruskasitteet_proficiency_view'),
    
    path('sadehoito/kuvantaminen_suunnittelu/', views.sadehoito_kuvantaminen_suunnittelu_view, name='sadehoito_kuvantaminen_suunnittelu'),
    path('sadehoito/kuvantaminen_suunnittelu/add_section/', views.add_sadehoito_kuvantaminen_suunnittelu_section_view, name='add_sadehoito_kuvantaminen_suunnittelu_section_view'),
    path('sadehoito/kuvantaminen_suunnittelu/edit_section/', views.edit_sadehoito_kuvantaminen_suunnittelu_section_view, name='edit_sadehoito_kuvantaminen_suunnittelu_section_view'),
    path('sadehoito/kuvantaminen_suunnittelu/delete_section/', views.delete_sadehoito_kuvantaminen_suunnittelu_section_view, name='delete_sadehoito_kuvantaminen_suunnittelu_section_view'),
    path('sadehoito/kuvantaminen_suunnittelu/update_proficiency/', views.update_sadehoito_kuvantaminen_suunnittelu_proficiency_view, name='update_sadehoito_kuvantaminen_suunnittelu_proficiency_view'),
    
    path('sadehoito/ulkoinen/', views.sadehoito_ulkoinen_view, name='sadehoito_ulkoinen'),
    path('sadehoito/ulkoinen/add_section/', views.add_sadehoito_ulkoinen_section_view, name='add_sadehoito_ulkoinen_section_view'),
    path('sadehoito/ulkoinen/edit_section/', views.edit_sadehoito_ulkoinen_section_view, name='edit_sadehoito_ulkoinen_section_view'),
    path('sadehoito/ulkoinen/delete_section/', views.delete_sadehoito_ulkoinen_section_view, name='delete_sadehoito_ulkoinen_section_view'),
    path('sadehoito/ulkoinen/update_proficiency/', views.update_sadehoito_ulkoinen_proficiency_view, name='update_sadehoito_ulkoinen_proficiency_view'),
    
    path('sadehoito/sisainen/', views.sadehoito_sisainen_view, name='sadehoito_sisainen'),
    path('sadehoito/sisainen/add_section/', views.add_sadehoito_sisainen_section_view, name='add_sadehoito_sisainen_section_view'),
    path('sadehoito/sisainen/edit_section/', views.edit_sadehoito_sisainen_section_view, name='edit_sadehoito_sisainen_section_view'),
    path('sadehoito/sisainen/delete_section/', views.delete_sadehoito_sisainen_section_view, name='delete_sadehoito_sisainen_section_view'),
    path('sadehoito/sisainen/update_proficiency/', views.update_sadehoito_sisainen_proficiency_view, name='update_sadehoito_sisainen_proficiency_view'),
    
    path('sadehoito/dosimetria/', views.sadehoito_dosimetria_view, name='sadehoito_dosimetria'),
    path('sadehoito/dosimetria/add_section/', views.add_sadehoito_dosimetria_section_view, name='add_sadehoito_dosimetria_section_view'),
    path('sadehoito/dosimetria/edit_section/', views.edit_sadehoito_dosimetria_section_view, name='edit_sadehoito_dosimetria_section_view'),
    path('sadehoito/dosimetria/delete_section/', views.delete_sadehoito_dosimetria_section_view, name='delete_sadehoito_dosimetria_section_view'),
    path('sadehoito/dosimetria/update_proficiency/', views.update_sadehoito_dosimetria_proficiency_view, name='update_sadehoito_dosimetria_proficiency_view'),
    
    path('sadehoito/laitteet/', views.sadehoito_laitteet_view, name='sadehoito_laitteet'),
    path('sadehoito/laitteet/add_section/', views.add_sadehoito_laitteet_section_view, name='add_sadehoito_laitteet_section_view'),
    path('sadehoito/laitteet/edit_section/', views.edit_sadehoito_laitteet_section_view, name='edit_sadehoito_laitteet_section_view'),
    path('sadehoito/laitteet/delete_section/', views.delete_sadehoito_laitteet_section_view, name='delete_sadehoito_laitteet_section_view'),
    path('sadehoito/laitteet/update_proficiency/', views.update_sadehoito_laitteet_proficiency_view, name='update_sadehoito_laitteet_proficiency_view'),
    
    path('sadehoito/sateilybiologia/', views.sadehoito_sateilybiologia_view, name='sadehoito_sateilybiologia'),
    path('sadehoito/sateilybiologia/add_section/', views.add_sadehoito_sateilybiologia_section_view, name='add_sadehoito_sateilybiologia_section_view'),
    path('sadehoito/sateilybiologia/edit_section/', views.edit_sadehoito_sateilybiologia_section_view, name='edit_sadehoito_sateilybiologia_section_view'),
    path('sadehoito/sateilybiologia/delete_section/', views.delete_sadehoito_sateilybiologia_section_view, name='delete_sadehoito_sateilybiologia_section_view'),
    path('sadehoito/sateilybiologia/update_proficiency/', views.update_sadehoito_sateilybiologia_proficiency_view, name='update_sadehoito_sateilybiologia_proficiency_view'),
    
    # Isotooppi sivut
    path('isotooppi/gammakamera/', views.isotooppi_gammakamera_view, name='isotooppi_gammakamera'),
    path('isotooppi/gammakamera/add_section/', views.add_isotooppi_gammakamera_section_view, name='add_isotooppi_gammakamera_section_view'),
    path('isotooppi/gammakamera/edit_section/', views.edit_isotooppi_gammakamera_section_view, name='edit_isotooppi_gammakamera_section_view'),
    path('isotooppi/gammakamera/delete_section/', views.delete_isotooppi_gammakamera_section_view, name='delete_isotooppi_gammakamera_section_view'),
    path('isotooppi/gammakamera/update_proficiency/', views.update_isotooppi_gammakamera_proficiency_view, name='update_isotooppi_gammakamera_proficiency_view'),


    path('isotooppi/pet_kamera/', views.isotooppi_pet_kamera_view, name='isotooppi_pet_kamera'),
    path('isotooppi/pet_kamera/add_section/', views.add_isotooppi_pet_kamera_section_view, name='add_isotooppi_pet_kamera_section_view'),
    path('isotooppi/pet_kamera/edit_section/', views.edit_isotooppi_pet_kamera_section_view, name='edit_isotooppi_pet_kamera_section_view'),
    path('isotooppi/pet_kamera/delete_section/', views.delete_isotooppi_pet_kamera_section_view, name='delete_isotooppi_pet_kamera_section_view'),
    path('isotooppi/pet_kamera/update_proficiency/', views.update_isotooppi_pet_kamera_proficiency_view, name='update_isotooppi_pet_kamera_proficiency_view'),

    path('isotooppi/annostelu_radiofarmasia/', views.isotooppi_annostelu_radiofarmasia_view, name='isotooppi_annostelu_radiofarmasia'),
    path('isotooppi/annostelu_radiofarmasia/add_section/', views.add_isotooppi_annostelu_radiofarmasia_section_view, name='add_isotooppi_annostelu_radiofarmasia_section_view'),
    path('isotooppi/annostelu_radiofarmasia/edit_section/', views.edit_isotooppi_annostelu_radiofarmasia_section_view, name='edit_isotooppi_annostelu_radiofarmasia_section_view'),
    path('isotooppi/annostelu_radiofarmasia/delete_section/', views.delete_isotooppi_annostelu_radiofarmasia_section_view, name='delete_isotooppi_annostelu_radiofarmasia_section_view'),
    path('isotooppi/annostelu_radiofarmasia/update_proficiency/', views.update_isotooppi_annostelu_radiofarmasia_proficiency_view, name='update_isotooppi_annostelu_radiofarmasia_proficiency_view'),
    
    path('isotooppi/gammakuvaus_spet/', views.isotooppi_gammakuvaus_spet_view, name='isotooppi_gammakuvaus_spet'),
    path('isotooppi/gammakuvaus_spet/add_section/', views.add_isotooppi_gammakuvaus_spet_section_view, name='add_isotooppi_gammakuvaus_spet_section_view'),
    path('isotooppi/gammakuvaus_spet/edit_section/', views.edit_isotooppi_gammakuvaus_spet_section_view, name='edit_isotooppi_gammakuvaus_spet_section_view'),
    path('isotooppi/gammakuvaus_spet/delete_section/', views.delete_isotooppi_gammakuvaus_spet_section_view, name='delete_isotooppi_gammakuvaus_spet_section_view'),
    path('isotooppi/gammakuvaus_spet/update_proficiency/', views.update_isotooppi_gammakuvaus_spet_proficiency_view, name='update_isotooppi_gammakuvaus_spet_proficiency_view'),
    
    path('isotooppi/pet_tutkimukset/', views.isotooppi_pet_tutkimukset_view, name='isotooppi_pet_tutkimukset'),
    path('isotooppi/pet_tutkimukset/add_section/', views.add_isotooppi_pet_tutkimukset_section_view, name='add_isotooppi_pet_tutkimukset_section_view'),
    path('isotooppi/pet_tutkimukset/edit_section/', views.edit_isotooppi_pet_tutkimukset_section_view, name='edit_isotooppi_pet_tutkimukset_section_view'),
    path('isotooppi/pet_tutkimukset/delete_section/', views.delete_isotooppi_pet_tutkimukset_section_view, name='delete_isotooppi_pet_tutkimukset_section_view'),
    path('isotooppi/pet_tutkimukset/update_proficiency/', views.update_isotooppi_pet_tutkimukset_proficiency_view, name='update_isotooppi_pet_tutkimukset_proficiency_view'),
    
    path('isotooppi/radionuklidihoidot/', views.isotooppi_radionuklidihoidot_view, name='isotooppi_radionuklidihoidot'),
    path('isotooppi/radionuklidihoidot/add_section/', views.add_isotooppi_radionuklidihoidot_section_view, name='add_isotooppi_radionuklidihoidot_section_view'),
    path('isotooppi/radionuklidihoidot/edit_section/', views.edit_isotooppi_radionuklidihoidot_section_view, name='edit_isotooppi_radionuklidihoidot_section_view'),
    path('isotooppi/radionuklidihoidot/delete_section/', views.delete_isotooppi_radionuklidihoidot_section_view, name='delete_isotooppi_radionuklidihoidot_section_view'),
    path('isotooppi/radionuklidihoidot/update_proficiency/', views.update_isotooppi_radionuklidihoidot_proficiency_view, name='update_isotooppi_radionuklidihoidot_proficiency_view'),
    
    path('isotooppi/sateilybiologia_suojelu/', views.isotooppi_sateilybiologia_suojelu_view, name='isotooppi_sateilybiologia_suojelu'),
    path('isotooppi/sateilybiologia_suojelu/add_section/', views.add_isotooppi_sateilybiologia_suojelu_section_view, name='add_isotooppi_sateilybiologia_suojelu_section_view'),
    path('isotooppi/sateilybiologia_suojelu/edit_section/', views.edit_isotooppi_sateilybiologia_suojelu_section_view, name='edit_isotooppi_sateilybiologia_suojelu_section_view'),
    path('isotooppi/sateilybiologia_suojelu/delete_section/', views.delete_isotooppi_sateilybiologia_suojelu_section_view, name='delete_isotooppi_sateilybiologia_suojelu_section_view'),
    path('isotooppi/sateilybiologia_suojelu/update_proficiency/', views.update_isotooppi_sateilybiologia_suojelu_proficiency_view, name='update_isotooppi_sateilybiologia_suojelu_proficiency_view'),
    
    # KNF sivut
    path('knf/eeg/', views.knf_eeg_view, name='knf_eeg'),
    path('knf/eeg/add_section/', views.add_knf_eeg_section_view, name='add_knf_eeg_section_view'),
    path('knf/eeg/edit_section/', views.edit_knf_eeg_section_view, name='edit_knf_eeg_section_view'),
    path('knf/eeg/delete_section/', views.delete_knf_eeg_section_view, name='delete_knf_eeg_section_view'),
    path('knf/eeg/update_proficiency/', views.update_knf_eeg_proficiency_view, name='update_knf_eeg_proficiency_view'),
    
    path('knf/heratepotentiaali_enmg/', views.knf_heratepotentiaali_enmg_view, name='knf_heratepotentiaali_enmg'),
    path('knf/heratepotentiaali_enmg/add_section/', views.add_knf_heratepotentiaali_enmg_section_view, name='add_knf_heratepotentiaali_enmg_section_view'),
    path('knf/heratepotentiaali_enmg/edit_section/', views.edit_knf_heratepotentiaali_enmg_section_view, name='edit_knf_heratepotentiaali_enmg_section_view'),
    path('knf/heratepotentiaali_enmg/delete_section/', views.delete_knf_heratepotentiaali_enmg_section_view, name='delete_knf_heratepotentiaali_enmg_section_view'),
    path('knf/heratepotentiaali_enmg/update_proficiency/', views.update_knf_heratepotentiaali_enmg_proficiency_view, name='update_knf_heratepotentiaali_enmg_proficiency_view'),
    
    path('knf/iom/', views.knf_iom_view, name='knf_iom'),
    path('knf/iom/add_section/', views.add_knf_iom_section_view, name='add_knf_iom_section_view'),
    path('knf/iom/edit_section/', views.edit_knf_iom_section_view, name='edit_knf_iom_section_view'),
    path('knf/iom/delete_section/', views.delete_knf_iom_section_view, name='delete_knf_iom_section_view'),
    path('knf/iom/update_proficiency/', views.update_knf_iom_proficiency_view, name='update_knf_iom_proficiency_view'),
    
    path('knf/laite_sahkoturvallisuus/', views.knf_laite_sahkoturvallisuus_view, name='knf_laite_sahkoturvallisuus'),
    path('knf/laite_sahkoturvallisuus/add_section/', views.add_knf_laite_sahkoturvallisuus_section_view, name='add_knf_laite_sahkoturvallisuus_section_view'),
    path('knf/laite_sahkoturvallisuus/edit_section/', views.edit_knf_laite_sahkoturvallisuus_section_view, name='edit_knf_laite_sahkoturvallisuus_section_view'),
    path('knf/laite_sahkoturvallisuus/delete_section/', views.delete_knf_laite_sahkoturvallisuus_section_view, name='delete_knf_laite_sahkoturvallisuus_section_view'),
    path('knf/laite_sahkoturvallisuus/update_proficiency/', views.update_knf_laite_sahkoturvallisuus_proficiency_view, name='update_knf_laite_sahkoturvallisuus_proficiency_view'),
    
    path('knf/sarja_tms_hoidot/', views.knf_sarja_tms_hoidot_view, name='knf_sarja_tms_hoidot'),
    path('knf/sarja_tms_hoidot/add_section/', views.add_knf_sarja_tms_hoidot_section_view, name='add_knf_sarja_tms_hoidot_section_view'),
    path('knf/sarja_tms_hoidot/edit_section/', views.edit_knf_sarja_tms_hoidot_section_view, name='edit_knf_sarja_tms_hoidot_section_view'),
    path('knf/sarja_tms_hoidot/delete_section/', views.delete_knf_sarja_tms_hoidot_section_view, name='delete_knf_sarja_tms_hoidot_section_view'),
    path('knf/sarja_tms_hoidot/update_proficiency/', views.update_knf_sarja_tms_hoidot_proficiency_view, name='update_knf_sarja_tms_hoidot_proficiency_view'),
    
    path('knf/uni/', views.knf_uni_view, name='knf_uni'),
    path('knf/uni/add_section/', views.add_knf_uni_section_view, name='add_knf_uni_section_view'),
    path('knf/uni/edit_section/', views.edit_knf_uni_section_view, name='edit_knf_uni_section_view'),
    path('knf/uni/delete_section/', views.delete_knf_uni_section_view, name='delete_knf_uni_section_view'),
    path('knf/uni/update_proficiency/', views.update_knf_uni_proficiency_view, name='update_knf_uni_proficiency_view'),
    
    # Fysiologia sivut
    path('fysiologia/ekg/', views.fysiologia_ekg_view, name='fysiologia_ekg'),
    path('fysiologia/ekg/add_section/', views.add_fysiologia_ekg_section_view, name='add_fysiologia_ekg_section_view'),
    path('fysiologia/ekg/edit_section/', views.edit_fysiologia_ekg_section_view, name='edit_fysiologia_ekg_section_view'),
    path('fysiologia/ekg/delete_section/', views.delete_fysiologia_ekg_section_view, name='delete_fysiologia_ekg_section_view'),
    path('fysiologia/ekg/update_proficiency/', views.update_fysiologia_ekg_proficiency_view, name='update_fysiologia_ekg_proficiency_view'),
    
    path('fysiologia/gi_kanava/', views.fysiologia_gi_kanava_view, name='fysiologia_gi_kanava'),
    path('fysiologia/gi_kanava/add_section/', views.add_fysiologia_gi_kanava_section_view, name='add_fysiologia_gi_kanava_section_view'),
    path('fysiologia/gi_kanava/edit_section/', views.edit_fysiologia_gi_kanava_section_view, name='edit_fysiologia_gi_kanava_section_view'),
    path('fysiologia/gi_kanava/delete_section/', views.delete_fysiologia_gi_kanava_section_view, name='delete_fysiologia_gi_kanava_section_view'),
    path('fysiologia/gi_kanava/update_proficiency/', views.update_fysiologia_gi_kanava_proficiency_view, name='update_fysiologia_gi_kanava_proficiency_view'),
    
    path('fysiologia/keuhkofunktio/', views.fysiologia_keuhkofunktio_view, name='fysiologia_keuhkofunktio'),
    path('fysiologia/keuhkofunktio/add_section/', views.add_fysiologia_keuhkofunktio_section_view, name='add_fysiologia_keuhkofunktio_section_view'),
    path('fysiologia/keuhkofunktio/edit_section/', views.edit_fysiologia_keuhkofunktio_section_view, name='edit_fysiologia_keuhkofunktio_section_view'),
    path('fysiologia/keuhkofunktio/delete_section/', views.delete_fysiologia_keuhkofunktio_section_view, name='delete_fysiologia_keuhkofunktio_section_view'),
    path('fysiologia/keuhkofunktio/update_proficiency/', views.update_fysiologia_keuhkofunktio_proficiency_view, name='update_fysiologia_keuhkofunktio_proficiency_view'),

    path('fysiologia/luuston_mineraali/', views.fysiologia_luuston_mineraali_view, name='fysiologia_luuston_mineraali'),
    path('fysiologia/luuston_mineraali/add_section/', views.add_fysiologia_luuston_mineraali_section_view, name='add_fysiologia_luuston_mineraali_section_view'),
    path('fysiologia/luuston_mineraali/edit_section/', views.edit_fysiologia_luuston_mineraali_section_view, name='edit_fysiologia_luuston_mineraali_section_view'),
    path('fysiologia/luuston_mineraali/delete_section/', views.delete_fysiologia_luuston_mineraali_section_view, name='delete_fysiologia_luuston_mineraali_section_view'),
    path('fysiologia/luuston_mineraali/update_proficiency/', views.update_fysiologia_luuston_mineraali_proficiency_view, name='update_fysiologia_luuston_mineraali_proficiency_view'),

    path('fysiologia/verenkierto/', views.fysiologia_verenkierto_view, name='fysiologia_verenkierto'),
    path('fysiologia/verenkierto/add_section/', views.add_fysiologia_verenkierto_section_view, name='add_fysiologia_verenkierto_section_view'),
    path('fysiologia/verenkierto/edit_section/', views.edit_fysiologia_verenkierto_section_view, name='edit_fysiologia_verenkierto_section_view'),
    path('fysiologia/verenkierto/delete_section/', views.delete_fysiologia_verenkierto_section_view, name='delete_fysiologia_verenkierto_section_view'),
    path('fysiologia/verenkierto/update_proficiency/', views.update_fysiologia_verenkierto_proficiency_view, name='update_fysiologia_verenkierto_proficiency_view'),

    # Raportoi ongelmasta sivu
    path('raportoi-ongelma/', views.raportoi_ongelma_view, name='raportoi_ongelma'),
    path('raportoi-ongelma/edit_section/', views.edit_raportoi_ongelma_section_view, name='edit_raportoi_ongelma_section_view'),
    
    # Image upload for CKEditor
    path('upload-image/', views.upload_image_view, name='upload_image'),

    # Theory image slots API (upload/delete MUST come before <str:modality>)
    path('modaliteetit/api/tts/', views.tts_generate, name='tts_generate'),
    path('modaliteetit/api/theory-images/upload/', views.theory_image_upload, name='theory_image_upload'),
    path('modaliteetit/api/theory-images/delete/', views.theory_image_delete, name='theory_image_delete'),
    path('modaliteetit/api/theory-images/<str:modality>/', views.theory_images_list, name='theory_images_list'),

    # Theory content inline editing API
    path('modaliteetit/api/theory-content/save/', views.theory_content_save, name='theory_content_save'),
    path('modaliteetit/api/theory-content/<str:modality>/<str:tab_id>/', views.theory_content_get, name='theory_content_get'),
]