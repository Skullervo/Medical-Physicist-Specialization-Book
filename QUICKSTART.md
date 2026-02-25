# Pikastarttiopas - Claude Code

## Vaihe 1: Projektin valmistelu

Kopioi tämä hakemisto Django-projektin juureen:
```bash
cp -r sairaalafyysikko-quiz/* /polku/projektiin/
```

Varmista että CLAUDE.md on projektin juuressa - Claude Code lukee sen automaattisesti.

## Vaihe 2: Django-appien luonti

```bash
python manage.py startapp epa
python manage.py startapp quiz
python manage.py startapp exams
python manage.py startapp progress
python manage.py startapp ai_evaluator
```

Lisää `settings.py` → `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'epa',
    'quiz',
    'exams',
    'progress',
    'ai_evaluator',
]
```

## Vaihe 3: Mallit (pyydä Claude Codea)

"Lue agents/data_modeler.md ja luo kaikki Django-mallit sen mukaisesti. 
Luo myös admin-rekisteröinnit ja migraatiot."

## Vaihe 4: EPA-korttien lataus

"Lue data/EPA_CARDS_README.md ja luo management command joka lataa 
kaikki 34 EPA-korttia PDF:stä tietokantaan. PDF on projektin juuressa."

## Vaihe 5: Kysymyspankki

"Lue agents/quiz_generator.md ja toteuta:
1. Kysymysten CRUD-viewit
2. Harjoittelunäkymä (yksi kysymys kerrallaan, HTMX-vastaus)
3. 5 esimerkkikysymystä per erikoisala seed dataksi"

## Vaihe 6: Spaced Repetition

"Lue agents/data_modeler.md SpacedRepetitionCard-malli ja toteuta:
1. SM-2 algoritmin view: /quiz/review/ joka näyttää kertaavat kysymykset
2. Vastauksen jälkeen päivitä SR-kortti
3. Dashboard-näkymä kertaavien kysymysten määrästä"

## Vaihe 7: AI-arviointi

"Lue agents/ai_evaluator.md ja toteuta:
1. AIEvaluator-service
2. Celery-task avointen vastausten arviointiin
3. Avointen kysymysten vastausnäkymä joka triggeröi AI-arvioinnin"

Tarvitset: `pip install anthropic celery redis`
Ja `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Vaihe 8: Tenttijärjestelmä

"Lue agents/exam_system.md ja toteuta tenttien harjoittelujärjestelmä."

## Vaihe 9: Pelillistäminen

"Lue agents/gamification.md ja toteuta XP-järjestelmä ja saavutukset."

## Vaihe 10: Frontend

"Lue agents/frontend_builder.md ja rakenna UI kaikkiin näkymiin."

## Riippuvuudet

```
# requirements.txt lisäykset
anthropic>=0.40.0
celery>=5.3.0
redis>=5.0.0
django-htmx>=1.17.0
```
