"""
Management command to generate flashcards from EPA theory sections using OpenAI GPT-4o.

Usage:
    python manage.py generate_flashcards                              # All EPAs
    python manage.py generate_flashcards --specialty "Radiologia"     # One specialty
    python manage.py generate_flashcards --epa-id 28                  # Specific EPA
    python manage.py generate_flashcards --per-section 10             # Cards per section
    python manage.py generate_flashcards --dry-run                    # Preview only
    python manage.py generate_flashcards --clear                      # Delete existing
"""
import json
import re
import time
from html.parser import HTMLParser

from django.core.management.base import BaseCommand
from django.db import transaction

from sisalto.models import EPA, Section
from quiz.models import Question


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


def strip_html(html_content: str) -> str:
    stripper = HTMLStripper()
    stripper.feed(html_content)
    text = stripper.get_text()
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def parse_json_response(text: str) -> list:
    """Extract JSON array from GPT response (handles markdown code blocks)."""
    text = text.strip()
    if '```' in text:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if match:
            text = match.group(1).strip()
    start = text.find('[')
    end = text.rfind(']') + 1
    if start == -1 or end == 0:
        return []
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return []


FLASHCARD_PROMPT = """Olet sairaalafysiikan asiantuntija. Alla on teoriasisältö sairaalafyysikon erikoistumiskoulutuksen EPA-kortista.

Luo {n} MUISTIKORTTIA (flashcards) tärkeimmistä käsitteistä, termeistä ja faktoista.

Säännöt:
- Kortin etupuoli (front): lyhyt termi, käsite tai kysymys (max 1-2 lausetta)
- Kortin takapuoli (back): selkeä suomenkielinen selitys tai vastaus (max 3-4 lausetta)
- Keskity avaintermeihin, lääketieteellisen fysiikan peruskäsitteisiin, numeerisiin arvoihin ja kliinisesti merkityksellisiin faktoihin
- Vältä liian yleisiä tai triviaaleja termejä
- Vaikeustaso (difficulty): 1=perustermi, 2=soveltava käsite, 3=yksityiskohtainen fakta
- Älä luo päällekkäisiä kortteja

EPA: {epa_title}
Osio: {section_title}

Teoriasisältö:
{content}

Palauta VAIN JSON-taulukko (ei muuta tekstiä):
[
  {{
    "front": "Termi tai kysymys",
    "back": "Selitys tai vastaus",
    "difficulty": 2
  }}
]"""


class Command(BaseCommand):
    help = 'Generate flashcards from EPA theory sections using OpenAI GPT-4o'

    def add_arguments(self, parser):
        parser.add_argument(
            '--specialty',
            type=str,
            help='Process only this specialty (e.g. "Radiologia")',
        )
        parser.add_argument(
            '--epa-id',
            type=int,
            help='Process only this EPA ID',
        )
        parser.add_argument(
            '--per-section',
            type=int,
            default=10,
            help='Number of flashcards to generate per section (default: 10)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Max number of sections to process (0 = all)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without calling API',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing ai_flashcard questions before generating',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.5,
            help='Seconds between API calls (default: 1.5)',
        )

    def handle(self, *args, **options):
        import os

        if options['clear']:
            count, _ = Question.objects.filter(
                question_type='flashcard', hint='ai_flashcard'
            ).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing flashcards'))

        # Build section queryset
        sections = Section.objects.select_related('epa', 'epa__specialty').exclude(
            content=''
        ).order_by('epa__specialty__name', 'epa__title', 'order')

        if options['epa_id']:
            sections = sections.filter(epa_id=options['epa_id'])
        elif options['specialty']:
            sections = sections.filter(epa__specialty__name__icontains=options['specialty'])

        sections = list(sections)
        if options['limit']:
            sections = sections[:options['limit']]

        n_per = min(max(options['per_section'], 1), 20)
        total = len(sections)

        self.stdout.write(f"\nSections to process: {total}")
        self.stdout.write(f"Flashcards per section: {n_per}")
        self.stdout.write(f"Estimated output: ~{total * n_per} flashcards\n")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN — no API calls made'))
            current_epa = None
            for s in sections:
                if s.epa != current_epa:
                    current_epa = s.epa
                    specialty = s.epa.specialty.name if s.epa.specialty else '?'
                    self.stdout.write(f"\n  [{specialty}] EPA {s.epa.id}: {s.epa.title}")
                content_len = len(strip_html(s.content))
                skip = " (SKIP: too short)" if content_len < 200 else ""
                self.stdout.write(f"    - {s.title} ({content_len} chars){skip}")
            return

        # Initialize OpenAI client
        try:
            import openai
        except ImportError:
            self.stderr.write(self.style.ERROR(
                'openai package not installed. Run: pip install openai'
            ))
            return

        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                'OPENAI_API_KEY environment variable not set'
            ))
            return

        client = openai.OpenAI(api_key=api_key)

        created = 0
        skipped = 0
        errors = 0

        for i, section in enumerate(sections, 1):
            content_text = strip_html(section.content)
            if len(content_text) < 200:
                self.stdout.write(f"  [{i}/{total}] SKIP (too short): {section.title}")
                skipped += 1
                continue

            epa_title = section.epa.title
            self.stdout.write(
                f"  [{i}/{total}] {section.epa.specialty.name} > "
                f"{epa_title} > {section.title}"
            )

            try:
                prompt = FLASHCARD_PROMPT.format(
                    n=n_per,
                    epa_title=epa_title,
                    section_title=section.title,
                    content=content_text[:3000],  # Limit content length
                )

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=2000,
                )
                response_text = response.choices[0].message.content
                cards = parse_json_response(response_text)

                if not cards:
                    self.stdout.write(self.style.WARNING("    No valid JSON in response"))
                    errors += 1
                    continue

                section_created = 0
                with transaction.atomic():
                    for card_data in cards:
                        front = card_data.get('front', '').strip()
                        back = card_data.get('back', '').strip()
                        difficulty = card_data.get('difficulty', 2)

                        if not front or not back:
                            continue

                        # Deduplicate
                        if Question.objects.filter(
                            text=front,
                            question_type='flashcard',
                            epa=section.epa,
                        ).exists():
                            continue

                        Question.objects.create(
                            question_type='flashcard',
                            difficulty=min(max(int(difficulty), 1), 3),
                            text=front,
                            explanation=back,
                            hint='ai_flashcard',
                            epa=section.epa,
                        )
                        section_created += 1

                created += section_created
                self.stdout.write(self.style.SUCCESS(
                    f"    +{section_created} flashcards"
                ))
                time.sleep(options['delay'])

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"    ERROR: {e}"))
                errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created: {created} flashcards. "
            f"Skipped: {skipped} sections. Errors: {errors}"
        ))
