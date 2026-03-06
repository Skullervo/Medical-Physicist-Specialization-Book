"""
Management command to generate MCQ questions from existing exam questions using Claude API.

Each ExamQuestion (with model_answer) is used as source material. Claude generates
2-3 targeted MCQs that test the key facts and concepts from the model answer.
Generated questions are linked back to the source ExamQuestion via FK.

Usage:
    python manage.py generate_exam_mcqs_ai                          # All subjects
    python manage.py generate_exam_mcqs_ai --subject "Radiologia"   # One subject area
    python manage.py generate_exam_mcqs_ai --questions-per 3        # 3 MCQs per exam q
    python manage.py generate_exam_mcqs_ai --skip-existing          # Skip already processed
    python manage.py generate_exam_mcqs_ai --dry-run                # Preview only
"""
import json
import re
import time

from django.core.management.base import BaseCommand
from django.db import transaction
from html.parser import HTMLParser

from sisalto.models import EPA, ExamQuestion
from quiz.models import Question, Choice


# Maps ExamQuestion.subject_area to a default EPA ID.
# Matches the AREA_EPA mapping used in populate_exam_mcqs.py.
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
    """Strip HTML tags and return plain text."""

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
    """Convert HTML to plain text."""
    stripper = HTMLStripper()
    stripper.feed(html_content)
    text = stripper.get_text()
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


SYSTEM_PROMPT = """Olet lääketieteellisen fysiikan asiantuntija ja opettaja. Tehtäväsi on \
luoda monivalintakysymyksiä vanhojen tenttikysymysten mallivastauksista siten, että \
opiskelija harjoittelee MCQ-muodossa juuri niitä käsitteitä, joita tentissä kysytään. \
MCQ-kysymysten jälkeen opiskelija pystyy vastaamaan avoimen tenttikysymyksen paremmin.

Luo kysymykset AINA suomeksi. Testaa konkreettisia faktoja, lukuarvoja ja menetelmiä \
— ei pelkkää määritelmien ulkoa osaamista."""

EXAM_MCQ_PROMPT = """Tenttikysymys ({year}):
"{question_text}"

Mallivastaus:
{model_answer}

---

Luo {n} monivalintakysymystä jotka testaavat mallivastauksessa esiintyviä avainasioita \
(käsitteet, lukuarvot, yhtälöt, menetelmät, periaatteet). Älä kysy suoraan \
tenttikysymystä uudestaan — sen sijaan pura mallivastaus pienempiin testattaviin osiin.

Ohjeita:
- Vaikeusluku: 4 (haastava, tenttitaso)
- Jokainen kysymys: YKSI oikea vastaus (tyyppi "multiple_choice"), 4 vaihtoehtoa
- Harhauttavat vaihtoehdot ovat uskottavia mutta selkeästi vääriä
- Jokaiselle vaihtoehdolle lyhyt selitys (miksi oikein / miksi väärin)
- Viittaa tarvittaessa lähteenä olevaan tenttikysymykseen

Palauta VAIN JSON-taulukko, ei muuta tekstiä:
[
  {{
    "question_type": "multiple_choice",
    "difficulty": 4,
    "text": "Kysymysteksti suomeksi?",
    "explanation": "Yleinen selitys oikeasta vastauksesta",
    "choices": [
      {{"text": "Oikea vastaus", "is_correct": true, "explanation": "Selitys"}},
      {{"text": "Väärä vaihtoehto 1", "is_correct": false, "explanation": "Selitys"}},
      {{"text": "Väärä vaihtoehto 2", "is_correct": false, "explanation": "Selitys"}},
      {{"text": "Väärä vaihtoehto 3", "is_correct": false, "explanation": "Selitys"}}
    ]
  }}
]"""


