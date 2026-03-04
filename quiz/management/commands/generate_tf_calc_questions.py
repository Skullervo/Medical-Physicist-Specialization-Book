"""
Management command to generate true_false, calculation and matching questions using Claude API.

Sources: ExamQuestion model answers.

Usage:
    python manage.py generate_tf_calc_questions                         # All subjects, all types
    python manage.py generate_tf_calc_questions --type true_false       # Only true/false
    python manage.py generate_tf_calc_questions --type calculation       # Only calculations
    python manage.py generate_tf_calc_questions --type matching          # Only matching pairs
    python manage.py generate_tf_calc_questions --subject "Isotooppilääketiede"
    python manage.py generate_tf_calc_questions --per-question 3
    python manage.py generate_tf_calc_questions --dry-run
"""
import json
import re
import time
from html.parser import HTMLParser

from django.core.management.base import BaseCommand
from django.db import transaction

from sisalto.models import EPA, ExamQuestion
from quiz.models import Question, Choice


SUBJECT_TO_EPA_ID = {
    'Radiologia':            1,
    'Sädehoito':            16,
    'Isotooppilääketiede':  28,
    'KNF':                   5,
    'Kliininen fysiologia': 11,
    'Fysiologia':           11,
    'Anatomia':              1,
}


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = False
        if tag in ('p', 'br', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr'):
            self.result.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.result.append(data)

    def get_text(self):
        return ''.join(self.result).strip()


def strip_html(html_content):
    stripper = HTMLStripper()
    stripper.feed(html_content)
    text = stripper.get_text()
    return re.sub(r'\n{3,}', '\n\n', text).strip()


TRUE_FALSE_PROMPT = """Olet lääketieteellisen fysiikan asiantuntija. Alla on tenttikysymyksen mallivastaus.

Luo {n} OIKEIN/VÄÄRIN-väittämää jotka testaavat keskeisiä faktoja.

Säännöt:
- Väittämät suomeksi, lyhyitä ja yksiselitteisiä (max 2 lausetta)
- Noin puolet tosia, puolet epätosia (ei aina sama määrä)
- Epätosat väittämät ovat realistisia mutta sisältävät yhden selkeän virheen
- Merkitse selvästi onko väittämä tosi vai epätosi
- Lisää lyhyt selitys (explanation) jonka opiskelija näkee vastauksen jälkeen

Tenttikysymys ({year}): {question_text}

Mallivastaus:
{model_answer}

Palauta VAIN JSON-taulukko, ei muuta tekstiä:
[
  {{
    "question_type": "true_false",
    "difficulty": 3,
    "text": "Väittämäteksti suomeksi.",
    "is_true": true,
    "explanation": "Lyhyt selitys miksi tosi/epätosi."
  }}
]"""


CALCULATION_PROMPT = """Olet lääketieteellisen fysiikan asiantuntija. Alla on tenttikysymyksen mallivastaus.

Luo {n} LASKUTEHTÄVÄÄ joissa opiskelijan tulee laskea numeerinen vastaus.

Säännöt:
- Tehtävät suomeksi
- Jokaisella tehtävällä on YKSI oikea numeerinen vastaus (ei vaihtoehtoväittämiä)
- Laske ja tarkista: calculation_answer on oikea vastaus
- Toleranssi on prosentuaalinen sallittu poikkeama (tyypillisesti 3-10%)
- Ilmoita yksikkö (esim. "MBq", "mSv", "Gy", "ms", "keV", "mm", "%")
- Selitys (explanation) kertoo ratkaisutavan lyhyesti

Tenttikysymys ({year}): {question_text}

Mallivastaus:
{model_answer}

Palauta VAIN JSON-taulukko, ei muuta tekstiä:
[
  {{
    "question_type": "calculation",
    "difficulty": 4,
    "text": "Laskutehtäväteksti suomeksi. Anna tulos yksiköissä X.",
    "calculation_answer": 123.4,
    "calculation_tolerance": 5.0,
    "calculation_unit": "MBq",
    "explanation": "Lyhyt selitys laskutavasta."
  }}
]"""


MATCHING_PROMPT = """Olet lääketieteellisen fysiikan asiantuntija. Alla on tenttikysymyksen mallivastaus.

Luo {n} YHDISTÄ PARIT -tehtävää. Jokaisessa tehtävässä opiskelija yhdistää vasemman sarakkeen termit oikeaan sarakkeeseen.

Säännöt:
- Tehtävät suomeksi
- 4 paria per tehtävä (ei enemmän, ei vähemmän)
- Vasen sarake: spesifiset termit / käsitteet / lyhenteet
- Oikea sarake: selitykset / arvot / yhteydet
- Parit ovat selkeitä ja yksiselitteisiä
- Sekoita oikeaa saraketta — älä laita pareja järjestyksessä
- Selitys kertoo mistä kategoriasta on kyse (esim. "Radionuklidit ja puoliintumisajat")

Tenttikysymys ({year}): {question_text}

Mallivastaus:
{model_answer}

Palauta VAIN JSON-taulukko, ei muuta tekstiä:
[
  {{
    "question_type": "matching",
    "difficulty": 3,
    "text": "Yhdistä termit oikeisiin määritelmiin / arvoihin.",
    "explanation": "Lyhyt kuvaus pariryhmästä.",
    "matching_pairs": [
      {{"left": "Termi 1", "right": "Määritelmä A"}},
      {{"left": "Termi 2", "right": "Määritelmä B"}},
      {{"left": "Termi 3", "right": "Määritelmä C"}},
      {{"left": "Termi 4", "right": "Määritelmä D"}}
    ]
  }}
]"""


def call_claude(client, prompt: str, model: str = 'claude-haiku-4-5-20251001') -> str:
    """Call Claude API and return response text."""
    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{'role': 'user', 'content': prompt}],
    )
    return msg.content[0].text


