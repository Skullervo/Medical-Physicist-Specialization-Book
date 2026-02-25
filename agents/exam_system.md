# Agentti: Exam System

## Rooli
Toteuta vanhojen tenttien harjoittelujärjestelmä AI-tarkistuksella.

## Tenttien rakenne

Sairaalafyysikkokuulustelu koostuu tyypillisesti:
- 6-10 avointa kysymystä
- Aikaa 3-4 tuntia
- Kysymykset kattavat kaikki erikoisalat
- Läpäisyraja: ~50%
- Pisteytys: 0-10 per kysymys

## Django Views ja URL-rakenne

```python
# exams/urls.py
urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam-list'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam-detail'),
    path('<int:pk>/start/', views.start_exam, name='exam-start'),
    path('session/<int:session_id>/question/<int:q_num>/', views.exam_question, name='exam-question'),
    path('session/<int:session_id>/submit/', views.submit_exam, name='exam-submit'),
    path('session/<int:session_id>/results/', views.exam_results, name='exam-results'),
]
```

## Tenttisession flow

1. Käyttäjä valitsee tentin → `start_exam` luo ExamSession + tyhjät ExamAnswer-rivit
2. Käyttäjä vastaa kysymys kerrallaan, HTMX autosave 30s välein
3. Käyttäjä lähettää tentin → status='submitted', Celery-task arvioi
4. AI arvioi jokaisen vastauksen erikseen, tallentaa pisteet ja palautteen
5. Käyttäjä näkee tulokset kun arviointi valmis (polling tai WebSocket)

## AI-arvioinnin kriteerit tenttikysymyksille

1. **Terminologia** (20%): Oikeiden sairaalafysiikan termien käyttö
2. **Fysiikan ymmärrys** (30%): Perusperiaatteiden hallinta
3. **Soveltaminen** (25%): Tiedon soveltaminen käytäntöön
4. **Kattavuus** (15%): Kuinka laajasti aihe käsitelty
5. **Selkeys** (10%): Vastauksen jäsentely

## Tenttien JSON-formaatti

Vanhat tentit tallennetaan `data/exams/` -hakemistoon:

```json
{
    "title": "Sairaalafyysikkokuulustelu 2023 kevät",
    "year": 2023,
    "semester": "kevät",
    "time_limit_minutes": 240,
    "questions": [
        {
            "number": 1,
            "text": "Selitä TT-kuvauksen beam hardening -artefaktin syntymekanismi ja korjausmenetelmät.",
            "max_points": 10,
            "epa_card_slug": "tietokonetomografia",
            "model_answer": "Beam hardening johtuu polykromaattisen röntgensäteilyn...",
            "scoring_rubric": "Täydet pisteet: polykromaattinen keila, vaimenemiskerroin, korjaukset (linearisaatio, iteratiivinen). 7-8p: mekanismi oikein, korjaukset osittain. 4-6p: perusidea oikein.",
            "key_concepts": ["polykromaattinen keila", "vaimenemiskerroin", "linearisaatiokorjaus", "cupping", "streak"]
        }
    ]
}
```

## Tärkeää

1. **Aikaraja**: Näytetään laskuri, mutta ei pakoteta kesken harjoittelun
2. **Automaattitallennus**: HTMX tallentaa vastauksen 30s välein
3. **Arvioinnin kesto**: AI-arviointi 30-120s per vastaus - näytä edistymispalkki
4. **Uudelleenyritys**: Sama tentti voi tehdä uudelleen, seuraa kehitystä
5. **Vertailu**: Näytä miten tulos vertautuu aiempiin yrityksiin
