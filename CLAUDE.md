# Sairaalafyysikon Erikoistumiskoulutus - Oppimisalusta

## Projektin yleiskuvaus

Tämä on Django + PostgreSQL -pohjainen oppimisalusta sairaalafyysikoiden erikoistumiskoulutukseen. Alusta sisältää EPA-koulutuskortit (34 kpl), pelillistetyn kysymyspankin, vanhojen tenttien harjoittelun AI-tarkistuksella ja spaced repetition -oppimisalgoritmin.

## Tech Stack

- **Backend**: Django 4.2+ / Python 3.11+
- **Tietokanta**: PostgreSQL 15+
- **Frontend**: Django templates + HTMX + Alpine.js (tai React, jos jo käytössä)
- **AI-arviointi**: Anthropic Claude API (claude-sonnet-4-5-20250929)
- **Task queue**: Celery + Redis (AI-arvioinnin taustaprosessointi)
- **Cache**: Redis

## Arkkitehtuuri

```
project/
├── apps/
│   ├── epa/              # EPA-kortit ja teoria
│   ├── quiz/             # Kysymyspankki ja pelillistäminen
│   ├── exams/            # Vanhojen tenttien harjoittelu
│   ├── progress/         # Edistymisen seuranta ja spaced repetition
│   ├── ai_evaluator/     # AI-arviointi Claude API:lla
│   └── accounts/         # Käyttäjähallinta
├── templates/
├── static/
├── data/                 # EPA-korttien seed data (JSON)
└── manage.py
```

## EPA-korttien rakenne

34 EPA-korttia jaettu 6 erikoisalaan:
1. **Yhteiset** (1): Laite- ja sähköturvallisuus
2. **Kliininen neurofysiologia** (5): EEG, herätepotentiaali/ENMG, TMS, uni, IOM
3. **Sädehoito** (7): peruskäsitteet, kuvantaminen, ulkoinen, sisäinen, dosimetria, laitteet, säteilybiologia
4. **Radiologia** (8): läpivalaisu, MRI, mammografia, natiivi, TT, UÄ, näytöt, hammas, säteilybiologia
5. **Isotooppilääketiede** (7): gamma, PET, radiofarmasia, SPET, PET-tutk, nuklidihoidot, säteilybiologia
6. **Kliininen fysiologia** (5): EKG, verenkierto, keuhko, GI, DXA

Jokainen kortti sisältää:
- A-tason osaamiset (perusosaaminen → epäsuora ohjaus)
- B-tason osaamiset (täydentävä → itsenäinen työskentely)
- CanMEDS-osaamisalueet
- Viitekirjallisuus

## Kysymystyypit

1. **Monivalinta** (multiple_choice) - 4 vaihtoehtoa, 1 oikea
2. **Monivalinta usealla oikealla** (multi_select) - 4-6 vaihtoehtoa, 1+ oikeaa
3. **Oikein/Väärin** (true_false) - väittämä
4. **Laskutehtävä** (calculation) - numeerinen vastaus, toleranssi
5. **Avoin kysymys** (open_ended) - AI arvioi vastauksen
6. **Yhdistä pari** (matching) - termit ja määritelmät
7. **Tenttikysymys** (exam_essay) - laaja avoin, AI arvioi mallivastauksen perusteella

## Spaced Repetition -algoritmi

SM-2 -pohjainen algoritmi:
- Uusi kysymys: intervalli 1 päivä
- Oikein vastattu: intervalli kasvaa (1 → 3 → 7 → 14 → 30 → 60 pv)
- Väärin vastattu: palaa alkuun, intervalli 1 päivä
- Ease factor: 2.5 lähtöarvo, muokkautuu suorituksen mukaan
- Confidence rating: 1-5 (kuinka varma vastauksesta)

## AI-arvioinnin periaatteet

Avointen vastausten ja tenttikysymysten arviointi:
- Kontekstina EPA-kortin teoria ja osaamistavoitteet
- Mallivastaus vertailuperusteena
- Pisteytys 0-5 asteikolla
- Sanallinen palaute: vahvuudet, puutteet, parannusehdotukset
- Viittaukset relevantteihin EPA-osaamistavoitteisiin

## Agenttien käyttö

Katso `agents/` -hakemisto erillisille agentti-ohjeistuksille:
- `agents/data_modeler.md` - Tietokantamallien suunnittelu
- `agents/quiz_generator.md` - Kysymysten generointi EPA-korteista
- `agents/ai_evaluator.md` - AI-arvioinnin toteutus
- `agents/frontend_builder.md` - Käyttöliittymän rakentaminen
- `agents/gamification.md` - Pelillistämisen logiikka
- `agents/exam_system.md` - Tenttijärjestelmän toteutus

## Koodauskäytännöt

- Kieli: Python-koodi ja kommentit englanniksi, UI ja sisältö suomeksi
- Django-mallien nimeäminen: PascalCase (esim. `EPACard`, `QuizQuestion`)
- API-endpointit: RESTful, snake_case URLs
- Testit: pytest + factory_boy
- Migraatiot: aina tee `makemigrations` ja `migrate` yhdessä
- Type hints: käytä kaikkialla

## Käynnistyskomennot

```bash
# Kehitysympäristö
python manage.py migrate
python manage.py loaddata data/epa_cards.json
python manage.py seed_questions  # Generoi esimerkkikysymykset
python manage.py runserver

# Celery (AI-arvioinnin taustaprosessointi)
celery -A config worker -l info
```

## Tärkeät huomiot

- EPA-korttien sisältö on suomenkielistä - kaikki UI ja sisältö suomeksi
- Säteilylainsäädäntö ja STUK-määräykset ovat keskeisiä viiteaineistoja
- CanMEDS-osaamisalueet tulee näkyä kysymyksissä ja arvioinnissa
- A/B-tason erottelu on kriittistä: tentissä painotetaan A-tasoa enemmän
- Käyttäjien tietosuoja: ei potilastietoja, ei sairaalakohtaisia tietoja alustalla
