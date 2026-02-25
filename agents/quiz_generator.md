# Agentti: Quiz Generator

## Rooli
Generoi korkealaatuisia kysymyksiä EPA-koulutuskorteista. Tämä agentti luo sekä manuaalisia esimerkkikysymyksiä (seed data) että ohjaa AI-pohjaista kysymysten generointia.

## Kysymysten generointiperiaatteet

### A-tason kysymykset (perusosaaminen)
- Painopiste: faktat, peruskäsitteet, tunnistaminen
- Vaikeustaso: 1-3
- Esimerkkejä:
  - "Mikä on GTV sädehoidon suunnittelussa?" (monivalinta)
  - "Tietokonetomografiassa kuvausputken jännitteen kasvattaminen parantaa aina kuvanlaatua" (oikein/väärin)
  - "Laske potilaan efektiivinen annos kun..." (laskutehtävä)

### B-tason kysymykset (täydentävä osaaminen)
- Painopiste: soveltaminen, ongelmanratkaisu, arviointi
- Vaikeustaso: 3-5
- Esimerkkejä:
  - "Potilaalla on sydämentahdistin ja hänelle suunnitellaan MRI-tutkimusta. Mitä seikkoja tulee huomioida?" (avoin)
  - "Vertaile IMRT- ja VMAT-tekniikoiden etuja prostatasyövän sädehoidossa" (tenttikysymys)

## Kysymysten generointi-template (Management Command)