def parse_json_response(text: str) -> list:
    """Extract JSON array from Claude response (handles markdown code blocks)."""
    text = text.strip()
    # Strip markdown code fences
    if '```' in text:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if match:
            text = match.group(1).strip()
    # Find JSON array
    start = text.find('[')
    end = text.rfind(']') + 1
    if start == -1 or end == 0:
        return []
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return []


class Command(BaseCommand):
    help = 'Generate true_false and calculation questions using Claude API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['true_false', 'calculation', 'matching', 'all'],
            default='all',
            help='Which question type to generate (default: all)',
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Process only this subject area (e.g. "Isotooppilääketiede")',
        )
        parser.add_argument(
            '--per-question',
            type=int,
            default=3,
            help='Number of questions to generate per exam question (default: 3)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Max number of source exam questions to process (0 = all)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without calling API',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.5,
            help='Seconds between API calls (default: 1.5)',
        )

    def handle(self, *args, **options):
        import os

        q_type = options['type']
        n_per = min(max(options['per_question'], 1), 5)
        types_to_generate = (
            ['true_false', 'calculation', 'matching'] if q_type == 'all' else [q_type]
        )

        client = None
        if not options['dry_run']:
            try:
                import anthropic
            except ImportError:
                self.stderr.write(self.style.ERROR(
                    'anthropic package not installed. Run: pip install anthropic'
                ))
                return

            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                self.stderr.write(self.style.ERROR(
                    'ANTHROPIC_API_KEY environment variable not set'
                ))
                return

            client = anthropic.Anthropic(api_key=api_key)

        # Build EPA cache
        epa_cache = {}
        for subject, epa_id in SUBJECT_TO_EPA_ID.items():
            try:
                epa_cache[subject] = EPA.objects.get(id=epa_id)
            except EPA.DoesNotExist:
                pass

        # Fetch source exam questions with model answers
        exam_qs = ExamQuestion.objects.exclude(model_answer='').order_by(
            'subject_area', 'year', 'question_number'
        )
        if options['subject']:
            exam_qs = exam_qs.filter(subject_area=options['subject'])
        exam_qs = list(exam_qs)
        if options['limit']:
            exam_qs = exam_qs[:options['limit']]

        total = len(exam_qs)
        self.stdout.write(f"\nSource exam questions: {total}")
        self.stdout.write(f"Generating: {', '.join(types_to_generate)}")
        self.stdout.write(f"Per question: {n_per} -> ~{total * n_per * len(types_to_generate)} new questions\n")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN — no API calls made'))
            for subj in sorted(set(q.subject_area for q in exam_qs)):
                cnt = sum(1 for q in exam_qs if q.subject_area == subj)
                epa = epa_cache.get(subj)
                epa_label = f"EPA {epa.id}: {epa.title}" if epa else 'EPA not found'
                self.stdout.write(f"  {subj}: {cnt} questions [{epa_label}]")
            return

        created_tf = 0
        created_calc = 0
        created_matching = 0
        errors = 0

        for i, exam_q in enumerate(exam_qs, 1):
            epa = epa_cache.get(exam_q.subject_area)
            if not epa:
                self.stdout.write(self.style.WARNING(
                    f"  [{i}/{total}] SKIP — no EPA for '{exam_q.subject_area}'"
                ))
                continue

            model_answer = strip_html(exam_q.model_answer)
            if len(model_answer) < 100:
                continue  # Too short to generate useful questions

            self.stdout.write(f"  [{i}/{total}] {exam_q.subject_area} {exam_q.year} Q{exam_q.question_number}")

            for qtype in types_to_generate:
                try:
                    if qtype == 'true_false':
                        prompt = TRUE_FALSE_PROMPT.format(
                            n=n_per,
                            year=exam_q.year or '?',
                            question_text=exam_q.question_text[:300],
                            model_answer=model_answer[:1500],
                        )
                    elif qtype == 'matching':
                        prompt = MATCHING_PROMPT.format(
                            n=min(n_per, 2),  # Max 2 matching per source (they're bigger)
                            year=exam_q.year or '?',
                            question_text=exam_q.question_text[:300],
                            model_answer=model_answer[:1500],
                        )
                    else:
                        prompt = CALCULATION_PROMPT.format(
                            n=n_per,
                            year=exam_q.year or '?',
                            question_text=exam_q.question_text[:300],
                            model_answer=model_answer[:1500],
                        )

                    response_text = call_claude(client, prompt)
                    questions = parse_json_response(response_text)

                    if not questions:
                        self.stdout.write(self.style.WARNING(f"    {qtype}: no valid JSON"))
                        errors += 1
                        continue

                    with transaction.atomic():
                        for qdata in questions:
                            if qdata.get('question_type') != qtype:
                                continue

                            if qtype == 'true_false':
                                # Create question with 2 choices
                                is_true = qdata.get('is_true', True)
                                q = Question.objects.create(
                                    question_type='true_false',
                                    difficulty=qdata.get('difficulty', 3),
                                    text=qdata['text'],
                                    explanation=qdata.get('explanation', ''),
                                    epa=epa,
                                    exam_question=exam_q,
                                )
                                # "Oikein" choice
                                Choice.objects.create(
                                    question=q,
                                    text='Oikein',
                                    is_correct=is_true,
                                    order=0,
                                    explanation=qdata.get('explanation', '') if is_true else '',
                                )
                                # "Väärin" choice
                                Choice.objects.create(
                                    question=q,
                                    text='Väärin',
                                    is_correct=not is_true,
                                    order=1,
                                    explanation='' if is_true else qdata.get('explanation', ''),
                                )
                                created_tf += 1

                            elif qtype == 'calculation':
                                calc_answer = qdata.get('calculation_answer')
                                if calc_answer is None:
                                    continue
                                Question.objects.create(
                                    question_type='calculation',
                                    difficulty=qdata.get('difficulty', 4),
                                    text=qdata['text'],
                                    explanation=qdata.get('explanation', ''),
                                    calculation_answer=float(calc_answer),
                                    calculation_tolerance=float(qdata.get('calculation_tolerance', 5.0)),
                                    calculation_unit=qdata.get('calculation_unit', ''),
                                    epa=epa,
                                    exam_question=exam_q,
                                )
                                created_calc += 1

                            elif qtype == 'matching':
                                pairs = qdata.get('matching_pairs', [])
                                if len(pairs) < 2:
                                    continue
                                Question.objects.create(
                                    question_type='matching',
                                    difficulty=qdata.get('difficulty', 3),
                                    text=qdata['text'],
                                    explanation=qdata.get('explanation', ''),
                                    matching_pairs=pairs,
                                    epa=epa,
                                    exam_question=exam_q,
                                )
                                created_matching += 1

                    self.stdout.write(self.style.SUCCESS(
                        f"    {qtype}: +{len(questions)} OK"
                    ))
                    time.sleep(options['delay'])

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"    {qtype} ERROR: {e}"))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created: {created_tf} true_false, {created_calc} calculation, "
            f"{created_matching} matching. Errors: {errors}"
        ))