class Command(BaseCommand):
    help = 'Generate MCQ questions from exam questions (model answers) using Claude API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            help='Process only this subject area (e.g. "Radiologia")',
        )
        parser.add_argument(
            '--questions-per',
            type=int,
            default=2,
            help='Number of MCQs to generate per exam question (default: 2)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip ExamQuestion records that already have linked MCQ questions',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be generated without making API calls',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=2.0,
            help='Delay in seconds between API calls (default: 2.0)',
        )

    def handle(self, *args, **options):
        import os

        n_per = min(max(options['questions_per'], 1), 3)

        # API client — only needed for actual generation, not dry-run
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

        # Fetch ExamQuestions that have model answers
        exam_qs = ExamQuestion.objects.exclude(model_answer='').order_by('subject_area', 'year', 'question_number')

        if options['subject']:
            exam_qs = exam_qs.filter(subject_area=options['subject'])

        # Build EPA cache to avoid repeated DB lookups
        epa_cache = {}
        for subject, epa_id in SUBJECT_TO_EPA_ID.items():
            try:
                epa_cache[subject] = EPA.objects.get(id=epa_id)
            except EPA.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"EPA id={epa_id} for subject '{subject}' not found — will skip those questions"
                ))

        # Optionally filter out already-processed exam questions
        if options['skip_existing']:
            already_linked = set(
                Question.objects.filter(exam_question__isnull=False)
                .values_list('exam_question_id', flat=True)
            )
            exam_qs = [q for q in exam_qs if q.id not in already_linked]
        else:
            exam_qs = list(exam_qs)

        total = len(exam_qs)
        self.stdout.write(f"\nFound {total} exam questions with model answers to process")
        self.stdout.write(f"Target: {n_per} MCQ(s) per question -> ~{total * n_per} new questions\n")

        if total == 0:
            self.stdout.write(self.style.WARNING('Nothing to process.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('--- DRY RUN: showing first 10 ---\n'))
            counts = {}
            for eq in exam_qs:
                counts[eq.subject_area] = counts.get(eq.subject_area, 0) + 1
            for subj, cnt in sorted(counts.items()):
                epa = epa_cache.get(subj)
                epa_label = f"EPA {epa.id}: {epa.title}" if epa else "EPA not found"
                self.stdout.write(f"  {subj}: {cnt} questions × {n_per} = ~{cnt * n_per} MCQs  [{epa_label}]")
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN total: ~{total * n_per} MCQs from {total} exam questions"
            ))
            return

        total_saved = 0
        total_errors = 0

        for i, exam_q in enumerate(exam_qs, 1):
            subject = exam_q.subject_area
            epa = epa_cache.get(subject)

            if epa is None:
                self.stderr.write(self.style.WARNING(
                    f"  [{i}/{total}] Skipping — no EPA mapping for subject '{subject}'"
                ))
                continue

            year_label = str(exam_q.year) if exam_q.year else exam_q.exam_date
            short_q = exam_q.question_text[:80].replace('\n', ' ')
            self.stdout.write(f"\n[{i}/{total}] {subject} ({year_label}) Q{exam_q.question_number}: {short_q}…")

            model_answer_text = strip_html(exam_q.model_answer)[:3000]

            prompt = EXAM_MCQ_PROMPT.format(
                year=year_label,
                question_text=exam_q.question_text,
                model_answer=model_answer_text,
                n=n_per,
            )

            try:
                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = response.content[0].text.strip()

                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if not json_match:
                    self.stderr.write(self.style.ERROR('  ERROR: could not extract JSON from response'))
                    total_errors += 1
                    continue

                questions_data = json.loads(json_match.group())

                saved = self._save_questions(questions_data, epa, exam_q)
                total_saved += saved
                self.stdout.write(self.style.SUCCESS(f"  Saved {saved} questions"))

            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f"  JSON parse error: {e}"))
                total_errors += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  API error: {e}"))
                total_errors += 1

            if i < total:
                time.sleep(options['delay'])

        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Saved {total_saved} new MCQ questions from {total} exam questions."
        ))
        if total_errors:
            self.stdout.write(self.style.ERROR(f"Errors: {total_errors}"))

    @transaction.atomic
    def _save_questions(self, questions_data, epa, exam_q):
        """Save parsed question data linked to the source exam question."""
        saved_count = 0
        for q_data in questions_data:
            q_type = q_data.get('question_type', 'multiple_choice')
            if q_type not in ('multiple_choice', 'multi_select'):
                q_type = 'multiple_choice'

            choices_data = q_data.get('choices', [])
            if len(choices_data) < 2:
                continue

            # Ensure exactly one correct answer for multiple_choice
            correct_count = sum(1 for c in choices_data if c.get('is_correct'))
            if q_type == 'multiple_choice' and correct_count != 1:
                found_correct = False
                for c in choices_data:
                    if c.get('is_correct') and not found_correct:
                        found_correct = True
                    elif c.get('is_correct'):
                        c['is_correct'] = False
                if not found_correct and choices_data:
                    choices_data[0]['is_correct'] = True

            if q_type == 'multi_select' and correct_count < 2:
                q_type = 'multiple_choice'

            question = Question.objects.create(
                question_type=q_type,
                difficulty=q_data.get('difficulty', 4),
                text=q_data.get('text', ''),
                explanation=q_data.get('explanation', ''),
                epa=epa,
                exam_question=exam_q,
                is_active=True,
            )

            for idx, c_data in enumerate(choices_data):
                Choice.objects.create(
                    question=question,
                    text=c_data.get('text', ''),
                    is_correct=c_data.get('is_correct', False),
                    order=idx,
                    explanation=c_data.get('explanation', ''),
                )

            saved_count += 1

        return saved_count