```python
# management/commands/generate_questions.py

from django.core.management.base import BaseCommand
from anthropic import Anthropic
from epa.models import EPACard, LearningObjective
from quiz.models import Question, Choice
import json


class Command(BaseCommand):
    help = 'Generoi kysymyksiä EPA-korteista Claude API:lla'
    
    def add_arguments(self, parser):
        parser.add_argument('--epa-card', type=str, help='EPA-kortin slug')
        parser.add_argument('--count', type=int, default=10, help='Kysymysten määrä')
        parser.add_argument('--difficulty', type=int, help='Vaikeustaso 1-5')
        parser.add_argument('--question-type', type=str, help='Kysymystyyppi')
        parser.add_argument('--dry-run', action='store_true', help='Älä tallenna tietokantaan')
    
    def handle(self, *args, **options):
        epa_card = EPACard.objects.get(slug=options['epa_card'])
        
        # Kokoa EPA-kortin konteksti
        context = self._build_context(epa_card)
        
        # Generoi kysymykset
        questions_data = self._generate_questions(
            context=context,
            count=options['count'],
            difficulty=options.get('difficulty'),
            question_type=options.get('question_type'),
        )
        
        if not options['dry_run']:
            self._save_questions(questions_data, epa_card)
        else:
            self.stdout.write(json.dumps(questions_data, indent=2, ensure_ascii=False))
    
    def _build_context(self, epa_card):
        objectives = []
        for obj in epa_card.objectives.all():
            objectives.append(f"{obj.code}: {obj.description}")
        
        theory = []
        for section in epa_card.theory_sections.all():
            theory.append(f"## {section.title}\n{section.content}")
        
        return {
            'epa_name': epa_card.name,
            'specialty': epa_card.specialty.name,
            'objectives': '\n'.join(objectives),
            'theory': '\n\n'.join(theory),
            'references': epa_card.references,
        }
    
    def _generate_questions(self, context, count, difficulty=None, question_type=None):
        client = Anthropic()
        
        difficulty_guidance = ""
        if difficulty:
            difficulty_guidance = f"Vaikeustaso: {difficulty}/5"
        
        type_guidance = ""
        if question_type:
            type_guidance = f"Kysymystyyppi: {question_type}"
        
        prompt = f"""Olet sairaalafysiikan asiantuntija. Generoi {count} kysymystä seuraavasta EPA-koulutuskortista.

EPA-kortti: {context['epa_name']}
Erikoisala: {context['specialty']}

Osaamistavoitteet:
{context['objectives']}

Teoriasisältö:
{context['theory']}

{difficulty_guidance}
{type_guidance}

Palauta kysymykset JSON-muodossa:
{{
  "questions": [
    {{
      "question_type": "multiple_choice|multi_select|true_false|calculation|open_ended|matching",
      "difficulty": 1-5,
      "text": "Kysymysteksti",
      "explanation": "Selitys oikeasta vastauksesta",
      "hint": "Vihje opiskelijalle",
      "learning_objective_codes": ["A1", "A3"],
      "choices": [  // vain monivalinnalle
        {{"text": "Vaihtoehto A", "is_correct": false, "explanation": "Miksi väärin"}},
        {{"text": "Vaihtoehto B", "is_correct": true, "explanation": "Miksi oikein"}}
      ],
      "calculation_answer": 42.5,  // vain laskutehtävälle
      "calculation_tolerance": 5,  // prosentti
      "calculation_unit": "mGy",
      "model_answer": "...",  // avoimille kysymyksille
      "scoring_rubric": "...",  // pisteytysohje
      "matching_pairs": [{{"left": "termi", "right": "määritelmä"}}]  // matching-tyypille
    }}
  ]
}}

TÄRKEÄÄ:
- Kysymysten tulee olla suomeksi
- Laskutehtävissä anna realistiset arvot sairaalafysiikan kontekstissa
- Monivalinnassa on oltava vähintään 4 vaihtoehtoa
- Väärät vaihtoehdot tulee olla uskottavia (tyypillisiä väärinkäsityksiä)
- Viittaa osaamistavoitteisiin (A1, B2 jne.)
- Huomioi säteilylainsäädäntö ja STUK-määräykset tarvittaessa
"""
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON from response
        response_text = message.content[0].text
        # Extract JSON block
        if '```json' in response_text:
            json_str = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            json_str = response_text.split('```')[1].split('```')[0]
        else:
            json_str = response_text
        
        return json.loads(json_str)
    
    def _save_questions(self, questions_data, epa_card):
        for q_data in questions_data['questions']:
            question = Question.objects.create(
                question_type=q_data['question_type'],
                difficulty=q_data['difficulty'],
                text=q_data['text'],
                explanation=q_data.get('explanation', ''),
                hint=q_data.get('hint', ''),
                epa_card=epa_card,
                calculation_answer=q_data.get('calculation_answer'),
                calculation_tolerance=q_data.get('calculation_tolerance'),
                calculation_unit=q_data.get('calculation_unit', ''),
                model_answer=q_data.get('model_answer', ''),
                scoring_rubric=q_data.get('scoring_rubric', ''),
                matching_pairs=q_data.get('matching_pairs'),
            )
            
            # Linkitä osaamistavoitteet
            for code in q_data.get('learning_objective_codes', []):
                try:
                    obj = LearningObjective.objects.get(
                        epa_card=epa_card, code=code
                    )
                    question.learning_objectives.add(obj)
                except LearningObjective.DoesNotExist:
                    pass
            
            # Luo vastausvaihtoehdot
            for i, choice_data in enumerate(q_data.get('choices', [])):
                Choice.objects.create(
                    question=question,
                    text=choice_data['text'],
                    is_correct=choice_data['is_correct'],
                    order=i,
                    explanation=choice_data.get('explanation', ''),
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Luotu: {question}')
            )
```

## Manuaaliset esimerkkikysymykset per erikoisala

Luo vähintään 5 esimerkkikysymystä per EPA-kortti seed dataksi. Näitä käytetään:
1. Alustana AI-generoiduille kysymyksille (few-shot examples)
2. Validointiin (onko AI-generoitu kysymys järkevä)
3. Offline-harjoitteluun ilman API-kutsuja

### Formaatti: `data/seed_questions/`
- `radiation_therapy.json` - Sädehoito
- `radiology.json` - Radiologia
- `nuclear_medicine.json` - Isotooppilääketiede
- `clinical_neurophysiology.json` - Kliininen neurofysiologia
- `clinical_physiology.json` - Kliininen fysiologia
- `common.json` - Yhteiset (laite- ja sähköturvallisuus)

## Laadunvalvonta

Jokaisen generoidun kysymyksen tulee:
1. Olla faktisesti oikein
2. Liittyä selkeästi EPA-kortin osaamistavoitteisiin
3. Olla yksiselitteinen (ei tulkinnanvarainen)
4. Olla sopivalla vaikeustasolla
5. Sisältää hyödyllinen selitys
6. Käyttää oikeaa suomenkielistä terminologiaa
