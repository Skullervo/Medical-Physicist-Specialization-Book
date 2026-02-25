"""
Management command to generate quiz questions from EPA theory content using Claude API.

Usage:
    python manage.py generate_questions                          # All EPAs
    python manage.py generate_questions --specialty "Radiologia"  # One specialty
    python manage.py generate_questions --epa-id 4               # One EPA
    python manage.py generate_questions --dry-run                # Preview only
"""
import json
import re
import time

from django.core.management.base import BaseCommand
from django.db import transaction
from html.parser import HTMLParser

from sisalto.models import EPA, Specialty, Section
from quiz.models import Question, Choice


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
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


SYSTEM_PROMPT = """Olet lääketieteellisen fysiikan asiantuntija ja opettaja. Tehtäväsi on luoda monivalintakysymyksiä
opiskelijoille sairaalafyysikon erikoistumiskoulutuksen teoriasisällön pohjalta.

Luo kysymykset AINA suomeksi. Kysymysten tulee testata ymmärrystä, ei pelkkää muistamista."""

QUESTION_PROMPT_TEMPLATE = """Luo {num_questions} monivalintakysymystä seuraavan teoriasisällön pohjalta.

EPA-kortti: {epa_title}
Osio: {section_title}
Erikoisala: {specialty_name}

Teoriasisältö:
{content}

OHJEET:
- Luo {num_mc} kysymystä joissa on YKSI oikea vastaus (tyyppi: "multiple_choice")
- Luo {num_ms} kysymystä joissa on USEITA oikeita vastauksia (tyyppi: "multi_select")
- Jokaisessa kysymyksessä 3-5 vaihtoehtoa
- Jokaiselle vaihtoehdolle lyhyt selitys miksi se on oikein tai väärin
- Kysymysten tulee olla suomeksi
- Vaikeustaso 1-5 (1=helppo, 3=haastava, 5=tenttitaso)
- Vaihda vaikeustasoja: noin puolet tasoa 2, neljäsosa tasoa 3, loput 1 tai 4

Palauta JSON-taulukko tässä muodossa:
[
  {{
    "question_type": "multiple_choice" tai "multi_select",
    "difficulty": 1-5,
    "text": "Kysymysteksti",
    "explanation": "Yleinen selitys oikeasta vastauksesta",
    "choices": [
      {{"text": "Vaihtoehto A", "is_correct": true, "explanation": "Selitys miksi oikein"}},
      {{"text": "Vaihtoehto B", "is_correct": false, "explanation": "Selitys miksi väärin"}},
      {{"text": "Vaihtoehto C", "is_correct": false, "explanation": "Selitys miksi väärin"}}
    ]
  }}
]

Palauta VAIN JSON-taulukko, ei muuta tekstiä."""


class Command(BaseCommand):
    help = 'Generate quiz questions from EPA theory content using Claude API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--specialty',
            type=str,
            help='Generate questions only for this specialty (name)',
        )
        parser.add_argument(
            '--epa-id',
            type=int,
            help='Generate questions only for this EPA (database ID)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be generated without saving',
        )
        parser.add_argument(
            '--min-chars',
            type=int,
            default=500,
            help='Minimum section content length in characters (default: 500)',
        )
        parser.add_argument(
            '--questions-per-section',
            type=int,
            default=5,
            help='Target questions per section (default: 5)',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=2.0,
            help='Delay in seconds between API calls (default: 2.0)',
        )

    def handle(self, *args, **options):
        try:
            import anthropic
        except ImportError:
            self.stderr.write(self.style.ERROR(
                'anthropic package not installed. Run: pip install anthropic'
            ))
            return

        import os
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'ANTHROPIC_API_KEY environment variable not set'
            ))
            return

        client = anthropic.Anthropic(api_key=api_key)

        # Get sections to process
        sections = Section.objects.select_related('epa__specialty').all()

        if options['epa_id']:
            sections = sections.filter(epa_id=options['epa_id'])
        elif options['specialty']:
            sections = sections.filter(epa__specialty__name=options['specialty'])

        # Filter by content length
        min_chars = options['min_chars']
        sections_to_process = []
        for section in sections:
            plain_text = strip_html(section.content)
            if len(plain_text) >= min_chars:
                sections_to_process.append((section, plain_text))

        total = len(sections_to_process)
        self.stdout.write(f"\nFound {total} sections with >= {min_chars} characters of content")

        if total == 0:
            self.stdout.write(self.style.WARNING('No sections to process.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n--- DRY RUN ---\n'))

        total_questions = 0
        total_errors = 0

        for i, (section, plain_text) in enumerate(sections_to_process, 1):
            epa = section.epa
            specialty = epa.specialty

            self.stdout.write(
                f"\n[{i}/{total}] {specialty.name} > {epa.title} > {section.title}"
            )
            self.stdout.write(f"  Content: {len(plain_text)} chars")

            # Determine question count and mix
            num_q = options['questions_per_section']
            # Scale based on content length
            if len(plain_text) > 3000:
                num_q = min(num_q + 3, 10)
            elif len(plain_text) < 1000:
                num_q = max(num_q - 2, 2)

            num_mc = max(1, round(num_q * 0.7))  # ~70% single answer
            num_ms = num_q - num_mc  # ~30% multi-select

            self.stdout.write(
                f"  Target: {num_q} questions ({num_mc} MC + {num_ms} MS)"
            )

            if options['dry_run']:
                total_questions += num_q
                continue

            # Truncate very long content to stay within token limits
            content_for_api = plain_text[:8000]

            prompt = QUESTION_PROMPT_TEMPLATE.format(
                num_questions=num_q,
                num_mc=num_mc,
                num_ms=num_ms,
                epa_title=epa.title,
                section_title=section.title,
                specialty_name=specialty.name,
                content=content_for_api,
            )

            try:
                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = response.content[0].text.strip()

                # Extract JSON from response (handle markdown code blocks)
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if not json_match:
                    self.stderr.write(self.style.ERROR(
                        f"  ERROR: Could not parse JSON from response"
                    ))
                    total_errors += 1
                    continue

                questions_data = json.loads(json_match.group())

                # Save to database
                saved = self._save_questions(questions_data, epa, section)
                total_questions += saved
                self.stdout.write(self.style.SUCCESS(f"  Saved {saved} questions"))

            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f"  JSON parse error: {e}"))
                total_errors += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  API error: {e}"))
                total_errors += 1

            # Rate limiting delay
            if i < total:
                time.sleep(options['delay'])

        self.stdout.write(f"\n{'=' * 50}")
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN: Would generate ~{total_questions} questions from {total} sections"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Generated {total_questions} questions from {total} sections"
            ))
            if total_errors:
                self.stdout.write(self.style.ERROR(f"Errors: {total_errors}"))

    @transaction.atomic
    def _save_questions(self, questions_data, epa, section):
        """Save parsed question data to database."""
        saved_count = 0
        for q_data in questions_data:
            q_type = q_data.get('question_type', 'multiple_choice')
            if q_type not in ('multiple_choice', 'multi_select'):
                q_type = 'multiple_choice'

            choices_data = q_data.get('choices', [])
            if len(choices_data) < 2:
                continue

            # Validate: multi_select needs multiple correct, multiple_choice needs exactly one
            correct_count = sum(1 for c in choices_data if c.get('is_correct'))
            if q_type == 'multiple_choice' and correct_count != 1:
                # Fix: mark only the first correct one
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
                difficulty=q_data.get('difficulty', 2),
                text=q_data.get('text', ''),
                explanation=q_data.get('explanation', ''),
                epa=epa,
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
